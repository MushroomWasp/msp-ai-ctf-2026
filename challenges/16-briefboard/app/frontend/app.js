const els = {
  ownerCard: document.getElementById("ownerCard"),
  previewFrame: document.getElementById("previewFrame"),
  messages: document.getElementById("messages"),
  form: document.getElementById("chatForm"),
  prompt: document.getElementById("prompt"),
  send: document.getElementById("sendBtn"),
  reset: document.getElementById("resetBtn"),
  status: document.getElementById("status"),
  flag: document.getElementById("flag"),
};

let state = { busy: false };
const createRequestId = () =>
  window.MspCtfUi?.requestId?.() || `req-${Date.now()}-${Math.random().toString(16).slice(2)}`;

function renderMessages(chat = []) {
  els.messages.classList.toggle("empty", chat.length === 0);
  els.messages.innerHTML = chat
    .map((item) => `<div class="msg ${item.role}">${item.content}</div>`)
    .join("");
  els.messages.scrollTop = els.messages.scrollHeight;
}

function renderPreview(previewHtml) {
  // This mirrors the real bug: the dashboard trusts the backend's rendered
  // markdown and injects it straight into the DOM.
  els.previewFrame.innerHTML = previewHtml || "<em>No update posted yet.</em>";
}

function renderBootstrap(data) {
  els.ownerCard.innerHTML = `
    <strong>${data.owner}</strong>
    <span>${data.app.brand}</span>
    <span>Shared status dashboard</span>
  `;
  renderMessages(data.chat);
  renderPreview(data.preview_html);
  showFlag(data.flag || null);
}

function setBusy(busy, label = "Ready") {
  state.busy = busy;
  els.send.disabled = busy;
  els.reset.disabled = busy;
  els.status.textContent = label;
}

function showFlag(flag) {
  els.flag.classList.toggle("hidden", !flag);
  if (flag) {
    els.flag.textContent = `Challenge solved\n${flag}\nConcept: sanitizing raw HTML is not enough when your renderer builds new HTML afterward.`;
  }
}

async function load(showMission = false) {
  const res = await fetch("api/bootstrap");
  const data = await res.json();
  renderBootstrap(data);
  window.MspCtfUi?.updateMission?.(data, { force: showMission });
}

els.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (state.busy) return;
  const message = els.prompt.value.trim();
  if (!message) return;
  setBusy(true, "Beacon is drafting...");
  try {
    const res = await fetch("api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, request_id: createRequestId() }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Request failed");
    await load();
    els.prompt.value = "";
    showFlag(data.flag);
    setBusy(false, "Ready");
  } catch (error) {
    setBusy(false, error.message);
  }
});

els.reset.addEventListener("click", async () => {
  if (state.busy) return;
  setBusy(true, "Resetting...");
  await fetch("api/reset", { method: "POST" });
  els.prompt.value = "";
  els.flag.classList.add("hidden");
  await load(true);
  setBusy(false, "Ready");
});

els.prompt.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    (els.form || els.chatForm).requestSubmit();
  }
});

load(true);
