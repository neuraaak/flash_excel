import OneColumnTable from './OneColumnTable.js';
export default {
  name: 'SelectTable',
  components: { OneColumnTable },
  props: { columns: { type: Array, default: () => [] }, payload: { type: Object, default: () => ({}) } },
  emits: ['update:payload'],
  computed: {
    selected() {
      const s = this.payload.columns;
      return Array.isArray(s) && s.length ? s : [...this.columns];
    },
  },
  methods: {
    onUpdate(selected) { this.$emit('update:payload', { action: 'select_columns', columns: selected }); },
  },
  template: `<OneColumnTable :columns="columns" :selected="selected"
    header="SELECT COLUMNS TO KEEP" @update:selected="onUpdate" />`,
};
