export default {
  name: 'RenameTable',
  props: { columns: { type: Array, default: () => [] }, payload: { type: Object, default: () => ({}) } },
  emits: ['update:payload'],
  data() { return { rows: [] }; },
  watch: {
    payload: { immediate: true, handler(v) {
      const mapping = v.mapping || {};
      const entries = Object.entries(mapping);
      this.rows = entries.length ? entries.map(([src, val]) => ({ src, val })) : [];
    }},
  },
  methods: {
    emit() {
      const mapping = {};
      for (const r of this.rows) { if (r.src && r.val.trim()) mapping[r.src] = r.val.trim(); }
      this.$emit('update:payload', { action: 'rename_columns', mapping });
    },
    addRow()     { this.rows.push({ src: this.columns[0] || '', val: '' }); this.emit(); },
    removeRow(i) { this.rows.splice(i, 1); this.emit(); },
  },
  template: `
    <div>
      <div class="panel-sub">Column mapping</div>
      <div class="rule-head" style="grid-template-columns:1fr 1fr var(--ctl-h);">
        <span>Source column</span><span>New name</span><span></span>
      </div>
      <div class="rule-list">
        <div v-for="(r, i) in rows" :key="i" class="rule-row" style="grid-template-columns:1fr 1fr var(--ctl-h);">
          <span class="select-wrap">
            <select v-model="r.src" @change="emit">
              <option v-if="r.src && !columns.includes(r.src)" :value="r.src">{{ r.src }}</option>
              <option v-for="c in columns" :key="c" :value="c">{{ c }}</option>
            </select>
          </span>
          <input class="input" v-model="r.val" placeholder="New name" @input="emit" />
          <button class="rule-del" @click="removeRow(i)" title="Remove">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>
          </button>
        </div>
      </div>
      <button class="add-rule" @click="addRow">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>
        Add mapping
      </button>
    </div>
  `,
};
