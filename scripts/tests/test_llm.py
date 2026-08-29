import sys
sys.path.insert(0, 'C:/IBVAP-Demo')
from src.utils.llm_integration import IBVAP_LLM

# Initialize LLM
llm = IBVAP_LLM()

# Test scene analysis
print("=" * 60)
print("🧠 Testing LLM Integration with Mistral")
print("=" * 60)

# Test 1: Scene analysis
test_data = {
    'camera': 'Border Camera 1',
    'people': 3,
    'vehicles': 1,
    'alerts': 0,
    'timestamp': '14:30:45',
    'status': 'normal'
}

print("\n📊 Test 1: Scene Analysis")
print("-" * 40)
response = llm.analyze_scene_async(test_data)
print(f"Response: {response}")

# Wait for async processing
import time
time.sleep(2)

print("\n✅ Analysis complete!")
print(f"Analysis: {llm.last_response}")

# Test 2: Alert generation
print("\n🚨 Test 2: Alert Generation")
print("-" * 40)
alert = llm.generate_alert_description({
    'type': 'intrusion',
    'object': 'person',
    'location': 'border fence',
    'timestamp': '14:32:10',
    'severity': 'high'
})
print(f"Alert: {alert}")

# Test 3: Report generation
print("\n📋 Test 3: Report Generation")
print("-" * 40)
report = llm.generate_report({
    'total_frames': 12543,
    'total_people': 45,
    'total_vehicles': 12,
    'total_alerts': 3,
    'intrusions': 2,
    'uptime': '2h 15m'
})
print(f"Report:\n{report}")
