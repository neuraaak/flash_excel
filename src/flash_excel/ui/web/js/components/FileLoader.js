export default {
  name: 'FileLoader',
  props: { fileInfo: { type: Object, default: null } },
  emits: ['load', 'clear'],
  data() { return { dragOver: false }; },
  computed: {
    sizeLabel() {
      if (!this.fileInfo) return '';
      const b = this.fileInfo.size_bytes;
      if (b < 1024) return `${b} B`;
      if (b < 1048576) return `${(b / 1024).toFixed(1)} KB`;
      return `${(b / 1048576).toFixed(1)} MB`;
    },
  },
  methods: {
    onClick()        { if (!this.fileInfo) this.$emit('load'); },
    onDragOver(e)    { e.preventDefault(); this.dragOver = true; },
    onDragLeave()    { this.dragOver = false; },
    onDrop(e) {
      e.preventDefault(); this.dragOver = false;
      const file = e.dataTransfer?.files[0];
      if (file) this.$emit('load', file.path || null);
    },
    clearFile(e) { e.stopPropagation(); this.$emit('clear'); },
  },
  template: `
    <div class="file-loader" :class="{ 'drag-over': dragOver }"
      @click="onClick" @dragover="onDragOver" @dragleave="onDragLeave" @drop="onDrop">

      <div v-if="!fileInfo" class="file-loader__empty">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
          <polyline points="16 16 12 12 8 16"/>
          <line x1="12" y1="12" x2="12" y2="21"/>
          <path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/>
        </svg>
        Load file — or drop it here
      </div>

      <div v-else class="file-loader__loaded">
        <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
          <rect x="4" y="2" width="20" height="28" rx="3"
            :fill="fileInfo.file_type === 'excel' ? '#217346' : '#5a6375'"/>
          <text x="14" y="21" text-anchor="middle" font-size="10" font-weight="700" fill="white">
            {{ fileInfo.file_type === 'excel' ? 'XLS' : 'CSV' }}
          </text>
        </svg>
        <div class="file-loader__meta">
          <div class="file-loader__name">{{ fileInfo.file_name }}</div>
          <div class="file-loader__size">{{ sizeLabel }}</div>
        </div>
        <button class="btn btn-ghost btn-icon-only" @click="clearFile" title="Remove file">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
            <path d="M10 11v6M14 11v6"/>
          </svg>
        </button>
      </div>
    </div>
  `,
};
