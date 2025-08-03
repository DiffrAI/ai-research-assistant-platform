"""Payment service for Stripe integration."""

from datetime import datetime
from typing import Any, Dict, Optional

from loguru import logger

from app import settings
from app.models import SubscriptionPlan, get_subscription_limits

# Configure Stripe only if keys are provided
if settings.stripe_secret_key:
    try:
        import stripe
        stripe.api_key = settings.stripe_secret_key
        USE_STRIPE = True
    except ImportError:
        USE_STRIPE = False
        logger.warning("Stripe not installed. Using mock payment service.")
else:
    USE_STRIPE = False
    logger.warning("Stripe keys not configured. Using mock payment service.")


class PaymentService:
    """Service for handling payments and subscriptions."""

    async def create_customer(self, email: str, name: str) -> Optional[str]:
        """Create a Stripe customer."""
        if not USE_STRIPE:
            return f"cus_mock_{email.replace('@', '_').replace('.', '_')}"

        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={"source": "ai_research_platform"},
            )
            return customer.id
        except Exception as e:
            logger.error(f"Error creating Stripe customer: {e}")
            return None

    async def create_checkout_session(
        self,
        customer_id: str,
        plan: SubscriptionPlan,
        success_url: str,
        cancel_url: str,
    ) -> Optional[str]:
        """Create a Stripe checkout session."""
        if not USE_STRIPE:
            plan_limits = get_subscription_limits(plan)
            mock_url = f"{success_url}&plan={plan.value}&price={plan_limits['price']}"
            logger.info(f"Mock checkout session created: {mock_url}")
            return mock_url

        try:
            plan_limits = get_subscription_limits(plan)
            
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": f"{plan.value.title()} Plan"},
                        "unit_amount": plan_limits["price"] * 100,
                        "recurring": {"interval": "month"},
                    },
                    "quantity": 1,
                }],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
            )
            return session.url
        except Exception as e:
            logger.error(f"Error creating checkout session: {e}")
            return None

    async def create_portal_session(
        self, customer_id: str, return_url: str
    ) -> Optional[str]:
        """Create a customer portal session."""
        if not USE_STRIPE:
            mock_url = f"{return_url}&mock_portal=true"
            logger.info(f"Mock portal session created: {mock_url}")
            return mock_url

        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            return session.url
        except Exception as e:
            logger.error(f"Error creating portal session: {e}")
            return None


# Global payment service instance
payment_service = PaymentService()