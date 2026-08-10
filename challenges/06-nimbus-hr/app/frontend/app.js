const els = {
  notes: document.getElementById("notes"),
  sources: document.getElementById("sources"),
  messages: document.getElementById("messages"),
  noteForm: document.getElementById("noteForm"),
  noteInput: document.getElementById("noteInput"),
  noteBtn: document.getElementById("noteBtn"),
  chatForm: document.getElementById("chatForm"),
  prompt: document.getElementById("prompt"),
  send: document.getElementById("sendBtn"),
  reset: document.getElementById("resetBtn"),
  status: document.getElementById("status"),
  flag: document.getElementById("flag"),
};

let busy = false;
const createRequestId = () =>
  window.MspCtfUi?.requestId?.() || `req-${Date.now()}-${Math.random().toString(16).slice(2)}`;

function render(data) {
  els.notes.innerHTML = data.notes.map((note) => `<div class="saved-note">${note}</div>`).join("");
  els.messages.classList.toggle("empty", data.chat.length === 0);
  els.messages.innerHTML = data.chat.map((item) => `<div class="msg ${item.role}">${item.content}</div>`).join("");
  els.sources.innerHTML = data.sources
    .map((src) => `<div class="source"><strong>${src.source}</strong><small>${src.trust}</small></div>`)
    .join("");
  showFlag(data.flag || null);
}

function setBusy(next, text = "Ready") {
  busy = next;
  els.noteBtn.disabled = next;
  els.send.disabled = next;
  els.reset.disabled = next;
  els.status.textContent = text;
}

function showFlag(flag) {
  els.flag.classList.toggle("hidden", !flag);
  if (flag) {
    els.flag.textContent = `Challenge solved\n${flag}\nConcept: Retrieved context needs provenance boundaries, not equal trust.`;
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
  const note = els.noteInput.value.trim();
  if (!note) return;
  setBusy(true, "Saving note...");
  try {
    const res = await fetch("api/notes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ note }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Save failed");
    els.noteInput.value = "";
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
  setBusy(true, "Searching...");
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
  els.noteInput.value = "";
  await load(true);
  setBusy(false, "Ready");
});

load(true);
