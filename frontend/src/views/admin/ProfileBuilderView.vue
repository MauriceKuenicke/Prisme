<template>
  <div class="profile-builder">
    <div class="builder-header">
      <h1>{{ isEditMode ? 'Edit' : 'Build' }} Profile: {{ consultant?.first_name }} {{ consultant?.last_name }}</h1>
      <div class="field-group">
        <label for="profile_name_input" class="field-label">Profile Name</label>
        <input id="profile_name_input" v-model="profileName" class="profile-name-input" />
      </div>
    </div>

    <p v-if="errorMessage" class="error-banner">{{ errorMessage }}</p>

    <div class="builder-content">
      <!-- Left sidebar: Available blocks -->
      <aside class="blocks-sidebar">
        <div v-for="type in blockTypes" :key="type" class="block-type-section">
          <h3>{{ formatBlockType(type) }}</h3>
          <div class="block-list">
            <div
              v-for="block in blocksByType[type]"
              :key="block.id"
              class="block-item"
              :class="{ selected: isSelected(block.id) }"
              @click="toggleBlock(block)"
            >
              <div class="block-item-content">
                <h4>{{ block.title }}</h4>
                <p class="block-meta">{{ getBlockMeta(block) }}</p>
              </div>
              <span v-if="isSelected(block.id)" class="selected-badge" aria-label="Selected">
                <LineIcon name="check" :size="18" />
              </span>
            </div>
          </div>
        </div>
      </aside>

      <!-- Right panel: Selected blocks with customization -->
      <main class="profile-preview">
        <!-- General Section - Editable -->
        <div v-if="consultant" class="general-section">
          <h2>General Information (Customizable for this profile)</h2>
          <div class="general-info-card editable">
            <div class="field-group">
              <label for="general_role_input" class="field-label">Role</label>
              <input
                id="general_role_input"
                v-model="generalCustomizations.role"
                class="field-input"
              />
            </div>
            <div class="field-group focus-area-group">
              <fieldset class="focus-area-section">
                <legend class="field-label focus-area-legend">Focus Areas</legend>
                <div class="focus-area-list">
                  <div v-for="(area, index) in generalCustomizations.focus_areas" :key="index" class="focus-area-row">
                    <input
                      :id="`general_focus_area_${index}`"
                      v-model="generalCustomizations.focus_areas[index]"
                      :aria-label="`Focus area ${index + 1}`"
                      class="field-input"
                    />
                    <button type="button" @click="removeFocusArea(index)" class="remove-btn focus-area-remove-btn" :aria-label="`Remove focus area ${index + 1}`" title="Remove">
                      <LineIcon name="x" :size="14" />
                    </button>
                  </div>
                </div>
              </fieldset>
              <button type="button" @click="addFocusArea" class="btn btn-secondary add-focus-btn">
                <LineIcon name="plus" :size="14" />
                Add Focus Area
              </button>
            </div>
            <div class="field-group">
              <label for="general_years_experience_input" class="field-label">Years of Experience</label>
              <input
                id="general_years_experience_input"
                v-model.number="generalCustomizations.years_experience"
                type="number"
                min="0"
                class="field-input"
              />
            </div>
            <div class="field-group">
              <label for="general_motto_input" class="field-label">Motto</label>
              <textarea
                id="general_motto_input"
                v-model="generalCustomizations.motto"
                rows="2"
                class="field-textarea"
              ></textarea>
            </div>
          </div>
        </div>

        <h2>Selected Blocks ({{ selectedBlockIds.length }})</h2>

        <div v-if="selectedBlockIds.length === 0" class="empty-state">
          <p>Select blocks from the left to build the profile</p>
        </div>

        <div v-else class="selected-blocks">
          <div v-for="type in blockTypes" :key="type">
            <template v-if="selectedByType[type].length > 0">
              <h3>{{ formatBlockType(type) }} ({{ selectedByType[type].length }})</h3>
              <div class="selected-block-list" :class="{ 'skill-block-list': type === 'skill' }">
                <div
                  v-for="block in selectedByType[type]"
                  :key="block.id"
                  class="selected-block-card editable"
                  :class="{ 'skill-card': block.block_type === 'skill' }"
                >
                  <div class="block-header">
                    <div class="field-group field-group-flex">
                      <label :for="`block_title_${block.id}`" class="field-label">Block Title</label>
                      <input :id="`block_title_${block.id}`" v-model="customizations[block.id].title" class="block-title-input" />
                    </div>
                    <button @click="removeBlock(block.id)" class="remove-btn" title="Remove block" aria-label="Remove block">
                      <LineIcon name="x" :size="14" />
                    </button>
                  </div>

                  <!-- Project customization -->
                  <div v-if="block.block_type === 'project'" class="block-fields">
                    <div class="field-group">
                      <label :for="`client_name_${block.id}`" class="field-label">Client Name</label>
                      <input :id="`client_name_${block.id}`" v-model="customizations[block.id].client_name" class="field-input" />
                    </div>
                    <div class="field-group">
                      <label :for="`project_role_${block.id}`" class="field-label">Your Role</label>
                      <input :id="`project_role_${block.id}`" v-model="customizations[block.id].role" class="field-input" />
                    </div>
                    <div class="field-group">
                      <label :for="`project_description_${block.id}`" class="field-label">Project Description</label>
                      <textarea :id="`project_description_${block.id}`" v-model="customizations[block.id].description" rows="3" class="field-textarea"></textarea>
                    </div>
                    <div class="field-group">
                      <label :for="`project_technologies_${block.id}`" class="field-label">Technologies (comma separated)</label>
                      <textarea :id="`project_technologies_${block.id}`" v-model="customizations[block.id].technologies" rows="2" class="field-textarea"></textarea>
                    </div>
                    <div class="field-group">
                      <label :for="`duration_months_${block.id}`" class="field-label">Duration (months)</label>
                      <input :id="`duration_months_${block.id}`" v-model.number="customizations[block.id].duration_months" type="number" min="0" class="field-input" />
                    </div>
                    <div class="field-group checkbox-field">
                      <label :for="`is_ongoing_${block.id}`" class="checkbox-label">
                        <input
                          :id="`is_ongoing_${block.id}`"
                          v-model="customizations[block.id].is_ongoing"
                          type="checkbox"
                          @change="handleProjectOngoingToggle(block.id)"
                        />
                        Ongoing project
                      </label>
                    </div>
                    <div class="field-row">
                      <div class="field-group field-group-flex">
                        <label :for="`start_date_${block.id}`" class="field-label">Start Date</label>
                        <input :id="`start_date_${block.id}`" v-model="customizations[block.id].start_date" class="field-input small" />
                      </div>
                      <div class="field-group field-group-flex">
                        <label :for="`end_date_${block.id}`" class="field-label">End Date</label>
                        <input :id="`end_date_${block.id}`" v-model="customizations[block.id].end_date" :disabled="customizations[block.id].is_ongoing" class="field-input small" />
                      </div>
                    </div>
                  </div>

                  <!-- Skill customization -->
                  <div v-else-if="block.block_type === 'skill'" class="block-fields skill-fields">
                    <div class="field-group">
                      <label :for="`skill_level_${block.id}`" class="field-label">Proficiency Level</label>
                      <select :id="`skill_level_${block.id}`" v-model="customizations[block.id].level" class="field-input">
                        <option value="">Select Proficiency</option>
                        <option
                          v-for="level in SKILL_PROFICIENCY_LEVELS"
                          :key="`skill_level_${block.id}_${level}`"
                          :value="level"
                        >
                          {{ level }}
                        </option>
                      </select>
                    </div>
                  </div>

                  <!-- Misc customization -->
                  <div v-else-if="block.block_type === 'misc'" class="block-fields">
                    <div class="field-group">
                      <label :for="`misc_content_${block.id}`" class="field-label">Details</label>
                      <textarea :id="`misc_content_${block.id}`" v-model="customizations[block.id].content" rows="4" class="field-textarea"></textarea>
                    </div>
                  </div>

                  <!-- Certification customization -->
                  <div v-else-if="block.block_type === 'certification'" class="block-fields">
                    <div class="field-group">
                      <label :for="`issuing_org_${block.id}`" class="field-label">Issuing Organization</label>
                      <input :id="`issuing_org_${block.id}`" v-model="customizations[block.id].issuing_organization" class="field-input" />
                    </div>
                    <div class="field-group">
                      <label :for="`issue_date_${block.id}`" class="field-label">Issue Date</label>
                      <input :id="`issue_date_${block.id}`" v-model="customizations[block.id].issue_date" class="field-input" />
                    </div>
                    <div class="field-group">
                      <label :for="`expiry_date_${block.id}`" class="field-label">Expiry Date</label>
                      <input :id="`expiry_date_${block.id}`" v-model="customizations[block.id].expiry_date" class="field-input" />
                    </div>
                    <div class="field-group">
                      <label :for="`credential_id_${block.id}`" class="field-label">Credential ID</label>
                      <input :id="`credential_id_${block.id}`" v-model="customizations[block.id].credential_id" class="field-input" />
                    </div>
                    <div class="field-group">
                      <label :for="`credential_url_${block.id}`" class="field-label">Credential URL</label>
                      <input :id="`credential_url_${block.id}`" v-model="customizations[block.id].credential_url" class="field-input" />
                    </div>
                  </div>
                </div>
              </div>
            </template>
          </div>
        </div>
      </main>
    </div>

    <footer class="builder-footer">
      <button @click="goBack" class="btn btn-secondary">Cancel</button>
      <button @click="saveProfile" :disabled="!canSave" class="btn btn-primary">
        {{ isEditMode ? 'Update' : 'Save' }} Profile
      </button>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBlocksStore } from '@/stores/blocks'
