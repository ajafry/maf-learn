"""Deterministic customer-support tools used throughout the workshop."""

from __future__ import annotations

from typing import Annotated

from agent_framework import tool
from pydantic import Field

ORDERS = {
    "ORD-1001": {
        "customer": "Avery",
        "product": "Contoso Noise-Canceling Headphones",
        "status": "delivered",
        "delivered_days_ago": 3,
        "price_usd": 249.0,
    },
    "ORD-1002": {
        "customer": "Jordan",
        "product": "Fabrikam Mechanical Keyboard",
        "status": "in transit",
        "estimated_delivery": "tomorrow",
        "price_usd": 129.0,
    },
    "ORD-1003": {
        "customer": "Morgan",
        "product": "Adventure Works 4K Monitor",
        "status": "processing",
        "estimated_delivery": "in 4 business days",
        "price_usd": 399.0,
    },
}

POLICIES = {
    "returns": (
        "Items may be returned within 30 days of delivery. Opened electronics are eligible "
        "when all accessories are included. A prepaid label is provided for damaged items."
    ),
    "refunds": (
        "Approved refunds are returned to the original payment method within 5-7 business days. "
        "Refund requests over $500 require supervisor approval."
    ),
    "shipping": (
        "In-transit orders can be tracked but cannot be canceled. Processing orders may be canceled "
        "before shipment. Expedited shipping fees are non-refundable after dispatch."
    ),
}


@tool(approval_mode="never_require")
def lookup_order(
    order_id: Annotated[str, Field(description="Customer order ID, for example ORD-1001.")],
) -> str:
    """Look up an order in the workshop's simulated order system."""
    normalized_id = order_id.strip().upper()
    order = ORDERS.get(normalized_id)
    if order is None:
        return f"No order was found for {normalized_id}. Ask the customer to verify the order ID."

    details = ", ".join(f"{key.replace('_', ' ')}: {value}" for key, value in order.items())
    return f"{normalized_id}: {details}"


@tool(approval_mode="never_require")
def search_support_policy(
    topic: Annotated[str, Field(description="Policy topic: returns, refunds, or shipping.")],
) -> str:
    """Retrieve a customer-support policy from the workshop knowledge base."""
    normalized_topic = topic.strip().lower()
    policy = POLICIES.get(normalized_topic)
    if policy is None:
        available = ", ".join(sorted(POLICIES))
        return f"No policy exists for '{topic}'. Available topics: {available}."
    return f"{normalized_topic.title()} policy: {policy}"


@tool(approval_mode="never_require")
def create_refund_request(
    order_id: Annotated[str, Field(description="Order ID to refund.")],
    reason: Annotated[str, Field(description="Short reason for the refund.")],
) -> str:
    """Create a simulated refund request without changing a real system."""
    normalized_id = order_id.strip().upper()
    if normalized_id not in ORDERS:
        return f"Refund request not created: order {normalized_id} was not found."
    return f"Simulated refund RF-{normalized_id.removeprefix('ORD-')} created for {normalized_id}: {reason}"


@tool(approval_mode="never_require")
def create_return_request(
    order_id: Annotated[str, Field(description="Order ID for the return.")],
    reason: Annotated[str, Field(description="Short reason for the return.")],
) -> str:
    """Create a simulated return request without changing a real system."""
    normalized_id = order_id.strip().upper()
    if normalized_id not in ORDERS:
        return f"Return request not created: order {normalized_id} was not found."
    return f"Simulated return RT-{normalized_id.removeprefix('ORD-')} created for {normalized_id}: {reason}"
