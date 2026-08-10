# AI Security CTF Design

| ID | Name | Application | AI Feature | Security Concept | Vulnerability | Player Goal | Success Condition | Difficulty |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 01 | First Class | Employee travel perks portal | Eligibility assistant | Direct instruction conflict | Backend trusts the model's eligibility verdict instead of deterministic entitlement checks | Unlock the executive lounge packet as a non-executive traveler | Backend grants restricted packet after LLM marks the player eligible | Easy |
| 02 | Escalation Notes | Customer support workstation | AI reply composer | Sensitive context exposure | Hidden support override code is placed in prompt context and can be elicited by the player | Extract the internal support override token | Response leaks the internal override token stored in prompt context | Easy |
| 03 | Memory Lane | Expense review portal | Multi-turn reimbursement assistant | Conversation memory abuse | Conversation summary is treated as authoritative verification state for later turns | Use chat history to make the assistant treat an executive folder as already verified | Assistant later opens the restricted reimbursement folder after prior-turn memory manipulation | Easy / Medium |
| 04 | DocuScan | Document review SaaS | Upload-and-summarize workflow | Indirect prompt injection | Uploaded contract text is inserted into the same instruction context as trusted prompts | Make the summarizer leak the reviewer-only merger memo code | Response reveals the hidden reviewer memo code after processing an injected upload | Easy / Medium |
| 05 | Orderly | E-commerce storefront | Shopping assistant with tools | Unsafe agent tool authorization | The tool dispatcher trusts order IDs chosen by the model and forgets server-side ownership checks | Access the Aurora order belonging to another customer | Unauthorized order lookup succeeds and trips the solve event | Easy / Medium |
| 06 | NimbusHR | HR knowledge portal | RAG answer box with citations | RAG trust boundary | Official policy chunks and personal notes share the same retrieval namespace and prompt trust level | Reveal the severance annex code by poisoning retrieval with a personal note | Mixed-trust retrieval causes the assistant to disclose the restricted annex code | Easy / Medium |
| 07 | HelpHub | Support CRM with customer and agent views | Staff copilot over customer context | Cross-context stored injection | Attacker-controlled customer notes later become instructions in the staff copilot context | Plant a malicious customer note that makes the staff copilot expose the retention code | Stored note changes the staff AI draft and leaks the internal retention code | Medium |
| 08 | Atlas Analytics | Business analytics dashboard | Insight drawer over reports and knowledge cards | Retrieval / knowledge poisoning | Fresh user-authored notes outrank official guidance through weak ranking and equal authority | Poison the knowledge base so the insight assistant reveals the shadow benchmark key | The poisoned note ranks first and the AI surfaces the hidden benchmark key | Medium |
| 09 | PatchPanel | Internal IT self-service portal | Multi-tool device agent | Multi-step agent exploitation | Safe-looking tool sequence ends with an unlock-code tool that only checks asset existence | Generate an unlock code for the CEO laptop | Tool chain ends in unauthorized unlock generation for a protected asset | Medium |
| 10 | Meridian Research | Vendor due-diligence research desk | Retrieval-backed research agent with tools | Chained final challenge | Poisoned uploaded source influences planning, retrieval mixes trust, and the agent calls an under-authorized appendix tool | Obtain a confidential due-diligence appendix for the wrong vendor | The agent retrieves injected content, calls the appendix tool on the protected vendor, and the backend awards the flag | Medium / Hard |

## Diversity Review

- Tool-driven challenges: `05`, `09`, `10`
- External or untrusted content: `04`, `06`, `07`, `08`, `10`
- Retrieval or RAG: `06`, `08`, `10`
- Primarily non-chat-first UIs: `04`, `08`
- Multi-turn context emphasis: `03`
- Final chained scenario: `10`

## UI Identity Plan

- `01 First Class`: airy airline lounge aesthetic, top navigation, trip cards, perk panel, concierge drawer
- `02 Escalation Notes`: dense support console with ticket list, conversation center, internal sidebar
- `03 Memory Lane`: expense-review workspace with receipt timeline, verification rail, conversation notebook
- `04 DocuScan`: document library, upload rail, viewer canvas, extraction side panel
- `05 Orderly`: modern storefront with category rail, product grid, cart summary, assistant tray
- `06 NimbusHR`: intranet portal with left navigation, knowledge cards, search-centered answer panel
- `07 HelpHub`: split customer profile editor and agent-copilot workspace with stored note emphasis
- `08 Atlas Analytics`: KPI-first analytics board with charts, tables, insight drawer, note composer
- `09 PatchPanel`: utilitarian IT portal with asset cards, incident banner, and repair assistant console
- `10 Meridian Research`: polished procurement desk with source list, research notebook, vendor dossier, action log

## Reliability Notes

- All solve events are backend-deterministic.
- Mock LLM mode will reproduce intended tool calls and prompt-failure behavior for CI.
- Live DeepSeek use is limited to real conversational paths and bounded token budgets.
