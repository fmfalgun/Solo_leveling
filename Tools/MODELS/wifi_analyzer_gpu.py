"""
Real-Time WiFi AI Analyzer - GPU + Model Persistence Edition
Enhanced version with:
- Model save/load between runs
- GPU acceleration
- 60-second flow timeout (reduced from 5 min)
- 10-packet sequences (reduced from 20)

Install: sudo pip3 install scapy numpy pandas scikit-learn xgboost tensorflow
"""

import subprocess, threading, time, signal, sys, os, pickle
from collections import defaultdict, deque
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
import pandas as pd
from scapy.all import sniff, IP, TCP, UDP, ICMP
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
import warnings
warnings.filterwarnings('ignore')

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except: XGBOOST_AVAILABLE = False

# TensorFlow GPU setup
try:
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, LSTM, Dropout, Conv1D, MaxPooling1D, Flatten
    from tensorflow.keras.optimizers import Adam
    
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print(f"[+] GPU enabled: {len(gpus)} GPU(s)")
    else:
        print("[*] CPU mode")
    TENSORFLOW_AVAILABLE = True
except:
    TENSORFLOW_AVAILABLE = False
    print("[!] TensorFlow unavailable")

# Model persistence
MODEL_DIR = Path("saved_models")
MODEL_DIR.mkdir(exist_ok=True)

class LivePacketCapture:
    def __init__(self, interface='wlan0'):
        self.interface = interface
        self.capture_active = False
        self.packet_count = 0
    
    def list_interfaces(self):
        try:
            result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True)
            print("\n=== Available Interfaces ===\n" + result.stdout)
        except Exception as e:
            print(f"Error: {e}")
    
    def start_capture(self, prn=None):
        self.capture_active = True
        print(f"\n[*] Capturing on {self.interface}...")
        try:
            sniff(iface=self.interface, prn=prn, store=False, 
                  stop_filter=lambda x: not self.capture_active)
        except PermissionError:
            print("\n[!] Run with sudo!")
            sys.exit(1)
        except Exception as e:
            print(f"[!] Error: {e}")
    
    def stop_capture(self):
        self.capture_active = False

