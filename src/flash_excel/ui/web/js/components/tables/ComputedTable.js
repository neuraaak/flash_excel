export default {
  name: 'ComputedTable',
  props: { columns: { type: Array, default: () => [] }, payload: { type: Object, default: () => ({}) } },
  emits: ['update:payload'],
  inject: ['i18n'],
  data() {
    return {
      showModal: false,
      editIndex: null,
      draft: { target: '', expression: '' },
    };
  },
  computed: {
    t() { return this.i18n.t; },
    items() { return this.payload.items || []; },
  },
  methods: {
    openAdd() {
      this.editIndex = null;
      this.draft = { target: '', expression: '' };
      this.showModal = true;
    },
    openEdit(idx) {
      this.editIndex = idx;
      const item = this.items[idx];
      this.draft = { target: item.target, expression: item.expression };
      this.showModal = true;
    },
    closeModal() { this.showModal = false; },

    addChip(col) {
      this.draft.expression += (this.draft.expression.trim() ? ' ' : '') + 'col("' + col + '")';
    },

    save() {
      if (this.draft.target.trim() === '' || this.draft.expression.trim() === '') return;
      const updated = [...this.items];
      if (this.editIndex === null) {
        updated.push({ target: this.draft.target.trim(), expression: this.draft.expression.trim() });
      } else {
        updated[this.editIndex] = { target: this.draft.target.trim(), expression: this.draft.expression.trim() };
      }
      this.emit(updated);
      this.closeModal();
    },

    deleteItem(idx) {
      const updated = this.items.filter((_, i) => i !== idx);
      this.emit(updated);
    },

    emit(items) {
      this.$emit('update:payload', { action: 'add_computed_column', items });
    },
  },
  template: `
    <div>

      <!-- Cards list -->
      <div v-if="items.length">
        <div v-for="(item, idx) in items" :key="idx" class="compute-card">
          <div class="cc-head">
            <span class="input" style="cursor:pointer;display:flex;align-items:center;" @click="openEdit(idx)">{{ item.target || '…' }}</span>
            <button class="mini-btn danger" @click="deleteItem(idx)">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
            </button>
          </div>
          <div class="panel-hint" style="margin-top:0;font-family:var(--mono);font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{{ item.expression }}</div>
        </div>
      </div>

      <!-- Add button -->
      <button class="add-rule" @click="openAdd">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        {{ t('computed.add') }}
      </button>

      <!-- Modal -->
      <teleport to="body">
        <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
          <div class="modal">

            <div class="modal-head">
              <span class="modal-title">{{ editIndex !== null ? t('computed.edit_title') : t('computed.add_title') }}</span>
              <button class="mini-btn" @click="closeModal">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </button>
            </div>

            <div class="modal-body">
              <div class="field">
                <span class="field-label">{{ t('computed.col_name') }}</span>
                <input class="input" v-model="draft.target" :placeholder="t('table.target')" />
              </div>
              <div class="field">
                <span class="field-label">{{ t('table.expression') }}</span>
                <textarea class="textarea" v-model="draft.expression" placeholder='col("first") + " " + col("last")'></textarea>
                <div class="chips">
                  <span v-for="col in columns" :key="col" class="chip" @click="addChip(col)">{{ col }}</span>
                </div>
              </div>
              <div class="panel-hint">Use Polars expressions. Reference columns with <code>col("name")</code>, e.g. <code>col("year") * 2</code>.</div>
            </div>

            <div class="modal-foot">
              <button class="btn btn-ghost" @click="closeModal">{{ t('modal.cancel') }}</button>
              <button class="btn btn-primary" @click="save" :disabled="!draft.target.trim() || !draft.expression.trim()">{{ t('modal.save') }}</button>
            </div>

          </div>
        </div>
      </teleport>

    </div>
  `,
};
