# ============================================================
# IBVAP - LLM Integration with Mistral
# src/utils/llm_integration.py
# ============================================================

import subprocess
import json
import threading
import time
from datetime import datetime
import re

class IBVAP_LLM:
    """
    LLM Integration for IBVAP using Ollama (Mistral)
    """
    
    def __init__(self, model="mistral:latest"):
        self.model = model
        self.last_response = None
        self.is_processing = False
        self.analysis_history = []
        self.alert_count = 0
        
        print(f"✅ LLM initialized with model: {model}")
    
    def query(self, prompt, timeout=30):
        """
        Send a query to the LLM and get response
        """
        try:
            result = subprocess.run(
                ['ollama', 'run', self.model, prompt],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "Error: Request timed out"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def analyze_scene_async(self, detection_data, callback=None):
        """
        Analyze scene in background (non-blocking)
        """
        def task():
            self.is_processing = True
            try:
                # Build prompt with detection data
                prompt = self._build_scene_prompt(detection_data)
                response = self.query(prompt)
                
                self.last_response = response
                self.analysis_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'data': detection_data,
                    'analysis': response
                })
                
                if callback:
                    callback(response)
                    
            except Exception as e:
                print(f"LLM Error: {e}")
            self.is_processing = False
        
        threading.Thread(target=task, daemon=True).start()
        return "Analyzing scene..."
    
    def _build_scene_prompt(self, data):
        """
        Build a prompt for scene analysis
        """
        return f"""
You are IBVAP, an Intelligent Border Video Analytics Platform. 
Analyze the following border surveillance scene:

- Camera: {data.get('camera', 'Border Camera 1')}
- People detected: {data.get('people', 0)}
- Vehicles detected: {data.get('vehicles', 0)}
- Total alerts: {data.get('alerts', 0)}
- Time: {data.get('timestamp', 'now')}
- Status: {data.get('status', 'normal')}

Provide a brief, professional situation description (2-3 sentences):
"""
    
    def generate_alert_description(self, alert_data):
        """
        Generate a human-readable alert description
        """
        prompt = f"""
Generate a concise border security alert for the following situation:

Alert Type: {alert_data.get('type', 'intrusion')}
Object: {alert_data.get('object', 'person')}
Location: {alert_data.get('location', 'border fence')}
Time: {alert_data.get('timestamp', 'now')}
Severity: {alert_data.get('severity', 'medium')}

Alert Description (one sentence):
"""
        return self.query(prompt)
    
    def generate_report(self, stats_data):
        """
        Generate a periodic surveillance report
        """
        prompt = f"""
Generate a border surveillance report based on the following data:

Total Frames Processed: {stats_data.get('total_frames', 0)}
People Detected: {stats_data.get('total_people', 0)}
Vehicles Detected: {stats_data.get('total_vehicles', 0)}
Total Alerts: {stats_data.get('total_alerts', 0)}
Intrusions: {stats_data.get('intrusions', 0)}
Uptime: {stats_data.get('uptime', 'N/A')}

Report (3-4 sentences covering activity summary and security status):
"""
        return self.query(prompt)
    
    def answer_question(self, question, context_data):
        """
        Answer user questions about the surveillance
        """
        prompt = f"""
Based on the following border surveillance context:

{json.dumps(context_data, indent=2)}

Answer the user's question:
Question: {question}

Answer (concise, informative):
"""
        return self.query(prompt)
    
    def get_recent_analysis(self, count=5):
        """
        Get recent analysis history
        """
        return self.analysis_history[-count:] if self.analysis_history else []
    
    def get_status(self):
        """
        Get LLM status
        """
        return {
            'model': self.model,
            'is_processing': self.is_processing,
            'last_response': self.last_response,
            'history_count': len(self.analysis_history),
            'alert_count': self.alert_count
        }

# ============================================================
# Integration Helper Functions
# ============================================================

def generate_intelligent_alert(llm, detection_count, event_type, details):
    """
    Generate an intelligent alert using LLM
    """
    alert_data = {
        'type': event_type,
        'object': details.get('class', 'unknown'),
        'location': 'border fence area',
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'severity': 'high' if event_type == 'intrusion' else 'medium',
        'count': detection_count
    }
    
    description = llm.generate_alert_description(alert_data)
    return description

def create_summary_report(llm, stats, uptime):
    """
    Create a summary report with LLM
    """
    stats_data = {
        'total_frames': stats.get('total_frames', 0),
        'total_people': stats.get('total_people', 0),
        'total_vehicles': stats.get('total_vehicles', 0),
        'total_alerts': stats.get('total_alerts', 0),
        'intrusions': stats.get('intrusions', 0),
        'uptime': uptime
    }
    
    return llm.generate_report(stats_data)
