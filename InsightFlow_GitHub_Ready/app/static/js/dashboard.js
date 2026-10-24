document.addEventListener('DOMContentLoaded', function () {
  // Check if chart data exists on the window object
  if (typeof window.dashboardChartData === 'undefined') {
    return;
  }

  const chartData = window.dashboardChartData;
  const ctxTrend = document.getElementById('revenueTrendCanvas');
  const ctxChannel = document.getElementById('revenueChannelCanvas');
  const ctxOrders = document.getElementById('ordersQuarterCanvas');

  // Common typography & tooltip options
  Chart.defaults.font.family = "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif";
  Chart.defaults.font.size = 11;
  Chart.defaults.color = '#7E869B';

  // 1. Revenue Trend Line Chart
  if (ctxTrend && chartData.revenue_trend) {
    const trendConfig = chartData.revenue_trend;
    const gradient = ctxTrend.getContext('2d').createLinearGradient(0, 0, 0, 260);
    gradient.addColorStop(0, 'rgba(108, 92, 231, 0.22)');
    gradient.addColorStop(1, 'rgba(108, 92, 231, 0.00)');

    if (trendConfig.data.datasets[0]) {
      trendConfig.data.datasets[0].backgroundColor = gradient;
    }

    new Chart(ctxTrend, {
      type: 'line',
      data: trendConfig.data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#151928',
            titleColor: '#A0A7BA',
            bodyColor: '#FFFFFF',
            padding: 10,
            cornerRadius: 8,
            callbacks: {
              label: function (context) {
                let val = context.raw;
                return `${context.dataset.label}: $${val.toLocaleString()}`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            border: { display: false }
          },
          y: {
            grid: {
              color: '#EEF2F6',
              drawBorder: false
            },
            border: { display: false },
            ticks: {
              callback: function (value) {
                return '$' + (value / 1000) + 'k';
              }
            }
          }
        }
      }
    });
  }

  // 2. Revenue By Channel Donut Chart
  if (ctxChannel && chartData.revenue_channel) {
    new Chart(ctxChannel, {
      type: 'doughnut',
      data: chartData.revenue_channel.data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '72%',
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#151928',
            callbacks: {
              label: function (context) {
                let val = context.raw;
                return ` $${val.toLocaleString()}`;
              }
            }
          }
        }
      }
    });
  }

  // 3. Orders By Quarter Grouped Bar Chart
  if (ctxOrders && chartData.orders_quarter) {
    new Chart(ctxOrders, {
      type: 'bar',
      data: chartData.orders_quarter.data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#151928',
            callbacks: {
              label: function (context) {
                return ` ${context.dataset.label}: ${context.raw.toLocaleString()} orders`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            border: { display: false }
          },
          y: {
            grid: {
              color: '#EEF2F6',
              drawBorder: false
            },
            border: { display: false },
            ticks: {
              callback: function (value) {
                return (value >= 1000 ? (value / 1000).toFixed(1) + 'k' : value);
              }
            }
          }
        }
      }
    });
  }

  // Live filter handlers
  const yearSelect = document.getElementById('yearSelect');
  if (yearSelect) {
    yearSelect.addEventListener('change', function () {
      const url = new URL(window.location.href);
      url.searchParams.set('year', this.value);
      window.location.href = url.toString();
    });
  }

  const datasetSelect = document.getElementById('datasetSelect');
  if (datasetSelect) {
    datasetSelect.addEventListener('change', function () {
      const url = new URL(window.location.href);
      url.searchParams.set('dataset_id', this.value);
      window.location.href = url.toString();
    });
  }
});
