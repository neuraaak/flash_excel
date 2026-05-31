import OneColumnTable from './OneColumnTable.js';
const SEL = 'background:transparent;border:none;color:var(--text-primary);font-size:var(--text-sm);cursor:pointer;outline:none;';
export default {
  name: 'DeduplicateTable',
  components: { OneColumnTable },
  props: { columns: { type: Array, default: () => [] }, payload: { type: Object, default: () => ({}) } },
  emits: ['update:payload'],
  data() { return { keep: 'first' }; },
  watch: { payload: { immediate: true, handler(v) { this.keep = v.keep || 'first'; } } },
  computed: { subset() { return this.payload.subset || []; } },
  methods: {
    onSubset(s) { this.$emit('update:payload', { action: 'deduplicate_rows', subset: s, keep: this.keep }); },
    onKeep()    { this.$emit('update:payload', { action: 'deduplicate_rows', subset: this.subset, keep: this.keep }); },
  },
  template: `
    <div style="display:flex;flex-direction:column;height:100%;">
      <div style="padding:var(--sp-3);display:flex;align-items:center;gap:var(--sp-2);border-bottom:1px solid var(--border-subtle);flex-shrink:0;">
        <span style="font-size:var(--text-sm);color:var(--text-secondary);">Keep</span>
        <select :style="'${SEL}'" v-model="keep" @change="onKeep">
          <option value="first" style="background:var(--surface-raised)">first occurrence</option>
          <option value="last"  style="background:var(--surface-raised)">last occurrence</option>
          <option value="none"  style="background:var(--surface-raised)">none (remove all)</option>
        </select>
      </div>
      <OneColumnTable :columns="columns" :selected="subset"
        header="DEDUPLICATE ON (empty = all)" @update:selected="onSubset" />
    </div>
  `,
};
