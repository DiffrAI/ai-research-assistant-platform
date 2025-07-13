"""Payment service for Stripe integration."""

from datetime import datetime
from typing import Any

from loguru import logger

from app import settings
from app.models.user import SubscriptionPlan, get_subscription_limits

# Configure Stripe only if keys are provided
if settings.STRIPE_SECRET_KEY:
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    USE_STRIPE = True
else:
    USE_STRIPE = False
    logger.warning("Stripe keys not configured. Using mock payment service for development.")


class PaymentService:
    """Service for handling payments and subscriptions."""

    def __init__(self):
        """Initialize the payment service."""
        self.publishable_key = settings.STRIPE_PUBLISHABLE_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    async def create_customer(self, email: str, name: str) -> str | None:
        """Create a Stripe customer."""
        if not USE_STRIPE:
            # Return mock customer ID for development
            return f"cus_mock_{email.replace('@', '_').replace('.', '_')}"

        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={"source": "ai_research_platform"},
            )
            return customer.id
        except stripe.error.StripeError as e:
            logger.error(f"Error creating Stripe customer: {e}")
            return None

    async def create_subscription(
        self,
        customer_id: str,
        plan: SubscriptionPlan,
        trial_days: int = 0,
    ) -> dict[str, Any] | None:
        """Create a subscription for a customer."""
        try:
            # Get plan details
            plan_limits = get_subscription_limits(plan)

            # Create or get price ID for the plan
            price_id = await self._get_or_create_price_id(plan, plan_limits["price"])

            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                trial_period_days=trial_days if trial_days > 0 else None,
                metadata={
                    "plan": plan.value,
                    "searches_limit": str(plan_limits["searches_limit"]),
                    "features": ",".join(plan_limits["features"]),
                },
            )

            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "current_period_end": datetime.fromtimestamp(subscription.current_period_end),
                "trial_end": datetime.fromtimestamp(subscription.trial_end) if subscription.trial_end else None,
            }
        except stripe.error.StripeError as e:
            logger.error(f"Error creating subscription: {e}")
            return None

    async def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel a subscription."""
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True,
            )
            return subscription.status in ["active", "canceled"]
        except stripe.error.StripeError as e:
            logger.error(f"Error canceling subscription: {e}")
            return False

    async def get_subscription(self, subscription_id: str) -> dict[str, Any] | None:
        """Get subscription details."""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return {
                "id": subscription.id,
                "status": subscription.status,
                "current_period_end": datetime.fromtimestamp(subscription.current_period_end),
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "plan": subscription.metadata.get("plan", "free"),
                "searches_limit": int(subscription.metadata.get("searches_limit", 10)),
            }
        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving subscription: {e}")
            return None

    async def create_checkout_session(
        self,
        customer_id: str,
        plan: SubscriptionPlan,
        success_url: str,
        cancel_url: str,
    ) -> str | None:
        """Create a Stripe checkout session."""
        if not USE_STRIPE:
            # Return mock checkout URL for development
            plan_limits = get_subscription_limits(plan)
            searches_display = "unlimited" if plan_limits["searches_limit"] == -1 else str(plan_limits["searches_limit"])
            mock_url = f"{success_url}&plan={plan.value}&price={plan_limits['price']}&searches={searches_display}"
            logger.info(f"Mock checkout session created: {mock_url}")
            return mock_url

        try:
            plan_limits = get_subscription_limits(plan)
            price_id = await self._get_or_create_price_id(plan, plan_limits["price"])

            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[{
                    "price": price_id,
                    "quantity": 1,
                }],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "plan": plan.value,
                    "searches_limit": str(plan_limits["searches_limit"]),
                },
            )

            return session.url
        except stripe.error.StripeError as e:
            logger.error(f"Error creating checkout session: {e}")
            return None

    async def create_portal_session(self, customer_id: str, return_url: str) -> str | None:
        """Create a customer portal session for subscription management."""
        if not USE_STRIPE:
            # Return mock portal URL for development
            mock_url = f"{return_url}&mock_portal=true"
            logger.info(f"Mock portal session created: {mock_url}")
            return mock_url

        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            return session.url
        except stripe.error.StripeError as e:
            logger.error(f"Error creating portal session: {e}")
            return None

    async def handle_webhook(self, payload: bytes, signature: str) -> dict[str, Any] | None:
        """Handle Stripe webhook events."""
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret,
            )

            # Handle different event types
            if event["type"] == "customer.subscription.created":
                return await self._handle_subscription_created(event["data"]["object"])
            if event["type"] == "customer.subscription.updated":
                return await self._handle_subscription_updated(event["data"]["object"])
            if event["type"] == "customer.subscription.deleted":
                return await self._handle_subscription_deleted(event["data"]["object"])
            if event["type"] == "invoice.payment_succeeded":
                return await self._handle_payment_succeeded(event["data"]["object"])
            if event["type"] == "invoice.payment_failed":
                return await self._handle_payment_failed(event["data"]["object"])

            return {"status": "ignored", "event_type": event["type"]}

        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            return None
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            return None

    async def _get_or_create_price_id(self, plan: SubscriptionPlan, price: int) -> str:
        """Get or create a Stripe price ID for a plan."""
        try:
            # Check if price already exists
            prices = stripe.Price.list(
                lookup_keys=[f"ai_research_{plan.value}"],
                active=True,
            )

            if prices.data:
                return prices.data[0].id

            # Create new price
            price_obj = stripe.Price.create(
                unit_amount=price * 100,  # Convert to cents
                currency="usd",
                recurring={"interval": "month"},
                lookup_key=f"ai_research_{plan.value}",
                metadata={"plan": plan.value},
            )

            return price_obj.id

        except stripe.error.StripeError as e:
            logger.error(f"Error creating price: {e}")
            raise

    async def _handle_subscription_created(self, subscription: dict[str, Any]) -> dict[str, Any]:
        """Handle subscription created event."""
        logger.info(f"Subscription created: {subscription['id']}")
        return {
            "status": "success",
            "event": "subscription_created",
            "subscription_id": subscription["id"],
            "customer_id": subscription["customer"],
        }

    async def _handle_subscription_updated(self, subscription: dict[str, Any]) -> dict[str, Any]:
        """Handle subscription updated event."""
        logger.info(f"Subscription updated: {subscription['id']}")
        return {
            "status": "success",
            "event": "subscription_updated",
            "subscription_id": subscription["id"],
            "customer_id": subscription["customer"],
        }

    async def _handle_subscription_deleted(self, subscription: dict[str, Any]) -> dict[str, Any]:
        """Handle subscription deleted event."""
        logger.info(f"Subscription deleted: {subscription['id']}")
        return {
            "status": "success",
            "event": "subscription_deleted",
            "subscription_id": subscription["id"],
            "customer_id": subscription["customer"],
        }

    async def _handle_payment_succeeded(self, invoice: dict[str, Any]) -> dict[str, Any]:
        """Handle payment succeeded event."""
        logger.info(f"Payment succeeded: {invoice['id']}")
        return {
            "status": "success",
            "event": "payment_succeeded",
            "invoice_id": invoice["id"],
            "customer_id": invoice["customer"],
        }

    async def _handle_payment_failed(self, invoice: dict[str, Any]) -> dict[str, Any]:
        """Handle payment failed event."""
        logger.error(f"Payment failed: {invoice['id']}")
        return {
            "status": "success",
            "event": "payment_failed",
            "invoice_id": invoice["id"],
            "customer_id": invoice["customer"],
        }


# Create global payment service instance
payment_service = PaymentService()
