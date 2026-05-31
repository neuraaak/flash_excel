const CAST_TYPES = ['string', 'int', 'float', 'bool', 'date', 'datetime'];
const SEL = 'background:transparent;border:none;color:var(--text-primary);font-size:var(--text-sm);width:100%;cursor:pointer;outline:none;';
export default {
  name: 'CastTable',
  props: { columns: { type: Array, default: () => [] }, payload: { type: Object, default: () => ({}) } },
  emits: ['update:payload'],
  data() { return { castTypes: CAST_TYPES }; },
  computed: { casts() { return this.payload.casts || {}; } },
  methods: {
    onChange(col, e) {
      const casts = { ...this.casts };
      if (e.target.value) casts[col] = e.target.value; else delete casts[col];
      this.$emit('update:payload', { action: 'cast_types', casts });
    },
  },
  template: `
    <div class="action-table">
      <div class="action-table__grid two-col">
        <div class="table-header__cell">SOURCE COLUMN</div>
        <div class="table-header__cell">TARGET TYPE</div>
        <template v-for="col in columns" :key="col">
          <div class="table-cell source"><span class="cell-dot"></span>{{ col }}</div>
          <div class="table-cell">
            <select :style="'${SEL}'" :value="casts[col] || ''" @change="onChange(col, $event)">
              <option value="" style="background:var(--surface-raised)">— no cast —</option>
              <option v-for="t in castTypes" :key="t" :value="t" style="background:var(--surface-raised)">{{ t }}</option>
            </select>
          </div>
        </template>
      </div>
    </div>
  `,
};
