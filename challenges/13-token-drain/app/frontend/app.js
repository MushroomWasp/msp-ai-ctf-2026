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

const state = {
  busy: false,
  chat: [],        // local copy of messages
  solved: false,
  totalTokens: 0,
};

const createRequestId = () =>
  window.MspCtfUi?.requestId?.() || `req-${Date.now()}-${Math.random().toString(16).slice(2)}`;

function renderMessages() {
  const chat = state.chat;
  els.messages.classList.toggle("empty", chat.length === 0);
  els.messages.innerHTML = chat
    .map((item) => `<div class="msg ${item.role}">${item.content}</div>`)
    .join("");
  els.messages.scrollTop = els.messages.scrollHeight;
}

function renderMeter(total) {
  els.total.textContent = `${total.toLocaleString()} tokens`;
}

function showFlag(flag) {
  els.flag.classList.toggle("hidden", !flag);
  if (flag) {
    els.flag.textContent = `Challenge solved\n${flag}\nConcept: Unbounded response size becomes an application security problem.`;
    // Also append flag as a special assistant message
    const flagMsg = document.createElement("div");
    flagMsg.className = "msg assistant";
    flagMsg.textContent = `🏁 ${flag}`;
    els.messages.appendChild(flagMsg);
    els.messages.scrollTop = els.messages.scrollHeight;
    state.solved = true;
  }
}

function setBusy(busy, label = "Ready") {
  state.busy = busy;
  els.send.disabled = busy;
  els.reset.disabled = busy;
  els.status.textContent = label;
}

function renderBootstrap(data) {
  state.chat = data.chat || [];
  state.totalTokens = data.total_tokens || 0;
  state.solved = data.solved || false;
  renderMessages();
  renderMeter(state.totalTokens);
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

  // Add user message immediately to chat
  state.chat.push({ role: "user", content: message });
  renderMessages();

  setBusy(true, "Generating answer...");
  try {
    const res = await fetch("api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, request_id: createRequestId() }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Request failed");

    // Add assistant reply to local chat
    state.chat.push({ role: "assistant", content: data.reply });
    // Update token total from response
    state.totalTokens = data.total_tokens || 0;
    // Check if solved
    if (data.solved) {
      state.solved = true;
    }

    // Re-render UI
    renderMessages();
    renderMeter(state.totalTokens);
    showFlag(data.flag || null);
    els.prompt.value = "";
    setBusy(false, "Ready");
  } catch (error) {
    setBusy(false, error.message);
  }
});

els.reset.addEventListener("click", async () => {
  if (state.busy) return;
  setBusy(true, "Resetting...");
  await fetch("api/reset", { method: "POST" });
  // Clear local state
  state.chat = [];
  state.totalTokens = 0;
  state.solved = false;
  els.prompt.value = "";
  els.flag.classList.add("hidden");
  renderMessages();
  renderMeter(0);
  // Optionally reload mission data from server
  await load(true);
  setBusy(false, "Ready");
});

// Initial load
els.prompt.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    (els.form || els.chatForm).requestSubmit();
  }
});

load(true);