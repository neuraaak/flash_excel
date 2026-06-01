export default {
  name: 'SortTable',
  props: { columns: { type: Array, default: () => [] }, payload: { type: Object, default: () => ({}) } },
  emits: ['update:payload'],
  inject: ['i18n'],
  computed: {
    t() { return this.i18n.t; },
  },
  data() { return { rows: [] }; },
  watch: {
    payload: { immediate: true, handler(v) {
      const by = v.by || [];
      const desc = v.descending;
      this.rows = by.map((col, i) => ({ col, desc: Array.isArray(desc) ? !!desc[i] : !!desc }));
    }},
  },
  methods: {
    emit() {
      const valid = this.rows.filter(r => r.col);
      this.$emit('update:payload', { action: 'sort_rows', by: valid.map(r => r.col), descending: valid.map(r => r.desc) });
    },
    setDir(i, desc) { this.rows[i].desc = desc; this.emit(); },
    addRow()        { this.rows.push({ col: this.columns[0] || '', desc: false }); this.emit(); },
    removeRow(i)    { this.rows.splice(i, 1); this.emit(); },
  },
  template: `
    <div>
      <div class="panel-sub">{{ t('table.sort_keys') }}</div>
      <div class="rule-list">
        <div v-for="(r, i) in rows" :key="i" class="rule-row" style="grid-template-columns:1fr auto var(--ctl-h);">
          <span class="select-wrap">
            <select v-model="r.col" @change="emit">
              <option v-if="r.col && !columns.includes(r.col)" :value="r.col">{{ r.col }}</option>
              <option v-for="c in columns" :key="c" :value="c">{{ c }}</option>
            </select>
          </span>
          <span class="seg">
            <button :class="{ active: !r.desc }" @click="setDir(i, false)">{{ t('table.asc') }}</button>
            <button :class="{ active: r.desc }"  @click="setDir(i, true)">{{ t('table.desc') }}</button>
          </span>
          <button class="rule-del" @click="removeRow(i)" title="Remove">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>
          </button>
        </div>
      </div>
      <button class="add-rule" @click="addRow">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>
        {{ t('table.add_rule') }}
      </button>
      <div class="panel-hint">Keys apply top to bottom — the first is the primary sort.</div>
    </div>
  `,
};
