const dropZone = document.getElementById('dropZone');
const imageInput = document.getElementById('imageInput');
const previewImage = document.getElementById('previewImage');
const previewShell = document.getElementById('previewShell');
const analyzeButton = document.getElementById('analyzeButton');
const resetButton = document.getElementById('resetButton');
const aiScore = document.getElementById('aiScore');
const humanScore = document.getElementById('humanScore');
const sugenoScore = document.getElementById('sugenoScore');
const accuracyScore = document.getElementById('accuracyScore');
const entropyValue = document.getElementById('entropyValue');
const noiseValue = document.getElementById('noiseValue');
const edgeValue = document.getElementById('edgeValue');
const edgeStatValue = document.getElementById('edgeStatValue');
const noiseStatValue = document.getElementById('noiseStatValue');
const sharpnessStatValue = document.getElementById('sharpnessStatValue');
const detectionStatus = document.getElementById('detectionStatus');
const downloadReportButton = document.getElementById('downloadReportButton');
const exportCsvButton = document.getElementById('exportCsvButton');
const edgeHeatmap = document.getElementById('edgeHeatmap');
const featureTableBody = document.querySelector('#featureTable tbody');
const datasetInput = document.getElementById('datasetInput');
const datasetTestButton = document.getElementById('datasetTestButton');
const datasetTotal = document.getElementById('datasetTotal');
const datasetAI = document.getElementById('datasetAI');
const datasetHuman = document.getElementById('datasetHuman');
const datasetUncertain = document.getElementById('datasetUncertain');
const datasetAccuracy = document.getElementById('datasetAccuracy');
const galleryImage1 = document.getElementById('galleryImage1');
const galleryImage2 = document.getElementById('galleryImage2');
const galleryImage3 = document.getElementById('galleryImage3');
const galleryLabel1 = document.getElementById('galleryLabel1');
const galleryLabel2 = document.getElementById('galleryLabel2');
const galleryLabel3 = document.getElementById('galleryLabel3');
const galleryScore1 = document.getElementById('galleryScore1');
const galleryScore2 = document.getElementById('galleryScore2');
const galleryScore3 = document.getElementById('galleryScore3');
const confusionTrueAI = document.getElementById('confusionTrueAI');
const confusionFalseAI = document.getElementById('confusionFalseAI');
const heroUpload = document.getElementById('heroUpload');
const heroDetect = document.getElementById('heroDetect');
const heroLearn = document.getElementById('heroLearn');

// FITUR BARU: Element References untuk Analisis Citra
const batchDropZone = document.getElementById('batchDropZone');
const batchImageInput = document.getElementById('batchImageInput');
const batchAnalyzeButton = document.getElementById('batchAnalyzeButton');
const batchSummary = document.getElementById('batchSummary');
const batchResultsList = document.getElementById('batchResultsList');
const batchTotal = document.getElementById('batchTotal');
const batchAI = document.getElementById('batchAI');
const batchHuman = document.getElementById('batchHuman');
const batchUncertain = document.getElementById('batchUncertain');
const batchAvgAccuracy = document.getElementById('batchAvgAccuracy');
const clearHistoryButton = document.getElementById('clearHistoryButton');
const historyTable = document.querySelector('#historyTable tbody');
const historySummary = document.getElementById('historySummary');
const historyTotal = document.getElementById('historyTotal');
const historyAI = document.getElementById('historyAI');
const historyHuman = document.getElementById('historyHuman');
const historyUncertain = document.getElementById('historyUncertain');
const historyAvgAccuracy = document.getElementById('historyAvgAccuracy');
const openaiInsightButton = document.getElementById('openaiInsightButton');
const openaiStatusLabel = document.getElementById('openaiStatus');
const openaiInsightOutput = document.getElementById('openaiInsightOutput');

let currentFile = null;
let lastResult = null;
let entropyChart = null;
let histChart = null;
let fftChart = null;
let glcmChart = null;
// FITUR BARU: Chart variables
let intensityChart = null;
let rgbHistogramChart = null;
let grayscaleHistogramChart = null;
let redChannelChart = null;
let greenChannelChart = null;
let blueChannelChart = null;

const setPreview = (file) => {
  const reader = new FileReader();
  reader.onload = (e) => {
    previewImage.src = e.target.result;
    previewImage.style.display = 'block';
    previewShell.querySelector('.preview-placeholder').style.display = 'none';
  };
  reader.readAsDataURL(file);
};

