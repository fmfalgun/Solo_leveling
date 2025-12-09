"""
Real-Time WiFi Traffic Capture & Multi-Model AI Analysis System
Uses 6 AI models concurrently for comprehensive analysis
Optimized for Kali Linux

Requirements:
pip install scapy numpy pandas scikit-learn xgboost lightgbm tensorflow psutil

System Requirements (Kali Linux):
- tshark (wireshark-cli) - usually pre-installed
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

import numpy as np
import pandas as pd
from scapy.all import sniff, IP, TCP, UDP, ICMP, wrpcap, Ether, RadioTap
from sklearn.ensemble import IsolationForest, RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans, DBSCAN
import xgboost as xgb
import lightgbm as lgb
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


class LivePacketCapture:
    """Live packet capture using Scapy and system tools"""
    
    def __init__(self, interface='wlan0', buffer_size=100):
        self.interface = interface
        self.buffer_size = buffer_size
        self.packet_buffer = deque(maxlen=buffer_size)
        self.capture_active = False
        self.packet_count = 0
        self.capture_thread = None
        
    def list_interfaces(self):
        """List available network interfaces"""
        try:
            result = subprocess.run(['ip', 'link', 'show'], 
                                  capture_output=True, text=True)
            print("\n=== Available Network Interfaces ===")
            print(result.stdout)
            
            # Also try iwconfig for wireless interfaces
            result = subprocess.run(['iwconfig'], 
                                  capture_output=True, text=True, stderr=subprocess.DEVNULL)
            if result.stdout:
                print("\n=== Wireless Interfaces ===")
                print(result.stdout)
        except Exception as e:
            print(f"Error listing interfaces: {e}")
    
    def enable_monitor_mode(self):
        """Enable monitor mode on wireless interface (Kali Linux)"""
        print(f"\n[*] Attempting to enable monitor mode on {self.interface}...")
        try:
            # Stop network manager
            subprocess.run(['sudo', 'airmon-ng', 'check', 'kill'], 
                         capture_output=True)
            
            # Enable monitor mode
            result = subprocess.run(['sudo', 'airmon-ng', 'start', self.interface], 
                                  capture_output=True, text=True)
            print(result.stdout)
            
            # Check if monitor interface was created (usually wlan0mon)
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
    
    def packet_callback(self, packet):
        """Callback for each captured packet"""
        self.packet_count += 1
        self.packet_buffer.append(packet)
        
        # Print progress every 100 packets
        if self.packet_count % 100 == 0:
            print(f"[*] Captured {self.packet_count} packets...")
    
    def start_capture(self, duration=None, packet_count=None, prn=None):
        """Start live packet capture"""
        self.capture_active = True
        self.packet_count = 0
        
        print(f"\n[*] Starting packet capture on interface: {self.interface}")
        print(f"[*] Press Ctrl+C to stop capture")
        
        try:
            if prn is None:
                prn = self.packet_callback
            
            # Start sniffing
            sniff(
                iface=self.interface,
                prn=prn,
                store=False,
                timeout=duration,
                count=packet_count,
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
    
    def get_packets(self):
        """Get captured packets from buffer"""
        return list(self.packet_buffer)


class RealTimeFeatureExtractor:
    """Extract features from packets in real-time"""
    
    def __init__(self, window_size=50, sequence_length=20):
        self.window_size = window_size
        self.sequence_length = sequence_length
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
            'inter_arrival_times': []
        })
    
    def extract_packet_features(self, packet):
        """Extract features from single packet"""
        features = {
            'timestamp': time.time(),
            'packet_length': len(packet),
            'has_ip': 0,
            'has_tcp': 0,
            'has_udp': 0,
            'has_icmp': 0
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
        
        stats = self.flow_stats[flow_key]
        current_time = time.time()
        
        # Update basic stats
        stats['packet_count'] += 1
        stats['byte_count'] += len(packet)
        stats['packet_sizes'].append(len(packet))
        
        if stats['start_time'] is None:
            stats['start_time'] = current_time
        else:
            # Calculate inter-arrival time
            inter_arrival = current_time - stats['last_time']
            stats['inter_arrival_times'].append(inter_arrival)
        
        stats['last_time'] = current_time
        
        # Store packet info
        ip = packet[IP]
        stats['src_ip'] = ip.src
        stats['dst_ip'] = ip.dst
        
        if packet.haslayer(TCP):
            stats['protocol'] = 'TCP'
            stats['src_port'] = packet[TCP].sport
            stats['dst_port'] = packet[TCP].dport
        elif packet.haslayer(UDP):
            stats['protocol'] = 'UDP'
            stats['src_port'] = packet[UDP].sport
            stats['dst_port'] = packet[UDP].dport
        
        # Add to flow window for aggregated features
        self.flow_windows[flow_key].append({
            'length': len(packet),
            'time': current_time
        })
        
        # Add to sequence for LSTM/TCN
        packet_features = self.extract_packet_features(packet)
        self.flow_sequences[flow_key].append([
            packet_features.get('packet_length', 0),
            packet_features.get('ip_ttl', 0),
            packet_features.get('tcp_window', 0),
            packet_features.get('has_tcp', 0),
            packet_features.get('has_udp', 0)
        ])
        
        return flow_key
    
    def get_flow_features(self, flow_key):
        """Get comprehensive features for a flow"""
        stats = self.flow_stats[flow_key]
        window = list(self.flow_windows[flow_key])
        
        if len(window) < 2:
            return None
        
        # Calculate statistics
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
        sequence = list(self.flow_sequences[flow_key])
        
        if len(sequence) < length:
            # Pad with zeros
            padding = [[0] * 5] * (length - len(sequence))
            sequence = padding + sequence
        else:
            # Take last 'length' packets
            sequence = sequence[-length:]
        
        return np.array(sequence)
    
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


class MultiModelAnalyzer:
    """Multi-model AI system with 6 concurrent models"""
    
    def __init__(self):
        # Model 1: Isolation Forest (Anomaly Detection)
        self.isolation_forest = None
        
        # Model 2: Autoencoder (Anomaly Detection)
        self.autoencoder = None
        self.autoencoder_threshold = None
        
        # Model 3: XGBoost (Traffic Classification)
        self.xgboost_classifier = None
        
        # Model 4: LSTM (Traffic Classification)
        self.lstm_classifier = None
        
        # Model 5: TCN/Conv1D (Performance Prediction)
        self.tcn_predictor = None
        
        # Model 6: Random Forest (Device Fingerprinting)
        self.rf_fingerprinter = None
        
        # Preprocessing
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.device_encoder = LabelEncoder()
        
        self.models_trained = False
        
    def build_autoencoder(self, input_dim):
        """Build autoencoder for anomaly detection"""
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
        """Build LSTM for traffic classification"""
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
        """Build TCN (Temporal Convolutional Network) for performance prediction"""
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
        
        # Prepare features
        X, ip_data = self._prepare_features(flow_features)
        
        if X is None or len(X) < 20:
            print("[!] Not enough data for training (need at least 20 samples)")
            return False
        
        # 1. Train Isolation Forest
        if verbose:
            print("\n[1/6] Training Isolation Forest (Anomaly Detection)...")
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        X_scaled = self.scaler.fit_transform(X)
        self.isolation_forest.fit(X_scaled)
        if verbose:
            print("      ✓ Isolation Forest trained")
        
        # 2. Train Autoencoder
        if TENSORFLOW_AVAILABLE and verbose:
            print("\n[2/6] Training Autoencoder (Anomaly Detection)...")
            self.autoencoder = self.build_autoencoder(X_scaled.shape[1])
            if self.autoencoder:
                self.autoencoder.fit(X_scaled, X_scaled, epochs=20, batch_size=32, 
                                    verbose=0, validation_split=0.2)
                # Calculate reconstruction error threshold
                reconstructions = self.autoencoder.predict(X_scaled, verbose=0)
                mse = np.mean(np.power(X_scaled - reconstructions, 2), axis=1)
                self.autoencoder_threshold = np.percentile(mse, 90)
                print("      ✓ Autoencoder trained")
        elif verbose:
            print("\n[2/6] Skipping Autoencoder (TensorFlow not available)")
        
        # 3. Train XGBoost Classifier
        if verbose:
            print("\n[3/6] Training XGBoost (Traffic Classification)...")
        # Use clustering for pseudo-labels
        kmeans = KMeans(n_clusters=min(5, len(X) // 4), random_state=42)
        traffic_labels = kmeans.fit_predict(X_scaled)
        
        self.xgboost_classifier = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            verbosity=0
        )
        self.xgboost_classifier.fit(X, traffic_labels)
        if verbose:
            print(f"      ✓ XGBoost trained ({len(np.unique(traffic_labels))} traffic classes)")
        
        # 4. Train LSTM Classifier
        if TENSORFLOW_AVAILABLE and len(sequences) > 0 and verbose:
            print("\n[4/6] Training LSTM (Traffic Classification)...")
            # Prepare sequences
            X_seq = np.array([seq for seq in sequences if len(seq) > 0])
            if len(X_seq) > 0:
                # Use same labels as XGBoost
                y_seq = traffic_labels[:len(X_seq)]
                n_classes = len(np.unique(y_seq))
                
                self.lstm_classifier = self.build_lstm_classifier(
                    X_seq.shape[1], X_seq.shape[2], n_classes
                )
                if self.lstm_classifier:
                    self.lstm_classifier.fit(X_seq, y_seq, epochs=15, batch_size=16, 
                                            verbose=0, validation_split=0.2)
                    print("      ✓ LSTM trained")
        elif verbose:
            print("\n[4/6] Skipping LSTM (TensorFlow not available or no sequences)")
        
        # 5. Train TCN Predictor
        if TENSORFLOW_AVAILABLE and len(sequences) > 0 and verbose:
            print("\n[5/6] Training TCN (Performance Prediction)...")
            X_seq = np.array([seq for seq in sequences if len(seq) > 0])
            if len(X_seq) > 0:
                # Create target: throughput (bytes/duration)
                throughput = X[:len(X_seq), 2] / (X[:len(X_seq), 0] + 1)
                
                self.tcn_predictor = self.build_tcn_predictor(
                    X_seq.shape[1], X_seq.shape[2]
                )
                if self.tcn_predictor:
                    self.tcn_predictor.fit(X_seq, throughput, epochs=15, batch_size=16, 
                                          verbose=0, validation_split=0.2)
                    print("      ✓ TCN trained")
        elif verbose:
            print("\n[5/6] Skipping TCN (TensorFlow not available or no sequences)")
        
        # 6. Train Random Forest Fingerprinter
        if verbose:
            print("\n[6/6] Training Random Forest (Device Fingerprinting)...")
        # Use DBSCAN for device clustering
        dbscan = DBSCAN(eps=0.5, min_samples=3)
        device_labels = dbscan.fit_predict(X_scaled)
        
        # Filter out noise
        valid_idx = device_labels != -1
        if np.sum(valid_idx) > 10:
            X_valid = X[valid_idx]
            y_valid = device_labels[valid_idx]
            
            self.rf_fingerprinter = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            self.rf_fingerprinter.fit(X_valid, y_valid)
            if verbose:
                n_devices = len(np.unique(y_valid))
                print(f"      ✓ Random Forest trained ({n_devices} device clusters)")
        elif verbose:
            print("      ! Not enough device clusters for training")
        
        self.models_trained = True
        
        if verbose:
            print("\n" + "="*70)
            print("✓ ALL MODELS TRAINED SUCCESSFULLY")
            print("="*70)
        
        return True
    
    def predict_all(self, flow_features, sequences):
        """Run predictions with all 6 models"""
        if not self.models_trained:
            return None
        
        X, ip_data = self._prepare_features(flow_features)
        if X is None:
            return None
        
        X_scaled = self.scaler.transform(X)
        
        results = {
            'flow_count': len(X),
            'models_used': []
        }
        
        # Model 1: Isolation Forest
        if self.isolation_forest:
            iso_scores = self.isolation_forest.score_samples(X_scaled)
            iso_pred = self.isolation_forest.predict(X_scaled)
            results['isolation_forest_scores'] = iso_scores
            results['isolation_forest_anomalies'] = iso_pred
            results['models_used'].append('Isolation Forest')
        
        # Model 2: Autoencoder
        if self.autoencoder and TENSORFLOW_AVAILABLE:
            reconstructions = self.autoencoder.predict(X_scaled, verbose=0)
            mse = np.mean(np.power(X_scaled - reconstructions, 2), axis=1)
            ae_anomalies = (mse > self.autoencoder_threshold).astype(int)
            ae_anomalies = np.where(ae_anomalies == 1, -1, 1)  # Convert to -1/1 format
            results['autoencoder_scores'] = -mse  # Negative for consistency
            results['autoencoder_anomalies'] = ae_anomalies
            results['models_used'].append('Autoencoder')
        
        # Model 3: XGBoost
        if self.xgboost_classifier:
            xgb_pred = self.xgboost_classifier.predict(X)
            xgb_proba = self.xgboost_classifier.predict_proba(X)
            results['xgboost_traffic_class'] = xgb_pred
            results['xgboost_confidence'] = np.max(xgb_proba, axis=1)
            results['models_used'].append('XGBoost')
        
        # Model 4: LSTM
        if self.lstm_classifier and len(sequences) > 0 and TENSORFLOW_AVAILABLE:
            X_seq = np.array([seq for seq in sequences if len(seq) > 0])
            if len(X_seq) > 0:
                lstm_pred = np.argmax(self.lstm_classifier.predict(X_seq, verbose=0), axis=1)
                lstm_proba = self.lstm_classifier.predict(X_seq, verbose=0)
                results['lstm_traffic_class'] = lstm_pred
                results['lstm_confidence'] = np.max(lstm_proba, axis=1)
                results['models_used'].append('LSTM')
        
        # Model 5: TCN
        if self.tcn_predictor and len(sequences) > 0 and TENSORFLOW_AVAILABLE:
            X_seq = np.array([seq for seq in sequences if len(seq) > 0])
            if len(X_seq) > 0:
                tcn_pred = self.tcn_predictor.predict(X_seq, verbose=0).flatten()
                results['tcn_throughput'] = tcn_pred
                results['models_used'].append('TCN')
        
        # Model 6: Random Forest
        if self.rf_fingerprinter:
            try:
                rf_pred = self.rf_fingerprinter.predict(X)
                rf_proba = self.rf_fingerprinter.predict_proba(X)
                results['rf_device_id'] = rf_pred
                results['rf_device_confidence'] = np.max(rf_proba, axis=1)
                results['models_used'].append('Random Forest')
            except:
                pass
        
        return results
    
    def _prepare_features(self, flow_features):
        """Convert flow features to numerical array"""
        if not flow_features:
            return None, None
        
        df = pd.DataFrame(flow_features)
        
        # Store IP addresses separately
        ip_data = df[['src_ip', 'dst_ip']].copy() if 'src_ip' in df.columns else None
        
        # Select numerical features
        numerical_cols = [col for col in df.columns 
                         if col not in ['src_ip', 'dst_ip', 'protocol']]
        
        X = df[numerical_cols].fillna(0)
        
        if self.feature_columns is None:
            self.feature_columns = X.columns.tolist()
        
        # Ensure consistent columns
        for col in self.feature_columns:
            if col not in X.columns:
                X[col] = 0
        
        X = X[self.feature_columns]
        return X.values, ip_data


class RealTimeMultiModelAnalyzer:
    """Real-time analysis with all 6 models running concurrently"""
    
    def __init__(self, update_interval=10):
        self.extractor = RealTimeFeatureExtractor()
        self.analyzer = MultiModelAnalyzer()
        self.update_interval = update_interval
        self.last_update = time.time()
        
        # Statistics
        self.total_packets = 0
        self.total_flows = 0
        self.total_anomalies_if = 0
        self.total_anomalies_ae = 0
        self.traffic_class_counts = defaultdict(int)
        self.device_counts = defaultdict(int)
        
    def process_packet(self, packet):
        """Process single packet in real-time"""
        self.total_packets += 1
        
        # Extract features and update flow stats
        flow_key = self.extractor.update_flow_stats(packet)
        
        if flow_key:
            self.total_flows = len(self.extractor.flow_stats)
        
        # Periodically analyze
        current_time = time.time()
        if current_time - self.last_update >= self.update_interval:
            self.analyze_all()
            self.last_update = current_time
    
    def train_models(self, initial_packets):
        """Train all 6 models on initial traffic"""
        print("\n[*] Extracting features for training...")
        
        # Extract flow features
        flow_features = []
        sequences = []
        
        for flow_key in self.extractor.flow_stats.keys():
            feat = self.extractor.get_flow_features(flow_key)
            if feat:
                flow_features.append(feat)
                seq = self.extractor.get_flow_sequence(flow_key)
                sequences.append(seq)
        
        if len(flow_features) < 20:
            print("[!] Not enough flows for training. Need at least 20 flows.")
            return False
        
        print(f"[*] Training on {len(flow_features)} flows with {len(sequences)} sequences")
        
        # Train all models
        success = self.analyzer.train_all_models(flow_features, sequences, verbose=True)
        
        return success
    
    def analyze_all(self):
        """Run all 6 models on current traffic"""
        if not self.analyzer.models_trained:
            return
        
        # Get flow features and sequences
        flow_features = []
        sequences = []
        flow_keys = []
        
        for flow_key in list(self.extractor.flow_stats.keys()):
            feat = self.extractor.get_flow_features(flow_key)
            if feat:
                flow_features.append(feat)
                seq = self.extractor.get_flow_sequence(flow_key)
                sequences.append(seq)
                flow_keys.append(flow_key)
        
        if not flow_features:
            return
        
        # Run all models
        results = self.analyzer.predict_all(flow_features, sequences)
        
        if results:
            self._display_multi_model_results(results, flow_features)
    
    def _display_multi_model_results(self, results, flow_features):
        """Display results from all 6 models"""
        print(f"\n{'='*70}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] MULTI-MODEL ANALYSIS RESULTS")
        print(f"{'='*70}")
        print(f"Models Active: {', '.join(results['models_used'])}")
        print(f"Flows Analyzed: {results['flow_count']}")
        print(f"{'='*70}")
        
        # Isolation Forest Results
        if 'isolation_forest_anomalies' in results:
            if_anomalies = np.sum(results['isolation_forest_anomalies'] == -1)
            self.total_anomalies_if += if_anomalies
            print(f"\n[Model 1: Isolation Forest - Anomaly Detection]")
            print(f"  Anomalies: {if_anomalies}/{results['flow_count']} ({if_anomalies/results['flow_count']*100:.1f}%)")
            
            if if_anomalies > 0:
                anomaly_idx = np.where(results['isolation_forest_anomalies'] == -1)[0]
                print(f"  Top 3 Anomalous Flows:")
                top_3 = np.argsort(results['isolation_forest_scores'])[:min(3, len(anomaly_idx))]
                for idx in top_3:
                    if idx < len(flow_features):
                        flow = flow_features[idx]
                        print(f"    • {flow.get('src_ip', 'N/A')}:{flow.get('src_port', 'N/A')} → "
                              f"{flow.get('dst_ip', 'N/A')}:{flow.get('dst_port', 'N/A')} "
                              f"(Score: {results['isolation_forest_scores'][idx]:.3f})")
        
        # Autoencoder Results
        if 'autoencoder_anomalies' in results:
            ae_anomalies = np.sum(results['autoencoder_anomalies'] == -1)
            self.total_anomalies_ae += ae_anomalies
            print(f"\n[Model 2: Autoencoder - Anomaly Detection]")
            print(f"  Anomalies: {ae_anomalies}/{results['flow_count']} ({ae_anomalies/results['flow_count']*100:.1f}%)")
            
            if ae_anomalies > 0:
                anomaly_idx = np.where(results['autoencoder_anomalies'] == -1)[0]
                print(f"  Top 3 Reconstruction Errors:")
                top_3 = np.argsort(results['autoencoder_scores'])[:min(3, len(anomaly_idx))]
                for idx in top_3:
                    if idx < len(flow_features):
                        flow = flow_features[idx]
                        print(f"    • {flow.get('src_ip', 'N/A')} → {flow.get('dst_ip', 'N/A')} "
                              f"(Error: {-results['autoencoder_scores'][idx]:.3f})")
        
        # XGBoost Results
        if 'xgboost_traffic_class' in results:
            print(f"\n[Model 3: XGBoost - Traffic Classification]")
            unique_classes, counts = np.unique(results['xgboost_traffic_class'], return_counts=True)
            print(f"  Traffic Classes Detected: {len(unique_classes)}")
            for cls, count in zip(unique_classes[:5], counts[:5]):  # Top 5
                self.traffic_class_counts[cls] += count
                avg_conf = np.mean(results['xgboost_confidence'][results['xgboost_traffic_class'] == cls])
                print(f"    Class {cls}: {count} flows ({count/results['flow_count']*100:.1f}%, "
                      f"Confidence: {avg_conf:.2f})")
        
        # LSTM Results
        if 'lstm_traffic_class' in results:
            print(f"\n[Model 4: LSTM - Sequential Traffic Classification]")
            unique_classes, counts = np.unique(results['lstm_traffic_class'], return_counts=True)
            print(f"  Traffic Patterns Detected: {len(unique_classes)}")
            for cls, count in zip(unique_classes[:3], counts[:3]):  # Top 3
                avg_conf = np.mean(results['lstm_confidence'][results['lstm_traffic_class'] == cls])
                print(f"    Pattern {cls}: {count} flows (Confidence: {avg_conf:.2f})")
        
        # TCN Results
        if 'tcn_throughput' in results:
            print(f"\n[Model 5: TCN - Performance Prediction]")
            print(f"  Predicted Throughput Statistics:")
            print(f"    Mean: {np.mean(results['tcn_throughput']):.2f} bytes/sec")
            print(f"    Max: {np.max(results['tcn_throughput']):.2f} bytes/sec")
            print(f"    Min: {np.min(results['tcn_throughput']):.2f} bytes/sec")
            print(f"    Std Dev: {np.std(results['tcn_throughput']):.2f}")
        
        # Random Forest Results
        if 'rf_device_id' in results:
            print(f"\n[Model 6: Random Forest - Device Fingerprinting]")
            unique_devices, counts = np.unique(results['rf_device_id'], return_counts=True)
            print(f"  Unique Devices Detected: {len(unique_devices)}")
            for dev, count in zip(unique_devices[:5], counts[:5]):  # Top 5
                self.device_counts[dev] += count
                avg_conf = np.mean(results['rf_device_confidence'][results['rf_device_id'] == dev])
                print(f"    Device {dev}: {count} flows ({count/results['flow_count']*100:.1f}%, "
                      f"Confidence: {avg_conf:.2f})")
        
        print(f"{'='*70}\n")
    
    def display_final_summary(self):
        """Display final comprehensive summary"""
        print(f"\n{'='*70}")
        print(f"FINAL ANALYSIS SUMMARY")
        print(f"{'='*70}")
        print(f"Total Packets Captured: {self.total_packets:,}")
        print(f"Total Flows Tracked: {self.total_flows:,}")
        print(f"Models Used: {len(self.analyzer.models_trained) if self.analyzer.models_trained else 0}/6")
        print(f"\nAnomaly Detection:")
        print(f"  Isolation Forest: {self.total_anomalies_if} anomalies")
        print(f"  Autoencoder: {self.total_anomalies_ae} anomalies")
        
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
    """Main execution with 6-model system"""
    
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║      Real-Time WiFi Traffic Multi-Model AI Analysis System     ║
    ║                    6 Models Running Concurrently               ║
    ║              Optimized for Kali Linux                          ║
    ╚════════════════════════════════════════════════════════════════╝
    
    Models:
    1. Isolation Forest     → Anomaly Detection
    2. Autoencoder          → Deep Anomaly Detection
    3. XGBoost              → Traffic Classification
    4. LSTM                 → Sequential Traffic Analysis
    5. TCN (Conv1D)         → Performance Prediction
    6. Random Forest        → Device Fingerprinting
    """)
    
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
    
    # Initialize analyzer with all 6 models
    analyzer = RealTimeMultiModelAnalyzer(update_interval=15)
    
    print("\n[*] Phase 1: Capturing initial traffic for model training...")
    print("[*] Capturing 1000 packets for comprehensive training...")
    
    # Capture initial packets for training
    initial_packets = []
    def training_callback(packet):
        initial_packets.append(packet)
        analyzer.extractor.update_flow_stats(packet)
        if len(initial_packets) % 200 == 0:
            print(f"[*] Training packets: {len(initial_packets)}/1000")
    
    try:
        capture.start_capture(packet_count=1000, prn=training_callback)
        
        # Train all 6 models
        if len(initial_packets) >= 200:
            success = analyzer.train_models(initial_packets)
            if not success:
                print("[!] Model training failed")
                return
        else:
            print("[!] Not enough packets captured for training")
            return
        
        print("\n[*] Phase 2: Starting real-time multi-model analysis...")
        print("[*] All 6 models are now running concurrently!")
        print("[*] Press Ctrl+C to stop\n")
        
        # Start real-time capture and analysis with all models
        capture.packet_count = 0
        capture.start_capture(prn=analyzer.process_packet)
        
    except KeyboardInterrupt:
        print("\n[*] Stopping capture...")
    finally:
        capture.stop_capture()
        
        if monitor == 'y':
            capture.disable_monitor_mode()
        
        # Final comprehensive summary
        analyzer.display_final_summary()
        print("\n[+] Multi-model analysis complete!")


if __name__ == "__main__":
    main()
        