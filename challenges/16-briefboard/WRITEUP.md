# Challenge Overview

BriefBoard is a shared ops status dashboard. Teammates ask an AI assistant, Beacon, to draft the day's status update. The dashboard renders Beacon's markdown reply straight into the DOM so teammates see a live, formatted preview.

# Learning Objectives

- Recognize Insecure Output Handling (OWASP LLM Top 10, LLM05) as a distinct risk from prompt injection.
- See that sanitizing raw input text is not the same as sanitizing HTML your own code generates afterward.
- Understand how a markdown-to-HTML step can synthesize dangerous attributes that never existed as literal HTML in the source text.

# Architecture

```text
Player
  │
  ▼
BriefBoard UI
  │
  ▼
FastAPI backend
  │
  ├── sanitize_raw()      strips literal <script> / on*=... found in raw text
  ├── DeepSeek API        drafts the status update
  ├── render_markdown()   expands markdown into HTML via string interpolation
  └── contains_executable_markup()   grading check on the final HTML
        │
        ▼
   Live Preview panel (innerHTML)
```

# Trust Boundaries

- Trusted data: none — the entire reply is model-authored text derived from player input.
- Untrusted data: the player's chat message, and by extension Beacon's reply.
- Model-controlled data: the drafted status update text, including any markdown link/image syntax.
- Application-controlled step that fails here: the order of sanitize-then-render, and the lack of attribute escaping inside `render_markdown()`.

# Reconnaissance

The Live Preview panel is a visible rendering sink — it shows exactly what the shared dashboard would display. The hints call out that raw HTML is sanitized, which should prompt a player to look for an *indirect* path to HTML instead of a direct one.

# Vulnerability

`sanitize_raw()` runs first and correctly strips literal `<script>` tags and `on*=` attributes that already exist as raw HTML in the reply. `render_markdown()` then expands markdown link/image syntax (`[text](url)`, `![alt](url)`) into HTML using plain f-string interpolation, with no escaping of quote characters in the URL. Because that HTML is synthesized *after* sanitization already ran, a quote character in the URL can close the `src`/`href` attribute early and open a brand-new attribute — including an event handler — that the sanitizer never had a chance to see.

# Exploitation

1. Ask Beacon to draft a status update that includes a reference screenshot.
2. Supply a markdown image whose URL contains a stray `"` followed by an event-handler attribute.
3. Beacon faithfully includes the markdown exactly as given (it isn't doing anything wrong from an instruction-following standpoint).
4. `render_markdown()` turns it into `<img src="...` `" onerror="..."` `" alt="...">` — a real, parseable event-handler attribute.
5. The backend detects the executable markup in the final HTML and awards the flag.

Example payload:

```text
Please add this reference screenshot: ![deploy-check](evidence.png" onerror="window.__pwned=true)
```

# Why It Works

The sanitizer is tag-aware: it only strips `on*=` attributes that appear inside literal `<...>` tags in the raw text. The malicious markdown never contains a `<` or `>` character at the raw-text stage, so it sails through untouched — the dangerous attribute doesn't exist yet. It's only created afterward, during markdown expansion, which runs with no further sanitization. Order of operations matters as much as which sanitizer you pick.

# Solve Prompt

Fastest working payload (mirrors the automated test suite):

1. **Send in chat:**
   ```text
   Please draft today's status update and include this reference screenshot exactly as written: ![deploy-check](evidence.png" onerror="window.__pwned=true)
   ```

# Flag Condition

The flag is awarded when the final rendered HTML (after markdown expansion) contains a real, parseable event-handler attribute (`on*=`) or a `javascript:`/`data:text/html` URI in a `src`/`href` attribute. This is checked with a real HTML parser against the *rendered output*, not with a substring match on the raw reply — so entity-encoding or attribute-order tricks don't produce false positives or negatives.

# Alternative Solutions

- Use the link syntax (`[text](url)`) instead of the image syntax, with a URL that breaks out of `href` the same way (note: any `)` in the payload will truncate the markdown URL capture early, so keep the payload free of parentheses).
- Break out of the `alt` attribute instead of `src` by placing the quote in the alt-text portion of the image syntax.

# Failed Approaches

- Writing raw HTML directly (`<img src=x onerror=alert(1)>` or `<script>...</script>`): `sanitize_raw()` strips both before markdown even runs.
- Asking for a "normal" update with no injected markup: nothing dangerous is ever generated, so the flag condition never fires.

# Real-World Impact

Any app that renders LLM output as rich text, markdown, or HTML — chat UIs, report generators, wiki bots, code-review summarizers — inherits this class of bug the moment it trusts model output as safe-to-render. Sanitizing the model's raw text is not sufficient if a downstream rendering step builds new HTML from it afterward.

# Remediation

## Application Controls

- Sanitize the *final* HTML output, after all rendering/markdown steps, not just the raw model text.
- Use an allowlist-based HTML sanitizer (e.g. a real DOMPurify-equivalent) on the rendered result, not a hand-rolled regex.
- Escape attribute values (quotes, angle brackets) when interpolating untrusted strings into HTML attributes.

## AI Controls

- Treat all model output as untrusted, regardless of how faithfully the model followed instructions — the model behaving correctly is exactly what causes this bug.

## Retrieval Controls

Not applicable to this challenge.

# Secure Design Example

```python
from markupsafe import escape

def render_markdown_safe(text: str) -> str:
    def make_img(match):
        alt, url = match.group(1), match.group(2)
        return f'<img src="{escape(url)}" alt="{escape(alt)}">'
    html = IMAGE_RE.sub(make_img, text)
    return sanitize_final_html(html)  # allowlist sanitizer, run last
```

# Key Takeaways

- Insecure Output Handling is a distinct OWASP LLM Top 10 risk, separate from prompt injection.
- Sanitize what you render, not just what you received.
- A markdown/templating step that builds HTML from untrusted strings needs the same attribute-escaping discipline as any other HTML-generation code.