const resetPreview = () => {
  previewImage.src = '';
  previewImage.style.display = 'none';
  previewShell.querySelector('.preview-placeholder').style.display = 'block';
  aiScore.textContent = '0%';
  humanScore.textContent = '0%';
  sugenoScore.textContent = '0.00';
  accuracyScore.textContent = '0%';
  entropyValue.textContent = '0.00';
  noiseValue.textContent = '0%';
  edgeValue.textContent = '0%';
  if (edgeStatValue) edgeStatValue.textContent = '0%';
  if (noiseStatValue) noiseStatValue.textContent = '0%';
  if (sharpnessStatValue) sharpnessStatValue.textContent = '0%';
  detectionStatus.textContent = 'Belum dianalisis';
  edgeHeatmap.src = '';
  featureTableBody.innerHTML = '';
  currentFile = null;
};

const fillFeatureTable = (data) => {
  const rows = [
    ['Entropy', data.entropy],
    ['Edge Density', `${data.edges}%`],
    ['Noise', `${data.noise}%`],
    ['Blur Score', `${data.blurScore}%`],
    ['Brightness', `${data.brightness}%`],
    ['Contrast', data.contrast],
    ['Saturation', `${data.saturation}%`],
    ['Color Variance', data.colorVariance],
    ['FFT High Freq', `${data.fftHighFreqRatio}%`],
    ['GLCM Contrast', data.glcmContrast],
    ['GLCM Homogeneity', data.glcmHomogeneity],
    ['GLCM Energy', data.glcmEnergy],
    ['GLCM Correlation', data.glcmCorrelation],
    ['Watermark Score', `${data.watermarkScore}%`],
    ['Defuzzified Value', `${data.defuzzifiedValue}%`],
    ['Accuracy', `${data.accuracy}%`],
  ];

  featureTableBody.innerHTML = rows
    .map(([label, value]) => `<tr><td>${label}</td><td>${value}</td></tr>`)
    .join('');
};

const downloadFile = (content, fileName, mimeType = 'text/plain') => {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

const buildReportText = (data) => {
  return `Laporan Deteksi Gambar\n` +
    `=========================\n` +
    `Status: ${data.status}\n` +
    `AI Confidence: ${data.aiConfidence}%\n` +
    `Human Confidence: ${data.humanConfidence}%\n` +
    `Accuracy: ${data.accuracy}%\n` +
    `Entropy: ${data.entropy}\n` +
    `Noise: ${data.noise}%\n` +
    `Edges: ${data.edges}%\n` +
    `Blur Score: ${data.blurScore}%\n` +
    `Brightness: ${data.brightness}%\n` +
    `Contrast: ${data.contrast}\n` +
    `Saturation: ${data.saturation}%\n` +
    `GLCM Contrast: ${data.glcmContrast}\n` +
    `GLCM Homogeneity: ${data.glcmHomogeneity}\n` +
    `GLCM Energy: ${data.glcmEnergy}\n` +
    `GLCM Correlation: ${data.glcmCorrelation}\n` +
    `Watermark Score: ${data.watermarkScore}%\n`;
};

const normalizeAnalysisData = (data) => {
  const features = data.features || {};
  const aiScore = Number(data.ai_score || 0);
  const confidence = Number(data.confidence || 0);

  return {
    filename: data.filename || '',
    status: data.classification || 'Unknown',
    aiConfidence: Math.round(aiScore * 100),
    humanConfidence: 100 - Math.round(aiScore * 100),
    fuzzySugenoScore: aiScore,
    accuracy: Math.round(confidence * 100),
    entropy: Number(features.entropy || 0),
    noise: Math.round((features.noise_score || 0) * 100),
    edges: Math.round((features.edge_density || 0) * 100),
    blurScore: Math.round((features.blur_score || 0) * 100),
    brightness: Math.round((features.brightness_score || 0) * 100),
    contrast: Number(features.contrast || 0),
    saturation: Math.round((features.saturation_score || 0) * 100),
    colorVariance: Number(features.color_variance || 0),
    fftHighFreqRatio: Math.round((features.fft_hf_ratio || 0) * 100),
    glcmContrast: Number(
      features.glcm_contrast ||
      features.glcmContrast ||
      features.glcm_contrast_raw ||
      0
    ).toFixed(4),
    glcmHomogeneity: Number(
      features.glcm_homogeneity ||
      features.glcmHomogeneity ||
      features.glcm_homogeneity_raw ||
      0
    ).toFixed(4),
    glcmEnergy: Number(
      features.glcm_energy ||
      features.glcmEnergy ||
      features.glcm_energy_raw ||
      0
    ).toFixed(4),
    glcmCorrelation: Number(
      features.glcm_correlation ||
      features.glcmCorrelation ||
      features.glcm_correlation_raw ||
      0
    ).toFixed(4),
    watermarkScore: Math.round((features.watermark_score || features.watermarkScore || 0) * 100),
    varianceIntensity: data.varianceIntensity || null,
    histogramAnalysis: data.histogramAnalysis || null,
    rgbChannels: data.rgbChannels || null,
    defuzzifiedValue: Math.round(aiScore * 100),
    sharpness: Math.round((features.blur_score || 0) * 100),
    edgeHeatmapUrl: data.heatmap_url || '',
    overlayUrl: data.overlay_url || ''
  };
};

const getStatusColor = (status) => {
  if (status === 'AI Generated') return '#ff6b6b';
  if (status === 'Human Made') return '#51cf66';
  if (status === 'Uncertain') return '#ffd43b';
  return '#c3c3c3';
};

const downloadReport = () => {
  if (!lastResult) {
    alert('Silakan lakukan analisis gambar terlebih dahulu.');
    return;
  }
  downloadFile(buildReportText(lastResult), 'deteksi_laporan.txt');
};

const renderAnalysisDashboard = (data) => {
  if (!data) return;

  updateCharts(data);
  fillFeatureTable(data);

  document.getElementById('aiScore').textContent = `${data.aiConfidence}%`;
  document.getElementById('humanScore').textContent = `${data.humanConfidence}%`;
  document.getElementById('sugenoScore').textContent = Number(data.fuzzySugenoScore).toFixed(2);
  document.getElementById('accuracyScore').textContent = `${data.accuracy}%`;
  document.getElementById('entropyValue').textContent = Number(data.entropy).toFixed(2);
  document.getElementById('noiseValue').textContent = `${data.noise}%`;
  document.getElementById('edgeValue').textContent = `${data.edges}%`;
  if (edgeStatValue) edgeStatValue.textContent = `${data.edges}%`;
  if (noiseStatValue) noiseStatValue.textContent = `${data.noise}%`;
  if (sharpnessStatValue) sharpnessStatValue.textContent = `${data.sharpness || data.blurScore || 0}%`;
  document.getElementById('detectionStatus').textContent = data.status;
};

const buildDatasetPreview = (files, results = []) => {
  const previewFiles = files.slice(0, 3);
  const resultByName = results.reduce((acc, item) => {
    acc[item.filename] = item;
    return acc;
  }, {});

  const cards = [
    { img: galleryImage1, label: galleryLabel1, score: galleryScore1, type: 'AI Generated' },
    { img: galleryImage2, label: galleryLabel2, score: galleryScore2, type: 'Human Made' },
    { img: galleryImage3, label: galleryLabel3, score: galleryScore3, type: 'Comparison' },
  ];

  cards.forEach((card, index) => {
    const file = previewFiles[index];
    const result = file ? resultByName[file.name] : null;

    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        card.img.src = event.target.result;
        card.img.style.display = 'block';
      };
      reader.readAsDataURL(file);
      card.label.textContent = result?.status || card.type;
      card.score.textContent = result ? `${result.status} (${result.accuracy}%)` : file.name;
    } else {
      card.img.src = '';
      card.img.style.display = 'none';
      card.label.textContent = card.type;
      card.score.textContent = 'Belum tersedia';
    }
  });
};

