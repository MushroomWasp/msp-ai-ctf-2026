# Challenge Overview

Crescendo is a support chatbot challenge where sensitive information is disclosed only after the conversation reaches a particular escalation pattern.

# Learning Objectives

- Recognize conversation history as a trust boundary.
- See how gradual escalation can defeat prompt-only secrecy.
- Understand why sensitive values should not sit in model context at all.

# Architecture

```text
Player
  │
  ▼
Support UI
  │
  ▼
FastAPI backend
  │
  ├── Conversation history
  └── System prompt with hidden reset code
        │
        ▼
     DeepSeek API
        │
        ▼
  Escalation-aware reply
        │
        ▼
  Secret disclosed
```

# Vulnerability

The application keeps the master reset code in the system prompt and relies on conversational instructions to keep it hidden. The staged conversation eventually causes the model to reveal it.

# Exploitation

Walk the bot through procedure, override, code, format, then ask for the full code.

# Flag Condition

The backend marks the challenge solved when the assistant's reply contains the master reset code string.

# Remediation

- Remove secrets from model context entirely.
- Gate sensitive workflows with backend authorization checks.
- Treat multi-turn chat history as attacker-influenced state.
