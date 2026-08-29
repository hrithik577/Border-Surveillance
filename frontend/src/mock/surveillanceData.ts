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
  camerasOnline: 247,
  camerasTotal: 255,
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

export const mockCameras: CameraNode[] = [
  { id: 'CAM-042', name: 'BOP ALPHA-07 Perimeter', lat: 31.6254, lng: 74.8765, status: 'incident', fps: 28.4, latencyMs: 31, persons: 3, vehicles: 1, aiActive: true, fovAngle: 65, fovBearing: 45 },
  { id: 'CAM-071', name: 'Border Road 12 Junction', lat: 31.6312, lng: 74.8821, status: 'degraded', fps: 29.1, latencyMs: 34, persons: 1, vehicles: 2, aiActive: true, fovAngle: 60, fovBearing: 120 },
  { id: 'CAM-039', name: 'Sector Alpha North', lat: 31.6220, lng: 74.8710, status: 'online', fps: 30.0, latencyMs: 29, persons: 2, vehicles: 0, aiActive: true, fovAngle: 70, fovBearing: 15 },
  { id: 'CAM-041', name: 'Outpost N Checkpoint', lat: 31.6240, lng: 74.8745, status: 'online', fps: 27.8, latencyMs: 32, persons: 1, vehicles: 1, aiActive: true, fovAngle: 55, fovBearing: 90 },
  { id: 'CAM-013', name: 'Gate 04 Main Entrance', lat: 31.6380, lng: 74.8690, status: 'online', fps: 28.5, latencyMs: 30, persons: 5, vehicles: 3, aiActive: true, fovAngle: 80, fovBearing: 210 },
  { id: 'CAM-032', name: 'Checkpost 02 Road', lat: 31.6190, lng: 74.8850, status: 'online', fps: 29.4, latencyMs: 31, persons: 0, vehicles: 4, aiActive: true, fovAngle: 65, fovBearing: 180 },
  { id: 'CAM-056', name: 'Freight Terminal East', lat: 31.6290, lng: 74.8640, status: 'online', fps: 30.0, latencyMs: 28, persons: 4, vehicles: 6, aiActive: true, fovAngle: 75, fovBearing: 300 },
  { id: 'CAM-091', name: 'Sector Bravo Patrol', lat: 31.6150, lng: 74.8910, status: 'online', fps: 28.0, latencyMs: 33, persons: 1, vehicles: 1, aiActive: true, fovAngle: 60, fovBearing: 135 }
];

export const mockBorderPosts: BorderPost[] = [
  { id: 'BOP ALPHA-07', name: 'Sector Alpha Outpost 7', lat: 31.6254, lng: 74.8765, camerasTotal: 18, camerasOnline: 17, incidentsActive: 2, perimeterStatus: 'ALERT' },
  { id: 'BOP CHARLIE-03', name: 'Sector Charlie Outpost 3', lat: 31.6350, lng: 74.8720, camerasTotal: 14, camerasOnline: 14, incidentsActive: 0, perimeterStatus: 'SECURE' },
  { id: 'BOP DELTA-09', name: 'Sector Delta Outpost 9', lat: 31.6180, lng: 74.8920, camerasTotal: 22, camerasOnline: 21, incidentsActive: 1, perimeterStatus: 'SECURE' },
  { id: 'BOP ECHO-11', name: 'Sector Echo Outpost 11', lat: 31.6420, lng: 74.8580, camerasTotal: 16, camerasOnline: 15, incidentsActive: 0, perimeterStatus: 'SECURE' }
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
  },
  {
    id: 'CRITICAL-PERIMETER-B',
    name: 'Critical Perimeter Zone B',
    riskLevel: 'SECURE',
    polygon: [
      [31.6340, 74.8680],
      [31.6380, 74.8740],
      [31.6320, 74.8770],
      [31.6300, 74.8700]
    ]
  }
];

