const threadId = crypto.randomUUID();

const chat = document.getElementById("chat");
const form = document.getElementById("composer");
const input = document.getElementById("message");
const sendButton = document.getElementById("send");

function createAvatar(role) {
  const avatar = document.createElement("div");
  avatar.className = "avatar";

  if (role === "assistant") {
    const img = document.createElement("img");
    img.src = "/static/icon.png";
    img.alt = "V-CEO";
    avatar.appendChild(img);
  } else {
    avatar.textContent = "D";
  }

  return avatar;
}

function scrollToBottom() {
  chat.scrollTop = chat.scrollHeight;
}

function appendMessage(role, text) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`;

  const avatar = createAvatar(role);

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  if (role === "assistant") {
    bubble.innerHTML = marked.parse(text);
  } else {
    bubble.textContent = text;
  }

  wrapper.appendChild(avatar);
  wrapper.appendChild(bubble);

  chat.appendChild(wrapper);

  scrollToBottom();

  return wrapper;
}

function showTypingIndicator() {
  const wrapper = document.createElement("div");
  wrapper.className = "message assistant typing-message";

  const avatar = createAvatar("assistant");

  const bubble = document.createElement("div");
  bubble.className = "bubble typing";

  bubble.innerHTML = `
      <span></span>
      <span></span>
      <span></span>
    `;

  wrapper.appendChild(avatar);
  wrapper.appendChild(bubble);

  chat.appendChild(wrapper);

  scrollToBottom();

  return wrapper;
}

async function sendMessage() {
  const message = input.value.trim();

  if (!message || sendButton.disabled) {
    return;
  }

  appendMessage("user", message);

  input.value = "";

  sendButton.disabled = true;

  const typingIndicator = showTypingIndicator();

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        thread_id: threadId,
      }),
    });

    const data = await response.json();

    typingIndicator.remove();

    if (!response.ok) {
      throw new Error(data.detail || "Request failed");
    }

    appendMessage("assistant", data.response);
  } catch (error) {
    typingIndicator.remove();

    appendMessage(
      "assistant",
      `⚠️ ${error.message}`
    );
  } finally {
    sendButton.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  await sendMessage();
});

input.addEventListener("keydown", async (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    await sendMessage();
  }
});