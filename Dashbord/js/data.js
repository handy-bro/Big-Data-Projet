/**
 * Gestionnaire des données
 * Gère le chargement, validation et stockage des données
 */

class DataManager {
  constructor() {
    this.benchData = null;
    this.corrData = null;
    this.listeners = [];
  }

  /**
   * Charge un fichier JSON et le traite
   */
  loadJSON(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = JSON.parse(e.target.result);
          resolve(data);
        } catch (err) {
          reject(new Error(`Erreur JSON: ${err.message}`));
        }
      };
      reader.onerror = () => reject(new Error('Erreur de lecture du fichier'));
      reader.readAsText(file);
    });
  }

  /**
   * Définit les données de benchmark
   */
  setBenchData(data, filename = '') {
    this.benchData = data;
    this.notifyListeners('bench', { data, filename });
  }

  /**
   * Définit les données de corrélation
   */
  setCorrData(data, filename = '') {
    this.corrData = data;
    this.notifyListeners('corr', { data, filename });
  }

  /**
   * Retourne les données de benchmark
   */
  getBenchData() {
    return this.benchData;
  }

  /**
   * Retourne les données de corrélation
   */
  getCorrData() {
    return this.corrData;
  }

  /**
   * Vérifie si les données sont complètes
   */
  isComplete() {
    return this.benchData !== null && this.corrData !== null;
  }

  /**
   * Réinitialise les données
   */
  reset() {
    this.benchData = null;
    this.corrData = null;
    this.notifyListeners('reset', null);
  }

  /**
   * Enregistre un listener
   */
  onChange(callback) {
    this.listeners.push(callback);
  }

  /**
   * Notifie les listeners
   */
  notifyListeners(type, payload) {
    this.listeners.forEach(cb => cb(type, payload));
  }
}

/**
 * Données de démonstration
 */
const DEMO_DATA = {
  bench: {
    benchmark: {
      total_transactions: { hive_avg_s: 1056.661, hive_std_s: 627.739, redis_miss_s: 2012.730, redis_hit_ms: 0.57, speedup: 1860230 },
      ca_par_categorie: { hive_avg_s: 1120.398, hive_std_s: 1084.152, redis_miss_s: 286.328, redis_hit_ms: 0.56, speedup: 2000385 },
      top_pays: { hive_avg_s: 208.631, hive_std_s: 10.836, redis_miss_s: 221.441, redis_hit_ms: 3.22, speedup: 64806 },
      taux_statut: { hive_avg_s: 248.627, hive_std_s: 12.867, redis_miss_s: 228.091, redis_hit_ms: 0.53, speedup: 464850 },
    }
  },
  corr: {
    echantillon_taille: 50000,
    qualite: {
      prix_min: 1.01, prix_max: 1999.83, prix_moyen: 1001.42, prix_std: 575.26,
      outliers_prix: 0, outliers_qte: 0,
      nulls: { prix: 0, qte: 0, note: 0, statut: 0, categorie: 0, pays: 0 }
    },
    pearson: {
      prix: { prix: 1.0, qte: 0.0019, note: -0.0041 },
      qte: { prix: 0.0019, qte: 1.0, note: 0.0074 },
      note: { prix: -0.0041, qte: 0.0074, note: 1.0 }
    },
    spearman: {
      prix_note: { corr: -0.0041, p_value: 0.362618, significatif: 0 },
      qte_note: { corr: 0.0074, p_value: 0.099117, significatif: 0 }
    },
    distribution_notes: { 1: 9941, 2: 9997, 3: 10043, 4: 9906, 5: 10113 },
    distribution_statuts: { livre: 10102, confirme: 10010, annule: 10009, en_attente: 9971, rembourse: 9908 }
  }
};

// Instance globale
let dataManager = null;

function initDataManager() {
  if (!dataManager) {
    dataManager = new DataManager();
  }
  return dataManager;
}
