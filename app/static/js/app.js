import { api, getToken } from './api.js';
import { isAuthenticated, getCurrentUser, logout } from './chat.js';

let currentUser = null;
let pollingIntervals = [];

function startPolling(key, fn, interval) {
  stopPolling(key);
  const id = setInterval(fn, interval);
  pollingIntervals.push({ key, id });
}

function stopPolling(key) {
  pollingIntervals = pollingIntervals.filter(p => {
    if (p.key === key) {
      clearInterval(p.id);
      return false;
    }
    return true;
  });
}

function stopAllPolling() {
  pollingIntervals.forEach(p => clearInterval(p.id));
  pollingIntervals = [];
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text || '';
  return div.innerHTML;
}

function highlightMentions(text) {
  const escaped = escapeHtml(text);
  return escaped.replace(/@(\w+)/g, '<span class="mention">@$1</span>');
}

function renderNavbar() {
  return `
    <nav class="navbar">
      <div class="nav-brand">OutoChat</div>
      <div class="nav-links">
        <a href="#dashboard">Dashboard</a>
        <a href="#friends">Friends</a>
        <a href="#notifications">Notifications <span class="notification-badge" style="display:none;"></span></a>
        <a href="#settings">Settings</a>
        <button id="logout-btn">Logout</button>
      </div>
    </nav>
  `;
}

async function renderLogin(container) {
  container.innerHTML = `
    <div class="auth-container">
      <div class="auth-card">
        <h1 class="auth-logo">Outo</h1>
        <p class="auth-tagline">Self-hosted chat server</p>
        <form id="login-form" class="auth-form">
          <div id="login-error" class="error" style="display:none;"></div>
          <input type="text" name="username" placeholder="Username" required minlength="3" maxlength="50">
          <input type="password" name="password" placeholder="Password" required minlength="8">
          <button type="submit" class="btn-primary">Sign In</button>
          <p class="auth-switch">Don't have an account? <a href="#register">Register</a></p>
        </form>
      </div>
    </div>
  `;

  document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const username = form.username.value;
    const password = form.password.value;
    const errorEl = document.getElementById('login-error');

    try {
      await api.auth.login(username, password);
      currentUser = await api.users.getProfile();
      window.location.hash = '#dashboard';
    } catch (err) {
      errorEl.textContent = err.message;
      errorEl.style.display = 'block';
    }
  });
}

async function renderRegister(container) {
  container.innerHTML = `
    <div class="auth-container">
      <div class="auth-card">
        <h1 class="auth-logo">Outo</h1>
        <p class="auth-tagline">Create account</p>
        <form id="register-form" class="auth-form">
          <div id="register-error" class="error" style="display:none;"></div>
          <input type="text" name="username" placeholder="Username (3-50 chars)" required minlength="3" maxlength="50">
          <input type="password" name="password" placeholder="Password (8+ chars)" required minlength="8">
          <button type="submit" class="btn-primary">Create Account</button>
          <p class="auth-switch">Already have an account? <a href="#login">Sign In</a></p>
        </form>
      </div>
    </div>
  `;

  document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const username = form.username.value;
    const password = form.password.value;
    const errorEl = document.getElementById('register-error');

    try {
      await api.auth.register(username, password);
      await api.auth.login(username, password);
      currentUser = await api.users.getProfile();
      window.location.hash = '#dashboard';
    } catch (err) {
      errorEl.textContent = err.message;
      errorEl.style.display = 'block';
    }
  });
}

