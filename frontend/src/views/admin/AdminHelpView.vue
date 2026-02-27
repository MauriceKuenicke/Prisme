<template>
  <div class="admin-help-view">
    <header class="help-hero">
      <div class="help-hero-content">
        <p class="eyebrow">Admin Guide</p>
        <h1>How To Use Prismé</h1>
        <p class="hero-description">
          Use this page as your operational playbook for profile work, installation, and admin access management.
        </p>
      </div>
      <div class="hero-badge">
        <span class="badge-label">Workflow Paths</span>
        <strong>4 Core Paths</strong>
      </div>
    </header>

    <section id="admin-access" class="help-section">
      <h2>Admin Access & Account Provisioning</h2>
      <p class="section-description">
        Admin access is only for internal users who actively create, edit, and export consultant profiles.
        Consultants should never receive admin credentials and should always work through temporary edit links.
        Only super admins can create new admin accounts.
      </p>

      <div class="access-grid">
        <article class="access-card">
          <h3>Who Should Have Admin Access</h3>
          <ul class="access-list">
            <li>Profile managers and sales operations who assemble customer-facing profiles.</li>
            <li>Delivery leads who review and tailor consultant profile content for opportunities.</li>
            <li>Only trusted platform owners should be granted Super Admin privileges.</li>
            <li>System owners who manage consultant records and generated access links.</li>
            <li>Consultants do not need admin accounts and should only use edit links (`/edit/:token`).</li>
          </ul>
        </article>

        <article class="access-card">
          <h3>Tutorial: Create A New Admin Account</h3>
          <ol class="tutorial-steps">
            <li><strong>Open Profile page:</strong> Go to <em>Admin -> Profile</em>.</li>
            <li><strong>Review access rule:</strong> Confirm this person actively manages profiles (not a consultant).</li>
            <li><strong>Create account:</strong> In <em>Create Admin Account</em>, enter username, email, and temporary password.</li>
            <li><strong>Optional privilege:</strong> Enable <em>Grant Super Admin privileges</em> only when truly required (can be changed later in the admin accounts table).</li>
            <li><strong>Share credentials securely:</strong> Provide credentials via approved internal channel only.</li>
            <li><strong>Verify access list:</strong> Check <em>Current Admin Accounts</em> to confirm account creation.</li>
          </ol>
        </article>
      </div>
    </section>

    <section id="install-locally" class="help-section install-section">
      <h2>Install Prismé Locally (PWA)</h2>
      <p class="section-description">
        Install Prismé to your device for quicker access and an app-like full screen experience.
      </p>

      <div class="install-grid">
        <article class="install-card">
          <h3>Desktop (Chrome or Edge)</h3>
          <ol class="install-steps">
            <li>Open Prismé in Chrome or Edge and sign in.</li>
            <li>Look for the install icon in the browser address bar.</li>
            <li>Click the icon and confirm Install.</li>
            <li>Launch Prismé from your desktop or app launcher.</li>
          </ol>
        </article>

        <article class="install-card">
          <h3>Android (Chrome)</h3>
          <ol class="install-steps">
            <li>Open Prismé in Chrome on Android.</li>
            <li>Tap the browser menu (three dots).</li>
            <li>Tap Install app or Add to Home screen.</li>
            <li>Confirm and launch from your home screen.</li>
          </ol>
        </article>

        <article class="install-card">
          <h3>iPhone / iPad (Safari)</h3>
          <ol class="install-steps">
            <li>Open Prismé in Safari.</li>
            <li>Tap Share, then choose Add to Home Screen.</li>
            <li>Tap Add to complete installation.</li>
            <li>Launch Prismé from your home screen icon.</li>
          </ol>
        </article>
      </div>

      <p class="install-footnote">
        If you do not see an install option, refresh the app once and use a supported browser over HTTPS.
      </p>
    </section>

    <section class="help-section">
      <h2>Step-by-Step Process Paths</h2>
      <p class="section-description">
        Each path below is an end-to-end process for a specific admin objective.
      </p>

      <div class="path-grid">
        <article v-for="path in processPaths" :key="path.key" class="path-card">
          <div class="path-header">
            <span class="path-tag">{{ path.tag }}</span>
            <h3>{{ path.title }}</h3>
            <p class="path-summary">{{ path.summary }}</p>
          </div>

          <ol class="path-steps">
            <li v-for="(step, index) in path.steps" :key="step.title" class="path-step">
              <div class="step-index">{{ index + 1 }}</div>
              <div class="step-content">
                <p class="step-title">{{ step.title }}</p>
                <p class="step-description">{{ step.description }}</p>
                <p class="step-where"><strong>Where:</strong> {{ step.location }}</p>
              </div>
            </li>
          </ol>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