import { useConsultantsStore } from '@/stores/consultants'
import { useProfilesStore } from '@/stores/profiles'
import LineIcon from '@/components/LineIcon.vue'
import { SKILL_PROFICIENCY_LEVELS } from '@/constants/skills'

const route = useRoute()
const router = useRouter()
const blocksStore = useBlocksStore()
const consultantsStore = useConsultantsStore()
const profilesStore = useProfilesStore()

const consultant = ref(null)
const profileName = ref('')
const selectedBlockIds = ref([])
const customizations = ref({})
const errorMessage = ref('')

function createGeneralCustomizations(data = {}) {
  return {
    role: data.role || '',
    focus_areas: Array.isArray(data.focus_areas) ? [...data.focus_areas] : [],
    years_experience: data.years_experience ?? null,
    motto: data.motto || ''
  }
}

const generalCustomizations = ref(createGeneralCustomizations())
const isEditMode = ref(false)
const editingProfileId = ref(null)

const blockTypes = ['project', 'skill', 'misc', 'certification']
const selectedBlockIdSet = computed(() => new Set(selectedBlockIds.value))

const blocksByType = computed(() => blocksStore.blocksByType)
const selectedBlocks = computed(() => blocksStore.blocks.filter((b) => selectedBlockIdSet.value.has(b.id)))
const selectedByType = computed(() => {
  const grouped = {}
  blockTypes.forEach((type) => {
    grouped[type] = selectedBlocks.value.filter((b) => b.block_type === type)
  })
  return grouped
})

