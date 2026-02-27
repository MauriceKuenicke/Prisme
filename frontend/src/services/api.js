import axios from 'axios'

const TOKEN_STORAGE_KEY = 'admin_token'
const TOKEN_EXPIRY_SKEW_SECONDS = 5

function decodeTokenPayload(token) {
  if (!token || typeof token !== 'string') {
    return null
  }

  const parts = token.split('.')
  if (parts.length !== 3) {
    return null
  }

  try {
    const normalizedBase64 = parts[1].replace(/-/g, '+').replace(/_/g, '/')
    const padded = normalizedBase64.padEnd(Math.ceil(normalizedBase64.length / 4) * 4, '=')
    return JSON.parse(atob(padded))
  } catch {
    return null
  }
}

function isTokenExpired(token) {
  const payload = decodeTokenPayload(token)
  const exp = payload?.exp
  if (typeof exp !== 'number') {
    return true
  }

  const expiresAtMs = exp * 1000
  const nowWithSkewMs = Date.now() + TOKEN_EXPIRY_SKEW_SECONDS * 1000
  return nowWithSkewMs >= expiresAtMs
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(TOKEN_STORAGE_KEY)
    if (token && !isTokenExpired(token)) {
      config.headers = config.headers ?? {}
      config.headers.Authorization = `Bearer ${token}`
    } else if (token) {
      localStorage.removeItem(TOKEN_STORAGE_KEY)
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const isUnauthorized = error.response?.status === 401
    const hadAuthHeader = Boolean(error.config?.headers?.Authorization)

    if (isUnauthorized && hadAuthHeader) {
      localStorage.removeItem(TOKEN_STORAGE_KEY)

      const currentPath = window.location.pathname
      if (currentPath.startsWith('/admin') && currentPath !== '/admin/login') {
        window.location.href = '/admin/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
