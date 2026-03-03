import asyncio
import time
import httpx
import sys
import os

# Setup path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

async def run_benchmark():
    url = "http://localhost:8000/analyze-project"
    payload = {
        "sector": "climate",
        "region": "East Africa",
        "project_description": "Benchmark test for deep documentation verification"
    }
    
    print("\n🚀 Starting Technical Velocity Benchmark...")
    start_time = time.perf_counter()
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, json=payload)
            duration = time.perf_counter() - start_time
            
            if response.status_code == 200:
                meta = response.json().get("metadata", {})
                pipeline_time = meta.get("pipeline_duration_seconds", "N/A")
                print(f"✅ Success! Total Roundtrip: {duration:.2f}s")
                print(f"🤖 Internal Pipeline Time: {pipeline_time}s")
                
                if duration < 15:
                    print(f"🔥 Performance Rating: ELITE (<10s target met locally)")
                else:
                    print(f"⚠️ Performance Rating: NOMINAL (Check network/API latency)")
            else:
                print(f"❌ Error: {response.status_code} - Is the backend running at {url}?")
                
        except Exception as e:
            print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