const canSave = computed(() => profileName.value.trim().length > 0 && selectedBlockIds.value.length > 0)

onMounted(async () => {
  const consultantId = Number(route.params.id)
  const profileId = route.params.profileId ? Number(route.params.profileId) : null

  if (!consultantId) {
    errorMessage.value = 'Invalid consultant identifier.'
    return
  }

  try {
    errorMessage.value = ''
    consultant.value = await consultantsStore.fetchConsultant(consultantId)
    await blocksStore.fetchBlocks(consultantId)

    // Initialize general customizations with consultant's current data.
    generalCustomizations.value = createGeneralCustomizations(consultant.value)

    if (profileId) {
      isEditMode.value = true
      editingProfileId.value = profileId
      await loadProfile(editingProfileId.value)
    }
  } catch (error) {
    console.error('Error loading profile builder:', error)
    errorMessage.value = 'Failed to load profile builder data.'
  }
})

// Watch for new block selections and initialize customizations
watch(selectedBlockIds, (newIds) => {
  newIds.forEach(id => {
    if (!customizations.value[id]) {
      const block = blocksStore.blocks.find(b => b.id === id)
      if (block) {
        initializeCustomization(block)
      }
    }
  })
})

async function loadProfile(profileId) {
  try {
    const profile = await profilesStore.fetchProfile(profileId)
    profileName.value = profile.profile_name

    const profileData = JSON.parse(profile.profile_data)

    // Extract general customizations if they exist
    if (profileData.general_customizations) {
      generalCustomizations.value = createGeneralCustomizations(profileData.general_customizations)
    }

    // Extract block IDs and customizations from profile_data
    const blockIds = []
    const customs = {}

    Object.values(profileData.blocks_by_type || {}).forEach(blocks => {
      blocks.forEach(block => {
        blockIds.push(block.id)
        customs[block.id] = extractCustomization(block)
      })
    })

    selectedBlockIds.value = blockIds
    customizations.value = customs
  } catch (error) {
    console.error('Error loading profile:', error)
    errorMessage.value = 'Error loading profile for editing.'
  }
}

