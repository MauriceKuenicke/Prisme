<template>
  <div class="profile-history-view">
    <div class="header">
      <div>
        <h1>Profile History</h1>
        <p v-if="consultant" class="consultant-info">
          {{ consultant.first_name }} {{ consultant.last_name }} - {{ consultant.title }}
        </p>
      </div>
      <button @click="goBack" class="btn btn-secondary" title="Back to consultants">Back to Consultants</button>
    </div>

    <p v-if="errorMessage" class="error-banner">{{ errorMessage }}</p>

    <div v-if="loading" class="loading">Loading profile history...</div>

    <div v-else-if="profiles.length === 0" class="empty-state">
      <p>No profiles created yet for this consultant.</p>
      <button @click="buildNewProfile" class="btn btn-primary" title="Build first profile">Build First Profile</button>
    </div>

    <div v-else class="profiles-list">
      <div v-for="profile in profiles" :key="profile.id" class="profile-card">
        <div class="profile-header">
          <div class="profile-info">
            <h3>{{ profile.profile_name }}</h3>
            <p class="profile-meta">
              Created {{ formatDate(profile.created_at) }} by Admin #{{ profile.created_by_admin_id }}
            </p>
          </div>
          <div class="profile-actions">
            <button @click="viewProfile(profile)" class="btn-icon" title="View Profile" aria-label="View profile">
              <LineIcon name="eye" :size="16" />
            </button>
            <button @click="showEditModal(profile)" class="btn-icon" title="Edit Profile" aria-label="Edit profile">
              <LineIcon name="pencil" :size="16" />
            </button>
            <button @click="showExportModal(profile)" class="btn-icon" title="Export as PDF" aria-label="Export as PDF">
              <LineIcon name="file" :size="16" />
            </button>
            <button @click="showDuplicateModal(profile)" class="btn-icon" title="Duplicate Profile" aria-label="Duplicate profile">
              <LineIcon name="copy" :size="16" />
            </button>
            <button @click="openDeleteModal(profile)" class="btn-icon btn-danger" title="Delete Profile" aria-label="Delete profile">
              <LineIcon name="trash" :size="16" />
            </button>
          </div>
        </div>
        <div class="profile-stats">
          <span class="stat-badge">{{ getBlockCount(profile) }} blocks</span>
          <span class="stat-badge">{{ getBlockTypes(profile).join(', ') }}</span>
        </div>
      </div>
    </div>

    <!-- View Profile Modal -->
    <div v-if="showViewModal" class="modal-overlay" @click="showViewModal = false">
      <div class="modal modal-large" @click.stop>
        <div class="modal-header">
          <h2>{{ viewingProfile?.profile_name }}</h2>
          <button @click="showViewModal = false" class="btn-close" aria-label="Close profile preview" title="Close">
            <LineIcon name="x" :size="18" />
          </button>
        </div>
        <div class="modal-content">
          <div v-if="profileData" class="profile-preview">
            <div class="consultant-section">
              <h3>{{ profileData.consultant.first_name }} {{ profileData.consultant.last_name }}</h3>
              <p class="consultant-title">{{ profileData.consultant.title }}</p>
              <p v-if="profileData.consultant.email" class="consultant-email">{{ profileData.consultant.email }}</p>
            </div>

            <div v-for="(blocks, blockType) in profileData.blocks_by_type" :key="blockType" class="block-section">
              <h4>{{ formatBlockType(blockType) }}</h4>
              <div v-for="block in blocks" :key="block.id" class="block-item">
                <h5>{{ block.title }}</h5>
                <div class="block-details">
                  <template v-if="blockType === 'project'">
                    <p v-if="block.client_name"><strong>Client:</strong> {{ block.client_name }}</p>
                    <p v-if="block.role"><strong>Role:</strong> {{ block.role }}</p>
                    <p v-if="block.description">{{ block.description }}</p>
                    <p v-if="block.technologies && block.technologies.length">
                      <strong>Technologies:</strong> {{ Array.isArray(block.technologies) ? block.technologies.join(', ') : block.technologies }}
                    </p>
                    <p v-if="block.duration_months"><strong>Duration (months):</strong> {{ block.duration_months }}</p>
                    <p v-if="block.start_date || block.end_date">
                      <strong>Duration:</strong>
                      {{ block.start_date }} - {{ block.is_ongoing ? 'Present' : (block.end_date || 'Present') }}
                    </p>
                  </template>
                  <template v-else-if="blockType === 'skill'">
                    <p><strong>Level:</strong> {{ block.level }}</p>
                    <p v-if="block.years_experience"><strong>Experience:</strong> {{ block.years_experience }} years</p>
                  </template>
                  <template v-else-if="blockType === 'certification'">
                    <p v-if="block.issuing_organization"><strong>Issued by:</strong> {{ block.issuing_organization }}</p>
                    <p v-if="block.issue_date"><strong>Issued:</strong> {{ block.issue_date }}</p>
                    <p v-if="block.expiry_date"><strong>Expires:</strong> {{ block.expiry_date }}</p>
                    <p v-if="block.credential_id"><strong>Credential ID:</strong> {{ block.credential_id }}</p>
                    <p v-if="block.credential_url"><strong>Credential URL:</strong> {{ block.credential_url }}</p>
                  </template>
                  <template v-else-if="blockType === 'misc'">
                    <p v-if="block.content">{{ block.content }}</p>
                  </template>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Duplicate Profile Modal -->
    <div v-if="showCopyModal" class="modal-overlay" @click="showCopyModal = false">
      <div class="modal" @click.stop>
        <h2>Duplicate Profile</h2>
        <p class="modal-description">Create a copy of "{{ duplicatingProfile?.profile_name }}"</p>
        <form @submit.prevent="handleDuplicateProfile" class="form">
          <div class="form-group">
            <label for="duplicate_profile_name">New Profile Name</label>
            <input
              id="duplicate_profile_name"
              v-model="newProfileName"
              required
              autofocus
            />
          </div>
          <div class="modal-actions">
            <button type="button" @click="showCopyModal = false" class="btn btn-secondary" title="Cancel duplication">Cancel</button>
            <button type="submit" class="btn btn-primary" title="Duplicate profile">Duplicate</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Profile Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="closeDeleteModal">
      <div class="modal" @click.stop>
        <h2>Delete Profile</h2>
        <p class="modal-description">
          This action permanently removes
          <strong>{{ deletingProfileName }}</strong>.
        </p>
        <div class="modal-actions">
          <button type="button" @click="closeDeleteModal" class="btn btn-secondary">Cancel</button>
          <button type="button" @click="confirmDeleteProfile" class="btn btn-primary btn-delete">Delete Profile</button>
        </div>
      </div>
    </div>

    <!-- Export Profile Modal -->
    <ExportProfileModal
      v-if="showExportPdfModal"
      :profile-id="exportingProfile?.id"
      :profile-name="exportingProfile?.profile_name"
      @close="showExportPdfModal = false"
      @exported="handleExported"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProfilesStore } from '@/stores/profiles'
