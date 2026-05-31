import TwoColumnTable from './TwoColumnTable.js';
export default {
  name: 'ReplaceTable',
  components: { TwoColumnTable },
  props: { columns: { type: Array, default: () => [] }, payload: { type: Object, default: () => ({}) } },
  emits: ['update:payload'],
  computed: { rules() { return this.payload.rules_by_column || {}; } },
  methods: {
    onUpdate(values) {
      const rules = Object.fromEntries(Object.entries(values).filter(([, v]) => v.trim()));
      this.$emit('update:payload', { action: 'replace_values', rules_by_column: rules });
    },
  },
  template: `<TwoColumnTable :columns="columns" :values="rules"
    left-header="SOURCE COLUMN" right-header="RULES (old=new, …)"
    placeholder="e.g. oui=yes, non=no" @update:values="onUpdate" />`,
};
