/**
 * 🌾 AGRIWISE AI - Lightweight Canvas Charting Engine
 * Zero-dependency, high-performance HTML5 Canvas charts for Mandi prices,
 * Farm health radar, weather curves, and multi-scenario ROI.
 */

const AgriCharts = {
  // 1. Line Chart with Gradient Fill (Mandi Prices & Weather)
  drawLineChart(canvasId, labels, dataPoints, options = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const width = canvas.width = canvas.parentElement.clientWidth || 600;
    const height = canvas.height = options.height || 260;

    ctx.clearRect(0, 0, width, height);

    const padding = { top: 30, right: 30, bottom: 40, left: 60 };
    const chartW = width - padding.left - padding.right;
    const chartH = height - padding.top - padding.bottom;

    const maxVal = Math.max(...dataPoints) * 1.1;
    const minVal = Math.max(0, Math.min(...dataPoints) * 0.9);
    const valRange = (maxVal - minVal) || 1;

    // Grid lines
    ctx.strokeStyle = '#f1f5f9';
    ctx.lineWidth = 1;
    const gridLines = 4;
    for (let i = 0; i <= gridLines; i++) {
      const y = padding.top + (chartH / gridLines) * i;
      ctx.beginPath();
      ctx.moveTo(padding.left, y);
      ctx.lineTo(width - padding.right, y);
      ctx.stroke();

      // Y-axis labels
      const labelVal = Math.round(maxVal - (valRange / gridLines) * i);
      ctx.fillStyle = '#94a3b8';
      ctx.font = '11px sans-serif';
      ctx.textAlign = 'right';
      ctx.fillText(options.prefix ? `${options.prefix}${labelVal}` : labelVal, padding.left - 10, y + 4);
    }

    // Points calculation
    const points = dataPoints.map((val, idx) => {
      const x = padding.left + (chartW / (dataPoints.length - 1)) * idx;
      const y = padding.top + chartH - ((val - minVal) / valRange) * chartH;
      return { x, y, val, label: labels[idx] };
    });

    // Gradient fill under curve
    const gradient = ctx.createLinearGradient(0, padding.top, 0, height - padding.bottom);
    gradient.addColorStop(0, options.fillColor || 'rgba(16, 185, 129, 0.25)');
    gradient.addColorStop(1, 'rgba(16, 185, 129, 0.0)');

    ctx.beginPath();
    ctx.moveTo(points[0].x, height - padding.bottom);
    points.forEach(pt => ctx.lineTo(pt.x, pt.y));
    ctx.lineTo(points[points.length - 1].x, height - padding.bottom);
    ctx.closePath();
    ctx.fillStyle = gradient;
    ctx.fill();

    // Draw Line
    ctx.beginPath();
    ctx.strokeStyle = options.lineColor || '#059669';
    ctx.lineWidth = 3;
    points.forEach((pt, idx) => {
      if (idx === 0) ctx.moveTo(pt.x, pt.y);
      else ctx.lineTo(pt.x, pt.y);
    });
    ctx.stroke();

    // Draw Points & X-Labels
    points.forEach(pt => {
      ctx.beginPath();
      ctx.arc(pt.x, pt.y, 4, 0, Math.PI * 2);
      ctx.fillStyle = '#ffffff';
      ctx.strokeStyle = options.lineColor || '#059669';
      ctx.lineWidth = 2;
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = '#64748b';
      ctx.font = '11px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(pt.label, pt.x, height - 12);
    });
  },

  // 2. Multi-scenario Bar Chart (Conservative, Expected, Optimistic)
  drawScenarioBarChart(canvasId, scenarios) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const width = canvas.width = canvas.parentElement.clientWidth || 600;
    const height = canvas.height = 280;

    ctx.clearRect(0, 0, width, height);

    const keys = ['conservative', 'expected', 'optimistic'];
    const labels = ['Conservative', 'Expected (Baseline)', 'Optimistic'];
    const colors = ['#f59e0b', '#059669', '#0284c7'];

    const padding = { top: 30, right: 30, bottom: 50, left: 70 };
    const chartW = width - padding.left - padding.right;
    const chartH = height - padding.top - padding.bottom;

    const revenues = keys.map(k => scenarios[k].expected_revenue_inr);
    const profits = keys.map(k => scenarios[k].estimated_net_profit_inr);
    const maxVal = Math.max(...revenues) * 1.15;

    // Grid
    for (let i = 0; i <= 4; i++) {
      const y = padding.top + (chartH / 4) * i;
      ctx.strokeStyle = '#f1f5f9';
      ctx.beginPath();
      ctx.moveTo(padding.left, y);
      ctx.lineTo(width - padding.right, y);
      ctx.stroke();

      const val = Math.round(maxVal - (maxVal / 4) * i);
      ctx.fillStyle = '#94a3b8';
      ctx.font = '11px sans-serif';
      ctx.textAlign = 'right';
      ctx.fillText(`₹${(val / 1000).toFixed(0)}k`, padding.left - 10, y + 4);
    }

    const groupWidth = chartW / keys.length;
    const barWidth = groupWidth * 0.28;

    keys.forEach((k, idx) => {
      const groupX = padding.left + groupWidth * idx + (groupWidth - barWidth * 2 - 10) / 2;
      const revH = (revenues[idx] / maxVal) * chartH;
      const profH = (profits[idx] / maxVal) * chartH;

      // Revenue Bar
      ctx.fillStyle = '#cbd5e1';
      ctx.beginPath();
      ctx.roundRect(groupX, padding.top + chartH - revH, barWidth, revH, [4, 4, 0, 0]);
      ctx.fill();

      // Profit Bar
      ctx.fillStyle = colors[idx];
      ctx.beginPath();
      ctx.roundRect(groupX + barWidth + 8, padding.top + chartH - profH, barWidth, profH, [4, 4, 0, 0]);
      ctx.fill();

      // Label below
      ctx.fillStyle = '#334155';
      ctx.font = 'bold 12px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(labels[idx], padding.left + groupWidth * idx + groupWidth / 2, height - 20);

      // ROI % tag above profit bar
      ctx.fillStyle = colors[idx];
      ctx.font = 'bold 11px sans-serif';
      ctx.fillText(`${scenarios[k].roi_percentage}% ROI`, groupX + barWidth + 8 + barWidth / 2, padding.top + chartH - profH - 8);
    });
  },

  // 3. Radar Chart for Farm Suitability Breakdown (Climate, Soil, Water, Weather, Season, Market, Economics)
  drawRadarChart(canvasId, scores) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const size = Math.min(canvas.parentElement.clientWidth || 320, 320);
    canvas.width = canvas.height = size;

    ctx.clearRect(0, 0, size, size);

    const centerX = size / 2;
    const centerY = size / 2;
    const radius = size * 0.36;

    const categories = [
      { label: 'Climate', key: 'climate' },
      { label: 'Soil', key: 'soil' },
      { label: 'Water', key: 'water' },
      { label: 'Weather', key: 'weather' },
      { label: 'Season', key: 'season' },
      { label: 'Market', key: 'market' },
      { label: 'Economics', key: 'economics' }
    ];

    const numAxes = categories.length;
    const angleStep = (Math.PI * 2) / numAxes;

    // Background concentric polygon webs
    for (let level = 1; level <= 4; level++) {
      const r = (radius / 4) * level;
      ctx.beginPath();
      for (let i = 0; i < numAxes; i++) {
        const angle = i * angleStep - Math.PI / 2;
        const x = centerX + r * Math.cos(angle);
        const y = centerY + r * Math.sin(angle);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.closePath();
      ctx.strokeStyle = '#e2e8f0';
      ctx.stroke();
    }

    // Axes
    for (let i = 0; i < numAxes; i++) {
      const angle = i * angleStep - Math.PI / 2;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(x, y);
      ctx.strokeStyle = '#cbd5e1';
      ctx.stroke();

      // Axis label
      const labelX = centerX + (radius + 20) * Math.cos(angle);
      const labelY = centerY + (radius + 20) * Math.sin(angle);
      ctx.fillStyle = '#64748b';
      ctx.font = '11px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(categories[i].label, labelX, labelY + 4);
    }

    // Data polygon
    ctx.beginPath();
    categories.forEach((cat, i) => {
      const val = scores[cat.key] || 80;
      const r = (radius * (val / 100));
      const angle = i * angleStep - Math.PI / 2;
      const x = centerX + r * Math.cos(angle);
      const y = centerY + r * Math.sin(angle);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.closePath();
    ctx.fillStyle = 'rgba(16, 185, 129, 0.35)';
    ctx.fill();
    ctx.strokeStyle = '#059669';
    ctx.lineWidth = 2.5;
    ctx.stroke();
  }
};

window.AgriCharts = AgriCharts;
