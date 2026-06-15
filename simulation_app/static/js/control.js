const API_URL = "/api";

const machineSelect = document.getElementById('machine-select');
const failureSelect = document.getElementById('failure-select');
const btnInject = document.getElementById('btn-inject');
const btnResolve = document.getElementById('btn-resolve');
const chartsContainer = document.getElementById('charts-container');
const statusMsg = document.getElementById('status-msg');

let failureModes = {};
let selectedMachine = null;
let charts = {};
let chartData = {}; // { sensor_name: [val1, val2, ...] }
const MAX_POINTS = 50;

async function init() {
    try {
        const response = await fetch(`${API_URL}/plant_config`);
        const data = await response.json();
        
        failureModes = data.failure_modes;
        
        // Populate machines
        data.machines.forEach(m => {
            const opt = document.createElement('option');
            opt.value = m.machine_id;
            opt.textContent = `${m.alias} - ${m.label}`;
            machineSelect.appendChild(opt);
        });
        
        // Load vision data
        loadVisionData();
        
        setInterval(pollData, 1000);
    } catch (err) {
        console.error("Failed to init control:", err);
    }
}

machineSelect.addEventListener('change', (e) => {
    selectedMachine = e.target.value;
    failureSelect.innerHTML = '<option value="">-- Select Failure --</option>';
    
    if (selectedMachine) {
        failureSelect.disabled = false;
        if (failureModes[selectedMachine]) {
            failureModes[selectedMachine].forEach(f => {
                const opt = document.createElement('option');
                opt.value = f;
                opt.textContent = f;
                failureSelect.appendChild(opt);
            });
        }
        setupCharts();
    } else {
        failureSelect.disabled = true;
        btnInject.disabled = true;
        chartsContainer.innerHTML = '<div style="color: var(--text-muted); text-align: center; padding: 2rem;">Select a machine to view raw telemetry streams.</div>';
        charts = {};
        chartData = {};
    }
});

failureSelect.addEventListener('change', (e) => {
    btnInject.disabled = !e.target.value;
});

btnInject.addEventListener('click', async () => {
    const failure = failureSelect.value;
    if (!selectedMachine || !failure) return;
    
    try {
        const response = await fetch(`${API_URL}/inject_failure`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ machine_id: selectedMachine, failure_mode: failure })
        });
        const result = await response.json();
        statusMsg.textContent = result.message;
        setTimeout(() => statusMsg.textContent = '', 3000);
    } catch (err) {}
});

