<template>
  <div class="consultants-view">
    <div class="header">
      <h1>Consultants</h1>
      <button @click="showCreateModal = true" class="btn btn-primary" type="button" title="Add consultant">Add Consultant</button>
    </div>

    <p v-if="errorMessage" class="error-banner">{{ errorMessage }}</p>

    <div v-if="loading" class="loading">Loading consultants...</div>

    <div v-else class="consultants-grid">
      <div v-for="consultant in consultants" :key="consultant.id" class="consultant-card">
        <button
          @click="openDeleteModal(consultant)"
          class="consultant-delete-icon btn-icon btn-danger"
          type="button"
          aria-label="Delete consultant"
          title="Delete consultant"
        >
          <LineIcon name="trash" :size="15" />
        </button>
        <div class="consultant-info">
          <h3>{{ consultant.first_name }} {{ consultant.last_name }}</h3>
          <p class="consultant-title">{{ consultant.title }}</p>
          <p class="consultant-email">{{ consultant.email }}</p>
        </div>
        <div class="consultant-actions">
          <button @click="generateLink(consultant.id)" class="btn btn-secondary" type="button" title="Generate link">Generate Link</button>
          <button @click="viewProfiles(consultant.id)" class="btn btn-secondary" type="button" title="View profiles">View Profiles</button>
          <button @click="buildProfile(consultant.id)" class="btn btn-primary" type="button" title="Build profile">Build Profile</button>
        </div>
      </div>
    </div>

    <!-- Create Consultant Modal (simplified) -->
    <div v-if="showCreateModal" class="modal-overlay" @click="showCreateModal = false">
      <div class="modal" @click.stop>
        <h2>Add New Consultant</h2>
        <form @submit.prevent="handleCreateConsultant" class="form">
          <div class="form-group">
            <label for="first_name">First Name</label>
            <input id="first_name" v-model="newConsultant.first_name" required />
          </div>
          <div class="form-group">
            <label for="last_name">Last Name</label>
            <input id="last_name" v-model="newConsultant.last_name" required />
          </div>
          <div class="form-group">
            <label for="email">Email</label>
            <input id="email" v-model="newConsultant.email" type="email" required />
          </div>
          <div class="form-group">
            <label for="title">Title</label>
            <input id="title" v-model="newConsultant.title" required />
          </div>
          <div class="form-group">
            <label for="summary">Summary</label>
            <textarea id="summary" v-model="newConsultant.summary" rows="4"></textarea>
          </div>

          <h3 class="section-title">General Section</h3>
          <div class="form-group">
            <label for="role">Role</label>
            <input id="role" v-model="newConsultant.role" />
          </div>

          <fieldset class="focus-area-section">
            <legend class="focus-area-legend">Focus Areas</legend>
            <div class="focus-area-list">
              <div v-for="(area, index) in newConsultant.focus_areas" :key="index" class="focus-area-row">
                <input
                  :id="`focus_area_${index}`"
                  v-model="newConsultant.focus_areas[index]"
                  :aria-label="`Focus area ${index + 1}`"
                  class="focus-area-input"
                />
                <button type="button" @click="removeFocusArea(index)" class="btn-icon btn-danger" :aria-label="`Remove focus area ${index + 1}`">
                  <LineIcon name="x" :size="14" />
                </button>
              </div>
            </div>
          </fieldset>
          <button type="button" @click="addFocusArea" class="btn btn-secondary add-focus-btn">
            <LineIcon name="plus" :size="14" />
            Add Focus Area
          </button>

          <div class="form-group">
            <label for="years_experience">Years of Experience</label>
            <input id="years_experience" v-model.number="newConsultant.years_experience" type="number" min="0" />
          </div>
          <div class="form-group">
            <label for="motto">Favorite Quote/Motto</label>
            <textarea id="motto" v-model="newConsultant.motto" rows="2"></textarea>
          </div>

          <div class="modal-actions">
            <button type="button" @click="showCreateModal = false" class="btn btn-secondary" title="Cancel create consultant">Cancel</button>
            <button type="submit" class="btn btn-primary">Create</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Edit Link Modal -->
    <div v-if="showLinkModal" class="modal-overlay" @click="showLinkModal = false">
      <div class="modal" @click.stop>
        <h2>Consultant Edit Link</h2>
        <div class="link-modal-content">
          <p class="link-instructions">
            Share this link with the consultant to allow them to edit their profile.
            The link is valid for <strong>{{ linkValidityHours }} hours</strong> from now.
          </p>
          <div class="link-display">
            <label for="generated_link" class="link-label">Shareable Link</label>
            <input
              id="generated_link"
              ref="linkInput"
              :value="generatedLink"
              readonly
              class="link-input"
              @click="selectLink"
            />
          </div>
          <div class="modal-actions">
            <button @click="copyLink" class="btn btn-primary" type="button" title="Copy link">
              {{ linkCopied ? 'Copied!' : 'Copy Link' }}
            </button>
            <button @click="showLinkModal = false" class="btn btn-secondary" type="button" title="Close link modal">Close</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Consultant Modal -->
    <div v-if="showDeleteModal" class="modal-overlay delete-modal-overlay" @click="closeDeleteModal">
      <div class="modal delete-modal" @click.stop>
        <div class="delete-modal-header">
          <span class="delete-modal-tag">Danger Zone</span>
          <h2>Delete Consultant Profile</h2>
          <p class="delete-modal-description">
            This action permanently removes the consultant and cannot be undone.
          </p>
        </div>

        <div v-if="consultantToDelete" class="delete-modal-body">
          <p class="delete-modal-target">
            Confirm deletion for:
            <strong>{{ getConsultantFullName(consultantToDelete) }}</strong>
          </p>
          <label for="delete_consultant_name" class="delete-input-label">
            Type the consultant name to confirm
          </label>
          <input
            id="delete_consultant_name"
            v-model="deleteConfirmationName"
            type="text"
            autocomplete="off"
            class="delete-input"
            :placeholder="getConsultantFullName(consultantToDelete)"
          />
          <p class="delete-help-text">
            You must enter the full name exactly as shown above.
          </p>
        </div>

        <div class="modal-actions delete-modal-actions">
          <button type="button" @click="closeDeleteModal" class="btn btn-secondary" :disabled="isDeleting">Cancel</button>
          <button
            type="button"
            @click="handleDeleteConsultant"
            class="btn btn-danger btn-delete-confirm"
            :disabled="!deleteNameMatches || isDeleting"
          >
            {{ isDeleting ? 'Deleting...' : 'Delete Consultant' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { useConsultantsStore } from '@/stores/consultants'
import api from '@/services/api'
import LineIcon from '@/components/LineIcon.vue'

const router = useRouter()
const consultantsStore = useConsultantsStore()
const { consultants } = storeToRefs(consultantsStore)

const loading = ref(true)
const errorMessage = ref('')
const showCreateModal = ref(false)
const showLinkModal = ref(false)
const showDeleteModal = ref(false)
const generatedLink = ref('')
const linkValidityHours = ref(72)
const linkCopied = ref(false)
const linkInput = ref(null)
const consultantToDelete = ref(null)
const deleteConfirmationName = ref('')
const isDeleting = ref(false)

function createEmptyConsultantForm() {
  return {
    first_name: '',
    last_name: '',
    email: '',
    title: '',
    summary: '',
    role: '',
    focus_areas: [],
    years_experience: null,
    motto: ''
  }
}

const newConsultant = ref(createEmptyConsultantForm())

onMounted(async () => {
  try {
    errorMessage.value = ''
    await consultantsStore.fetchConsultants()
  } catch (error) {
    console.error('Error loading consultants:', error)
    errorMessage.value = 'Failed to load consultants. Please refresh and try again.'
  } finally {
    loading.value = false
  }
})

const deleteNameMatches = computed(() => {
  if (!consultantToDelete.value) {
    return false
  }
  return deleteConfirmationName.value.trim() === getConsultantFullName(consultantToDelete.value)
})

function addFocusArea() {
  newConsultant.value.focus_areas.push('')
}

function removeFocusArea(index) {
  newConsultant.value.focus_areas.splice(index, 1)
}

async function handleCreateConsultant() {
  try {
    errorMessage.value = ''
    // Filter out empty focus areas
    const cleanedData = {
      ...newConsultant.value,
      focus_areas: newConsultant.value.focus_areas.filter(area => area.trim() !== '')
    }
    await consultantsStore.createConsultant(cleanedData)
    showCreateModal.value = false
    newConsultant.value = createEmptyConsultantForm()
  } catch (error) {
    console.error('Error creating consultant:', error)
    errorMessage.value = 'Error creating consultant.'
  }
}

async function generateLink(consultantId) {
  try {
    errorMessage.value = ''
    const response = await api.post('/access-links', { consultant_id: consultantId, validity_hours: 72 })
    generatedLink.value = `${window.location.origin}/edit/${response.data.token}`
    linkValidityHours.value = 72
    linkCopied.value = false
    showLinkModal.value = true
  } catch (error) {
    console.error('Error generating link:', error)
    errorMessage.value = 'Error generating link.'
  }
}

function selectLink() {
  if (linkInput.value) {
    linkInput.value.select()
  }
}

async function copyLink() {
  try {
    await navigator.clipboard.writeText(generatedLink.value)
    linkCopied.value = true
    setTimeout(() => {
      linkCopied.value = false
    }, 2000)
  } catch (error) {
    // Fallback for older browsers
    if (linkInput.value) {
      linkInput.value.select()
      document.execCommand('copy')
      linkCopied.value = true
      setTimeout(() => {
        linkCopied.value = false
      }, 2000)
    }
  }
}

function viewProfiles(consultantId) {
  router.push(`/admin/consultants/${consultantId}/profiles`)
}

function buildProfile(consultantId) {
  router.push(`/admin/consultants/${consultantId}/build-profile`)
}

function getConsultantFullName(consultant) {
  return `${consultant.first_name} ${consultant.last_name}`.trim()
}

function openDeleteModal(consultant) {
  consultantToDelete.value = consultant
  deleteConfirmationName.value = ''
  showDeleteModal.value = true
}

function closeDeleteModal() {
  if (isDeleting.value) {
    return
  }
  showDeleteModal.value = false
  consultantToDelete.value = null
  deleteConfirmationName.value = ''
}

async function handleDeleteConsultant() {
  if (!consultantToDelete.value || !deleteNameMatches.value || isDeleting.value) {
    return
  }

  isDeleting.value = true
  try {
    errorMessage.value = ''
    const consultantId = consultantToDelete.value.id
    await consultantsStore.deleteConsultant(consultantId)
    closeDeleteModal()
  } catch (error) {
    console.error('Error deleting consultant:', error)
    errorMessage.value = 'Error deleting consultant.'
  } finally {
    isDeleting.value = false
  }
}
</script>

<style scoped>
.consultants-view {
  max-width: 1200px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xl);
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

.consultants-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--spacing-lg);
}

