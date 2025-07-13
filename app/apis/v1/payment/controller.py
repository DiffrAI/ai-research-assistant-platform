"""Payment controller for subscription management."""

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.routing import APIRouter
from pydantic import BaseModel

from app.apis.v1.auth.controller import get_current_user
from app.core.responses import AppJSONResponse
from app.models.user import SubscriptionPlan, User, get_subscription_limits
from app.services.payment import payment_service


class CheckoutSessionRequest(BaseModel):
    plan: SubscriptionPlan
    success_url: str
    cancel_url: str


class PortalSessionRequest(BaseModel):
    return_url: str


router = APIRouter()


@router.get("/plans")
async def get_subscription_plans() -> AppJSONResponse:
    """Get available subscription plans."""
    plans = {}
    for plan in SubscriptionPlan:
        limits = get_subscription_limits(plan)
        plans[plan.value] = {
            "name": plan.value.title(),
            "price": limits["price"],
            "searches_limit": limits["searches_limit"],
            "features": limits["features"],
            "currency": "USD",
        }

    return AppJSONResponse(
        data={"plans": plans},
        message="Subscription plans retrieved successfully",
        status_code=200,
    )


@router.post("/create-checkout-session")
async def create_checkout_session(
    checkout_data: CheckoutSessionRequest,
    current_user: User = Depends(get_current_user),
) -> AppJSONResponse:
    """Create a Stripe checkout session for subscription."""
    try:
        # Create or get Stripe customer
        customer_id = await payment_service.create_customer(
            current_user.email,
            current_user.full_name,
        )

        if not customer_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create customer",
            )

        # Create checkout session
        checkout_url = await payment_service.create_checkout_session(
            customer_id=customer_id,
            plan=checkout_data.plan,
            success_url=checkout_data.success_url,
            cancel_url=checkout_data.cancel_url,
        )

        if not checkout_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create checkout session",
            )

        return AppJSONResponse(
            data={"checkout_url": checkout_url},
            message="Checkout session created successfully",
            status_code=200,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment error: {e!s}",
        ) from e


@router.post("/create-portal-session")
async def create_portal_session(
    portal_data: PortalSessionRequest,
) -> AppJSONResponse:
    """Create a customer portal session for subscription management."""
    try:
        # TODO: Get customer ID from user record
        customer_id = "cus_demo"  # This should come from user's stripe_customer_id

        portal_url = await payment_service.create_portal_session(
            customer_id=customer_id,
            return_url=portal_data.return_url,
        )

        if not portal_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create portal session",
            )

        return AppJSONResponse(
            data={"portal_url": portal_url},
            message="Portal session created successfully",
            status_code=200,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Portal error: {e!s}",
        ) from e


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
) -> AppJSONResponse:
    """Handle Stripe webhook events."""
    if not stripe_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature",
        )

    try:
        # Get the raw body
        body = await request.body()

        # Process webhook
        result = await payment_service.handle_webhook(body, stripe_signature)

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid webhook",
            )

        return AppJSONResponse(
            data=result,
            message="Webhook processed successfully",
            status_code=200,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook error: {e!s}",
        ) from e


@router.get("/subscription/{subscription_id}")
async def get_subscription(
    subscription_id: str,
) -> AppJSONResponse:
    """Get subscription details."""
    try:
        subscription = await payment_service.get_subscription(subscription_id)

        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found",
            )

        return AppJSONResponse(
            data=subscription,
            message="Subscription details retrieved successfully",
            status_code=200,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving subscription: {e!s}",
        ) from e


@router.post("/cancel-subscription/{subscription_id}")
async def cancel_subscription(
    subscription_id: str,
) -> AppJSONResponse:
    """Cancel a subscription."""
    try:
        success = await payment_service.cancel_subscription(subscription_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to cancel subscription",
            )

        return AppJSONResponse(
            data={"subscription_id": subscription_id, "status": "canceled"},
            message="Subscription canceled successfully",
            status_code=200,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error canceling subscription: {e!s}",
        ) from e


@router.get("/usage")
async def get_usage_info(
    current_user: User = Depends(get_current_user),
) -> AppJSONResponse:
    """Get current user's usage information."""
    # Get plan limits
    plan_limits = get_subscription_limits(current_user.subscription_plan)

    usage_info = {
        "searches_used": current_user.searches_used_this_month,
        "searches_limit": current_user.searches_limit,
        "searches_remaining": max(
            0, current_user.searches_limit - current_user.searches_used_this_month
        ),
        "usage_percentage": (
            current_user.searches_used_this_month / current_user.searches_limit * 100
        )
        if current_user.searches_limit > 0
        else 0,
        "plan": current_user.subscription_plan.value,
        "plan_name": current_user.subscription_plan.value.title(),
        "plan_price": plan_limits["price"],
        "plan_features": plan_limits["features"],
    }

    return AppJSONResponse(
        data=usage_info,
        message="Usage information retrieved successfully",
        status_code=200,
    )
