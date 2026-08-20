(() => {
  const documentListEl = document.getElementById("documentList");
  const fileInput = document.getElementById("fileInput");
  const dropArea = document.querySelector(".file-drop-area");
  const dropText = document.getElementById("dropText");
  const uploadBtn = document.getElementById("uploadBtn");
  const resetBtn = document.getElementById("resetBtn");
  const messagesEl = document.getElementById("messages");
  const chatForm = document.getElementById("chatForm");
  const promptInput = document.getElementById("prompt");
  const sendBtn = document.getElementById("sendBtn");
  const statusEl = document.getElementById("status");
  const flagEl = document.getElementById("flag");
  const sourcesEl = document.getElementById("sources");

  let state = {
    documents: [],
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

  function renderDocuments() {
    documentListEl.innerHTML = "";

    state.documents.forEach((doc) => {
      const item = document.createElement("div");
      item.className = `saved-doc ${doc.is_protected ? "protected" : ""}`;

      const title = document.createElement("strong");
      title.textContent = doc.title;

      const meta = document.createElement("small");
      meta.textContent = doc.is_protected
        ? "🔒 Enclave Restricted (Policy Sec-99)"
        : "📄 Custom Ingestion Chunk";

      item.appendChild(title);
      item.appendChild(meta);
      documentListEl.appendChild(item);
    });
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
      div.textContent = msg.content;
      messagesEl.appendChild(div);
    });
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function renderFlag(flag) {
    if (flag) {
      flagEl.textContent = `🚩 FLAG: ${flag}`;
      flagEl.classList.remove("hidden");
    } else {
      flagEl.classList.add("hidden");
    }
  }

  function renderSources(sources) {
    sourcesEl.innerHTML = "";
    if (!sources || sources.length === 0) return;

    sources.forEach((s) => {
      const item = document.createElement("div");
      item.className = "source";
      item.innerHTML = `<strong>${s.title}</strong><small>Vector Relevance Score: ${(s.score * 100).toFixed(1)}%</small>`;
      sourcesEl.appendChild(item);
    });
  }

  async function bootstrap() {
    setStatus("Loading...", true);
    try {
      const res = await fetch("api/bootstrap");
      const data = await res.json();
      state.documents = data.documents || [];
      state.messages = data.chat || [];
      state.solved = data.solved || false;
      renderDocuments();
      renderMessages();
      if (data.solved && data.flag) {
        renderFlag(data.flag);
      }
      setStatus("Ready", false);
    } catch (err) {
      console.error(err);
      setStatus("Error", false);
    }
  }

  async function uploadFile(file) {
    if (!file || state.busy) return;

    setStatus("Ingesting vector...", true);
    dropText.textContent = `Ingesting: ${file.name}...`;
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("api/upload", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (res.ok && data.ok) {
        state.documents.push(data.doc);
        renderDocuments();
        dropText.textContent = `✓ Ingested ${file.name}`;
      } else {
        alert(data.error || data.detail || "Upload rejected by Ingestion Guard.");
        dropText.textContent = "Click or drop .txt/.md memo here";
      }
    } catch (err) {
      alert("Failed to upload document.");
      dropText.textContent = "Click or drop .txt/.md memo here";
    } finally {
      fileInput.value = "";
      setStatus("Ready", false);
    }
  }

  uploadBtn.addEventListener("click", () => {
    fileInput.click();
  });

  fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (file) uploadFile(file);
  });

  if (dropArea) {
    dropArea.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropArea.style.borderColor = "var(--accent)";
    });
    dropArea.addEventListener("dragleave", (e) => {
      e.preventDefault();
      dropArea.style.borderColor = "";
    });
    dropArea.addEventListener("drop", (e) => {
      e.preventDefault();
      dropArea.style.borderColor = "";
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        uploadFile(e.dataTransfer.files[0]);
      }
    });
  }

  resetBtn.addEventListener("click", async () => {
    if (!confirm("Reset all uploaded documents and conversation history?")) return;
    setStatus("Resetting...", true);
    try {
      const res = await fetch("api/reset", { method: "POST" });
      const data = await res.json();
      state.documents = data.state.documents || [];
      state.messages = [];
      state.solved = false;
      dropText.textContent = "Click or drop .txt/.md memo here";
      renderDocuments();
      renderMessages();
      renderFlag(null);
      renderSources([]);
      setStatus("Ready", false);
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
    setStatus("Searching vectors & generating...", true);

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
      renderSources(data.sources);

      if (data.solved && data.flag) {
        state.solved = true;
        renderFlag(data.flag);
      }
    } catch (err) {
      state.messages.push({
        role: "assistant",
        content: "Error: Unable to connect to the vector inference engine.",
      });
      renderMessages();
    } finally {
      state.busy = false;
      sendBtn.disabled = false;
      setStatus("Ready", false);
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
