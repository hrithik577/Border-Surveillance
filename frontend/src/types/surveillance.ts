// ============================================================
// IBVAP Strict TypeScript Type Definitions
// ============================================================

export type CameraStatus = 'online' | 'degraded' | 'offline' | 'incident';
export type IncidentSeverity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type IncidentStatus = 'NEW' | 'ACKNOWLEDGED' | 'INVESTIGATING' | 'DISPATCHED' | 'CONTAINED' | 'RESOLVED';
export type GeofenceRisk = 'SECURE' | 'WARNING' | 'BREACH';

export interface CameraNode {
  id: string;
  name: string;
  lat: number;
  lng: number;
  status: CameraStatus;
  fps: number;
  latencyMs: number;
  persons: number;
  vehicles: number;
  aiActive: boolean;
  streamUrl?: string;
  fovAngle?: number;
  fovBearing?: number;
}

export interface BorderPost {
  id: string;
  name: string;
  lat: number;
  lng: number;
  camerasTotal: number;
  camerasOnline: number;
  incidentsActive: number;
  perimeterStatus: 'SECURE' | 'ALERT' | 'BREACH';
}

export interface GeofenceZone {
  id: string;
  name: string;
  riskLevel: GeofenceRisk;
  polygon: [number, number][];
}

export interface TrackedEntity {
  id: string;
  type: 'PERSON' | 'VEHICLE' | 'UNKNOWN';
  confidence: number;
  currentCam: string;
  trajectory: { camId: string; lat: number; lng: number; timestamp: string }[];
  breachedZone?: string;
}

export interface IncidentAlert {
  id: string;
  timestamp: string;
  severity: IncidentSeverity;
  event: string;
  location: string;
  camera: string;
  confidence: number;
  threatScore: number;
  status: IncidentStatus;
  assignedOperator?: string;
  evidenceSnapshot?: string;
}

export interface SystemMetrics {
  camerasOnline: number;
  camerasTotal: number;
  aiModelsActive: number;
  aiModelsTotal: number;
  activeAlerts: number;
  gpuUtilization: number;
  inferenceFps: number;
  latencyMs: number;
  vramUsage: string;
  accuracy: number;
  precision: number;
  recall: number;
  personsDetected: number;
  vehiclesDetected: number;
  securityEvents: number;
  criticalAlerts: number;
  anprMatches: number;
  intrusions: number;
}

export interface ANPRMatch {
  id: string;
  plate: string;
  vehicleType: string;
  camera: string;
  location: string;
  timestamp: string;
  confidence: number;
  status: 'CLEAR' | 'REVIEW REQUIRED' | 'WATCHLIST MATCH';
  flagged: boolean;
}

export interface FaceDetection {
  id: string;
  camera: string;
  timestamp: string;
  confidence: number;
  status: 'AUTHORIZED' | 'UNKNOWN PERSON' | 'REVIEW REQUIRED';
  flagged: boolean;
}

export interface BehaviourEvent {
  id: string;
  event: string;
  riskScore: number;
  confidence: number;
  camera: string;
  duration: string;
  status: string;
}

export interface EvidenceRecord {
  id: string;
  incidentId: string;
  camera: string;
  location: string;
  timestamp: string;
  hash: string;
  status: 'LOCKED' | 'ARCHIVED' | 'EXPORTED';
}

export interface AuditLogItem {
  id: string;
  timestamp: string;
  operator: string;
  action: string;
  resource: string;
  status: 'SUCCESS' | 'FAILED' | 'PENDING';
}
