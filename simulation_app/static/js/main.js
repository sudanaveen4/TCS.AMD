const API_URL = "http://127.0.0.1:5000/api";

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
                
                const sipoc = t.sipoc || {};
                const taskEl = document.createElement('div');
                taskEl.className = 'panel';
                taskEl.style.cssText = `padding:1rem;border-left:4px solid ${statusColor};margin-bottom:0.5rem;`;
                
                taskEl.innerHTML = `
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <h3 style="font-size:1rem;"><i class="fa-solid ${statusIcon}" style="color:${statusColor};margin-right:0.5rem;"></i>${t.title} 
                            <span class="badge" style="font-size:0.6rem;margin-left:0.5rem;">${(t.type || 'auto').toUpperCase()}</span>
                            ${t.assigned_to ? `<span style="font-size:0.7rem;color:var(--text-muted);margin-left:0.5rem;"><i class="fa-solid fa-user"></i> ${t.assigned_to}</span>` : ''}
                        </h3>
                        <span style="color:${statusColor};font-weight:bold;font-size:0.85rem;">${(t.status || 'pending').toUpperCase()}</span>
                    </div>
                    <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:0.5rem;margin:0.8rem 0;font-size:0.75rem;">
                        <div style="background:rgba(59,130,246,0.1);padding:0.5rem;border-radius:4px;text-align:center;"><strong style="color:#3b82f6;">S</strong><br>${sipoc.Supplier || '-'}</div>
                        <div style="background:rgba(168,85,247,0.1);padding:0.5rem;border-radius:4px;text-align:center;"><strong style="color:#a855f7;">I</strong><br>${sipoc.Input || '-'}</div>
                        <div style="background:rgba(245,158,11,0.1);padding:0.5rem;border-radius:4px;text-align:center;"><strong style="color:#f59e0b;">P</strong><br>${sipoc.Process || '-'}</div>
                        <div style="background:rgba(34,197,94,0.1);padding:0.5rem;border-radius:4px;text-align:center;"><strong style="color:#22c55e;">O</strong><br>${sipoc.Output || '-'}</div>
                        <div style="background:rgba(239,68,68,0.1);padding:0.5rem;border-radius:4px;text-align:center;"><strong style="color:#ef4444;">C</strong><br>${sipoc.Customer || '-'}</div>
                    </div>
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
    const views = ['dashboard', 'incidents', 'chat', 'documents', 'rca', 'ontology', 'database'];
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
        'ontology': 'Agentic Ontology Generator',
        'rca': 'Root Cause Analysis Reports'
    };
    
    const targetView = document.getElementById(`view-${viewName}`);
    const targetNav = document.getElementById(`nav-${viewName}`);
    if (targetView) targetView.style.display = viewName === 'dashboard' ? 'block' : 'flex';
    if (targetNav) targetNav.classList.add('active');
    if (pageTitle) pageTitle.textContent = titles[viewName] || viewName;
    
    // Trigger data fetch for specific views
    if (viewName === 'documents') fetchDocuments();
    if (viewName === 'rca') fetchRCA();
    if (viewName === 'ontology') fetchOntologyCache();
    if (viewName === 'database') fetchDatabases();
    if (viewName === 'incidents') fetchIncidents();
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
                el.style.cssText = 'padding:0.5rem 0.5rem 0.5rem 1.5rem;margin:2px 0;background:rgba(255,255,255,0.03);border-radius:4px;cursor:pointer;font-size:0.8rem;transition:background 0.2s;';
                el.onmouseenter = () => el.style.background = 'rgba(255,255,255,0.08)';
                el.onmouseleave = () => el.style.background = 'rgba(255,255,255,0.03)';
                el.innerHTML = `<i class="fa-solid ${doc.icon || 'fa-file'}" style="color:var(--color-primary);margin-right:0.5rem;"></i>${doc.name}`;
                el.onclick = () => {
                    document.getElementById('pdf-viewer-title').textContent = doc.name;
                    if (doc.ext === '.md' || doc.ext === '.json' || doc.ext === '.txt') {
                        // Fetch and render text content
                        fetch(`${API_URL}/document/${doc.path}`)
                            .then(r => r.text())
                            .then(text => {
                                const iframe = document.getElementById('pdf-iframe');
                                const htmlContent = `<html><head><style>body{background:#1e1e2e;color:#cdd6f4;font-family:'Segoe UI',sans-serif;padding:2rem;white-space:pre-wrap;font-size:14px;line-height:1.6;} pre{background:#313244;padding:1rem;border-radius:8px;overflow-x:auto;} code{color:#a6e3a1;} h1,h2,h3{color:#89b4fa;} strong{color:#f9e2af;} table{border-collapse:collapse;width:100%;} th,td{border:1px solid #45475a;padding:8px;text-align:left;} th{background:#313244;}</style></head><body>${escapeHtml(text)}</body></html>`;
                                iframe.srcdoc = htmlContent;
                            });
                    } else {
                        document.getElementById('pdf-iframe').src = `${API_URL}/document/${doc.path}`;
                    }
                };
                folderEl.appendChild(el);
            });
            explorer.appendChild(folderEl);
        });
    } catch(e) { console.error("Failed to load documents:", e); }
}