import { useConsultantsStore } from '@/stores/consultants'
import ExportProfileModal from '@/components/ExportProfileModal.vue'
import LineIcon from '@/components/LineIcon.vue'

const route = useRoute()
const router = useRouter()
const profilesStore = useProfilesStore()
const consultantsStore = useConsultantsStore()

const consultantId = ref(Number(route.params.id))
const consultant = ref(null)
const profiles = ref([])
const loading = ref(true)
const errorMessage = ref('')

const showViewModal = ref(false)
const viewingProfile = ref(null)
const profileData = ref(null)

const showCopyModal = ref(false)
const duplicatingProfile = ref(null)
const newProfileName = ref('')

const showDeleteModal = ref(false)
const deletingProfileId = ref(null)
const deletingProfileName = ref('')

const showExportPdfModal = ref(false)
const exportingProfile = ref(null)

onMounted(async () => {
  if (!Number.isInteger(consultantId.value) || consultantId.value <= 0) {
    errorMessage.value = 'Invalid consultant identifier.'
    loading.value = false
    return
  }

  try {
    errorMessage.value = ''
    consultant.value = await consultantsStore.fetchConsultant(consultantId.value)
    profiles.value = await profilesStore.fetchConsultantProfiles(consultantId.value)
  } catch (error) {
    console.error('Error loading profile history:', error)
    errorMessage.value = 'Error loading profile history.'
  } finally {
    loading.value = false
  }
})

function goBack() {
  router.push('/admin/consultants')
}

function buildNewProfile() {
  router.push(`/admin/consultants/${consultantId.value}/build-profile`)
}

function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

function formatBlockType(type) {
  if (type === 'misc') return 'Miscellaneous'
  return type.charAt(0).toUpperCase() + type.slice(1) + 's'
}

function getBlockCount(profile) {
  try {
    const blockIds = JSON.parse(profile.selected_block_ids)
    return blockIds.length
  } catch {
    return 0
  }
}

function getBlockTypes(profile) {
  try {
    const data = JSON.parse(profile.profile_data)
    return Object.keys(data.blocks_by_type || {})
  } catch {
    return []
  }
}

