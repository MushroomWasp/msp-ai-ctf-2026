const els = {
  folders: document.getElementById("folderList"),
  memory: document.getElementById("memoryList"),
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

function render(data) {
  els.folders.innerHTML = data.folders
    .map((folder) => `<div class="folder"><strong>${folder.id}</strong><div>${folder.title}</div><small>${folder.status}</small></div>`)
    .join("");
  els.memory.innerHTML = data.memory_notes.map((note) => `<div class="memory">${note}</div>`).join("");
  els.messages.classList.toggle("empty", data.chat.length === 0);
  els.messages.innerHTML = data.chat.map((item) => `<div class="msg ${item.role}">${item.content}</div>`).join("");
  showFlag(data.flag || null);
}

function setBusy(next, text = "Ready") {
  busy = next;
  els.send.disabled = next;
  els.reset.disabled = next;
  els.status.textContent = text;
}

function showFlag(flag) {
  els.flag.classList.toggle("hidden", !flag);
  if (flag) {
    els.flag.textContent = `Challenge solved\n${flag}\nConcept: Saved conversation state becomes a trust boundary.`;
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
  setBusy(true, "Saving and checking...");
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
  if (busy) return;
  setBusy(true, "Resetting...");
  await fetch("api/reset", { method: "POST" });
  showFlag(null);
  els.prompt.value = "";
  await load(true);
  setBusy(false, "Ready");
});

load(true);
