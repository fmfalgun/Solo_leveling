"""
Real-Time WiFi Traffic Capture & Multi-Model AI Analysis System
Uses 6 AI models concurrently with parallel processing
Optimized for Kali Linux

Requirements:
sudo pip3 install scapy numpy pandas scikit-learn xgboost lightgbm tensorflow psutil

System Requirements (Kali Linux):
- Root/sudo privileges for packet capture
"""

import subprocess
import threading
import queue
import time
import signal
import sys
import os
from collections import defaultdict, deque
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd
from scapy.all import sniff, IP, TCP, UDP, ICMP

try:
    from sklearn.ensemble import IsolationForest, RandomForestClassifier, RandomForestRegressor
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.cluster import KMeans, DBSCAN
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("[!] scikit-learn not available. Please install: sudo pip3 install scikit-learn")
    sys.exit(1)

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("[!] XGBoost not available. Install: sudo pip3 install xgboost")

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    print("[!] LightGBM not available. Install: sudo pip3 install lightgbm")

import warnings
warnings.filterwarnings('ignore')

# TensorFlow for deep learning models
try:
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    import tensorflow as tf
    from tensorflow.keras.models import Model, Sequential
    from tensorflow.keras.layers import Input, Dense, LSTM, Dropout, Conv1D, MaxPooling1D, Flatten, Reshape
    from tensorflow.keras.optimizers import Adam
    tf.get_logger().setLevel('ERROR')
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("[!] TensorFlow not available. Deep learning models will be disabled.")
    print("    Install: sudo pip3 install tensorflow")


class LivePacketCapture:
    """Live packet capture using Scapy"""
    
    def __init__(self, interface='wlan0'):
        self.interface = interface
        self.capture_active = False
        self.packet_count = 0
        
    def list_interfaces(self):
        """List available network interfaces"""
        try:
            result = subprocess.run(['ip', 'link', 'show'], 
                                  capture_output=True, text=True)
            print("\n=== Available Network Interfaces ===")
            print(result.stdout)
            
            result = subprocess.run(['iwconfig'], 
                                  capture_output=True, text=True, stderr=subprocess.DEVNULL)
            if result.stdout:
                print("\n=== Wireless Interfaces ===")
                print(result.stdout)
        except Exception as e:
            print(f"Error listing interfaces: {e}")
    
    def enable_monitor_mode(self):
        """Enable monitor mode on wireless interface"""
        print(f"\n[*] Attempting to enable monitor mode on {self.interface}...")
        try:
            subprocess.run(['sudo', 'airmon-ng', 'check', 'kill'], 
                         capture_output=True)
            
            result = subprocess.run(['sudo', 'airmon-ng', 'start', self.interface], 
                                  capture_output=True, text=True)
            print(result.stdout)
            
            if 'mon' in result.stdout:
                self.interface = self.interface + 'mon'
                print(f"[+] Monitor mode enabled on {self.interface}")
                return True
            else:
                print("[!] Monitor mode may already be enabled")
                return True
                
        except Exception as e:
            print(f"[!] Error enabling monitor mode: {e}")
            print("[*] Continuing with managed mode...")
            return False
    
    def disable_monitor_mode(self):
        """Disable monitor mode"""
        try:
            original_interface = self.interface.replace('mon', '')
            subprocess.run(['sudo', 'airmon-ng', 'stop', self.interface], 
                         capture_output=True)
            print(f"[+] Monitor mode disabled on {original_interface}")
        except Exception as e:
            print(f"[!] Error disabling monitor mode: {e}")
    
    def start_capture(self, prn=None):
        """Start live packet capture"""
        self.capture_active = True
        self.packet_count = 0
        
        print(f"\n[*] Starting continuous packet capture on interface: {self.interface}")
        print(f"[*] Press Ctrl+C to stop capture")
        
        try:
            sniff(
                iface=self.interface,
                prn=prn,
                store=False,
                stop_filter=lambda x: not self.capture_active
            )
            
        except PermissionError:
            print("\n[!] ERROR: Permission denied. Please run with sudo:")
            print(f"    sudo python3 {sys.argv[0]}")
            sys.exit(1)
        except Exception as e:
            print(f"\n[!] Capture error: {e}")
        finally:
            self.capture_active = False
    
    def stop_capture(self):
        """Stop packet capture"""
        self.capture_active = False
        print(f"\n[+] Capture stopped. Total packets: {self.packet_count}")