.consultant-card {
  position: relative;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.consultant-info h3 {
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--color-text-primary);
}

.consultant-title {
  color: var(--color-primary);
  font-weight: 500;
  margin: 0;
}

.consultant-email {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  margin: 0;
}

.consultant-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}

.consultant-actions button {
  flex: 1;
  min-width: 120px;
  padding: var(--spacing-sm);
  font-size: var(--font-size-sm);
}

.consultant-delete-icon {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  border: 1px solid #fecaca;
  background: #fff1f2;
  color: #b91c1c;
  line-height: 0;
  transition: transform var(--transition-fast), background-color var(--transition-fast), box-shadow var(--transition-fast);
}

.consultant-delete-icon:hover {
  background: #fee2e2;
  transform: translateY(-1px);
  box-shadow: 0 6px 14px rgba(220, 38, 38, 0.2);
}

.consultant-delete-icon:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.2);
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
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.section-title {
  margin-top: var(--spacing-sm);
  margin-bottom: var(--spacing-xs);
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

.form input,
.form textarea {
  width: 100%;
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.form input:focus,
.form textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(232, 93, 41, 0.14);
}

.focus-area-section {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}

.focus-area-legend {
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-xs);
}

.focus-area-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.focus-area-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.focus-area-input {
  flex: 1;
}