const exportCsv = () => {
  if (!lastResult) {
    alert('Silakan lakukan analisis gambar terlebih dahulu.');
    return;
  }

  const rows = [
    ['Fitur', 'Nilai'],
    ['Status', lastResult.status],
    ['AI Confidence', `${lastResult.aiConfidence}%`],
    ['Human Confidence', `${lastResult.humanConfidence}%`],
    ['Accuracy', `${lastResult.accuracy}%`],
    ['Entropy', lastResult.entropy],
    ['Noise', `${lastResult.noise}%`],
    ['Edges', `${lastResult.edges}%`],
    ['Blur Score', `${lastResult.blurScore}%`],
    ['Brightness', `${lastResult.brightness}%`],
    ['Contrast', lastResult.contrast],
    ['Saturation', `${lastResult.saturation}%`],
    ['Color Variance', lastResult.colorVariance],
    ['FFT High Freq', `${lastResult.fftHighFreqRatio}%`],
    ['GLCM Contrast', lastResult.glcmContrast],
    ['GLCM Homogeneity', lastResult.glcmHomogeneity],
    ['GLCM Energy', lastResult.glcmEnergy],
    ['GLCM Correlation', lastResult.glcmCorrelation],
    ['Watermark Score', `${lastResult.watermarkScore}%`],
  ];

  const csv = rows.map(row => row.map(value => `"${value}"`).join(',')).join('\n');
  downloadFile(csv, 'deteksi_laporan.csv', 'text/csv');
};

