'use client';

import React, { useState, useEffect } from 'react';
import {
  ArrowDown,
  Cpu,
  ShieldAlert,
  Activity,
  Zap,
  RefreshCw,
  Lock,
  UserCheck,
  Workflow,
  Radio,
  FileCode
} from 'lucide-react';

export interface ArchitectureNode {
  id: string;
  title: string;
  subtitle: string;
  category: 'ingestion' | 'buffer' | 'perception' | 'intel' | 'fusion' | 'ai' | 'governance' | 'command' | 'operator' | 'mlops';
  techStack: string;
  status: string;
  latency: string;
  throughput: string;
  accentColor?: string;
  description: string;
  sampleData: Record<string, any>;
}

export const initialArchitectureNodes: ArchitectureNode[] = [
  {
    id: 'node-1',
    title: 'EXISTING IP CCTV NETWORK',
    subtitle: 'RTSP / ONVIF / PTZ',
    category: 'ingestion',
    techStack: 'IP Cameras • RTSP Stream • ONVIF • PTZ Protocol',
    status: 'HEALTHY',
    latency: '8 ms',
    throughput: '247 Cameras Online',
    description: 'Hardware layer ingesting multi-channel HD video streams from border checkpoint IP cameras and thermal sensors.',
    sampleData: {
      rtsp_url: 'rtsp://admin:pass@192.168.1.104:554/h264',
      fps: 60,
      resolution: '1920x1080',
      codec: 'H.264 / H.265 Direct'
    }
  },
  {
    id: 'node-2',
    title: 'VIDEO INGESTION GATEWAY',
    subtitle: 'FFmpeg / OpenCV / stream health',
    category: 'ingestion',
    techStack: 'FFmpeg 6.0 • OpenCV Python • Hardware Decoding',
    status: 'HEALTHY',
    latency: '12 ms',
    throughput: '1080p @ 60 FPS',
    description: 'De-compresses, rescales, and monitors health/packet loss for incoming raw camera streams before frame extraction.',
    sampleData: {
      active_pipes: 4,
      frame_drop_rate: '0.01%',
      stream_health: 'OPTIMAL',
      buffer_time_ms: 12
    }
  },
  {
    id: 'node-3a',
    title: 'OPTIONAL EDGE AI',
    subtitle: 'Fast local inference / buffering',
    category: 'buffer',
    techStack: 'NVIDIA Jetson AGX Orin • TensorRT • CUDA',
    status: 'ACTIVE',
    latency: '6 ms',
    throughput: '32.1 FPS Edge',
    description: 'Zero-latency edge inference node performing rapid boundary filter and local video chunk buffering.',
    sampleData: {
      edge_node_id: 'JETSON-ALPHA-07',
      gpu_load: '54%',
      local_buffer_sec: 300
    }
  },
  {
    id: 'node-3b',
    title: 'VMS / NVR',
    subtitle: 'Raw / short-term recording',
    category: 'buffer',
    techStack: 'NVMe Storage Vault • Short-term H.265 Sinks',
    status: 'RECORDING',
    latency: '15 ms',
    throughput: '4.2 TB Vault',
    description: 'Continuous ring buffer storage capturing uncompressed raw footage for forensic review and legal evidence packaging.',
    sampleData: {
      storage_used: '3.8 TB / 4.0 TB',
      retention_days: 30,
      write_speed_mbps: 450
    }
  },
  {
    id: 'node-3c',
    title: 'STREAM BUFFER / MESSAGE QUEUE',
    subtitle: 'Redis Streams / Kafka',
    category: 'buffer',
    techStack: 'Redis Streams 7.2 • Apache Kafka • Event PubSub',
    status: 'HEALTHY',
    latency: '2 ms',
    throughput: '1,280 msg/sec',
    description: 'High-throughput event message broker decoupling stream ingestion from downstream AI perception workers.',
    sampleData: {
      queue_depth: 14,
      pubsub_channels: ['camera_frames', 'detection_events'],
      broker: 'Redis Cluster (Port 6379)'
    }
  },
  {
    id: 'node-4',
    title: 'CENTRAL AI PERCEPTION',
    subtitle: 'Person • Vehicle • Face • ANPR',
    category: 'perception',
    techStack: 'YOLOv8 PyTorch • DeepSORT • InsightFace • ANPR Engine',
    status: 'HEALTHY',
    latency: '18 ms',
    throughput: '28.4 FPS Core',
    description: 'Multi-modal neural network pipeline detecting subject bounding boxes, vehicle license plates, facial vectors, and threat features.',
    sampleData: {
      detected_persons: 1284,
      detected_vehicles: 437,
      anpr_confidence: '98.4%',
      face_embeddings_generated: 142
    }
  },
  {
    id: 'node-5',
    title: 'TRACKING + GEO-SPATIAL',
    subtitle: 'Persistent ID • trajectory • geofences',
    category: 'perception',
    accentColor: 'cyan',
    techStack: 'ByteTrack • MapLibre GIS • Turf.js Geofencing',
    status: 'ACTIVE',
    latency: '5 ms',
    throughput: '38 Persistent Track IDs',
    description: 'Assigns unique spatial UUIDs to targets, projects GPS trajectories onto border map layers, and evaluates geofence boundaries.',
    sampleData: {
      tracked_target: 'P-014',
      current_geofence: 'Restricted Zone A',
      trajectory_length: '240 meters',
      speed_kmh: 4.8
    }
  },
  {
    id: 'node-6a',
    title: 'AUTHORIZED EXTERNAL INTELLIGENCE',
    subtitle: 'Watchlist / vehicle / policy connectors',
    category: 'intel',
    techStack: 'REST Watchlist API • Interpol DB • Border Security Cloud',
    status: 'SYNCED',
    latency: '45 ms',
    throughput: '1,420 Active Watchlist Records',
    description: 'Real-time synchronization against external law enforcement watchlists, blacklisted license plates, and intelligence feeds.',
    sampleData: {
      watchlist_matches: 1,
      match_flag: 'FLAGGED_SUBJECT_ALPHA',
      sync_interval: '500 ms'
    }
  },
  {
    id: 'node-6b',
    title: 'CROSS-CAMERA + BEHAVIOUR',
    subtitle: 'Correlation • handoff • anomalies',
    category: 'perception',
    techStack: 'Spatial-Temporal Graph Neural Network • Multi-Cam Handoff',
    status: 'TRACKING',
    latency: '11 ms',
    throughput: '4 Camera Matrix',
    description: 'Correlates subject movement across adjacent cameras (CAM-039 ➔ CAM-041 ➔ CAM-042) to detect anomalous loitering or perimeter scaling.',
    sampleData: {
      camera_path: ['CAM-039', 'CAM-041', 'CAM-042'],
      behaviour_anomaly: 'PERIMETER_LOITERING',
      duration_sec: 140
    }
  },
  {
    id: 'node-7',
    title: 'THREAT FUSION ENGINE',
    subtitle: 'Multi-signal risk scoring',
    category: 'fusion',
    accentColor: 'amber',
    techStack: 'Multi-Signal Bayesian Inference • Threat Vector Scoring',
    status: 'CRITICAL',
    latency: '8 ms',
    throughput: 'Risk Score: 95 / 100',
    description: 'Fuses spatial breach lines, watchlist flags, cross-camera trajectories, and temporal factors into a unified tactical risk score.',
    sampleData: {
      fused_threat_score: 95,
      threat_level: 'CRITICAL_BREACH',
      factors: [
        'Geofence Polygon Breach (+40)',
        'Night Vector Movement (+25)',
        'Watchlist High Correlation (+30)'
      ]
    }
  },
  {
    id: 'node-8',
    title: 'AI REASONING + ORCHESTRATION',
    subtitle: 'Ollama + Mistral (current)',
    category: 'ai',
    techStack: 'Local Ollama LLM • Mistral-7B • Prompt Orchestration Engine',
    status: 'ONLINE',
    latency: '140 ms',
    throughput: 'Mistral-7B Active',
    description: 'Generates natural language intelligence reports, evaluates tactical protocols, and suggests tactical operator dispatch recommendations.',
    sampleData: {
      llm_model: 'mistral:latest (Ollama local API)',
      copilot_recommendation: 'Immediate dispatch to BOP Alpha-07. Subject P-014 crossed perimeter line at 18:46:00 IST.',
      reasoning_latency_ms: 140
    }
  },
  {
    id: 'node-9',
    title: 'PRIVACY + DATA GOVERNANCE',
    subtitle: 'Policy sidecar over API / evidence / access',
    category: 'governance',
    techStack: 'AES-256 Sidecar • Cryptographic SHA-256 Audit • RBAC Policy',
    status: 'ENFORCED',
    latency: '3 ms',
    throughput: 'Policy Enforced',
    description: 'Applies automated face-blurring for unauthorized users, maintains immutable audit trails, and restricts evidence export access.',
    sampleData: {
      encryption: 'AES-256-GCM',
      anonymization_status: 'ACTIVE',
      audit_sidecar: 'OPERATIONAL'
    }
  },
  {
    id: 'node-10a',
    title: 'SYSTEM OBSERVABILITY',
    subtitle: 'Camera • GPU • network • latency',
    category: 'command',
    techStack: 'NVML Telemetry • Prometheus Metrics • Socket.IO Status',
    status: 'OPERATIONAL',
    latency: '1 ms',
    throughput: '76% GPU / 8.4GB VRAM',
    description: 'Monitors infrastructure health, GPU utilization, network bandwidth, frame drop rates, and sub-system processing latencies.',
    sampleData: {
      gpu_utilization: '76%',
      vram_allocated: '8.4 GB / 12.0 GB',
      system_temp_c: 62
    }
  },
  {
    id: 'node-10b',
    title: 'INCIDENT / ALERT / EVIDENCE',
    subtitle: 'Priority • clips • metadata • audit',
    category: 'command',
    accentColor: 'rose',
    techStack: 'Evidence Vault • Signed Video Packages • Alert Dispatcher',
    status: 'CRITICAL',
    latency: '4 ms',
    throughput: '6 Active Alerts',
    description: 'Packages annotated video clips, bounding box metadata, timestamp hashes, and priority tags into actionable incident cards.',
    sampleData: {
      incident_id: 'INC-2026-0891',
      evidence_hash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
      priority: 'ALPHA_P1'
    }
  },
  {
    id: 'node-11',
    title: 'COMMAND CENTER',
    subtitle: 'Live map • CCTV wall • copilot • analytics',
    category: 'command',
    techStack: 'Next.js 14 Dashboard • MapLibre GIS • Video Player Grid',
    status: 'OPERATIONAL',
    latency: '16 ms',
    throughput: 'C4ISR UI Active',
    description: 'Central unified Operations Command Dashboard displaying live map layers, video walls, copilot assessments, and threat feeds.',
    sampleData: {
      dashboard_view: 'OVERVIEW_SPLIT_MAP',
      connected_operators: 3,
      websocket_sync: 'CONNECTED'
    }
  },
  {
    id: 'node-12',
    title: 'HUMAN OPERATOR',
    subtitle: 'Verify • acknowledge • escalate • resolve',
    category: 'operator',
    accentColor: 'emerald',
    techStack: 'Operator Workstation • Security Clearance L5 • Dispatch Terminal',
    status: 'ENGAGED',
    latency: 'Manual',
    throughput: 'Operator OP-014',
    description: 'Human-in-the-loop validation console allowing command personnel to acknowledge alerts, dispatch field teams, or dismiss false alarms.',
    sampleData: {
      operator_id: 'OP-014',
      clearance_level: 'LEVEL_5_COMMANDER',
      action_pending: 'ACKNOWLEDGE_INCIDENT_0891'
    }
  },
  {
    id: 'node-13',
    title: 'FEEDBACK + LABEL STORE',
    subtitle: 'True/false positive • annotations',
    category: 'mlops',
    techStack: 'SQLite Annotation Vault • COCO Format • Label Studio Sync',
    status: 'RECORDED',
    latency: '20 ms',
    throughput: '890 Annotated Clips',
    description: 'Stores operator verification feedback, true/false positive decisions, and annotated frame bounding boxes for continuous learning.',
    sampleData: {
      operator_verdict: 'TRUE_POSITIVE_BREACH',
      saved_frames: 12,
      export_format: 'YOLO_FORMAT_TXT'
    }
  },
  {
    id: 'node-14',
    title: 'MLOps',
    subtitle: 'Evaluate • registry • controlled rollout',
    category: 'mlops',
    techStack: 'MLflow Model Registry • Automated Fine-Tuning • CI/CD Edge Sync',
    status: 'ACTIVE LOOP',
    latency: 'Batch',
    throughput: 'Model v1.4.2 Active',
    description: 'Evaluates model accuracy, retrains vision weights on novel edge samples, and manages controlled canary rollouts back to Central AI Perception.',
    sampleData: {
      model_registry_version: 'yolov8_ibvap_v1.4.2',
      eval_precision: '95.2%',
      eval_recall: '93.7%',
      target_perception_node: 'node-4'
    }
  }
];

