<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal" @click.stop>
      <div class="modal-header">
        <h2>Export Profile as PDF</h2>
        <button @click="$emit('close')" class="btn-close" aria-label="Close export modal">
          <LineIcon name="x" :size="18" />
        </button>
      </div>

      <p class="modal-description">
        Export "{{ profileName }}" as a clean, modern PDF profile.
      </p>

      <form @submit.prevent="handleExport" class="form">
        <div class="form-group">
          <label for="company-name">Company Name (optional)</label>
          <input
            id="company-name"
            v-model="formData.companyName"
            type="text"
          />
        </div>

        <div class="form-group">
          <label for="accent-color">Accent Color (optional)</label>
          <div class="color-input-wrapper">
            <input
              id="accent-color"
              v-model="formData.accentColor"
              type="color"
              class="color-picker"
            />
            <input
              v-model="formData.accentColor"
              type="text"
              pattern="^#[0-9A-Fa-f]{6}$"
              class="color-text"
            />
          </div>
          <p class="form-hint">Hex color for section headers and accents.</p>
        </div>

        <div class="modal-actions">
          <button type="button" @click="$emit('close')" class="btn btn-secondary" :disabled="exporting">
            Cancel
          </button>
          <button type="submit" class="btn btn-primary" :disabled="exporting">
            <span v-if="!exporting">Export PDF</span>
            <span v-else>Exporting...</span>
          </button>
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import LineIcon from '@/components/LineIcon.vue'
import { useProfilesStore } from '@/stores/profiles'

const props = defineProps({
  profileId: {
    type: Number,
    required: true
  },
  profileName: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['close', 'exported'])
const profilesStore = useProfilesStore()

const formData = ref({
  companyName: '',
  accentColor: '#0E4B8A'
})

const exporting = ref(false)
const error = ref(null)

// Load saved company name from localStorage
onMounted(() => {
  const savedCompanyName = localStorage.getItem('export_company_name')
  if (savedCompanyName) {
    formData.value.companyName = savedCompanyName
  }
})

async function handleExport() {
  exporting.value = true
  error.value = null

  try {
    // Save company name to localStorage for next time
    if (formData.value.companyName) {
      localStorage.setItem('export_company_name', formData.value.companyName)
    }

    await profilesStore.exportProfilePdf(props.profileId, {
      companyName: formData.value.companyName || null,
      accentColor: formData.value.accentColor
    })

    emit('exported')
    emit('close')
  } catch (err) {
    console.error('Export error:', err)
    error.value = err.response?.data?.detail || err.message || 'Export failed. Please try again or contact support.'
  } finally {
    exporting.value = false
  }
}
</script>

<style scoped>
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

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.modal-header h2 {
  margin: 0;
  font-size: var(--font-size-xl);
}

.btn-close {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 6px;
  color: var(--color-text-secondary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
}

.btn-close:hover {
  color: var(--color-text-primary);
  background: var(--color-background);
}

.modal-description {
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-lg);
  line-height: 1.5;
}

.form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.form-group label {
  font-weight: 500;
  color: var(--color-text-primary);
}

.form-group input[type="text"] {
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
}

.form-group input[type="text"]:focus {
  outline: none;
  border-color: var(--color-primary);
}

.color-input-wrapper {
  display: flex;
  gap: var(--spacing-sm);
  align-items: center;
}

.color-picker {
  width: 60px;
  height: 40px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
}

.color-text {
  flex: 1;
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  font-family: monospace;
}

.color-text:focus {
  outline: none;
  border-color: var(--color-primary);
}

.form-hint {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
}

.modal-actions {
  display: flex;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-md);
}

.modal-actions button {
  flex: 1;
  padding: var(--spacing-sm) var(--spacing-md);
}

.error-message {
  background: var(--color-error-bg, #fee);
  color: var(--color-error);
  padding: var(--spacing-sm);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  margin-top: var(--spacing-sm);
}

.btn {
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
  border: none;
}

.btn-primary:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-secondary {
  background: transparent;
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover:not(:disabled) {
  border-color: var(--color-primary);
}
</style>