const formatInsightData = (data) => {
  if (!data) return '<p>Tidak ada data insight.</p>';

  if (typeof data === 'string') {
    return `<p>${data}</p>`;
  }

  const lines = [];
  if (data.analysis) {
    lines.push(`<h4>Ringkasan</h4><p>${data.analysis}</p>`);
  }

  if (data.characteristics && Array.isArray(data.characteristics)) {
    lines.push('<h4>Karakteristik</h4><ul>' + data.characteristics.map(item => `<li>${item}</li>`).join('') + '</ul>');
  }

  if (data.confidence) {
    ['GLCM Contrast', `${data.glcmContrast}%`],
    ['GLCM Homogeneity', `${data.glcmHomogeneity}%`],
    ['GLCM Energy', `${data.glcmEnergy}%`],
    ['GLCM Correlation', `${data.glcmCorrelation}%`],
    lines.push(`<h4>Rekomendasi</h4><p>${data.recommendation}</p>`);
  }

  if (data.fallback) {
    lines.push('<p class="fallback-note"><em>Catatan: insight ini dihasilkan dari fallback lokal karena layanan OpenAI tidak tersedia.</em></p>');
  }

  return lines.join('');
};

const fetchOpenAIInsight = async () => {
  if (!lastResult) {
    alert('Silakan lakukan analisis gambar terlebih dahulu.');
    return;
  }

  openaiInsightOutput.innerHTML = '<p>Mengambil insight OpenAI...</p>';

  try {
    const response = await fetch('/api/analyze-with-ai', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(lastResult),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => null);
      openaiInsightOutput.innerHTML = `<p>Gagal mengambil insight OpenAI: ${error?.error || response.statusText}</p>`;
      return;
    }

    const data = await response.json();
    openaiInsightOutput.innerHTML = formatInsightData(data.insight || data);

    if (data.openai_status) {
      openaiStatusLabel.textContent = data.openai_status.available ? 'Tersedia' : 'Tidak tersedia';
    }
  } catch (error) {
    console.error('OpenAI insight error:', error);
    openaiInsightOutput.innerHTML = `<p>Terjadi kesalahan saat meminta insight OpenAI: ${error.message}</p>`;
  }
};

const fetchOpenAIStatus = async () => {
  try {
    const response = await fetch('/api/openai-status');
    if (!response.ok) return;

    const statusData = await response.json();
    openaiStatusLabel.textContent = statusData.available ? 'Tersedia' : 'Tidak tersedia';
  } catch (error) {
    console.error('OpenAI status error:', error);
    openaiStatusLabel.textContent = 'Gagal terhubung';
  }
};

const processDataset = async () => {
  if (!datasetInput.files.length) {
    alert('Silakan pilih folder dataset terlebih dahulu.');
    return;
  }

  const files = Array.from(datasetInput.files).filter((file) => file.type.startsWith('image/'));
  if (!files.length) {
    alert('Tidak ada file gambar yang valid dalam folder dataset.');
    return;
  }

  const formData = new FormData();
  files.forEach((file) => formData.append('datasetFiles', file));

  try {
    const response = await fetch('/api/dataset-detection', {
      method: 'POST',
      body: formData,
    });

    const json = await response.json().catch(() => null);

    // Remove previous inline message if any
    const prevMsg = document.getElementById('datasetMessage');
    if (prevMsg) prevMsg.remove();

    if (!response.ok) {
      const message = json?.error || 'Gagal menguji dataset.';
      const p = document.createElement('p');
      p.id = 'datasetMessage';
      p.style.color = '#ff6b6b';
      p.style.marginTop = '8px';
      p.textContent = message;
      datasetSummary.appendChild(p);
      return;
    }

    const data = json;
    // Clear any previous message
    const prev = document.getElementById('datasetMessage');
    if (prev) prev.remove();

    datasetTotal.textContent = data.total;
    datasetAI.textContent = data.aiCount;
    datasetHuman.textContent = data.humanCount;
    datasetUncertain.textContent = data.uncertainCount;
    datasetAccuracy.textContent = `${data.averageAccuracy}%`;
    confusionTrueAI.textContent = `${data.total ? Math.round((data.aiCount / data.total) * 100) : 0}%`;
    confusionFalseAI.textContent = `${data.total ? Math.round((data.humanCount / data.total) * 100) : 0}%`;
    buildDatasetPreview(files, data.results || []);
  } catch (error) {
    console.error(error);
    const p = document.createElement('p');
    p.id = 'datasetMessage';
    p.style.color = '#ff6b6b';
    p.style.marginTop = '8px';
    p.textContent = 'Terjadi kesalahan saat menguji dataset.';
    datasetSummary.appendChild(p);
  }
};

imageInput.addEventListener('change', (event) => {
  const file = event.target.files[0];
  if (!file) return;
  currentFile = file;
  setPreview(file);
});

