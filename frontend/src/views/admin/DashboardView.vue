<template>
  <div class="dashboard">
    <h1>Dashboard</h1>
    <div class="dashboard-stats">
      <div class="stat-card">
        <h3>Total Consultants</h3>
        <p class="stat-value">{{ consultantCount }}</p>
      </div>
      <div class="stat-card">
        <h3>Total Profiles</h3>
        <p class="stat-value">{{ profileCount }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useConsultantsStore } from '@/stores/consultants'
import { useProfilesStore } from '@/stores/profiles'

const consultantsStore = useConsultantsStore()
const profilesStore = useProfilesStore()
const { consultants } = storeToRefs(consultantsStore)
const { profiles } = storeToRefs(profilesStore)

const consultantCount = computed(() => consultants.value.length)
const profileCount = computed(() => profiles.value.length)

onMounted(async () => {
  await Promise.all([
    consultantsStore.fetchConsultants(),
    profilesStore.fetchProfiles()
  ])
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
}

.dashboard-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-lg);
  margin-top: var(--spacing-xl);
}

.stat-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
  border-left: 4px solid var(--color-primary);
}

.stat-card h3 {
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
  margin-bottom: var(--spacing-md);
}

.stat-value {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--color-primary);
  margin: 0;
}
</style>