class RealTimeFeatureExtractor:
    """Extract features from packets in real-time"""
    
    def __init__(self, window_size=50, sequence_length=20, flow_timeout=300):
        self.window_size = window_size
        self.sequence_length = sequence_length
        self.flow_timeout = flow_timeout  # 5 minutes = 300 seconds
        self.flow_windows = defaultdict(lambda: deque(maxlen=window_size))
        self.flow_sequences = defaultdict(lambda: deque(maxlen=sequence_length))
        self.flow_stats = defaultdict(lambda: {
            'packet_count': 0,
            'byte_count': 0,
            'start_time': None,
            'last_time': None,
            'src_ip': None,
            'dst_ip': None,
            'src_port': None,
            'dst_port': None,
            'protocol': None,
            'packet_sizes': [],
            'inter_arrival_times': [],
            'completed': False
        })
        self.lock = threading.Lock()
    
    def extract_packet_features(self, packet):
        """Extract features from single packet"""
        features = {
            'timestamp': time.time(),
            'packet_length': len(packet),
            'has_ip': 0,
            'has_tcp': 0,
            'has_udp': 0,
            'has_icmp': 0,
            'ip_len': 0,
            'ip_ttl': 0,
            'ip_proto': 0,
            'tcp_window': 0,
            'flag_syn': 0,
            'flag_ack': 0,
            'flag_fin': 0,
            'flag_rst': 0,
            'flag_psh': 0,
            'udp_len': 0
        }
        
        if packet.haslayer(IP):
            features['has_ip'] = 1
            ip = packet[IP]
            features['ip_len'] = ip.len
            features['ip_ttl'] = ip.ttl
            features['ip_proto'] = ip.proto
            features['src_ip'] = ip.src
            features['dst_ip'] = ip.dst
            
            if packet.haslayer(TCP):
                features['has_tcp'] = 1
                tcp = packet[TCP]
                features['src_port'] = tcp.sport
                features['dst_port'] = tcp.dport
                features['tcp_window'] = tcp.window
                features['flag_syn'] = 1 if tcp.flags.S else 0
                features['flag_ack'] = 1 if tcp.flags.A else 0
                features['flag_fin'] = 1 if tcp.flags.F else 0
                features['flag_rst'] = 1 if tcp.flags.R else 0
                features['flag_psh'] = 1 if tcp.flags.P else 0
                
            elif packet.haslayer(UDP):
                features['has_udp'] = 1
                udp = packet[UDP]
                features['src_port'] = udp.sport
                features['dst_port'] = udp.dport
                features['udp_len'] = udp.len
            
            elif packet.haslayer(ICMP):
                features['has_icmp'] = 1
        
        return features
    
    def update_flow_stats(self, packet):
        """Update flow statistics with new packet"""
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
            stats['packet_sizes'].append(len(packet))
            
            if stats['start_time'] is None:
                stats['start_time'] = current_time
            else:
                inter_arrival = current_time - stats['last_time']
                stats['inter_arrival_times'].append(inter_arrival)
            
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
            
            self.flow_windows[flow_key].append({
                'length': len(packet),
                'time': current_time
            })
            
            packet_features = self.extract_packet_features(packet)
            self.flow_sequences[flow_key].append([
                packet_features.get('packet_length', 0),
                packet_features.get('ip_ttl', 0),
                packet_features.get('tcp_window', 0),
                packet_features.get('has_tcp', 0),
                packet_features.get('has_udp', 0)
            ])
        
        return flow_key
    
    def check_completed_flows(self):
        """Check for completed or timed-out flows (5 minute timeout)"""
        current_time = time.time()
        completed = []
        
        with self.lock:
            for flow_key, stats in list(self.flow_stats.items()):
                time_since_last = current_time - stats['last_time'] if stats['last_time'] else 0
                
                # Flow complete if: TCP FIN/RST, timeout (5 min), or has 5+ packets
                if stats['packet_count'] >= 5 and (
                    stats['completed'] or 
                    time_since_last > self.flow_timeout
                ):
                    completed.append(flow_key)
        
        return completed
    
    def get_flow_features(self, flow_key):
        """Get comprehensive features for a flow"""
        with self.lock:
            stats = self.flow_stats.get(flow_key)
            if not stats:
                return None
            
            window = list(self.flow_windows[flow_key])
            
            if len(window) < 2:
                return None
            
            lengths = [p['length'] for p in window]
            times = [p['time'] for p in window]
            intervals = [times[i] - times[i-1] for i in range(1, len(times))]
            
            features = {
                'flow_duration': stats['last_time'] - stats['start_time'] if stats['start_time'] else 0,
                'flow_packet_count': stats['packet_count'],
                'flow_byte_count': stats['byte_count'],
                'flow_bytes_per_packet_mean': np.mean(lengths),
                'flow_bytes_per_packet_std': np.std(lengths),
                'flow_bytes_per_packet_min': np.min(lengths),
                'flow_bytes_per_packet_max': np.max(lengths),
                'src_ip': stats['src_ip'],
                'dst_ip': stats['dst_ip'],
                'src_port': stats.get('src_port', 0),
                'dst_port': stats.get('dst_port', 0),
                'protocol': stats.get('protocol', 'OTHER')
            }
            
            if intervals:
                features['flow_inter_arrival_mean'] = np.mean(intervals)
                features['flow_inter_arrival_std'] = np.std(intervals)
                features['flow_inter_arrival_min'] = np.min(intervals)
                features['flow_inter_arrival_max'] = np.max(intervals)
            else:
                features['flow_inter_arrival_mean'] = 0
                features['flow_inter_arrival_std'] = 0
                features['flow_inter_arrival_min'] = 0
                features['flow_inter_arrival_max'] = 0
            
            return features
    
    def get_flow_sequence(self, flow_key, length=20):
        """Get sequence of packets for LSTM/TCN"""
        with self.lock:
            sequence = list(self.flow_sequences.get(flow_key, []))
            
            if len(sequence) < length:
                padding = [[0] * 5] * (length - len(sequence))
                sequence = padding + sequence
            else:
                sequence = sequence[-length:]
            
            return np.array(sequence)
    
    def remove_flow(self, flow_key):
        """Remove a completed flow from tracking"""
        with self.lock:
            if flow_key in self.flow_stats:
                del self.flow_stats[flow_key]
            if flow_key in self.flow_windows:
                del self.flow_windows[flow_key]
            if flow_key in self.flow_sequences:
                del self.flow_sequences[flow_key]
    
    def get_active_flow_count(self):
        """Thread-safe flow count"""
        with self.lock:
            return len(self.flow_stats)
    
    def _get_flow_key(self, packet):
        """Generate flow identifier"""
        if not packet.haslayer(IP):
            return None
        
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        
        if packet.haslayer(TCP):
            src_port = packet[TCP].sport
            dst_port = packet[TCP].dport
            proto = 'TCP'
        elif packet.haslayer(UDP):
            src_port = packet[UDP].sport
            dst_port = packet[UDP].dport
            proto = 'UDP'
        else:
            src_port = 0
            dst_port = 0
            proto = 'OTHER'
        
        return tuple(sorted([(src_ip, src_port), (dst_ip, dst_port)]) + [proto])