async function renderDashboard(container) {
  const workspaces = await api.workspaces.list();

  container.innerHTML = `
    ${renderNavbar()}
    <div class="view-content">
      <h1>Your Workspaces</h1>
      <div class="workspace-actions">
        <button id="create-workspace-btn" class="btn-primary">Create Workspace</button>
        <button id="join-workspace-btn" class="btn-secondary">Join Workspace</button>
      </div>
      <div id="workspace-form" style="display:none; margin-top: 1rem;">
        <input type="text" id="workspace-name" placeholder="Workspace name">
        <button id="submit-workspace">Create</button>
      </div>
      <div id="join-form" style="display:none; margin-top: 1rem;">
        <input type="text" id="workspace-id-input" placeholder="Enter workspace ID">
        <button id="submit-join">Join</button>
      </div>
      <div class="workspace-list">
        ${workspaces.length === 0 ? '<p>No workspaces yet. Create or join one!</p>' : ''}
        ${workspaces.map(ws => `
          <div class="workspace-card" data-id="${ws.id}">
            <h3>${escapeHtml(ws.name)}</h3>
            <p class="workspace-id">ID: ${ws.id}</p>
            <p>${ws.member_count} members</p>
            <button class="view-rooms-btn" data-id="${ws.id}">View Rooms</button>
            ${ws.owner_id === currentUser.id ? `<button class="delete-workspace-btn" data-id="${ws.id}">Delete</button>` : ''}
          </div>
        `).join('')}
      </div>
    </div>
  `;

  document.getElementById('logout-btn').addEventListener('click', logout);
  
  document.getElementById('create-workspace-btn').addEventListener('click', () => {
    document.getElementById('workspace-form').style.display = 'block';
    document.getElementById('join-form').style.display = 'none';
  });

  document.getElementById('join-workspace-btn').addEventListener('click', () => {
    document.getElementById('join-form').style.display = 'block';
    document.getElementById('workspace-form').style.display = 'none';
  });

  document.getElementById('submit-workspace').addEventListener('click', async () => {
    const name = document.getElementById('workspace-name').value.trim();
    if (!name) return;
    try {
      await api.workspaces.create(name);
      renderDashboard(container);
    } catch (err) {
      alert(err.message);
    }
  });

  document.getElementById('submit-join').addEventListener('click', async () => {
    const workspaceId = document.getElementById('workspace-id-input').value.trim();
    if (!workspaceId) return;
    try {
      await api.workspaces.join(workspaceId);
      renderDashboard(container);
    } catch (err) {
      alert(err.message);
    }
  });

  container.querySelectorAll('.delete-workspace-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      if (confirm('Delete this workspace?')) {
        try {
          await api.workspaces.delete(e.target.dataset.id);
          renderDashboard(container);
        } catch (err) {
          alert(err.message);
        }
      }
    });
  });

  container.querySelectorAll('.view-rooms-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      window.location.hash = `#chat?workspace=${e.target.dataset.id}`;
    });
  });

  startPolling('workspaces', async () => {
    try {
      const newWorkspaces = await api.workspaces.list();
      const listEl = container.querySelector('.workspace-list');
      if (listEl) {
        listEl.innerHTML = newWorkspaces.length === 0 ? '<p>No workspaces yet. Create or join one!</p>' : '';
        newWorkspaces.forEach(ws => {
          const div = document.createElement('div');
          div.className = 'workspace-card';
          div.dataset.id = ws.id;
          div.innerHTML = `
            <h3>${escapeHtml(ws.name)}</h3>
            <p class="workspace-id">ID: ${ws.id}</p>
            <p>${ws.member_count} members</p>
            <button class="view-rooms-btn" data-id="${ws.id}">View Rooms</button>
            ${ws.owner_id === currentUser.id ? `<button class="delete-workspace-btn" data-id="${ws.id}">Delete</button>` : ''}
          `;
          listEl.appendChild(div);
        });
      }
    } catch (err) {
      console.error('Poll workspaces error:', err);
    }
  }, 10000);
}

async function renderFriends(container) {
  const friends = await api.friends.list();

  container.innerHTML = `
    ${renderNavbar()}
    <div class="view-content">
      <h1>Friends</h1>
      <div class="add-friend-form">
        <input type="text" id="friend-id-input" placeholder="Enter user ID">
        <button id="add-friend-btn">Add Friend</button>
      </div>
      <div class="friend-list">
        ${friends.length === 0 ? '<p>No friends yet.</p>' : ''}
        ${friends.map(f => `
          <div class="friend-card">
            <span class="friend-name">${escapeHtml(f.display_name || f.username)}</span>
            <button class="remove-friend-btn" data-id="${f.id}">Remove</button>
          </div>
        `).join('')}
      </div>
    </div>
  `;

  document.getElementById('logout-btn').addEventListener('click', logout);

  document.getElementById('add-friend-btn').addEventListener('click', async () => {
    const friendId = document.getElementById('friend-id-input').value.trim();
    if (!friendId) return;
    try {
      await api.friends.add(friendId);
      renderFriends(container);
    } catch (err) {
      alert(err.message);
    }
  });

  container.querySelectorAll('.remove-friend-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      if (confirm('Remove this friend?')) {
        try {
          await api.friends.remove(e.target.dataset.id);
          renderFriends(container);
        } catch (err) {
          alert(err.message);
        }
      }
    });
  });
}

