export default {
  name: 'ReorderTable',
  props: { columns: { type: Array, default: () => [] }, payload: { type: Object, default: () => ({}) } },
  emits: ['update:payload'],
  inject: ['i18n'],
  computed: {
    t() { return this.i18n.t; },
  },
  data() { return { order: [] }; },
  watch: {
    columns: { immediate: true, handler(v) { if (!this.order.length && v.length) this.order = [...v]; } },
    payload: { immediate: true, handler(v) {
      const cols = v.columns?.length ? v.columns : this.columns;
      this.order = cols.length ? [...cols] : [...this.order];
    }},
  },
  methods: {
    move(i, dir) {
      const j = i + dir;
      if (j < 0 || j >= this.order.length) return;
      const next = [...this.order];
      [next[i], next[j]] = [next[j], next[i]];
      this.order = next;
      this.$emit('update:payload', { action: 'reorder_columns', columns: [...this.order] });
    },
  },
  template: `
    <div>
      <div class="panel-sub">{{ t('table.col_order') }}</div>
      <div class="order-list">
        <div v-for="(col, i) in order" :key="col" class="order-row">
          <span class="order-grip" title="Reorder">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><circle cx="9" cy="6" r="1.6"/><circle cx="15" cy="6" r="1.6"/><circle cx="9" cy="12" r="1.6"/><circle cx="15" cy="12" r="1.6"/><circle cx="9" cy="18" r="1.6"/><circle cx="15" cy="18" r="1.6"/></svg>
          </span>
          <span class="order-idx">{{ i + 1 }}</span>
          <span class="order-dot"></span>
          <span class="order-name">{{ col }}</span>
          <span class="order-arrows">
            <span class="arr" :class="{ disabled: i === 0 }" @click="move(i, -1)" title="Move up">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 15l-6-6-6 6"/></svg>
            </span>
            <span class="arr" :class="{ disabled: i === order.length - 1 }" @click="move(i, 1)" title="Move down">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>
            </span>
          </span>
        </div>
      </div>
    </div>
  `,
};
