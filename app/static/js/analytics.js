/* VisionBoard AI — Analytics Chart.js Visualizations */

function initAnalyticsCharts(objectData, colorData) {
  // 1. Objects Bar Chart
  const objCanvas = document.getElementById('objectsChart');
  if (objCanvas && objectData) {
    const labels = objectData.map(item => item[0]);
    const counts = objectData.map(item => item[1]);

    new Chart(objCanvas, {
      type: 'bar',
      data: {
        labels: labels.length > 0 ? labels : ['No Data'],
        datasets: [{
          label: 'Detections Count',
          data: counts.length > 0 ? counts : [0],
          backgroundColor: 'rgba(0, 242, 254, 0.6)',
          borderColor: '#00F2FE',
          borderWidth: 2,
          borderRadius: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: {
            ticks: { color: '#94A3B8' },
            grid: { color: 'rgba(255, 255, 255, 0.05)' }
          },
          y: {
            beginAtZero: true,
            ticks: { color: '#94A3B8', precision: 0 },
            grid: { color: 'rgba(255, 255, 255, 0.05)' }
          }
        }
      }
    });
  }

  // 2. Colors Doughnut Chart
  const colCanvas = document.getElementById('colorsChart');
  if (colCanvas && colorData) {
    const hexCodes = colorData.map(item => item[0]);
    const counts = colorData.map(item => item[1]);

    new Chart(colCanvas, {
      type: 'doughnut',
      data: {
        labels: hexCodes.length > 0 ? hexCodes : ['#3A86FF'],
        datasets: [{
          data: counts.length > 0 ? counts : [1],
          backgroundColor: hexCodes.length > 0 ? hexCodes : ['#3A86FF'],
          borderColor: 'rgba(9, 13, 22, 0.8)',
          borderWidth: 3
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right',
            labels: { color: '#F1F5F9', font: { family: 'Outfit' } }
          }
        }
      }
    });
  }
}
