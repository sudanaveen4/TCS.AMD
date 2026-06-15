const API_URL = "/api";

let machineConfig = [];
let failureModes = {};
let selectedMachine = null;
let miniCharts = {};

// DOM Elements
const markersContainer = document.getElementById('machine-markers');
const healthCardsContainer = document.getElementById('health-cards');
const alertsContainer = document.getElementById('alerts-container');
const activeAlertsCount = document.getElementById('active-alerts-count');
const alertBadge = document.getElementById('alert-badge');

let shiftStartTime = Date.now();
let shiftCycle = 'day';
const SHIFT_DURATION_MS = 5 * 60 * 1000;
const SIMULATED_SHIFT_HOURS = 12;

function getIcon(alias) {
    const icons = {
        "M1": "fa-angles-right",
        "M2": "fa-gear",
        "M3": "fa-water",
        "M4": "fa-wind",
        "M5": "fa-cube"
    };
    return icons[alias] || "fa-server";
}

async function init() {
    try {
        const response = await fetch(`${API_URL}/plant_config`);
        const data = await response.json();
        
        machineConfig = data.machines;
        failureModes = data.failure_modes;
        
        populateUI();
        setInterval(pollData, 1000);
        setInterval(updateShiftClock, 1000);
        
        // Dynamically load GPU info from the backend status endpoint
        fetch(`${API_URL}/status`)
            .then(res => res.json())
            .then(statusData => {
                if (statusData.gpu) {
                    const footerGpu = document.getElementById('gpu-status-footer');
                    if (footerGpu) {
                        footerGpu.innerHTML = `<i class="fa-solid fa-server"></i> GPU: ${statusData.gpu}`;
                    }
                }
            })
            .catch(err => console.error("Failed to load GPU status:", err));
            
    } catch (err) {
        console.error("Failed to init:", err);
    }
}

function populateUI() {
    markersContainer.innerHTML = '';
    healthCardsContainer.innerHTML = '';
    
    machineConfig.forEach(m => {
        // Map Marker
        const marker = document.createElement('div');
        marker.className = 'machine-node';
        marker.id = `marker-${m.machine_id}`;
        marker.style.left = `${m.x}%`;
        marker.style.top = `${m.y}%`;
        marker.innerHTML = `
            <div class="m-icon"><i class="fa-solid ${getIcon(m.alias)}"></i></div>
            <div class="m-id">${m.alias}</div>
            <div class="m-label">${m.label}</div>
        `;
        markersContainer.appendChild(marker);
        
        // Health Card
        const card = document.createElement('div');
        card.className = 'health-card';
        card.id = `health-${m.machine_id}`;
        card.innerHTML = `
            <div class="hc-header">
                <div class="hc-title">
                    <div class="hc-dot" id="dot-${m.machine_id}"></div>
                    <div class="hc-title-text">
                        <h4>${m.alias}</h4>
                        <p>${m.label}</p>
                    </div>
                </div>
                <i class="fa-solid fa-ellipsis-vertical hc-menu"></i>
            </div>
            <div class="hc-score">
                <span>Health</span>
                <h3 id="score-${m.machine_id}">100%</h3>
            </div>
            <div class="hc-chart">
                <canvas id="chart-${m.machine_id}"></canvas>
            </div>
            <div class="hc-metrics" id="metrics-${m.machine_id}"></div>
        `;
        healthCardsContainer.appendChild(card);
        initMiniChart(m.machine_id);
    });
}

function initMiniChart(m_id) {
    const ctx = document.getElementById(`chart-${m_id}`).getContext('2d');
    Chart.defaults.color = '#94a3b8';
    miniCharts[m_id] = new Chart(ctx, {
        type: 'line',
        data: { labels: Array(20).fill(''), datasets: [{ data: Array(20).fill(0), borderColor: '#f59e0b', borderWidth: 1.5, tension: 0.4, pointRadius: 0 }] },
        options: {
            responsive: true, maintainAspectRatio: false, animation: false,
            plugins: { legend: { display: false }, tooltip: { enabled: false } },
            scales: { x: { display: false }, y: { display: false, min: -2, max: 2 } }
        }
    });
}

// ===== DATA POLLING =====
async function pollData() {
    try {
        const response = await fetch(`${API_URL}/live_data`);
        const data = await response.json();
        
        updateMapStatus(data.machine_status);
        updateAlerts(data.alerts);
        updateHealthCards(data.telemetry, data.machine_status);
        
        if (document.getElementById('nav-incidents')?.classList.contains('active')) {
            fetchIncidents();
        }
    } catch (err) {}
}

function updateMapStatus(statusDict) {
    Object.keys(statusDict).forEach(m_id => {
        const marker = document.getElementById(`marker-${m_id}`);
        if (marker) {
            marker.classList.toggle('alert', statusDict[m_id] === 'alert');
        }
    });
}

function updateAlerts(alertsList) {
    activeAlertsCount.textContent = alertsList.length;
    if (alertBadge) alertBadge.textContent = alertsList.length;
    
    if (alertsList.length === 0) {
        alertsContainer.innerHTML = '<div class="empty-state">All systems optimal.</div>';
    } else {
        alertsContainer.innerHTML = '';
        alertsList.forEach(alert => {
            const mConfig = machineConfig.find(m => m.machine_id === alert.machine_id);
            const alias = mConfig ? mConfig.alias : alert.machine_id;
            const el = document.createElement('div');
            el.className = 'alert-item critical';
            el.innerHTML = `
                <div class="alert-header">
                    <span class="alert-tag critical">CRITICAL</span>
                    <span class="alert-time">${alert.timestamp}</span>
                </div>
                <div class="alert-title">${alias} - Anomaly Detected</div>
                <div class="alert-desc">${alert.sensor.replace('_', ' ')} = ${alert.value}</div>
                <div class="alert-desc" style="color: #fca5a5; font-size: 0.7rem; margin-top: 4px;">
                    <i class="fa-solid fa-microchip"></i> Detected by: ${alert.detected_by}
                </div>
                <div class="alert-slm"><i class="fa-solid fa-robot"></i> ${alert.slm_analysis}</div>
            `;
            alertsContainer.appendChild(el);
        });
    }
    
    // Update sidebar incidents panel
    const incidentsContainer = document.getElementById('incidents-container');
    if (incidentsContainer) {
        incidentsContainer.innerHTML = '';
        if (alertsList.length === 0) {
            incidentsContainer.innerHTML = '<div style="padding: 1rem; font-size: 0.8rem; color: var(--text-muted);">No active incidents.</div>';
        } else {
            alertsList.forEach(alert => {
                const inc = document.createElement('div');
                inc.style.cssText = 'padding:0.8rem;border-bottom:1px solid var(--panel-border);';
                inc.innerHTML = `
                    <div style="font-size:0.8rem;font-weight:bold;color:var(--color-danger);"><i class="fa-solid fa-triangle-exclamation"></i> ${alert.machine_id}</div>
                    <div style="font-size:0.75rem;color:var(--text-muted);margin-top:4px;">Sensor: ${alert.sensor} at ${alert.timestamp}</div>
                `;
                incidentsContainer.appendChild(inc);
            });
        }
    }
    
    // Update Full Alerts View
    const fullAlertsContainer = document.getElementById('full-alerts-container');
    if (fullAlertsContainer) {
        fullAlertsContainer.innerHTML = '';
        if (alertsList.length === 0) {
            fullAlertsContainer.innerHTML = '<div class="empty-state">No historical alerts found.</div>';
        } else {
            alertsList.forEach(alert => {
                const mConfig = machineConfig.find(m => m.machine_id === alert.machine_id);
                const alias = mConfig ? mConfig.alias : alert.machine_id;
                const el = document.createElement('div');
                el.className = 'alert-item critical';
                el.innerHTML = `
                    <div class="alert-header">
                        <span class="alert-tag critical">CRITICAL</span>
                        <span class="alert-time">${alert.timestamp}</span>
                    </div>
                    <div class="alert-title">${alias} - Anomaly Detected</div>
                    <div class="alert-desc">${alert.sensor.replace('_', ' ')} = ${alert.value}</div>
                    <div class="alert-slm"><i class="fa-solid fa-robot"></i> ${alert.slm_analysis}</div>
                `;
                fullAlertsContainer.appendChild(el);
            });
        }
    }
}

