const BTN = 'background:transparent;border:none;color:var(--text-secondary);cursor:pointer;padding:2px 5px;border-radius:3px;font-size:15px;line-height:1;';
export default {
  name: 'ReorderTable',
  props: { columns: { type: Array, default: () => [] }, payload: { type: Object, default: () => ({}) } },
  emits: ['update:payload'],
  data() { return { order: [] }; },
  watch: {
    columns:  { immediate: true, handler() { if (!this.order.length) this.order = [...this.columns]; } },
    payload:  { immediate: true, handler(v) { this.order = (v.columns?.length) ? [...v.columns] : [...this.columns]; } },
  },
  methods: {
    move(i, dir) {
      const j = i + dir;
      if (j < 0 || j >= this.order.length) return;
      [this.order[i], this.order[j]] = [this.order[j], this.order[i]];
      this.$emit('update:payload', { action: 'reorder_columns', columns: [...this.order] });
    },
  },
  template: `
    <div class="action-table">
      <div class="action-table__grid one-col">
        <div class="table-header__cell">COLUMN ORDER</div>
        <div v-for="(col, i) in order" :key="col" class="table-cell source" style="justify-content:space-between;">
          <span style="display:flex;align-items:center;gap:var(--sp-2);"><span class="cell-dot"></span>{{ col }}</span>
          <span style="display:flex;gap:2px;">
            <button :style="'${BTN}'" @click="move(i, -1)" :disabled="i === 0" title="Up">↑</button>
            <button :style="'${BTN}'" @click="move(i, 1)"  :disabled="i === order.length - 1" title="Down">↓</button>
          </span>
        </div>
      </div>
    </div>
  `,
};
