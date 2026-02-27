<template>
  <div class="access-expired">
    <div class="message-card">
      <div class="icon" aria-hidden="true">
        <LineIcon name="clock" :size="56" />
      </div>
      <h1>Access Link Expired</h1>
      <p>The link you're trying to access has expired or is invalid.</p>
      <p class="help-text">Please contact your administrator for a new access link.</p>
    </div>
  </div>
</template>

<script setup>
import LineIcon from '@/components/LineIcon.vue'
</script>

<style scoped>
.access-expired {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-background);
}

.message-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--spacing-2xl);
  text-align: center;
  max-width: 500px;
  box-shadow: var(--shadow-lg);
}

.icon {
  margin-bottom: var(--spacing-lg);
  color: var(--color-primary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

h1 {
  color: var(--color-error);
  margin-bottom: var(--spacing-md);
}

p {
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-sm);
}

.help-text {
  font-weight: 600;
  color: var(--color-text-primary);
}
</style>
