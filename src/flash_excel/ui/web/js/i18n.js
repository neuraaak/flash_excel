import { ref, readonly } from './vendor/vue.esm-browser.prod.js';
import en from './locales/en.js';
import fr from './locales/fr.js';

const LOCALES = { en, fr };
const _locale = ref('en');
const _dict   = ref(LOCALES['en']);

function setLocale(code) {
  _locale.value = code;
  _dict.value   = LOCALES[code] ?? LOCALES['en'];
}

function t(key) {
  return _dict.value[key] ?? LOCALES['en'][key] ?? key;
}

export const i18n = { locale: readonly(_locale), setLocale, t };