// ===== INITIALIZATION =====
async function fetchConfig() {
    try {
        const res = await fetch(`${API_URL}/plant_config`);
        const config = await res.json();
        
        // Populate failures in ontology select
        const ontSelect = document.getElementById('ontology-failure-select');
        if (ontSelect && config.failure_modes) {
            ontSelect.innerHTML = '';
            for (const [mId, modes] of Object.entries(config.failure_modes)) {
                modes.forEach(m => {
                    const opt = document.createElement('option');
                    opt.value = m;
                    opt.innerText = `[${mId}] ${m}`;
                    ontSelect.appendChild(opt);
                });
            }
        }
    } catch(e) { console.error("Config load error:", e); }
}

// ===== INCIDENT TRACKING =====
async function fetchIncidents() {
    try {
        const response = await fetch(`${API_URL}/incidents`);
        const data = await response.json();
        
        const container = document.getElementById('full-incidents-container');
        if (!container) return;
        
        container.innerHTML = '';
        if (!data.incidents || data.incidents.length === 0) {
            container.innerHTML = '<div style="padding:1rem;color:var(--text-muted);">No recorded incidents. Inject a failure from the Simulation Controller to trigger one.</div>';
            return;
        }
        
        data.incidents.sort((a,b) => new Date(b.start_time) - new Date(a.start_time));
        
        data.incidents.forEach(inc => {
            const completedTasks = (inc.tasks || []).filter(t => t.status === 'completed').length;
            const totalTasks = (inc.tasks || []).length;
            const progressPct = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
            
            const el = document.createElement('div');
            el.style.cssText = `padding:1rem;background:rgba(255,255,255,0.03);border-radius:8px;border-left:4px solid ${inc.status === 'open' ? 'var(--color-danger)' : 'var(--color-success)'};cursor:pointer;transition:background 0.2s;`;
            el.onmouseenter = () => el.style.background = 'rgba(255,255,255,0.07)';
            el.onmouseleave = () => el.style.background = 'rgba(255,255,255,0.03)';
            el.onclick = () => openSipocModal(inc.id);
            
            el.innerHTML = `
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
                    <div style="font-size:1.1rem;font-weight:bold;color:${inc.status === 'open' ? 'var(--color-danger)' : 'var(--color-success)'};">
                        <i class="fa-solid fa-triangle-exclamation"></i> ${inc.id} (${inc.machine_id})
                    </div>
                    <span class="badge ${inc.status === 'open' ? 'red' : 'green'}">${inc.status.toUpperCase()}</span>
                </div>
                <div style="color:var(--text-muted);margin-bottom:0.5rem;">
                    Failure: <strong>${inc.failure_mode}</strong> | Started: <strong>${inc.start_time}</strong>
                </div>
                <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.3rem;">
                    <div style="flex-grow:1;background:rgba(255,255,255,0.1);border-radius:4px;height:6px;overflow:hidden;">
                        <div style="width:${progressPct}%;height:100%;background:${progressPct === 100 ? 'var(--color-success)' : 'var(--color-primary)'};transition:width 0.5s;"></div>
                    </div>
                    <span style="font-size:0.8rem;color:var(--text-muted);">${completedTasks}/${totalTasks} tasks</span>
                </div>
                <div style="font-size:0.8rem;color:var(--color-primary);"><i class="fa-solid fa-diagram-project"></i> Click to view SIPOC Workflow & Tasks</div>
            `;
            container.appendChild(el);
        });
    } catch(e) { console.error("Failed to fetch incidents:", e); }
}

