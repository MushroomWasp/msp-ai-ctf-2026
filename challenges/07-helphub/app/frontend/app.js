const els = {
  customerName: document.getElementById("customerName"),
  customerMeta: document.getElementById("customerMeta"),
  noteForm: document.getElementById("noteForm"),
  noteInput: document.getElementById("noteInput"),
  saveBtn: document.getElementById("saveBtn"),
  chatForm: document.getElementById("chatForm"),
  prompt: document.getElementById("prompt"),
  send: document.getElementById("sendBtn"),
  reset: document.getElementById("resetBtn"),
  messages: document.getElementById("messages"),
  status: document.getElementById("status"),
  flag: document.getElementById("flag"),
};

let busy = false;
const createRequestId = () =>
  window.MspCtfUi?.requestId?.() || `req-${Date.now()}-${Math.random().toString(16).slice(2)}`;

function render(data) {
  els.customerName.textContent = data.customer.name;
  els.customerMeta.innerHTML = `
    <div>${data.customer.company}</div>
    <div>${data.customer.plan} plan</div>
    <div>${data.customer.ticket}</div>
  `;
  els.noteInput.value = data.customer_note;
  els.messages.classList.toggle("empty", data.chat.length === 0);
  els.messages.innerHTML = data.chat.map((item) => `<div class="msg ${item.role}">${item.content}</div>`).join("");
  showFlag(data.flag || null);
}

function setBusy(next, text = "Ready") {
  busy = next;
  els.saveBtn.disabled = next;
  els.send.disabled = next;
  els.reset.disabled = next;
  els.status.textContent = text;
}

function showFlag(flag) {
  els.flag.classList.toggle("hidden", !flag);
  if (flag) {
    els.flag.textContent = `Challenge solved\n${flag}\nConcept: Stored customer content can later steer a privileged AI workflow.`;
  }
}

async function load(showMission = false) {
  const res = await fetch("api/bootstrap");
  const data = await res.json();
  render(data);
  window.MspCtfUi?.updateMission?.(data, { force: showMission });
}

els.noteForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (busy) return;
  setBusy(true, "Saving note...");
  try {
    const res = await fetch("api/customer-note", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ note: els.noteInput.value }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Save failed");
    await load();
    setBusy(false, "Ready");
  } catch (error) {
    setBusy(false, error.message);
  }
});

els.chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (busy) return;
  const message = els.prompt.value.trim();
  if (!message) return;
  setBusy(true, "Drafting...");
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
    showFlag(data.flag);
    setBusy(false, "Ready");
  } catch (error) {
    setBusy(false, error.message);
  }
});

els.reset.addEventListener("click", async () => {
  if (busy) return;
  setBusy(true, "Resetting...");
  await fetch("api/reset", { method: "POST" });
  showFlag(null);
  els.prompt.value = "";
  await load(true);
  setBusy(false, "Ready");
});

load(true);
