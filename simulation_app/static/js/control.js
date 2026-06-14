const API_URL = "http://127.0.0.1:5000/api";

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
    
    // We don't know the exact sensors yet until the first poll, 
    // so the first poll for the selected machine will build the canvas elements.
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
                
                // Add title
                const title = document.createElement('h3');
                title.style.fontSize = '1rem';
                title.style.marginBottom = '1rem';
                title.textContent = `Signal: ${sensorName.toUpperCase()}`;
                box.appendChild(title);
                
                // Add canvas container
                const canvasWrap = document.createElement('div');
                canvasWrap.style.height = '280px';
                canvasWrap.style.width = '100%';
                
                const canvas = document.createElement('canvas');
                canvas.id = `chart-${sensorName}`;
                canvasWrap.appendChild(canvas);
                
                box.appendChild(canvasWrap);
                chartsContainer.appendChild(box);
                
                // Init Chart.js
                const ctx = canvas.getContext('2d');
                chartData[sensorName] = Array(MAX_POINTS).fill(sensors[sensorName]); // fill with current val
                
                charts[sensorName] = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: Array(MAX_POINTS).fill(''),
                        datasets: [
                            {
                                label: 'Raw Signal',
                                data: chartData[sensorName],
                                borderColor: '#3b82f6',
                                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                                borderWidth: 2,
                                tension: 0.1,
                                fill: true,
                                pointRadius: 0
                            }
                        ]
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
            
            // Deflection visual cue (turn line red if value deviates heavily from moving avg)
            const arr = chartData[sensorName];
            const avg = arr.reduce((a,b)=>a+b,0) / arr.length;
            const diff = Math.abs((val - avg) / avg);
            
            const chart = charts[sensorName];
            chart.data.datasets[0].data = chartData[sensorName];
            
            if (diff > 0.15) {
                chart.data.datasets[0].borderColor = '#ef4444'; // Red for anomaly
                chart.data.datasets[0].backgroundColor = 'rgba(239, 68, 68, 0.1)';
            } else {
                chart.data.datasets[0].borderColor = '#3b82f6'; // Normal blue
                chart.data.datasets[0].backgroundColor = 'rgba(59, 130, 246, 0.1)';
            }
            
            chart.update();
        });
        
    } catch (err) {}
}

init();
