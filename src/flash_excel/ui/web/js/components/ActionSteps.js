import RenameTable      from './tables/RenameTable.js';
import SelectTable      from './tables/SelectTable.js';
import CastTable        from './tables/CastTable.js';
import ReplaceTable     from './tables/ReplaceTable.js';
import CleanTable       from './tables/CleanTable.js';
import ComputedTable    from './tables/ComputedTable.js';
import FilterTable      from './tables/FilterTable.js';
import DeduplicateTable from './tables/DeduplicateTable.js';
import SortTable        from './tables/SortTable.js';
import ReorderTable     from './tables/ReorderTable.js';

const STEPS = [
  { action: 'rename_columns',      label: 'Rename columns',      desc: 'Give one or more columns a new name.' },
  { action: 'select_columns',      label: 'Select columns',      desc: 'Keep only the columns you choose.' },
  { action: 'cast_types',          label: 'Cast types',          desc: 'Convert columns to a target data type.' },
  { action: 'replace_values',      label: 'Replace values',      desc: 'Find and replace values inside columns.' },
  { action: 'trim_whitespace',     label: 'Clean text',          desc: 'Trim, normalise and strip whitespace.' },
  { action: 'add_computed_column', label: 'Add computed column', desc: 'Create a new column from an expression.' },
  { action: 'filter_rows',         label: 'Filter rows',         desc: 'Keep only rows matching your conditions.' },
  { action: 'deduplicate_rows',    label: 'Deduplicate rows',    desc: 'Remove duplicate rows by key columns.' },
  { action: 'sort_rows',           label: 'Sort rows',           desc: 'Order rows by one or more columns.' },
  { action: 'reorder_columns',     label: 'Reorder columns',     desc: 'Change the column order.' },
];

const EDITOR_MAP = {
  rename_columns:      RenameTable,
  select_columns:      SelectTable,
  cast_types:          CastTable,
  replace_values:      ReplaceTable,
  trim_whitespace:     CleanTable,
  add_computed_column: ComputedTable,
  filter_rows:         FilterTable,
  deduplicate_rows:    DeduplicateTable,
  sort_rows:           SortTable,
  reorder_columns:     ReorderTable,
};

function countPayload(p) {
  if (!p) return 0;
  if (p.mapping)          return Object.keys(p.mapping).length;
  if (p.columns)          return p.columns.length;
  if (p.casts)            return Object.keys(p.casts).length;
  if (p.rules_by_column)  return Object.keys(p.rules_by_column).length;
  if (p.conditions)       return p.conditions.length;
  if (p.subset)           return p.subset.length;
  if (p.by)               return p.by.length;
  if (p.target)           return 1;
  return 0;
}

export default {
  name: 'ActionSteps',
  components: { ...EDITOR_MAP },
  props: {
    columns:  { type: Array,  default: () => [] },
    payloads: { type: Object, default: () => ({}) },
  },
  emits: ['update:payloads'],
  data() { return { activeAction: null, steps: STEPS }; },
  computed: {
    activeEditor()  { return this.activeAction ? EDITOR_MAP[this.activeAction] : null; },
    activePayload() { return this.activeAction ? (this.payloads[this.activeAction] || {}) : {}; },
    activeStep()    { return this.steps.find(s => s.action === this.activeAction); },
    activeCount()   { return countPayload(this.activePayload); },
  },
  methods: {
    countFor(action) { return countPayload(this.payloads[action]); },
    onPayload(payload) {
      this.$emit('update:payloads', { ...this.payloads, [this.activeAction]: payload });
    },
  },
  template: `
    <div class="config">

      <!-- Left: action list -->
      <div class="action-list">
        <div v-for="s in steps" :key="s.action"
          class="action-item"
          :class="{ active: activeAction === s.action, on: countFor(s.action) > 0 }"
          @click="activeAction = s.action">
          <span class="ai-status"><span class="ring"></span></span>
          <span class="ai-name">{{ s.label }}</span>
          <span v-if="countFor(s.action) > 0" class="ai-count">{{ countFor(s.action) }}</span>
          <span class="ai-info" :title="s.desc" @click.stop>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/></svg>
          </span>
        </div>
      </div>

      <!-- Right: config panel -->
      <div class="panel">
        <div v-if="!activeAction" class="panel-empty">
          Select an action to configure it
        </div>
        <template v-else>
          <div class="panel-head">
            <div class="ph-text">
              <h3>{{ activeStep.label }}</h3>
              <p>{{ activeStep.desc }}</p>
            </div>
            <span class="ph-count">{{ activeCount }} configured</span>
          </div>
          <div class="panel-body">
            <component :is="activeEditor"
              :columns="columns"
              :payload="activePayload"
              @update:payload="onPayload" />
          </div>
        </template>
      </div>

    </div>
  `,
};