class RealTimeFeatureExtractor:
    def __init__(self, sequence_length=10, flow_timeout=60):
        self.sequence_length = sequence_length
        self.flow_timeout = flow_timeout
        self.flow_sequences = defaultdict(lambda: deque(maxlen=sequence_length))
        self.flow_stats = defaultdict(lambda: {
            'packet_count': 0, 'byte_count': 0, 'start_time': None,
            'last_time': None, 'src_ip': None, 'dst_ip': None,
            'src_port': None, 'dst_port': None, 'protocol': None,
            'completed': False
        })
        self.lock = threading.Lock()
    
    def update_flow_stats(self, packet):
        if not packet.haslayer(IP):
            return None
        
        flow_key = self._get_flow_key(packet)
        if not flow_key:
            return None
        
        with self.lock:
            stats = self.flow_stats[flow_key]
            current_time = time.time()
            
            stats['packet_count'] += 1
            stats['byte_count'] += len(packet)
            if stats['start_time'] is None:
                stats['start_time'] = current_time
            stats['last_time'] = current_time
            
            ip = packet[IP]
            stats['src_ip'] = ip.src
            stats['dst_ip'] = ip.dst
            
            if packet.haslayer(TCP):
                stats['protocol'] = 'TCP'
                stats['src_port'] = packet[TCP].sport
                stats['dst_port'] = packet[TCP].dport
                if packet[TCP].flags.F or packet[TCP].flags.R:
                    stats['completed'] = True
            elif packet.haslayer(UDP):
                stats['protocol'] = 'UDP'
                stats['src_port'] = packet[UDP].sport
                stats['dst_port'] = packet[UDP].dport
            
            self.flow_sequences[flow_key].append([
                len(packet), ip.ttl,
                packet[TCP].window if packet.haslayer(TCP) else 0,
                1 if packet.haslayer(TCP) else 0,
                1 if packet.haslayer(UDP) else 0
            ])
        
        return flow_key
    
    def check_completed_flows(self):
        current_time = time.time()
        completed = []
        with self.lock:
            for flow_key, stats in list(self.flow_stats.items()):
                time_since = current_time - stats['last_time'] if stats['last_time'] else 0
                if stats['packet_count'] >= 5 and (
                    stats['completed'] or 
                    time_since > self.flow_timeout or
                    (stats['packet_count'] >= 10 and time_since > 30)
                ):
                    completed.append(flow_key)
        return completed
    
    def get_flow_features(self, flow_key):
        with self.lock:
            stats = self.flow_stats.get(flow_key)
            if not stats or stats['packet_count'] < 2:
                return None
            
            duration = stats['last_time'] - stats['start_time'] if stats['start_time'] else 0
            return {
                'flow_duration': duration,
                'flow_packet_count': stats['packet_count'],
                'flow_byte_count': stats['byte_count'],
                'flow_bytes_per_packet_mean': stats['byte_count'] / stats['packet_count'],
                'src_ip': stats['src_ip'],
                'dst_ip': stats['dst_ip'],
                'src_port': stats.get('src_port', 0),
                'dst_port': stats.get('dst_port', 0)
            }
    
    def get_flow_sequence(self, flow_key):
        with self.lock:
            seq = list(self.flow_sequences.get(flow_key, []))
            if len(seq) < self.sequence_length:
                padding = [[0]*5] * (self.sequence_length - len(seq))
                seq = padding + seq
            return np.array(seq[-self.sequence_length:])
    
    def remove_flow(self, flow_key):
        with self.lock:
            self.flow_stats.pop(flow_key, None)
            self.flow_sequences.pop(flow_key, None)
    
    def get_active_flow_count(self):
        with self.lock:
            return len(self.flow_stats)
    
    def _get_flow_key(self, packet):
        if not packet.haslayer(IP):
            return None
        src_ip, dst_ip = packet[IP].src, packet[IP].dst
        if packet.haslayer(TCP):
            return tuple(sorted([(src_ip, packet[TCP].sport), (dst_ip, packet[TCP].dport)]) + ['TCP'])
        elif packet.haslayer(UDP):
            return tuple(sorted([(src_ip, packet[UDP].sport), (dst_ip, packet[UDP].dport)]) + ['UDP'])
        return tuple(sorted([(src_ip, 0), (dst_ip, 0)]) + ['OTHER'])

class ParallelModelPredictor:
    def __init__(self, models):
        self.models = models
        self.executor = ThreadPoolExecutor(max_workers=6)
    
    def predict_all_parallel(self, X, X_scaled, X_seq):
        futures = {}
        results = {'models_used': []}
        
        if self.models['isolation_forest']:
            futures['if'] = self.executor.submit(
                lambda: {'scores': self.models['isolation_forest'].score_samples(X_scaled),
                        'predictions': self.models['isolation_forest'].predict(X_scaled)})
        
        if self.models['autoencoder'] and TENSORFLOW_AVAILABLE:
            futures['ae'] = self.executor.submit(
                lambda: self._predict_ae(X_scaled))
        
        if self.models['xgboost_classifier']:
            futures['xgb'] = self.executor.submit(
                lambda: {'predictions': self.models['xgboost_classifier'].predict(X),
                        'confidence': np.max(self.models['xgboost_classifier'].predict_proba(X), axis=1)})
        
        if self.models['lstm_classifier'] and len(X_seq) > 0 and TENSORFLOW_AVAILABLE:
            futures['lstm'] = self.executor.submit(
                lambda: self._predict_lstm(X_seq))
        
        if self.models['tcn_predictor'] and len(X_seq) > 0 and TENSORFLOW_AVAILABLE:
            futures['tcn'] = self.executor.submit(
                lambda: {'predictions': self.models['tcn_predictor'].predict(X_seq, verbose=0).flatten()})
        
        if self.models['rf_fingerprinter']:
            futures['rf'] = self.executor.submit(
                lambda: {'predictions': self.models['rf_fingerprinter'].predict(X),
                        'confidence': np.max(self.models['rf_fingerprinter'].predict_proba(X), axis=1)})
        
        for name, future in futures.items():
            try:
                result = future.result(timeout=5)
                if result:
                    if name == 'if':
                        results['isolation_forest_scores'] = result['scores']
                        results['isolation_forest_anomalies'] = result['predictions']
                        results['models_used'].append('Isolation Forest')
                    elif name == 'ae':
                        results['autoencoder_scores'] = result['scores']
                        results['autoencoder_anomalies'] = result['predictions']
                        results['models_used'].append('Autoencoder')
                    elif name == 'xgb':
                        results['xgboost_traffic_class'] = result['predictions']
                        results['xgboost_confidence'] = result['confidence']
                        results['models_used'].append('XGBoost')
                    elif name == 'lstm':
                        results['lstm_traffic_class'] = result['predictions']
                        results['lstm_confidence'] = result['confidence']
                        results['models_used'].append('LSTM')
                    elif name == 'tcn':
                        results['tcn_throughput'] = result['predictions']
                        results['models_used'].append('TCN')
                    elif name == 'rf':
                        results['rf_device_id'] = result['predictions']
                        results['rf_device_confidence'] = result['confidence']
                        results['models_used'].append('Random Forest')
            except:
                pass
        
        return results
    
    def _predict_ae(self, X_scaled):
        recon = self.models['autoencoder'].predict(X_scaled, verbose=0)
        mse = np.mean(np.power(X_scaled - recon, 2), axis=1)
        anomalies = np.where((mse > self.models['autoencoder_threshold']), -1, 1)
        return {'scores': -mse, 'predictions': anomalies}
    
    def _predict_lstm(self, X_seq):
        pred = np.argmax(self.models['lstm_classifier'].predict(X_seq, verbose=0), axis=1)
        proba = self.models['lstm_classifier'].predict(X_seq, verbose=0)
        return {'predictions': pred, 'confidence': np.max(proba, axis=1)}

