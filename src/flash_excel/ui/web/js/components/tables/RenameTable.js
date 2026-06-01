export default {
  name: 'RenameTable',
  props: { columns: { type: Array, default: () => [] }, payload: { type: Object, default: () => ({}) } },
  emits: ['update:payload'],
  inject: ['i18n'],
  data() { return { rows: [] }; },
  watch: {
    payload: { immediate: true, handler(v) {
      if (this._emitting) return;
      const mapping = v.mapping || {};
      const entries = Object.entries(mapping);
      this.rows = entries.length ? entries.map(([src, val]) => ({ src, val })) : [];
    }},
  },
  computed: {
    t() { return this.i18n.t; },
    // Colonnes déjà assignées à une règle existante
    usedSources() { return new Set(this.rows.map(r => r.src).filter(Boolean)); },
    // Doublons de target : targets qui apparaissent plus d'une fois
    duplicateTargets() {
      const seen = {}, dupes = new Set();
      for (const r of this.rows) {
        const v = r.val.trim();
        if (!v) continue;
        if (seen[v]) dupes.add(v);
        seen[v] = true;
      }
      return dupes;
    },
    // Colonnes disponibles pour une nouvelle règle
    availableForNew() { return this.columns.filter(c => !this.usedSources.has(c)); },
  },
  methods: {
    emit() {
      this._emitting = true;
      const mapping = {};
      for (const r of this.rows) { if (r.src && r.val.trim()) mapping[r.src] = r.val.trim(); }
      this.$emit('update:payload', { action: 'rename_columns', mapping });
      this.$nextTick(() => { this._emitting = false; });
    },
    // Colonnes disponibles pour une ligne existante (inclut sa propre source)
    availableForRow(row) {
      return this.columns.filter(c => c === row.src || !this.usedSources.has(c));
    },
    addRow() {
      const next = this.availableForNew[0] || this.columns[0] || '';
      this.rows.push({ src: next, val: '' });
      this.emit();
    },
    removeRow(i) { this.rows.splice(i, 1); this.emit(); },
  },
  template: `
    <div>
      <div class="panel-sub">{{ t('table.col_mapping') }}</div>
      <div class="rule-head" style="grid-template-columns:1fr 1fr var(--ctl-h);">
        <span>{{ t('table.source') }}</span><span>{{ t('table.new_name') }}</span><span></span>
      </div>
      <div class="rule-list">
        <div v-for="(r, i) in rows" :key="i" class="rule-row" style="grid-template-columns:1fr 1fr var(--ctl-h);">
          <span class="select-wrap">
            <select v-model="r.src" @change="emit">
              <option v-if="r.src && !columns.includes(r.src)" :value="r.src">{{ r.src }}</option>
              <option v-for="c in availableForRow(r)" :key="c" :value="c">{{ c }}</option>
            </select>
          </span>
          <span style="position:relative;display:flex;align-items:center;">
            <input class="input" v-model="r.val" :placeholder="t('table.new_name')" @input="emit"
              :style="duplicateTargets.has(r.val.trim()) ? 'border-color:var(--semantic_warning);padding-right:32px;' : ''" />
            <span v-if="duplicateTargets.has(r.val.trim())" title="Duplicate target name"
              style="position:absolute;right:9px;color:var(--semantic_warning);display:flex;pointer-events:none;">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            </span>
          </span>
          <button class="rule-del" @click="removeRow(i)" title="Remove">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>
          </button>
        </div>
      </div>
      <button class="add-rule" @click="addRow" :disabled="availableForNew.length === 0">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>
        {{ t('table.add_rule') }}
      </button>
    </div>
  `,
};
