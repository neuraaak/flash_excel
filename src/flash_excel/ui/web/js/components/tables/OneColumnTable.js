export default {
  name: 'OneColumnTable',
  props: {
    columns:  { type: Array,  default: () => [] },
    selected: { type: Array,  default: () => [] },
    header:   { type: String, default: 'COLUMN' },
  },
  emits: ['update:selected'],
  methods: {
    toggle(col) {
      const set = new Set(this.selected);
      if (set.has(col)) set.delete(col); else set.add(col);
      this.$emit('update:selected', this.columns.filter(c => set.has(c)));
    },
  },
  template: `
    <div class="action-table">
      <div class="action-table__grid one-col">
        <div class="table-header__cell">{{ header }}</div>
        <template v-for="col in columns" :key="col">
          <div class="table-cell source" style="cursor:pointer;gap:10px;" @click="toggle(col)">
            <input type="checkbox" :checked="selected.includes(col)"
              @click.stop="toggle(col)" style="accent-color:var(--accent-brand);cursor:pointer;" />
            {{ col }}
          </div>
        </template>
      </div>
    </div>
  `,
};
