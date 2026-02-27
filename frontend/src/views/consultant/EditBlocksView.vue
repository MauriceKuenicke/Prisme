<template>
  <div class="edit-blocks-view">
    <header class="header">
      <h1>Edit Your Profile</h1>
      <p class="info-text">Update your general information and content blocks</p>
    </header>

    <p v-if="errorMessage" class="error-banner">{{ errorMessage }}</p>

    <div v-if="loading" class="loading">Loading your profile...</div>

    <div v-else>
      <!-- General Section -->
      <div class="general-section">
        <div class="section-header">
          <h2>General Information</h2>
          <button @click="showGeneralModal = true" class="btn btn-primary">Edit General Info</button>
        </div>
        <div v-if="consultant" class="general-info-card">
          <div class="info-item">
            <strong>Name:</strong> {{ consultant.first_name }} {{ consultant.last_name }}
          </div>
          <div class="info-item">
            <strong>Title:</strong> {{ consultant.title }}
          </div>
          <div class="info-item" v-if="consultant.role">
            <strong>Role:</strong> {{ consultant.role }}
          </div>
          <div class="info-item" v-if="consultant.focus_areas && consultant.focus_areas.length > 0">
            <strong>Focus Areas:</strong> {{ consultant.focus_areas.join(', ') }}
          </div>
          <div class="info-item" v-if="consultant.years_experience">
            <strong>Years of Experience:</strong> {{ consultant.years_experience }}
          </div>
          <div class="info-item" v-if="consultant.motto">
            <strong>Motto:</strong> "{{ consultant.motto }}"
          </div>
        </div>
      </div>

      <div class="blocks-container">
        <div v-for="type in blockTypes" :key="type" class="block-section">
          <div class="section-header">
            <h2>{{ formatBlockType(type) }}</h2>
            <button @click="showCreateModal(type)" class="btn btn-primary">Add {{ formatBlockTypeSingular(type) }}</button>
          </div>

          <div v-if="blocksByType[type].length === 0" class="empty-message">
            No {{ formatBlockType(type).toLowerCase() }} yet. Click "Add {{ formatBlockTypeSingular(type) }}" to create one.
          </div>

          <div v-else class="blocks-list">
            <div v-for="block in blocksByType[type]" :key="block.id" class="block-card">
              <div class="block-content">
                <h3>{{ block.title }}</h3>
                <p class="block-meta">{{ getBlockMeta(block) }}</p>
              </div>
              <div class="block-actions">
                <button @click="editBlock(block)" class="btn-icon" type="button" title="Edit block" aria-label="Edit block">
                  <LineIcon name="pencil" :size="16" />
                </button>
                <button @click="openDeleteModal(block)" class="btn-icon btn-danger" type="button" title="Delete block" aria-label="Delete block">
                  <LineIcon name="trash" :size="16" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Block Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="closeDeleteModal">
      <div class="modal" @click.stop>
        <h2>Delete Block</h2>
        <p class="modal-description">
          This action permanently removes
          <strong>{{ deletingBlockTitle }}</strong>.
        </p>
        <div class="modal-actions">
          <button type="button" @click="closeDeleteModal" class="btn btn-secondary">Cancel</button>
          <button type="button" @click="confirmDeleteBlock" class="btn btn-primary btn-delete">Delete Block</button>
        </div>
      </div>
    </div>

    <!-- Simple Create/Edit Modal -->
    <div v-if="showModal" class="modal-overlay" @click="showModal = false">
      <div class="modal" @click.stop>
        <h2>{{ editingBlock ? 'Edit' : 'Create' }} {{ formatBlockTypeSingular(currentBlockType) }} Block</h2>
        <form @submit.prevent="handleSaveBlock" class="form">
          <div class="form-group">
            <label for="block_title">Title</label>
            <input id="block_title" v-model="blockForm.title" required />
          </div>

          <template v-if="currentBlockType === 'project'">
            <div class="form-group">
              <label for="client_name">Client Name</label>
              <input id="client_name" v-model="blockForm.client_name" />
            </div>
            <div class="form-group">
              <label for="project_description">Description</label>
              <textarea id="project_description" v-model="blockForm.project_description" rows="3"></textarea>
            </div>
            <div class="form-group">
              <label for="project_role">Your Role</label>
              <input id="project_role" v-model="blockForm.role" />
            </div>
            <div class="date-row">
              <div class="date-field">
                <label class="date-label">Start Date</label>
                <div class="date-selects">
                  <select v-model="startMonth" class="month-select">
                    <option value="">Month</option>
                    <option v-for="(month, idx) in months" :key="idx" :value="idx + 1">{{ month }}</option>
                  </select>
                  <select v-model="startYear" class="year-select">
                    <option value="">Year</option>
                    <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
                  </select>
                </div>
              </div>
              <div class="date-field">
                <label class="date-label">End Date</label>
                <div class="date-selects">
                  <select v-model="endMonth" class="month-select" :disabled="blockForm.is_ongoing">
                    <option value="">Month</option>
                    <option v-for="(month, idx) in months" :key="idx" :value="idx + 1">{{ month }}</option>
                  </select>
                  <select v-model="endYear" class="year-select" :disabled="blockForm.is_ongoing">
                    <option value="">Year</option>
                    <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
                  </select>
                </div>
              </div>
            </div>
            <div class="checkbox-row">
              <label>
                <input v-model="blockForm.is_ongoing" type="checkbox" />
                <span>This project is ongoing</span>
              </label>
            </div>
          </template>

          <template v-if="currentBlockType === 'skill'">
            <div class="form-group">
              <label for="skill_proficiency">Proficiency</label>
              <select id="skill_proficiency" v-model="blockForm.proficiency_level">
                <option value="">Select Proficiency</option>
                <option v-for="level in SKILL_PROFICIENCY_LEVELS" :key="level" :value="level">{{ level }}</option>
              </select>
            </div>
          </template>

          <template v-if="currentBlockType === 'misc'">
            <div class="form-group">
              <label for="misc_content">Details</label>
              <textarea id="misc_content" v-model="blockForm.misc_content" rows="4" placeholder="Add talks, presentations, blogs, websites, or other relevant information."></textarea>
            </div>
          </template>

          <template v-if="currentBlockType === 'certification'">
            <div class="form-group">
              <label for="issuing_organization">Issuing Organization</label>
              <input id="issuing_organization" v-model="blockForm.issuing_organization" />
            </div>
            <div class="form-group">
              <label for="credential_id">Credential ID</label>
              <input id="credential_id" v-model="blockForm.credential_id" />
            </div>
            <div class="form-group">
              <label for="credential_url">Credential URL</label>
              <input id="credential_url" v-model="blockForm.credential_url" type="url" />
            </div>
          </template>

          <div class="modal-actions">
            <button type="button" @click="showModal = false" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary">Save</button>
          </div>
        </form>
      </div>
    </div>

    <!-- General Info Modal -->
    <div v-if="showGeneralModal" class="modal-overlay" @click="showGeneralModal = false">
      <div class="modal" @click.stop>
        <h2>Edit General Information</h2>
        <form @submit.prevent="handleSaveGeneral" class="form">
          <div class="form-group">
            <label for="general_role">Role</label>
            <input id="general_role" v-model="generalForm.role" />
          </div>

          <fieldset class="focus-area-section">
            <legend class="focus-area-legend">Focus Areas</legend>
            <div class="focus-area-list">
              <div v-for="(area, index) in generalForm.focus_areas" :key="index" class="focus-area-row">
                <input
                  :id="`general_focus_area_${index}`"
                  v-model="generalForm.focus_areas[index]"
                  :aria-label="`Focus area ${index + 1}`"
                  class="focus-area-input"
                />
                <button type="button" @click="removeGeneralFocusArea(index)" class="btn-icon btn-danger" :aria-label="`Remove focus area ${index + 1}`">
                  <LineIcon name="x" :size="14" />
                </button>
              </div>
            </div>
          </fieldset>
          <button type="button" @click="addGeneralFocusArea" class="btn btn-secondary add-focus-btn">
            <LineIcon name="plus" :size="14" />
            Add Focus Area
          </button>

          <div class="form-group">
            <label for="general_years_experience">Years of Experience</label>
            <input id="general_years_experience" v-model.number="generalForm.years_experience" type="number" min="0" />
          </div>
          <div class="form-group">
            <label for="general_motto">Favorite Quote/Motto</label>
            <textarea id="general_motto" v-model="generalForm.motto" rows="2"></textarea>
          </div>
          <div class="modal-actions">
            <button type="button" @click="showGeneralModal = false" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary">Save</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBlocksStore } from '@/stores/blocks'
