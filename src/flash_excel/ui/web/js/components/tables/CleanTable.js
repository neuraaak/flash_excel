import OneColumnTable from './OneColumnTable.js';
export default {
  name: 'CleanTable',
  components: { OneColumnTable },
  props: { columns: { type: Array, default: () => [] }, payload: { type: Object, default: () => ({}) } },
  emits: ['update:payload'],
  computed: { selected() { return this.payload.columns || []; } },
  methods: {
    onUpdate(selected) { this.$emit('update:payload', { action: 'trim_whitespace', columns: selected }); },
  },
  template: `<OneColumnTable :columns="columns" :selected="selected"
    header="TRIM WHITESPACE ON" @update:selected="onUpdate" />`,
};
