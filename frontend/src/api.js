const API_BASE_URL = (
  import.meta.env.VITE_API_URL || 'http://localhost:8000'
).replace(/\/$/, '')

const SESSION_KEY = 'foodys_auth'

function errorMessage(detail, fallback) {
  if (typeof detail === 'string') {
    return detail
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => item.msg || 'Invalid value')
      .join(' ')
  }

  return fallback
}

export async function apiRequest(
  path,
  { method = 'GET', body, token } = {},
) {
  let response

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers: {
        ...(body ? { 'Content-Type': 'application/json' } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      ...(body ? { body: JSON.stringify(body) } : {}),
    })
  } catch {
    throw new Error(
      'Cannot reach the backend. Check that FastAPI is running on port 8000.',
    )
  }

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    throw new Error(
      errorMessage(data?.detail, `Request failed with status ${response.status}.`),
    )
  }

  return data
}

export function loadSession() {
  const savedSession = sessionStorage.getItem(SESSION_KEY)

  if (!savedSession) {
    return null
  }

  try {
    const session = JSON.parse(savedSession)

    if (!session.token || !session.user) {
      clearSession()
      return null
    }

    return session
  } catch {
    clearSession()
    return null
  }
}

export function saveSession(token, user) {
  sessionStorage.setItem(SESSION_KEY, JSON.stringify({ token, user }))
}

export function clearSession() {
  sessionStorage.removeItem(SESSION_KEY)
}
