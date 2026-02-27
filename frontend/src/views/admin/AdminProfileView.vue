<template>
  <div class="admin-profile-view">
    <header class="profile-hero">
      <div>
        <p class="eyebrow">Account Settings</p>
        <h1>Admin Profile & Access Management</h1>
        <p class="hero-description">
          Update your own login details, rotate your password safely, and create admin accounts only for
          colleagues who actively build and manage consultant profiles.
        </p>
      </div>
      <div class="hero-badge">
        <span class="badge-label">Access Rule</span>
        <strong>{{ isCurrentUserSuperAdmin ? 'Super Admin Session' : 'Admin Session' }}</strong>
      </div>
    </header>

    <div v-if="loading" class="loading-state">Loading account settings...</div>

    <div v-else class="profile-grid">
      <section class="settings-card">
        <h2>My Account</h2>
        <p class="card-description">Keep your username and email current.</p>

        <form class="settings-form" @submit.prevent="saveProfile">
          <div class="form-group">
            <label for="profile_username">Username</label>
            <input id="profile_username" v-model.trim="profileForm.username" type="text" minlength="3" required />
          </div>

          <div class="form-group">
            <label for="profile_email">Email</label>
            <input id="profile_email" v-model.trim="profileForm.email" type="email" required />
          </div>

          <p v-if="profileError" class="status-message status-error">{{ profileError }}</p>
          <p v-if="profileSuccess" class="status-message status-success">{{ profileSuccess }}</p>

          <button
            type="submit"
            class="btn btn-primary"
            :disabled="isSavingProfile || !hasProfileChanges"
          >
            {{ isSavingProfile ? 'Saving...' : 'Save Profile Details' }}
          </button>
        </form>
      </section>

      <section class="settings-card">
        <h2>Password Security</h2>
        <p class="card-description">
          To change your password, enter your new password first, then confirm your current password in a secure modal.
        </p>

        <div class="settings-form">
          <div class="form-group">
            <label for="new_password">New Password</label>
            <input id="new_password" v-model="passwordForm.newPassword" type="password" minlength="8" required />
          </div>

          <div class="form-group">
            <label for="confirm_password">Confirm New Password</label>
            <input
              id="confirm_password"
              v-model="passwordForm.confirmPassword"
              type="password"
              minlength="8"
              required
            />
          </div>

          <p v-if="passwordError" class="status-message status-error">{{ passwordError }}</p>

          <button
            type="button"
            class="btn btn-primary"
            :disabled="isUpdatingPassword"
            @click="openPasswordModal"
          >
            {{ isUpdatingPassword ? 'Updating...' : 'Update Password' }}
          </button>
        </div>
      </section>

      <section class="settings-card access-policy-card">
        <h2>Who Should Get Admin Access?</h2>
        <p class="card-description">
          Admin accounts are only for internal team members who actively manage consultant profiles and export deliverables.
        </p>
        <ul class="policy-list">
          <li>Give access to profile managers, sales operations, and delivery leads who build/edit profiles.</li>
          <li>Do not create admin accounts for consultants.</li>
          <li>Consultants should use temporary edit links only (`/edit/:token`).</li>
          <li>Review active admin accounts regularly and keep access limited to required roles.</li>
        </ul>
      </section>

      <section class="settings-card">
        <h2>Create Admin Account</h2>
        <p class="card-description">
          Provision a new admin for someone who needs to create or manage profiles.
          Consultants should not receive admin accounts.
        </p>

        <form v-if="isCurrentUserSuperAdmin" class="settings-form" @submit.prevent="createAdminAccount">
          <div class="form-group">
            <label for="new_admin_username">Username</label>
            <input id="new_admin_username" v-model.trim="newAdminForm.username" type="text" minlength="3" required />
          </div>

          <div class="form-group">
            <label for="new_admin_email">Email</label>
            <input id="new_admin_email" v-model.trim="newAdminForm.email" type="email" required />
          </div>

          <div class="form-group">
            <label for="new_admin_password">Temporary Password</label>
            <input id="new_admin_password" v-model="newAdminForm.password" type="password" minlength="8" required />
          </div>

          <div class="form-group">
            <label for="new_admin_password_confirm">Confirm Temporary Password</label>
            <input
              id="new_admin_password_confirm"
              v-model="newAdminForm.confirmPassword"
              type="password"
              minlength="8"
              required
            />
          </div>

          <label class="checkbox-row" for="new_admin_super_admin">
            <input id="new_admin_super_admin" v-model="newAdminForm.isSuperAdmin" type="checkbox" />
            <span>Grant Super Admin privileges</span>
          </label>

          <p v-if="newAdminError" class="status-message status-error">{{ newAdminError }}</p>
          <p v-if="newAdminSuccess" class="status-message status-success">{{ newAdminSuccess }}</p>

          <button type="submit" class="btn btn-primary" :disabled="isCreatingAdmin">
            {{ isCreatingAdmin ? 'Creating...' : 'Create Admin Account' }}
          </button>
        </form>

        <p v-else class="status-message status-warning">
          Only super admins can create new admin accounts or assign super admin access.
        </p>
      </section>

      <section class="settings-card admin-list-card">
        <h2>Current Admin Accounts</h2>
        <p class="card-description">Use this list to verify who currently has system access.</p>

        <p v-if="adminListError" class="status-message status-error">{{ adminListError }}</p>
        <p v-if="roleUpdateError" class="status-message status-error">{{ roleUpdateError }}</p>
        <p v-if="roleUpdateSuccess" class="status-message status-success">{{ roleUpdateSuccess }}</p>

        <div v-if="adminAccounts.length" class="admin-table-wrapper">
          <table class="admin-table">
            <thead>
              <tr>
                <th>Username</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Last Login</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="admin in adminAccounts" :key="admin.id">
                <td>{{ admin.username }}</td>
                <td>{{ admin.email }}</td>
                <td>
                  <span :class="['status-pill', admin.is_super_admin ? 'status-super-admin' : 'status-standard-admin']">
                    {{ admin.is_super_admin ? 'Super Admin' : 'Admin' }}
                  </span>
                </td>
                <td>
                  <span :class="['status-pill', admin.is_active ? 'status-active' : 'status-inactive']">
                    {{ admin.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td>{{ formatDateTime(admin.last_login_at) }}</td>
                <td>{{ formatDate(admin.created_at) }}</td>
                <td>
                  <button
                    v-if="isCurrentUserSuperAdmin && currentAdmin && admin.id !== currentAdmin.id"
                    type="button"
                    class="btn btn-secondary btn-role-toggle"
                    :disabled="roleUpdateInFlightId === admin.id"
                    @click="toggleAdminSuperStatus(admin)"
                  >
                    {{
                      roleUpdateInFlightId === admin.id
                        ? 'Updating...'
                        : admin.is_super_admin
                          ? 'Revoke Super Admin'
                          : 'Make Super Admin'
                    }}
                  </button>
                  <span v-else class="muted-cell">
                    {{ currentAdmin && admin.id === currentAdmin.id ? 'Current User' : 'No Action' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <p v-else class="empty-state">No admin accounts found.</p>
      </section>
    </div>

    <div v-if="isPasswordModalOpen" class="modal-overlay" @click="closePasswordModal">
      <div class="modal" @click.stop>
        <h3>Confirm Current Password</h3>
        <p class="modal-description">
          For security, enter your current password to confirm this password change.
        </p>

        <div class="form-group">
          <label for="current_password">Current Password</label>
          <input
            id="current_password"
            v-model="passwordForm.currentPassword"
            type="password"
            autocomplete="current-password"
            required
          />
        </div>

        <p v-if="passwordError" class="status-message status-error">{{ passwordError }}</p>

        <div class="modal-actions">
          <button type="button" class="btn btn-secondary" :disabled="isUpdatingPassword" @click="closePasswordModal">
            Cancel
          </button>
          <button type="button" class="btn btn-primary" :disabled="isUpdatingPassword" @click="confirmPasswordUpdate">
            {{ isUpdatingPassword ? 'Updating...' : 'Confirm Password Change' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const isSavingProfile = ref(false)
const isCreatingAdmin = ref(false)
const isUpdatingPassword = ref(false)
const isPasswordModalOpen = ref(false)

const profileError = ref('')
const profileSuccess = ref('')
const passwordError = ref('')
const newAdminError = ref('')
const newAdminSuccess = ref('')
const adminListError = ref('')
const roleUpdateError = ref('')
const roleUpdateSuccess = ref('')
const roleUpdateInFlightId = ref(null)
const currentAdmin = ref(null)

const profileForm = reactive({
  username: '',
  email: ''
})

const originalProfile = reactive({
  username: '',
  email: ''
})

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const newAdminForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  isSuperAdmin: false
})

const adminAccounts = ref([])

const hasProfileChanges = computed(() => {
  return (
    profileForm.username.trim() !== originalProfile.username ||
    profileForm.email.trim() !== originalProfile.email
  )
})
const isCurrentUserSuperAdmin = computed(() => Boolean(currentAdmin.value?.is_super_admin))

const dateFormatter = new Intl.DateTimeFormat(undefined, {
  year: 'numeric',
  month: 'short',
  day: 'numeric'
})
const dateTimeFormatter = new Intl.DateTimeFormat(undefined, {
  year: 'numeric',
  month: 'short',
  day: 'numeric',
  hour: '2-digit',
  minute: '2-digit'
})

function getErrorMessage(error, fallbackMessage) {
  const detail = error?.response?.data?.detail
  if (Array.isArray(detail)) {
    return detail.map((entry) => entry.msg).join(', ')
  }

  if (typeof detail === 'string' && detail.trim()) {
    return detail
  }

  return fallbackMessage
}

function applyProfile(admin) {
  currentAdmin.value = admin
  profileForm.username = admin.username
  profileForm.email = admin.email
  originalProfile.username = admin.username
  originalProfile.email = admin.email
}

function resetPasswordForm() {
  passwordForm.currentPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
}

function resetNewAdminForm() {
  newAdminForm.username = ''
  newAdminForm.email = ''
  newAdminForm.password = ''
  newAdminForm.confirmPassword = ''
  newAdminForm.isSuperAdmin = false
}

async function loadAdminAccounts() {
  adminListError.value = ''

  try {
    const response = await api.get('/auth/admins')
    adminAccounts.value = response.data
  } catch (error) {
    adminListError.value = getErrorMessage(error, 'Unable to load admin accounts.')
  }
}

async function loadPageData() {
  loading.value = true

  try {
    const [profileResponse, adminsResponse] = await Promise.all([
      api.get('/auth/me'),
      api.get('/auth/admins')
    ])

    applyProfile(profileResponse.data)
    adminAccounts.value = adminsResponse.data
  } catch (error) {
    profileError.value = getErrorMessage(error, 'Unable to load profile settings.')
  } finally {
    loading.value = false
  }
}

async function saveProfile() {
  profileError.value = ''
  profileSuccess.value = ''

  if (!hasProfileChanges.value) {
    return
  }

  isSavingProfile.value = true

  try {
    const response = await api.put('/auth/me', {
      username: profileForm.username.trim(),
      email: profileForm.email.trim()
    })

    applyProfile(response.data)
    profileSuccess.value = 'Profile details updated successfully.'
  } catch (error) {
    profileError.value = getErrorMessage(error, 'Unable to update profile details.')
  } finally {
    isSavingProfile.value = false
  }
}

function openPasswordModal() {
  passwordError.value = ''

  if (passwordForm.newPassword.length < 8) {
    passwordError.value = 'New password must be at least 8 characters long.'
    return
  }

  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    passwordError.value = 'New password and confirmation do not match.'
    return
  }

  passwordForm.currentPassword = ''
  isPasswordModalOpen.value = true
}

function closePasswordModal() {
  if (isUpdatingPassword.value) {
    return
  }

  isPasswordModalOpen.value = false
  passwordForm.currentPassword = ''
}

async function confirmPasswordUpdate() {
  passwordError.value = ''

  if (!passwordForm.currentPassword) {
    passwordError.value = 'Current password is required to confirm this change.'
    return
  }

  isUpdatingPassword.value = true

  try {
    await api.put('/auth/me/password', {
      current_password: passwordForm.currentPassword,
      new_password: passwordForm.newPassword
    })

    resetPasswordForm()
    isPasswordModalOpen.value = false
    authStore.logout()
    await router.push({ path: '/admin/login', query: { reason: 'password-updated' } })
  } catch (error) {
    passwordError.value = getErrorMessage(error, 'Unable to update password.')
  } finally {
    isUpdatingPassword.value = false
  }
}

async function createAdminAccount() {
  newAdminError.value = ''
  newAdminSuccess.value = ''

  if (!isCurrentUserSuperAdmin.value) {
    newAdminError.value = 'Only super admins can create admin accounts.'
    return
  }

  if (newAdminForm.password.length < 8) {
    newAdminError.value = 'Temporary password must be at least 8 characters long.'
    return
  }

  if (newAdminForm.password !== newAdminForm.confirmPassword) {
    newAdminError.value = 'Temporary password and confirmation do not match.'
    return
  }

  isCreatingAdmin.value = true

  try {
    await api.post('/auth/admins', {
      username: newAdminForm.username.trim(),
      email: newAdminForm.email.trim(),
      password: newAdminForm.password,
      is_super_admin: newAdminForm.isSuperAdmin
    })

    newAdminSuccess.value = 'Admin account created successfully.'
    resetNewAdminForm()
    await loadAdminAccounts()
  } catch (error) {
    newAdminError.value = getErrorMessage(error, 'Unable to create admin account.')
  } finally {
    isCreatingAdmin.value = false
  }
}

async function toggleAdminSuperStatus(admin) {
  roleUpdateError.value = ''
  roleUpdateSuccess.value = ''

  if (!isCurrentUserSuperAdmin.value || !currentAdmin.value || admin.id === currentAdmin.value.id) {
    roleUpdateError.value = 'Only super admins can update super admin roles for other admins.'
    return
  }

  roleUpdateInFlightId.value = admin.id

  try {
    const response = await api.put(`/auth/admins/${admin.id}/super-admin`, {
      is_super_admin: !admin.is_super_admin
    })

    roleUpdateSuccess.value = response.data.is_super_admin
      ? `${response.data.username} now has super admin access.`
      : `${response.data.username} is now a standard admin.`
    await loadAdminAccounts()
  } catch (error) {
    roleUpdateError.value = getErrorMessage(error, 'Unable to update super admin status.')
  } finally {
    roleUpdateInFlightId.value = null
  }
}

function formatDate(value) {
  const parsedDate = new Date(value)
  if (Number.isNaN(parsedDate.getTime())) {
    return value
  }

  return dateFormatter.format(parsedDate)
}

function formatDateTime(value) {
  if (!value) {
    return 'Never'
  }

  const parsedDate = new Date(value)
  if (Number.isNaN(parsedDate.getTime())) {
    return value
  }

  return dateTimeFormatter.format(parsedDate)
}

onMounted(loadPageData)
</script>

<style scoped>
.admin-profile-view {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.profile-hero {
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  border: 1px solid #f3ddd4;
  background:
    radial-gradient(circle at 12% 10%, #fff3ec 0%, transparent 40%),
    radial-gradient(circle at 100% -10%, #ffe2d5 0%, transparent 36%),
    var(--color-surface);
  box-shadow: var(--shadow-sm);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacing-lg);
}

.eyebrow {
  margin: 0 0 var(--spacing-xs) 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 700;
  color: var(--color-primary);
  font-size: var(--font-size-xs);
}

.hero-description {
  margin: 0;
  max-width: 740px;
  color: var(--color-text-secondary);
}

.hero-badge {
  min-width: 210px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  padding: var(--spacing-md);
  background: var(--color-background);
  text-align: center;
}

.badge-label {
  display: block;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
  font-size: var(--font-size-sm);
}

.profile-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--spacing-md);
}

.settings-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: var(--spacing-lg);
}

.settings-card h2 {
  margin: 0 0 var(--spacing-xs) 0;
  font-size: var(--font-size-xl);
}

.card-description {
  margin: 0 0 var(--spacing-md) 0;
  color: var(--color-text-secondary);
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.form-group label {
  font-weight: 600;
  color: var(--color-text-primary);
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.form-group input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(232, 93, 41, 0.16);
}

.policy-list {
  margin: 0;
  padding-left: 1.25rem;
  color: var(--color-text-secondary);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.status-message {
  margin: 0;
  font-size: var(--font-size-sm);
  border-radius: var(--radius-md);
  padding: var(--spacing-sm) var(--spacing-md);
}

.status-error {
  background: #fee2e2;
  border: 1px solid #fecaca;
  color: #991b1b;
}

.status-success {
  background: #dcfce7;
  border: 1px solid #86efac;
  color: #166534;
}

.status-warning {
  background: #fff7ed;
  border: 1px solid #fdba74;
  color: #9a3412;
}

.admin-list-card {
  grid-column: span 2;
}

.admin-table-wrapper {
  overflow-x: auto;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
}

.admin-table th,
.admin-table td {
  text-align: left;
  padding: 0.7rem;
  border-bottom: 1px solid var(--color-border);
  font-size: var(--font-size-sm);
}

.admin-table th {
  color: var(--color-text-secondary);
  font-weight: 600;
}

.btn-role-toggle {
  padding: 0.4rem 0.65rem;
  font-size: 0.78rem;
  line-height: 1.2;
}

.muted-cell {
  color: var(--color-text-tertiary);
  font-size: var(--font-size-sm);
}

.status-pill {
  display: inline-flex;
  align-items: center;
  border-radius: var(--radius-full);
  padding: 0.2rem 0.55rem;
  font-size: 0.72rem;
  font-weight: 700;
}

.status-active {
  background: #dcfce7;
  color: #166534;
}

.status-super-admin {
  background: #e0f2fe;
  color: #0c4a6e;
}

.status-standard-admin {
  background: #f3f4f6;
  color: #374151;
}

.status-inactive {
  background: #fee2e2;
  color: #991b1b;
}

.checkbox-row {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}

.checkbox-row input[type='checkbox'] {
  width: 16px;
  height: 16px;
}

.empty-state,
.loading-state {
  color: var(--color-text-secondary);
  margin: 0;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1400;
  padding: var(--spacing-md);
}

.modal {
  width: min(460px, 100%);
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-lg);
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.modal h3 {
  margin: 0;
}

.modal-description {
  margin: 0;
  color: var(--color-text-secondary);
}

.modal-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.modal-actions .btn {
  flex: 1;
}

@media (max-width: 960px) {
  .profile-hero {
    flex-direction: column;
    align-items: stretch;
  }

  .hero-badge {
    width: 100%;
  }

  .profile-grid {
    grid-template-columns: 1fr;
  }

  .admin-list-card {
    grid-column: span 1;
  }
}
</style>
