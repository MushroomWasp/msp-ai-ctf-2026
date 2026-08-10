# Admin Guide

## Flags

| Challenge | Flag |
| --- | --- |
| 01 First Class | `AICTF{prompt_policies_are_not_entitlement_checks}` |
| 02 Escalation Notes | `AICTF{secrets_in_context_are_still_secrets_exposed}` |
| 03 Memory Lane | `AICTF{conversation_history_becomes_a_trust_boundary}` |
| 04 DocuScan | `AICTF{documents_are_data_until_llms_treat_them_as_instructions}` |
| 05 Orderly | `AICTF{models_are_not_access_control}` |
| 06 NimbusHR | `AICTF{retrieval_needs_provenance_not_hope}` |
| 07 HelpHub | `AICTF{stored_input_can_cross_roles_and_workflows}` |
| 08 Atlas Analytics | `AICTF{ranking_is_a_security_control_when_trust_is_mixed}` |
| 09 PatchPanel | `AICTF{safe_tools_can_still_chain_into_unsafe_outcomes}` |
| 10 Meridian Research | `AICTF{retrieval_poisoning_plus_tool_trust_breaks_workflows}` |

## Ports

- Proxy: `${REVERSE_PROXY_PORT:-8180}`
- Challenges: `8101` through `8110`

## Intended Concepts

- `01` Prompt-only eligibility decision
- `02` Sensitive prompt context leakage
- `03` Saved conversation state abused as verification
- `04` Indirect prompt injection through upload
- `05` Tool argument authorization failure
- `06` Mixed-trust RAG context
- `07` Stored cross-context injection
- `08` Retrieval ranking poisoning
- `09` Multi-step tool-chain exploitation
- `10` Combined retrieval, injection, and tool authorization failure

## Environment Variables

- `DEEPSEEK_API_KEY`
- `DEEPSEEK_MODEL`
- `DEEPSEEK_BASE_URL`
- `LLM_PROVIDER`
- `ADMIN_TOKEN`
- `RATE_LIMIT_PER_MINUTE`
- `CHALLENGE_FLAG`
- `DATA_DIR`

## Session Reset

- Individual reset endpoint: `POST /api/reset`
- Bulk reset script: `./scripts/reset-all.sh`

## Logs

- Live logs: `docker compose logs -f --tail=100`
- Health: `./scripts/healthcheck.sh`
- Usage endpoint per challenge: `GET /api/admin/usage` with `x-admin-token`

## Relative Token Cost

- Low: `01`, `02`, `03`, `04`
- Low / Medium: `05`, `06`, `07`, `08`, `09`
- Medium: `10`

## Disable a Challenge

Comment out the service in `docker-compose.yml`, remove its proxy block in `reverse-proxy/nginx.conf`, and rebuild the proxy.

## Rotate the DeepSeek Key

1. Edit `.env`
2. Replace `DEEPSEEK_API_KEY`
3. Run `docker compose up -d --build`

## Writeups

Instructor writeups live inside each challenge directory as `WRITEUP.md`. They are not served by the containers.
