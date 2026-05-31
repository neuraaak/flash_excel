export default {
  name: 'DeduplicateTable',
  props: { columns: { type: Array, default: () => [] }, payload: { type: Object, default: () => ({}) } },
  emits: ['update:payload'],
  computed: {
    keep()   { return this.payload.keep || 'first'; },
    subset() { return this.payload.subset || []; },
    effectiveColumns() {
      return this.columns.length ? this.columns : this.subset;
    },
  },
  methods: {
    isOn(col) { return this.subset.includes(col); },
    emit(subset, keep) { this.$emit('update:payload', { action: 'deduplicate_rows', subset, keep }); },
    toggle(col) {
      const set = new Set(this.subset);
      if (set.has(col)) set.delete(col); else set.add(col);
      this.emit(this.effectiveColumns.filter(c => set.has(c)), this.keep);
    },
    setKeep(v) { this.emit(this.subset, v); },
  },
  template: `
    <div>
      <div class="panel-sub">Key columns</div>
      <div class="toggle-list">
        <div v-for="col in effectiveColumns" :key="col" class="toggle-row" :class="{ on: isOn(col) }">
          <span class="tr-name">{{ col }}</span>
          <label class="switch">
            <input type="checkbox" :checked="isOn(col)" @change="toggle(col)">
            <span class="track"></span>
          </label>
        </div>
      </div>
      <div class="field" style="margin-top:16px;">
        <span class="field-label">When duplicates are found, keep</span>
        <span class="seg">
          <button :class="{ active: keep === 'first' }" @click="setKeep('first')">First row</button>
          <button :class="{ active: keep === 'last' }"  @click="setKeep('last')">Last row</button>
          <button :class="{ active: keep === 'none' }"  @click="setKeep('none')">None</button>
        </span>
      </div>
      <div class="panel-hint">Rows are duplicates when all selected key columns match. Leave empty to use all columns.</div>
    </div>
  `,
};