async function renderNotifications(container) {
  const notifications = await api.notifications.list();

  container.innerHTML = `
    ${renderNavbar()}
    <div class="view-content">
      <h1>Notifications</h1>
      <div class="notification-list">
        ${notifications.length === 0 ? '<p>No notifications.</p>' : ''}
        ${notifications.map(n => `
          <div class="notification-card ${n.read ? 'read' : 'unread'}" data-id="${n.id}">
            <span class="notification-type">${escapeHtml(n.type)}</span>
            ${n.type === 'mention' && n.payload?.sender_username ? `<span class="mention-sender">@${escapeHtml(n.payload.sender_username)}</span>` : ''}
            ${n.type === 'mention' && n.payload?.content_preview ? `<span class="notification-preview">${escapeHtml(n.payload.content_preview)}</span>` : ''}
            <span class="notification-time">${new Date(n.created_at).toLocaleString()}</span>
            ${!n.read ? '<button class="mark-read-btn">Mark Read</button>' : ''}
          </div>
        `).join('')}
      </div>
    </div>
  `;

  document.getElementById('logout-btn').addEventListener('click', logout);

  container.querySelectorAll('.mark-read-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      const id = e.target.closest('.notification-card').dataset.id;
      try {
        await api.notifications.markRead(id);
        renderNotifications(container);
      } catch (err) {
        alert(err.message);
      }
    });
  });
}

async function renderSettings(container) {
  container.innerHTML = `
    ${renderNavbar()}
    <div class="view-content">
      <h1>Settings</h1>
      <form id="settings-form">
        <label>Display Name</label>
        <input type="text" id="display-name" value="${escapeHtml(currentUser.display_name || '')}">
        <button type="submit" class="btn-primary">Save</button>
      </form>
      <div class="user-info">
        <p><strong>User ID:</strong> ${currentUser.id}</p>
        <p><strong>Username:</strong> ${currentUser.username}</p>
      </div>
    </div>
  `;

  document.getElementById('logout-btn').addEventListener('click', logout);

  document.getElementById('settings-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      await api.users.updateSettings({ display_name: document.getElementById('display-name').value.trim() });
      currentUser = await api.users.getProfile();
      alert('Settings saved!');
    } catch (err) {
      alert(err.message);
    }
  });
}

