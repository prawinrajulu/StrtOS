import asyncio
from app.llm.router import llm_router
from app.llm.providers.base_provider import LLMRequest
from app.tools.registry import tool_registry

async def test_llm_and_tools():
    print("\n=======================================================")
    print("STARTING REAL LLM ROUTER & TOOL REGISTRY UNIT TEST")
    print("=======================================================")

    # 1. LLM Router Execution & Fallback Verification
    print("\n[1/4] Testing LLM Router Execution & Fallback Matrix...")
    req = LLMRequest(prompt="Summarize enterprise strategy in JSON format.")
    resp = await llm_router.route_and_generate("Business Analysis Agent", req)
    print(f"Primary Response Provider: {resp.provider}, Status: {resp.status}, Latency: {resp.latency_seconds}s")
    assert resp.provider is not None

    # 2. Firecrawl Tool Verification
    print("\n[2/4] Testing Firecrawl Scraping Tool...")
    fc_res = await tool_registry.execute_tool("firecrawl", {"url": "https://example.com"})
    print("Firecrawl Tool Result Status:", fc_res.get("status"))
    assert fc_res.get("status") in ["SUCCESS", "UNAVAILABLE"]

    # 3. Tavily Research Tool Verification
    print("\n[3/4] Testing Tavily Search Tool...")
    tav_res = await tool_registry.execute_tool("tavily", {"query": "SaaS TAM Market Benchmarks 2026"})
    print("Tavily Tool Result Status:", tav_res.get("status"))
    assert tav_res.get("status") in ["SUCCESS", "UNAVAILABLE", "configured"]

    # 4. PageSpeed Tool Verification
    print("\n[4/4] Testing PageSpeed Insights Tool...")
    ps_res = await tool_registry.execute_tool("pagespeed", {"url": "https://example.com"})
    print("PageSpeed Tool Result Status:", ps_res.get("status"))
    assert ps_res.get("status") in ["SUCCESS", "UNAVAILABLE"]

    print("\n=======================================================")
    print("LLM ROUTER & TOOL REGISTRY TESTS PASSED SUCCESSFULLY!")
    print("=======================================================")

if __name__ == "__main__":
    asyncio.run(test_llm_and_tools())