function extractCustomization(block) {
  const custom = {
    title: block.title
  }

  if (block.block_type === 'project') {
    custom.client_name = block.client_name || ''
    custom.role = block.role || ''
    custom.description = block.description || ''
    custom.start_date = block.start_date || ''
    custom.end_date = block.end_date || ''
    custom.technologies = formatTechnologiesForInput(block.technologies)
    custom.duration_months = block.duration_months ?? null
    custom.is_ongoing = Boolean(block.is_ongoing)
  } else if (block.block_type === 'skill') {
    custom.level = block.level || ''
  } else if (block.block_type === 'misc') {
    custom.content = block.content || ''
  } else if (block.block_type === 'certification') {
    custom.issuing_organization = block.issuing_organization || ''
    custom.issue_date = block.issue_date || ''
    custom.expiry_date = block.expiry_date || ''
    custom.credential_id = block.credential_id || ''
    custom.credential_url = block.credential_url || ''
  }

  return custom
}

function initializeCustomization(block) {
  const custom = {
    title: block.title
  }

  if (block.block_type === 'project') {
    custom.client_name = block.client_name || ''
    custom.role = block.role || ''
    custom.description = block.project_description || ''
    custom.technologies = formatTechnologiesForInput(block.technologies)
    custom.duration_months = block.duration_months ?? null
    custom.is_ongoing = Boolean(block.is_ongoing)
    custom.start_date = formatDate(block.start_date)
    custom.end_date = block.is_ongoing ? '' : formatDate(block.end_date)
  } else if (block.block_type === 'skill') {
    custom.level = block.proficiency_level || ''
  } else if (block.block_type === 'misc') {
    custom.content = block.misc_content || ''
  } else if (block.block_type === 'certification') {
    custom.issuing_organization = block.issuing_organization || ''
    custom.issue_date = formatDate(block.issue_date)
    custom.expiry_date = formatDate(block.expiry_date)
    custom.credential_id = block.credential_id || ''
    custom.credential_url = block.credential_url || ''
  }

  customizations.value[block.id] = custom
}

function formatTechnologiesForInput(value) {
  if (!value) {
    return ''
  }

  if (Array.isArray(value)) {
    return value.join(', ')
  }

  if (typeof value === 'string') {
    const trimmed = value.trim()
    if (!trimmed) {
      return ''
    }

    try {
      const parsed = JSON.parse(trimmed)
      if (Array.isArray(parsed)) {
        return parsed.join(', ')
      }
    } catch {
      // Keep the original string when not JSON.
    }

    return trimmed
  }

  return ''
}

function normalizeTechnologies(value) {
  if (!value) {
    return []
  }

  if (Array.isArray(value)) {
    return value.map((entry) => String(entry).trim()).filter(Boolean)
  }

  return String(value)
    .split(',')
    .map((entry) => entry.trim())
    .filter(Boolean)
}

function buildCleanedCustomizations() {
  const cleaned = {}

  selectedBlockIds.value.forEach((blockId) => {
    const source = customizations.value[blockId] || {}
    const normalized = { ...source }
    const block = blocksStore.blocks.find((entry) => entry.id === blockId)

    if (block?.block_type === 'project') {
      normalized.technologies = normalizeTechnologies(source.technologies)
      normalized.duration_months =
        source.duration_months === '' || source.duration_months === null || source.duration_months === undefined
          ? null
          : Number(source.duration_months)
      normalized.is_ongoing = Boolean(source.is_ongoing)
      if (normalized.is_ongoing) {
        normalized.end_date = ''
      }
    }

    cleaned[String(blockId)] = normalized
  })

  return cleaned
}

