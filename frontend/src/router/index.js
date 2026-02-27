import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    redirect: '/admin/login'
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('@/views/admin/LoginView.vue')
  },
  {
    path: '/admin',
    component: () => import('@/views/admin/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/admin/DashboardView.vue')
      },
      {
        path: 'consultants',
        name: 'Consultants',
        component: () => import('@/views/admin/ConsultantsView.vue')
      },
      {
        path: 'help',
        name: 'AdminHelp',
        component: () => import('@/views/admin/AdminHelpView.vue')
      },
      {
        path: 'profile',
        name: 'AdminProfile',
        component: () => import('@/views/admin/AdminProfileView.vue')
      },
      {
        path: 'consultants/:id/build-profile',
        name: 'ProfileBuilder',
        component: () => import('@/views/admin/ProfileBuilderView.vue')
      },
      {
        path: 'consultants/:id/profiles',
        name: 'ProfileHistory',
        component: () => import('@/views/admin/ProfileHistoryView.vue')
      },
      {
        path: 'consultants/:id/profiles/:profileId/edit',
        name: 'ProfileEdit',
        component: () => import('@/views/admin/ProfileBuilderView.vue')
      }
    ]
  },
  {
    path: '/edit/:token',
    name: 'EditBlocks',
    component: () => import('@/views/consultant/EditBlocksView.vue')
  },
  {
    path: '/access-expired',
    name: 'AccessExpired',
    component: () => import('@/views/consultant/AccessExpiredView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach(async (to) => {
  const authStore = useAuthStore()
  await authStore.initializeAuth()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return '/admin/login'
  }

  if (to.path === '/admin/login' && authStore.isAuthenticated) {
    return '/admin/dashboard'
  }

  return true
})

export default router