class MultiModelAnalyzer:
    def __init__(self):
        self.models = {
            'isolation_forest': None, 'autoencoder': None, 'autoencoder_threshold': None,
            'xgboost_classifier': None, 'lstm_classifier': None,
            'tcn_predictor': None, 'rf_fingerprinter': None
        }
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.training_data = []
        self.models_trained = False
        self.min_samples = 15
        self.parallel_predictor = None
    
    def save_models(self):
        try:
            print("\n[*] Saving models...")
            if self.models['isolation_forest']:
                with open(MODEL_DIR / 'if.pkl', 'wb') as f:
                    pickle.dump(self.models['isolation_forest'], f)
            if self.models['xgboost_classifier']:
                with open(MODEL_DIR / 'xgb.pkl', 'wb') as f:
                    pickle.dump(self.models['xgboost_classifier'], f)
            if self.models['rf_fingerprinter']:
                with open(MODEL_DIR / 'rf.pkl', 'wb') as f:
                    pickle.dump(self.models['rf_fingerprinter'], f)
            if self.models['autoencoder_threshold']:
                with open(MODEL_DIR / 'ae_thresh.pkl', 'wb') as f:
                    pickle.dump(self.models['autoencoder_threshold'], f)
            
            if TENSORFLOW_AVAILABLE:
                if self.models['autoencoder']:
                    self.models['autoencoder'].save(MODEL_DIR / 'ae.h5')
                if self.models['lstm_classifier']:
                    self.models['lstm_classifier'].save(MODEL_DIR / 'lstm.h5')
                if self.models['tcn_predictor']:
                    self.models['tcn_predictor'].save(MODEL_DIR / 'tcn.h5')
            
            with open(MODEL_DIR / 'scaler.pkl', 'wb') as f:
                pickle.dump(self.scaler, f)
            with open(MODEL_DIR / 'features.pkl', 'wb') as f:
                pickle.dump(self.feature_columns, f)
            
            print("[+] ✓ Models saved")
        except Exception as e:
            print(f"[!] Save error: {e}")
    
    def load_models(self):
        try:
            print("\n[*] Loading saved models...")
            count = 0
            
            if (MODEL_DIR / 'if.pkl').exists():
                with open(MODEL_DIR / 'if.pkl', 'rb') as f:
                    self.models['isolation_forest'] = pickle.load(f)
                count += 1
            
            if (MODEL_DIR / 'xgb.pkl').exists():
                with open(MODEL_DIR / 'xgb.pkl', 'rb') as f:
                    self.models['xgboost_classifier'] = pickle.load(f)
                count += 1
            
            if (MODEL_DIR / 'rf.pkl').exists():
                with open(MODEL_DIR / 'rf.pkl', 'rb') as f:
                    self.models['rf_fingerprinter'] = pickle.load(f)
                count += 1
            
            if (MODEL_DIR / 'ae_thresh.pkl').exists():
                with open(MODEL_DIR / 'ae_thresh.pkl', 'rb') as f:
                    self.models['autoencoder_threshold'] = pickle.load(f)
            
            if TENSORFLOW_AVAILABLE:
                if (MODEL_DIR / 'ae.h5').exists():
                    self.models['autoencoder'] = tf.keras.models.load_model(MODEL_DIR / 'ae.h5')
                    count += 1
                if (MODEL_DIR / 'lstm.h5').exists():
                    self.models['lstm_classifier'] = tf.keras.models.load_model(MODEL_DIR / 'lstm.h5')
                    count += 1
                if (MODEL_DIR / 'tcn.h5').exists():
                    self.models['tcn_predictor'] = tf.keras.models.load_model(MODEL_DIR / 'tcn.h5')
                    count += 1
            
            if (MODEL_DIR / 'scaler.pkl').exists():
                with open(MODEL_DIR / 'scaler.pkl', 'rb') as f:
                    self.scaler = pickle.load(f)
            if (MODEL_DIR / 'features.pkl').exists():
                with open(MODEL_DIR / 'features.pkl', 'rb') as f:
                    self.feature_columns = pickle.load(f)
            
            if count >= 3:
                self.models_trained = True
                self.parallel_predictor = ParallelModelPredictor(self.models)
                print(f"[+] ✓ Loaded {count} models - READY!")
                return True
            print(f"[*] Found {count} models, need training")
            return False
        except Exception as e:
            print(f"[!] Load error: {e}")
            return False
    
    def train_all_models(self, flow_features, sequences):
        print("\n" + "="*70)
        print("TRAINING 6 AI MODELS")
        print("="*70)
        
        X, _ = self._prepare_features(flow_features)
        if X is None or len(X) < self.min_samples:
            print(f"[!] Need {self.min_samples}, got {len(X) if X is not None else 0}")
            return False
        
        X_scaled = self.scaler.fit_transform(X)
        
        # Prepare sequences with padding for ALL flows
        X_seq_all = []
        for seq in sequences:
            if len(seq) > 0:
                X_seq_all.append(seq)
            else:
                # Create dummy sequence for flows without enough packets
                X_seq_all.append(np.zeros((10, 5)))
        X_seq_all = np.array(X_seq_all) if X_seq_all else np.array([])
        
        # Train models
        print("[1/6] Isolation Forest...")
        self.models['isolation_forest'] = IsolationForest(contamination=0.1, random_state=42)
        self.models['isolation_forest'].fit(X_scaled)
        print("      ✓ Done")
        
        if TENSORFLOW_AVAILABLE:
            print("[2/6] Autoencoder...")
            input_dim = X_scaled.shape[1]
            enc_dim = max(input_dim // 2, 8)
            ae = Sequential([
                Dense(enc_dim, activation='relu', input_shape=(input_dim,)),
                Dense(enc_dim // 2, activation='relu'),
                Dense(enc_dim // 4, activation='relu'),
                Dense(enc_dim // 2, activation='relu'),
                Dense(enc_dim, activation='relu'),
                Dense(input_dim, activation='linear')
            ])
            ae.compile(optimizer=Adam(0.001), loss='mse')
            ae.fit(X_scaled, X_scaled, epochs=20, batch_size=32, verbose=0)
            self.models['autoencoder'] = ae
            recon = ae.predict(X_scaled, verbose=0)
            mse = np.mean(np.power(X_scaled - recon, 2), axis=1)
            self.models['autoencoder_threshold'] = np.percentile(mse, 90)
            print("      ✓ Done")
        
        if XGBOOST_AVAILABLE:
            print("[3/6] XGBoost...")
            kmeans = KMeans(n_clusters=min(5, max(2, len(X)//4)), random_state=42)
            labels = kmeans.fit_predict(X_scaled)
            self.models['xgboost_classifier'] = xgb.XGBClassifier(
                n_estimators=100, max_depth=6, random_state=42, verbosity=0)
            self.models['xgboost_classifier'].fit(X, labels)
            print("      ✓ Done")
        
        # LSTM - Relaxed requirements (train with 10+ flows)
        if TENSORFLOW_AVAILABLE and len(X_seq_all) >= 10:
            print("[4/6] LSTM...")
            try:
                y_seq = labels[:len(X_seq_all)]
                n_classes = max(2, len(np.unique(y_seq)))
                lstm = Sequential([
                    LSTM(32, input_shape=(X_seq_all.shape[1], X_seq_all.shape[2]), return_sequences=True),
                    Dropout(0.2),
                    LSTM(16),
                    Dropout(0.2),
                    Dense(16, activation='relu'),
                    Dense(n_classes, activation='softmax')
                ])
                lstm.compile(optimizer=Adam(0.001), loss='sparse_categorical_crossentropy')
                lstm.fit(X_seq_all, y_seq, epochs=10, batch_size=8, verbose=0)
                self.models['lstm_classifier'] = lstm
                print("      ✓ Done")
            except Exception as e:
                print(f"      ✗ Failed: {e}")
        else:
            print("[4/6] LSTM... ✗ Need 10+ flows with sequences")
        
        # TCN - Relaxed requirements (train with 10+ flows)
        if TENSORFLOW_AVAILABLE and len(X_seq_all) >= 10:
            print("[5/6] TCN...")
            try:
                throughput = X[:len(X_seq_all), 2] / (X[:len(X_seq_all), 0] + 1)
                tcn = Sequential([
                    Conv1D(32, 3, activation='relu', padding='same', 
                           input_shape=(X_seq_all.shape[1], X_seq_all.shape[2])),
                    Conv1D(32, 3, activation='relu', padding='same', dilation_rate=2),
                    Conv1D(16, 3, activation='relu', padding='same', dilation_rate=4),
                    MaxPooling1D(2),
                    Flatten(),
                    Dense(16, activation='relu'),
                    Dense(1, activation='linear')
                ])
                tcn.compile(optimizer=Adam(0.001), loss='mse')
                tcn.fit(X_seq_all, throughput, epochs=10, batch_size=8, verbose=0)
                self.models['tcn_predictor'] = tcn
                print("      ✓ Done")
            except Exception as e:
                print(f"      ✗ Failed: {e}")
        else:
            print("[5/6] TCN... ✗ Need 10+ flows with sequences")
        
        # Random Forest - Relaxed requirements (train with 5+ clustered devices)
        print("[6/6] Random Forest...")
        try:
            dbscan = DBSCAN(eps=1.0, min_samples=2)  # More lenient clustering
            dev_labels = dbscan.fit_predict(X_scaled)
            valid = dev_labels != -1
            
            if np.sum(valid) >= 5:  # Reduced from 10 to 5
                self.models['rf_fingerprinter'] = RandomForestClassifier(
                    n_estimators=50, max_depth=8, random_state=42)
                self.models['rf_fingerprinter'].fit(X[valid], dev_labels[valid])
                print(f"      ✓ Done ({len(np.unique(dev_labels[valid]))} devices)")
            else:
                print(f"      ✗ Need 5+ clustered flows (got {np.sum(valid)})")
        except Exception as e:
            print(f"      ✗ Failed: {e}")
        
        self.models_trained = True
        self.parallel_predictor = ParallelModelPredictor(self.models)
        
        trained_count = sum([
            self.models['isolation_forest'] is not None,
            self.models['autoencoder'] is not None,
            self.models['xgboost_classifier'] is not None,
            self.models['lstm_classifier'] is not None,
            self.models['tcn_predictor'] is not None,
            self.models['rf_fingerprinter'] is not None
        ])
        
        print("\n" + "="*70)
        print(f"✓ TRAINING COMPLETE - {trained_count}/6 MODELS ACTIVE")
        print("="*70)
        
        # Auto-save after training
        self.save_models()
        
        return True
    
    def predict_all(self, flow_features, sequences):
        if not self.models_trained:
            return None
        
        X, _ = self._prepare_features(flow_features)
        if X is None:
            return None
        
        X_scaled = self.scaler.transform(X)
        X_seq = np.array([s for s in sequences if len(s) > 0]) if sequences else np.array([])
        
        results = self.parallel_predictor.predict_all_parallel(X, X_scaled, X_seq)
        results['flow_count'] = len(X)
        return results
    
    def _prepare_features(self, flow_features):
        if not flow_features:
            return None, None
        df = pd.DataFrame(flow_features)
        numerical = [c for c in df.columns if c not in ['src_ip', 'dst_ip', 'protocol']]
        X = df[numerical].fillna(0)
        if self.feature_columns is None:
            self.feature_columns = X.columns.tolist()
        for col in self.feature_columns:
            if col not in X.columns:
                X[col] = 0
        return X[self.feature_columns].values, None

class RealTimeMultiModelAnalyzer:
    def __init__(self):
        self.extractor = RealTimeFeatureExtractor(sequence_length=10, flow_timeout=60)
        self.analyzer = MultiModelAnalyzer()
        self.last_analysis = time.time()
        self.last_debug = time.time()
        self.total_packets = 0
        self.total_flows_processed = 0
        self.total_anomalies_if = 0
        self.total_anomalies_ae = 0
    
    def process_packet(self, packet):
        self.total_packets += 1
        flow_key = self.extractor.update_flow_stats(packet)
        
        current = time.time()
        if current - self.last_debug >= 5:
            active = self.extractor.get_active_flow_count()
            print(f"[DEBUG {datetime.now().strftime('%H:%M:%S')}] "
                  f"Packets: {self.total_packets:,} | Active: {active} | "
                  f"Processed: {self.total_flows_processed} | "
                  f"Models: {'✓ TRAINED' if self.analyzer.models_trained else '✗ Training...'}")
            self.last_debug = current
        
        completed = self.extractor.check_completed_flows()
        if completed:
            self._process_completed_flows(completed)
        
        if current - self.last_analysis >= 15:
            if self.analyzer.models_trained:
                self.analyze_all_active_flows()
            self.last_analysis = current
    
    def _process_completed_flows(self, completed_keys):
        features, sequences = [], []
        for key in completed_keys:
            feat = self.extractor.get_flow_features(key)
            if feat:
                features.append(feat)
                sequences.append(self.extractor.get_flow_sequence(key))
                self.total_flows_processed += 1
        
        if not features:
            return
        
        if not self.analyzer.models_trained:
            total = len(self.analyzer.training_data) + len(features)
            if total >= 15:
                print(f"\n[*] Training with {total} flows...")
                all_features = self.analyzer.training_data + features
                self.analyzer.train_all_models(all_features, sequences)
            else:
                self.analyzer.training_data.extend(features)
                print(f"[*] Collecting... ({total}/15)")
        elif self.analyzer.models_trained:
            results = self.analyzer.predict_all(features, sequences)
            if results:
                print(f"\n{'='*70}")
                print(f"[{datetime.now().strftime('%H:%M:%S')}] COMPLETED FLOWS ({len(features)})")
                print(f"{'='*70}")
                print(f"  Models: {', '.join(results['models_used'])}")
                
                if 'isolation_forest_anomalies' in results:
                    anom = np.sum(results['isolation_forest_anomalies'] == -1)
                    if anom > 0:
                        self.total_anomalies_if += anom
                        print(f"  [IF] ⚠ {anom}/{results['flow_count']} anomalies")
                
                if 'autoencoder_anomalies' in results:
                    anom = np.sum(results['autoencoder_anomalies'] == -1)
                    if anom > 0:
                        self.total_anomalies_ae += anom
                        print(f"  [AE] ⚠ {anom}/{results['flow_count']} anomalies")
                
                if 'xgboost_traffic_class' in results:
                    classes = np.unique(results['xgboost_traffic_class'])
                    print(f"  [XGB] Classes: {list(classes[:3])}")
                
                print(f"{'='*70}\n")
        
        for key in completed_keys:
            self.extractor.remove_flow(key)
    
    def analyze_all_active_flows(self):
        features, sequences = [], []
        for key in list(self.extractor.flow_stats.keys()):
            feat = self.extractor.get_flow_features(key)
            if feat:
                features.append(feat)
                sequences.append(self.extractor.get_flow_sequence(key))
        
        if not features:
            return
        
        results = self.analyzer.predict_all(features, sequences)
        if results:
            print(f"\n{'='*70}")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] PERIODIC ANALYSIS")
            print(f"{'='*70}")
            print(f"Models: {', '.join(results['models_used'])}")
            print(f"Active Flows: {results['flow_count']}")
            print(f"{'='*70}")
            
            if 'isolation_forest_anomalies' in results:
                anom = np.sum(results['isolation_forest_anomalies'] == -1)
                print(f"\n[IF] Anomalies: {anom}/{results['flow_count']} ({anom/results['flow_count']*100:.1f}%)")
            
            if 'autoencoder_anomalies' in results:
                anom = np.sum(results['autoencoder_anomalies'] == -1)
                print(f"[AE] Anomalies: {anom}/{results['flow_count']} ({anom/results['flow_count']*100:.1f}%)")
            
            if 'xgboost_traffic_class' in results:
                classes, counts = np.unique(results['xgboost_traffic_class'], return_counts=True)
                print(f"\n[XGB] Classes: {len(classes)}")
                for cls, cnt in zip(classes[:3], counts[:3]):
                    print(f"  Class {cls}: {cnt} ({cnt/results['flow_count']*100:.1f}%)")
            
            if 'lstm_traffic_class' in results:
                print(f"\n[LSTM] Patterns: {len(np.unique(results['lstm_traffic_class']))}")
            
            if 'tcn_throughput' in results:
                print(f"[TCN] Throughput: Avg={np.mean(results['tcn_throughput']):.1f} bytes/sec")
            
            if 'rf_device_id' in results:
                print(f"[RF] Devices: {len(np.unique(results['rf_device_id']))}")
            
            print(f"{'='*70}\n")
    
    def display_final_summary(self):
        print(f"\n{'='*70}")
        print("FINAL SUMMARY")
        print(f"{'='*70}")
        print(f"Packets: {self.total_packets:,}")
        print(f"Flows Processed: {self.total_flows_processed:,}")
        print(f"Active Flows: {self.extractor.get_active_flow_count()}")
        print(f"Models Trained: {'Yes' if self.analyzer.models_trained else 'No'}")
        
        if self.analyzer.models_trained:
            print(f"\nAnomalies Detected:")
            print(f"  Isolation Forest: {self.total_anomalies_if}")
            print(f"  Autoencoder: {self.total_anomalies_ae}")
        
        print(f"{'='*70}\n")

def signal_handler(sig, frame):
    print("\n[*] Shutting down...")
    sys.exit(0)

def main():
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║   WiFi AI Analyzer - GPU + Model Persistence Edition          ║
    ║              6 Models Running in Parallel                      ║
    ╚════════════════════════════════════════════════════════════════╝
    
    Enhanced Features:
    ✓ GPU acceleration (TensorFlow models)
    ✓ Model persistence (saves/loads between runs)
    ✓ 60-second flow timeout (faster processing)
    ✓ 10-packet sequences (easier to train)
    ✓ Parallel execution (all 6 models simultaneously)
    
    Models:
    1. Isolation Forest  → Anomaly Detection
    2. Autoencoder       → Deep Anomaly Detection
    3. XGBoost           → Traffic Classification
    4. LSTM              → Sequential Analysis
    5. TCN               → Throughput Prediction
    6. Random Forest     → Device Fingerprinting
    """)
    
    if os.geteuid() != 0:
        print("[!] Run with sudo!")
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    capture = LivePacketCapture()
    capture.list_interfaces()
    
    interface = input("\n[?] Interface (default: wlan0): ").strip()
    if interface:
        capture.interface = interface
    
    analyzer = RealTimeMultiModelAnalyzer()
    
    # Try loading saved models
    analyzer.analyzer.load_models()
    
    print("\n[*] Starting capture...")
    print("[*] System features:")
    print("    - Auto-saves models after training")
    print("    - Processes flows after 60s timeout or 10+ packets")
    print("    - Debug every 5s, analysis every 15s")
    print("    - Press Ctrl+C to stop\n")
    
    try:
        capture.start_capture(prn=analyzer.process_packet)
    except KeyboardInterrupt:
        print("\n[*] Stopping...")
    finally:
        capture.stop_capture()
        analyzer.display_final_summary()
        
        # Save models on exit
        if analyzer.analyzer.models_trained:
            analyzer.analyzer.save_models()
        
        print("[+] Complete!")

if __name__ == "__main__":
    main()