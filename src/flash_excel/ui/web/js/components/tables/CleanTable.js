export default {
  name: 'CleanTable',
  props: { columns: { type: Array, default: () => [] }, payload: { type: Object, default: () => ({}) } },
  emits: ['update:payload'],
  inject: ['i18n'],
  computed: {
    t() { return this.i18n.t; },
    selected() { return this.payload.columns || []; },
    effectiveColumns() {
      return this.columns.length ? this.columns : this.selected;
    },
  },
  methods: {
    isOn(col) { return this.selected.includes(col); },
    toggle(col) {
      const set = new Set(this.selected);
      if (set.has(col)) set.delete(col); else set.add(col);
      const cols = this.effectiveColumns.filter(c => set.has(c));
      this.$emit('update:payload', { action: 'trim_whitespace', columns: cols });
    },
  },
  template: `
    <div>
      <div class="panel-sub">{{ t('table.cols_clean') }}</div>
      <div class="toggle-list">
        <div v-for="col in effectiveColumns" :key="col" class="toggle-row" :class="{ on: isOn(col) }">
          <span class="tr-name">{{ col }}</span>
          <label class="switch">
            <input type="checkbox" :checked="isOn(col)" @change="toggle(col)">
            <span class="track"></span>
          </label>
        </div>
      </div>
      <div class="panel-hint">Leading and trailing whitespace is removed from the selected columns.</div>
    </div>
  `,
};