function handleProjectOngoingToggle(blockId) {
  const customization = customizations.value[blockId]
  if (!customization) {
    return
  }

  if (customization.is_ongoing) {
    customization.end_date = ''
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const parts = dateStr.split('-')
  if (parts.length >= 2) {
    const year = parts[0]
    const month = new Date(year, parseInt(parts[1]) - 1).toLocaleDateString('en-US', { month: 'short' })
    return `${month} ${year}`
  }
  return dateStr
}

function isSelected(blockId) {
  return selectedBlockIdSet.value.has(blockId)
}

function toggleBlock(block) {
  const index = selectedBlockIds.value.indexOf(block.id)
  if (index > -1) {
    selectedBlockIds.value.splice(index, 1)
    delete customizations.value[block.id]
  } else {
    selectedBlockIds.value.push(block.id)
    initializeCustomization(block)
  }
}

function removeBlock(blockId) {
  const index = selectedBlockIds.value.indexOf(blockId)
  if (index > -1) {
    selectedBlockIds.value.splice(index, 1)
    delete customizations.value[blockId]
  }
}

function addFocusArea() {
  generalCustomizations.value.focus_areas.push('')
}

function removeFocusArea(index) {
  generalCustomizations.value.focus_areas.splice(index, 1)
}

async function saveProfile() {
  try {
    errorMessage.value = ''
    // Clean up general customizations
    const cleanedGeneralCustomizations = {
      ...generalCustomizations.value,
      focus_areas: generalCustomizations.value.focus_areas.filter(area => area.trim() !== '')
    }

    // Build profile data with customizations
    const profileData = {
      profile_name: profileName.value,
      selected_block_ids: selectedBlockIds.value,
      customizations: buildCleanedCustomizations(),
      general_customizations: cleanedGeneralCustomizations
    }

    if (isEditMode.value) {
      await profilesStore.updateProfile(editingProfileId.value, profileData)
    } else {
      await profilesStore.createProfile({
        ...profileData,
        consultant_id: consultant.value.id
      })
    }

    router.push(`/admin/consultants/${consultant.value.id}/profiles`)
  } catch (error) {
    console.error('Error saving profile:', error)
    errorMessage.value = `Error ${isEditMode.value ? 'updating' : 'creating'} profile.`
  }
}

function goBack() {
  if (consultant.value) {
    router.push(`/admin/consultants/${consultant.value.id}/profiles`)
  } else {
    router.push('/admin/consultants')
  }
}

function formatBlockType(type) {
  if (type === 'misc') return 'Miscellaneous'
  return type.charAt(0).toUpperCase() + type.slice(1) + 's'
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
.profile-builder {
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
  max-width: 100%;
}

.builder-header {
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
}

.builder-header h1 {
  margin: 0 0 var(--spacing-md) 0;
}

.error-banner {
  margin: var(--spacing-sm) var(--spacing-lg) 0;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  background: #fee2e2;
  border: 1px solid #fecaca;
  color: #991b1b;
  font-size: var(--font-size-sm);
}

.profile-name-input {
  width: 100%;
  max-width: 600px;
  padding: 0.75rem;
  font-size: var(--font-size-base);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-sm);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.profile-name-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(232, 93, 41, 0.14);
}

.builder-content {
  flex: 1;
  display: grid;
  grid-template-columns: 400px 1fr;
  overflow: hidden;
}

.blocks-sidebar {
  border-right: 1px solid var(--color-border);
  overflow-y: auto;
  padding: var(--spacing-lg);
  background: var(--color-background);
}

.block-type-section {
  margin-bottom: var(--spacing-xl);
}

.block-type-section h3 {
  color: var(--color-primary);
  margin: 0 0 var(--spacing-md) 0;
  font-size: var(--font-size-lg);
}

.block-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.block-item {
  padding: var(--spacing-md);
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s;
}

.block-item:hover {
  border-color: var(--color-primary);
  transform: translateX(4px);
}

.block-item.selected {
  border-color: var(--color-primary);
  background: rgba(var(--color-primary-rgb, 59, 130, 246), 0.1);
}

.block-item-content {
  flex: 1;
}

.block-item h4 {
  margin: 0 0 var(--spacing-xs) 0;
  font-size: var(--font-size-base);
}

.block-meta {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
}

.selected-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
}