async function renderChat(container) {
  const params = new URLSearchParams(window.location.hash.split('?')[1] || '');
  const workspaceId = params.get('workspace');
  const roomId = params.get('room');

  if (!workspaceId) {
    container.innerHTML = `${renderNavbar()}<div class="view-content"><p>Select a workspace first.</p><a href="#dashboard">Go to Dashboard</a></div>`;
    return;
  }

  const rooms = await api.rooms.list(workspaceId);

  container.innerHTML = `
    ${renderNavbar()}
    <div class="chat-layout">
      <div class="room-sidebar">
        <h3>Rooms</h3>
        <div class="room-list">
          ${rooms.map(r => `
            <a href="#chat?workspace=${workspaceId}&room=${r.id}" class="room-item ${r.id === roomId ? 'active' : ''}">
              ${escapeHtml(r.name)}
            </a>
          `).join('')}
        </div>
        <div class="create-room-form">
          <input type="text" id="new-room-name" placeholder="New room name">
          <button id="create-room-btn">+</button>
        </div>
      </div>
      <div class="chat-main">
        ${roomId ? `
          <div class="messages-container" id="messages"></div>
          <div class="typing-container" id="typing"></div>
          <div class="input-area">
            <div id="reply-indicator" style="display:none;"></div>
            <div id="mention-dropdown" class="mention-dropdown" style="display:none;"></div>
            <textarea id="message-input" placeholder="Type a message..."></textarea>
            <button id="send-btn" class="btn-primary">Send</button>
          </div>
        ` : '<p class="no-room-selected">Select a room to start chatting</p>'}
      </div>
    </div>
  `;

  document.getElementById('logout-btn').addEventListener('click', logout);

  document.getElementById('create-room-btn')?.addEventListener('click', async () => {
    const name = document.getElementById('new-room-name').value.trim();
    if (!name) return;
    try {
      await api.rooms.create(workspaceId, name);
      window.location.hash = `#chat?workspace=${workspaceId}`;
    } catch (err) {
      alert(err.message);
    }
  });

  startPolling('rooms', async () => {
    try {
      const newRooms = await api.rooms.list(workspaceId);
      const roomListEl = container.querySelector('.room-list');
      if (roomListEl) {
        roomListEl.innerHTML = newRooms.map(r => `
          <a href="#chat?workspace=${workspaceId}&room=${r.id}" class="room-item ${r.id === roomId ? 'active' : ''}">
            ${escapeHtml(r.name)}
          </a>
        `).join('');
      }
    } catch (err) {
      console.error('Poll rooms error:', err);
    }
  }, 10000);

  if (roomId) {
    const messagesContainer = document.getElementById('messages');
    const typingContainer = document.getElementById('typing');
    const messageInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');
    const replyIndicator = document.getElementById('reply-indicator');

    let replyToId = null;
    let lastMessageId = null;

    async function loadMessages() {
      const messages = await api.messages.list(workspaceId, roomId);
      messagesContainer.innerHTML = '';
      messages.forEach(m => {
        const div = document.createElement('div');
        div.className = `message ${m.user_id === currentUser.id ? 'own' : ''}`;
        div.innerHTML = `
          <div class="message-header">
            <span class="message-username">${escapeHtml(m.username)}</span>
            <span class="message-time">${new Date(m.created_at).toLocaleTimeString()}</span>
          </div>
          ${m.reply_to_id ? `<div class="message-reply">Reply: ${escapeHtml(m.reply_to_content || '')}</div>` : ''}
          <div class="message-content">${highlightMentions(m.content)}</div>
          <button class="reply-btn" data-id="${m.id}">Reply</button>
        `;
        messagesContainer.appendChild(div);
      });

      if (messages.length > 0) {
        lastMessageId = messages[messages.length - 1].id;
      }

      messagesContainer.scrollTop = messagesContainer.scrollHeight;

      messagesContainer.querySelectorAll('.reply-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
          replyToId = e.target.dataset.id;
          const content = e.target.closest('.message').querySelector('.message-content').textContent;
          replyIndicator.innerHTML = `<span>Replying to: ${escapeHtml(content)}</span><button id="cancel-reply">×</button>`;
          replyIndicator.style.display = 'flex';
          document.getElementById('cancel-reply').addEventListener('click', () => {
            replyToId = null;
            replyIndicator.style.display = 'none';
          });
        });
      });
    }

    async function pollMessages() {
      try {
        const messages = await api.messages.list(workspaceId, roomId);
        const newLastId = messages.length > 0 ? messages[messages.length - 1].id : null;
        if (newLastId !== lastMessageId) {
          await loadMessages();
        }
      } catch (err) {
        console.error('Poll messages error:', err);
      }
    }

    async function pollTyping() {
      try {
        const users = await api.typing.getTypingUsers(workspaceId, roomId);
        const filtered = users.filter(u => u.user_id !== currentUser.id);
        if (filtered.length === 0) {
          typingContainer.innerHTML = '';
        } else if (filtered.length === 1) {
          typingContainer.innerHTML = `<div class="typing-indicator">${escapeHtml(filtered[0].username)} is typing...</div>`;
        } else {
          typingContainer.innerHTML = `<div class="typing-indicator">Several people are typing...</div>`;
        }
      } catch (err) {
        console.error('Poll typing error:', err);
      }
    }

    await loadMessages();

    stopAllPolling();
    startPolling('messages', pollMessages, 3000);
    startPolling('typing', pollTyping, 2000);

    sendBtn.addEventListener('click', async () => {
      const content = messageInput.value.trim();
      if (!content) return;
      messageInput.value = '';
      try {
        if (replyToId) {
          await api.messages.reply(workspaceId, roomId, replyToId, content);
        } else {
          await api.messages.send(workspaceId, roomId, content);
        }
        replyToId = null;
        replyIndicator.style.display = 'none';
        await pollMessages();
      } catch (err) {
        alert(err.message);
      }
    });

    messageInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendBtn.click();
      }
    });

    let mentionState = {
      active: false,
      start: null,
      query: '',
      selected: 0,
      members: [],
      cachedMembers: {}
    };

    const mentionDropdown = document.getElementById('mention-dropdown');

    async function fetchMembers() {
      if (mentionState.cachedMembers[workspaceId]) {
        return mentionState.cachedMembers[workspaceId];
      }
      try {
        const members = await api.workspaces.listMembers(workspaceId);
        mentionState.cachedMembers[workspaceId] = members;
        return members;
      } catch {
        return [];
      }
    }

    function showMentionDropdown(members, query) {
      const filtered = members.filter(m =>
        m.username.toLowerCase().startsWith(query.toLowerCase())
      );
      if (filtered.length === 0) {
        mentionDropdown.style.display = 'none';
        mentionState.active = false;
        return;
      }
      mentionDropdown.innerHTML = filtered.map((m, i) =>
        `<div class="mention-dropdown-item ${i === mentionState.selected ? 'active' : ''}" data-username="${escapeHtml(m.username)}">${escapeHtml(m.username)}</div>`
      ).join('');
      mentionDropdown.style.display = 'block';
      mentionState.active = true;
      mentionState.members = filtered;
      mentionState.selected = 0;
    }

    function hideMentionDropdown() {
      mentionDropdown.style.display = 'none';
      mentionState.active = false;
      mentionState.start = null;
      mentionState.query = '';
      mentionState.selected = 0;
    }

    function updateMentionSelection() {
      const items = mentionDropdown.querySelectorAll('.mention-dropdown-item');
      items.forEach((item, i) => {
        item.classList.toggle('active', i === mentionState.selected);
      });
    }

    messageInput.addEventListener('input', async (e) => {
      const cursorPos = messageInput.selectionStart;
      const textBefore = messageInput.value.substring(0, cursorPos);
      const atIndex = textBefore.lastIndexOf('@');

      if (atIndex !== -1 && (atIndex === 0 || /\s/.test(textBefore[atIndex - 1]))) {
        const query = textBefore.substring(atIndex + 1);
        if (!query.includes(' ') && query.length < 32) {
          mentionState.start = atIndex;
          mentionState.query = query;
          const members = await fetchMembers();
          showMentionDropdown(members, query);
          return;
        }
      }
      hideMentionDropdown();
    });

    messageInput.addEventListener('keydown', (e) => {
      if (!mentionState.active) return;
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        mentionState.selected = Math.min(mentionState.selected + 1, mentionState.members.length - 1);
        updateMentionSelection();
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        mentionState.selected = Math.max(mentionState.selected - 1, 0);
        updateMentionSelection();
      } else if (e.key === 'Enter' || e.key === 'Tab') {
        e.preventDefault();
        const selectedMember = mentionState.members[mentionState.selected];
        if (selectedMember) {
          const before = messageInput.value.substring(0, mentionState.start);
          const after = messageInput.value.substring(messageInput.selectionStart);
          messageInput.value = before + '@' + selectedMember.username + ' ' + after;
          const newPos = mentionState.start + selectedMember.username.length + 2;
          messageInput.setSelectionRange(newPos, newPos);
        }
        hideMentionDropdown();
      } else if (e.key === 'Escape') {
        hideMentionDropdown();
      }
    });

    mentionDropdown.addEventListener('click', (e) => {
      const item = e.target.closest('.mention-dropdown-item');
      if (item) {
        const username = item.dataset.username;
        const before = messageInput.value.substring(0, mentionState.start);
        const after = messageInput.value.substring(messageInput.selectionStart);
        messageInput.value = before + '@' + username + ' ' + after;
        const newPos = mentionState.start + username.length + 2;
        messageInput.setSelectionRange(newPos, newPos);
        messageInput.focus();
        hideMentionDropdown();
      }
    });

    document.addEventListener('click', (e) => {
      if (!mentionDropdown.contains(e.target) && e.target !== messageInput) {
        hideMentionDropdown();
      }
    });
  }
}

