/**
 * Curated icon set — paths extraits de Lucide v1.x (ISC license).
 * Chaque valeur est le contenu SVG interne (sans la balise <svg> elle-même).
 * Usage : import { ICONS } from './vendor/icons.js'
 */

export const ICONS = {
  // Navigation / structure
  'presets':
    `<path d="M5 7h6M5 12h10M5 17h6"/>` +
    `<circle cx="17" cy="7" r="2"/><circle cx="18" cy="17" r="2"/>`,

  'processing':
    `<path d="M5 18a8 8 0 1 1 14 0"/><path d="M12 14l4-4"/>`,

  'settings':
    `<circle cx="12" cy="12" r="3"/>` +
    `<path d="M12 2v2M12 20v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42` +
    `M2 12h2M20 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>`,

  // Actions génériques
  'x':
    `<path d="M18 6 6 18M6 6l12 12"/>`,

  'check':
    `<path d="M20 6 9 17l-5-5"/>`,

  'plus':
    `<path d="M12 5v14M5 12h14"/>`,

  'trash':
    `<path d="M3 6h18M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2M19 6l-1 14` +
    `a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>`,

  'save':
    `<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>` +
    `<path d="M17 21v-8H7v8M7 3v4h8"/>`,

  'export':
    `<path d="M12 16V4M8 8l4-4 4 4"/>`,

  // Thème
  'moon':
    `<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>`,

  'sun':
    `<circle cx="12" cy="12" r="4"/>` +
    `<path d="M12 2v2M12 20v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42` +
    `M2 12h2M20 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>`,

  // Feedback / état
  'info':
    `<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>`,

  // Fichiers
  'upload-cloud':
    `<path d="M12 16V8M9 11l3-3 3 3"/>` +
    `<path d="M20 16.5A4.5 4.5 0 0 0 18 8h-1.26A7 7 0 1 0 4 14.9"/>`,

  // Navigation verticale (ReorderTable)
  'chevron-up':
    `<path d="M18 15l-6-6-6 6"/>`,

  'chevron-down':
    `<path d="M6 9l6 6 6-6"/>`,
};