import api from '@/services/api'
import LineIcon from '@/components/LineIcon.vue'
import { SKILL_PROFICIENCY_LEVELS } from '@/constants/skills'

const route = useRoute()
const router = useRouter()
const blocksStore = useBlocksStore()

const loading = ref(true)
const token = ref(typeof route.params.token === 'string' ? route.params.token : '')
const blockTypes = ['project', 'skill', 'misc', 'certification']
const consultant = ref(null)
const errorMessage = ref('')

const showModal = ref(false)
const showGeneralModal = ref(false)
const showDeleteModal = ref(false)
const editingBlock = ref(null)
const deletingBlockId = ref(null)
const deletingBlockTitle = ref('')
const currentBlockType = ref('')
const blockForm = ref({})
const generalForm = ref({
  role: '',
  focus_areas: [],
  years_experience: null,
  motto: ''
})

// Date selection helpers
const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
const currentYear = new Date().getFullYear()
const years = Array.from({ length: 50 }, (_, i) => currentYear - i + 5) // 5 years future to 45 years past

const startMonth = ref('')
const startYear = ref('')
const endMonth = ref('')
const endYear = ref('')

const blocksByType = computed(() => blocksStore.blocksByType)

onMounted(async () => {
  if (!token.value.trim()) {
    router.replace('/access-expired')
    return
  }

  try {
    errorMessage.value = ''
    await blocksStore.fetchBlocks(null, token.value)
    // Fetch consultant data
    const response = await api.get(`/consultants/edit/${token.value}`)
    consultant.value = response.data
    generalForm.value = {
      role: consultant.value.role || '',
      focus_areas: Array.isArray(consultant.value.focus_areas) ? [...consultant.value.focus_areas] : [],
      years_experience: consultant.value.years_experience ?? null,
      motto: consultant.value.motto || ''
    }
  } catch (error) {
    console.error('Error loading consultant edit page:', error)
    router.push('/access-expired')
  } finally {
    loading.value = false
  }
})

