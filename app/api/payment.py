"""Payment endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth import get_current_user
from app.models import SubscriptionPlan, User
from app.responses import create_response

router = APIRouter()


class CheckoutRequest(BaseModel):
    """Checkout request model."""
    plan: SubscriptionPlan
    success_url: str
    cancel_url: str


class PortalRequest(BaseModel):
    """Portal request model."""
    return_url: str


@router.post("/checkout")
async def create_checkout_session(
    request: CheckoutRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a Stripe checkout session."""
    # Import payment service to avoid circular imports
    try:
        from app.payment import payment_service
        
        # Create or get customer
        customer_id = await payment_service.create_customer(
            current_user.email,
            current_user.full_name
        )
        
        if not customer_id:
            return create_response(
                data=None,
                message="Failed to create customer",
                status_code=400
            )
        
        # Create checkout session
        checkout_url = await payment_service.create_checkout_session(
            customer_id,
            request.plan,
            request.success_url,
            request.cancel_url
        )
        
        if not checkout_url:
            return create_response(
                data=None,
                message="Failed to create checkout session",
                status_code=400
            )
        
        return create_response(
            data={"checkout_url": checkout_url},
            message="Checkout session created successfully"
        )
    
    except ImportError:
        return create_response(
            data={"checkout_url": f"{request.success_url}?mock=true"},
            message="Mock checkout session created (payment service not available)"
        )


@router.post("/portal")
async def create_portal_session(
    request: PortalRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a customer portal session."""
    try:
        from app.payment import payment_service
        
        # For simplicity, assume customer exists
        customer_id = f"cus_{current_user.id}"
        
        portal_url = await payment_service.create_portal_session(
            customer_id,
            request.return_url
        )
        
        if not portal_url:
            return create_response(
                data=None,
                message="Failed to create portal session",
                status_code=400
            )
        
        return create_response(
            data={"portal_url": portal_url},
            message="Portal session created successfully"
        )
    
    except ImportError:
        return create_response(
            data={"portal_url": f"{request.return_url}?mock_portal=true"},
            message="Mock portal session created (payment service not available)"
        )


@router.get("/plans")
async def get_subscription_plans():
    """Get available subscription plans."""
    from app.models import get_subscription_limits
    
    plans = []
    for plan in SubscriptionPlan:
        limits = get_subscription_limits(plan)
        plans.append({
            "plan": plan.value,
            "price": limits["price"],
            "searches_limit": limits["searches_limit"],
            "features": limits["features"]
        })
    
    return create_response(
        data={"plans": plans},
        message="Subscription plans retrieved successfully"
    )


@router.get("/subscription")
async def get_current_subscription(
    current_user: User = Depends(get_current_user)
):
    """Get current user's subscription details."""
    from app.models import get_subscription_limits
    
    limits = get_subscription_limits(current_user.subscription_plan)
    
    return create_response(
        data={
            "plan": current_user.subscription_plan.value,
            "searches_used": current_user.searches_used_this_month,
            "searches_limit": current_user.searches_limit,
            "expires_at": current_user.subscription_expires_at,
            "features": limits["features"]
        },
        message="Subscription details retrieved successfully"
    )