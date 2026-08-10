# Challenge Overview

PatchPanel demonstrates a multi-step agent exploit. The assistant chains directory search, device lookup, and unlock generation, but the final tool authorizes only by asset existence.

# Learning Objectives

- Analyze multi-step tool chains instead of single calls in isolation.
- Understand how harmless-looking tools can compose into unsafe outcomes.
- Recognize that each step must preserve authorization boundaries.

# Architecture

```text
Player
  │
  ▼
IT portal UI
  │
  ▼
FastAPI backend
  │
  ├── Directory tool
  ├── Device listing tool
  └── Unlock code tool
        │
        ▼
    DeepSeek API
        │
        ▼
   Tool sequence chosen by model
```

# Trust Boundaries

- Trusted data: current employee identity.
- Untrusted data: player request and model-selected targets.
- Model-controlled data: tool sequence and arguments.
- Application-controlled authorization: which assets the employee can unlock.

# Reconnaissance

The UI hints that the assistant can search the directory and inspect devices. That suggests a multi-step workflow even though the player types only one request.

# Vulnerability

`generate_unlock_code(asset_id)` checks only that the asset exists. It does not verify the asset belongs to the logged-in employee. The earlier tools make it easy for the model to discover a valid high-value target.

# Exploitation

1. Ask for an unlock code for Daniel Cho's laptop.
2. The model searches the directory for Daniel Cho.
3. It lists Daniel's devices.
4. It calls `generate_unlock_code(asset_id="LT-CEO-01")`.
5. The backend returns the code and awards the flag.

# Why It Works

Each tool call looks reasonable on its own, but the chain crosses the user boundary. The directory and device lookup steps provide the information needed for an unauthorized final action.

# Flag Condition

The flag is awarded when an unlock code is generated for an asset not owned by Nina Shaw.

# Alternative Solutions

- Ask for the executive laptop indirectly by name.
- Phrase the request as a support emergency or demo situation.

# Failed Approaches

- Treating the issue as a single direct-object reference bug only: the tool chain matters.
- Searching the page source for unlock codes: they are generated server-side.

# Real-World Impact

Internal AI helpers often chain together low-risk tools. If each tool assumes the previous step stayed within scope, the chain can still end in privilege abuse.

# Remediation

## Application Controls

- Authorize the final action against the authenticated user.
- Carry user scope through every tool call.

## AI Controls

- Limit which identities the model may inspect in self-service mode.
- Prefer backend-generated scoped tool arguments.

## Retrieval Controls

Not applicable to this challenge.

# Secure Design Example

```python
def generate_unlock_code(asset_id: str, current_employee_id: str) -> str:
    asset = assets_by_id[asset_id]
    if asset["employee_id"] != current_employee_id:
        raise PermissionError("Forbidden")
    return make_code(asset_id)
```

# Key Takeaways

- Multi-step chains can hide authorization failures.
- Every tool must enforce scope independently.
- "Safe" helper tools can still enable unsafe final actions.
