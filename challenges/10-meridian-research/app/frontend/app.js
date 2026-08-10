const els = {
  vendors: document.getElementById("vendors"),
  uploads: document.getElementById("uploads"),
  messages: document.getElementById("messages"),
  file: document.getElementById("fileInput"),
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
  els.vendors.innerHTML = data.vendors
    .map((vendor) => `<div class="vendor"><strong>${vendor.name}</strong><div>${vendor.vendor_id}</div><small>${vendor.risk} risk</small></div>`)
    .join("");
  els.uploads.innerHTML = data.uploads
    .map((item) => `<div class="upload-item">${item.name}</div>`)
    .join("");
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
    els.flag.textContent = `Challenge solved\n${flag}\nConcept: Indirect injection plus retrieval plus under-authorized tools can chain into a full workflow break.`;
  }
}

async function load(showMission = false) {
  const res = await fetch("api/bootstrap");
  const data = await res.json();
  render(data);
  window.MspCtfUi?.updateMission?.(data, { force: showMission });
}

els.file.addEventListener("change", async () => {
  const file = els.file.files[0];
  if (!file || busy) return;
  setBusy(true, "Uploading...");
  try {
    const body = new FormData();
    body.append("file", file);
    const res = await fetch("api/upload", { method: "POST", body });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Upload failed");
    await load();
    setBusy(false, "Ready");
  } catch (error) {
    setBusy(false, error.message);
  } finally {
    els.file.value = "";
  }
});

els.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (busy) return;
  const message = els.prompt.value.trim();
  if (!message) return;
  setBusy(true, "Running agent...");
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
