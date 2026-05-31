import TwoColumnTable from './TwoColumnTable.js';
export default {
  name: 'RenameTable',
  components: { TwoColumnTable },
  props: { columns: { type: Array, default: () => [] }, payload: { type: Object, default: () => ({}) } },
  emits: ['update:payload'],
  computed: { mapping() { return this.payload.mapping || {}; } },
  methods: {
    onUpdate(values) {
      const mapping = Object.fromEntries(Object.entries(values).filter(([, v]) => v.trim()));
      this.$emit('update:payload', { action: 'rename_columns', mapping });
    },
  },
  template: `<TwoColumnTable :columns="columns" :values="mapping"
    left-header="SOURCE COLUMN" right-header="NEW COLUMN NAME"
    placeholder="Leave empty to keep original" @update:values="onUpdate" />`,
};
