<template>
  <div class="admin-layout">
    <nav class="admin-nav">
      <div class="nav-brand">
        <h2>Prismé</h2>
      </div>
      <div class="nav-links">
        <router-link to="/admin/dashboard" class="nav-link">Dashboard</router-link>
        <router-link to="/admin/consultants" class="nav-link">Consultants</router-link>
        <router-link to="/admin/profile" class="nav-link">Profile</router-link>
        <router-link to="/admin/help" class="nav-link">Help</router-link>
      </div>
      <button @click="handleLogout" class="btn-logout">Logout</button>
    </nav>
    <main class="admin-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

function handleLogout() {
  authStore.logout()
  router.push('/admin/login')
}
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.admin-nav {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  padding: var(--spacing-lg) var(--spacing-xl);
  display: flex;
  align-items: center;
  gap: var(--spacing-xl);
}

.nav-brand h2 {
  color: var(--color-primary);
  margin: 0;
}

.nav-links {
  display: flex;
  gap: var(--spacing-lg);
  flex: 1;
}

.nav-link {
  padding: var(--spacing-sm) var(--spacing-md);
  color: var(--color-text-secondary);
  font-weight: 500;
  transition: color var(--transition-fast);
}

.nav-link:hover,
.nav-link.router-link-active {
  color: var(--color-primary);
}

.btn-logout {
  padding: var(--spacing-sm) var(--spacing-lg);
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-weight: 500;
}

.btn-logout:hover {
  border-color: var(--color-error);
  color: var(--color-error);
}

.admin-content {
  flex: 1;
  padding: var(--spacing-xl);
}
</style>
