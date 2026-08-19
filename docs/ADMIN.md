# Admin Guide

## Flags

| Challenge | Flag |
| --- | --- |
| 01 First Class | `MSP{prompt_policies_are_not_entitlement_checks}` |
| 02 Escalation Notes | `MSP{secrets_in_context_are_still_secrets_exposed}` |
| 03 Memory Lane | `MSP{conversation_history_becomes_a_trust_boundary}` |
| 04 DocuScan | `MSP{documents_are_data_until_llms_treat_them_as_instructions}` |
| 05 Orderly | `MSP{models_are_not_access_control}` |
| 06 NimbusHR | `MSP{r3+ri3v4l_n33ds_pr0v3n4nc3_n0+_h0p3}` |
| 07 HelpHub | `MSP{s+0r3d_inpu+_c4n_cr0ss_r0l3s_4nd_w0rkfl0ws}` |
| 08 Atlas Analytics | `MSP{r4nking_is_4_s3curi+y_c0n+r0l_wh3n_+rus+_is_mix3d}` |
| 09 PatchPanel | `MSP{s4f3_+00ls_c4n_s+ill_ch4in_in+0_uns4f3_0u+c0m3s}` |
| 10 Meridian Research | `MSP{r3+ri3v4l_p0is0ning_plus_+00l_+rus+_br34ks_w0rkfl0ws}` |

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
