export default {
  name: 'AppShell',
  props: { currentPage: { type: String, default: 'presets' } },
  emits: ['navigate'],
  template: `
    <div class="sidebar">
      <div class="sidebar__logo">F</div>

      <button class="nav-btn" :class="{ active: currentPage === 'presets' }"
        title="Presets" @click="$emit('navigate', 'presets')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
          <line x1="4" y1="6"  x2="20" y2="6"/>
          <line x1="4" y1="12" x2="20" y2="12"/>
          <line x1="4" y1="18" x2="20" y2="18"/>
          <circle cx="8"  cy="6"  r="2" fill="currentColor" stroke="none"/>
          <circle cx="16" cy="12" r="2" fill="currentColor" stroke="none"/>
          <circle cx="10" cy="18" r="2" fill="currentColor" stroke="none"/>
        </svg>
      </button>

      <button class="nav-btn" :class="{ active: currentPage === 'processing' }"
        title="Processing" @click="$emit('navigate', 'processing')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
          <circle cx="12" cy="12" r="9"/>
          <path d="M12 12 L17 7"/>
          <path d="M7.2 16.8 a7 7 0 0 1 0-9.6"/>
          <path d="M16.8 16.8 a7 7 0 0 0 0-9.6"/>
        </svg>
      </button>

      <div class="sidebar__spacer"></div>
    </div>

    <div class="main-content">
      <slot />
    </div>
  `,
};
