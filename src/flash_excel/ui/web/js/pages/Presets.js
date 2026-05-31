import { api }      from '../api.js';
import FileLoader   from '../components/FileLoader.js';
import ActionSteps  from '../components/ActionSteps.js';

export default {
  name: 'PresetsPage',
  components: { FileLoader, ActionSteps },
  inject: ['showToast'],
  data() {
    return {
      presets:        [],
      selectedPath:   null,
      isNew:          false,
      presetName:     '',
      fileInfo:       null,
      presetColumns:  [],
      payloads:       {},
    };
  },
  computed: {
    hasSelection()  { return !!this.selectedPath || this.isNew; },
    sourceColumns() { return this.fileInfo?.columns || this.presetColumns; },
  },
  async created() { await this.loadList(); },
  methods: {
    async loadList() {
      try { this.presets = await api.getPresets(); }
      catch (e) { this.showToast(`Failed to load presets: ${e.message}`, 'error'); }
    },

    async selectPreset(path) {
      try {
        const data = await api.loadPreset(path);
        this.selectedPath = path;
        this.isNew = false;
        this.presetName = data.name;
        this.fileInfo = null;
        this.presetColumns = data.source_columns || [];
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
        this.presetName = name; this.fileInfo = null;
        this.presetColumns = []; this.payloads = {};
      } catch (e) { this.showToast(`Error: ${e.message}`, 'error'); }
    },

    async savePreset() {
      if (!this.presetName.trim()) { this.showToast('Preset name cannot be empty', 'error'); return; }
      try {
        const steps = Object.values(this.payloads).filter(p => p && Object.keys(p).length > 1);
        const res = await api.savePreset(this.presetName, steps);
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

    onPayloads(p) { this.payloads = p; },
  },

  template: `
    <div class="presets-page">

      <!-- Toolbar -->
      <div class="toolbar">
        <div class="tb-presets-cell">
          <span class="sec-label">Presets</span>
          <button class="icon-btn" @click="newPreset" title="New preset">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>
          </button>
        </div>
        <div class="tb-actions-cell">
          <template v-if="hasSelection">
            <input class="input name-input" v-model="presetName" placeholder="Preset name" aria-label="Preset name" />
            <button class="btn primary" @click="savePreset">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><path d="M17 21v-8H7v8M7 3v5h8"/></svg>
              Save
            </button>
            <span class="tb-spacer"></span>
            <button class="btn danger-hover" @click="deletePreset" :disabled="!selectedPath">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6M10 11v6M14 11v6"/></svg>
              Delete
            </button>
            <button class="btn" @click="exportPreset" :disabled="!selectedPath">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 16V4M8 8l4-4 4 4"/><path d="M4 16v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"/></svg>
              Export
            </button>
          </template>
        </div>
      </div>

      <!-- Body -->
      <div class="presets-body">

        <!-- Left: preset list -->
        <aside class="presets-col">
          <div v-if="!presets.length" class="presets-empty">
            No presets yet.<br/>Click + to create one.
          </div>
          <div v-for="p in presets" :key="p.path"
            class="preset-card" :class="{ active: selectedPath === p.path }"
            @click="selectPreset(p.path)">
            <span class="pc-name">{{ p.name }}</span>
            <span class="pc-meta">{{ p.step_count }}</span>
          </div>
        </aside>

        <!-- Right: settings -->
        <section class="settings-col">
          <div v-if="!hasSelection" class="settings-placeholder">
            Select a preset or create a new one
          </div>

          <template v-else>
            <h2 class="panel-title">Settings</h2>

            <!-- Step 1 -->
            <div class="step">
              <div class="step-head">
                <span class="step-badge">1</span>
                <span class="step-title">Load the Excel template</span>
                <span class="step-hint">Accepted formats <code>.xlsx .xls .xlsm .csv</code></span>
              </div>
              <FileLoader :fileInfo="fileInfo" @load="loadFile" @clear="clearFile" />
            </div>

            <div class="sep-line"></div>

            <!-- Step 2 -->
            <div class="step">
              <div class="step-head">
                <span class="step-badge">2</span>
                <span class="step-title">Action configuration</span>
                <span v-if="!sourceColumns.length" class="step-hint">Load a file to enable column mapping</span>
              </div>
              <ActionSteps :columns="sourceColumns" :payloads="payloads" @update:payloads="onPayloads" />
            </div>
          </template>
        </section>

      </div>
    </div>
  `,
};
