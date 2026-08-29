import {
  CameraNode,
  BorderPost,
  GeofenceZone,
  TrackedEntity,
  IncidentAlert,
  SystemMetrics,
  ANPRMatch,
  FaceDetection,
  BehaviourEvent,
  EvidenceRecord,
  AuditLogItem
} from '../types/surveillance';

export const mockMetrics: SystemMetrics = {
  camerasOnline: 2,
  camerasTotal: 2,
  aiModelsActive: 12,
  aiModelsTotal: 12,
  activeAlerts: 16,
  gpuUtilization: 76,
  inferenceFps: 28.4,
  latencyMs: 31,
  vramUsage: '8.4 / 12 GB',
  accuracy: 94.8,
  precision: 95.2,
  recall: 93.7,
  personsDetected: 1284,
  vehiclesDetected: 437,
  securityEvents: 23,
  criticalAlerts: 4,
  anprMatches: 17,
  intrusions: 6
};

// 2 Primary CCTV Channels for Direct Video Playback
export const mockCameras: CameraNode[] = [
  { id: 'CAM-042', name: 'BOP ALPHA-07 Perimeter Feed', lat: 31.6254, lng: 74.8765, status: 'incident', fps: 28.4, latencyMs: 31, persons: 3, vehicles: 1, aiActive: true, fovAngle: 65, fovBearing: 45 },
  { id: 'CAM-071', name: 'Top View Pedestrian Surveillance', lat: 31.6312, lng: 74.8821, status: 'degraded', fps: 29.1, latencyMs: 34, persons: 4, vehicles: 0, aiActive: true, fovAngle: 60, fovBearing: 120 }
];

export const mockBorderPosts: BorderPost[] = [
  { id: 'BOP ALPHA-07', name: 'Sector Alpha Outpost 7', lat: 31.6254, lng: 74.8765, camerasTotal: 1, camerasOnline: 1, incidentsActive: 1, perimeterStatus: 'ALERT' },
  { id: 'BOP CHARLIE-03', name: 'Sector Charlie Outpost 3', lat: 31.6312, lng: 74.8821, camerasTotal: 1, camerasOnline: 1, incidentsActive: 1, perimeterStatus: 'SECURE' }
];

export const mockGeofences: GeofenceZone[] = [
  {
    id: 'RESTRICTED-ZONE-A',
    name: 'Restricted Zone A',
    riskLevel: 'BREACH',
    polygon: [
      [31.6280, 74.8740],
      [31.6300, 74.8790],
      [31.6240, 74.8820],
      [31.6220, 74.8770]
    ]
  }
];

export const mockTrackedSubject: TrackedEntity = {
  id: 'P-014',
  type: 'PERSON',
  confidence: 96.7,
  currentCam: 'CAM-042',
  trajectory: [
    { camId: 'CAM-071', lat: 31.6312, lng: 74.8821, timestamp: '21:43:10' },
    { camId: 'CAM-042', lat: 31.6254, lng: 74.8765, timestamp: '21:43:18' }
  ],
  breachedZone: 'Restricted Zone A'
};

export const mockIncidents: IncidentAlert[] = [
  {
    id: 'IBV-240184',
    timestamp: '21:43:18 IST',
    severity: 'CRITICAL',
    event: 'Unauthorized perimeter crossing',
    location: 'Sector Alpha / BOP-07',
    camera: 'CAM-042',
    confidence: 96.7,
    threatScore: 91,
    status: 'INVESTIGATING',
    assignedOperator: 'OP-014 (COMMAND OFFICER)'
  },
  {
    id: 'IBV-240183',
    timestamp: '21:42:51 IST',
    severity: 'HIGH',
    event: 'Top-view pedestrian zone breach',
    location: 'Border Sector 12',
    camera: 'CAM-071',
    confidence: 94.2,
    threatScore: 84,
    status: 'ACKNOWLEDGED'
  }
];

export const mockANPR: ANPRMatch[] = [
  { id: 'ANPR-101', plate: 'KA05XY7821', vehicleType: 'SUV', camera: 'CAM-042', location: 'BOP-07 Checkpost', timestamp: '21:37 IST', confidence: 96.8, status: 'REVIEW REQUIRED', flagged: true }
];

export const mockFaces: FaceDetection[] = [
  { id: 'FACE-1092', camera: 'CAM-042', timestamp: '21:43 IST', confidence: 96.7, status: 'UNKNOWN PERSON', flagged: true }
];

export const mockBehaviour: BehaviourEvent[] = [
  { id: 'BEH-501', event: 'LOITERING NEAR RESTRICTED ZONE', riskScore: 78, confidence: 91.4, camera: 'CAM-042', duration: '04:18', status: 'ACTIVE' }
];

export const mockEvidence: EvidenceRecord[] = [
  { id: 'EV-9941', incidentId: 'IBV-240184', camera: 'CAM-042', location: 'Sector Alpha / BOP-07', timestamp: '21:43:18 IST', hash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', status: 'LOCKED' }
];

export const mockAuditLogs: AuditLogItem[] = [
  { id: 'LOG-301', timestamp: '21:43:23 IST', operator: 'OP-014', action: 'Incident acknowledged', resource: 'IBV-240184', status: 'SUCCESS' }
];