.profile-preview {
  overflow-y: auto;
  padding: var(--spacing-lg);
}

.profile-preview h2 {
  margin: 0 0 var(--spacing-lg) 0;
}

.general-section {
  margin-bottom: var(--spacing-2xl);
}

.general-info-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
}

.general-info-card.editable {
  background: var(--color-background);
  padding: var(--spacing-lg);
}

.field-group {
  width: 100%;
  margin-bottom: var(--spacing-md);
}

.checkbox-field {
  margin-bottom: var(--spacing-sm);
}

.checkbox-label {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-sm);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
}

.checkbox-label input[type='checkbox'] {
  width: auto;
}

.field-group-flex {
  flex: 1;
}

.field-label {
  display: block;
  font-weight: 600;
  color: var(--color-primary);
  margin-bottom: var(--spacing-xs);
  font-size: var(--font-size-sm);
}

.focus-area-group {
  margin-bottom: var(--spacing-lg);
}

.focus-area-section {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-sm);
  background: var(--color-surface);
}

.focus-area-legend {
  margin-bottom: var(--spacing-sm);
  padding: 0;
}

.focus-area-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.focus-area-row {
  display: flex;
  gap: var(--spacing-xs);
  align-items: center;
}

.focus-area-row .field-input {
  flex: 1;
  margin-bottom: 0;
}

.focus-area-remove-btn {
  align-self: stretch;
}

.add-focus-btn {
  width: 100%;
  margin-top: var(--spacing-sm);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--color-text-secondary);
}

.selected-blocks {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

.selected-blocks h3 {
  color: var(--color-primary);
  margin: 0 0 var(--spacing-md) 0;
}

.selected-block-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.selected-block-list.skill-block-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: var(--spacing-md);
  align-items: stretch;
}

.selected-block-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
  width: 100%;
  box-sizing: border-box;
}

.selected-block-card.editable {
  padding: var(--spacing-lg);
}

.selected-block-card.skill-card {
  border-left: 4px solid var(--color-primary);
}

.block-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.block-title-input {
  flex: 1;
  width: 100%;
  box-sizing: border-box;
  font-size: var(--font-size-lg);
  font-weight: 600;
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-background);
}

.block-title-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(232, 93, 41, 0.14);
}

.remove-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  width: 32px;
  height: 32px;
  padding: 0;
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: all 0.2s;
}

.remove-btn:hover {
  border-color: var(--color-error);
  color: var(--color-error);
  background: rgba(239, 68, 68, 0.1);
}

.block-fields {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  width: 100%;
}

.skill-fields {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-sm);
  background: var(--color-background);
}

.skill-helper-text {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: var(--font-size-xs);
}

.field-input,
.field-textarea {
  display: block;
  width: 100%;
  box-sizing: border-box;
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  background: var(--color-background);
}

.field-input:focus,
.field-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(232, 93, 41, 0.14);
}

.field-textarea {
  resize: vertical;
  font-family: inherit;
}

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-sm);
}

.field-input.small {
  width: 100%;
}

.builder-footer {
  padding: var(--spacing-lg);
  border-top: 1px solid var(--color-border);
  background: var(--color-surface);
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-md);
}

.builder-footer button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 1024px) {
  .builder-content {
    grid-template-columns: 1fr;
  }

  .blocks-sidebar {
    border-right: none;
    border-bottom: 1px solid var(--color-border);
    max-height: 40vh;
  }
}

@media (max-width: 720px) {
  .error-banner {
    margin-left: var(--spacing-md);
    margin-right: var(--spacing-md);
  }

  .builder-header,
  .profile-preview,
  .blocks-sidebar,
  .builder-footer {
    padding: var(--spacing-md);
  }

  .field-row {
    grid-template-columns: 1fr;
  }

  .selected-block-list.skill-block-list {
    grid-template-columns: 1fr;
  }

  .builder-footer {
    justify-content: stretch;
  }

  .builder-footer .btn {
    flex: 1;
  }
}
</style>
