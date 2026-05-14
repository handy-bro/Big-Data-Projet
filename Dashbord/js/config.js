/**
 * Configuration centralisée du dashboard
 * Gère les paramètres, labels, et constantes globales
 */

const CONFIG = {
  // Thèmes disponibles
  themes: {
    dark: {
      name: 'Sombre',
      colors: {
        bg: '#060810',
        bg2: '#0c1020',
        bg3: '#111828',
        border: '#1a2540',
        c1: '#00ffa3',
        c2: '#ff3d6b',
        c3: '#3d9bff',
        c4: '#ffc93d',
        c5: '#bf5fff',
        text: '#dce8ff',
        muted: '#4a5f80',
      },
    },
    light: {
      name: 'Clair',
      colors: {
        bg: '#ffffff',
        bg2: '#f5f7fa',
        bg3: '#e8ecf1',
        border: '#d0d8e0',
        c1: '#00a86b',
        c2: '#d64545',
        c3: '#1e5a96',
        c4: '#e89c3f',
        c5: '#7c3aed',
        text: '#1a202c',
        muted: '#6b7280',
      },
    },
  },

  // Polices
  fonts: {
    mono: "'JetBrains Mono', monospace",
    display: "'Bebas Neue', sans-serif",
    body: "'Inter', sans-serif",
  },

  // Labels des requêtes
  queryLabels: {
    total_transactions: 'Total txn',
    ca_par_categorie: 'CA catégorie',
    top_pays: 'Top pays',
    taux_statut: 'Taux statut',
  },

  // Couleurs des barres (gradient)
  barColors: ['#00ffa3', '#3d9bff', '#ffc93d', '#ff3d6b'],

  // Couleurs des notes
  noteColors: {
    dark: ['#ff3d6b', '#ffc93d', '#888', '#3d9bff', '#00ffa3'],
    light: ['#d64545', '#e89c3f', '#999', '#1e5a96', '#00a86b'],
  },

  // Animation
  animationDuration: 500,

  // Chart.js defaults
  chartDefaults: {
    responsive: true,
    maintainAspectRatio: false,
  },
};

// Export pour Node/Module
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CONFIG;
}
