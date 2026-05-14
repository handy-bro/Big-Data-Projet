/**
 * Gestionnaire de rendu du dashboard
 * Responsable du rendu de tous les éléments du dashboard
 */

class DashboardRenderer {
  constructor(config = CONFIG, themeManager = null, chartManager = null) {
    this.config = config;
    this.themeManager = themeManager;
    this.chartManager = chartManager;
  }

  /**
   * Rendu principal
   */
  render(benchData, corrData) {
    const dashboard = document.getElementById('dashboard');
    if (!dashboard) return;

    dashboard.classList.add('on');
    document.getElementById('fDate').textContent = new Date().toLocaleString('fr-FR');

    if (benchData) this.renderBench(benchData);
    if (corrData) this.renderCorr(corrData);
  }

  /**
   * Rendu des données de benchmark
   */
  renderBench(data) {
    const b = data.benchmark;
    const names = Object.keys(b);
    const speedups = names.map(n => b[n].speedup);
    const hives = names.map(n => b[n].hive_avg_s);
    const hits = names.map(n => b[n].redis_hit_ms);

    // Cartes KPI
    document.getElementById('cSpeedup').textContent = 'x' + Math.max(...speedups).toLocaleString('fr-FR');
    document.getElementById('cHive').textContent = Math.max(...hives).toFixed(0) + 's';
    document.getElementById('cRedis').textContent = (hits.reduce((a, b) => a + b, 0) / hits.length).toFixed(2) + 'ms';
    document.getElementById('cNb').textContent = names.length;

    // Graphiques
    this.chartManager?.createTimeChart('chTemps', data);
    this.chartManager?.createSpeedupChart('chSpeedup', data);

    // Table
    this.renderBenchTable(b, names, speedups);
  }

  /**
   * Rendu du tableau de benchmark
   */
  renderBenchTable(benchmark, names, speedups) {
    const theme = this.themeManager?.getCurrent() || this.config.themes.dark;
    const maxSp = Math.max(...speedups);
    const barColors = this.config.barColors;

    const html = names.map((n, i) => {
      const row = benchmark[n];
      const pct = (row.speedup / maxSp * 100).toFixed(1);
      const color = barColors[i % barColors.length];
      return `<tr>
        <td style="color:${color};font-weight:700">${this.config.queryLabels[n] || n}</td>
        <td class="red">${row.hive_avg_s}s <span style="color:${theme.colors.muted};font-size:0.6rem">±${row.hive_std_s || 0}</span></td>
        <td class="red">${row.redis_miss_s || '—'}s</td>
        <td class="green">${row.redis_hit_ms}ms</td>
        <td class="gold"><div class="bar-wrap">x${row.speedup.toLocaleString('fr-FR')}<div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div></div></td>
      </tr>`;
    }).join('');

    document.getElementById('tBody').innerHTML = html;
  }

  /**
   * Rendu des données de corrélation
   */
  renderCorr(c) {
    const n = c.echantillon_taille;
    document.getElementById('cSample').textContent = (n / 1000).toFixed(0) + 'K';

    this.renderQualityStats(c.qualite, n);
    this.renderDistributionNotes(c.distribution_notes);
    this.renderDistributionStatuts(c.distribution_statuts);
    this.renderPearsonMatrix(c.pearson);
    this.renderSpearman(c.spearman);
  }

  /**
   * Rendu des statistiques de qualité
   */
  renderQualityStats(qualite, sampleSize) {
    const theme = this.themeManager?.getCurrent() || this.config.themes.dark;
  }

  /**
   * Rendu de la distribution des notes
   */
  renderDistributionNotes(notes) {
    const theme = this.themeManager?.getCurrent() || this.config.themes.dark;
    const noteColors = this.config.noteColors[this.themeManager?.currentTheme || 'dark'];
    const total = Object.values(notes).reduce((a, b) => a + b, 0);

    const html = Object.entries(notes).map(([k, v], i) => `
      <div class="note-bar">
        <span class="note-lbl">Note ${k}</span>
        <div class="note-track"><div class="note-fill" style="width:${(v / total * 100).toFixed(0)}%;background:${noteColors[i]}"></div></div>
        <span class="note-pct">${(v / total * 100).toFixed(1)}%</span>
      </div>
    `).join('');
  }

