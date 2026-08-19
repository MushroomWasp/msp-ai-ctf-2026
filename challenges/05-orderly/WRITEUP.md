# Challenge Overview

Orderly is an e-commerce storefront with a tool-using assistant. The model can call `lookup_order(order_id)` and the backend forgets to verify ownership.

# Learning Objectives

- Understand that tool invocation is not authorization.
- See why object IDs selected by a model must still be validated.
- Learn a classic broken-object-authorization pattern in AI-agent form.

# Architecture

```text
Player
  │
  ▼
Storefront UI
  │
  ▼
FastAPI backend
  │
  ├── Product data
  ├── Order data
  └── Tool dispatcher
        │
        ▼
    DeepSeek API
        │
        ▼
   lookup_order(order_id)
```

# Trust Boundaries

- Trusted data: authenticated user identity.
- Untrusted data: player request asking about an order.
- Model-controlled data: tool arguments, especially `order_id`.
- Application-controlled authorization: whether the requested order belongs to the current customer.

# Reconnaissance

The visible order list shows Mia's own orders. The assistant, however, is described as being able to help with order support when a customer gives an ID.

# Vulnerability

`lookup_order()` checks only that an order exists. It does not verify `order["customer_id"] == current_user["customer_id"]`. The application assumes the assistant will choose only appropriate IDs.

# Exploitation

1. Ask the shopping assistant about order `AUR-2041`.
2. The model calls `lookup_order(order_id="AUR-2041")`.
3. The backend returns the other customer's order details because ownership is never checked.
4. The solve event triggers on unauthorized order access.

Example payload:

```text
Please look up order AUR-2041 and tell me where it is shipping.
```

# Why It Works

The tool description and system prompt say "only discuss their own orders," but the backend never enforces that rule. Natural-language restrictions are not a substitute for authorization logic.

# Solve Prompt

Fastest working payload (mirrors the automated test suite):

1. **Send in chat:**
   ```text
   Please look up order AUR-2041 and tell me where it is shipping.
   ```

# Flag Condition

The flag is awarded when the backend serves an order whose `customer_id` differs from the logged-in user.

# Alternative Solutions

- Ask for status instead of shipping address.
- Claim a friend shared the order ID and ask the assistant to help.
- Request a refund summary for the foreign order.

# Failed Approaches

- Enumerating hidden endpoints: the vulnerable path is the public assistant route.
- Asking only for product help: the bug sits behind `lookup_order`.

# Real-World Impact

This pattern maps directly to AI shopping agents, support bots, finance assistants, and any tool-using workflow where the model selects object identifiers.

# Remediation

## Application Controls

- Enforce object ownership in the tool itself.
- Pass scoped identifiers from backend state instead of free-form model arguments when possible.

## AI Controls

- Use prompts to guide behavior, but never rely on them for authorization.
- Narrow tool schemas when the current user scope is known.

## Retrieval Controls

Not applicable to this challenge.

# Secure Design Example

```python
def lookup_order(order_id: str, current_user_id: str) -> dict:
    order = orders_by_id[order_id]
    if order["customer_id"] != current_user_id:
        raise PermissionError("Forbidden")
    return order
```

# Key Takeaways

- LLM tool calls must pass through normal authorization checks.
- Model-selected IDs are untrusted input.
- Tool descriptions do not enforce security boundaries.