class ParallelModelPredictor:
    """Run all 6 models in parallel using ThreadPoolExecutor"""
    
    def __init__(self, models):
        self.models = models
        self.executor = ThreadPoolExecutor(max_workers=6)
    
    def predict_isolation_forest(self, X_scaled):
        """Model 1: Isolation Forest"""
        if self.models['isolation_forest']:
            scores = self.models['isolation_forest'].score_samples(X_scaled)
            predictions = self.models['isolation_forest'].predict(X_scaled)
            return {'scores': scores, 'predictions': predictions}
        return None
    
    def predict_autoencoder(self, X_scaled):
        """Model 2: Autoencoder"""
        if self.models['autoencoder'] and TENSORFLOW_AVAILABLE:
            reconstructions = self.models['autoencoder'].predict(X_scaled, verbose=0)
            mse = np.mean(np.power(X_scaled - reconstructions, 2), axis=1)
            ae_anomalies = (mse > self.models['autoencoder_threshold']).astype(int)
            ae_anomalies = np.where(ae_anomalies == 1, -1, 1)
            return {'scores': -mse, 'predictions': ae_anomalies}
        return None
    
    def predict_xgboost(self, X):
        """Model 3: XGBoost"""
        if self.models['xgboost_classifier']:
            pred = self.models['xgboost_classifier'].predict(X)
            proba = self.models['xgboost_classifier'].predict_proba(X)
            return {'predictions': pred, 'confidence': np.max(proba, axis=1)}
        return None
    
    def predict_lstm(self, X_seq):
        """Model 4: LSTM"""
        if self.models['lstm_classifier'] and len(X_seq) > 0 and TENSORFLOW_AVAILABLE:
            pred = np.argmax(self.models['lstm_classifier'].predict(X_seq, verbose=0), axis=1)
            proba = self.models['lstm_classifier'].predict(X_seq, verbose=0)
            return {'predictions': pred, 'confidence': np.max(proba, axis=1)}
        return None
    
    def predict_tcn(self, X_seq):
        """Model 5: TCN"""
        if self.models['tcn_predictor'] and len(X_seq) > 0 and TENSORFLOW_AVAILABLE:
            pred = self.models['tcn_predictor'].predict(X_seq, verbose=0).flatten()
            return {'predictions': pred}
        return None
    
    def predict_random_forest(self, X):
        """Model 6: Random Forest"""
        if self.models['rf_fingerprinter']:
            try:
                pred = self.models['rf_fingerprinter'].predict(X)
                proba = self.models['rf_fingerprinter'].predict_proba(X)
                return {'predictions': pred, 'confidence': np.max(proba, axis=1)}
            except:
                return None
        return None
    
    def predict_all_parallel(self, X, X_scaled, X_seq):
        """Run all models in parallel"""
        futures = {}
        results = {'models_used': []}
        
        # Submit all prediction tasks
        futures['isolation_forest'] = self.executor.submit(self.predict_isolation_forest, X_scaled)
        futures['autoencoder'] = self.executor.submit(self.predict_autoencoder, X_scaled)
        futures['xgboost'] = self.executor.submit(self.predict_xgboost, X)
        futures['lstm'] = self.executor.submit(self.predict_lstm, X_seq)
        futures['tcn'] = self.executor.submit(self.predict_tcn, X_seq)
        futures['random_forest'] = self.executor.submit(self.predict_random_forest, X)
        
        # Collect results as they complete
        for model_name, future in futures.items():
            try:
                result = future.result(timeout=5)  # 5 second timeout per model
                if result:
                    if model_name == 'isolation_forest':
                        results['isolation_forest_scores'] = result['scores']
                        results['isolation_forest_anomalies'] = result['predictions']
                        results['models_used'].append('Isolation Forest')
                    elif model_name == 'autoencoder':
                        results['autoencoder_scores'] = result['scores']
                        results['autoencoder_anomalies'] = result['predictions']
                        results['models_used'].append('Autoencoder')
                    elif model_name == 'xgboost':
                        results['xgboost_traffic_class'] = result['predictions']
                        results['xgboost_confidence'] = result['confidence']
                        results['models_used'].append('XGBoost')
                    elif model_name == 'lstm':
                        results['lstm_traffic_class'] = result['predictions']
                        results['lstm_confidence'] = result['confidence']
                        results['models_used'].append('LSTM')
                    elif model_name == 'tcn':
                        results['tcn_throughput'] = result['predictions']
                        results['models_used'].append('TCN')
                    elif model_name == 'random_forest':
                        results['rf_device_id'] = result['predictions']
                        results['rf_device_confidence'] = result['confidence']
                        results['models_used'].append('Random Forest')
            except Exception as e:
                pass  # Model failed, skip
        
        return results


