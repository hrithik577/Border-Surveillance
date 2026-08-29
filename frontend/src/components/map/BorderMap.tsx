'use client';

import React, { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { CameraNode, BorderPost, GeofenceZone, TrackedEntity } from '@/types/surveillance';
import { Layers, Maximize2, Compass, ShieldAlert } from 'lucide-react';

interface BorderMapProps {
  cameras: CameraNode[];
  borderPosts: BorderPost[];
  geofences: GeofenceZone[];
  trackedSubject: TrackedEntity;
  selectedCameraId?: string;
  onSelectCamera: (camId: string) => void;
}

export const BorderMap: React.FC<BorderMapProps> = ({
  cameras,
  borderPosts,
  geofences,
  trackedSubject,
  selectedCameraId,
  onSelectCamera
}) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const [showLayersMenu, setShowLayersMenu] = useState(false);

  useEffect(() => {
    if (!mapContainer.current) return;

    const centerLat = 31.6254;
    const centerLng = 74.8765;

    const map = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {
          'carto-dark': {
            type: 'raster',
            tiles: ['https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png'],
            tileSize: 256,
            attribution: '© OpenStreetMap © CARTO'
          }
        },
        layers: [
          {
            id: 'carto-dark-layer',
            type: 'raster',
            source: 'carto-dark',
            minzoom: 0,
            maxzoom: 19
          }
        ]
      },
      center: [centerLng, centerLat],
      zoom: 13.5
    });

    mapRef.current = map;

    map.on('load', () => {
      // 1. National Border Polyline Source & Layer
      map.addSource('border-line', {
        type: 'geojson',
        data: {
          type: 'Feature',
          properties: {},
          geometry: {
            type: 'LineString',
            coordinates: [
              [74.8600, 31.6450],
              [74.8720, 31.6350],
              [74.8850, 31.6250],
              [74.8980, 31.6150]
            ]
          }
        }
      });

      map.addLayer({
        id: 'border-line-layer',
        type: 'line',
        source: 'border-line',
        layout: { 'line-join': 'round', 'line-cap': 'round' },
        paint: {
          'line-color': '#ef4444',
          'line-width': 2.5,
          'line-dasharray': [4, 4]
        }
      });

      // 2. Restricted Geofence Polygon Source & Layer
      map.addSource('geofence-zone-a', {
        type: 'geojson',
        data: {
          type: 'Feature',
          properties: { name: 'Restricted Zone A' },
          geometry: {
            type: 'Polygon',
            coordinates: [
              [
                [74.8740, 31.6280],
                [74.8790, 31.6300],
                [74.8820, 31.6240],
                [74.8770, 31.6220],
                [74.8740, 31.6280]
              ]
            ]
          }
        }
      });

      map.addLayer({
        id: 'geofence-fill',
        type: 'fill',
        source: 'geofence-zone-a',
        paint: {
          'fill-color': '#ef4444',
          'fill-opacity': 0.2
        }
      });

      map.addLayer({
        id: 'geofence-outline',
        type: 'line',
        source: 'geofence-zone-a',
        paint: {
          'line-color': '#ef4444',
          'line-width': 2
        }
      });

      // 3. Tracked Subject P-014 Trajectory Line
      map.addSource('trajectory-p014', {
        type: 'geojson',
        data: {
          type: 'Feature',
          properties: {},
          geometry: {
            type: 'LineString',
            coordinates: [
              [74.8710, 31.6220], // CAM-039
              [74.8745, 31.6240], // CAM-041
              [74.8765, 31.6254], // CAM-042
              [74.8780, 31.6265]  // Breach
            ]
          }
        }
      });

      map.addLayer({
        id: 'trajectory-line',
        type: 'line',
        source: 'trajectory-p014',
        paint: {
          'line-color': '#38bdf8',
          'line-width': 3.5
        }
      });

      // 4. Add Custom HTML Markers for Cameras & BOPs
      cameras.forEach(cam => {
        const el = document.createElement('div');
        el.className = 'w-4 h-4 rounded-full border-2 border-slate-900 cursor-pointer shadow-[0_0_8px_rgba(0,0,0,0.8)] flex items-center justify-center text-[9px] font-bold text-black';
        
        if (cam.status === 'incident') el.style.backgroundColor = '#ef4444';
        else if (cam.status === 'degraded') el.style.backgroundColor = '#f59e0b';
        else el.style.backgroundColor = '#10b981';

        const popup = new maplibregl.Popup({ offset: 25 }).setHTML(`
          <div style="font-family:sans-serif; font-size:12px; color:#0f172a; padding:4px;">
            <b>${cam.id}</b> (${cam.name})<br/>
            Status: <b>${cam.status.toUpperCase()}</b><br/>
            FPS: ${cam.fps} | Latency: ${cam.latencyMs}ms<br/>
            Persons: ${cam.persons} | Vehicles: ${cam.vehicles}
          </div>
        `);

        el.addEventListener('click', () => {
          onSelectCamera(cam.id);
        });

        new maplibregl.Marker({ element: el })
          .setLngLat([cam.lng, cam.lat])
          .setPopup(popup)
          .addTo(map);
      });

      // Border Post Markers
      borderPosts.forEach(bop => {
        const el = document.createElement('div');
        el.className = 'px-1.5 py-0.5 bg-sky-900/90 text-sky-200 border border-sky-400 rounded text-[9px] font-mono font-bold shadow-md cursor-pointer';
        el.textContent = bop.id;

        new maplibregl.Marker({ element: el })
          .setLngLat([bop.lng, bop.lat])
          .addTo(map);
      });
    });

    return () => {
      map.remove();
    };
  }, []);

  useEffect(() => {
    if (!mapRef.current || !selectedCameraId) return;
    const targetCam = cameras.find(c => c.id === selectedCameraId);
    if (targetCam) {
      mapRef.current.flyTo({ center: [targetCam.lng, targetCam.lat], zoom: 15.5 });
    }
  }, [selectedCameraId, cameras]);

  return (
    <div className="relative w-full h-full bg-base border border-border rounded overflow-hidden flex flex-col">
      {/* Map Control Bar */}
      <div className="h-8 bg-surfaceElevated border-b border-border px-3 flex items-center justify-between z-10 shrink-0">
        <div className="text-[11px] font-bold uppercase tracking-wider text-slate-100 flex items-center gap-2">
          <ShieldAlert className="w-3.5 h-3.5 text-sky-400" />
          LIVE BORDER SITUATIONAL MAP (MAPLIBRE GIS ENGINE)
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
            ● REAL-TIME TRAJECTORY
          </span>
          <button
            onClick={() => setShowLayersMenu(!showLayersMenu)}
            className="p-1 bg-surface border border-border text-slate-300 rounded hover:bg-border transition-all"
            title="Toggle GIS Layers"
          >
            <Layers className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Map Canvas */}
      <div ref={mapContainer} className="w-full flex-1" />

      {/* GIS Layers Control Drawer */}
      {showLayersMenu && (
        <div className="absolute top-10 right-3 z-20 bg-surface/95 backdrop-blur-md border border-border rounded p-2.5 w-44 text-[10px] shadow-xl space-y-1">
          <div className="font-bold uppercase text-slate-400 pb-1 border-b border-border mb-1">
            GIS LAYERS
          </div>
          <label className="flex items-center gap-2 text-slate-300 cursor-pointer">
            <input type="checkbox" defaultChecked /> Cameras (247)
          </label>
          <label className="flex items-center gap-2 text-slate-300 cursor-pointer">
            <input type="checkbox" defaultChecked /> Border Posts (4)
          </label>
          <label className="flex items-center gap-2 text-slate-300 cursor-pointer">
            <input type="checkbox" defaultChecked /> Virtual Geofences
          </label>
          <label className="flex items-center gap-2 text-slate-300 cursor-pointer">
            <input type="checkbox" defaultChecked /> Tracked Path P-014
          </label>
        </div>
      )}
    </div>
  );
};
