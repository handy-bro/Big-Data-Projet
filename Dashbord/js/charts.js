/**
 * Gestionnaire des graphiques
 * Crée et gère les graphiques Chart.js
 */

class ChartManager {
  constructor(config = CONFIG, themeManager = null) {
    this.config = config;
    this.themeManager = themeManager;
    this.charts = new Map();
  }

  /**
   * Crée les graphiques de temps d'exécution
   */
  createTimeChart(containerId, benchData) {
    if (this.charts.has('timeChart')) {
      this.charts.get('timeChart').destroy();
    }

    const benchmark = benchData.benchmark;
    const names = Object.keys(benchmark);
    const hives = names.map(n => benchmark[n].hive_avg_s);
    const hits = names.map(n => benchmark[n].redis_hit_ms);

    const theme = this.themeManager?.getCurrent() || this.config.themes.dark;
    const colors = theme.colors;

    const ctx = document.getElementById(containerId);
    if (!ctx) return null;

    const chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: names.map(n => this.config.queryLabels[n] || n),
        datasets: [
          {
            label: 'Hive (s)',
            data: hives,
            backgroundColor: this.rgba(colors.c2, 0.7),
            borderColor: colors.c2,
            borderWidth: 1,
            borderRadius: 4,
            yAxisID: 'yH'
          },
          {
            label: 'Redis HIT (ms)',
            data: hits,
            backgroundColor: this.rgba(colors.c1, 0.7),
            borderColor: colors.c1,
            borderWidth: 1,
            borderRadius: 4,
            yAxisID: 'yR'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: {
              color: colors.muted,
              font: { family: this.config.fonts.mono, size: 10 }
            }
          }
        },
        scales: {
          x: {
            ticks: { color: colors.muted, font: { family: this.config.fonts.mono, size: 10 } },
            grid: { color: colors.border }
          },
          yH: {
            type: 'linear',
            position: 'left',
            ticks: { color: colors.c2, font: { family: this.config.fonts.mono, size: 9 } },
            grid: { color: colors.border },
            title: { display: true, text: 'Hive(s)', color: colors.c2, font: { size: 9 } }
          },
          yR: {
            type: 'linear',
            position: 'right',
            ticks: { color: colors.c1, font: { family: this.config.fonts.mono, size: 9 } },
            grid: { drawOnChartArea: false },
            title: { display: true, text: 'Redis(ms)', color: colors.c1, font: { size: 9 } }
          }
        }
      }
    });

    this.charts.set('timeChart', chart);
    return chart;
  }

  /**
   * Crée le graphique de facteur d'accélération
   */
  createSpeedupChart(containerId, benchData) {
    if (this.charts.has('speedupChart')) {
      this.charts.get('speedupChart').destroy();
    }

    const benchmark = benchData.benchmark;
    const names = Object.keys(benchmark);
    const speedups = names.map(n => benchmark[n].speedup);

    const theme = this.themeManager?.getCurrent() || this.config.themes.dark;
    const colors = theme.colors;

    const ctx = document.getElementById(containerId);
    if (!ctx) return null;

    const chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: names.map(n => this.config.queryLabels[n] || n),
        datasets: [{
          label: 'Speedup x',
          data: speedups,
          backgroundColor: this.config.barColors.map(c => this.rgba(c, 0.7)),
          borderColor: this.config.barColors,
          borderWidth: 1,
          borderRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: {
            ticks: { color: colors.muted, font: { family: this.config.fonts.mono, size: 10 } },
            grid: { color: colors.border }
          },
          y: {
            ticks: {
              color: colors.muted,
              font: { family: this.config.fonts.mono, size: 9 },
              callback: v => 'x' + v.toLocaleString()
            },
            grid: { color: colors.border }
          }
        }
      }
    });

    this.charts.set('speedupChart', chart);
    return chart;
  }

  /**
   * Détruit tous les graphiques
   */
  destroyAll() {
    this.charts.forEach(chart => chart.destroy());
    this.charts.clear();
  }

  /**
   * Utilitaire: convertir couleur hex en rgba
   */
  rgba(hex, alpha) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r},${g},${b},${alpha})`;
  }
}

let chartManager = null;

function initChartManager() {
  if (!chartManager) {
    chartManager = new ChartManager(CONFIG, themeManager);
  }
  return chartManager;
}