export const mockTrackedSubject: TrackedEntity = {
  id: 'P-014',
  type: 'PERSON',
  confidence: 96.7,
  currentCam: 'CAM-042',
  trajectory: [
    { camId: 'CAM-039', lat: 31.6220, lng: 74.8710, timestamp: '21:43:10' },
    { camId: 'CAM-041', lat: 31.6240, lng: 74.8745, timestamp: '21:43:14' },
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
    event: 'Virtual fence breach',
    location: 'Border Road 12',
    camera: 'CAM-071',
    confidence: 94.2,
    threatScore: 84,
    status: 'ACKNOWLEDGED'
  },
  {
    id: 'IBV-240180',
    timestamp: '21:41:07 IST',
    severity: 'MEDIUM',
    event: 'Unknown vehicle loitering',
    location: 'Border Road 6',
    camera: 'CAM-032',
    confidence: 88.6,
    threatScore: 62,
    status: 'NEW'
  },
  {
    id: 'IBV-240177',
    timestamp: '21:38:22 IST',
    severity: 'LOW',
    event: 'ANPR watchlist match',
    location: 'Gate 04 Checkpost',
    camera: 'CAM-013',
    confidence: 98.4,
    threatScore: 45,
    status: 'RESOLVED'
  }
];

export const mockANPR: ANPRMatch[] = [
  { id: 'ANPR-101', plate: 'KA05XY7821', vehicleType: 'SUV', camera: 'CAM-032', location: 'Gate 04 Checkpost', timestamp: '21:37 IST', confidence: 96.8, status: 'REVIEW REQUIRED', flagged: true },
  { id: 'ANPR-102', plate: 'KA01AB1234', vehicleType: 'SEDAN', camera: 'CAM-013', location: 'Checkpost 02', timestamp: '21:34 IST', confidence: 98.4, status: 'CLEAR', flagged: false },
  { id: 'ANPR-103', plate: 'DL03CC9081', vehicleType: 'TRUCK', camera: 'CAM-056', location: 'Freight Gate', timestamp: '21:28 IST', confidence: 94.1, status: 'CLEAR', flagged: false },
  { id: 'ANPR-104', plate: 'HR26DQ4411', vehicleType: 'PICKUP', camera: 'CAM-091', location: 'Sector Bravo', timestamp: '21:15 IST', confidence: 97.2, status: 'CLEAR', flagged: false }
];

export const mockFaces: FaceDetection[] = [
  { id: 'FACE-1092', camera: 'CAM-042', timestamp: '21:43 IST', confidence: 96.7, status: 'UNKNOWN PERSON', flagged: true },
  { id: 'FACE-1088', camera: 'CAM-013', timestamp: '21:39 IST', confidence: 99.1, status: 'AUTHORIZED', flagged: false },
  { id: 'FACE-1085', camera: 'CAM-032', timestamp: '21:35 IST', confidence: 94.5, status: 'UNKNOWN PERSON', flagged: true }
];

export const mockBehaviour: BehaviourEvent[] = [
  { id: 'BEH-501', event: 'LOITERING NEAR RESTRICTED ZONE', riskScore: 78, confidence: 91.4, camera: 'CAM-013', duration: '04:18', status: 'ACTIVE' },
  { id: 'BEH-502', event: 'WRONG-DIRECTION VEHICLE MOVEMENT', riskScore: 65, confidence: 89.2, camera: 'CAM-056', duration: '01:45', status: 'MONITORING' },
  { id: 'BEH-503', event: 'GROUP FORMATION NEAR FENCE', riskScore: 82, confidence: 93.7, camera: 'CAM-042', duration: '03:10', status: 'REVIEW REQUIRED' }
];

export const mockEvidence: EvidenceRecord[] = [
  { id: 'EV-9941', incidentId: 'IBV-240184', camera: 'CAM-042', location: 'Sector Alpha / BOP-07', timestamp: '21:43:18 IST', hash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', status: 'LOCKED' },
  { id: 'EV-9940', incidentId: 'IBV-240183', camera: 'CAM-071', location: 'Border Road 12', timestamp: '21:42:51 IST', hash: '8f4e9112423985a218d6e9871f9273c509748239081230491823940192834019', status: 'ARCHIVED' }
];

export const mockAuditLogs: AuditLogItem[] = [
  { id: 'LOG-301', timestamp: '21:43:23 IST', operator: 'OP-014', action: 'Incident acknowledged', resource: 'IBV-240184', status: 'SUCCESS' },
  { id: 'LOG-302', timestamp: '21:44:01 IST', operator: 'OP-014', action: 'Evidence locked & encrypted', resource: 'EV-9941', status: 'SUCCESS' },
  { id: 'LOG-303', timestamp: '21:45:12 IST', operator: 'OP-014', action: 'Patrol alert dispatched', resource: 'SECTOR ALPHA / BOP-07', status: 'SUCCESS' }
];
