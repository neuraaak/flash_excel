export default {
  name: 'ComputedTable',
  props: { columns: { type: Array, default: () => [] }, payload: { type: Object, default: () => ({}) } },
  emits: ['update:payload'],
  data() { return { localTarget: '', localExpression: '' }; },
  watch: {
    payload: { immediate: true, handler(v) { this.localTarget = v.target || ''; this.localExpression = v.expression || ''; } },
  },
  methods: {
    emit() { this.$emit('update:payload', { action: 'add_computed_column', target: this.localTarget, expression: this.localExpression }); },
  },
  template: `
    <div style="padding:var(--sp-4);display:flex;flex-direction:column;gap:var(--sp-3);">
      <div>
        <label style="display:block;font-size:var(--text-xs);font-weight:600;text-transform:uppercase;letter-spacing:.05em;color:var(--text-secondary);margin-bottom:var(--sp-1);">New column name</label>
        <input class="input" style="width:100%;" v-model="localTarget" placeholder="e.g. full_name" @input="emit" />
      </div>
      <div>
        <label style="display:block;font-size:var(--text-xs);font-weight:600;text-transform:uppercase;letter-spacing:.05em;color:var(--text-secondary);margin-bottom:var(--sp-1);">Expression (Polars)</label>
        <input class="input" style="width:100%;font-family:var(--font-mono);" v-model="localExpression" placeholder='e.g. col("first") + " " + col("last")' @input="emit" />
      </div>
      <p style="font-size:var(--text-xs);color:var(--text-secondary);">Available: {{ columns.join(', ') }}</p>
    </div>
  `,
};
