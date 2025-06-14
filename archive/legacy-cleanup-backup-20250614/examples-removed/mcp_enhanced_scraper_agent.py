"""
MCP Enhanced Scraper Agent for TokenHunter - Framework-free implementation

This agent provides MCP browser control capabilities for improved success 
rates on challenging websites with traditional scraping as fallback.
"""

import asyncio
import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


class MCPBrowserClient:
    """Lightweight MCP client for browser control integration."""

    def __init__(self, mcp_server_path: str):
        self.mcp_server_path = mcp_server_path
        self.process: Optional[subprocess.Popen] = None
        self.request_id = 0
        self.logger = logging.getLogger(__name__)

    async def start_server(self) -> bool:
        """Start the MCP server process."""
        try:
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
                            "name": "tokenhunter-mcp-client",
                            "version": "1.0.0",
                        },
                    },
                }
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to start MCP server: {e}")
            return False

    async def stop_server(self) -> None:
        """Stop the MCP server process."""
        if self.process:
            try:
                await self.call_tool("close_browser", {})
            except:
                pass
            self.process.terminate()
            self.process.wait()

    def _next_id(self) -> int:
        self.request_id += 1
        return self.request_id

    async def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to MCP server."""
        if not self.process:
            raise RuntimeError("MCP server not started")

        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json)
        self.process.stdin.flush()

        response_line = self.process.stdout.readline()
        if not response_line:
            raise RuntimeError("No response from MCP server")

        return json.loads(response_line.strip())

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool."""
        response = await self._send_request(
            {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments},
            }
        )

        if "error" in response:
            raise RuntimeError(f"MCP tool error: {response['error']}")

        return response.get("result", {})


