import { api, ws, getToken, clearToken } from './api.js';

let socket = null;
let currentRoomId = null;
let typingTimeout = null;
let typingUsers = new Map();
let currentUser = null;

export function isAuthenticated() {
  return !!getToken();
}

export async function getCurrentUser() {
  if (!currentUser) {
    currentUser = await api.users.getProfile();
  }
  return currentUser;
}

export function logout() {
  clearToken();
  currentUser = null;
  disconnectWebSocket();
  window.location.hash = '#login';
}

const messageHandlers = [];
const typingHandlers = [];
const notificationHandlers = [];

export function onMessage(handler) {
  messageHandlers.push(handler);
}

export function onTyping(handler) {
  typingHandlers.push(handler);
}

export function onNotification(handler) {
  notificationHandlers.push(handler);
}

function emitMessage(message) {
  messageHandlers.forEach(h => h(message));
}

function emitTyping(data) {
  typingHandlers.forEach(h => h(data));
}

function emitNotification(notification) {
  notificationHandlers.forEach(h => h(notification));
}

export function connectWebSocket() {
  if (socket) return;

  socket = ws.connect(
    (message) => emitMessage(message),
    (typing) => emitTyping(typing),
    (notification) => emitNotification(notification)
  );
}

export function disconnectWebSocket() {
  if (socket) {
    socket.close();
    socket = null;
  }
}

export function sendTypingIndicator(roomId) {
  if (socket) {
    ws.send(socket, 'typing', { room_id: roomId, is_typing: true });
  }
  api.typing.setTyping(roomId, true).catch(() => {});

  clearTimeout(typingTimeout);
  typingTimeout = setTimeout(() => {
    if (socket) {
      ws.send(socket, 'typing', { room_id: roomId, is_typing: false });
    }
    api.typing.setTyping(roomId, false).catch(() => {});
  }, 3000);
}

export async function loadMessages(roomId) {
  currentRoomId = roomId;
  return api.messages.list(roomId);
}

export async function sendMessage(roomId, content, replyToId = null) {
  if (replyToId) {
    return api.messages.reply(roomId, replyToId, content);
  }
  return api.messages.send(roomId, content);
}

export async function getTypingUsers(roomId) {
  try {
    const users = await api.typing.getTypingUsers(roomId);
    users.forEach(u => typingUsers.set(u.user_id, u));
    return users;
  } catch {
    return [];
  }
}

export function formatTimestamp(date) {
  const d = new Date(date);
  const now = new Date();
  const diff = now - d;

  if (diff < 60000) return 'just now';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;

  if (d.toDateString() === now.toDateString()) {
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
  return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
}

export function renderMessage(message, currentUserId) {
  const div = document.createElement('div');
  div.className = 'message';
  div.dataset.id = message.id;

  const isOwn = message.user_id === currentUserId;
  const time = formatTimestamp(message.created_at);

  let replyHtml = '';
  if (message.reply_to_id && message.reply_to_content) {
    replyHtml = `
      <div class="message-reply">
        <span class="reply-label">Replying to:</span>
        <span class="reply-content">${escapeHtml(message.reply_to_content)}</span>
      </div>
    `;
  }

  const highlightMentions = (text) => {
    const escaped = escapeHtml(text);
    return escaped.replace(/@(\w+)/g, '<span class="mention">@$1</span>');
  };

  div.innerHTML = `
    <div class="message-header">
      <span class="message-username">${escapeHtml(message.username)}</span>
      <span class="message-time">${time}</span>
    </div>
    ${replyHtml}
    <div class="message-content">${highlightMentions(message.content)}</div>
    <div class="message-actions">
      <button class="reply-btn" data-id="${message.id}" data-content="${escapeHtml(message.content)}">Reply</button>
    </div>
  `;

  return div;
}

export function renderTypingIndicator(users) {
  if (users.length === 0) {
    return '';
  }

  if (users.length === 1) {
    return `<div class="typing-indicator">${escapeHtml(users[0].username)} is typing...</div>`;
  }

  if (users.length === 2) {
    return `<div class="typing-indicator">${escapeHtml(users[0].username)} and ${escapeHtml(users[1].username)} are typing...</div>`;
  }

  return `<div class="typing-indicator">Several people are typing...</div>`;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

export class ChatManager {
  constructor() {
    this.messagesContainer = null;
    this.typingContainer = null;
    this.inputArea = null;
    this.currentUserId = null;
    this.replyToId = null;
    this.replyToContent = null;
  }

  init({ messagesContainer, typingContainer, inputArea }) {
    this.messagesContainer = messagesContainer;
    this.typingContainer = typingContainer;
    this.inputArea = inputArea;

    if (this.inputArea) {
      this.inputArea.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this.handleSend();
        }
      });

      this.inputArea.addEventListener('input', () => {
        if (currentRoomId) {
          sendTypingIndicator(currentRoomId);
        }
      });
    }

    onTyping((data) => {
      if (data.room_id === currentRoomId) {
        if (data.is_typing) {
          typingUsers.set(data.user_id, { user_id: data.user_id, username: data.username });
        } else {
          typingUsers.delete(data.user_id);
        }
        this.updateTypingDisplay();
      }
    });

    onMessage((message) => {
      if (message.room_id === currentRoomId) {
        this.appendMessage(message);
      }
    });
  }

  setCurrentUser(userId) {
    this.currentUserId = userId;
  }

  async loadRoom(roomId) {
    currentRoomId = roomId;
    typingUsers.clear();
    this.messagesContainer.innerHTML = '';

    const messages = await loadMessages(roomId);
    messages.forEach(m => this.appendMessage(m, false));

    this.scrollToBottom();
    this.updateTypingDisplay();

    getTypingUsers(roomId).then(users => {
      users.forEach(u => typingUsers.set(u.user_id, u));
      this.updateTypingDisplay();
    });
  }

  appendMessage(message, scroll = true) {
    const el = renderMessage(message, this.currentUserId);

    el.querySelector('.reply-btn').addEventListener('click', () => {
      this.setReplyTo(message.id, message.content);
    });

    this.messagesContainer.appendChild(el);
    if (scroll) this.scrollToBottom();
  }

  setReplyTo(messageId, content) {
    this.replyToId = messageId;
    this.replyToContent = content;

    const replyIndicator = document.getElementById('reply-indicator');
    if (replyIndicator) {
      replyIndicator.innerHTML = `
        <span>Replying to: ${escapeHtml(content)}</span>
        <button id="cancel-reply">×</button>
      `;
      replyIndicator.style.display = 'flex';
      document.getElementById('cancel-reply').addEventListener('click', () => {
        this.cancelReply();
      });
    }
  }

  cancelReply() {
    this.replyToId = null;
    this.replyToContent = null;
    const replyIndicator = document.getElementById('reply-indicator');
    if (replyIndicator) {
      replyIndicator.style.display = 'none';
    }
  }

  async handleSend() {
    const content = this.inputArea.value.trim();
    if (!content || !currentRoomId) return;

    this.inputArea.value = '';
    this.cancelReply();

    try {
      await sendMessage(currentRoomId, content, this.replyToId);
      this.replyToId = null;
      this.replyToContent = null;
    } catch (err) {
      alert('Failed to send message: ' + err.message);
    }
  }

  updateTypingDisplay() {
    if (!this.typingContainer) return;
    const users = Array.from(typingUsers.values()).filter(u => u.user_id !== this.currentUserId);
    this.typingContainer.innerHTML = renderTypingIndicator(users);
  }

  scrollToBottom() {
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
  }
}

export const chatManager = new ChatManager();