function viewProfile(profile) {
  viewingProfile.value = profile
  try {
    profileData.value = JSON.parse(profile.profile_data)
    showViewModal.value = true
  } catch (error) {
    console.error('Error parsing profile data:', error)
    errorMessage.value = 'Error loading profile data.'
  }
}

function showEditModal(profile) {
  router.push(`/admin/consultants/${consultantId.value}/profiles/${profile.id}/edit`)
}

function showDuplicateModal(profile) {
  duplicatingProfile.value = profile
  newProfileName.value = `${profile.profile_name} (Copy)`
  showCopyModal.value = true
}

function showExportModal(profile) {
  exportingProfile.value = profile
  showExportPdfModal.value = true
}

function handleExported() {
  errorMessage.value = ''
}

function openDeleteModal(profile) {
  deletingProfileId.value = profile.id
  deletingProfileName.value = profile.profile_name
  showDeleteModal.value = true
}

function closeDeleteModal() {
  showDeleteModal.value = false
  deletingProfileId.value = null
  deletingProfileName.value = ''
}

async function handleDuplicateProfile() {
  try {
    errorMessage.value = ''
    const newProfile = await profilesStore.duplicateProfile(duplicatingProfile.value.id, newProfileName.value)
    profiles.value.unshift(newProfile)
    showCopyModal.value = false
    newProfileName.value = ''
    duplicatingProfile.value = null
  } catch (error) {
    console.error('Error duplicating profile:', error)
    errorMessage.value = 'Error duplicating profile.'
  }
}

async function confirmDeleteProfile() {
  if (!deletingProfileId.value) {
    return
  }

  try {
    errorMessage.value = ''
    await profilesStore.deleteProfile(deletingProfileId.value)
    profiles.value = profiles.value.filter((p) => p.id !== deletingProfileId.value)
    closeDeleteModal()
  } catch (error) {
    console.error('Error deleting profile:', error)
    errorMessage.value = 'Error deleting profile.'
  }
}
</script>

<style scoped>
.profile-history-view {
  max-width: 1200px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-xl);
}

.header h1 {
  margin: 0 0 var(--spacing-xs) 0;
}

.error-banner {
  margin: 0 0 var(--spacing-md) 0;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  background: #fee2e2;
  border: 1px solid #fecaca;
  color: #991b1b;
  font-size: var(--font-size-sm);
}

.consultant-info {
  color: var(--color-text-secondary);
  margin: 0;
}

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  background: var(--color-surface);
  border-radius: var(--radius-lg);
}

.empty-state p {
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-lg);
}

.profiles-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.profile-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-md);
}

.profile-info h3 {
  margin: 0 0 var(--spacing-xs) 0;
  color: var(--color-text-primary);
}

.profile-meta {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  margin: 0;
}

.profile-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.btn-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--color-border);
  width: 36px;
  height: 36px;
  padding: 0;
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.btn-icon:hover {
  border-color: var(--color-primary);
}

.btn-danger:hover {
  border-color: var(--color-error);
}

.btn-delete {
  background: var(--color-error);
  color: #fff;
  border: none;
}

.btn-delete:hover {
  background: #dc2626;
}

.profile-stats {
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
}

.stat-badge {
  background: var(--color-background);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-large {
  max-width: 900px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.modal-header h2 {
  margin: 0;
}

.btn-close {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 6px;
  color: var(--color-text-secondary);
  border-radius: var(--radius-sm);
}

.btn-close:hover {
  color: var(--color-text-primary);
  background: var(--color-background);
}

.modal-description {
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-lg);
}

.modal-content {
  overflow-y: auto;
}

.profile-preview {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

.consultant-section h3 {
  margin: 0 0 var(--spacing-xs) 0;
}

.consultant-title {
  color: var(--color-primary);
  font-weight: 500;
  margin: 0 0 var(--spacing-xs) 0;
}

.consultant-email {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  margin: 0 0 var(--spacing-sm) 0;
}

.block-section h4 {
  margin: 0 0 var(--spacing-md) 0;
  color: var(--color-primary);
  font-size: var(--font-size-lg);
}

.block-item {
  background: var(--color-background);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-md);
}

.block-item:last-child {
  margin-bottom: 0;
}

.block-item h5 {
  margin: 0 0 var(--spacing-sm) 0;
}

.block-details p {
  margin: 0 0 var(--spacing-xs) 0;
  line-height: 1.6;
}

.block-details p:last-child {
  margin-bottom: 0;
}

.form {
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

.form input {
  width: 100%;
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.form input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb, 59, 130, 246), 0.12);
}

.modal-actions {
  display: flex;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-md);
}

.modal-actions button {
  flex: 1;
}
</style>
