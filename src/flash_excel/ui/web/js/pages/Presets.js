import { api }      from '../api.js';
import FileLoader   from '../components/FileLoader.js';
import ActionSteps  from '../components/ActionSteps.js';

export default {
  name: 'PresetsPage',
  components: { FileLoader, ActionSteps },
  inject: ['showToast'],
  data() {
    return {
      presets:      [],     // [{name, description, step_count, path}]
      selectedPath: null,
      isNew:        false,
      presetName:   '',
      fileInfo:     null,   // {file_name, size_bytes, file_type, columns}
      payloads:     {},     // action → payload dict
    };
  },
  computed: {
    hasSelection()   { return !!this.selectedPath || this.isNew; },
    sourceColumns()  { return this.fileInfo?.columns || []; },
  },
  async created() { await this.loadList(); },
  methods: {
    // ── List ──────────────────────────────────────────────────────
    async loadList() {
      try { this.presets = await api.getPresets(); }
      catch (e) { this.showToast(`Failed to load presets: ${e.message}`, 'error'); }
    },

    async selectPreset(path) {
      try {
        const data    = await api.loadPreset(path);
        this.selectedPath = path;
        this.isNew    = false;
        this.presetName = data.name;
        this.fileInfo = null;
        this.payloads = {};
        for (const step of data.steps) {
          const { action, ...rest } = step;
          this.payloads[action] = { action, ...rest };
        }
      } catch (e) { this.showToast(`Load failed: ${e.message}`, 'error'); }
    },

    async newPreset() {
      const name = `Preset ${this.presets.length + 1}`;
      try {
        await api.newPreset(name);
        this.isNew = true; this.selectedPath = null;
        this.presetName = name; this.fileInfo = null; this.payloads = {};
      } catch (e) { this.showToast(`Error: ${e.message}`, 'error'); }
    },

    async savePreset() {
      if (!this.presetName.trim()) { this.showToast('Preset name cannot be empty', 'error'); return; }
      try {
        const steps = Object.values(this.payloads).filter(p => p && Object.keys(p).length > 1);
        const res   = await api.savePreset(this.presetName, steps);
        this.selectedPath = res.path; this.isNew = false;
        await this.loadList();
        this.showToast('Preset saved');
      } catch (e) { this.showToast(`Save failed: ${e.message}`, 'error'); }
    },

    async deletePreset() {
      if (!this.selectedPath) return;
      if (!confirm(`Delete "${this.presetName}"?`)) return;
      try {
        await api.deletePreset(this.selectedPath);
        this.selectedPath = null; this.isNew = false;
        this.presetName = ''; this.fileInfo = null; this.payloads = {};
        await this.loadList();
        this.showToast('Preset deleted');
      } catch (e) { this.showToast(`Delete failed: ${e.message}`, 'error'); }
    },

    async exportPreset() {
      if (!this.selectedPath) return;
      try {
        const res = await api.exportPreset(this.selectedPath);
        if (!res?.cancelled) this.showToast('Preset exported');
      } catch (e) { this.showToast(`Export failed: ${e.message}`, 'error'); }
    },

    // ── File ──────────────────────────────────────────────────────
    async loadFile() {
      try {
        const res = await api.openFileDialog();
        if (res?.cancelled) return;
        this.fileInfo = res;
      } catch (e) { this.showToast(`File error: ${e.message}`, 'error'); }
    },

    async clearFile() {
      await api.clearFile();
      this.fileInfo = null;
    },

    // ── Payloads ──────────────────────────────────────────────────
    onPayloads(p) { this.payloads = p; },
  },

  template: `
    <div class="presets-page">

      <!-- Header -->
      <div class="presets-header">
        <span class="presets-header__title">Presets</span>

        <button class="btn btn-ghost btn-icon-only" @click="newPreset" title="New preset">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
        </button>

        <template v-if="hasSelection">
          <input class="input" style="flex:1;max-width:340px;" v-model="presetName" placeholder="Preset name" />

          <button class="btn btn-primary" @click="savePreset">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
              <polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/>
            </svg>
            Save
          </button>

          <div class="vdivider"></div>

          <button class="btn btn-danger" @click="deletePreset" :disabled="!selectedPath">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
            </svg>
            Delete
          </button>

          <button class="btn btn-ghost" @click="exportPreset" :disabled="!selectedPath">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
            Export
          </button>
        </template>
      </div>

      <!-- Body -->
      <div class="presets-body">

        <!-- Left panel -->
        <div class="presets-left">
          <div v-if="!presets.length" style="padding:var(--sp-3);font-size:var(--text-sm);color:var(--text-secondary);text-align:center;">
            No presets yet.<br/>Click + to create one.
          </div>
          <div v-for="p in presets" :key="p.path"
            class="preset-item" :class="{ active: selectedPath === p.path }"
            @click="selectPreset(p.path)">
            <span class="preset-item__name">{{ p.name }}</span>
            <span class="badge badge--neutral">{{ p.step_count }}</span>
          </div>
        </div>

        <!-- Right panel -->
        <div class="presets-right">
          <div v-if="!hasSelection" class="presets-right__placeholder">
            Select a preset or create a new one
          </div>

          <div v-else class="presets-form">
            <div style="font-size:var(--text-lg);font-weight:600;color:var(--text-primary);">Settings</div>

            <div class="hdivider"></div>

            <!-- Step 1 -->
            <div class="section-heading">
              <span class="step-badge">1</span>
              <span class="section-heading__title">Load the Excel template</span>
              <span class="section-heading__hint">
                <strong style="color:var(--text-primary);">.xlsx</strong>
                &nbsp;<strong style="color:var(--text-primary);">.xls</strong>
                &nbsp;<strong style="color:var(--text-primary);">.xlsm</strong>
                &nbsp;<strong style="color:var(--text-primary);">.csv</strong>
              </span>
            </div>

            <FileLoader :fileInfo="fileInfo" @load="loadFile" @clear="clearFile" />

            <div class="hdivider"></div>

            <!-- Step 2 -->
            <div class="section-heading">
              <span class="step-badge">2</span>
              <span class="section-heading__title">Action configuration</span>
              <span v-if="!sourceColumns.length" class="section-heading__hint">
                Load a file to enable column mapping
              </span>
            </div>

            <ActionSteps :columns="sourceColumns" :payloads="payloads" @update:payloads="onPayloads" />
          </div>
        </div>
      </div>
    </div>
  `,
};