function showCreateModal(type) {
  currentBlockType.value = type
  editingBlock.value = null
  blockForm.value = { block_type: type, title: '' }
  // Reset date selects
  startMonth.value = ''
  startYear.value = ''
  endMonth.value = ''
  endYear.value = ''
  showModal.value = true
}

function editBlock(block) {
  currentBlockType.value = block.block_type
  editingBlock.value = block
  blockForm.value = { ...block }

  // Parse existing dates into month/year selects
  if (block.start_date) {
    const [year, month] = block.start_date.split('-')
    startYear.value = year
    startMonth.value = parseInt(month, 10).toString()
  } else {
    startMonth.value = ''
    startYear.value = ''
  }

  if (block.end_date) {
    const [year, month] = block.end_date.split('-')
    endYear.value = year
    endMonth.value = parseInt(month, 10).toString()
  } else {
    endMonth.value = ''
    endYear.value = ''
  }

  showModal.value = true
}

async function handleSaveBlock() {
  try {
    errorMessage.value = ''
    const formData = { ...blockForm.value }

    // Build date strings from month/year selects
    if (startYear.value && startMonth.value) {
      const month = startMonth.value.toString().padStart(2, '0')
      formData.start_date = `${startYear.value}-${month}-01`
    } else {
      formData.start_date = null
    }

    if (formData.is_ongoing) {
      formData.end_date = null
    } else if (endYear.value && endMonth.value) {
      const month = endMonth.value.toString().padStart(2, '0')
      formData.end_date = `${endYear.value}-${month}-01`
    } else {
      formData.end_date = null
    }

    if (editingBlock.value) {
      await blocksStore.updateBlock(editingBlock.value.id, formData, token.value)
    } else {
      await blocksStore.createBlock(formData, token.value)
    }
    showModal.value = false
    blockForm.value = {}
    startMonth.value = ''
    startYear.value = ''
    endMonth.value = ''
    endYear.value = ''
  } catch (error) {
    console.error('Error saving block:', error)
    errorMessage.value = 'Error saving block.'
  }
}

function openDeleteModal(block) {
  deletingBlockId.value = block.id
  deletingBlockTitle.value = block.title
  showDeleteModal.value = true
}

function closeDeleteModal() {
  showDeleteModal.value = false
  deletingBlockId.value = null
  deletingBlockTitle.value = ''
}

async function confirmDeleteBlock() {
  if (!deletingBlockId.value) {
    return
  }

  try {
    errorMessage.value = ''
    await blocksStore.deleteBlock(deletingBlockId.value, token.value)
    closeDeleteModal()
  } catch (error) {
    console.error('Error deleting block:', error)
    errorMessage.value = 'Error deleting block.'
  }
}

function addGeneralFocusArea() {
  generalForm.value.focus_areas.push('')
}