btnResolve.addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_URL}/resolve_failures`, { method: 'POST' });
        const result = await response.json();
        statusMsg.textContent = result.message;
        setTimeout(() => statusMsg.textContent = '', 3000);
    } catch (err) {}
});

function setupCharts() {
    chartsContainer.innerHTML = '';
    charts = {};
    chartData = {};
}

async function pollData() {
    if (!selectedMachine) return;
    
    try {
        const response = await fetch(`${API_URL}/live_data`);
        const data = await response.json();
        
        const machineData = data.telemetry[selectedMachine];
        if (!machineData) return;
        
        const sensors = machineData.sensors;
        
        // Build chart containers if they don't exist
        if (Object.keys(charts).length === 0) {
            Object.keys(sensors).forEach(sensorName => {
                const box = document.createElement('div');
                box.className = 'chart-box';
                
                const title = document.createElement('h3');
                title.style.fontSize = '1rem';
                title.style.marginBottom = '1rem';
                title.textContent = `Signal: ${sensorName.toUpperCase()}`;
                box.appendChild(title);
                
                const canvasWrap = document.createElement('div');
                canvasWrap.style.height = '280px';
                canvasWrap.style.width = '100%';
                
                const canvas = document.createElement('canvas');
                canvas.id = `chart-${sensorName}`;
                canvasWrap.appendChild(canvas);
                
                box.appendChild(canvasWrap);
                chartsContainer.appendChild(box);
                
                const ctx = canvas.getContext('2d');
                chartData[sensorName] = Array(MAX_POINTS).fill(sensors[sensorName]);
                
                charts[sensorName] = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: Array(MAX_POINTS).fill(''),
                        datasets: [{
                            label: 'Raw Signal',
                            data: chartData[sensorName],
                            borderColor: '#3b82f6',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            borderWidth: 2,
                            tension: 0.1,
                            fill: true,
                            pointRadius: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: false,
                        scales: {
                            x: { display: false },
                            y: { 
                                display: true,
                                grid: { color: 'rgba(255,255,255,0.05)' }
                            }
                        },
                        plugins: { legend: { display: false } }
                    }
                });
            });
        }
        
        // Update charts with new data
        Object.keys(sensors).forEach(sensorName => {
            const val = sensors[sensorName];
            chartData[sensorName].push(val);
            chartData[sensorName].shift();
            
            const arr = chartData[sensorName];
            const avg = arr.reduce((a,b)=>a+b,0) / arr.length;
            const diff = Math.abs((val - avg) / avg);
            
            const chart = charts[sensorName];
            chart.data.datasets[0].data = chartData[sensorName];
            
            if (diff > 0.15) {
                chart.data.datasets[0].borderColor = '#ef4444';
                chart.data.datasets[0].backgroundColor = 'rgba(239, 68, 68, 0.1)';
            } else {
                chart.data.datasets[0].borderColor = '#3b82f6';
                chart.data.datasets[0].backgroundColor = 'rgba(59, 130, 246, 0.1)';
            }
            
            chart.update();
        });
        
    } catch (err) {}
}

// ===== VISION / PPE SAFETY CAMERA =====

async function loadVisionData() {
    try {
        // Load camera zones
        const camRes = await fetch(`${API_URL}/vision/cameras`);
        const camData = await camRes.json();
        const camSelect = document.getElementById('camera-zone-select');
        camSelect.innerHTML = '<option value="">-- Select Camera Zone --</option>';
        (camData.cameras || []).forEach(cam => {
            const opt = document.createElement('option');
            opt.value = cam.zone;
            opt.textContent = cam.zone;
            camSelect.appendChild(opt);
        });
        
        // Load available images
        const imgRes = await fetch(`${API_URL}/vision/images`);
        const imgData = await imgRes.json();
        const imgSelect = document.getElementById('camera-image-select');
        imgSelect.innerHTML = '<option value="">-- Select Image --</option>';
        (imgData.images || []).forEach(img => {
            const opt = document.createElement('option');
            opt.value = img.name;
            opt.textContent = `${img.name} (${img.size_kb} KB)`;
            imgSelect.appendChild(opt);
        });
    } catch (err) {
        console.error("Failed to load vision data:", err);
    }
}

document.getElementById('btn-analyze').addEventListener('click', async () => {
    const cameraZone = document.getElementById('camera-zone-select').value;
    const imageName = document.getElementById('camera-image-select').value;
    
    if (!imageName) {
        document.getElementById('vision-status').innerHTML = '<span style="color:var(--color-danger);"><i class="fa-solid fa-exclamation-circle"></i> Please select an image to analyze.</span>';
        return;
    }
    
    const zone = cameraZone || 'Unspecified Zone';
    const resultsContainer = document.getElementById('vision-results');
    const statusEl = document.getElementById('vision-status');
    const detectionsEl = document.getElementById('vision-detections');
    
    // Show loading
    statusEl.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin" style="color:var(--color-primary);"></i> Running YOLO inference on image...';
    resultsContainer.innerHTML = `<div style="text-align:center; padding:3rem;"><i class="fa-solid fa-circle-notch fa-spin fa-3x" style="color:var(--color-primary);"></i><p style="margin-top:1rem; color:var(--text-muted);">Running PPE detection model...</p></div>`;
    detectionsEl.innerHTML = '';
    
    try {
        const response = await fetch(`${API_URL}/vision/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image_name: imageName, camera_zone: zone })
        });
        const report = await response.json();
        
        if (report.error) {
            statusEl.innerHTML = `<span style="color:var(--color-danger);"><i class="fa-solid fa-circle-xmark"></i> ${report.error}</span>`;
            return;
        }
        
        // Update status
        const compliant = report.compliant;
        const methodIcon = report.analysis_method === 'YOLO' ? 'fa-crosshairs' : (report.analysis_method === 'LLM' ? 'fa-brain' : 'fa-question-circle');
        const methodLabel = report.analysis_method === 'YOLO' ? 'YOLOv8 Detection' : (report.analysis_method === 'LLM' ? 'LLM Vision Analysis' : 'Heuristic');
        statusEl.innerHTML = `
            <div class="compliance-badge ${compliant ? 'compliant' : 'violation'}">
                <i class="fa-solid ${compliant ? 'fa-shield-check' : 'fa-triangle-exclamation'}"></i>
                ${compliant ? 'COMPLIANT' : 'VIOLATIONS DETECTED'}
            </div>
            <div style="margin-top:0.6rem; font-size:0.78rem; color:var(--text-muted);">
                <div><i class="fa-solid ${methodIcon}" style="margin-right:0.3rem;"></i><strong>Method:</strong> ${methodLabel}</div>
                <div><strong>Zone:</strong> ${report.camera_zone}</div>
                <div><strong>Time:</strong> ${report.timestamp}</div>
                ${report.incident_created ? `<div style="color:var(--color-danger); margin-top:0.4rem;"><i class="fa-solid fa-triangle-exclamation"></i> Safety incident <strong>${report.incident_id}</strong> created!</div>` : ''}
            </div>
        `;
        
        // PPE status
        let ppeHtml = '<div class="detection-list">';
        const ppeItems = report.ppe_status || {};
        for (const [item, present] of Object.entries(ppeItems)) {
            ppeHtml += `
                <div class="detection-item ${present ? 'safe' : 'unsafe'}">
                    <span><i class="fa-solid ${present ? 'fa-circle-check' : 'fa-circle-xmark'}" style="color:${present ? 'var(--color-success)' : 'var(--color-danger)'};margin-right:0.4rem;"></i>${item.toUpperCase()}</span>
                    <span style="font-weight:600;color:${present ? 'var(--color-success)' : 'var(--color-danger)'};">${present ? 'Present' : 'MISSING'}</span>
                </div>
            `;
        }
        ppeHtml += '</div>';
        detectionsEl.innerHTML = ppeHtml;
        
        // Results panel — show annotated image
        const annotatedUrl = report.annotated_image ? `/api/document/${report.annotated_image}` : `/api/document/OpenCV/${imageName}`;
        const originalUrl = `/api/document/OpenCV/${imageName}`;
        
        resultsContainer.innerHTML = `
            <div style="display:flex;flex-direction:column;gap:1rem;">
                <div style="display:flex;gap:1rem;align-items:center;margin-bottom:0.5rem;">
                    <h3 style="font-size:0.95rem;"><i class="fa-solid fa-image" style="color:var(--color-primary);margin-right:0.4rem;"></i>Detection Results</h3>
                    <span style="font-size:0.75rem;color:var(--text-muted);">${report.violations_count || 0} violation(s) found</span>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
                    <div>
                        <p style="font-size:0.72rem;color:var(--text-muted);margin-bottom:0.4rem;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">Original Image</p>
                        <img src="${originalUrl}" class="vision-image-preview" alt="Original" />
                    </div>
                    <div>
                        <p style="font-size:0.72rem;color:var(--text-muted);margin-bottom:0.4rem;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">AI Detection (Annotated)</p>
                        <img src="${annotatedUrl}" class="vision-image-preview" alt="Annotated" />
                    </div>
                </div>
                ${!compliant ? `
                <div style="background:var(--color-danger-dim);border:1px solid rgba(239,68,68,0.3);border-radius:var(--radius-sm);padding:1rem;margin-top:0.5rem;">
                    <div style="font-weight:700;color:var(--color-danger);margin-bottom:0.4rem;"><i class="fa-solid fa-triangle-exclamation"></i> PPE Violations Detected</div>
                    <div style="font-size:0.82rem;color:var(--text-secondary);">Missing PPE: <strong>${(report.missing_ppe || []).join(', ')}</strong></div>
                    <div style="font-size:0.78rem;color:var(--text-muted);margin-top:0.3rem;">A safety incident has been automatically created. Switch to the main dashboard's Incident tab to manage it.</div>
                </div>` : `
                <div style="background:var(--color-success-dim);border:1px solid rgba(16,185,129,0.3);border-radius:var(--radius-sm);padding:1rem;margin-top:0.5rem;">
                    <div style="font-weight:700;color:var(--color-success);"><i class="fa-solid fa-shield-check"></i> All Clear — PPE Compliance Verified</div>
                    <div style="font-size:0.82rem;color:var(--text-secondary);margin-top:0.3rem;">All personnel in the camera feed are wearing required PPE.</div>
                </div>`}
                ${report.llm_summary ? `
                <div style="background:rgba(139,92,246,0.06);border:1px solid rgba(139,92,246,0.2);border-radius:var(--radius-sm);padding:0.8rem;margin-top:0.5rem;">
                    <div style="font-size:0.72rem;font-weight:700;color:var(--color-purple);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:0.4rem;"><i class="fa-solid fa-brain"></i> AI Vision Analysis</div>
                    <div style="font-size:0.82rem;color:var(--text-secondary);">${report.llm_summary}</div>
                    ${report.hazards_noted && report.hazards_noted !== 'None detected' ? `<div style="font-size:0.78rem;color:var(--color-warning);margin-top:0.3rem;"><i class="fa-solid fa-exclamation-triangle"></i> Hazards: ${report.hazards_noted}</div>` : ''}
                </div>` : ''}
            </div>
        `;
    } catch (err) {
        statusEl.innerHTML = `<span style="color:var(--color-danger);"><i class="fa-solid fa-circle-xmark"></i> Analysis failed: ${err.message}</span>`;
        console.error("Vision analysis error:", err);
    }
});

init();
