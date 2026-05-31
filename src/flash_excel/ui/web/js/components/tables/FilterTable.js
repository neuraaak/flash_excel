const OPS = [
  { value: 'eq', label: '= equals' }, { value: 'neq', label: '≠ not equals' },
  { value: 'gt', label: '> greater' }, { value: 'gte', label: '≥ ≥ equal' },
  { value: 'lt', label: '< less' },   { value: 'lte', label: '≤ ≤ equal' },
  { value: 'contains', label: '∋ contains' }, { value: 'startswith', label: '↳ starts with' }, { value: 'endswith', label: '↲ ends with' },
];
const SEL = 'background:transparent;border:none;color:var(--text-primary);font-size:var(--text-sm);width:100%;cursor:pointer;outline:none;';
export default {
  name: 'FilterTable',
  props: { columns: { type: Array, default: () => [] }, payload: { type: Object, default: () => ({}) } },
  emits: ['update:payload'],
  data() { return { combine: 'AND', conditions: [{ column: '', operator: 'eq', value: '' }], ops: OPS }; },
  watch: {
    payload: { immediate: true, handler(v) {
      this.combine = v.combine || 'AND';
      this.conditions = (v.conditions?.length) ? JSON.parse(JSON.stringify(v.conditions)) : [{ column: '', operator: 'eq', value: '' }];
    }},
  },
  methods: {
    emit() { this.$emit('update:payload', { action: 'filter_rows', combine: this.combine, conditions: this.conditions.filter(c => c.column && c.value) }); },
    addRow()     { this.conditions.push({ column: '', operator: 'eq', value: '' }); },
    removeRow(i) { this.conditions.splice(i, 1); this.emit(); },
  },
  template: `
    <div style="padding:var(--sp-3);display:flex;flex-direction:column;gap:var(--sp-3);">
      <div style="display:flex;align-items:center;gap:var(--sp-2);">
        <span style="font-size:var(--text-sm);color:var(--text-secondary);">Combine with</span>
        <select :style="'${SEL}'" style="width:auto;" v-model="combine" @change="emit">
          <option style="background:var(--surface-raised)">AND</option>
          <option style="background:var(--surface-raised)">OR</option>
        </select>
      </div>
      <div v-for="(c, i) in conditions" :key="i" style="display:grid;grid-template-columns:1fr 1fr 1fr auto;gap:var(--sp-2);align-items:center;">
        <select :style="'${SEL}'" v-model="c.column" @change="emit">
          <option value="" style="background:var(--surface-raised)">Column…</option>
          <option v-for="col in columns" :key="col" :value="col" style="background:var(--surface-raised)">{{ col }}</option>
        </select>
        <select :style="'${SEL}'" v-model="c.operator" @change="emit">
          <option v-for="op in ops" :key="op.value" :value="op.value" style="background:var(--surface-raised)">{{ op.label }}</option>
        </select>
        <input class="input" style="height:26px;" v-model="c.value" placeholder="value" @input="emit" />
        <button class="btn btn-ghost btn-icon-only" style="height:26px;width:26px;" @click="removeRow(i)">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <button class="btn btn-ghost" style="align-self:flex-start;height:26px;" @click="addRow">+ Add condition</button>
    </div>
  `,
};
