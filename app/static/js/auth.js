import { api, getToken, clearToken } from './api.js';

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
  window.location.hash = '#login';
}

export async function handleLogin(event) {
  event.preventDefault();
  const form = event.target;
  const username = form.username.value;
  const password = form.password.value;
  const errorEl = form.querySelector('.error') || document.getElementById('login-error');

  try {
    await api.auth.login(username, password);
    currentUser = await api.users.getProfile();
    window.location.hash = '#dashboard';
  } catch (err) {
    if (errorEl) {
      errorEl.textContent = err.message;
      errorEl.style.display = 'block';
    } else {
      alert(err.message);
    }
  }
}

export async function handleRegister(event) {
  event.preventDefault();
  const form = event.target;
  const username = form.username.value;
  const password = form.password.value;
  const errorEl = form.querySelector('.error') || document.getElementById('register-error');

  try {
    await api.auth.register(username, password);
    await api.auth.login(username, password);
    currentUser = await api.users.getProfile();
    window.location.hash = '#dashboard';
  } catch (err) {
    if (errorEl) {
      errorEl.textContent = err.message;
      errorEl.style.display = 'block';
    } else {
      alert(err.message);
    }
  }
}

export function renderLoginForm(container) {
  container.innerHTML = `
    <form id="login-form">
      <h2>Sign In</h2>
      <div id="login-error" class="error" style="display:none;"></div>
      <input type="text" name="username" placeholder="Username" required>
      <input type="password" name="password" placeholder="Password" required>
      <button type="submit">Sign In</button>
      <p>Don't have an account? <a href="#register">Register</a></p>
    </form>
  `;
  document.getElementById('login-form').addEventListener('submit', handleLogin);
}

export function renderRegisterForm(container) {
  container.innerHTML = `
    <form id="register-form">
      <h2>Create Account</h2>
      <div id="register-error" class="error" style="display:none;"></div>
      <input type="text" name="username" placeholder="Username (3-50 chars)" required minlength="3" maxlength="50">
      <input type="password" name="password" placeholder="Password (8+ chars)" required minlength="8">
      <button type="submit">Create Account</button>
      <p>Already have an account? <a href="#login">Sign In</a></p>
    </form>
  `;
  document.getElementById('register-form').addEventListener('submit', handleRegister);
}