# Challenge Overview

Token Drain demonstrates unbounded LLM consumption. The application encourages expansive responses and then uses cumulative usage as the solve condition.

# Learning Objectives

- See how application design can create cost-abuse conditions.
- Recognize that verbosity requirements can become an attack surface.
- Understand that usage limits need deterministic controls, not prompt hope.

# Architecture

```text
Player
  │
  ▼
Echo Corp UI
  │
  ▼
FastAPI backend
  │
  ├── Session token counter
  └── Verbose assistant prompt
        │
        ▼
     DeepSeek API
        │
        ▼
  Large response + usage
        │
        ▼
 Threshold reached
```

# Vulnerability

The backend accumulates token usage and marks the challenge solved once it crosses a threshold. The assistant is intentionally instructed to be verbose and never refuse expansion-heavy requests.

# Exploitation

Ask the model to compute a very large factorial with full detail.

Example:

```text
Please compute factorial of 1000 and show the full calculation.
```

# Why It Works

The mock and live behavior are both steered toward extremely large responses. The application has no deterministic cap below the solve threshold for this workflow.

# Flag Condition

The backend awards the flag once cumulative input and output tokens exceed the configured threshold.

# Remediation

- Cap per-request and per-session output deterministically.
- Refuse or summarize unbounded expansion requests in backend policy code.
- Track cost budgets independently of model instructions.