  /**
   * Rendu de la distribution des statuts
   */
  renderDistributionStatuts(statuts) {
    const total = Object.values(statuts).reduce((a, b) => a + b, 0);

    const html = Object.entries(statuts).map(([k, v]) => `
      <div class="stat-row">
        <span class="stat-k">${k}</span>
        <span class="stat-v">${(v / total * 100).toFixed(1)}%</span>
      </div>
    `).join('');
  }

  /**
   * Rendu de la matrice de Pearson
   */
  renderPearsonMatrix(pearson) {
    const theme = this.themeManager?.getCurrent() || this.config.themes.dark;
    const colors = theme.colors;
    const cols = ['prix', 'qte', 'note'];

    const corrBg = (val) => {
      const a = Math.abs(val);
      if (val > 0) return `rgba(${this.hexToRgb(colors.c1).join(',')},${0.1 + a * 0.6})`;
      return `rgba(${this.hexToRgb(colors.c2).join(',')},${0.1 + a * 0.6})`;
    };

    const corrColor = (val) => {
      return Math.abs(val) < 0.2 ? colors.muted : val > 0 ? colors.c1 : colors.c2;
    };

    let mHtml = '<div></div>' + cols.map(c => `<div class="mx-hdr">${c}</div>`).join('');
    cols.forEach(row => {
      mHtml += `<div class="mx-lbl">${row}</div>`;
      cols.forEach(col => {
        const val = pearson[row][col];
        mHtml += `<div class="mx-cell" style="background:${corrBg(val)};color:${corrColor(val)}">${val.toFixed(4)}</div>`;
      });
    });
  }

  /**
   * Rendu de Spearman
   */
  renderSpearman(spearman) {
    const theme = this.themeManager?.getCurrent() || this.config.themes.dark;
    const colors = theme.colors;

    const spItems = [
      { label: 'Prix ↔ Note client', data: spearman.prix_note },
      { label: 'Quantité ↔ Note client', data: spearman.qte_note },
    ];

    const html = spItems.map(item => {
      const sig = item.data.significatif;
      const col = item.data.corr > 0 ? colors.c1 : item.data.corr < 0 ? colors.c2 : colors.muted;
      const interp = Math.abs(item.data.corr) < 0.1
        ? '→ Corrélation très faible — variables indépendantes'
        : item.data.corr > 0 ? '→ Corrélation positive' : '→ Corrélation négative';

      return `<div class="sp-item">
        <div class="sp-row">
          <span class="sp-name">${item.label}</span>
          <span class="badge ${sig ? 'sig' : 'nsig'}">${sig ? 'SIGNIFICATIF' : 'NON SIG.'}</span>
        </div>
        <div class="sp-row">
          <span class="sp-val" style="color:${col}">ρ = ${item.data.corr.toFixed(4)}</span>
          <span class="sp-p">p = ${item.data.p_value.toFixed(4)}</span>
        </div>
        <div class="sp-interp">${interp}</div>
      </div>`;
    }).join('');
  }

  /**
   * Utilitaire: convertir hex en RGB
   */
  hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? [
      parseInt(result[1], 16),
      parseInt(result[2], 16),
      parseInt(result[3], 16)
    ] : [0, 0, 0];
  }

  /**
   * Réinitialise le rendu
   */
  reset() {
    document.getElementById('dashboard').classList.remove('on');
    this.chartManager?.destroyAll();
  }
}

let renderer = null;

function initRenderer() {
  if (!renderer) {
    renderer = new DashboardRenderer(CONFIG, themeManager, chartManager);
  }
  return renderer;
}
