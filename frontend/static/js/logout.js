/**
 * Syntra — Fetch-based logout utility.
 *
 * Usage:
 *   <button onclick="syntraLogout()">Sign Out</button>
 *
 * Or attach manually:
 *   document.getElementById('logout-btn').addEventListener('click', syntraLogout);
 */

function getCsrfToken() {
  const cookie = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='));
  if (cookie) return cookie.split('=')[1];

  // Fallback: read from the hidden input Django renders with {% csrf_token %}
  const input = document.querySelector('[name=csrfmiddlewaretoken]');
  return input ? input.value : '';
}

async function syntraLogout() {
  try {
    const res = await fetch('/accounts/logout/', {
      method: 'POST',
      credentials: 'same-origin',          // send session cookie
      headers: {
        'X-CSRFToken': getCsrfToken(),
        'Accept': 'application/json',       // tell Django to return JSON
      },
    });

    if (!res.ok) {
      console.error('Logout failed:', res.status);
    }
  } catch (err) {
    console.error('Logout error:', err);
  }

  // Always redirect — even if the request fails the session is likely gone
  window.location.replace('/accounts/login/');
}
