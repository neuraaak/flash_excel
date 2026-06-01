const CAST_TYPES = ['string', 'int', 'float', 'bool', 'date', 'datetime'];

export default {
  name: 'CastTable',
  props: { columns: { type: Array, default: () => [] }, payload: { type: Object, default: () => ({}) } },
  emits: ['update:payload'],
  inject: ['i18n'],
  data() { return { rows: [], castTypes: CAST_TYPES }; },
  computed: {
    t() { return this.i18n.t; },
    usedCols() { return new Set(this.rows.map(r => r.col).filter(Boolean)); },
    availableForNew() { return this.columns.filter(c => !this.usedCols.has(c)); },
  },
  watch: {
    payload: { immediate: true, handler(v) {
      if (this._emitting) return;
      const casts = v.casts || {};
      const entries = Object.entries(casts);
      this.rows = entries.length ? entries.map(([col, type]) => ({ col, type })) : [];
    }},
  },
  methods: {
    emit() {
      this._emitting = true;
      const casts = {};
      for (const r of this.rows) { if (r.col) casts[r.col] = r.type; }
      this.$emit('update:payload', { action: 'cast_types', casts });
      this.$nextTick(() => { this._emitting = false; });
    },
    availableForRow(row) { return this.columns.filter(c => c === row.col || !this.usedCols.has(c)); },
    addRow() {
      const next = this.availableForNew[0] || this.columns[0] || '';
      this.rows.push({ col: next, type: CAST_TYPES[0] });
      this.emit();
    },
    removeRow(i) { this.rows.splice(i, 1); this.emit(); },
  },
  template: `
    <div>
      <div class="panel-sub">{{ t('table.type_casts') }}</div>
      <div class="rule-head" style="grid-template-columns:1fr 1fr var(--ctl-h);">
        <span>{{ t('table.column') }}</span><span>{{ t('table.type') }}</span><span></span>
      </div>
      <div class="rule-list">
        <div v-for="(r, i) in rows" :key="i" class="rule-row" style="grid-template-columns:1fr 1fr var(--ctl-h);">
          <span class="select-wrap">
            <select v-model="r.col" @change="emit">
              <option v-if="r.col && !columns.includes(r.col)" :value="r.col">{{ r.col }}</option>
              <option v-for="c in availableForRow(r)" :key="c" :value="c">{{ c }}</option>
            </select>
          </span>
          <span class="select-wrap">
            <select v-model="r.type" @change="emit">
              <option v-for="ct in castTypes" :key="ct" :value="ct">{{ ct }}</option>
            </select>
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
