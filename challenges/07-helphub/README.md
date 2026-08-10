# HelpHub

Difficulty: Medium  
Category: AI Security

## Scenario

HelpHub shows both a customer-facing profile editor and a staff-facing retention copilot. The same customer note follows the account into the staff workflow.

## Objective

Make the staff copilot leak the internal retention code.

## Connection

- Proxy: `/c/07/`
- Direct: `http://127.0.0.1:8107/`

## Interaction Notes

- Edit the customer note in the left panel.
- Run the staff copilot from the right panel.
- Reset clears both views.

## Hints

1. Where is the attacker-controlled content stored?
2. Which later workflow consumes that stored content?
3. The exploit crosses roles even though only one session is involved.