function escapeHtml(text) {
    return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// ===== DATABASE VIEWER =====
async function fetchDatabases() {
    try {
        // Fetch databases list
        const dbListRes = await fetch(`${API_URL}/databases`);
        const dbListData = await dbListRes.json();
        
        // Also fetch incidents
        const incRes = await fetch(`${API_URL}/incidents`);
        const incData = await incRes.json();
        
        const rcaRes = await fetch(`${API_URL}/rca_reports`);
        const rcaData = await rcaRes.json();
        const rcaMap = {};
        rcaData.reports.forEach(r => { rcaMap[r.incident_id] = r; });
        
        const tbody = document.getElementById('db-table-body');
        tbody.innerHTML = '';
        
        // Show incidents
        if (incData.incidents && incData.incidents.length > 0) {
            incData.incidents.forEach(inc => {
                const tr = document.createElement('tr');
                tr.style.cssText = 'border-bottom:1px solid rgba(255,255,255,0.1);cursor:pointer;';
                tr.onclick = () => openSipocModal(inc.id);
                
                const hasRca = rcaMap[inc.id] ? '<span class="badge green">Generated</span>' : '<span class="badge gray">Pending</span>';
                const completedTasks = (inc.tasks || []).filter(t => t.status === 'completed').length;
                const totalTasks = (inc.tasks || []).length;
                
                tr.innerHTML = `
                    <td style="padding:0.8rem;">${inc.id}</td>
                    <td style="padding:0.8rem;">${inc.machine_id}</td>
                    <td style="padding:0.8rem;">${inc.failure_mode}</td>
                    <td style="padding:0.8rem;"><span class="badge ${inc.status === 'open' ? 'red' : 'green'}">${inc.status.toUpperCase()}</span> ${completedTasks}/${totalTasks}</td>
                    <td style="padding:0.8rem;">${hasRca}</td>
                `;
                tbody.appendChild(tr);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="5" style="padding:1rem;color:var(--text-muted);text-align:center;">No incidents recorded yet. Inject a failure from the Simulation Controller.</td></tr>';
        }
        
        // Also show database files info below the table
        const dbInfoEl = document.getElementById('db-files-info');
        if (dbInfoEl && dbListData.databases) {
            dbInfoEl.innerHTML = '<h4 style="margin-bottom:0.5rem;"><i class="fa-solid fa-database"></i> Available Plant Databases</h4>';
            dbListData.databases.forEach(db => {
                const chip = document.createElement('span');
                chip.style.cssText = 'display:inline-block;padding:0.3rem 0.8rem;margin:0.2rem;background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:20px;font-size:0.75rem;color:#3b82f6;';
                chip.textContent = `${db.name} (${db.record_count} records)`;
                dbInfoEl.appendChild(chip);
            });
        }
    } catch (e) {
        console.error(e);
    }
}

// ==========================================
// RCA DOCUMENTS
// ==========================================
async function fetchRCA() {
    try {
        const res = await fetch('/api/documents');
        const data = await res.json();
        const tree = document.getElementById('rca-explorer');
        tree.innerHTML = '';
        
        // We only care about the rca_documents folder
        const buildRCATree = (node, path) => {
            let html = '';
            for (const [key, value] of Object.entries(node)) {
                const currentPath = path ? `${path}/${key}` : key;
                if (key === 'rca_documents' && typeof value === 'object') {
                    for (const [rcaKey, rcaValue] of Object.entries(value)) {
                        if (typeof rcaValue === 'string') continue;
                        html += `
                        <div class="doc-file" onclick="openRCA('${currentPath}/${rcaKey}')">
                            <i class="fa-solid fa-file-contract"></i> ${rcaKey}
                        </div>`;
                    }
                } else if (typeof value === 'object') {
                    html += buildRCATree(value, currentPath);
                }
            }
            return html;
        };
        
        const rcaFiles = buildRCATree(data.documents, '');
        if (!rcaFiles) {
            tree.innerHTML = '<div style="padding: 1rem; color: var(--text-muted);">No RCA reports generated yet.</div>';
        } else {
            tree.innerHTML = rcaFiles;
        }
    } catch (e) {
        console.error(e);
    }
}

function openRCA(path) {
    document.getElementById('rca-viewer-title').innerText = path.split('/').pop();
    document.getElementById('rca-iframe').src = `/api/document/${path}`;
}

// ==========================================
// ONTOLOGY GENERATOR
// ==========================================
async function generateAllOntologies() {
    alert("Starting Mass Ontology Generation. Check the 'Incidents' tab in a few moments as incidents are simulated.");
    try {
        await fetch('/api/generate_all_ontologies', { method: 'POST' });
        setTimeout(() => switchView('incidents'), 2000);
    } catch (e) {
        console.error(e);
    }
}

async function generateOntology() {
    const failureMode = document.getElementById('ontology-failure-select').value;
    const container = document.getElementById('ontology-results');
    
    container.innerHTML = `<div style="text-align:center;color:var(--color-primary);padding:2rem;"><i class="fa-solid fa-circle-notch fa-spin fa-2x"></i><br><br>Querying RAG Vector Store & generating SIPOC DAG via Ollama...<br><small style="color:var(--text-muted);">This may take 10-30 seconds</small></div>`;
    
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
            const taskEl = document.createElement('div');
            taskEl.className = 'panel';
            taskEl.style.cssText = 'padding:1rem;border-left:4px solid var(--color-primary);margin-bottom:0.5rem;';
            
            taskEl.innerHTML = `
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <h3 style="font-size:0.95rem;">${t.id || `t${idx+1}`}. ${t.title} 
                        <span class="badge" style="font-size:0.6rem;">${(t.type||'auto').toUpperCase()}</span>
                        ${t.assigned_to ? `<span style="font-size:0.7rem;color:var(--text-muted);margin-left:0.5rem;"><i class="fa-solid fa-user"></i> ${t.assigned_to}</span>` : ''}
                    </h3>
                </div>
                <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:0.5rem;margin:0.8rem 0;font-size:0.75rem;">
                    <div style="background:rgba(59,130,246,0.1);padding:0.4rem;border-radius:4px;text-align:center;"><strong style="color:#3b82f6;">S</strong><br>${sipoc.Supplier || '-'}</div>
                    <div style="background:rgba(168,85,247,0.1);padding:0.4rem;border-radius:4px;text-align:center;"><strong style="color:#a855f7;">I</strong><br>${sipoc.Input || '-'}</div>
                    <div style="background:rgba(245,158,11,0.1);padding:0.4rem;border-radius:4px;text-align:center;"><strong style="color:#f59e0b;">P</strong><br>${sipoc.Process || '-'}</div>
                    <div style="background:rgba(34,197,94,0.1);padding:0.4rem;border-radius:4px;text-align:center;"><strong style="color:#22c55e;">O</strong><br>${sipoc.Output || '-'}</div>
                    <div style="background:rgba(239,68,68,0.1);padding:0.4rem;border-radius:4px;text-align:center;"><strong style="color:#ef4444;">C</strong><br>${sipoc.Customer || '-'}</div>
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

// Boot
init();