.add-focus-btn {
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.modal-actions {
  display: flex;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-md);
}

.modal-actions button {
  flex: 1;
}

.link-modal-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.link-instructions {
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin: 0;
}

.link-display {
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-sm);
}

.link-label {
  display: block;
  font-weight: 600;
  margin-bottom: var(--spacing-xs);
}

.link-input {
  width: 100%;
  background: transparent;
  border: none;
  padding: var(--spacing-xs);
  font-family: monospace;
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  cursor: pointer;
}

.link-input:focus {
  outline: none;
}

.delete-modal-overlay {
  backdrop-filter: blur(3px);
}

.delete-modal {
  max-width: 560px;
  border: 1px solid rgba(220, 38, 38, 0.24);
  box-shadow:
    0 30px 65px rgba(2, 6, 23, 0.35),
    0 12px 26px rgba(220, 38, 38, 0.18);
}

.delete-modal-header {
  margin-bottom: var(--spacing-md);
}

.delete-modal-tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  font-weight: 700;
  color: #991b1b;
  background: #fee2e2;
  border: 1px solid #fecaca;
}

.delete-modal-header h2 {
  margin-top: var(--spacing-sm);
  margin-bottom: 6px;
}

.delete-modal-description {
  margin: 0;
  color: var(--color-text-secondary);
}

.delete-modal-body {
  margin-top: var(--spacing-md);
  margin-bottom: var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.delete-modal-target {
  margin: 0;
  color: var(--color-text-primary);
}

.delete-input-label {
  font-weight: 600;
  color: var(--color-text-primary);
}

.delete-input {
  width: 100%;
  padding: var(--spacing-sm);
  border: 1px solid #fca5a5;
  border-radius: var(--radius-md);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.delete-input:focus {
  outline: none;
  border-color: #dc2626;
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.16);
}

.delete-help-text {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.delete-modal-actions {
  margin-top: 0;
}

.btn-delete-confirm:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

@media (max-width: 720px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm);
  }

  .modal {
    padding: var(--spacing-lg);
  }

  .delete-modal-actions {
    flex-direction: column-reverse;
  }

  .delete-modal-actions button {
    width: 100%;
  }
}
</style>
