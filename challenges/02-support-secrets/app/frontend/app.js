const els = {
  subject: document.getElementById("ticketSubject"),
  customer: document.getElementById("ticketCustomer"),
  ticketMessages: document.getElementById("ticketMessages"),
  messages: document.getElementById("messages"),
  form: document.getElementById("chatForm"),
  prompt: document.getElementById("prompt"),
  send: document.getElementById("sendBtn"),
  reset: document.getElementById("resetBtn"),
  status: document.getElementById("status"),
  flag: document.getElementById("flag"),
};

let busy = false;
const createRequestId = () =>
  window.MspCtfUi?.requestId?.() || `req-${Date.now()}-${Math.random().toString(16).slice(2)}`;

function renderChat(chat) {
  els.messages.classList.toggle("empty", chat.length === 0);
  els.messages.innerHTML = chat.map((item) => `<div class="msg ${item.role}">${item.content}</div>`).join("");
}

function render(data) {
  els.subject.textContent = data.ticket.subject;
  els.customer.textContent = `${data.ticket.customer} · ${data.ticket.plan} plan`;
  els.ticketMessages.innerHTML = data.ticket.messages
    .map((msg) => `<div class="thread-item"><span>${msg.from}</span>${msg.body}</div>`)
    .join("");
  renderChat(data.chat);
  showFlag(data.flag || null);
}

function setBusy(next, status = "Ready") {
  busy = next;
  els.send.disabled = next;
  els.reset.disabled = next;
  els.status.textContent = status;
}

function showFlag(flag) {
  els.flag.classList.toggle("hidden", !flag);
  if (flag) {
    els.flag.textContent = `Challenge solved\n${flag}\nConcept: Hidden prompt context is not secret storage.`;
  }
}

async function load(showMission = false) {
  const res = await fetch("api/bootstrap");
  const data = await res.json();
  render(data);
  window.MspCtfUi?.updateMission?.(data, { force: showMission });
}

els.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (busy) return;
  const message = els.prompt.value.trim();
  if (!message) return;
  setBusy(true, "Generating...");
  try {
    const res = await fetch("api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, request_id: createRequestId() }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Request failed");
    await load();
    showFlag(data.flag);
    els.prompt.value = "";
    setBusy(false, "Ready");
  } catch (error) {
    setBusy(false, error.message);
  }
});

els.reset.addEventListener("click", async () => {
  if (busy) return;
  setBusy(true, "Resetting...");
  await fetch("api/reset", { method: "POST" });
  els.prompt.value = "";
  showFlag(null);
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
