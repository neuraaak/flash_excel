export default {
  name: 'ComputedTable',
  props: { columns: { type: Array, default: () => [] }, payload: { type: Object, default: () => ({}) } },
  emits: ['update:payload'],
  inject: ['i18n'],
  computed: {
    t() { return this.i18n.t; },
  },
  data() { return { localTarget: '', localExpression: '' }; },
  watch: {
    payload: { immediate: true, handler(v) { this.localTarget = v.target || ''; this.localExpression = v.expression || ''; } },
  },
  methods: {
    emit() { this.$emit('update:payload', { action: 'add_computed_column', target: this.localTarget, expression: this.localExpression }); },
    addChip(col) {
      this.localExpression += (this.localExpression.trim() ? ' ' : '') + 'col("' + col + '")';
      this.emit();
    },
  },
  template: `
    <div>
      <div class="panel-sub">{{ t('table.computed') }}</div>
      <div class="compute-card">
        <div class="cc-head">
          <input class="input" v-model="localTarget" :placeholder="t('table.target')" @input="emit" />
        </div>
        <textarea class="textarea" v-model="localExpression" placeholder='col("first") + " " + col("last")' @input="emit"></textarea>
        <div class="chips">
          <span v-for="col in columns" :key="col" class="chip" @click="addChip(col)">{{ col }}</span>
        </div>
      </div>
      <div class="panel-hint">Use Polars expressions. Reference columns with <code>col("name")</code>, e.g. <code>col("year") * 2</code>.</div>
    </div>
  `,
};
