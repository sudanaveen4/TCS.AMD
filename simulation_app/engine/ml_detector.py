import numpy as np
from sklearn.svm import OneClassSVM
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import time

class MLDetector:
    def __init__(self, slm_client):
        self.slm_client = slm_client
        self.svm_models = {}
        self.if_models = {}
        self.scalers = {}
        self.machine_status = {}
        
    def _train_on_fly(self, machine_id, sensors_dict):
        # Quick fit for a new machine based on first observed point
        features = list(sensors_dict.values())
        normal_data = []
        for _ in range(300):
            # Widen the synthetic normal bounds slightly (5% std dev) so normal noise doesn't trigger alerts
            noise = [f + np.random.normal(0, max(0.1, abs(f)*0.05)) for f in features]
            normal_data.append(noise)
            
        scaler = StandardScaler()
        scaled = scaler.fit_transform(normal_data)
        
        # Train Model 1: One-Class SVM with very low nu
        svm = OneClassSVM(nu=0.001, kernel="rbf", gamma=0.05)
        svm.fit(scaled)
        
        # Train Model 2: Isolation Forest
        iso = IsolationForest(contamination=0.005, random_state=42)
        iso.fit(scaled)
        
        self.svm_models[machine_id] = svm
        self.if_models[machine_id] = iso
        self.scalers[machine_id] = scaler
        
    def clear_status(self):
        for m in self.machine_status:
            self.machine_status[m] = "running"
            
    def get_machine_status(self):
        return self.machine_status
        
    def detect_anomalies(self, latest_telemetry):
        new_alerts = []
        
        for m_id, data in latest_telemetry.items():
            if m_id not in self.machine_status:
                self.machine_status[m_id] = "running"
                
            sensors = data['sensors']
            
            if m_id not in self.svm_models:
                self._train_on_fly(m_id, sensors)
                
            features = list(sensors.values())
            scaled = self.scalers[m_id].transform([features])
            
            # Ensemble predictions
            svm_pred = self.svm_models[m_id].predict(scaled)[0]
            if_pred = self.if_models[m_id].predict(scaled)[0]
            
            detectors = []
            if svm_pred == -1: detectors.append("One-Class SVM")
            if if_pred == -1: detectors.append("Isolation Forest")
            
            # DEBUG LOGGING
            with open("ml_debug.log", "a") as f:
                f.write(f"{m_id} | sensors: {features} | scaled: {scaled[0]} | svm: {svm_pred} | iso: {if_pred} | detectors: {detectors}\n")
            
            if len(detectors) > 0: # Anomaly caught by at least one model
                self.machine_status[m_id] = "alert"
                
                # Determine which sensor deviated the most
                deviations = np.abs(scaled[0])
                worst_idx = np.argmax(deviations)
                worst_sensor = list(sensors.keys())[worst_idx]
                worst_val = features[worst_idx]
                
                # Ask SLM to analyze
                slm_msg = self.slm_client.generate_alert(m_id, worst_sensor, worst_val)
                
                new_alerts.append({
                    "id": f"ALM-{int(time.time()*1000)}",
                    "timestamp": time.strftime("%H:%M:%S"),
                    "machine_id": m_id,
                    "sensor": worst_sensor,
                    "value": round(worst_val, 2),
                    "slm_analysis": slm_msg,
                    "detected_by": ", ".join(detectors),
                    "severity": "critical"
                })
                
        return new_alerts