// ===== SIPOC MODAL =====
async function openSipocModal(incident_id) {
    try {
        const response = await fetch(`${API_URL}/incident/${incident_id}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const inc = await response.json();
        
        if (inc.error) {
            alert(`Incident not found: ${incident_id}`);
            return;
        }
        
        document.getElementById('sipoc-title').textContent = `Workflow: ${inc.id} — ${inc.failure_mode}`;
        
        const container = document.getElementById('sipoc-dag-container');
        container.innerHTML = '';
        
        // Status header
        const statusHeader = document.createElement('div');
        const completedCount = (inc.tasks || []).filter(t => t.status === 'completed').length;
        const totalCount = (inc.tasks || []).length;
        statusHeader.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:center;padding:0.5rem 0;border-bottom:1px solid var(--panel-border);margin-bottom:1rem;">
                <div>
                    <span class="badge ${inc.status === 'open' ? 'red' : 'green'}" style="font-size:0.8rem;">${inc.status.toUpperCase()}</span>
                    <span style="margin-left:1rem;color:var(--text-muted);">Machine: <strong>${inc.machine_id}</strong> | Started: ${inc.start_time}</span>
                </div>
                <div style="color:var(--text-muted);">Progress: <strong>${completedCount}/${totalCount}</strong> tasks complete</div>
            </div>
        `;
        container.appendChild(statusHeader);
        
        // Task cards
        if (!inc.tasks || inc.tasks.length === 0) {
            container.innerHTML += '<div style="padding:1rem;color:var(--text-muted);">No tasks generated for this incident.</div>';
        } else {
            inc.tasks.forEach((t, idx) => {
                const statusColor = t.status === 'completed' ? 'var(--color-success)' : (t.status === 'in_progress' ? 'var(--color-warning)' : '#666');
                const statusIcon = t.status === 'completed' ? 'fa-circle-check' : (t.status === 'in_progress' ? 'fa-spinner fa-spin' : 'fa-circle');
                
                let actionHtml = '';
                if (t.status === 'pending' || t.status === 'in_progress') {
                    if (t.type === 'automated') {
                        actionHtml = `<span style="color:var(--color-warning);"><i class="fa-solid fa-robot"></i> Automated (Running...)</span>`;
                    } else {
                        actionHtml = `
                        <div style="display:flex; gap:0.5rem;">
                            <input type="text" id="review-${t.id}" class="btn-outline" style="flex-grow:1; background:var(--bg-dark); color:white; border-radius:4px; padding:0.4rem;" placeholder="Add review/closure notes...">
                            <button class="btn-primary" onclick="resolveTask('${inc.id}', '${t.id}')">Complete</button>
                        </div>`;
                    }
                } else {
                    actionHtml = `<span style="color:var(--color-success);"><i class="fa-solid fa-check-circle"></i> Completed</span>`;
                    if (t.review_note) {
                        actionHtml += `<div style="color:var(--text-muted); font-size:0.85rem; margin-top:0.3rem;"><em>Note: ${t.review_note}</em></div>`;
                    }
                }
                
                // Check if this task has an associated image (PPE safety incidents)
                let imageHtml = '';
                if (t.image_path) {
                    imageHtml = `
                    <div style="margin:0.8rem 0; padding:0.8rem; background:#080c16; border-radius:8px; border:1px solid var(--panel-border);">
                        <div style="font-size:0.75rem; color:var(--text-muted); margin-bottom:0.5rem; font-weight:600; text-transform:uppercase;"><i class="fa-solid fa-camera"></i> AI Detection Image — Review Required</div>
                        <img src="${API_URL}/document/${t.image_path}" style="width:100%; max-height:300px; object-fit:contain; border-radius:6px; border:1px solid var(--panel-border);" alt="Detection Image" />
                        ${t.original_image_path ? `<div style="margin-top:0.5rem;"><a href="${API_URL}/document/${t.original_image_path}" target="_blank" style="color:var(--color-primary); font-size:0.75rem;"><i class="fa-solid fa-external-link"></i> View Original Image</a></div>` : ''}
                    </div>`;
                }

                const sipoc = t.sipoc || {};
                const inputVal = sipoc.Input || t.inputs || '-';
                const processVal = sipoc.Process || t.procedure || t.process || '-';
                const outputVal = sipoc.Output || t.outputs || '-';
                
                const taskTypeDisplay = t.type === 'manual' ? (t.assigned_to || 'Manual').toUpperCase() : (t.type || 'auto').toUpperCase();

                const taskEl = document.createElement('div');
                taskEl.className = 'panel';
                taskEl.style.cssText = `padding:1rem;border-left:4px solid ${statusColor};margin-bottom:0.5rem;`;
                
                taskEl.innerHTML = `
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <h3 style="font-size:1rem;"><i class="fa-solid ${statusIcon}" style="color:${statusColor};margin-right:0.5rem;"></i>${t.title} 
                            <span class="badge" style="font-size:0.65rem;margin-left:0.5rem;background:${t.type === 'manual' ? 'var(--color-primary-dim)' : ''};color:${t.type === 'manual' ? 'var(--color-primary)' : ''};">${taskTypeDisplay}</span>
                            ${(t.type !== 'manual' && t.assigned_to) ? `<span style="font-size:0.7rem;color:var(--text-muted);margin-left:0.5rem;"><i class="fa-solid fa-user"></i> ${t.assigned_to}</span>` : ''}
                        </h3>
                        <span style="color:${statusColor};font-weight:bold;font-size:0.85rem;">${(t.status || 'pending').toUpperCase()}</span>
                    </div>
                    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.5rem;margin:0.8rem 0;font-size:0.75rem;">
                        <div style="background:rgba(168,85,247,0.1);padding:0.5rem;border-radius:4px;text-align:center;"><strong style="color:#a855f7;">Inputs</strong><br>${inputVal}</div>
                        <div style="background:rgba(245,158,11,0.1);padding:0.5rem;border-radius:4px;text-align:center;"><strong style="color:#f59e0b;">Procedure</strong><br>${processVal}</div>
                        <div style="background:rgba(34,197,94,0.1);padding:0.5rem;border-radius:4px;text-align:center;"><strong style="color:#22c55e;">Outputs</strong><br>${outputVal}</div>
                    </div>
                    ${imageHtml}
                    ${t.depends_on && t.depends_on.length > 0 ? `<div style="font-size:0.75rem;color:var(--text-muted);"><i class="fa-solid fa-link"></i> Depends on: ${t.depends_on.join(', ')}</div>` : ''}
                    ${t.notes ? `<div style="font-size:0.8rem;margin-top:0.5rem;padding:0.5rem;background:rgba(34,197,94,0.05);border-radius:4px;border-left:3px solid var(--color-success);"><i class="fa-solid fa-note-sticky"></i> ${t.notes}</div>` : ''}
                    <div style="margin-top:0.8rem;">${actionHtml}</div>
                `;
                container.appendChild(taskEl);
            });
        }
        
        // Show logs
        if (inc.logs && inc.logs.length > 0) {
            const logsEl = document.createElement('div');
            logsEl.style.cssText = 'margin-top:1rem;padding:1rem;background:rgba(0,0,0,0.3);border-radius:8px;max-height:150px;overflow-y:auto;';
            logsEl.innerHTML = `<h4 style="margin-bottom:0.5rem;"><i class="fa-solid fa-terminal"></i> Activity Log</h4>` +
                inc.logs.map(l => `<div style="font-size:0.75rem;color:var(--text-muted);font-family:monospace;margin:2px 0;">${l}</div>`).join('');
            container.appendChild(logsEl);
        }
        
        document.getElementById('sipoc-modal').style.display = 'flex';
    } catch(e) {
        console.error("Failed to load incident:", e);
        alert(`Error loading incident ${incident_id}: ${e.message}`);
    }
}

async function resolveTask(incId, taskId) {
    const reviewEl = document.getElementById(`review-${taskId}`);
    const review_note = reviewEl ? reviewEl.value : "";
    
    try {
        await fetch(`${API_URL}/resolve_task`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({incident_id: incId, task_id: taskId, review_note: review_note})
        });
        openSipocModal(incId);
    } catch(e) { console.error("Failed to resolve task", e); }
}

// ===== HEALTH CARDS =====
let historyStore = {};

function updateHealthCards(telemetry, statusDict) {
    Object.keys(telemetry).forEach(m_id => {
        const data = telemetry[m_id];
        const status = statusDict[m_id] || 'running';
        
        const card = document.getElementById(`health-${m_id}`);
        const scoreEl = document.getElementById(`score-${m_id}`);
        const metricsEl = document.getElementById(`metrics-${m_id}`);
        if (!card) return;
        
        card.classList.toggle('alert', status === 'alert');
        scoreEl.textContent = status === 'alert' ? `${Math.floor(Math.random()*30+20)}%` : `${Math.floor(Math.random()*5+92)}%`;
        
        const sensors = Object.keys(data.sensors);
        if (sensors.length >= 2) {
            const s1 = sensors[0], s2 = sensors[1];
            metricsEl.innerHTML = `
                <div class="hc-metric"><span>${s1.split('_')[0].toUpperCase()}</span><span>${data.sensors[s1].toFixed(1)}</span></div>
                <div class="hc-metric"><span>${s2.split('_')[0].toUpperCase()}</span><span>${data.sensors[s2].toFixed(1)}</span></div>
            `;
            const val = data.sensors[s1];
            if(!historyStore[m_id]) historyStore[m_id] = { base: val, vals: Array(20).fill(0) };
            const diff = (val - historyStore[m_id].base) / historyStore[m_id].base * 10; 
            historyStore[m_id].vals.push(diff);
            historyStore[m_id].vals.shift();
            const chart = miniCharts[m_id];
            chart.data.datasets[0].data = historyStore[m_id].vals;
            chart.data.datasets[0].borderColor = status === 'alert' ? '#ef4444' : '#f59e0b';
            chart.update();
        }
    });
}