async function navigate(view) {
  const app = document.getElementById('app');

  stopAllPolling();

  if (view === 'login' || view === 'register') {
    if (isAuthenticated()) {
      window.location.hash = '#dashboard';
      return;
    }
    if (view === 'login') await renderLogin(app);
    else await renderRegister(app);
    return;
  }

  if (!isAuthenticated()) {
    window.location.hash = '#login';
    return;
  }

  if (!currentUser) {
    try {
      currentUser = await api.users.getProfile();
    } catch {
      window.location.hash = '#login';
      return;
    }
  }

  startPolling('notifications', async () => {
    try {
      const notifs = await api.notifications.list();
      const unread = notifs.filter(n => !n.read).length;
      const badge = document.querySelector('.notification-badge');
      if (badge) {
        badge.textContent = unread > 0 ? unread : '';
        badge.style.display = unread > 0 ? 'inline' : 'none';
      }
    } catch (err) {
      console.error('Poll notifications error:', err);
    }
  }, 30000);

  switch (view) {
    case 'dashboard': await renderDashboard(app); break;
    case 'friends': await renderFriends(app); break;
    case 'notifications': await renderNotifications(app); break;
    case 'settings': await renderSettings(app); break;
    case 'chat': await renderChat(app); break;
    default: window.location.hash = '#dashboard';
  }
}

function getViewFromHash() {
  const hash = window.location.hash.slice(1) || '';
  return hash.split('?')[0] || 'login';
}

async function init() {
  const view = getViewFromHash();
  await navigate(view);

  window.addEventListener('hashchange', async () => {
    await navigate(getViewFromHash());
  });
}

init();
