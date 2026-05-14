/**
 * Gestionnaire de thème
 * Gère le basculement entre thème clair et sombre
 */

class ThemeManager {
  constructor(config = CONFIG) {
    this.config = config;
    this.currentTheme = this.loadTheme() || 'dark';
    this.listeners = [];
    this.init();
  }

  /**
   * Initialise le gestionnaire de thème
   */
  init() {
    this.applyTheme(this.currentTheme);
    this.setupMediaListener();
    this.createThemeToggle();
  }

  /**
   * Charge le thème depuis le localStorage
   */
  loadTheme() {
    return localStorage.getItem('dashboard-theme');
  }

  /**
   * Sauvegarde le thème dans le localStorage
   */
  saveTheme(theme) {
    localStorage.setItem('dashboard-theme', theme);
  }

  /**
   * Applique un thème en mettant à jour les variables CSS
   */
  applyTheme(themeName) {
    const theme = this.config.themes[themeName];
    if (!theme) {
      console.warn(`Thème '${themeName}' introuvable`);
      return;
    }

    const root = document.documentElement;
    Object.entries(theme.colors).forEach(([key, value]) => {
      root.style.setProperty(`--${key}`, value);
    });

    document.body.setAttribute('data-theme', themeName);
    this.currentTheme = themeName;
    this.saveTheme(themeName);
    this.notifyListeners(themeName);
  }

  /**
   * Alterne entre clair et sombre
   */
  toggle() {
    const nextTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
    this.applyTheme(nextTheme);
  }

  /**
   * Détecte les préférences système et applique automatiquement
   */
  setupMediaListener() {
    const prefDark = window.matchMedia('(prefers-color-scheme: dark)');
    prefDark.addListener(() => {
      if (!localStorage.getItem('dashboard-theme')) {
        this.applyTheme(prefDark.matches ? 'dark' : 'light');
      }
    });
  }

  /**
   * Crée le bouton de basculement de thème dans le header
   */
  createThemeToggle() {
    const headerRight = document.querySelector('.loaders');
    if (!headerRight) return;

    const toggle = document.createElement('button');
    toggle.className = 'btn-theme-toggle';
    toggle.setAttribute('aria-label', 'Basculer le thème');
    toggle.innerHTML = this.currentTheme === 'dark' 
      ? '🌙 Clair' 
      : '☀️ Sombre';
    
    toggle.addEventListener('click', () => {
      this.toggle();
      toggle.innerHTML = this.currentTheme === 'dark' 
        ? '🌙 Clair' 
        : '☀️ Sombre';
    });

    headerRight.appendChild(toggle);
  }

  /**
   * Enregistre un listener pour les changements de thème
   */
  onChange(callback) {
    this.listeners.push(callback);
  }

  /**
   * Notifie tous les listeners
   */
  notifyListeners(themeName) {
    this.listeners.forEach(cb => cb(themeName));
  }

  /**
   * Retourne le thème courant
   */
  getCurrent() {
    return this.config.themes[this.currentTheme];
  }

  /**
   * Retourne une couleur du thème courant
   */
  getColor(colorName) {
    return this.getCurrent().colors[colorName];
  }
}

// Instance globale
let themeManager = null;

function initThemeManager() {
  if (!themeManager) {
    themeManager = new ThemeManager(CONFIG);
  }
  return themeManager;
}
