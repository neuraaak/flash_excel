export default {
  name: 'FileLoader',
  props: { fileInfo: { type: Object, default: null } },
  emits: ['load', 'clear'],
  methods: {
    onClear(e) { e.stopPropagation(); this.$emit('clear'); },
    sizeLabel(b) {
      if (b < 1024) return `${b} B`;
      if (b < 1048576) return `${(b / 1024).toFixed(1)} KB`;
      return `${(b / 1048576).toFixed(1)} MB`;
    },
  },
  template: `
    <div v-if="!fileInfo" class="dropzone" @click="$emit('load')">
      <span class="dz-ico">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 16V8M9 11l3-3 3 3"/>
          <path d="M20 16.5A4.5 4.5 0 0 0 18 8h-1.26A7 7 0 1 0 4 14.9"/>
        </svg>
      </span>
      <span>Load file <span style="color:var(--text_secondary);font-weight:400;">— or drop it here</span></span>
    </div>

    <div v-else class="file-loaded">
      <div class="file-loaded__icon">
        <svg width="32" height="36" viewBox="0 0 32 36" fill="none">
          <rect x="1" y="1" width="22" height="30" rx="3"
            :fill="fileInfo.file_type !== 'csv' ? '#217346' : '#4a5568'" stroke="none"/>
          <text x="12" y="22" text-anchor="middle" font-size="9" font-weight="700" fill="white" font-family="sans-serif">
            {{ fileInfo.file_type === 'csv' ? 'CSV' : 'XLS' }}
          </text>
        </svg>
      </div>
      <div class="file-loaded__meta">
        <div class="file-loaded__name">{{ fileInfo.file_name }}</div>
        <div class="file-loaded__size">{{ sizeLabel(fileInfo.size_bytes) }}</div>
      </div>
      <button class="icon-btn" @click="onClear" title="Remove file">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <path d="M6 6l12 12M18 6L6 18"/>
        </svg>
      </button>
    </div>
  `,
};