// ===== SHIFT CLOCK =====
function updateShiftClock() {
    const shiftClockEl = document.getElementById('shift-clock');
    const shiftNameEl = document.querySelector('.shift-name');
    if (!shiftClockEl || !shiftNameEl) return;
    
    const now = Date.now();
    let elapsedMs = now - shiftStartTime;
    
    if (elapsedMs > SHIFT_DURATION_MS) {
        // Trigger auto shift handover generation on shift completion
        if (shiftCycle === 'day' || shiftCycle === 'night') {
            const shiftName = shiftCycle === 'day' ? 'Day Shift' : 'Night Shift';
            triggerAutoShiftHandover(shiftName);
        }
        
        elapsedMs = 0;
        shiftStartTime = now;
        if (shiftCycle === 'day') shiftCycle = 'break1';
        else if (shiftCycle === 'break1') shiftCycle = 'night';
        else if (shiftCycle === 'night') shiftCycle = 'break2';
        else shiftCycle = 'day';
    }
    
    if (shiftCycle === 'day' || shiftCycle === 'night') {
        const fraction = elapsedMs / SHIFT_DURATION_MS;
        const totalSimMs = SIMULATED_SHIFT_HOURS * 60 * 60 * 1000;
        const currentSimMs = fraction * totalSimMs;
        const baseHour = shiftCycle === 'day' ? 6 : 18;
        const d = new Date(1970, 0, 1, baseHour, 0, 0, 0);
        d.setMilliseconds(d.getMilliseconds() + currentSimMs);
        let hh = d.getHours();
        const mm = String(d.getMinutes()).padStart(2, '0');
        const ss = String(d.getSeconds()).padStart(2, '0');
        const ampm = hh >= 12 ? 'PM' : 'AM';
        hh = hh % 12 || 12;
        shiftClockEl.textContent = `${String(hh).padStart(2, '0')}:${mm}:${ss} ${ampm}`;
        shiftNameEl.innerHTML = shiftCycle === 'day' ? 'Day Shift<br>06:00 AM - 06:00 PM' : 'Night Shift<br>06:00 PM - 06:00 AM';
        shiftClockEl.style.color = 'var(--color-success)';
    } else {
        const remainingMs = SHIFT_DURATION_MS - elapsedMs;
        const mm = String(Math.floor(remainingMs / 60000)).padStart(2, '0');
        const ss = String(Math.floor((remainingMs % 60000) / 1000)).padStart(2, '0');
        shiftClockEl.textContent = `${mm}:${ss}`;
        shiftNameEl.innerHTML = 'Shift Break<br>Maintenance & Handover';
        shiftClockEl.style.color = 'var(--color-warning)';
    }
}

// ===== VIEW SWITCHING =====
function switchView(viewName) {
    const views = ['dashboard', 'alerts', 'incidents', 'assistant', 'documents', 'rca', 'ontology', 'database', 'shift-handover'];
    views.forEach(v => {
        const el = document.getElementById(`view-${v}`);
        if (el) el.style.display = 'none';
    });
    
    // Manage active state on nav links
    document.querySelectorAll('.sidebar ul li').forEach(li => {
        li.classList.remove('active');
    });
    const navEl = document.getElementById(`nav-${viewName}`);
    if (navEl) navEl.classList.add('active');
    
    const pageTitle = document.getElementById('main-page-title');
    const titles = {
        'dashboard': 'Live Plant Overview',
        'alerts': 'Alerts History',
        'incidents': 'Incident Tracking Log',
        'assistant': 'Multi-Agent AI Copilot',
        'documents': 'Knowledge Base Documents',
        'database': 'System Database (Live)',
        'ontology': 'Agentic Task Generator',
        'rca': 'Root Cause Analysis Reports',
        'shift-handover': 'Shift Handover & Operations Log'
    };
    
    const targetView = document.getElementById(`view-${viewName}`);
    const targetNav = document.getElementById(`nav-${viewName}`);
    if (targetView) {
        if (viewName === 'dashboard') {
            targetView.style.display = 'block';
        } else if (viewName === 'shift-handover') {
            targetView.style.display = 'block';
        } else {
            targetView.style.display = 'flex';
        }
    }
    if (targetNav) targetNav.classList.add('active');
    if (pageTitle) pageTitle.textContent = titles[viewName] || viewName;
    
    // Trigger data fetch for specific views
    if (viewName === 'documents') fetchDocuments();
    if (viewName === 'rca') fetchRCA();
    if (viewName === 'ontology') fetchOntologyCache();
    if (viewName === 'database') fetchDatabases();
    if (viewName === 'incidents') fetchIncidents();
    if (viewName === 'shift-handover') fetchShiftDocuments();
}

// ===== DOCUMENT VIEWER =====
async function fetchDocuments() {
    try {
        const response = await fetch(`${API_URL}/documents`);
        const data = await response.json();
        const explorer = document.getElementById('doc-explorer');
        explorer.innerHTML = '';
        
        if (!data.documents || data.documents.length === 0) {
            explorer.innerHTML = '<p style="color:var(--text-muted)">No documents found.</p>';
            return;
        }
        
        // Group by folder
        const groups = {};
        data.documents.forEach(doc => {
            const folder = doc.folder || 'root';
            if (!groups[folder]) groups[folder] = [];
            groups[folder].push(doc);
        });
        
        Object.keys(groups).sort().forEach(folder => {
            const folderEl = document.createElement('div');
            folderEl.style.marginBottom = '0.5rem';
            
            const folderHeader = document.createElement('div');
            folderHeader.style.cssText = 'padding:0.5rem;font-weight:bold;font-size:0.85rem;color:var(--color-primary);cursor:pointer;';
            folderHeader.innerHTML = `<i class="fa-solid fa-folder" style="margin-right:0.5rem;"></i>${folder}`;
            folderEl.appendChild(folderHeader);
            
            groups[folder].forEach(doc => {
                const el = document.createElement('div');
                el.className = 'doc-file';
                el.style.cssText = 'padding:0.5rem 0.5rem 0.5rem 1.5rem;margin:2px 0;background:rgba(255,255,255,0.03);border:1px solid transparent;border-radius:4px;cursor:pointer;font-size:0.8rem;transition:all 0.2s;';
                el.innerHTML = `<i class="fa-solid ${doc.icon || 'fa-file'}" style="color:var(--color-primary);margin-right:0.5rem;"></i>${doc.name}`;
                el.onclick = () => openDocument(doc);
                folderEl.appendChild(el);
            });
            explorer.appendChild(folderEl);
        });
    } catch(e) { console.error("Failed to load documents:", e); }
}

