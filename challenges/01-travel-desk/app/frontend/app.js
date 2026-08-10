const els = {
  tripCard: document.getElementById("tripCard"),
  perks: document.getElementById("perks"),
  messages: document.getElementById("messages"),
  form: document.getElementById("chatForm"),
  prompt: document.getElementById("prompt"),
  send: document.getElementById("sendBtn"),
  reset: document.getElementById("resetBtn"),
  status: document.getElementById("status"),
  flag: document.getElementById("flag"),
};

let state = { busy: false };

function renderMessages(chat = []) {
  els.messages.classList.toggle("empty", chat.length === 0);
  els.messages.innerHTML = chat
    .map((item) => `<div class="msg ${item.role}">${item.content}</div>`)
    .join("");
  els.messages.scrollTop = els.messages.scrollHeight;
}

function renderBootstrap(data) {
  const trip = data.traveler.trip;
  els.tripCard.innerHTML = `
    <strong>${data.traveler.name}</strong>
    <span>${data.traveler.title}</span>
    <span>${trip.flight} · ${trip.destination}</span>
    <span>${trip.departure}</span>
    <span>${trip.purpose}</span>
  `;
  els.perks.innerHTML = data.perks
    .map((perk) => `<div class="perk"><span>${perk.name}</span><strong>${perk.status}</strong></div>`)
    .join("");
  renderMessages(data.chat);
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
    els.flag.textContent = `Challenge solved\n${flag}\nConcept: Prompt-only policy text is not access control.`;
  }
}

async function load() {
  const res = await fetch("api/bootstrap");
  const data = await res.json();
  renderBootstrap(data);
}

els.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (state.busy) return;
  const message = els.prompt.value.trim();
  if (!message) return;
  setBusy(true, "Concierge is thinking...");
  try {
    const res = await fetch("api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, request_id: crypto.randomUUID() }),
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
  await load();
  setBusy(false, "Ready");
});

load();
