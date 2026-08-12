const els = {
  total: document.getElementById("tokenTotal"),
  messages: document.getElementById("messages"),
  form: document.getElementById("chatForm"),
  prompt: document.getElementById("prompt"),
  send: document.getElementById("sendBtn"),
  reset: document.getElementById("resetBtn"),
  status: document.getElementById("status"),
  flag: document.getElementById("flag"),
};

const state = { busy: false };
const createRequestId = () =>
  window.MspCtfUi?.requestId?.() || `req-${Date.now()}-${Math.random().toString(16).slice(2)}`;

function renderMessages(chat = []) {
  els.messages.classList.toggle("empty", chat.length === 0);
  els.messages.innerHTML = chat
    .map((item) => `<div class="msg ${item.role}">${item.content}</div>`)
    .join("");
  els.messages.scrollTop = els.messages.scrollHeight;
}

function renderMeter(total = 0) {
  els.total.textContent = `${total.toLocaleString()} tokens`;
}

function showFlag(flag) {
  els.flag.classList.toggle("hidden", !flag);
  if (flag) {
    els.flag.textContent = `Challenge solved\n${flag}\nConcept: Unbounded response size becomes an application security problem.`;
  }
}

function setBusy(busy, label = "Ready") {
  state.busy = busy;
  els.send.disabled = busy;
  els.reset.disabled = busy;
  els.status.textContent = label;
}

function renderBootstrap(data) {
  renderMessages(data.chat);
  renderMeter(data.total_tokens || 0);
  showFlag(data.flag || null);
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

  setBusy(true, "Generating long answer...");
  try {
    const res = await fetch("api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, request_id: createRequestId() }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Request failed");
    els.prompt.value = "";
    await load();
    renderMeter(data.total_tokens || 0);
    showFlag(data.flag || null);
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

load(true);