class MultiModelAnalyzer:
    """Multi-model AI system with 6 concurrent models"""
    
    def __init__(self):
        self.models = {
            'isolation_forest': None,
            'autoencoder': None,
            'autoencoder_threshold': None,
            'xgboost_classifier': None,
            'lstm_classifier': None,
            'tcn_predictor': None,
            'rf_fingerprinter': None
        }
        
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.training_data = []
        self.models_trained = False
        self.min_samples_for_training = 20
        self.parallel_predictor = None
        
    def build_autoencoder(self, input_dim):
        """Build autoencoder"""
        if not TENSORFLOW_AVAILABLE:
            return None
        
        encoding_dim = max(input_dim // 2, 8)
        model = Sequential([
            Dense(encoding_dim, activation='relu', input_shape=(input_dim,)),
            Dense(encoding_dim // 2, activation='relu'),
            Dense(encoding_dim // 4, activation='relu'),
            Dense(encoding_dim // 2, activation='relu'),
            Dense(encoding_dim, activation='relu'),
            Dense(input_dim, activation='linear')
        ])
        model.compile(optimizer=Adam(0.001), loss='mse')
        return model
    
    def build_lstm_classifier(self, sequence_length, n_features, n_classes):
        """Build LSTM"""
        if not TENSORFLOW_AVAILABLE:
            return None
        
        model = Sequential([
            LSTM(64, input_shape=(sequence_length, n_features), return_sequences=True),
            Dropout(0.3),
            LSTM(32),
            Dropout(0.3),
            Dense(32, activation='relu'),
            Dense(n_classes, activation='softmax')
        ])
        model.compile(optimizer=Adam(0.001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        return model
    
    def build_tcn_predictor(self, sequence_length, n_features):
        """Build TCN"""
        if not TENSORFLOW_AVAILABLE:
            return None
        
        model = Sequential([
            Conv1D(64, 3, activation='relu', padding='same', input_shape=(sequence_length, n_features)),
            Conv1D(64, 3, activation='relu', padding='same', dilation_rate=2),
            Conv1D(32, 3, activation='relu', padding='same', dilation_rate=4),
            MaxPooling1D(2),
            Flatten(),
            Dense(32, activation='relu'),
            Dense(1, activation='linear')
        ])
        model.compile(optimizer=Adam(0.001), loss='mse', metrics=['mae'])
        return model
    
    def train_all_models(self, flow_features, sequences, verbose=True):
        """Train all 6 models"""
        if verbose:
            print("\n" + "="*70)
            print("TRAINING ALL 6 AI MODELS")
            print("="*70)
        
        X, ip_data = self._prepare_features(flow_features)
        
        if X is None or len(X) < self.min_samples_for_training:
            if verbose:
                print(f"[!] Not enough data (need {self.min_samples_for_training}, got {len(X) if X is not None else 0})")
            return False
        
        self.training_data.extend(flow_features)
        X_scaled = self.scaler.fit_transform(X)
        
        # Train all models
        if verbose:
            print(f"\n[1/6] Training Isolation Forest on {len(X)} flows...")
        self.models['isolation_forest'] = IsolationForest(contamination=0.1, random_state=42, n_estimators=100)
        self.models['isolation_forest'].fit(X_scaled)
        if verbose:
            print("      ✓ Isolation Forest trained")
        
        if TENSORFLOW_AVAILABLE:
            if verbose:
                print(f"\n[2/6] Training Autoencoder...")
            self.models['autoencoder'] = self.build_autoencoder(X_scaled.shape[1])
            if self.models['autoencoder']:
                self.models['autoencoder'].fit(X_scaled, X_scaled, epochs=20, batch_size=32, verbose=0, validation_split=0.2)
                reconstructions = self.models['autoencoder'].predict(X_scaled, verbose=0)
                mse = np.mean(np.power(X_scaled - reconstructions, 2), axis=1)
                self.models['autoencoder_threshold'] = np.percentile(mse, 90)
                if verbose:
                    print("      ✓ Autoencoder trained")
        
        if XGBOOST_AVAILABLE:
            if verbose:
                print(f"\n[3/6] Training XGBoost...")
            kmeans = KMeans(n_clusters=min(5, len(X) // 4), random_state=42)
            traffic_labels = kmeans.fit_predict(X_scaled)
            self.models['xgboost_classifier'] = xgb.XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, verbosity=0)
            self.models['xgboost_classifier'].fit(X, traffic_labels)
            if verbose:
                print(f"      ✓ XGBoost trained ({len(np.unique(traffic_labels))} classes)")
        
        if TENSORFLOW_AVAILABLE and len(sequences) >= self.min_samples_for_training:
            if verbose:
                print(f"\n[4/6] Training LSTM...")
            X_seq = np.array([seq for seq in sequences if len(seq) > 0])
            if len(X_seq) >= self.min_samples_for_training:
                y_seq = traffic_labels[:len(X_seq)]
                n_classes = len(np.unique(y_seq))
                self.models['lstm_classifier'] = self.build_lstm_classifier(X_seq.shape[1], X_seq.shape[2], n_classes)
                if self.models['lstm_classifier']:
                    self.models['lstm_classifier'].fit(X_seq, y_seq, epochs=15, batch_size=16, verbose=0, validation_split=0.2)
                    if verbose:
                        print("      ✓ LSTM trained")
        
        if TENSORFLOW_AVAILABLE and len(sequences) >= self.min_samples_for_training:
            if verbose:
                print(f"\n[5/6] Training TCN...")
            X_seq = np.array([seq for seq in sequences if len(seq) > 0])
            if len(X_seq) >= self.min_samples_for_training:
                throughput = X[:len(X_seq), 2] / (X[:len(X_seq), 0] + 1)
                self.models['tcn_predictor'] = self.build_tcn_predictor(X_seq.shape[1], X_seq.shape[2])
                if self.models['tcn_predictor']:
                    self.models['tcn_predictor'].fit(X_seq, throughput, epochs=15, batch_size=16, verbose=0, validation_split=0.2)
                    if verbose:
                        print("      ✓ TCN trained")
        
        if LIGHTGBM_AVAILABLE:
            if verbose:
                print(f"\n[6/6] Training Random Forest...")
            dbscan = DBSCAN(eps=0.5, min_samples=3)
            device_labels = dbscan.fit_predict(X_scaled)
            valid_idx = device_labels != -1
            if np.sum(valid_idx) >= 10:
                X_valid = X[valid_idx]
                y_valid = device_labels[valid_idx]
                self.models['rf_fingerprinter'] = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
                self.models['rf_fingerprinter'].fit(X_valid, y_valid)
                if verbose:
                    print(f"      ✓ Random Forest trained ({len(np.unique(y_valid))} devices)")
        
        self.models_trained = True
        self.parallel_predictor = ParallelModelPredictor(self.models)
        
        if verbose:
            print("\n" + "="*70)
            print("✓ ALL MODELS TRAINED - PARALLEL PROCESSING ENABLED")
            print("="*70)
        
        return True
    
    def predict_all(self, flow_features, sequences):
        """Run predictions with all 6 models IN PARALLEL"""
        if not self.models_trained or not self.parallel_predictor:
            return None
        
        X, ip_data = self._prepare_features(flow_features)
        if X is None:
            return None
        
        X_scaled = self.scaler.transform(X)
        X_seq = np.array([seq for seq in sequences if len(seq) > 0]) if sequences else np.array([])
        
        # Run all models in parallel
        results = self.parallel_predictor.predict_all_parallel(X, X_scaled, X_seq)
        results['flow_count'] = len(X)
        
        return results
    
    def _prepare_features(self, flow_features):
        """Convert flow features to numerical array"""
        if not flow_features:
            return None, None
        
        df = pd.DataFrame(flow_features)
        ip_data = df[['src_ip', 'dst_ip']].copy() if 'src_ip' in df.columns else None
        numerical_cols = [col for col in df.columns if col not in ['src_ip', 'dst_ip', 'protocol']]
        X = df[numerical_cols].fillna(0)
        
        if self.feature_columns is None:
            self.feature_columns = X.columns.tolist()
        
        for col in self.feature_columns:
            if col not in X.columns:
                X[col] = 0
        
        X = X[self.feature_columns]
        return X.values, ip_data


class RealTimeMultiModelAnalyzer:
    """Real-time continuous analysis with parallel model execution"""
    
    def __init__(self, analysis_interval=15, debug_interval=5):
        self.extractor = RealTimeFeatureExtractor(flow_timeout=300)  # 5 minute timeout
        self.analyzer = MultiModelAnalyzer()
        self.analysis_interval = analysis_interval
        self.debug_interval = debug_interval
        self.last_analysis = time.time()
        self.last_debug = time.time()
        
        # Statistics
        self.total_packets = 0
        self.total_flows_processed = 0
        self.total_anomalies_if = 0
        self.total_anomalies_ae = 0
        self.traffic_class_counts = defaultdict(int)
        self.device_counts = defaultdict(int)
        
        self.running = True
        
    def process_packet(self, packet):
        """Process single packet in real-time"""
        self.total_packets += 1
        
        # Extract features and update flow stats
        flow_key = self.extractor.update_flow_stats(packet)
        
        # Debug output every X seconds
        current_time = time.time()
        if current_time - self.last_debug >= self.debug_interval:
            self._print_debug_info()
            self.last_debug = current_time
        
        # Check for completed flows and analyze them immediately
        completed_flows = self.extractor.check_completed_flows()
        if completed_flows:
            self._process_completed_flows(completed_flows)
        
        # Periodic full analysis
        if current_time - self.last_analysis >= self.analysis_interval:
            if self.analyzer.models_trained:
                self.analyze_all_active_flows()
            self.last_analysis = current_time
    
    def _print_debug_info(self):
        """Print debug information every few seconds"""
        active_flows = self.extractor.get_active_flow_count()
        print(f"\n[DEBUG {datetime.now().strftime('%H:%M:%S')}] "
              f"Packets: {self.total_packets:,} | "
              f"Active Flows: {active_flows} | "
              f"Processed: {self.total_flows_processed} | "
              f"Models: {'✓ TRAINED' if self.analyzer.models_trained else '✗ Training...'}")
    
    def _process_completed_flows(self, completed_flow_keys):
        """Process completed flows immediately with PARALLEL model execution"""
        flow_features = []
        sequences = []
        
        for flow_key in completed_flow_keys:
            feat = self.extractor.get_flow_features(flow_key)
            if feat:
                flow_features.append(feat)
                seq = self.extractor.get_flow_sequence(flow_key)
                sequences.append(seq)
                self.total_flows_processed += 1
        
        if not flow_features:
            return
        
        # If models not trained yet, accumulate data and train when ready
        if not self.analyzer.models_trained:
            total_data = len(self.analyzer.training_data) + len(flow_features)
            if total_data >= 20:
                print(f"\n[*] Sufficient flows ({total_data}). Training all 6 models in parallel...")
                all_features = self.analyzer.training_data + flow_features
                all_sequences = sequences
                success = self.analyzer.train_all_models(all_features, all_sequences, verbose=True)
                if success:
                    print("[+] ✓ Models ready! All predictions now run in PARALLEL!")
            else:
                # Store for later training
                self.analyzer.training_data.extend(flow_features)
                print(f"[*] Collecting flows... ({total_data}/20 for training)")
        
        # If models are trained, analyze completed flows IN PARALLEL
        elif self.analyzer.models_trained:
            results = self.analyzer.predict_all(flow_features, sequences)
            if results:
                print(f"\n{'='*70}")
                print(f"[{datetime.now().strftime('%H:%M:%S')}] COMPLETED FLOWS → PARALLEL ANALYSIS ({len(flow_features)} flows)")
                print(f"{'='*70}")
                self._display_flow_results(results, flow_features)
        
        # Remove completed flows from tracking
        for flow_key in completed_flow_keys:
            self.extractor.remove_flow(flow_key)
    
    def analyze_all_active_flows(self):
        """Analyze all currently active flows IN PARALLEL"""
        if not self.analyzer.models_trained:
            return
        
        flow_features = []
        sequences = []
        
        for flow_key in list(self.extractor.flow_stats.keys()):
            feat = self.extractor.get_flow_features(flow_key)
            if feat:
                flow_features.append(feat)
                seq = self.extractor.get_flow_sequence(flow_key)
                sequences.append(seq)
        
        if not flow_features:
            return
        
        results = self.analyzer.predict_all(flow_features, sequences)
        if results:
            self._display_multi_model_results(results, flow_features)
    
    def _display_flow_results(self, results, flow_features):
        """Display brief results from completed flows"""
        print(f"  Models Used: {', '.join(results['models_used'])}")
        
        # Isolation Forest
        if 'isolation_forest_anomalies' in results:
            if_anomalies = np.sum(results['isolation_forest_anomalies'] == -1)
            if if_anomalies > 0:
                self.total_anomalies_if += if_anomalies
                print(f"  [IF] ⚠ Anomalies: {if_anomalies}/{results['flow_count']}")
                anomaly_idx = np.where(results['isolation_forest_anomalies'] == -1)[0]
                for idx in anomaly_idx[:2]:
                    if idx < len(flow_features):
                        flow = flow_features[idx]
                        print(f"       • {flow.get('src_ip', 'N/A')} → {flow.get('dst_ip', 'N/A')} "
                              f"(Score: {results['isolation_forest_scores'][idx]:.3f})")
        
        # Autoencoder
        if 'autoencoder_anomalies' in results:
            ae_anomalies = np.sum(results['autoencoder_anomalies'] == -1)
            if ae_anomalies > 0:
                self.total_anomalies_ae += ae_anomalies
                print(f"  [AE] ⚠ Anomalies: {ae_anomalies}/{results['flow_count']}")
        
        # XGBoost
        if 'xgboost_traffic_class' in results:
            unique_classes = np.unique(results['xgboost_traffic_class'])
            print(f"  [XGB] Traffic Classes: {list(unique_classes[:3])}")
        
        print(f"{'='*70}\n")
    
    def _display_multi_model_results(self, results, flow_features):
        """Display comprehensive results from all models"""
        print(f"\n{'='*70}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] PERIODIC ANALYSIS - ALL MODELS (PARALLEL)")
        print(f"{'='*70}")
        print(f"Models: {', '.join(results['models_used'])}")
        print(f"Active Flows: {results['flow_count']}")
        print(f"{'='*70}")
        
        # Isolation Forest
        if 'isolation_forest_anomalies' in results:
            if_anomalies = np.sum(results['isolation_forest_anomalies'] == -1)
            print(f"\n[1. Isolation Forest - Anomaly Detection]")
            print(f"  Anomalies: {if_anomalies}/{results['flow_count']} ({if_anomalies/results['flow_count']*100:.1f}%)")
            
            if if_anomalies > 0:
                anomaly_idx = np.where(results['isolation_forest_anomalies'] == -1)[0]
                top_3 = np.argsort(results['isolation_forest_scores'])[:min(3, len(anomaly_idx))]
                for idx in top_3:
                    if idx < len(flow_features):
                        flow = flow_features[idx]
                        print(f"    • {flow.get('src_ip', 'N/A')}:{flow.get('src_port', 'N/A')} → "
                              f"{flow.get('dst_ip', 'N/A')}:{flow.get('dst_port', 'N/A')} "
                              f"| Pkts: {flow.get('flow_packet_count', 0)} | Score: {results['isolation_forest_scores'][idx]:.3f}")
        
        # Autoencoder
        if 'autoencoder_anomalies' in results:
            ae_anomalies = np.sum(results['autoencoder_anomalies'] == -1)
            print(f"\n[2. Autoencoder - Deep Anomaly Detection]")
            print(f"  Anomalies: {ae_anomalies}/{results['flow_count']} ({ae_anomalies/results['flow_count']*100:.1f}%)")
        
        # XGBoost
        if 'xgboost_traffic_class' in results:
            print(f"\n[3. XGBoost - Traffic Classification]")
            unique_classes, counts = np.unique(results['xgboost_traffic_class'], return_counts=True)
            print(f"  Classes Detected: {len(unique_classes)}")
            for cls, count in zip(unique_classes[:3], counts[:3]):
                self.traffic_class_counts[cls] += count
                avg_conf = np.mean(results['xgboost_confidence'][results['xgboost_traffic_class'] == cls])
                print(f"    Class {cls}: {count} flows ({count/results['flow_count']*100:.1f}%, Conf: {avg_conf:.2f})")
        
        # LSTM
        if 'lstm_traffic_class' in results:
            print(f"\n[4. LSTM - Sequential Analysis]")
            unique_classes = np.unique(results['lstm_traffic_class'])
            print(f"  Patterns: {len(unique_classes)}")
        
        # TCN
        if 'tcn_throughput' in results:
            print(f"\n[5. TCN - Performance Prediction]")
            print(f"  Throughput: Avg={np.mean(results['tcn_throughput']):.1f} "
                  f"Max={np.max(results['tcn_throughput']):.1f} bytes/sec")
        
        # Random Forest
        if 'rf_device_id' in results:
            print(f"\n[6. Random Forest - Device Fingerprinting]")
            unique_devices = np.unique(results['rf_device_id'])
            print(f"  Devices: {len(unique_devices)}")
        
        print(f"{'='*70}\n")
    
    def display_final_summary(self):
        """Display final comprehensive summary"""
        print(f"\n{'='*70}")
        print(f"FINAL ANALYSIS SUMMARY")
        print(f"{'='*70}")
        print(f"Total Packets Captured: {self.total_packets:,}")
        print(f"Total Flows Processed: {self.total_flows_processed:,}")
        print(f"Active Flows at End: {self.extractor.get_active_flow_count()}")
        print(f"Models Trained: {'Yes' if self.analyzer.models_trained else 'No'}")
        print(f"Parallel Processing: {'Enabled' if self.analyzer.parallel_predictor else 'Disabled'}")
        
        if self.analyzer.models_trained:
            print(f"\nAnomaly Detection:")
            print(f"  Isolation Forest: {self.total_anomalies_if} total anomalies")
            print(f"  Autoencoder: {self.total_anomalies_ae} total anomalies")
            
            if self.traffic_class_counts:
                print(f"\nTop Traffic Classes:")
                for cls, count in sorted(self.traffic_class_counts.items(), 
                                        key=lambda x: x[1], reverse=True)[:5]:
                    print(f"  Class {cls}: {count} flows")
            
            if self.device_counts:
                print(f"\nTop Devices:")
                for dev, count in sorted(self.device_counts.items(), 
                                        key=lambda x: x[1], reverse=True)[:5]:
                    print(f"  Device {dev}: {count} flows")
        
        print(f"{'='*70}\n")


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n[*] Shutting down gracefully...")
    sys.exit(0)


def main():
    """Main execution with continuous parallel 6-model system"""
    
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║   Real-Time WiFi Multi-Model AI Analysis System (PARALLEL)    ║
    ║              6 Models Running Concurrently                      ║
    ║              Optimized for Kali Linux                          ║
    ╚════════════════════════════════════════════════════════════════╝
    
    Models (All run in PARALLEL via ThreadPoolExecutor):
    1. Isolation Forest     → Anomaly Detection
    2. Autoencoder          → Deep Anomaly Detection
    3. XGBoost              → Traffic Classification
    4. LSTM                 → Sequential Traffic Analysis
    5. TCN (Conv1D)         → Performance Prediction
    6. Random Forest        → Device Fingerprinting
    
    Features:
    ✓ Continuous packet capture (unlimited)
    ✓ 5-minute flow timeout (auto-analyze incomplete flows)
    ✓ Parallel model execution (6 models simultaneously)
    ✓ No packet buffering (memory efficient)
    ✓ Immediate analysis of completed flows
    ✓ Debug output every 5 seconds
    ✓ Full analysis every 15 seconds
    """)
    
    # Check dependencies
    if not SKLEARN_AVAILABLE:
        print("[!] ERROR: scikit-learn not installed")
        print("    Install: sudo pip3 install scikit-learn")
        return
    
    # Check if running as root
    if os.geteuid() != 0:
        print("[!] This script requires root privileges.")
        print("[*] Please run with: sudo python3 script.py")
        sys.exit(1)
    
    # Setup signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize capture
    capture = LivePacketCapture()
    
    # List available interfaces
    capture.list_interfaces()
    
    # Get interface from user
    interface = input("\n[?] Enter interface name (default: wlan0): ").strip()
    if interface:
        capture.interface = interface
    
    # Ask about monitor mode
    monitor = input("[?] Enable monitor mode? (y/n, default: n): ").strip().lower()
    if monitor == 'y':
        capture.enable_monitor_mode()
    
    # Initialize analyzer with parallel processing
    analyzer = RealTimeMultiModelAnalyzer(analysis_interval=15, debug_interval=5)
    
    print("\n[*] Starting continuous packet capture...")
    print("[*] System will:")
    print("    1. Capture packets continuously (no limit)")
    print("    2. Train models when 20+ flows collected")
    print("    3. Analyze flows immediately upon completion")
    print("    4. Auto-analyze flows after 5-minute timeout")
    print("    5. Run ALL 6 models in PARALLEL (fast!)")
    print("    6. Debug output every 5 seconds")
    print("    7. Full analysis every 15 seconds")
    print("\n[*] Press Ctrl+C to stop\n")
    
    try:
        # Start continuous capture with real-time processing
        capture.start_capture(prn=analyzer.process_packet)
        
    except KeyboardInterrupt:
        print("\n[*] Stopping capture...")
    finally:
        capture.stop_capture()
        
        if monitor == 'y':
            capture.disable_monitor_mode()
        
        # Final comprehensive summary
        analyzer.display_final_summary()
        print("\n[+] Multi-model parallel analysis complete!")


if __name__ == "__main__":
    main()