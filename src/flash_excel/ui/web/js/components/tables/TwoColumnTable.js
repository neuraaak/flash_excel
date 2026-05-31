export default {
  name: 'TwoColumnTable',
  props: {
    columns:     { type: Array,  default: () => [] },
    values:      { type: Object, default: () => ({}) },
    leftHeader:  { type: String, default: 'SOURCE COLUMN' },
    rightHeader: { type: String, default: 'VALUE' },
    placeholder: { type: String, default: '' },
  },
  emits: ['update:values'],
  methods: {
    onInput(col, e) {
      this.$emit('update:values', { ...this.values, [col]: e.target.value });
    },
  },
  template: `
    <div class="action-table">
      <div class="action-table__grid two-col">
        <div class="table-header__cell">{{ leftHeader }}</div>
        <div class="table-header__cell">{{ rightHeader }}</div>
        <template v-for="col in columns" :key="col">
          <div class="table-cell source">
            <span class="cell-dot"></span>{{ col }}
          </div>
          <div class="table-cell">
            <input class="table-input" type="text"
              :placeholder="placeholder" :value="values[col] || ''"
              @input="onInput(col, $event)" />
          </div>
        </template>
      </div>
    </div>
  `,
};
