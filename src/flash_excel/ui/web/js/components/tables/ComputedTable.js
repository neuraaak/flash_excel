const FUNCTIONS = [
  {
    name: "CONCATENER", cat: "Texte", hint: "CONCATENER(col1, col2, …)",
    desc: "Assemble plusieurs colonnes ou textes en une seule chaîne.",
    example: 'CONCATENER(prenom, " ", nom)',
  },
  {
    name: "MAJUSCULE", cat: "Texte", hint: "MAJUSCULE(col)",
    desc: "Convertit tous les caractères en majuscules.",
    example: "MAJUSCULE(nom)",
  },
  {
    name: "MINUSCULE", cat: "Texte", hint: "MINUSCULE(col)",
    desc: "Convertit tous les caractères en minuscules.",
    example: "MINUSCULE(email)",
  },
  {
    name: "GAUCHE", cat: "Texte", hint: "GAUCHE(col, n)",
    desc: "Retourne les n premiers caractères de la colonne.",
    example: "GAUCHE(code, 3)",
  },
  {
    name: "DROITE", cat: "Texte", hint: "DROITE(col, n)",
    desc: "Retourne les n derniers caractères de la colonne.",
    example: "DROITE(reference, 4)",
  },
  {
    name: "NBCAR", cat: "Texte", hint: "NBCAR(col)",
    desc: "Retourne le nombre de caractères de la colonne.",
    example: "NBCAR(description)",
  },
  {
    name: "SUPPRESPACE", cat: "Texte", hint: "SUPPRESPACE(col)",
    desc: "Supprime les espaces en début et fin de chaîne.",
    example: "SUPPRESPACE(nom)",
  },
  {
    name: "ARRONDI", cat: "Math", hint: "ARRONDI(col, n)",
    desc: "Arrondit à n décimales (0 = entier).",
    example: "ARRONDI(prix, 2)",
  },
  {
    name: "ABS", cat: "Math", hint: "ABS(col)",
    desc: "Retourne la valeur absolue (toujours positif).",
    example: "ABS(ecart)",
  },
  {
    name: "MULTIPLIER", cat: "Math", hint: "MULTIPLIER(col, n)",
    desc: "Multiplie chaque valeur par n.",
    example: "MULTIPLIER(prix, 1.2)",
  },
  {
    name: "AJOUTER", cat: "Math", hint: "AJOUTER(col1, col2)",
    desc: "Additionne deux colonnes numériques.",
    example: "AJOUTER(base, bonus)",
  },
  {
    name: "ANNEE", cat: "Date", hint: "ANNEE(col)",
    desc: "Extrait l'année d'une colonne date.",
    example: "ANNEE(date_naissance)",
  },
  {
    name: "MOIS", cat: "Date", hint: "MOIS(col)",
    desc: "Extrait le mois (1–12) d'une colonne date.",
    example: "MOIS(date_commande)",
  },
  {
    name: "JOUR", cat: "Date", hint: "JOUR(col)",
    desc: "Extrait le jour du mois d'une colonne date.",
    example: "JOUR(date_livraison)",
  },
  {
    name: "AUJOURD_HUI", cat: "Date", hint: "AUJOURD_HUI()", label: "AUJOURD'HUI",
    desc: "Retourne la date du jour.",
    example: "AUJOURD_HUI()",
  },
  {
    name: "SI", cat: "Logique", hint: "SI(cond, alors, sinon)",
    desc: "Si la condition est vraie retourne 'alors', sinon 'sinon'. La condition peut utiliser ==, !=, <, >, <=, >=.",
    example: 'SI(age >= 18, "majeur", "mineur")',
  },
];

const FN_CATS = ["Texte", "Math", "Date", "Logique"];

