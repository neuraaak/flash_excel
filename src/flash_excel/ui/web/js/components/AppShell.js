import SettingsModal from './SettingsModal.js';
import LucideIcon    from './LucideIcon.js';

export default {
  name: 'AppShell',
  components: { SettingsModal, LucideIcon },
  props: { currentPage: { type: String, default: 'presets' } },
  emits: ['navigate'],

  data() {
    return { showSettings: false };
  },

  template: `
    <div class="app">

      <!-- Main (sidebar + page area) -->
      <div class="main">
        <nav class="sidebar">
          <div class="sidebar-logo">
            <div class="logo">F</div>
          </div>
          <div class="sidebar-nav">
            <button class="nav-btn" :class="{ active: currentPage === 'presets' }"
              title="Presets" @click="$emit('navigate', 'presets')">
              <LucideIcon name="presets" :size="20" />
            </button>
            <button class="nav-btn" :class="{ active: currentPage === 'processing' }"
              title="Processing" @click="$emit('navigate', 'processing')">
              <LucideIcon name="processing" :size="20" />
            </button>
          </div>
          <div class="sidebar-bottom">
            <button class="nav-btn" :class="{ active: showSettings }"
              title="Settings" @click="showSettings = true">
              <LucideIcon name="settings" :size="18" />
            </button>
          </div>
        </nav>

        <div class="page-area">
          <slot />
        </div>
      </div>

      <!-- Footer -->
      <footer class="footer">
        <div class="footer-left">Made with <span class="heart">&#10084;</span> by Flash-Excel</div>
        <div>v1.0.0</div>
      </footer>

      <!-- Settings popup -->
      <SettingsModal v-if="showSettings" @close="showSettings = false" />

    </div>
  `,
};