class MCPEnhancedScraperAgent:
    """
    Framework-free enhanced scraper agent that uses MCP browser control
    for challenging websites with enhanced scraping capabilities.

    This agent implements the hybrid approach defined in our MCP integration strategy:
    1. Primary: MCP browser control (comprehensive, high success rate)
    2. Fallback: Traditional scraping methods (when MCP unavailable)
    """

    def __init__(
        self,
        gemini_model=None,
        gemini_config=None,
        event_data_schema=None,
        name: str = "MCPEnhancedScraperAgent",
    ):
        """Initialize the framework-free MCP Enhanced Scraper Agent."""
        self.name = name
        self.gemini_model = gemini_model
        self.gemini_config = gemini_config
        self.event_data_schema = event_data_schema
        self.logger = logging.getLogger(__name__)

        self.logger.info(
            f"[{self.name}] Initialized framework-free MCP Enhanced Scraper Agent"
        )

        # MCP client for enhanced scraping
        self.mcp_client: Optional[MCPBrowserClient] = None
        self.mcp_enabled = False

        # Statistics tracking
        self.stats = {
            "total_attempts": 0,
            "mcp_primary_success": 0,
            "traditional_fallback_used": 0,
            "traditional_fallback_success": 0,
            "total_failures": 0,
        }

    async def initialize_mcp(self, mcp_server_path: Optional[str] = None) -> bool:
        """Initialize MCP browser control capabilities."""
        if not mcp_server_path:
            # Try to find the MCP server in the project
            project_root = Path(__file__).parent.parent
            mcp_server_path = project_root / "mcp_tools" / "dist" / "index.js"

            if not mcp_server_path.exists():
                self.logger.warning(
                    "MCP server not found, running in traditional mode only"
                )
                return False

        try:
            self.mcp_client = MCPBrowserClient(str(mcp_server_path))
            self.mcp_enabled = await self.mcp_client.start_server()

            if self.mcp_enabled:
                self.logger.info("MCP browser control initialized successfully")
            else:
                self.logger.warning(
                    "Failed to initialize MCP, falling back to traditional mode"
                )

            return self.mcp_enabled
        except Exception as e:
            self.logger.error(f"MCP initialization failed: {e}")
            return False

    async def run_async(
        self, website_url: str, existing_event_data: Optional[Dict] = None
    ) -> Tuple[str, Optional[Dict]]:
        """
        Enhanced scraping with MCP primary and traditional fallback.

        Args:
            website_url: URL to scrape
            existing_event_data: Context from original event data

        Returns:
            Tuple of (status, extracted_data)
        """
        self.stats["total_attempts"] += 1
        self.logger.info(f"[{self.name}] Starting enhanced scraping for: {website_url}")

        # Phase 1: Try MCP Browser Control (primary method if available)
        if self.mcp_enabled and self.mcp_client:
            try:
                self.logger.debug("Attempting MCP browser control scraping")
                status, data = await self._mcp_primary_scrape(
                    website_url, existing_event_data
                )

                if status == "Success" and data:
                    self.stats["mcp_primary_success"] += 1
                    self.logger.info("MCP primary scraping successful")
                    return status, data

                self.logger.info(f"MCP primary scraping failed with status: {status}")

            except Exception as e:
                self.logger.warning(f"MCP primary scraping failed with exception: {e}")

        # Phase 2: Traditional Fallback (when MCP unavailable or failed)
        try:
            self.logger.info("Attempting traditional fallback scraping")
            self.stats["traditional_fallback_used"] += 1

            status, data = await self._traditional_fallback_scrape(
                website_url, existing_event_data
            )

            if status == "Success" and data:
                self.stats["traditional_fallback_success"] += 1
                self.logger.info("Traditional fallback scraping successful")
                return status, data

            self.logger.warning(f"Traditional fallback failed with status: {status}")

        except Exception as e:
            self.logger.error(f"Traditional fallback failed with exception: {e}")

        # Both methods failed
        self.stats["total_failures"] += 1
        self.logger.error(f"All scraping methods failed for: {website_url}")

        return "Failed", None

    async def _mcp_primary_scrape(
        self, website_url: str, existing_event_data: Optional[Dict] = None
    ) -> Tuple[str, Optional[Dict]]:
        """Perform MCP-enhanced scraping as primary method."""
        try:
            # Launch browser with MCP
            await self.mcp_client.call_tool(
                "launch_browser", {"headless": True, "debug": False}
            )

            # Navigate to URL with extended timeout
            nav_result = await self.mcp_client.call_tool(
                "navigate_to_url",
                {
                    "url": website_url,
                    "waitFor": "networkidle",
                    "timeout": 45000,  # Extended timeout for challenging sites
                },
            )

            nav_data = json.loads(nav_result["content"][0]["text"])

            if not nav_data.get("success"):
                return "Navigation Failed", None

            # Extract page content
            content_result = await self.mcp_client.call_tool(
                "extract_content", {"extractType": "text"}
            )

            content_data = json.loads(content_result["content"][0]["text"])
            extracted_text = content_data.get("content", "")

            if not extracted_text:
                return "Content Extraction Failed", None

            # Use AI to extract structured data (similar to traditional scraper)
            if self.gemini_model and extracted_text:
                try:
                    structured_data = await self._ai_extract_data(
                        website_url, extracted_text, existing_event_data
                    )
                    return "Success", structured_data

                except Exception as e:
                    self.logger.error(f"AI extraction failed: {e}")
                    return "AI Extraction Failed", None

            # Return raw extracted content if AI extraction not available
            return "Success", {
                "extracted_content": extracted_text,
                "extraction_method": "mcp_raw",
                "url": website_url,
                "title": nav_data.get("title", ""),
                "status": "mcp_fallback_success",
            }

        except Exception as e:
            self.logger.error(f"MCP fallback scraping failed: {e}")
            return "MCP Error", None

        finally:
            try:
                if self.mcp_client:
                    await self.mcp_client.call_tool("close_browser", {})
            except:
                pass

    async def _traditional_fallback_scrape(
        self, website_url: str, existing_event_data: Optional[Dict] = None
    ) -> Tuple[str, Optional[Dict]]:
        """Perform traditional scraping as fallback when MCP is unavailable."""
        try:
            import aiohttp
            from bs4 import BeautifulSoup

            # Simple HTTP request with basic scraping
            async with aiohttp.ClientSession() as session:
                async with session.get(website_url, timeout=30) as response:
                    if response.status != 200:
                        return f"HTTP Error {response.status}", None

                    html_content = await response.text()

            # Basic content extraction with BeautifulSoup
            soup = BeautifulSoup(html_content, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Extract text content
            text_content = soup.get_text()

            # Clean up text
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text_content = " ".join(chunk for chunk in chunks if chunk)

            if not text_content:
                return "Content Extraction Failed", None

            # Use AI to extract structured data if available
            if self.gemini_model and text_content:
                try:
                    structured_data = await self._ai_extract_data(
                        website_url, text_content, existing_event_data
                    )
                    structured_data["extraction_method"] = "traditional_fallback"
                    return "Success", structured_data

                except Exception as e:
                    self.logger.error(
                        f"AI extraction failed in traditional fallback: {e}"
                    )

            # Return basic extracted content if AI extraction not available
            return "Success", {
                "extracted_content": text_content[:2000],  # Limit content size
                "extraction_method": "traditional_basic",
                "url": website_url,
                "title": soup.find("title").get_text() if soup.find("title") else "",
                "status": "traditional_fallback_success",
            }

        except Exception as e:
            self.logger.error(f"Traditional fallback scraping failed: {e}")
            return "Traditional Error", None

    async def _ai_extract_data(
        self, url: str, content: str, existing_event_data: Optional[Dict] = None
    ) -> Dict:
        """Extract structured data using AI (similar to traditional scraper)."""
        if not self.gemini_model:
            raise ValueError("Gemini model not available for AI extraction")

        # Create prompt for AI extraction (similar to ExternalSiteScraperAgent)
        prompt = self._create_extraction_prompt(url, content, existing_event_data)

        # Run AI extraction in thread
        response = await asyncio.to_thread(
            self.gemini_model.generate_content,
            prompt,
            generation_config=self.gemini_config,
        )

        if response and response.text:
            try:
                extracted_data = json.loads(response.text.strip())
                extracted_data["extraction_method"] = "mcp_ai_enhanced"
                return extracted_data
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse AI response: {e}")
                raise

        raise ValueError("No valid response from AI model")

    def _create_extraction_prompt(
        self, url: str, content: str, existing_event_data: Optional[Dict] = None
    ) -> str:
        """Create prompt for AI extraction (similar to ExternalSiteScraperAgent)."""
        # Truncate content if too long
        max_content_length = 8000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "...[truncated]"

        prompt = f"""
        Analyze this website content and extract event-related information.
        
        Website URL: {url}
        
        Existing Event Context:
        {json.dumps(existing_event_data, indent=2) if existing_event_data else "None"}
        
        Website Content:
        {content}
        
        Extract structured information following this schema:
        {json.dumps(self.event_data_schema, indent=2) if self.event_data_schema else "{}"}
        
        Return only a valid JSON object with the extracted information.
        If the page is not relevant to the event, return an empty JSON object {{}}.
        """

        return prompt

    def get_statistics(self) -> Dict[str, Any]:
        """Get scraping statistics."""
        total = self.stats["total_attempts"]
        if total == 0:
            return self.stats

        return {
            **self.stats,
            "mcp_primary_success_rate": self.stats["mcp_primary_success"] / total,
            "traditional_fallback_rate": self.stats["traditional_fallback_used"]
            / total,
            "traditional_fallback_success_rate": (
                self.stats["traditional_fallback_success"]
                / self.stats["traditional_fallback_used"]
                if self.stats["traditional_fallback_used"] > 0
                else 0
            ),
            "overall_success_rate": (
                (
                    self.stats["mcp_primary_success"]
                    + self.stats["traditional_fallback_success"]
                )
                / total
            ),
            "mcp_enabled": self.mcp_enabled,
        }

    async def cleanup(self) -> None:
        """Cleanup MCP resources."""
        if self.mcp_client:
            await self.mcp_client.stop_server()
            self.mcp_client = None
        self.mcp_enabled = False

    def __del__(self):
        """Ensure cleanup on destruction."""
        if self.mcp_enabled and self.mcp_client:
            try:
                # Try to cleanup synchronously
                import asyncio

                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.cleanup())
                else:
                    loop.run_until_complete(self.cleanup())
            except:
                pass