dropZone.addEventListener('dragover', (event) => {
  event.preventDefault();
  dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (event) => {
  event.preventDefault();
  dropZone.classList.remove('drag-over');
  const files = event.dataTransfer.files;
  if (!files.length) return;

  const dt = new DataTransfer();
  Array.from(files).forEach((file) => dt.items.add(file));
  imageInput.files = dt.files;

  const firstFile = files[0];
  currentFile = firstFile;
  setPreview(firstFile);
});

const analyzeImage = async () => {
  if (!currentFile) {
    alert('Silakan unggah gambar terlebih dahulu.');
    return;
  }

  const formData = new FormData();
  formData.append('image', currentFile);

  try {
    const response = await fetch('/api/upload', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => null);
        const message = error?.error || 'Gagal mengunggah gambar. Pastikan format JPG/PNG.';
        alert(message);
        return;
      }

      const data = await response.json();
      console.log('Upload response data:', data);
      const normalized = normalizeAnalysisData(data);
      lastResult = normalized;
      renderAnalysisDashboard(normalized);
      edgeHeatmap.src = normalized.edgeHeatmapUrl || '';
      loadDetectionHistory();
    } catch (error) {
      console.error('Analyze error:', error);
      alert(`Terjadi kesalahan saat memproses gambar: ${error.message || error}`);
    }
  };
// Event Listeners untuk Tombol Analisis
analyzeButton.addEventListener('click', analyzeImage);
resetButton.addEventListener('click', resetPreview);
downloadReportButton.addEventListener('click', downloadReport);
openaiInsightButton?.addEventListener('click', fetchOpenAIInsight);
exportCsvButton.addEventListener('click', exportCsv);
datasetInput.addEventListener('change', () => buildDatasetPreview(Array.from(datasetInput.files), []));
datasetTestButton.addEventListener('click', processDataset);

// Event Listeners untuk Tombol Hero Section
heroUpload.addEventListener('click', () => {
  imageInput.click();
  setTimeout(() => document.getElementById('detection').scrollIntoView({ behavior: 'smooth' }), 300);
});
heroDetect.addEventListener('click', () => {
  document.getElementById('detection').scrollIntoView({ behavior: 'smooth' });
});
heroLearn.addEventListener('click', () => document.getElementById('sugeno').scrollIntoView({ behavior: 'smooth' }));

// Event Listeners untuk Tombol Navbar
const startDetectionBtn = document.getElementById('startDetection');
const uploadNowBtn = document.getElementById('uploadNow');

if (startDetectionBtn) {
  startDetectionBtn.addEventListener('click', () => {
    document.getElementById('detection').scrollIntoView({ behavior: 'smooth' });
  });
}

if (uploadNowBtn) {
  uploadNowBtn.addEventListener('click', () => {
    imageInput.click();
    setTimeout(() => document.getElementById('detection').scrollIntoView({ behavior: 'smooth' }), 300);
  });
}

// FITUR BARU: Event Listeners untuk Batch Detection
if (batchDropZone) {
  batchDropZone.addEventListener('dragover', (event) => {
    event.preventDefault();
    batchDropZone.classList.add('drag-over');
  });

  batchDropZone.addEventListener('dragleave', () => {
    batchDropZone.classList.remove('drag-over');
  });

  batchDropZone.addEventListener('drop', (event) => {
    event.preventDefault();
    batchDropZone.classList.remove('drag-over');
    const files = event.dataTransfer.files;
    if (!files.length) return;

    const dt = new DataTransfer();
    Array.from(files).forEach((file) => dt.items.add(file));
    batchImageInput.files = dt.files;
  });
}

if (batchImageInput) {
  batchImageInput.addEventListener('change', (event) => {
    // Handle file selection
  });
}

if (batchAnalyzeButton) {
  batchAnalyzeButton.addEventListener('click', processBatchDetection);
}

if (clearHistoryButton) {
  clearHistoryButton.addEventListener('click', clearDetectionHistory);
}

// FITUR BARU: Fungsi untuk Batch Detection
async function processBatchDetection() {
  if (!batchImageInput.files.length) {
    alert('Silakan pilih gambar terlebih dahulu.');
    return;
  }

  const files = Array.from(batchImageInput.files).filter((file) => file.type.startsWith('image/'));
  if (!files.length) {
    alert('Tidak ada file gambar yang valid.');
    return;
  }

  const formData = new FormData();
  files.forEach((file) => formData.append('batchImages', file));

  try {
    const response = await fetch('/api/batch-detection', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => null);
      alert(error?.error || 'Gagal memproses batch detection.');
      return;
    }

    const data = await response.json();
    batchTotal.textContent = data.totalFiles;
    batchAI.textContent = data.aiCount;
    batchHuman.textContent = data.humanCount;
    batchUncertain.textContent = data.uncertainCount;
    batchAvgAccuracy.textContent = `${data.averageAccuracy}%`;

    // Tampilkan hasil
    batchResultsList.innerHTML = data.results
      .map(
        (result) => `
        <div class="batch-result-item" style="padding: 10px; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; margin-bottom: 10px;">
          <p><strong>${result.filename}</strong></p>
          <p>Status: <span style="color: ${result.status === 'AI Generated' ? '#ff6b6b' : '#51cf66'}">${result.status}</span></p>
          <p>Accuracy: ${result.accuracy}%</p>
        </div>
      `
      )
      .join('');

    loadDetectionHistory();
  } catch (error) {
    console.error(error);
    alert('Terjadi kesalahan saat memproses batch detection.');
  }
}