function removeGeneralFocusArea(index) {
  generalForm.value.focus_areas.splice(index, 1)
}

async function handleSaveGeneral() {
  try {
    errorMessage.value = ''
    // Filter out empty focus areas
    const cleanedData = {
      ...generalForm.value,
      focus_areas: generalForm.value.focus_areas.filter(area => area.trim() !== '')
    }
    const response = await api.put(`/consultants/edit/${token.value}`, cleanedData)
    consultant.value = response.data
    showGeneralModal.value = false
  } catch (error) {
    console.error('Error saving general info:', error)
    errorMessage.value = 'Error saving general information.'
  }
}

function formatBlockType(type) {
  if (type === 'misc') return 'Miscellaneous'
  return type.charAt(0).toUpperCase() + type.slice(1) + 's'
}

function formatBlockTypeSingular(type) {
  if (type === 'misc') return 'Misc Item'
  return type.charAt(0).toUpperCase() + type.slice(1)
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  // Handle both YYYY-MM and YYYY-MM-DD formats
  const parts = dateStr.split('-')
  if (parts.length >= 2) {
    const year = parts[0]
    const month = new Date(year, parseInt(parts[1]) - 1).toLocaleDateString('en-US', { month: 'short' })
    return `${month} ${year}`
  }
  return dateStr
}

function getBlockMeta(block) {
  if (block.block_type === 'project') {
    const client = block.client_name || 'No client'
    let dateRange = ''
    if (block.start_date) {
      dateRange = formatDate(block.start_date)
      if (block.is_ongoing) {
        dateRange += ' - Present'
      } else if (block.end_date) {
        dateRange += ' - ' + formatDate(block.end_date)
      }
    }
    return dateRange ? `${client} • ${dateRange}` : client
  } else if (block.block_type === 'skill') {
    return block.proficiency_level || 'Unknown'
  } else if (block.block_type === 'misc') {
    return block.misc_content || 'Additional details'
  } else if (block.block_type === 'certification') {
    return block.issuing_organization || 'No organization'
  }
  return ''
}
</script>

<style scoped>
.edit-blocks-view {
  min-height: 100vh;
  padding: var(--spacing-xl);
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: var(--spacing-2xl);
}

.header h1 {
  color: var(--color-primary);
  margin-bottom: var(--spacing-sm);
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

.info-text {
  color: var(--color-text-secondary);
}

.general-section {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--spacing-2xl);
}

.general-info-card {
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
}

.info-item {
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--color-border);
}

.info-item:last-child {
  border-bottom: none;
}

.info-item strong {
  color: var(--color-primary);
  margin-right: var(--spacing-sm);
}

.blocks-container {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2xl);
}

.block-section {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.section-header h2 {
  margin: 0;
}

.blocks-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.block-card {
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.block-content h3 {
  margin: 0 0 var(--spacing-xs) 0;
  font-size: var(--font-size-lg);
}

.block-meta {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  margin: 0;
}

.block-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.btn-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--color-border);
  width: 34px;
  height: 34px;
  padding: 0;
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.btn-icon:hover {
  border-color: var(--color-primary);
}

.btn-danger:hover {
  border-color: var(--color-error);
  color: var(--color-error);
}

.btn-delete {
  background: var(--color-error);
  color: #fff;
  border: none;
}

.btn-delete:hover {
  background: #dc2626;
}

.empty-message {
  text-align: center;
  padding: var(--spacing-xl);
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

.modal-description {
  margin: 0;
  color: var(--color-text-secondary);
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

.form input,
.form textarea,
.form select {
  width: 100%;
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.form input:focus,
.form textarea:focus,
.form select:focus {
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
  margin-bottom: var(--spacing-md);
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

.date-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-sm);
}

.date-field {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.date-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  font-weight: 500;
}

.date-selects {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--spacing-xs);
}

.month-select,
.year-select {
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-family: inherit;
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  background: var(--color-background);
  cursor: pointer;
}

.month-select:disabled,
.year-select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: var(--color-surface);
}

.checkbox-row {
  display: flex;
  align-items: center;
}

.checkbox-row label {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  cursor: pointer;
  user-select: none;
}

.checkbox-row input[type="checkbox"] {
  width: auto;
  cursor: pointer;
}

.checkbox-row span {
  color: var(--color-text-primary);
}

@media (max-width: 720px) {
  .edit-blocks-view {
    padding: var(--spacing-lg);
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm);
  }

  .date-row {
    grid-template-columns: 1fr;
  }
}
</style>
