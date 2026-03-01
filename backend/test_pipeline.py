import asyncio
import traceback
from app.agents.orchestrator import AgentOrchestrator

async def main():
    try:
        from app.services.vector_store import vector_store
        vector_store.build_index()
        o = AgentOrchestrator()
        await o.run_pipeline("climate", "africa", "test")
    except Exception as e:
        traceback.print_exc()

asyncio.run(main())