// FITUR BARU: Fungsi untuk Load Detection History
async function loadDetectionHistory() {
  try {
    const response = await fetch('/api/detection-history');
    if (!response.ok) return;

    const data = await response.json();
    const history = data.history || [];
    const stats = data.statistics || {};

    // Update statistik
    historyTotal.textContent = stats.total || 0;
    historyAI.textContent = stats.aiCount || 0;
    historyHuman.textContent = stats.humanCount || 0;
    historyUncertain.textContent = stats.uncertainCount || 0;
    historyAvgAccuracy.textContent = `${stats.averageAccuracy || 0}%`;

    // Update history table
    historyTable.innerHTML = history
      .reverse()
      .slice(0, 20)
      .map(
        (entry) => `
        <tr>
          <td>${new Date(entry.timestamp).toLocaleString('id-ID')}</td>
          <td>${entry.filename}</td>
          <td><span style="color: ${getStatusColor(entry.status)}">${entry.status}</span></td>
          <td>${entry.accuracy}%</td>
        </tr>
      `
      )
      .join('');
  } catch (error) {
    console.error('Error loading detection history:', error);
  }
}

// FITUR BARU: Fungsi untuk Clear Detection History
async function clearDetectionHistory() {
  if (!confirm('Apakah Anda yakin ingin menghapus riwayat deteksi?')) return;

  try {
    const response = await fetch('/api/detection-history/clear', { method: 'POST' });
    if (response.ok) {
      alert('Riwayat deteksi berhasil dihapus.');
      loadDetectionHistory();
    }
  } catch (error) {
    console.error('Error clearing detection history:', error);
    alert('Gagal menghapus riwayat deteksi.');
  }
}

const initParticles = () => {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
  const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  document.getElementById('particles').appendChild(renderer.domElement);

  const geometry = new THREE.BufferGeometry();
  const particleCount = 700;
  const positions = new Float32Array(particleCount * 3);
  const colors = new Float32Array(particleCount * 3);

  for (let i = 0; i < particleCount; i++) {
    const i3 = i * 3;
    positions[i3] = (Math.random() - 0.5) * 120;
    positions[i3 + 1] = (Math.random() - 0.5) * 120;
    positions[i3 + 2] = (Math.random() - 0.5) * 120;
    colors[i3] = 0.41;
    colors[i3 + 1] = 0.75;
    colors[i3 + 2] = 0.99;
  }

  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

  const material = new THREE.PointsMaterial({
    size: 1.5,
    vertexColors: true,
    transparent: true,
    opacity: 0.75,
  });

  const particles = new THREE.Points(geometry, material);
  scene.add(particles);
  camera.position.z = 80;

  const animate = () => {
    requestAnimationFrame(animate);
    particles.rotation.y += 0.0009;
    particles.rotation.x += 0.0007;
    renderer.render(scene, camera);
  };

  animate();
};