function openDocument(doc) {
    document.getElementById('pdf-viewer-title').textContent = doc.name;
    const iframe = document.getElementById('pdf-iframe');
    
    if (doc.ext === '.md' || doc.ext === '.txt') {
        fetch(`${API_URL}/document/${doc.path}`)
            .then(r => r.text())
            .then(text => {
                const parsedHtml = parseMarkdownToHTML(text);
                iframe.srcdoc = buildDocViewerHTML(parsedHtml);
            });
    } else if (doc.ext === '.json') {
        fetch(`${API_URL}/document/${doc.path}`)
            .then(r => r.text())
            .then(text => {
                const prettyJson = JSON.stringify(JSON.parse(text), null, 2);
                const htmlContent = `<html><head><style>body{background:#090e17;color:#10b981;font-family:'Consolas','Courier New',monospace;padding:2rem;white-space:pre-wrap;font-size:13px;line-height:1.6;}</style></head><body>${escapeHtml(prettyJson)}</body></html>`;
                iframe.srcdoc = htmlContent;
            });
    } else if (doc.ext === '.png' || doc.ext === '.jpg' || doc.ext === '.svg') {
        iframe.src = `${API_URL}/document/${doc.path}`;
    } else {
        iframe.src = `${API_URL}/document/${doc.path}`;
    }
}

function buildDocViewerHTML(bodyHtml) {
    return `<html><head><style>
        body {
            background:#090e17;
            color:#cbd5e1;
            font-family:'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            padding:2rem;
            line-height:1.7;
            font-size:14px;
        }
        h1, h2, h3, h4 { color: #8b5cf6; font-weight: 600; margin-top: 1.5rem; }
        h1 { font-size: 1.5rem; color: #f0f4f8; }
        h2 { color: #3b82f6; border-bottom: 2px solid #232d45; padding-bottom: 0.5rem; font-size: 1.2rem; }
        h3 { color: #8b5cf6; font-size: 1.05rem; }
        strong { color: #f8fafc; }
        em { color: #94a3b8; }
        a { color: #3b82f6; text-decoration: none; }
        a:hover { text-decoration: underline; }
        pre {
            background:#141b2d;
            border: 1px solid #232d45;
            padding:1rem;
            border-radius:8px;
            overflow-x:auto;
        }
        code {
            color:#10b981;
            font-family: Consolas, 'Courier New', monospace;
        }
        img {
            max-width: 100%;
            border-radius: 8px;
            border: 1px solid #232d45;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            margin: 1rem 0;
        }
        table {
            width:100%;
            border-collapse:collapse;
            margin:1.5rem 0;
        }
        th, td {
            border-bottom:1px solid #232d45;
            padding:8px 12px;
            text-align:left;
        }
        th {
            background:#0d131f;
            color:#94a3b8;
            font-size:0.75rem;
            text-transform:uppercase;
            letter-spacing:0.5px;
        }
        ul, ol { padding-left:1.5rem; }
        li { margin-bottom:0.4rem; }
        blockquote {
            border-left: 3px solid #3b82f6;
            padding-left: 1rem;
            color: #94a3b8;
            font-style: italic;
            margin: 1rem 0;
        }
        hr { border: none; border-top: 1px solid #232d45; margin: 1.5rem 0; }
    </style></head><body>${bodyHtml}</body></html>`;
}