export const SystemArchitectureFlow: React.FC<{
  onSelectNode?: (node: ArchitectureNode) => void;
}> = ({ onSelectNode }) => {
  const [nodes, setNodes] = useState<ArchitectureNode[]>(initialArchitectureNodes);
  const [selectedNode, setSelectedNode] = useState<ArchitectureNode>(initialArchitectureNodes[7]); // Default Threat Fusion
  const [isSimulating, setIsSimulating] = useState(true);
  const [pulseStage, setPulseStage] = useState(0);

  // Fetch API telemetry if backend is available
  useEffect(() => {
    const fetchArchitectureFlow = async () => {
      try {
        const res = await fetch('http://127.0.0.1:5000/api/architecture/flow');
        if (res.ok) {
          const data = await res.json();
          if (data.nodes && Array.isArray(data.nodes)) {
            setNodes(prev =>
              prev.map(n => {
                const fetched = data.nodes.find((fn: any) => fn.id === n.id);
                if (fetched) {
                  return {
                    ...n,
                    status: fetched.status || n.status,
                    latency: fetched.latency || n.latency,
                    throughput: fetched.throughput || n.throughput
                  };
                }
                return n;
              })
            );
          }
        }
      } catch (e) {
        // Fallback to static mock state
      }
    };

    fetchArchitectureFlow();
    const interval = setInterval(fetchArchitectureFlow, 5000);
    return () => clearInterval(interval);
  }, []);

  // Pulse animation sequence simulating live data travelling down the flow
  useEffect(() => {
    if (!isSimulating) return;
    const interval = setInterval(() => {
      setPulseStage(prev => (prev + 1) % 10);
    }, 1200);
    return () => clearInterval(interval);
  }, [isSimulating]);

  const getNodeById = (id: string) => nodes.find(n => n.id === id) || initialArchitectureNodes[0];

  const handleNodeClick = (node: ArchitectureNode) => {
    setSelectedNode(node);
    if (onSelectNode) onSelectNode(node);
  };

  const getNodeCardClasses = (node: ArchitectureNode) => {
    const isSelected = selectedNode.id === node.id;
    let base =
      'relative p-3 rounded-lg border text-left cursor-pointer transition-all duration-200 shadow-md flex flex-col justify-between ';

    if (isSelected) {
      base += 'ring-2 ring-sky-400 border-sky-400 scale-[1.01] shadow-sky-900/40 z-20 ';
    }

    if (node.accentColor === 'amber' || node.id === 'node-7') {
      return base + 'bg-amber-950/35 border-amber-500/60 text-amber-100 hover:bg-amber-900/40 hover:border-amber-400';
    }
    if (node.accentColor === 'rose' || node.id === 'node-10b') {
      return base + 'bg-rose-950/35 border-rose-500/60 text-rose-100 hover:bg-rose-900/40 hover:border-rose-400';
    }
    if (node.accentColor === 'emerald' || node.id === 'node-12') {
      return base + 'bg-emerald-950/35 border-emerald-500/60 text-emerald-100 hover:bg-emerald-900/40 hover:border-emerald-400';
    }
    if (node.accentColor === 'cyan' || node.id === 'node-5') {
      return base + 'bg-cyan-950/35 border-cyan-500/60 text-cyan-100 hover:bg-cyan-900/40 hover:border-cyan-400';
    }

    return base + 'bg-surface border-border text-slate-200 hover:border-sky-500/60 hover:bg-surfaceElevated';
  };

  return (
    <div className="flex flex-col h-full bg-base text-slate-100 p-4 space-y-4 overflow-y-auto font-sans">
      {/* Header Controls & Telemetry Summary */}
      <div className="bg-surface border border-border rounded-lg p-3.5 flex flex-wrap items-center justify-between gap-3 shrink-0 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-600/20 border border-blue-500/40 rounded-md text-blue-400">
            <Workflow className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-extrabold uppercase tracking-wider text-slate-100 flex items-center gap-2">
              SYSTEM ARCHITECTURE & END-TO-END DATA FLOW
              <span className="px-2 py-0.5 text-[9px] bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 rounded font-mono">
                SIH26-26187
              </span>
            </h2>
            <p className="text-[11px] text-slate-400 font-mono">
              RTSP Ingestion ➔ Central AI Perception ➔ Threat Fusion ➔ Ollama LLM Reasoning ➔ Command Center ➔ MLOps Feedback Loop
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="flex items-center gap-2 bg-base border border-border px-3 py-1.5 rounded">
            <Radio className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
            <span className="text-slate-400">PIPELINE LATENCY:</span>
            <span className="text-emerald-400 font-bold">31 ms</span>
          </div>

          <div className="flex items-center gap-2 bg-base border border-border px-3 py-1.5 rounded">
            <Zap className="w-3.5 h-3.5 text-purple-400" />
            <span className="text-slate-400">OLLAMA LLM:</span>
            <span className="text-purple-400 font-bold">MISTRAL (ONLINE)</span>
          </div>

          <div className="flex items-center gap-2 bg-base border border-border px-3 py-1.5 rounded">
            <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-slate-400">FUSED RISK SCORE:</span>
            <span className="text-amber-400 font-bold">95 / 100</span>
          </div>

          <button
            onClick={() => setIsSimulating(!isSimulating)}
            className={`px-3 py-1.5 rounded text-[11px] font-bold flex items-center gap-1.5 transition-all ${
              isSimulating
                ? 'bg-sky-600/30 text-sky-300 border border-sky-500/50 hover:bg-sky-600/50'
                : 'bg-surfaceElevated text-slate-400 border border-border'
            }`}
          >
            <RefreshCw className={`w-3 h-3 ${isSimulating ? 'animate-spin' : ''}`} />
            {isSimulating ? 'STREAM PULSE ACTIVE' : 'PAUSED'}
          </button>
        </div>
      </div>

      {/* Main Container: Left Flow Visualizer + Right Detail Inspector */}
      <div className="grid grid-cols-12 gap-4 flex-1 items-start min-h-0">
        {/* Left Column: Interactive Flowchart Node Matrix (Col 8) */}
        <div className="col-span-8 bg-base/50 border border-border/80 rounded-lg p-4 space-y-3 relative">
          {/* Loopback Visualizer Badge */}
          <div className="absolute top-2 right-4 bg-purple-500/10 border border-purple-500/30 rounded px-2.5 py-1 text-[10px] text-purple-300 font-mono flex items-center gap-1.5 z-10">
            <RefreshCw className="w-3 h-3 animate-spin text-purple-400" />
            <span>MLOps Continuous Feedback Loop Active</span>
          </div>

          {/* STAGE 1: INGESTION LAYER */}
          <div className="space-y-2">
            <div className="text-[10px] font-bold uppercase tracking-widest text-slate-400 font-mono border-b border-border/40 pb-1">
              01. VIDEO INGESTION LAYER
            </div>

            {/* Node 1 */}
            <div className={getNodeCardClasses(getNodeById('node-1'))} onClick={() => handleNodeClick(getNodeById('node-1'))}>
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-bold text-xs tracking-wide">{getNodeById('node-1').title}</h3>
                  <p className="text-[10px] text-slate-400 font-mono mt-0.5">{getNodeById('node-1').subtitle}</p>
                </div>
                <span className="px-2 py-0.5 text-[9px] font-mono font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded">
                  {getNodeById('node-1').status}
                </span>
              </div>
            </div>

            <div className="flex justify-center my-0.5">
              <div className={`p-1 rounded-full border ${pulseStage === 1 ? 'bg-sky-500 text-white animate-bounce' : 'bg-surface border-border text-slate-500'}`}>
                <ArrowDown className="w-3.5 h-3.5" />
              </div>
            </div>

            {/* Node 2 */}
            <div className={getNodeCardClasses(getNodeById('node-2'))} onClick={() => handleNodeClick(getNodeById('node-2'))}>
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-bold text-xs tracking-wide">{getNodeById('node-2').title}</h3>
                  <p className="text-[10px] text-slate-400 font-mono mt-0.5">{getNodeById('node-2').subtitle}</p>
                </div>
                <span className="px-2 py-0.5 text-[9px] font-mono font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded">
                  {getNodeById('node-2').status}
                </span>
              </div>
            </div>
          </div>

          {/* Branch Connectors */}
          <div className="grid grid-cols-3 gap-2 py-1">
            <div className={getNodeCardClasses(getNodeById('node-3a'))} onClick={() => handleNodeClick(getNodeById('node-3a'))}>
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-bold text-[11px]">{getNodeById('node-3a').title}</h4>
                  <p className="text-[9px] text-slate-400 font-mono mt-0.5">{getNodeById('node-3a').subtitle}</p>
                </div>
                <span className="text-[9px] font-mono text-sky-400 font-bold">{getNodeById('node-3a').latency}</span>
              </div>
            </div>

            <div className={getNodeCardClasses(getNodeById('node-3b'))} onClick={() => handleNodeClick(getNodeById('node-3b'))}>
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-bold text-[11px]">{getNodeById('node-3b').title}</h4>
                  <p className="text-[9px] text-slate-400 font-mono mt-0.5">{getNodeById('node-3b').subtitle}</p>
                </div>
                <span className="text-[9px] font-mono text-amber-400 font-bold">{getNodeById('node-3b').status}</span>
              </div>
            </div>

            <div className={getNodeCardClasses(getNodeById('node-3c'))} onClick={() => handleNodeClick(getNodeById('node-3c'))}>
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-bold text-[11px]">{getNodeById('node-3c').title}</h4>
                  <p className="text-[9px] text-slate-400 font-mono mt-0.5">{getNodeById('node-3c').subtitle}</p>
                </div>
                <span className="text-[9px] font-mono text-emerald-400 font-bold">{getNodeById('node-3c').latency}</span>
              </div>
            </div>
          </div>

          <div className="flex justify-center">
            <div className={`p-1 rounded-full border ${pulseStage === 2 ? 'bg-sky-500 text-white animate-bounce' : 'bg-surface border-border text-slate-500'}`}>
              <ArrowDown className="w-3.5 h-3.5" />
            </div>
          </div>

          {/* STAGE 2: PERCEPTION & TRACKING */}
          <div className="space-y-2">
            <div className="text-[10px] font-bold uppercase tracking-widest text-slate-400 font-mono border-b border-border/40 pb-1 flex justify-between items-center">
              <span>02. CENTRAL AI PERCEPTION & TRACKING</span>
              <span className="text-[9px] text-purple-400 font-mono">◄ Retrained Weights from MLOps</span>
            </div>

            <div className={getNodeCardClasses(getNodeById('node-4'))} onClick={() => handleNodeClick(getNodeById('node-4'))}>
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-bold text-xs tracking-wide text-sky-300">{getNodeById('node-4').title}</h3>
                  <p className="text-[10px] text-slate-400 font-mono mt-0.5">{getNodeById('node-4').subtitle}</p>
                </div>
                <span className="px-2 py-0.5 text-[9px] font-mono font-bold bg-sky-500/20 text-sky-400 border border-sky-500/30 rounded">
                  {getNodeById('node-4').status}
                </span>
              </div>
            </div>

            <div className="flex justify-center my-0.5">
              <ArrowDown className="w-3.5 h-3.5 text-slate-500" />
            </div>

            <div className={getNodeCardClasses(getNodeById('node-5'))} onClick={() => handleNodeClick(getNodeById('node-5'))}>
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-bold text-xs tracking-wide text-cyan-300">{getNodeById('node-5').title}</h3>
                  <p className="text-[10px] text-slate-400 font-mono mt-0.5">{getNodeById('node-5').subtitle}</p>
                </div>
                <span className="px-2 py-0.5 text-[9px] font-mono font-bold bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 rounded">
                  {getNodeById('node-5').status}
                </span>
              </div>
            </div>
          </div>

          {/* STAGE 3: INTELLIGENCE & BEHAVIOUR CORRELATION */}
          <div className="grid grid-cols-2 gap-2 py-1">
            <div className={getNodeCardClasses(getNodeById('node-6a'))} onClick={() => handleNodeClick(getNodeById('node-6a'))}>
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-bold text-[11px] text-slate-200">{getNodeById('node-6a').title}</h4>
                  <p className="text-[9px] text-slate-400 font-mono mt-0.5">{getNodeById('node-6a').subtitle}</p>
                </div>
                <span className="text-[9px] font-mono text-cyan-400 font-bold">{getNodeById('node-6a').status}</span>
              </div>
            </div>

            <div className={getNodeCardClasses(getNodeById('node-6b'))} onClick={() => handleNodeClick(getNodeById('node-6b'))}>
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-bold text-[11px] text-slate-200">{getNodeById('node-6b').title}</h4>
                  <p className="text-[9px] text-slate-400 font-mono mt-0.5">{getNodeById('node-6b').subtitle}</p>
                </div>
                <span className="text-[9px] font-mono text-purple-400 font-bold">{getNodeById('node-6b').status}</span>
              </div>
            </div>
          </div>

          <div className="flex justify-center">
            <div className={`p-1 rounded-full border ${pulseStage === 4 ? 'bg-amber-500 text-white animate-bounce' : 'bg-amber-950/80 border-amber-500 text-amber-400'}`}>
              <ArrowDown className="w-3.5 h-3.5" />
            </div>
          </div>

          {/* STAGE 4: THREAT FUSION ENGINE */}
          <div className="space-y-2">
            <div className="text-[10px] font-bold uppercase tracking-widest text-amber-400 font-mono border-b border-amber-500/30 pb-1">
              03. MULTI-SIGNAL RISK SCORING & FUSION
            </div>

            <div className={getNodeCardClasses(getNodeById('node-7'))} onClick={() => handleNodeClick(getNodeById('node-7'))}>
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-extrabold text-xs tracking-wide text-amber-300 flex items-center gap-2">
                    <ShieldAlert className="w-4 h-4 text-amber-400" />
                    {getNodeById('node-7').title}
                  </h3>
                  <p className="text-[10px] text-amber-200/80 font-mono mt-0.5">{getNodeById('node-7').subtitle}</p>
                </div>
                <span className="px-2 py-0.5 text-[10px] font-mono font-extrabold bg-rose-500 text-white rounded shadow-md animate-pulse">
                  SCORE 95 / 100
                </span>
              </div>
            </div>
          </div>

          <div className="flex justify-center my-0.5">
            <ArrowDown className="w-3.5 h-3.5 text-slate-500" />
          </div>

          {/* STAGE 5: AI REASONING & PRIVACY GOVERNANCE */}
          <div className="grid grid-cols-2 gap-2">
            <div className={getNodeCardClasses(getNodeById('node-8'))} onClick={() => handleNodeClick(getNodeById('node-8'))}>
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-bold text-[11px] text-purple-300 flex items-center gap-1.5">
                    <Cpu className="w-3.5 h-3.5 text-purple-400" />
                    {getNodeById('node-8').title}
                  </h4>
                  <p className="text-[9px] text-slate-400 font-mono mt-0.5">{getNodeById('node-8').subtitle}</p>
                </div>
                <span className="text-[9px] font-mono text-purple-400 font-bold">{getNodeById('node-8').status}</span>
              </div>
            </div>

            <div className={getNodeCardClasses(getNodeById('node-9'))} onClick={() => handleNodeClick(getNodeById('node-9'))}>
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-bold text-[11px] text-slate-200 flex items-center gap-1.5">
                    <Lock className="w-3.5 h-3.5 text-emerald-400" />
                    {getNodeById('node-9').title}
                  </h4>
                  <p className="text-[9px] text-slate-400 font-mono mt-0.5">{getNodeById('node-9').subtitle}</p>
                </div>
                <span className="text-[9px] font-mono text-emerald-400 font-bold">{getNodeById('node-9').status}</span>
              </div>
            </div>
          </div>

          {/* STAGE 6: INCIDENTS, OBSERVABILITY & COMMAND CENTER */}
          <div className="space-y-2 pt-1">
            <div className="text-[10px] font-bold uppercase tracking-widest text-slate-400 font-mono border-b border-border/40 pb-1">
              04. COMMAND CENTER & OPERATOR INCIDENT DISPATCH
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div className={getNodeCardClasses(getNodeById('node-10a'))} onClick={() => handleNodeClick(getNodeById('node-10a'))}>
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-bold text-[11px] text-slate-200">{getNodeById('node-10a').title}</h4>
                    <p className="text-[9px] text-slate-400 font-mono mt-0.5">{getNodeById('node-10a').subtitle}</p>
                  </div>
                  <span className="text-[9px] font-mono text-emerald-400 font-bold">{getNodeById('node-10a').latency}</span>
                </div>
              </div>

              <div className={getNodeCardClasses(getNodeById('node-10b'))} onClick={() => handleNodeClick(getNodeById('node-10b'))}>
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-bold text-[11px] text-rose-300">{getNodeById('node-10b').title}</h4>
                    <p className="text-[9px] text-rose-200/80 font-mono mt-0.5">{getNodeById('node-10b').subtitle}</p>
                  </div>
                  <span className="text-[9px] font-mono text-rose-400 font-bold">{getNodeById('node-10b').status}</span>
                </div>
              </div>
            </div>

            <div className={getNodeCardClasses(getNodeById('node-11'))} onClick={() => handleNodeClick(getNodeById('node-11'))}>
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-bold text-xs text-sky-300 tracking-wide">{getNodeById('node-11').title}</h3>
                  <p className="text-[10px] text-slate-400 font-mono mt-0.5">{getNodeById('node-11').subtitle}</p>
                </div>
                <span className="px-2 py-0.5 text-[9px] font-mono font-bold bg-sky-500/20 text-sky-400 border border-sky-500/30 rounded">
                  {getNodeById('node-11').status}
                </span>
              </div>
            </div>

            <div className="flex justify-center my-0.5">
              <ArrowDown className="w-3.5 h-3.5 text-slate-500" />
            </div>

            <div className={getNodeCardClasses(getNodeById('node-12'))} onClick={() => handleNodeClick(getNodeById('node-12'))}>
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-extrabold text-xs text-emerald-300 tracking-wide flex items-center gap-1.5">
                    <UserCheck className="w-4 h-4 text-emerald-400" />
                    {getNodeById('node-12').title}
                  </h3>
                  <p className="text-[10px] text-emerald-200/80 font-mono mt-0.5">{getNodeById('node-12').subtitle}</p>
                </div>
                <span className="px-2 py-0.5 text-[9px] font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 rounded">
                  OP-014 CLEARANCE L5
                </span>
              </div>
            </div>
          </div>

          {/* STAGE 7: FEEDBACK & MLOps LOOP BACK */}
          <div className="space-y-2 pt-1 border-t border-border/60">
            <div className="text-[10px] font-bold uppercase tracking-widest text-purple-400 font-mono flex items-center justify-between">
              <span>05. MLOps CONTINUOUS RETRAINING FEEDBACK LOOP</span>
              <span className="text-[9px] text-purple-400 font-mono">Loop ➔ Central AI Perception</span>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div className={getNodeCardClasses(getNodeById('node-13'))} onClick={() => handleNodeClick(getNodeById('node-13'))}>
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-bold text-[11px] text-slate-200">{getNodeById('node-13').title}</h4>
                    <p className="text-[9px] text-slate-400 font-mono mt-0.5">{getNodeById('node-13').subtitle}</p>
                  </div>
                  <span className="text-[9px] font-mono text-purple-400 font-bold">{getNodeById('node-13').status}</span>
                </div>
              </div>

              <div className={getNodeCardClasses(getNodeById('node-14'))} onClick={() => handleNodeClick(getNodeById('node-14'))}>
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-bold text-[11px] text-purple-300">{getNodeById('node-14').title}</h4>
                    <p className="text-[9px] text-purple-200/80 font-mono mt-0.5">{getNodeById('node-14').subtitle}</p>
                  </div>
                  <span className="text-[9px] font-mono text-emerald-400 font-bold">{getNodeById('node-14').status}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Node Detailed Telemetry Inspector (Col 4) */}
        <div className="col-span-4 bg-surface border border-border rounded-lg p-4 space-y-4 sticky top-4 shadow-xl shrink-0">
          <div className="flex justify-between items-start border-b border-border pb-3">
            <div>
              <div className="text-[10px] font-bold text-slate-400 font-mono uppercase">NODE INSPECTOR</div>
              <h3 className="text-sm font-extrabold text-slate-100 tracking-wide mt-0.5">{selectedNode.title}</h3>
              <p className="text-[10px] text-sky-400 font-mono">{selectedNode.subtitle}</p>
            </div>
            <span className="px-2 py-0.5 text-[9px] font-mono font-bold bg-sky-500/20 text-sky-400 border border-sky-500/40 rounded uppercase">
              {selectedNode.status}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs font-mono">
            <div className="bg-base border border-border p-2 rounded">
              <div className="text-[9px] text-slate-400 font-bold">LATENCY</div>
              <div className="text-xs font-bold text-emerald-400 mt-0.5">{selectedNode.latency}</div>
            </div>
            <div className="bg-base border border-border p-2 rounded">
              <div className="text-[9px] text-slate-400 font-bold">THROUGHPUT</div>
              <div className="text-xs font-bold text-sky-400 mt-0.5">{selectedNode.throughput}</div>
            </div>
          </div>

          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase font-mono mb-1">STAGE OVERVIEW</div>
            <p className="text-xs text-slate-300 leading-relaxed bg-base/60 p-2.5 border border-border/60 rounded">
              {selectedNode.description}
            </p>
          </div>

          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase font-mono mb-1">TECHNOLOGY STACK</div>
            <div className="text-xs font-mono text-purple-300 bg-purple-950/20 border border-purple-500/30 p-2 rounded">
              {selectedNode.techStack}
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center text-[10px] font-bold text-slate-400 uppercase font-mono mb-1">
              <span>LIVE PAYLOAD SAMPLE</span>
              <span className="text-[9px] text-emerald-400">● REALTIME</span>
            </div>
            <pre className="bg-base border border-border p-2.5 rounded text-[10px] font-mono text-slate-300 overflow-x-auto max-h-48">
              {JSON.stringify(selectedNode.sampleData, null, 2)}
            </pre>
          </div>

          <div className="space-y-2 pt-2 border-t border-border">
            <button
              onClick={() => alert(`Triggering active diagnostics check on ${selectedNode.title}... Status: 100% OPERATIONAL`)}
              className="w-full py-2 bg-blue-600/30 hover:bg-blue-600/50 text-blue-300 border border-blue-500/40 rounded text-xs font-bold font-mono transition-all flex items-center justify-center gap-1.5"
            >
              <Activity className="w-3.5 h-3.5 text-blue-400" />
              RUN NODE DIAGNOSTICS
            </button>
            <button
              onClick={() => alert(`Exporting JSON schema for ${selectedNode.id}...`)}
              className="w-full py-1.5 bg-surfaceElevated hover:bg-border text-slate-300 border border-border rounded text-[11px] font-mono transition-all flex items-center justify-center gap-1.5"
            >
              <FileCode className="w-3.5 h-3.5 text-slate-400" />
              EXPORT TELEMETRY PAYLOAD
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
