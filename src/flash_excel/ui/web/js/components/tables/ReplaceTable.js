export default {
  name: 'ReplaceTable',
  props: { columns: { type: Array, default: () => [] }, payload: { type: Object, default: () => ({}) } },
  emits: ['update:payload'],
  inject: ['i18n'],
  computed: {
    t() { return this.i18n.t; },
  },
  data() { return { rows: [] }; },
  watch: {
    payload: { immediate: true, handler(v) {
      const rules = v.rules_by_column || {};
      const rows = [];
      for (const [col, spec] of Object.entries(rules)) {
        String(spec).split(',').forEach(pair => {
          const idx = pair.indexOf('=');
          if (idx === -1) return;
          rows.push({ col, find: pair.slice(0, idx).trim(), rep: pair.slice(idx + 1).trim() });
        });
      }
      this.rows = rows;
    }},
  },
  methods: {
    emit() {
      const rules = {};
      for (const r of this.rows) {
        if (!r.col || !r.find.trim()) continue;
        const pair = `${r.find.trim()}=${r.rep.trim()}`;
        rules[r.col] = rules[r.col] ? `${rules[r.col]}, ${pair}` : pair;
      }
      this.$emit('update:payload', { action: 'replace_values', rules_by_column: rules });
    },
    addRow()     { this.rows.push({ col: this.columns[0] || '', find: '', rep: '' }); this.emit(); },
    removeRow(i) { this.rows.splice(i, 1); this.emit(); },
  },
  template: `
    <div>
      <div v-if="!rows.length" class="empty-state">
        <span class="es-title">No replacements yet</span>
        <span class="es-sub">Add a rule to find and replace values.</span>
      </div>
      <template v-else>
        <div class="panel-sub">{{ t('table.replacements') }}</div>
        <div class="rule-head" style="grid-template-columns:1fr 1fr 1fr var(--ctl-h);">
          <span>{{ t('table.column') }}</span><span>Find</span><span>Replace with</span><span></span>
        </div>
        <div class="rule-list">
          <div v-for="(r, i) in rows" :key="i" class="rule-row" style="grid-template-columns:1fr 1fr 1fr var(--ctl-h);">
            <span class="select-wrap">
              <select v-model="r.col" @change="emit">
                <option v-if="r.col && !columns.includes(r.col)" :value="r.col">{{ r.col }}</option>
                <option v-for="c in columns" :key="c" :value="c">{{ c }}</option>
              </select>
            </span>
            <input class="input" v-model="r.find" placeholder="Find" @input="emit" />
            <input class="input" v-model="r.rep" placeholder="Replace with" @input="emit" />
            <button class="rule-del" @click="removeRow(i)" title="Remove">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>
            </button>
          </div>
        </div>
      </template>
      <button class="add-rule" @click="addRow">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>
        {{ t('table.add_rule') }}
      </button>
    </div>
  `,
};