export default {
  name: 'ComputedTable',
  props: { columns: { type: Array, default: () => [] }, payload: { type: Object, default: () => ({}) } },
  emits: ['update:payload'],
  inject: ['i18n'],

  data() {
    return {
      showModal:   false,
      editIndex:   null,
      draft:       { target: '', expression: '' },
      fnCat:       'Texte',
      hintText:    '',
      hoveredFn:   null,
      popoverStyle: {},
      functions:   FUNCTIONS,
      fnCats:      FN_CATS,
    };
  },

  computed: {
    t()          { return this.i18n.t; },
    items()      { return this.payload.items || []; },
    visibleFns() { return this.functions.filter(f => f.cat === this.fnCat); },
  },

  methods: {
    openAdd() {
      this.editIndex = null;
      this.draft = { target: '', expression: '' };
      this.hintText = '';
      this.showModal = true;
    },
    openEdit(idx) {
      this.editIndex = idx;
      const item = this.items[idx];
      this.draft = { target: item.target, expression: item.expression };
      this.hintText = '';
      this.showModal = true;
    },
    closeModal() { this.showModal = false; this.hoveredFn = null; },

    insertCol(col) {
      this.draft.expression += (this.draft.expression.trim() ? ' ' : '') + col;
      this.focusExpr();
    },
    insertFn(fn) {
      this.draft.expression += (this.draft.expression.trim() ? ' ' : '') + fn.name + '(';
      this.hintText = fn.hint;
      this.focusExpr();
    },
    focusExpr() {
      this.$nextTick(() => {
        const el = this.$refs.exprInput;
        if (el) { el.focus(); el.setSelectionRange(el.value.length, el.value.length); }
      });
    },

    showPopover(fn, evt) {
      this.hoveredFn = fn;
      const rect = evt.currentTarget.getBoundingClientRect();
      // Position popover to the left of the index panel
      this.popoverStyle = {
        top:   rect.top + 'px',
        right: (window.innerWidth - rect.left + 8) + 'px',
      };
    },
    hidePopover() { this.hoveredFn = null; },

    save() {
      if (!this.draft.target.trim() || !this.draft.expression.trim()) return;
      const updated = [...this.items];
      const entry = { target: this.draft.target.trim(), expression: this.draft.expression.trim() };
      if (this.editIndex === null) updated.push(entry);
      else updated[this.editIndex] = entry;
      this.emit(updated);
      this.closeModal();
    },

    deleteItem(idx) {
      this.emit(this.items.filter((_, i) => i !== idx));
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

          <!-- Two-column modal layout -->
          <div style="display:flex;align-items:flex-start;gap:0;max-width:820px;width:95vw;max-height:90vh;border-radius:10px;overflow:hidden;background:var(--surface_raised);box-shadow:0 8px 40px rgba(0,0,0,.4)">

            <!-- LEFT — editor -->
            <div style="flex:1 1 0;min-width:0;display:flex;flex-direction:column;max-height:90vh">

              <div class="modal-head">
                <span class="modal-title">{{ editIndex !== null ? t('computed.edit_title') : t('computed.add_title') }}</span>
                <button class="mini-btn" @click="closeModal">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </button>
              </div>

              <div class="modal-body" style="gap:14px;overflow-y:auto;flex:1 1 auto">

                <div class="field">
                  <span class="field-label">{{ t('computed.col_name') }}</span>
                  <input class="input" v-model="draft.target" :placeholder="t('table.target')" />
                </div>

                <div class="field">
                  <span class="field-label">{{ t('table.expression') }}</span>
                  <textarea ref="exprInput" class="textarea" v-model="draft.expression"
                    placeholder='MAJUSCULE(CONCATENER(prenom, " ", nom))'
                    style="font-family:var(--mono);font-size:12px;min-height:72px"></textarea>
                  <div v-if="hintText" style="font-family:var(--mono);font-size:11px;color:var(--accent_brand);margin-top:3px">{{ hintText }}</div>
                </div>

                <div class="field" style="gap:6px">
                  <span class="field-label">Colonnes</span>
                  <div class="chips">
                    <span v-for="col in columns" :key="col" class="chip" :title="col" @click="insertCol(col)">{{ col }}</span>
                  </div>
                </div>

                <div class="field" style="gap:6px">
                  <div style="display:flex;align-items:center;gap:8px;margin-bottom:2px">
                    <span class="field-label" style="margin:0">Fonctions</span>
                    <div class="seg" style="font-size:11px">
                      <button v-for="cat in fnCats" :key="cat" :class="{ active: fnCat === cat }" @click="fnCat = cat">{{ cat }}</button>
                    </div>
                  </div>
                  <div class="chips">
                    <span v-for="fn in visibleFns" :key="fn.name" class="chip" :title="fn.hint" @click="insertFn(fn)">{{ fn.label || fn.name }}</span>
                  </div>
                </div>

              </div>

              <div class="modal-foot">
                <button class="btn btn-ghost" @click="closeModal">{{ t('modal.cancel') }}</button>
                <button class="btn btn-primary" @click="save" :disabled="!draft.target.trim() || !draft.expression.trim()">{{ t('modal.save') }}</button>
              </div>

            </div>

            <!-- RIGHT — function index -->
            <div style="width:200px;flex:0 0 200px;border-left:1px solid var(--border_subtle);display:flex;flex-direction:column;max-height:90vh">

              <div style="padding:12px 14px 8px;font-size:10px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--text_secondary);border-bottom:1px solid var(--border_subtle)">
                Index
              </div>

              <!-- Category tabs -->
              <div style="display:flex;border-bottom:1px solid var(--border_subtle)">
                <button v-for="cat in fnCats" :key="cat"
                  @click="fnCat = cat"
                  style="flex:1;padding:6px 0;font-size:10px;font-weight:600;border:none;background:none;cursor:pointer;transition:.12s;"
                  :style="fnCat === cat ? 'color:var(--accent_brand);border-bottom:2px solid var(--accent_brand);margin-bottom:-1px' : 'color:var(--text_secondary)'">
                  {{ cat[0] }}
                </button>
              </div>

              <!-- Function rows -->
              <div style="flex:1;overflow-y:auto;padding:4px 0">
                <div v-for="fn in visibleFns" :key="fn.name"
                  @mouseenter="showPopover(fn, $event)"
                  @mouseleave="hidePopover"
                  @click="insertFn(fn)"
                  style="display:flex;align-items:center;justify-content:space-between;padding:7px 14px;cursor:pointer;transition:.1s;gap:6px"
                  :style="hoveredFn && hoveredFn.name === fn.name ? 'background:var(--surface_overlay)' : ''">
                  <span style="font-family:var(--mono);font-size:11px;font-weight:600;color:var(--text_primary)">{{ fn.label || fn.name }}</span>
                  <span style="font-size:10px;color:var(--text_secondary);opacity:.7">?</span>
                </div>
              </div>

            </div>

          </div>

          <!-- Popover (teleported to body, positioned absolutely) -->
          <teleport to="body">
            <div v-if="hoveredFn" :style="popoverStyle"
              style="position:fixed;z-index:9999;width:240px;padding:12px 14px;background:var(--surface_floating);border:1px solid var(--border_subtle);border-radius:8px;box-shadow:0 4px 20px rgba(0,0,0,.35);pointer-events:none">
              <div style="font-family:var(--mono);font-size:12px;font-weight:700;color:var(--accent_brand);margin-bottom:6px">{{ hoveredFn.hint }}</div>
              <div style="font-size:12px;color:var(--text_primary);margin-bottom:8px;line-height:1.5">{{ hoveredFn.desc }}</div>
              <div style="font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.05em;color:var(--text_secondary);margin-bottom:4px">Exemple</div>
              <div style="font-family:var(--mono);font-size:11px;color:var(--text_primary);background:var(--surface_sunken);padding:5px 8px;border-radius:4px">{{ hoveredFn.example }}</div>
            </div>
          </teleport>

        </div>
      </teleport>

    </div>
  `,
};