const processPaths = [
  {
    key: 'create_consultant',
    tag: 'Path 1',
    title: 'Create a New Consultant',
    summary: 'Use this when onboarding a consultant who is not in the system yet.',
    steps: [
      {
        title: 'Open Consultants Overview',
        description: 'Go to the consultants page to manage consultant records.',
        location: 'Admin -> Consultants'
      },
      {
        title: 'Start Consultant Creation',
        description: 'Click "Add Consultant" to open the creation modal.',
        location: 'Consultants header'
      },
      {
        title: 'Fill Required Fields',
        description: 'Enter first name, last name, email, and title; add optional profile context if available.',
        location: 'Add New Consultant modal'
      },
      {
        title: 'Create and Verify',
        description: 'Save and confirm the consultant appears in the consultant card list.',
        location: 'Consultants grid'
      }
    ]
  },
  {
    key: 'build_profile',
    tag: 'Path 2',
    title: 'Create a Consultant Profile',
    summary: 'Use this when assembling a new profile version from consultant content blocks.',
    steps: [
      {
        title: 'Open Profile Builder',
        description: 'Find the consultant and click "Build Profile".',
        location: 'Consultants -> Build Profile'
      },
      {
        title: 'Enter Profile Name',
        description: 'Provide a clear profile name for this version.',
        location: 'Profile Builder header'
      },
      {
        title: 'Select and Refine Blocks',
        description: 'Choose relevant projects/skills/certifications and adjust text where needed.',
        location: 'Profile Builder sidebar + main editor'
      },
      {
        title: 'Save Profile Version',
        description: 'Save the profile so it appears in profile history for later edits, duplication, or export.',
        location: 'Profile Builder footer'
      }
    ]
  },
  {
    key: 'share_link',
    tag: 'Path 3',
    title: 'Share Update Link With Consultant',
    summary: 'Use this when the consultant should update their own profile content.',
    steps: [
      {
        title: 'Generate Link',
        description: 'Click "Generate Link" on the consultant card.',
        location: 'Consultants -> Generate Link'
      },
      {
        title: 'Copy and Send Link',
        description: 'Copy the generated link and share it with the consultant.',
        location: 'Consultant Edit Link modal'
      },
      {
        title: 'Consultant Updates Content',
        description: 'Consultant uses the link to edit blocks and general info.',
        location: 'Consultant edit page (/edit/:token)'
      },
      {
        title: 'Review Changes as Admin',
        description: 'Return to Build Profile or Profile History to validate updates.',
        location: 'Consultants -> Build Profile / View Profiles'
      }
    ]
  },
  {
    key: 'duplicate_and_export',
    tag: 'Path 4',
    title: 'Duplicate for Customer/Project and Export PDF',
    summary: 'Use this when adapting an existing profile for a specific customer or opportunity.',
    steps: [
      {
        title: 'Open Profile History',
        description: 'Navigate to profile history for the consultant.',
        location: 'Consultants -> View Profiles'
      },
      {
        title: 'Duplicate Existing Profile',
        description: 'Duplicate the closest matching profile version.',
        location: 'Profile History -> Duplicate icon'
      },
      {
        title: 'Rename and Tailor Content',
        description: 'Give it a customer/project-specific name, then edit selected blocks and wording.',
        location: 'Duplicate modal + Edit Profile flow'
      },
      {
        title: 'Export PDF',
        description: 'Use the export action to generate and share the final PDF profile.',
        location: 'Profile History -> Export icon'
      }
    ]
  }
]
</script>