function escapeHtml(text) {
    return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// ===== DATABASE VIEWER =====
async function fetchDatabases() {
    try {
        const dbListRes = await fetch(`${API_URL}/databases`);
        const dbListData = await dbListRes.json();
        
        // Build sidebar list
        const sidebar = document.getElementById('db-sidebar-list');
        if (!sidebar) return;
        sidebar.innerHTML = '';
        
        if (dbListData.databases && dbListData.databases.length > 0) {
            dbListData.databases.forEach(db => {
                const el = document.createElement('div');
                el.className = 'doc-file';
                el.style.cssText = 'padding:0.7rem 0.8rem;margin:3px 0;background:rgba(255,255,255,0.03);border:1px solid transparent;border-radius:6px;cursor:pointer;font-size:0.8rem;transition:all 0.2s;display:flex;justify-content:space-between;align-items:center;';
                el.innerHTML = `
                    <span><i class="fa-solid fa-database" style="color:var(--color-primary);margin-right:0.5rem;"></i>${db.name.replace(/_/g, ' ')}</span>
                    <span class="badge" style="background:var(--color-primary-dim);color:var(--color-primary);border:1px solid rgba(59,130,246,0.2);font-size:0.65rem;">${db.record_count}</span>
                `;
                el.onclick = () => loadDatabaseTable(db.name);
                sidebar.appendChild(el);
            });
        }
        
        // Also load incidents view
        const incRes = await fetch(`${API_URL}/incidents`);
        const incData = await incRes.json();
        const rcaRes = await fetch(`${API_URL}/rca_reports`);
        const rcaData = await rcaRes.json();
        const rcaMap = {};
        rcaData.reports.forEach(r => { rcaMap[r.incident_id] = r; });
        
        // Add incidents as a special entry
        const incEl = document.createElement('div');
        incEl.className = 'doc-file';
        incEl.style.cssText = 'padding:0.7rem 0.8rem;margin:3px 0;background:rgba(239,68,68,0.04);border:1px solid rgba(239,68,68,0.15);border-radius:6px;cursor:pointer;font-size:0.8rem;transition:all 0.2s;display:flex;justify-content:space-between;align-items:center;';
        incEl.innerHTML = `
            <span><i class="fa-solid fa-triangle-exclamation" style="color:var(--color-danger);margin-right:0.5rem;"></i>Incident Reports</span>
            <span class="badge red">${(incData.incidents || []).length}</span>
        `;
        incEl.onclick = () => loadIncidentTable(incData.incidents || [], rcaMap);
        sidebar.insertBefore(incEl, sidebar.firstChild);
        
        // Auto-load first item (incidents)
        loadIncidentTable(incData.incidents || [], rcaMap);
        
    } catch (e) {
        console.error(e);
    }
}

async function loadDatabaseTable(dbName) {
    const container = document.getElementById('db-table-container');
    container.innerHTML = '<div style="text-align:center;padding:2rem;"><i class="fa-solid fa-circle-notch fa-spin fa-2x" style="color:var(--color-primary);"></i></div>';
    
    try {
        const res = await fetch(`${API_URL}/db_content/${dbName}`);
        const result = await res.json();
        
        if (result.error) {
            container.innerHTML = `<div style="padding:1rem;color:var(--color-danger);">${result.error}</div>`;
            return;
        }
        
        const data = result.data;
        const displayName = dbName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        
        let html = `<div style="padding:0.8rem 1rem;border-bottom:1px solid var(--panel-border);display:flex;justify-content:space-between;align-items:center;">
            <h3 style="font-size:0.95rem;"><i class="fa-solid fa-table" style="color:var(--color-primary);margin-right:0.5rem;"></i>${displayName}</h3>
            <span class="badge" style="background:var(--color-primary-dim);color:var(--color-primary);">${Array.isArray(data) ? data.length : 1} records</span>
        </div>`;
        
        if (Array.isArray(data) && data.length > 0) {
            // Get columns from first object
            const columns = Object.keys(data[0]).slice(0, 8); // Limit columns for readability
            
            html += '<div style="overflow-x:auto;">';
            html += '<table class="data-table">';
            html += '<thead><tr>';
            columns.forEach(col => {
                html += `<th>${col.replace(/_/g, ' ')}</th>`;
            });
            html += '</tr></thead><tbody>';
            
            data.forEach(row => {
                html += '<tr>';
                columns.forEach(col => {
                    let val = row[col];
                    if (val === null || val === undefined) val = '—';
                    else if (typeof val === 'object') val = JSON.stringify(val).substring(0, 60) + '...';
                    else val = String(val).substring(0, 80);
                    html += `<td>${val}</td>`;
                });
                html += '</tr>';
            });
            
            html += '</tbody></table></div>';
        } else if (typeof data === 'object') {
            html += '<div style="padding:1rem;"><pre style="background:#0d131f;padding:1rem;border-radius:8px;border:1px solid var(--panel-border);color:#10b981;font-size:0.82rem;overflow:auto;max-height:500px;">' + JSON.stringify(data, null, 2) + '</pre></div>';
        }
        
        container.innerHTML = html;
    } catch (e) {
        container.innerHTML = `<div style="padding:1rem;color:var(--color-danger);">Error: ${e.message}</div>`;
    }
}

function loadIncidentTable(incidents, rcaMap) {
    const container = document.getElementById('db-table-container');
    let html = `<div style="padding:0.8rem 1rem;border-bottom:1px solid var(--panel-border);">
        <h3 style="font-size:0.95rem;"><i class="fa-solid fa-triangle-exclamation" style="color:var(--color-danger);margin-right:0.5rem;"></i>Incident Reports</h3>
    </div>`;
    
    if (incidents.length === 0) {
        html += '<div style="padding:2rem;text-align:center;color:var(--text-muted);">No incidents recorded yet.</div>';
    } else {
        html += '<table class="data-table"><thead><tr><th>ID</th><th>Machine</th><th>Failure</th><th>Status</th><th>RCA</th></tr></thead><tbody>';
        incidents.forEach(inc => {
            const hasRca = rcaMap[inc.id] ? '<span class="badge green">Generated</span>' : '<span class="badge gray">Pending</span>';
            const completedTasks = (inc.tasks || []).filter(t => t.status === 'completed').length;
            const totalTasks = (inc.tasks || []).length;
            html += `<tr style="cursor:pointer;" onclick="openSipocModal('${inc.id}')">
                <td>${inc.id}</td>
                <td>${inc.machine_id}</td>
                <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${inc.failure_mode}</td>
                <td><span class="badge ${inc.status === 'open' ? 'red' : 'green'}">${inc.status.toUpperCase()}</span> ${completedTasks}/${totalTasks}</td>
                <td>${hasRca}</td>
            </tr>`;
        });
        html += '</tbody></table>';
    }
    container.innerHTML = html;
}

// ==========================================
// RCA DOCUMENTS
// ==========================================
async function fetchRCA() {
    try {
        const res = await fetch(`${API_URL}/documents`);
        const data = await res.json();
        const tree = document.getElementById('rca-explorer');
        tree.innerHTML = '';
        
        let html = '';
        if (data.documents && data.documents.length > 0) {
            data.documents.forEach(doc => {
                if (doc.folder === 'rca_documents') {
                    html += `
                    <div class="doc-file" style="padding:0.6rem 0.8rem; margin:4px 0; background:rgba(255,255,255,0.03); border-radius:6px; cursor:pointer; font-size:0.8rem; transition:background 0.2s; display:flex; align-items:center; gap:0.5rem;" onclick="openRCA('${doc.path}')">
                        <i class="fa-solid fa-file-contract" style="color:var(--color-primary);"></i>
                        <span style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${doc.name}</span>
                    </div>`;
                }
            });
        }
        
        if (!html) {
            tree.innerHTML = '<div style="padding: 1rem; color: var(--text-muted); font-size:0.8rem;">No RCA reports generated yet.</div>';
        } else {
            tree.innerHTML = html;
        }
    } catch (e) {
        console.error(e);
    }
}

function openRCA(path) {
    document.getElementById('rca-viewer-title').innerText = path.split('/').pop();
    
    const ext = path.split('.').pop().toLowerCase();
    if (ext === 'md' || ext === 'txt') {
        fetch(`${API_URL}/document/${path}`)
            .then(r => r.text())
            .then(text => {
                const iframe = document.getElementById('rca-iframe');
                const parsedHtml = parseMarkdownToHTML(text);
                iframe.srcdoc = buildDocViewerHTML(parsedHtml);
            });
    } else {
        document.getElementById('rca-iframe').src = `${API_URL}/document/${path}`;
    }
}

function parseMarkdownToHTML(md) {
    let html = md;
    
    // Code blocks
    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (match, lang, code) => {
        return `<pre><code>${escapeHtml(code)}</code></pre>`;
    });

    // Inline code
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Images: ![alt](url)
    html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<div style="text-align:center; margin:1.5rem 0;"><img src="$2" alt="$1" style="max-width:100%; border-radius:8px; border:1px solid #232d45; box-shadow:0 10px 25px rgba(0,0,0,0.5);" /><p style="color:#94a3b8; font-size:0.8rem; margin-top:0.5rem; font-style:italic;">$1</p></div>');

    // Links: [text](url)
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" style="color:#3b82f6; text-decoration:none;">$1</a>');

    // Headers
    html = html.replace(/^### (.*?)$/gm, '<h4>$1</h4>');
    html = html.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.*?)$/gm, '<h1>$1</h1>');

    // Bold & Italic
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    // Tables
    const tableRegex = /((?:\|[^\n]*\|(?:\n|$))+)/g;
    html = html.replace(tableRegex, (match) => {
        const lines = match.trim().split('\n');
        if (lines.length < 2) return match;
        
        let tableHtml = '<table>';
        
        const headers = lines[0].split('|').map(x => x.trim()).filter(x => x !== '');
        tableHtml += '<thead><tr>';
        headers.forEach(h => {
            tableHtml += `<th>${h}</th>`;
        });
        tableHtml += '</tr></thead><tbody>';
        
        for (let i = 2; i < lines.length; i++) {
            const cols = lines[i].split('|').map(x => x.trim()).filter(x => x !== '');
            if (cols.length === 0) continue;
            tableHtml += '<tr>';
            cols.forEach(c => {
                tableHtml += `<td>${c}</td>`;
            });
            tableHtml += '</tr>';
        }
        
        tableHtml += '</tbody></table>';
        return tableHtml;
    });

    // Unordered lists
    html = html.replace(/^\s*-\s+(.*?)$/gm, '<li>$1</li>');
    // Wrap lists
    html = html.replace(/((?:<li>[\s\S]*?<\/li>\n?)+)/g, '<ul>$1</ul>');

    // Paragraphs
    const paragraphs = html.split(/\n\n+/);
    html = paragraphs.map(p => {
        const trimmed = p.trim();
        if (trimmed.startsWith('<pre') || trimmed.startsWith('<table') || trimmed.startsWith('<ul') || trimmed.startsWith('<h') || trimmed.startsWith('<div')) {
            return p;
        }
        return `<p style="line-height:1.6; color:#cbd5e1; margin-bottom:1rem; font-size:0.95rem;">${p.replace(/\n/g, '<br>')}</p>`;
    }).join('\n');

    return html;
}

