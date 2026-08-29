// ============================================================
// IBVAP WebSocket Service (Event Emitter Architecture)
// ============================================================

type EventCallback = (data: any) => void;

class SurveillanceWebSocketService {
  private listeners: Map<string, EventCallback[]> = new Map();
  private isConnected: boolean = false;

  constructor() {
    this.initMockConnection();
  }

  private initMockConnection() {
    this.isConnected = true;
    console.log('[IBVAP WS] Service connected (Simulated/FastAPI backend subscriber).');
  }

  public subscribe(event: string, callback: EventCallback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)?.push(callback);
  }

  public unsubscribe(event: string, callback: EventCallback) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      this.listeners.set(event, callbacks.filter(cb => cb !== callback));
    }
  }

  public emit(event: string, data: any) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach(cb => cb(data));
    }
  }

  public status(): boolean {
    return this.isConnected;
  }
}

export const wsService = new SurveillanceWebSocketService();
