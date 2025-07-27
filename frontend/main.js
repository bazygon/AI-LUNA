<<<<<<< HEAD
// frontend/main.js
document.addEventListener('DOMContentLoaded', () => {
  const params    = new URLSearchParams(location.search);
  const diva      = params.get('diva') || localStorage.getItem("divaKey") || 'Diva';
  const avatarUrl = params.get('avatar') || localStorage.getItem("divaAvatar");
  const chatBox   = document.getElementById('chat-box');
  const input     = document.getElementById('user-input');
  const btn       = document.getElementById('send-button');
  let chatHistory = [];

  // Diva name
  const divaNameEl = document.getElementById('diva-name');
  if (divaNameEl) divaNameEl.textContent = diva.charAt(0).toUpperCase() + diva.slice(1);

  // Avatar
  const divaAvatar = document.getElementById('diva-avatar');
  if (divaAvatar && avatarUrl) {
    divaAvatar.src = avatarUrl;
  }

  // Append message helper
  function appendMessage(who, text) {
    const d = document.createElement('div');
    d.classList.add('message', who === 'user' ? 'user' : 'ai');
    if (who === 'user') {
      d.innerHTML = `<strong>You:</strong> ${text}`;
    } else {
      d.innerHTML = `<strong>${diva}:</strong> `;
    }
    chatBox.appendChild(d);
    chatBox.scrollTop = chatBox.scrollHeight;
    return d;
  }

  // Typing indicator
  function showTyping() {
    btn.disabled = input.disabled = true;
    const t = document.createElement('div');
    t.className = 'typing-indicator';
    t.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
    chatBox.appendChild(t);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function hideTyping() {
    btn.disabled = input.disabled = false;
    const t = chatBox.querySelector('.typing-indicator');
    if (t) t.remove();
  }

  // Send & Stream
  async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;
    appendMessage('user', text);
    chatHistory.push({ role: 'user', content: text });
    input.value = '';
    showTyping();

    try {
      const res = await fetch('/chat_stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ diva, history: chatHistory, message: text })
      });

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split('\n\n');
        buffer = parts.pop();
        for (const block of parts) {
          if (!block.startsWith('data:')) continue;
          const token = block.replace(/^data:\s*/, '');
          if (token === '[DONE]') continue;

          let last = chatBox.querySelector('.message.ai:last-child');
          if (!last) last = appendMessage('ai', '');
          const needsSpace = !/\s$/.test(last.textContent) && !/^\s/.test(token);
          last.textContent += (needsSpace ? ' ' : '') + token;
          chatBox.scrollTop = chatBox.scrollHeight;
        }
      }

      hideTyping();
      const full = chatBox.querySelector('.message.ai:last-child').textContent;
      chatHistory.push({ role: 'assistant', content: full });
    } catch (error) {
      hideTyping();
      appendMessage('ai', '⚠️ Error: Unable to connect. Please try again later.');
      console.error('Chat stream error:', error);
    }
  }

  // Event bindings
  btn?.addEventListener('click', sendMessage);
  input?.addEventListener('keypress', e => {
    if (e.key === 'Enter') {
      e.preventDefault();
      sendMessage();
    }
  });

  // Night mode toggle handling (if present on page)
  const toggle = document.getElementById('modeToggle');
  const body = document.body;

  if (toggle) {
    if (localStorage.getItem('theme') === 'light') {
      body.classList.add('light-mode');
      toggle.checked = true;
    }

    toggle.addEventListener('change', () => {
      if (toggle.checked) {
        body.classList.add('light-mode');
        localStorage.setItem('theme', 'light');
      } else {
        body.classList.remove('light-mode');
        localStorage.setItem('theme', 'dark');
      }
    });
  }
});
=======
const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');

sendButton.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', function(e) {
  if (e.key === 'Enter') sendMessage();
});

async function sendMessage() {
  const message = userInput.value.trim();
  if (!message) return;
  appendMessage('user', message);
  userInput.value = '';
  try {
    const response = await fetch('/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message})
    });
    const data = await response.json();
    appendMessage('ai', data.reply);
  } catch (err) {
    appendMessage('ai', 'Błąd serwera: ' + err.message);
  }
}

function appendMessage(sender, text) {
  const msgDiv = document.createElement('div');
  msgDiv.className = sender === 'user' ? 'user-msg' : 'ai-msg';
  msgDiv.innerText = text;
  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}
>>>>>>> 0bbfa77aa1e33e9faf44f7bc948d05eb6373f508
