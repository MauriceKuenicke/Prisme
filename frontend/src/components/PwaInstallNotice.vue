<template>
  <aside v-if="shouldShowNotice" class="install-notice" role="status" aria-live="polite">
    <div class="install-notice-header">
      <p class="install-kicker">Install Prismé Locally</p>
      <button type="button" class="dismiss-button" @click="dismissNotice" aria-label="Dismiss install notice">
        ×
      </button>
    </div>

    <p class="install-message">{{ noticeMessage }}</p>
    <p class="install-path">Help path: <strong>Admin -> Help -> Install Prismé Locally</strong></p>

    <p v-if="route.path === '/admin/login'" class="install-note">
      Sign in first, then open the Help page path above for full install instructions.
    </p>

    <div class="install-actions">
      <button
        v-if="canPromptInstall"
        type="button"
        class="btn btn-primary"
        @click="promptInstall"
      >
        Install Now
      </button>

      <button type="button" class="btn btn-secondary" @click="openInstallHelp">
        Open Help Guide
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const DISMISS_STORAGE_KEY = 'prisme_pwa_install_notice_dismissed'

const route = useRoute()
const router = useRouter()

const deferredInstallPrompt = ref(null)
const isStandalone = ref(false)
const isDismissed = ref(readDismissState())

function readDismissState() {
  try {
    return localStorage.getItem(DISMISS_STORAGE_KEY) === '1'
  } catch {
    return false
  }
}

function writeDismissState(value) {
  try {
    if (value) {
      localStorage.setItem(DISMISS_STORAGE_KEY, '1')
      return
    }
    localStorage.removeItem(DISMISS_STORAGE_KEY)
  } catch {
    // Ignore storage issues in private/locked-down browsing contexts.
  }
}

function detectStandaloneMode() {
  const standaloneMedia = window.matchMedia('(display-mode: standalone)').matches
  const legacyStandalone = window.navigator.standalone === true
  return standaloneMedia || legacyStandalone
}

const isIOS = /iphone|ipad|ipod/i.test(window.navigator.userAgent)
const isSafari = /^((?!chrome|android).)*safari/i.test(window.navigator.userAgent)

const canPromptInstall = computed(() => !!deferredInstallPrompt.value)
const isHelpRoute = computed(() => route.path === '/admin/help')
const shouldShowNotice = computed(() => !isStandalone.value && !isDismissed.value && !isHelpRoute.value)

const noticeMessage = computed(() => {
  if (canPromptInstall.value) {
    return 'This browser supports direct PWA install. Use Install Now or open Help for manual steps.'
  }

  if (!import.meta.env.PROD) {
    return 'Install prompts usually appear in production builds. Use the Help guide for manual install steps.'
  }

  if (isIOS && isSafari) {
    return 'On iPhone/iPad, install through Safari: Share -> Add to Home Screen.'
  }

  return 'If no install button appears in your browser, use the Help guide for manual install steps.'
})

function handleBeforeInstallPrompt(event) {
  event.preventDefault()
  deferredInstallPrompt.value = event
}

function handleAppInstalled() {
  isStandalone.value = true
  deferredInstallPrompt.value = null
  writeDismissState(false)
}

function dismissNotice() {
  isDismissed.value = true
  writeDismissState(true)
}

async function promptInstall() {
  if (!deferredInstallPrompt.value) {
    return
  }

  const promptEvent = deferredInstallPrompt.value
  await promptEvent.prompt()
  await promptEvent.userChoice
  deferredInstallPrompt.value = null
}

function openInstallHelp() {
  router.push('/admin/help#install-locally')
}

onMounted(() => {
  isStandalone.value = detectStandaloneMode()
  window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
  window.addEventListener('appinstalled', handleAppInstalled)
})

onBeforeUnmount(() => {
  window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
  window.removeEventListener('appinstalled', handleAppInstalled)
})
</script>

<style scoped>
.install-notice {
  position: fixed;
  right: var(--spacing-lg);
  bottom: var(--spacing-lg);
  width: min(420px, calc(100vw - (var(--spacing-lg) * 2)));
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-left: 4px solid var(--color-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: var(--spacing-md);
  z-index: 1200;
}

.install-notice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}

.install-kicker {
  margin: 0;
  font-size: var(--font-size-sm);
  font-weight: 700;
  letter-spacing: 0.02em;
  color: var(--color-primary);
  text-transform: uppercase;
}

.dismiss-button {
  min-width: 28px;
  min-height: 28px;
  line-height: 1;
  border-radius: var(--radius-full);
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-secondary);
}

.dismiss-button:hover {
  color: var(--color-text-primary);
  border-color: var(--color-border-dark);
}

.install-message,
.install-path,
.install-note {
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.install-path {
  color: var(--color-text-primary);
}

.install-note {
  color: var(--color-text-tertiary);
}

.install-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}

.install-actions .btn {
  padding: 0.55rem 0.95rem;
  font-size: var(--font-size-sm);
}

@media (max-width: 640px) {
  .install-notice {
    right: var(--spacing-sm);
    left: var(--spacing-sm);
    bottom: var(--spacing-sm);
    width: auto;
  }
}
</style>