const initCharts = () => {
  const entropyContext = document.getElementById('entropyChart');
  const histContext = document.getElementById('histChart');
  const fftContext = document.getElementById('fftChart');
  const glcmContext = document.getElementById('glcmChart');

  entropyChart = new Chart(entropyContext, {
    type: 'doughnut',
    data: {
      labels: ['Entropy', 'Remaining'],
      datasets: [{
        data: [0, 100],
        backgroundColor: ['rgba(109, 230, 255, 0.94)', 'rgba(13, 18, 42, 0.32)'],
        borderWidth: 0,
      }],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
      },
      cutout: '68%',
    },
  });

  fftChart = new Chart(fftContext, {
    type: 'doughnut',
    data: {
      labels: ['High Freq', 'Low Freq'],
      datasets: [{
        data: [0, 100],
        backgroundColor: ['rgba(255, 182, 82, 0.94)', 'rgba(40, 109, 255, 0.30)'],
        borderWidth: 0,
      }],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
      },
      cutout: '68%',
    },
  });

  glcmChart = new Chart(glcmContext, {
    type: 'bar',
    data: {
      labels: ['Contrast', 'Homogeneity', 'Energy', 'Correlation'],
      datasets: [{
        label: 'GLCM',
        data: [0, 0, 0, 0],
        backgroundColor: 'rgba(144, 255, 166, 0.85)',
        borderRadius: 10,
      }],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
      },
      scales: {
        x: { grid: { display: false } },
        y: { grid: { color: 'rgba(255,255,255,0.08)' }, beginAtZero: true },
      },
    },
  });

  histChart = new Chart(histContext, {
    type: 'bar',
    data: {
      labels: ['Brightness', 'Noise', 'Saturation'],
      datasets: [{
        label: 'Image Features',
        data: [0, 0, 0],
        backgroundColor: 'rgba(106, 215, 255, 0.85)',
        borderRadius: 10,
      }],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
      },
      scales: {
        x: { grid: { display: false } },
        y: { grid: { color: 'rgba(255,255,255,0.08)' }, beginAtZero: true },
      },
    },
  });

  // FITUR BARU: Initialize chart untuk Variance Intensity
  const intensityCtx = document.getElementById('intensityChart');
  if (intensityCtx) {
    intensityChart = new Chart(intensityCtx, {
      type: 'line',
      data: {
        labels: Array(20).fill(0).map((_, i) => (i * 5)),
        datasets: [{
          label: 'Intensity Distribution',
          data: Array(20).fill(0),
          borderColor: 'rgba(109, 230, 255, 0.94)',
          backgroundColor: 'rgba(109, 230, 255, 0.1)',
          borderRadius: 5,
          fill: true,
          tension: 0.4,
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: 'rgba(255,255,255,0.08)' }, beginAtZero: true },
        },
      },
    });
  }

  // FITUR BARU: Initialize chart untuk RGB Histogram
  const rgbHistCtx = document.getElementById('rgbHistogram');
  if (rgbHistCtx) {
    rgbHistogramChart = new Chart(rgbHistCtx, {
      type: 'line',
      data: {
        labels: Array(64).fill(0).map((_, i) => (i * 4)),
        datasets: [
          {
            label: 'Red',
            data: Array(64).fill(0),
            borderColor: 'rgba(255, 107, 107, 0.8)',
            backgroundColor: 'rgba(255, 107, 107, 0.1)',
            borderWidth: 2,
            fill: false,
            tension: 0.3,
          },
          {
            label: 'Green',
            data: Array(64).fill(0),
            borderColor: 'rgba(107, 255, 107, 0.8)',
            backgroundColor: 'rgba(107, 255, 107, 0.1)',
            borderWidth: 2,
            fill: false,
            tension: 0.3,
          },
          {
            label: 'Blue',
            data: Array(64).fill(0),
            borderColor: 'rgba(107, 107, 255, 0.8)',
            backgroundColor: 'rgba(107, 107, 255, 0.1)',
            borderWidth: 2,
            fill: false,
            tension: 0.3,
          },
        ],
      },
      options: {
        responsive: true,
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: 'rgba(255,255,255,0.08)' }, beginAtZero: true },
        },
      },
    });
  }

  // FITUR BARU: Initialize chart untuk Grayscale Histogram
  const grayscaleCtx = document.getElementById('grayscaleHistogram');
  if (grayscaleCtx) {
    grayscaleHistogramChart = new Chart(grayscaleCtx, {
      type: 'bar',
      data: {
        labels: Array(64).fill(0).map((_, i) => (i * 4)),
        datasets: [{
          label: 'Grayscale',
          data: Array(64).fill(0),
          backgroundColor: 'rgba(169, 169, 169, 0.85)',
          borderRadius: 5,
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: 'rgba(255,255,255,0.08)' }, beginAtZero: true },
        },
      },
    });
  }

  // FITUR BARU: Initialize chart untuk Red Channel
  const redCtx = document.getElementById('redChannelChart');
  if (redCtx) {
    redChannelChart = new Chart(redCtx, {
      type: 'bar',
      data: {
        labels: Array(64).fill(0).map((_, i) => (i * 4)),
        datasets: [{
          label: 'Red Channel',
          data: Array(64).fill(0),
          backgroundColor: 'rgba(255, 107, 107, 0.85)',
          borderRadius: 5,
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: 'rgba(255,255,255,0.08)' }, beginAtZero: true },
        },
      },
    });
  }

  // FITUR BARU: Initialize chart untuk Green Channel
  const greenCtx = document.getElementById('greenChannelChart');
  if (greenCtx) {
    greenChannelChart = new Chart(greenCtx, {
      type: 'bar',
      data: {
        labels: Array(64).fill(0).map((_, i) => (i * 4)),
        datasets: [{
          label: 'Green Channel',
          data: Array(64).fill(0),
          backgroundColor: 'rgba(107, 255, 107, 0.85)',
          borderRadius: 5,
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: 'rgba(255,255,255,0.08)' }, beginAtZero: true },
        },
      },
    });
  }

  // FITUR BARU: Initialize chart untuk Blue Channel
  const blueCtx = document.getElementById('blueChannelChart');
  if (blueCtx) {
    blueChannelChart = new Chart(blueCtx, {
      type: 'bar',
      data: {
        labels: Array(64).fill(0).map((_, i) => (i * 4)),
        datasets: [{
          label: 'Blue Channel',
          data: Array(64).fill(0),
          backgroundColor: 'rgba(107, 107, 255, 0.85)',
          borderRadius: 5,
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: 'rgba(255,255,255,0.08)' }, beginAtZero: true },
        },
      },
    });
  }
};