// ==========================================
// ONTOLOGY GENERATOR
// ==========================================
async function generateAllOntologies() {
    alert("Starting Mass Ontology Generation. Check the 'Incidents' tab in a few moments as incidents are simulated.");
    try {
        await fetch(`${API_URL}/generate_all_ontologies`, { method: 'POST' });
        setTimeout(() => switchView('incidents'), 2000);
    } catch (e) {
        console.error(e);
    }
}

async function generateOntology() {
    const failureMode = document.getElementById('ontology-failure-select').value;
    const container = document.getElementById('ontology-results');
    
    container.innerHTML = `<div style="text-align:center;color:var(--color-primary);padding:2rem;"><i class="fa-solid fa-circle-notch fa-spin fa-2x"></i><br><br>Querying RAG Vector Store & generating resolution tasks via Ollama...<br><small style="color:var(--text-muted);">This may take 10-30 seconds</small></div>`;
    
    try {
        const response = await fetch(`${API_URL}/generate_ontology`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({failure_mode: failureMode})
        });
        const data = await response.json();
        
        container.innerHTML = '';
        if (data.error) {
            container.innerHTML = `<div style="color:var(--color-danger);padding:1rem;">Error: ${data.error}<br><pre style="font-size:0.7rem;max-height:200px;overflow:auto;">${data.raw || ''}</pre></div>`;
            return;
        }
        
        // Header
        container.innerHTML = `<div style="padding:0.5rem;border-bottom:1px solid var(--panel-border);margin-bottom:0.5rem;">
            <strong>Generated ${(data.tasks||[]).length} resolution tasks for: ${data.failure_mode || failureMode}</strong>
        </div>`;
        
        (data.tasks || []).forEach((t, idx) => {
            const sipoc = t.sipoc || {};
            const inputVal = sipoc.Input || t.inputs || '-';
            const processVal = sipoc.Process || t.procedure || t.process || '-';
            const outputVal = sipoc.Output || t.outputs || '-';
            
            const taskTypeDisplay = t.type === 'manual' ? (t.assigned_to || 'Manual').toUpperCase() : (t.type||'auto').toUpperCase();

            const taskEl = document.createElement('div');
            taskEl.className = 'panel';
            taskEl.style.cssText = 'padding:1rem;border-left:4px solid var(--color-primary);margin-bottom:0.5rem;';
            
            taskEl.innerHTML = `
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <h3 style="font-size:0.95rem;">${t.id || `t${idx+1}`}. ${t.title} 
                        <span class="badge" style="font-size:0.65rem;background:${t.type === 'manual' ? 'var(--color-primary-dim)' : ''};color:${t.type === 'manual' ? 'var(--color-primary)' : ''};">${taskTypeDisplay}</span>
                        ${(t.type !== 'manual' && t.assigned_to) ? `<span style="font-size:0.7rem;color:var(--text-muted);margin-left:0.5rem;"><i class="fa-solid fa-user"></i> ${t.assigned_to}</span>` : ''}
                    </h3>
                </div>
                <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.5rem;margin:0.8rem 0;font-size:0.75rem;">
                    <div style="background:rgba(168,85,247,0.1);padding:0.4rem;border-radius:4px;text-align:center;"><strong style="color:#a855f7;">Inputs</strong><br>${inputVal}</div>
                    <div style="background:rgba(245,158,11,0.1);padding:0.4rem;border-radius:4px;text-align:center;"><strong style="color:#f59e0b;">Procedure</strong><br>${processVal}</div>
                    <div style="background:rgba(34,197,94,0.1);padding:0.4rem;border-radius:4px;text-align:center;"><strong style="color:#22c55e;">Outputs</strong><br>${outputVal}</div>
                </div>
                <div style="font-size:0.75rem;color:var(--text-muted);"><i class="fa-solid fa-link"></i> Depends on: ${(t.depends_on||[]).join(', ') || 'None (Start)'}</div>
            `;
            container.appendChild(taskEl);
        });
    } catch(e) {
        container.innerHTML = `<div style="color:var(--color-danger);padding:1rem;">Network Error: ${e.message}</div>`;
    }
}

// ===== CHATBOT =====
async function sendChatMessage() {
    const inputEl = document.getElementById('chat-input');
    const historyEl = document.getElementById('chat-history');
    const personaEl = document.getElementById('persona-select');
    
    const query = inputEl.value.trim();
    if (!query) return;
    
    // User message
    const userMsg = document.createElement('div');
    userMsg.className = 'chat-message user';
    userMsg.innerHTML = `<div class="chat-bubble" style="background:var(--color-primary);margin-left:auto;">${escapeHtml(query)}</div>`;
    historyEl.appendChild(userMsg);
    inputEl.value = '';
    historyEl.scrollTop = historyEl.scrollHeight;
    
    // Typing indicator
    const typingMsg = document.createElement('div');
    typingMsg.className = 'chat-message bot';
    typingMsg.innerHTML = `<div class="chat-bubble"><i class="fa-solid fa-brain" style="color:var(--color-primary);"></i> Planning tools & querying databases... <i class="fa-solid fa-circle-notch fa-spin"></i></div>`;
    historyEl.appendChild(typingMsg);
    historyEl.scrollTop = historyEl.scrollHeight;
    
    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ query: query, persona: personaEl.value })
        });
        const data = await response.json();
        
        historyEl.removeChild(typingMsg);
        
        const botMsg = document.createElement('div');
        botMsg.className = 'chat-message bot';
        
        // Simple markdown to HTML
        let formatted = data.response
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/### (.*?)$/gm, '<h4 style="color:var(--color-primary);margin:0.5rem 0;">$1</h4>')
            .replace(/## (.*?)$/gm, '<h3 style="color:var(--color-primary);margin:0.5rem 0;">$1</h3>')
            .replace(/^- (.*?)$/gm, '<li>$1</li>')
            .replace(/\n/g, '<br>');
        
        let toolsInfo = '';
        if (data.tools_called && data.tools_called.length > 0) {
            toolsInfo = `<div style="font-size:0.7rem;color:#a855f7;margin-top:0.5rem;padding:0.3rem 0.5rem;background:rgba(168,85,247,0.1);border-radius:4px;">
                <i class="fa-solid fa-wrench"></i> Tools used: ${data.tools_called.join(', ')}
            </div>`;
        }
        
        botMsg.innerHTML = `
            <div class="chat-bubble">
                ${formatted}
                ${toolsInfo}
                <div style="font-size:0.7rem;color:#a1a1aa;margin-top:0.5rem;">
                    <i class="fa-solid fa-server"></i> Sources: ${data.sources_used.join(' • ')}
                </div>
            </div>`;
        historyEl.appendChild(botMsg);
        historyEl.scrollTop = historyEl.scrollHeight;
        
    } catch(e) {
        historyEl.removeChild(typingMsg);
        const errMsg = document.createElement('div');
        errMsg.className = 'chat-message bot';
        errMsg.innerHTML = `<div class="chat-bubble" style="border-left:3px solid var(--color-danger);">Error: ${e.message}</div>`;
        historyEl.appendChild(errMsg);
    }
}

