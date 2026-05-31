const SEL = 'background:transparent;border:none;color:var(--text-primary);font-size:var(--text-sm);width:100%;cursor:pointer;outline:none;';
export default {
  name: 'SortTable',
  props: { columns: { type: Array, default: () => [] }, payload: { type: Object, default: () => ({}) } },
  emits: ['update:payload'],
  data() { return { rows: [] }; },
  watch: {
    payload: { immediate: true, handler(v) {
      const by = v.by || [];
      const desc = v.descending;
      this.rows = by.length ? by.map((col, i) => ({ col, desc: Array.isArray(desc) ? (desc[i] || false) : (desc || false) })) : [{ col: '', desc: false }];
    }},
  },
  methods: {
    emit() {
      const valid = this.rows.filter(r => r.col);
      this.$emit('update:payload', { action: 'sort_rows', by: valid.map(r => r.col), descending: valid.map(r => r.desc) });
    },
    addRow()     { this.rows.push({ col: '', desc: false }); },
    removeRow(i) { this.rows.splice(i, 1); this.emit(); },
  },
  template: `
    <div style="padding:var(--sp-3);display:flex;flex-direction:column;gap:var(--sp-2);">
      <div v-for="(r, i) in rows" :key="i" style="display:grid;grid-template-columns:1fr auto auto;gap:var(--sp-2);align-items:center;">
        <select :style="'${SEL}'" v-model="r.col" @change="emit">
          <option value="" style="background:var(--surface-raised)">Column…</option>
          <option v-for="c in columns" :key="c" :value="c" style="background:var(--surface-raised)">{{ c }}</option>
        </select>
        <select :style="'${SEL}'" style="width:auto;" v-model="r.desc" @change="emit">
          <option :value="false" style="background:var(--surface-raised)">↑ Ascending</option>
          <option :value="true"  style="background:var(--surface-raised)">↓ Descending</option>
        </select>
        <button class="btn btn-ghost btn-icon-only" style="height:26px;width:26px;" @click="removeRow(i)">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <button class="btn btn-ghost" style="align-self:flex-start;height:26px;" @click="addRow">+ Add sort key</button>
    </div>
  `,
};
