import { api }      from '../api.js';
import LucideIcon   from './LucideIcon.js';

const THEME_TOKENS = [
  'surface_sunken', 'surface_base', 'surface_raised',
  'surface_overlay', 'surface_floating', 'border_subtle',
  'accent_brand', 'text_primary', 'text_secondary', 'text_on_accent',
  'overlay_scrim',
  'semantic_success', 'semantic_warning', 'semantic_error', 'semantic_info',
];

const PALETTE_PREVIEWS = {
  'blue-gray':   { surface: '#212530', accent: '#96CD32', text: '#dadce4' },
  'github-dark': { surface: '#161b22', accent: '#58a6ff', text: '#e6edf3' },
  'warm-dark':   { surface: '#211c16', accent: '#d97706', text: '#e8ddd0' },
};

export default {
  name: 'SettingsModal',
  components: { LucideIcon },
  emits: ['close'],

  data() {
    return {
      palette: 'blue-gray',
      mode: 'dark',
      themes: {},
      palettes: [
        { key: 'blue-gray',    label: 'Blue Gray' },
        { key: 'github-dark',  label: 'GitHub' },
        { key: 'warm-dark',    label: 'Warm Dark' },
      ],
    };
  },

  computed: {
    paletteCards() {
      return this.palettes.map(p => ({
        ...p,
        preview: PALETTE_PREVIEWS[p.key] || {},
      }));
    },
  },

  async mounted() {
    const [cfgRes, themesRes] = await Promise.all([
      api.getAppConfig().catch(() => null),
      api.getThemes().catch(() => null),
    ]);
    if (cfgRes?.appearance) {
      this.palette = cfgRes.appearance.palette;
      this.mode    = cfgRes.appearance.mode;
    }
    if (themesRes) this.themes = themesRes;
  },

  methods: {
    async setPalette(key) {
      this.palette = key;
      this._applyTheme();
      await api.saveAppConfig(this.palette, this.mode).catch(() => {});
    },
    async setMode(m) {
      this.mode = m;
      this._applyTheme();
      await api.saveAppConfig(this.palette, this.mode).catch(() => {});
    },
    _applyTheme() {
      const tokens = this.themes[this.palette]?.[this.mode];
      if (!tokens) return;
      const root = document.documentElement;
      for (const key of THEME_TOKENS) {
        if (tokens[key]) root.style.setProperty(`--${key}`, tokens[key]);
      }
    },
    closeOnOverlay(e) {
      if (e.target === e.currentTarget) this.$emit('close');
    },
  },

  template: `
    <div class="settings-overlay" @click="closeOnOverlay" @keydown.esc="$emit('close')">
      <div class="settings-modal" role="dialog" aria-modal="true" aria-label="Settings">

        <div class="settings-head">
          <span class="settings-head-title">
            <LucideIcon name="settings" :size="15" :stroke="1.8" />
            Settings
          </span>
          <button class="btn-icon" @click="$emit('close')" aria-label="Fermer">
            <LucideIcon name="x" :size="14" :stroke="2" />
          </button>
        </div>

        <div class="settings-body">
          <div class="settings-section">
            <div class="settings-section-label">Apparence</div>

            <div class="settings-field">
              <div class="settings-field-label">Palette de couleurs</div>
              <div class="palette-grid">
                <button
                  v-for="p in paletteCards"
                  :key="p.key"
                  class="palette-card"
                  :class="{ active: palette === p.key }"
                  @click="setPalette(p.key)"
                >
                  <div class="palette-card-swatches">
                    <span class="palette-card-swatch" :style="{ background: p.preview.surface }"></span>
                    <span class="palette-card-swatch" :style="{ background: p.preview.accent  }"></span>
                    <span class="palette-card-swatch" :style="{ background: p.preview.text    }"></span>
                  </div>
                  <div class="palette-card-name">{{ p.label }}</div>
                  <div v-if="palette === p.key" class="palette-card-check">
                    <LucideIcon name="check" :size="10" :stroke="2.5" />
                  </div>
                </button>
              </div>
            </div>

            <div class="settings-field">
              <div class="settings-field-label">Mode</div>
              <div class="seg settings-mode-seg">
                <button :class="{ active: mode === 'dark' }" @click="setMode('dark')">
                  <LucideIcon name="moon" :size="13" :stroke="1.8" />
                  Dark
                </button>
                <button :class="{ active: mode === 'light' }" @click="setMode('light')">
                  <LucideIcon name="sun" :size="13" :stroke="1.8" />
                  Light
                </button>
              </div>
            </div>

          </div>
        </div>

      </div>
    </div>
  `,
};
