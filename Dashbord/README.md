# Dashboard Big Data — Architecture Refactorisée

## Vue d'ensemble

Le code a été **refactorisé pour maximiser l'extensibilité** avec une **séparation claire des préoccupations**. L'architecture est maintenant modulaire, maintenable et facilement extensible.

## Structure des fichiers

```
Dashbord/
├── dashboard.html          # Fichier HTML principal (épuré)
├── css/
│   └── styles.css          # Tous les styles CSS (séparés)
├── js/
│   ├── config.js           # Configuration centralisée (thèmes, labels, constantes)
│   ├── data.js             # Gestion des données et données de démo
│   ├── theme.js            # Gestionnaire de thème clair/sombre
│   ├── charts.js           # Gestionnaire des graphiques Chart.js
│   ├── renderer.js         # Moteur de rendu du dashboard
│   └── app.js              # Application principale (orchestration)
└── README.md               # Cette documentation
```

## Améliorations principales

### 1. **Séparation des préoccupations** ✅
Chaque module a une responsabilité unique et bien définie :

- **`config.js`** : Centralise tous les paramètres (thèmes, labels, couleurs)
- **`data.js`** : Gère le cycle de vie des données (chargement, stockage, événements)
- **`theme.js`** : Contrôle le basculement thème clair/sombre + localStorage
- **`charts.js`** : Encapsule la logique Chart.js (création, mise à jour, destruction)
- **`renderer.js`** : Responsable du rendu UI (conversion données → DOM)
- **`app.js`** : Orchestre tous les modules (orchestration)

### 2. **Système de thème amélioré** 🌓

#### Points forts :
- **Deux thèmes complets** : Sombre (défaut) + Clair
- **Basculement en temps réel** : Bascule fluide avec transition CSS
- **Persistance** : Le choix utilisateur est sauvegardé en localStorage
- **Détection système** : Respecte les préférences du système (`prefers-color-scheme`)
- **Bouton intégré** : Toggle dans le header du dashboard
- **Couleurs optimisées** : Contraste maximal pour chaque thème

#### Configuration des thèmes :
```javascript
CONFIG.themes = {
  dark: { colors: { /* couleurs sombres */ } },
  light: { colors: { /* couleurs claires */ } }
}
```

### 3. **Architecture modulaire extensible**

#### Ajouter une nouvelle fonctionnalité :

**Exemple : Ajouter un exporteur PDF**

```javascript
// nouveau fichier: js/exporter.js
class PDFExporter {
  constructor(renderer) {
    this.renderer = renderer;
  }
  export(filename) {
    // logique d'export
  }
}

// Dans app.js
this.exporter = new PDFExporter(this.renderer);
```

#### Ajouter un nouveau thème :

```javascript
// Dans config.js
themes: {
  dark: { /* ... */ },
  light: { /* ... */ },
  highContrast: { /* nouveau thème */ }
}

// Utilisation automatique via themeManager.toggle()
```

### 4. **Avantages de cette architecture**

| Aspect | Avant | Après |
|--------|-------|-------|
| **Fichier unique** | ✗ 1000+ lignes | ✓ ~50 lignes |
| **Réutilisabilité** | ✗ Code dupliqué | ✓ Modules indépendants |
| **Testabilité** | ✗ Difficile | ✓ Chaque classe isolée |
| **Maintenance** | ✗ Complexe | ✓ Responsabilités claires |
| **Extension** | ✗ Couplage fort | ✓ Plugins faciles |
| **Thèmes** | ✗ Sombre seulement | ✓ Clair + Sombre + custom |

## Utilisation

### Mode développement
```bash
# Ouvrir simplement dashboard.html dans un navigateur
# Les modules se chargeront en cascade
```

### Charger des données
1. **Par fichier JSON** : Cliquez sur "Charger" pour chaque section
2. **Mode démo** : Décommentez `<!-- <button class="btn-demo">⚡ Démo</button> -->` en HTML

### Basculer de thème
- Cliquez sur le bouton **"☀️ Sombre"** ou **"🌙 Clair"** dans le header
- Choix sauvegardé automatiquement

## Extensibilité : Cas d'usage

### ✅ Ajouter un nouveau type de graphique
```javascript
// Dans charts.js
createHistogramChart(containerId, data) {
  // Logique du nouvel histogramme
}
```

### ✅ Ajouter une métrique personnalisée
```javascript
// Dans config.js - ajouter dans CONFIG
customMetrics: {
  myMetric: { label: '...', color: '...' }
}

// Dans renderer.js - ajouter le rendu
renderCustomMetric(data) { /* ... */ }
```

### ✅ Ajouter une action utilisateur
```javascript
// Dans app.js
setupEventListeners() {
  document.getElementById('my-button').addEventListener('click', 
    () => this.myAction()
  );
}
```

### ✅ Intégrer une nouvelle source de données
```javascript
// Nouveau dans data.js
async loadFromAPI(url) {
  const response = await fetch(url);
  return response.json();
}

dataManager.loadFromAPI('/api/benchmark').then(data => 
  dataManager.setBenchData(data)
);
```

## Flux de données

```
Utilisateur
    ↓
[app.js] ← Événements utilisateur
    ↓
[dataManager] ← Données chargées
    ↓
[renderer] ← Rendu + [chartManager] ← Graphiques
    ↓
[themeManager] ← Couleurs actuelles
    ↓
DOM (CSS variables)
```

## Variables CSS globales

Toutes les couleurs utilisent des variables CSS qui changent avec le thème :

```css
:root {
  --bg: /* couleur fond */
  --bg2: /* couleur fond secondaire */
  --c1: /* couleur primaire */
  --text: /* couleur texte */
  /* etc. */
}
```

Modifier une couleur ? C'est automatique dans tous les composants.

## Performance

- **Lazy loading** : Les graphiques ne se créent que si nécessaire
- **Destruction propre** : Les graphiques sont détruits avant recréation
- **localStorage** : Thème sauvegardé (pas de requête à chaque rechargement)
- **CSS transitions** : Changements de thème fluides

## Compatibilité

- ✅ Chrome/Edge (dernier)
- ✅ Firefox (dernier)
- ✅ Safari (dernier)
- ✅ Mobile (responsive)

## Prochaines étapes possibles

1. **Framework** : Migrer vers Vue/React si nécessaire (structure prête)
2. **Backend** : API REST pour les données
3. **Cache** : IndexedDB pour cache local
4. **Export** : PDF/CSV export
5. **Thèmes** : Ajouter plus de palettes (High Contrast, Colorblind-friendly)
6. **Tests** : Ajouter Jest/Vitest pour chaque module

---

**Architecture pensée pour l'avenir** 🚀
