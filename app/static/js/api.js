const API_BASE = '/api';
const WS_BASE = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}`;

const TOKEN_KEY = 'auth_token';

class ApiError extends Error {
  constructor(status, data) {
    super(data.detail || 'An error occurred');
    this.status = status;
    this.data = data;
  }
}

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

async function request(method, path, body = null, requireAuth = true) {
  const headers = { 'Content-Type': 'application/json' };

  if (requireAuth) {
    const token = getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  const config = { method, headers };
  if (body && method !== 'GET') {
    config.body = JSON.stringify(body);
  }

  const response = await fetch(`${API_BASE}${path}`, config);

  if (response.status === 401) {
    clearToken();
    window.location.hash = '#login';
    throw new ApiError(401, { detail: 'Unauthorized' });
  }

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new ApiError(response.status, data);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export const api = {
  auth: {
    register: (username, password) =>
      request('POST', '/register', { username, password }, false),
    login: (username, password) =>
      request('POST', '/token', { username, password }, false).then(data => {
        if (data.access_token) {
          setToken(data.access_token);
        }
        return data;
      }),
  },

  users: {
    getProfile: () => request('GET', '/me'),
    updateSettings: (settings) => request('PUT', '/me/settings', settings),
  },

  friends: {
    list: () => request('GET', '/friends'),
    add: (friendId) => request('POST', '/friends', { friend_id: friendId }),
    remove: (friendId) => request('DELETE', `/friends/${friendId}`),
  },

  workspaces: {
    list: () => request('GET', '/workspaces'),
    create: (name) => request('POST', '/workspaces', { name }),
    join: (workspaceId) => request('POST', `/workspaces/${workspaceId}/join`),
    delete: (workspaceId) => request('DELETE', `/workspaces/${workspaceId}`),
    listMembers: (workspaceId) => request('GET', `/workspaces/${workspaceId}/members`),
  },

  rooms: {
    list: (workspaceId) => request('GET', `/workspaces/${workspaceId}/rooms`),
    create: (workspaceId, name) =>
      request('POST', `/workspaces/${workspaceId}/rooms`, { name }),
    delete: (workspaceId, roomId) =>
      request('DELETE', `/workspaces/${workspaceId}/rooms/${roomId}`),
  },

  messages: {
    list: (workspaceId, roomId) => request('GET', `/workspaces/${workspaceId}/rooms/${roomId}/messages`),
    send: (workspaceId, roomId, content) =>
      request('POST', `/workspaces/${workspaceId}/rooms/${roomId}/messages`, { content }),
    reply: (workspaceId, roomId, replyToId, content) =>
      request('POST', `/workspaces/${workspaceId}/rooms/${roomId}/messages/${replyToId}/reply`, { content }),
  },

  typing: {
    setTyping: (workspaceId, roomId, isTyping) =>
      request('POST', `/workspaces/${workspaceId}/rooms/${roomId}/typing`, { is_typing: isTyping }),
    getTypingUsers: (workspaceId, roomId) => request('GET', `/workspaces/${workspaceId}/rooms/${roomId}/typing`),
  },

  notifications: {
    list: () => request('GET', '/notifications'),
    markRead: (notificationId) =>
      request('PUT', `/notifications/${notificationId}/read`),
  },

  help: {
    getHelp: () => request('GET', '/help'),
  },
};

export const ws = {
  connect: (onMessage, onTyping, onNotification) => {
    const token = getToken();
    const socket = new WebSocket(`${WS_BASE}/ws?token=${token}`);

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      switch (data.type) {
        case 'message':
          onMessage(data.payload);
          break;
        case 'typing':
          onTyping(data.payload);
          break;
        case 'notification':
          onNotification(data.payload);
          break;
      }
    };

    socket.onclose = () => {
      setTimeout(() => ws.connect(onMessage, onTyping, onNotification), 3000);
    };

    return socket;
  },

  send: (socket, type, payload) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ type, payload }));
    }
  },
};

export { getToken, setToken, clearToken, TOKEN_KEY };