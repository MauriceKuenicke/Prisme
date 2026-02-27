import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

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

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem(TOKEN_STORAGE_KEY) || null)
  const admin = ref(null)
  const isAuthenticated = computed(() => !!token.value && !isTokenExpired(token.value))

  async function fetchCurrentAdmin() {
    if (!token.value || isTokenExpired(token.value)) {
      admin.value = null
      return null
    }

    try {
      const response = await api.get('/auth/me')
      admin.value = response.data
      return admin.value
    } catch {
      logout()
      return null
    }
  }

  async function initializeAuth() {
    if (!token.value) {
      admin.value = null
      return
    }

    if (isTokenExpired(token.value)) {
      logout()
      return
    }

    if (!admin.value) {
      await fetchCurrentAdmin()
    }
  }

  async function login(username, password) {
    try {
      const response = await api.post('/auth/login', { username, password })
      token.value = response.data.access_token
      localStorage.setItem(TOKEN_STORAGE_KEY, token.value)
      await fetchCurrentAdmin()
      return true
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  }

  function logout() {
    token.value = null
    admin.value = null
    localStorage.removeItem(TOKEN_STORAGE_KEY)
  }

  return { token, admin, isAuthenticated, initializeAuth, fetchCurrentAdmin, login, logout }
})
