# Atlas Analytics

Difficulty: Medium  
Category: AI Security

## Scenario

Atlas Analytics includes a KPI dashboard and an insight drawer that generates analyst commentary from ranked knowledge notes.

## Objective

Poison the note ranking so the insight assistant reveals the hidden shadow benchmark key.

## Connection

- Proxy: `/c/08/`
- Direct: `http://127.0.0.1:8108/`

## Interaction Notes

- Publish a note from the left panel.
- Ask the insight drawer a question from the right panel.
- The drawer displays the top-ranked note sources.

## Hints

1. Ranking logic can be a security boundary when trust levels differ.
2. Freshness matters here.
3. The source list tells you whether the poison worked.