// ===== SHIFT HANDOVER LOGIC =====
async function triggerAutoShiftHandover(shiftName) {
    try {
        const response = await fetch(`${API_URL}/generate_shift_handover`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                shift_name: shiftName,
                supervisor: 'Supervisor (Plant Manager)',
                manual: false
            })
        });
        const data = await response.json();
        if (data.success) {
            showToastNotification("Shift Handover Completed", `Handover document for ${shiftName} generated automatically.`, "success");
            if (document.getElementById('nav-shift-handover')?.classList.contains('active')) {
                fetchShiftDocuments();
            }
        }
    } catch (err) {
        console.error("Auto-handover failed:", err);
    }
}

async function generateShiftHandover() {
    const currentShift = shiftCycle === 'day' ? 'Day Shift' : (shiftCycle === 'night' ? 'Night Shift' : 'Break Handover');
    
    showToastNotification("Generating Report", "Compiling telemetry, active incidents, and LLM summary...", "info");
    
    try {
        const response = await fetch(`${API_URL}/generate_shift_handover`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                shift_name: currentShift,
                supervisor: 'Supervisor (Plant Manager)',
                manual: true
            })
        });
        const data = await response.json();
        if (data.success) {
            showToastNotification("Report Generated", `Handover report ready to view.`, "success");
            switchView('shift-handover');
            await fetchShiftDocuments(); // will auto-open the newest
        } else {
            showToastNotification("Generation Failed", data.error || "Unknown error occurred.", "error");
        }
    } catch (err) {
        showToastNotification("Generation Failed", err.message, "error");
    }
}

async function fetchShiftDocuments() {
    try {
        const response = await fetch(`${API_URL}/shift_documents`);
        const data = await response.json();
        const explorer = document.getElementById('shift-doc-explorer');
        if (!explorer) return;
        
        explorer.innerHTML = '';
        if (!data.documents || data.documents.length === 0) {
            explorer.innerHTML = '<div style="color:var(--text-muted); text-align:center; font-size:0.85rem; padding-top:2rem;"><i class="fa-solid fa-folder-open" style="font-size:2rem;display:block;margin-bottom:0.5rem;opacity:0.3;"></i>No handover reports found.<br><small>Click "Generate Handover" to create one.</small></div>';
            return;
        }
        
        data.documents.forEach((doc, idx) => {
            const el = document.createElement('div');
            el.className = 'doc-file';
            el.style.cssText = 'padding:0.7rem 0.8rem; margin:4px 0; background:rgba(255,255,255,0.03); border:1px solid transparent; border-radius:6px; cursor:pointer; font-size:0.8rem; display:flex; align-items:center; gap:0.5rem;';
            
            // Clean filename display by replacing either extension
            const displayName = doc.name.replace('_Handover.html', '').replace('_Handover.md', '');
            
            el.innerHTML = `
                <i class="fa-solid fa-file-contract" style="color:var(--color-primary); flex-shrink:0;"></i>
                <div style="overflow:hidden; flex:1;">
                    <div style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:var(--text-main); font-weight:500;">${displayName}</div>
                    <div style="font-size:0.72rem; color:var(--text-muted); margin-top:1px;">${doc.date} &middot; ${(doc.size/1024).toFixed(1)} KB</div>
                </div>
            `;
            el.onclick = () => openShiftDocument(doc.path, el);
            explorer.appendChild(el);
            
            // Auto-open the first (most recent) document
            if (idx === 0) {
                setTimeout(() => openShiftDocument(doc.path, el), 100);
            }
        });
    } catch (err) {
        console.error("Failed to load shift documents:", err);
    }
}

function openShiftDocument(path, clickedEl) {
    // Highlight active
    document.querySelectorAll('#shift-doc-explorer .doc-file').forEach(el => {
        el.style.background = 'rgba(255,255,255,0.03)';
        el.style.borderColor = 'transparent';
    });
    if (clickedEl) {
        clickedEl.style.background = 'rgba(59,130,246,0.1)';
        clickedEl.style.borderColor = 'rgba(59,130,246,0.4)';
    }
    
    const filename = path.split('/').pop();
    const titleEl = document.getElementById('shift-viewer-title');
    if (titleEl) {
        titleEl.textContent = filename.replace('_Handover.html', ' — Shift Handover Report').replace('_Handover.md', ' — Shift Handover Report');
    }
    
    const iframe = document.getElementById('shift-iframe');
    if (!iframe) return;
    
    // Serve HTML directly via iframe src
    iframe.src = `${API_URL}/document/${path}`;
}

function showToastNotification(title, message, type='info') {
    if (!document.getElementById('toast-styles')) {
        const style = document.createElement('style');
        style.id = 'toast-styles';
        style.innerHTML = `
            @keyframes slideIn { from { transform: translateX(120%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
            @keyframes slideOut { from { transform: translateX(0); opacity: 1; } to { transform: translateX(120%); opacity: 0; } }
        `;
        document.head.appendChild(style);
    }

    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        bottom: 50px;
        right: 20px;
        background: var(--panel-bg);
        border-left: 4px solid ${type === 'error' ? 'var(--color-danger)' : (type === 'info' ? 'var(--color-primary)' : 'var(--color-success)')};
        border-top: 1px solid var(--panel-border);
        border-right: 1px solid var(--panel-border);
        border-bottom: 1px solid var(--panel-border);
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        z-index: 10000;
        max-width: 320px;
        animation: slideIn 0.3s ease-out;
    `;
    toast.innerHTML = `
        <div style="font-weight:bold; color: white; display:flex; align-items:center; gap:0.5rem; margin-bottom: 0.2rem;">
            <i class="fa-solid ${type === 'error' ? 'fa-triangle-exclamation' : (type === 'info' ? 'fa-circle-info' : 'fa-circle-check')}" style="color:${type === 'error' ? 'var(--color-danger)' : (type === 'info' ? 'var(--color-primary)' : 'var(--color-success)')};"></i>
            ${title}
        </div>
        <div style="font-size:0.8rem; color: var(--text-muted); line-height:1.4;">${message}</div>
    `;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// Boot
init();
