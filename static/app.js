const form = document.querySelector('#chat-form');
const input = document.querySelector('#message-input');
const conversation = document.querySelector('#conversation');
const sendButton = form.querySelector('.send-button');
const clearButton = document.querySelector('#clear-chat');
const promptButtons = document.querySelectorAll('[data-prompt]');

let messages = [];

function addMessage(role, text) {
  let list = conversation.querySelector('.message-list');
  if (!list) {
    conversation.innerHTML = '<div class="message-list"></div>';
    list = conversation.querySelector('.message-list');
  }

  const message = document.createElement('div');
  message.className = `message ${role}`;
  const label = role === 'user' ? 'you' : 'tr';
  message.innerHTML = `<div class="message-label">${label}</div><div class="message-body"></div>`;
  message.querySelector('.message-body').textContent = text;
  list.appendChild(message);
  conversation.scrollTop = conversation.scrollHeight;
}

function addTypingIndicator() {
  const list = conversation.querySelector('.message-list');
  const message = document.createElement('div');
  message.className = 'message assistant typing';
  message.innerHTML = '<div class="message-label">tr</div><div class="message-body"><span class="typing-dots"><i></i><i></i><i></i></span></div>';
  list.appendChild(message);
  conversation.scrollTop = conversation.scrollHeight;
  return message;
}

async function sendMessage(text) {
  const cleanText = text.trim();
  if (!cleanText || sendButton.disabled) return;

  messages.push({ role: 'user', content: cleanText });
  addMessage('user', cleanText);
  input.value = '';
  input.style.height = 'auto';
  sendButton.disabled = true;
  const typing = addTypingIndicator();

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'The teacher could not respond.');
    messages.push({ role: 'assistant', content: data.response });
    typing.remove();
    addMessage('assistant', data.response);
  } catch (error) {
    typing.remove();
    addMessage('assistant', `There was a problem: ${error.message}`);
  } finally {
    sendButton.disabled = false;
    input.focus();
  }
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  sendMessage(input.value);
});

input.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

input.addEventListener('input', () => {
  input.style.height = 'auto';
  input.style.height = `${Math.min(input.scrollHeight, 130)}px`;
});

promptButtons.forEach((button) => {
  button.addEventListener('click', () => {
    input.value = button.dataset.prompt;
    input.dispatchEvent(new Event('input'));
    input.focus();
  });
});

clearButton.addEventListener('click', () => {
  messages = [];
  conversation.innerHTML = `<div class="welcome-message"><div class="welcome-kicker">A question is a good place to begin.</div><h3>What are you working<br>through today?</h3><p>Bring a problem, a half-formed idea, or something that still feels foggy. We will take it one step at a time.</p></div><div class="prompt-grid" aria-label="Starter questions"><button class="prompt-chip" type="button" data-prompt="Help me understand this concept step by step.">Understand a concept <span aria-hidden="true">-&gt;</span></button><button class="prompt-chip" type="button" data-prompt="I am stuck on a problem. Help me find the next step without giving me the answer.">Find the next step <span aria-hidden="true">-&gt;</span></button><button class="prompt-chip" type="button" data-prompt="Quiz me on a topic and adjust the difficulty as we go.">Practice together <span aria-hidden="true">-&gt;</span></button></div>`;
  conversation.querySelectorAll('[data-prompt]').forEach((button) => button.addEventListener('click', () => {
    input.value = button.dataset.prompt;
    input.dispatchEvent(new Event('input'));
    input.focus();
  }));
});