<style scoped>
.admin-help-view {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

.help-hero {
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  background:
    radial-gradient(circle at 10% 10%, #fff3ec 0%, transparent 38%),
    radial-gradient(circle at 90% 0%, #ffe5db 0%, transparent 30%),
    var(--color-surface);
  border: 1px solid #f3ddd4;
  box-shadow: var(--shadow-sm);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacing-lg);
}

.help-hero-content h1 {
  margin: 0 0 var(--spacing-sm) 0;
}

.eyebrow {
  margin: 0 0 var(--spacing-xs) 0;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-size: var(--font-size-xs);
  color: var(--color-primary);
  font-weight: 700;
}

.hero-description {
  margin: 0;
  color: var(--color-text-secondary);
  max-width: 760px;
}

.hero-badge {
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  min-width: 160px;
  text-align: center;
}

.badge-label {
  display: block;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  margin-bottom: 4px;
}

.help-section {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
}

.help-section h2 {
  margin-top: 0;
  margin-bottom: var(--spacing-lg);
}

.section-description {
  margin-top: -4px;
  color: var(--color-text-secondary);
}

.access-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--spacing-md);
}

.access-card {
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
}

.access-card h3 {
  margin: 0 0 var(--spacing-sm) 0;
  font-size: var(--font-size-lg);
}

.access-list {
  margin: 0;
  padding-left: var(--spacing-lg);
  color: var(--color-text-secondary);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.tutorial-steps {
  margin: 0;
  padding-left: var(--spacing-lg);
  color: var(--color-text-secondary);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.tutorial-steps strong {
  color: var(--color-text-primary);
}

.install-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--spacing-md);
}

.install-card {
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
}

.install-card h3 {
  margin: 0 0 var(--spacing-sm) 0;
  font-size: var(--font-size-base);
}

.install-steps {
  margin: 0;
  padding-left: var(--spacing-lg);
  color: var(--color-text-secondary);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  font-size: var(--font-size-sm);
}

.install-footnote {
  margin: var(--spacing-md) 0 0 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.path-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--spacing-md);
}

.path-card {
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
}

.path-header {
  margin-bottom: var(--spacing-md);
}

.path-tag {
  display: inline-block;
  margin-bottom: var(--spacing-xs);
  padding: 4px 10px;
  border-radius: var(--radius-full);
  background: #fff1eb;
  color: var(--color-primary);
  font-size: var(--font-size-xs);
  font-weight: 700;
  letter-spacing: 0.02em;
}

.path-header h3 {
  margin: 0;
  font-size: var(--font-size-lg);
}

.path-summary {
  margin: var(--spacing-sm) 0 0 0;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.path-steps {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.path-step {
  display: flex;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
}

.step-index {
  width: 26px;
  height: 26px;
  border-radius: 999px;
  background: var(--color-primary-light);
  color: var(--color-primary);
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: var(--font-size-xs);
}

.step-content {
  min-width: 0;
}

.step-title {
  margin: 0 0 4px 0;
  color: var(--color-text-primary);
  font-weight: 600;
  font-size: var(--font-size-sm);
}

.step-description {
  margin: 0 0 4px 0;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.step-where {
  margin: 0;
  color: var(--color-text-primary);
  font-size: var(--font-size-xs);
}

@media (max-width: 900px) {
  .help-hero {
    flex-direction: column;
    align-items: stretch;
  }

  .access-grid,
  .install-grid,
  .path-grid {
    grid-template-columns: 1fr;
  }
}
</style>
