# ============================================================
# Simple LLM Test (No encoding issues)
# ============================================================

import subprocess
import time

def test_ollama():
    print("=" * 60)
    print("🧠 Testing Ollama with Mistral")
    print("=" * 60)
    
    # Simple test
    print("\n📝 Test 1: Simple Query")
    print("-" * 40)
    
    try:
        result = subprocess.run(
            ['ollama', 'run', 'mistral:latest', 'Say "Hello" in one word'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✅ Response: {result.stdout.strip()}")
        else:
            print(f"❌ Error: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: Surveillance prompt
    print("\n📝 Test 2: Surveillance Query")
    print("-" * 40)
    
    prompt = """You are a border surveillance AI. 
Describe what to do when someone crosses a border fence in one sentence:"""
    
    try:
        result = subprocess.run(
            ['ollama', 'run', 'mistral:latest', prompt],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=60
        )
        
        if result.returncode == 0:
            print(f"✅ Response: {result.stdout.strip()}")
        else:
            print(f"❌ Error: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Test complete!")

if __name__ == "__main__":
    test_ollama()
