/**
 * Application principale
 * Orchestre tous les modules et gère le cycle de vie
 */

class DashboardApp {
  constructor() {
    this.dataManager = initDataManager();
    this.themeManager = initThemeManager();
    this.chartManager = initChartManager();
    this.renderer = initRenderer();
    
    this.setupEventListeners();
    this.setupDataListeners();
  }

  /**
   * Initialise les écouteurs d'événements
   */
  setupEventListeners() {
    // Fichier benchmark
    const fileInput1 = document.getElementById('f1');
    if (fileInput1) {
      fileInput1.addEventListener('change', (e) => this.handleBenchmarkFileLoad(e));
    }

    // Fichier corrélation
    const fileInput2 = document.getElementById('f2');
    if (fileInput2) {
      fileInput2.addEventListener('change', (e) => this.handleCorrFileLoad(e));
    }

    // Bouton démo (si présent)
    if (window.loadDemo) {
      const demoBtn = document.querySelector('.btn-demo');
      if (demoBtn) {
        demoBtn.addEventListener('click', () => this.loadDemo());
      }
    }
  }

  /**
   * Initialise les écouteurs de données
   */
  setupDataListeners() {
    this.dataManager.onChange((type, payload) => {
      if (type === 'bench' || type === 'corr') {
        this.checkAndRender();
      } else if (type === 'reset') {
        this.renderer.reset();
      }
    });

    // Re-rendu lors du changement de thème
    this.themeManager.onChange((theme) => {
      if (this.dataManager.isComplete()) {
        this.renderer.reset();
        this.renderer.render(
          this.dataManager.getBenchData(),
          this.dataManager.getCorrData()
        );
      }
    });
  }

  /**
   * Gère le chargement du fichier benchmark
   */
  async handleBenchmarkFileLoad(event) {
    const file = event.target.files[0];
    if (!file) return;

    try {
      const data = await this.dataManager.loadJSON(file);
      this.dataManager.setBenchData(data, file.name);
      
      const box = document.getElementById('box1');
      if (box) {
        box.classList.add('loaded');
      }
      
      const status = document.getElementById('st1');
      if (status) {
        status.textContent = file.name;
      }
    } catch (error) {
      alert(error.message);
    }
  }

  /**
   * Gère le chargement du fichier corrélation
   */
  async handleCorrFileLoad(event) {
    const file = event.target.files[0];
    if (!file) return;

    try {
      const data = await this.dataManager.loadJSON(file);
      this.dataManager.setCorrData(data, file.name);
      
      const box = document.getElementById('box2');
      if (box) {
        box.classList.add('loaded');
      }
      
      const status = document.getElementById('st2');
      if (status) {
        status.textContent = file.name;
      }
    } catch (error) {
      alert(error.message);
    }
  }

  /**
   * Charge les données de démonstration
   */
  loadDemo() {
    this.dataManager.setBenchData(DEMO_DATA.bench, 'benchmark_results.json');
    this.dataManager.setCorrData(DEMO_DATA.corr, 'correlation_results.json');
    
    const box1 = document.getElementById('box1');
    const box2 = document.getElementById('box2');
    if (box1) box1.classList.add('loaded');
    if (box2) box2.classList.add('loaded');
    
    const st1 = document.getElementById('st1');
    const st2 = document.getElementById('st2');
    if (st1) st1.textContent = 'benchmark_results.json';
    if (st2) st2.textContent = 'correlation_results.json';
  }

  /**
   * Vérifie si les données sont complètes et effectue le rendu
   */
  checkAndRender() {
    if (this.dataManager.isComplete()) {
      this.renderer.render(
        this.dataManager.getBenchData(),
        this.dataManager.getCorrData()
      );
    }
  }
}

// Initialisation au chargement du DOM
document.addEventListener('DOMContentLoaded', () => {
  window.app = new DashboardApp();
});

// Expose les fonctions globales (compatibilité)
function loadDemo() {
  if (window.app) {
    window.app.loadDemo();
  }
}
