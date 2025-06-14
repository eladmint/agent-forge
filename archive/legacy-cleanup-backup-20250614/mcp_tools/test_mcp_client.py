#!/usr/bin/env python3
"""
Test client for the TokenHunter Browser Control MCP server.

This client demonstrates how to integrate MCP browser control 
with the existing TokenHunter scraping workflow.
"""

import asyncio
import json
import subprocess
from typing import Any, Dict, List, Optional


class MCPBrowserClient:
    """Client for communicating with the Browser Control MCP server."""

    def __init__(self, mcp_server_path: str):
        """Initialize the MCP client.

        Args:
            mcp_server_path: Path to the MCP server executable
        """
        self.mcp_server_path = mcp_server_path
        self.process: Optional[subprocess.Popen] = None
        self.request_id = 0

    async def start_server(self) -> None:
        """Start the MCP server process."""
        self.process = subprocess.Popen(
            ["node", self.mcp_server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0,
        )

        # Initialize the connection
        await self._send_request(
            {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {
                        "name": "tokenhunter-test-client",
                        "version": "1.0.0",
                    },
                },
            }
        )

    async def stop_server(self) -> None:
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            self.process.wait()

    def _next_id(self) -> int:
        """Get next request ID."""
        self.request_id += 1
        return self.request_id

    async def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request to the MCP server and get response."""
        if not self.process:
            raise RuntimeError("MCP server not started")

        # Send request
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json)
        self.process.stdin.flush()

        # Read response
        response_line = self.process.stdout.readline()
        if not response_line:
            raise RuntimeError("No response from MCP server")

        return json.loads(response_line.strip())

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools."""
        response = await self._send_request(
            {"jsonrpc": "2.0", "id": self._next_id(), "method": "tools/list"}
        )

        if "error" in response:
            raise RuntimeError(f"Error listing tools: {response['error']}")

        return response.get("result", {}).get("tools", [])

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool with given arguments."""
        response = await self._send_request(
            {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments},
            }
        )

        if "error" in response:
            raise RuntimeError(f"Error calling tool {name}: {response['error']}")

        return response.get("result", {})


class MCPScrapingEnhancer:
    """Enhanced scraping capabilities using MCP browser control."""

    def __init__(self, mcp_client: MCPBrowserClient):
        """Initialize the scraping enhancer.

        Args:
            mcp_client: MCP browser client instance
        """
        self.mcp_client = mcp_client

    async def enhanced_scrape_site(
        self, url: str, debug: bool = False
    ) -> Dict[str, Any]:
        """Scrape a site using MCP browser control with enhanced capabilities.

        Args:
            url: URL to scrape
            debug: Enable debug mode for interactive exploration

        Returns:
            Dictionary containing scraped data and metadata
        """
        results = {
            "url": url,
            "success": False,
            "data": {},
            "metadata": {},
            "debug_info": {},
        }

        try:
            # Launch browser
            print(f"🚀 Launching browser for {url}")
            await self.mcp_client.call_tool(
                "launch_browser", {"headless": not debug, "debug": debug}
            )

            # Navigate to URL
            print(f"🌐 Navigating to {url}")
            nav_result = await self.mcp_client.call_tool(
                "navigate_to_url",
                {"url": url, "waitFor": "networkidle", "timeout": 30000},
            )

            nav_data = json.loads(nav_result["content"][0]["text"])
            results["metadata"]["navigation"] = nav_data

            if not nav_data.get("success"):
                raise RuntimeError(f"Failed to navigate to {url}")

            # Extract page content
            print("📄 Extracting page content")
            content_result = await self.mcp_client.call_tool(
                "extract_content", {"extractType": "text"}
            )

            content_data = json.loads(content_result["content"][0]["text"])
            results["data"]["text_content"] = content_data["content"]

            # Extract HTML structure
            html_result = await self.mcp_client.call_tool(
                "extract_content", {"extractType": "html"}
            )

            html_data = json.loads(html_result["content"][0]["text"])
            results["data"]["html_content"] = html_data["content"]

            # Take screenshot for debugging
            if debug:
                print("📸 Taking screenshot")
                screenshot_result = await self.mcp_client.call_tool(
                    "take_screenshot",
                    {
                        "fullPage": True,
                        "path": f"debug_screenshot_{int(asyncio.get_event_loop().time())}.png",
                    },
                )

                screenshot_data = json.loads(screenshot_result["content"][0]["text"])
                results["debug_info"]["screenshot"] = screenshot_data

            # Analyze network requests
            print("🔍 Analyzing network requests")
            network_result = await self.mcp_client.call_tool(
                "analyze_network", {"includeRedirects": True}
            )

            network_data = json.loads(network_result["content"][0]["text"])
            results["metadata"]["network"] = network_data

            results["success"] = True
            print("✅ Enhanced scraping completed successfully")

        except Exception as e:
            print(f"❌ Enhanced scraping failed: {e}")
            results["error"] = str(e)

        finally:
            # Close browser
            try:
                await self.mcp_client.call_tool("close_browser", {})
            except Exception as e:
                print(f"⚠️ Warning: Failed to close browser: {e}")

        return results

    async def compare_with_traditional_scraping(self, url: str) -> Dict[str, Any]:
        """Compare MCP-enhanced scraping with traditional methods.

        Args:
            url: URL to scrape with both methods

        Returns:
            Comparison results
        """
        print(f"🔬 Comparing scraping methods for {url}")

        # Traditional scraping (using requests + BeautifulSoup)
        traditional_start = asyncio.get_event_loop().time()
        traditional_result = await self._traditional_scrape(url)
        traditional_time = asyncio.get_event_loop().time() - traditional_start

        # MCP-enhanced scraping
        mcp_start = asyncio.get_event_loop().time()
        mcp_result = await self.enhanced_scrape_site(url, debug=False)
        mcp_time = asyncio.get_event_loop().time() - mcp_start

        return {
            "url": url,
            "traditional": {
                "result": traditional_result,
                "time_seconds": traditional_time,
                "success": traditional_result.get("success", False),
            },
            "mcp_enhanced": {
                "result": mcp_result,
                "time_seconds": mcp_time,
                "success": mcp_result.get("success", False),
            },
            "comparison": {
                "mcp_advantage": mcp_result.get("success", False)
                and not traditional_result.get("success", False),
                "time_difference": mcp_time - traditional_time,
                "content_length_diff": len(str(mcp_result.get("data", {})))
                - len(str(traditional_result.get("data", {}))),
            },
        }

    async def _traditional_scrape(self, url: str) -> Dict[str, Any]:
        """Traditional scraping using requests and BeautifulSoup."""
        try:
            import requests
            from bs4 import BeautifulSoup

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            return {
                "success": True,
                "data": {
                    "text_content": soup.get_text(),
                    "html_content": str(soup),
                    "title": soup.title.string if soup.title else None,
                },
                "metadata": {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "url": response.url,
                },
            }
        except Exception as e:
            return {"success": False, "error": str(e), "data": {}, "metadata": {}}


async def main():
    """Test the MCP browser control integration."""
    print("🧪 Testing TokenHunter MCP Browser Control Integration")

    # Initialize MCP client
    mcp_server_path = "dist/index.js"
    client = MCPBrowserClient(mcp_server_path)

    try:
        # Start the MCP server
        print("🔧 Starting MCP server...")
        await client.start_server()

        # List available tools
        print("📋 Listing available tools...")
        tools = await client.list_tools()
        print(f"Available tools: {[tool['name'] for tool in tools]}")

        # Initialize scraping enhancer
        enhancer = MCPScrapingEnhancer(client)

        # Test URLs (including some that might challenge traditional scraping)
        test_urls = [
            "https://lu.ma/event-example",  # Example Luma event page
            "https://httpbin.org/html",  # Simple test page
        ]

        for url in test_urls:
            print(f"\n🎯 Testing enhanced scraping for: {url}")
            try:
                result = await enhancer.enhanced_scrape_site(url, debug=True)
                print(f"Result: {'✅ Success' if result['success'] else '❌ Failed'}")
                if result.get("error"):
                    print(f"Error: {result['error']}")
                else:
                    print(f"Content length: {len(str(result['data']))}")
                    print(
                        f"Title: {result['metadata'].get('navigation', {}).get('title', 'N/A')}"
                    )
            except Exception as e:
                print(f"❌ Test failed: {e}")

        print("\n🎉 MCP integration testing completed!")

    except Exception as e:
        print(f"❌ MCP testing failed: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Stop the MCP server
        print("🛑 Stopping MCP server...")
        await client.stop_server()


if __name__ == "__main__":
    asyncio.run(main())
