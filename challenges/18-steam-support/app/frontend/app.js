(() => {
  const resetBtn = document.getElementById("resetBtn");
  const messagesEl = document.getElementById("messages");
  const chatForm = document.getElementById("chatForm");
  const promptInput = document.getElementById("prompt");
  const sendBtn = document.getElementById("sendBtn");
  const statusEl = document.getElementById("status");
  const flagEl = document.getElementById("flag");

  let state = {
    messages: [],
    solved: false,
    busy: false,
  };

  function setStatus(text, isBusy = false) {
    statusEl.textContent = text;
    if (isBusy) {
      statusEl.classList.add("busy");
    } else {
      statusEl.classList.remove("busy");
    }
  }

  function renderMessages() {
    messagesEl.innerHTML = "";
    if (state.messages.length === 0) {
      messagesEl.className = "messages empty";
      return;
    }

    messagesEl.className = "messages";
    state.messages.forEach((msg) => {
      const div = document.createElement("div");
      div.className = `msg ${msg.role}`;

      const sender = document.createElement("span");
      sender.className = "msg-sender";
      sender.textContent = msg.role === "assistant" ? "xX_N00b_S14y3r_420_Xx" : "You";

      const content = document.createElement("div");
      content.textContent = msg.content;

      div.appendChild(sender);
      div.appendChild(content);
      messagesEl.appendChild(div);
    });
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function renderFlag(flag) {
    if (flag) {
      flagEl.textContent = `🚩 FLAG SOLVED: ${flag}`;
      flagEl.classList.remove("hidden");
    } else {
      flagEl.classList.add("hidden");
    }
  }

  async function bootstrap() {
    setStatus("Connecting...", true);
    try {
      const res = await fetch("api/bootstrap");
      const data = await res.json();
      state.messages = data.chat || [];
      state.solved = data.solved || false;
      renderMessages();
      if (data.solved && data.flag) {
        renderFlag(data.flag);
      }
      setStatus("Online", false);
    } catch (err) {
      console.error(err);
      setStatus("Error", false);
    }
  }

  resetBtn.addEventListener("click", async () => {
    if (!confirm("Reset chat history with the target gamer?")) return;
    setStatus("Resetting...", true);
    try {
      await fetch("api/reset", { method: "POST" });
      state.messages = [];
      state.solved = false;
      renderMessages();
      renderFlag(null);
      setStatus("Online", false);
    } catch (err) {
      alert("Failed to reset session.");
      setStatus("Error", false);
    }
  });

  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = promptInput.value.trim();
    if (!query || state.busy) return;

    state.busy = true;
    sendBtn.disabled = true;
    setStatus("Typing...", true);

    state.messages.push({ role: "user", content: query });
    renderMessages();
    promptInput.value = "";

    try {
      const res = await fetch("api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: query }),
      });
      const data = await res.json();

      state.messages.push({ role: "assistant", content: data.reply });
      renderMessages();

      if (data.solved && data.flag) {
        state.solved = true;
        renderFlag(data.flag);
      }
    } catch (err) {
      state.messages.push({
        role: "assistant",
        content: "Error: Steam Friends Network communication timed out.",
      });
      renderMessages();
    } finally {
      state.busy = false;
      sendBtn.disabled = false;
      setStatus("Online", false);
    }
  });

  promptInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      chatForm.requestSubmit();
    }
  });

  bootstrap();
})();