function updateCharts(data) {
  if (entropyChart) {
    entropyChart.data.datasets[0].data = [data.entropy, Math.max(0, 8 - data.entropy)];
    entropyChart.update();
  }

  if (fftChart) {
    fftChart.data.datasets[0].data = [data.fftHighFreqRatio, Math.max(0, 100 - data.fftHighFreqRatio)];
    fftChart.update();
  }

  if (glcmChart) {
    glcmChart.data.datasets[0].data = [data.glcmContrast, data.glcmHomogeneity, data.glcmEnergy, data.glcmCorrelation];
    glcmChart.update();
  }

  if (histChart) {
    histChart.data.datasets[0].data = [data.brightness, data.noise, data.saturation];
    histChart.update();
  }

  // FITUR BARU: Update visualisasi analisis citra
  updateVarianceIntensity(data);
  updateHistogramAnalysis(data);
  updateRGBChannels(data);
};

// FITUR BARU: Fungsi untuk update Variance Intensity
function updateVarianceIntensity(data) {
  if (data.varianceIntensity) {
    const vi = data.varianceIntensity;
    document.getElementById('varianceMean').textContent = vi.mean.toFixed(2);
    document.getElementById('varianceValue').textContent = vi.variance.toFixed(2);
    document.getElementById('varianceStd').textContent = vi.std.toFixed(2);
    document.getElementById('varianceContrast').textContent = vi.contrastLevel.toFixed(1);
    document.getElementById('q25').textContent = vi.q25.toFixed(0);
    document.getElementById('q50').textContent = vi.q50.toFixed(0);
    document.getElementById('q75').textContent = vi.q75.toFixed(0);
    document.getElementById('intensityRange').textContent = vi.range.toFixed(2);

    // Update intensity chart
    if (intensityChart) {
      const histogram = data.histogramAnalysis?.histogram || [];
      const intensityData = histogram.slice(0, 20).map((value) => Number(value));
      intensityChart.data.datasets[0].data = intensityData.length ? intensityData : Array(20).fill(0);
      intensityChart.update();
    }
  }
};

// FITUR BARU: Fungsi untuk update Histogram Analysis
function updateHistogramAnalysis(data) {
  if (data.histogramAnalysis) {
    const ha = data.histogramAnalysis;
    document.getElementById('histLeft').textContent = ha.leftDistribution.toFixed(1);
    document.getElementById('histMiddle').textContent = ha.middleDistribution.toFixed(1);
    document.getElementById('histRight').textContent = ha.rightDistribution.toFixed(1);
    document.getElementById('histPeak').textContent = ha.peakBin;

    // Update RGB histogram
    if (rgbHistogramChart && data.rgbChannels) {
      const rgb = data.rgbChannels;
      rgbHistogramChart.data.datasets[0].data = rgb.redHistogram.slice(0, 64);
      rgbHistogramChart.data.datasets[1].data = rgb.greenHistogram.slice(0, 64);
      rgbHistogramChart.data.datasets[2].data = rgb.blueHistogram.slice(0, 64);
      rgbHistogramChart.update();
    }

    // Update grayscale histogram
    if (grayscaleHistogramChart) {
      grayscaleHistogramChart.data.datasets[0].data = ha.histogram.slice(0, 64);
      grayscaleHistogramChart.update();
    }
  }
};

// FITUR BARU: Fungsi untuk update RGB Channels
function updateRGBChannels(data) {
  if (data.rgbChannels) {
    const rgb = data.rgbChannels;
    document.getElementById('redMean').textContent = rgb.redMean.toFixed(0);
    document.getElementById('greenMean').textContent = rgb.greenMean.toFixed(0);
    document.getElementById('blueMean').textContent = rgb.blueMean.toFixed(0);
    document.getElementById('redStd').textContent = rgb.redStd.toFixed(2);
    document.getElementById('greenStd').textContent = rgb.greenStd.toFixed(2);
    document.getElementById('blueStd').textContent = rgb.blueStd.toFixed(2);

    // Update RGB channel charts
    if (redChannelChart) {
      redChannelChart.data.datasets[0].data = rgb.redHistogram.slice(0, 64);
      redChannelChart.update();
    }
    if (greenChannelChart) {
      greenChannelChart.data.datasets[0].data = rgb.greenHistogram.slice(0, 64);
      greenChannelChart.update();
    }
    if (blueChannelChart) {
      blueChannelChart.data.datasets[0].data = rgb.blueHistogram.slice(0, 64);
      blueChannelChart.update();
    }
  }
};

window.addEventListener('load', () => {
  initCharts();
  fetchOpenAIStatus();
  // FITUR BARU: Load detection history pada startup
  loadDetectionHistory();
});

window.addEventListener('resize', () => {
  const canvas = document.querySelector('#particles canvas');
  if (canvas) {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
});
