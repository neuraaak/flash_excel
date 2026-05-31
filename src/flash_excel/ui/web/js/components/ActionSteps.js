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
  { action: 'rename_columns',      label: 'Rename columns',      desc: 'Rename one or more columns.' },
  { action: 'select_columns',      label: 'Select columns',      desc: 'Keep only selected columns.' },
  { action: 'cast_types',          label: 'Cast types',          desc: 'Convert column data types.' },
  { action: 'replace_values',      label: 'Replace values',      desc: 'Replace exact values in a column.' },
  { action: 'trim_whitespace',     label: 'Clean text',          desc: 'Strip leading/trailing whitespace.' },
  { action: 'add_computed_column', label: 'Add computed column', desc: 'Create a column from an expression.' },
  { action: 'filter_rows',         label: 'Filter rows',         desc: 'Keep rows matching conditions.' },
  { action: 'deduplicate_rows',    label: 'Deduplicate rows',    desc: 'Remove duplicate rows.' },
  { action: 'sort_rows',           label: 'Sort rows',           desc: 'Sort rows by one or more columns.' },
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
    activeEditor()      { return this.activeAction ? EDITOR_MAP[this.activeAction] : null; },
    activePayload()     { return this.activeAction ? (this.payloads[this.activeAction] || {}) : {}; },
    activeStep()        { return this.steps.find(s => s.action === this.activeAction); },
  },
  methods: {
    countFor(action) { return countPayload(this.payloads[action]); },
    onPayload(payload) {
      this.$emit('update:payloads', { ...this.payloads, [this.activeAction]: payload });
    },
  },
  template: `
    <div class="action-steps">
      <!-- Left list -->
      <div class="action-steps__list">
        <div v-for="s in steps" :key="s.action"
          class="action-step-item" :class="{ active: activeAction === s.action }"
          :title="s.desc" @click="activeAction = s.action">
          <span class="step-dot" :class="countFor(s.action) > 0 ? 'on' : 'off'"></span>
          <span class="action-step-item__title" :class="{ configured: countFor(s.action) > 0 }">{{ s.label }}</span>
          <span v-if="countFor(s.action) > 0" class="badge badge--accent">{{ countFor(s.action) }}</span>
          <span class="badge badge--neutral" style="padding:0 5px;font-size:10px;cursor:help;" :title="s.desc">i</span>
        </div>
      </div>

      <!-- Right editor -->
      <div class="action-steps__editor">
        <div v-if="!activeAction" style="display:flex;align-items:center;justify-content:center;height:100%;color:var(--text-secondary);font-size:var(--text-sm);">
          Select an action to configure it
        </div>
        <template v-else>
          <div style="padding:var(--sp-3);border-bottom:1px solid var(--border-subtle);flex-shrink:0;">
            <div style="font-size:var(--text-md);font-weight:600;color:var(--text-primary);">{{ activeStep?.label }}</div>
            <div style="font-size:var(--text-sm);color:var(--text-secondary);margin-top:2px;">{{ activeStep?.desc }}</div>
          </div>
          <div style="flex:1;overflow:auto;min-height:0;">
            <component :is="activeEditor" :columns="columns" :payload="activePayload" @update:payload="onPayload" />
          </div>
        </template>
      </div>
    </div>
  `,
};
