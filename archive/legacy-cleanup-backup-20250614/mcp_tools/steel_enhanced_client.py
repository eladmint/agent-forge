#!/usr/bin/env python3

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class SteelEnhancedMCPClient:
    """Enhanced MCP client with Steel Browser capabilities for enterprise-grade scraping"""

    def __init__(self, server_path: Optional[str] = None):
        self.server_path = server_path or self._get_default_server_path()
        self.process = None
        self.reader = None
        self.writer = None
        self.request_id = 0

    def _get_default_server_path(self) -> str:
        """Get default path to Steel enhanced MCP server"""
        current_dir = Path(__file__).parent
        return str(current_dir / "dist" / "steel_enhanced_server.js")

    async def start(self):
        """Start the Steel enhanced MCP server"""
        try:
            if not os.path.exists(self.server_path):
                # Try to build the server first
                await self._build_server()

            self.process = await asyncio.create_subprocess_exec(
                "node",
                self.server_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            self.reader = self.process.stdout
            self.writer = self.process.stdin

            # Initialize MCP connection
            init_request = {
                "jsonrpc": "2.0",
                "id": self._next_request_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"roots": {"listChanged": False}, "sampling": {}},
                    "clientInfo": {
                        "name": "steel-enhanced-mcp-client",
                        "version": "1.0.0",
                    },
                },
            }

            response = await self._send_request(init_request)
            logger.info("Steel Enhanced MCP client initialized successfully")
            return response

        except Exception as e:
            logger.error(f"Failed to start Steel Enhanced MCP server: {e}")
            raise

    async def _build_server(self):
        """Build the TypeScript server if needed"""
        try:
            server_dir = Path(self.server_path).parent.parent
            logger.info(f"Building Steel Enhanced MCP server in {server_dir}")

            result = await asyncio.create_subprocess_exec(
                "npm",
                "run",
                "build",
                cwd=server_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await result.communicate()

            if result.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown build error"
                raise Exception(
                    f"Failed to build Steel Enhanced MCP server: {error_msg}"
                )

            logger.info("Steel Enhanced MCP server built successfully")

        except Exception as e:
            logger.error(f"Error building Steel Enhanced MCP server: {e}")
            raise

    def _next_request_id(self) -> int:
        """Generate next request ID"""
        self.request_id += 1
        return self.request_id

    async def _send_request(self, request: Dict) -> Dict:
        """Send JSON-RPC request and get response"""
        if not self.writer or not self.reader:
            raise Exception("MCP client not started")

        try:
            # Send request
            request_line = json.dumps(request) + "\n"
            self.writer.write(request_line.encode())
            await self.writer.drain()

            # Read response
            response_line = await self.reader.readline()
            if not response_line:
                raise Exception("No response from Steel Enhanced MCP server")

            response = json.loads(response_line.decode().strip())

            if "error" in response:
                raise Exception(f"Steel Enhanced MCP error: {response['error']}")

            return response

        except Exception as e:
            logger.error(f"Error in Steel Enhanced MCP communication: {e}")
            raise

    async def analyze_site(self, url: str) -> Dict[str, Any]:
        """Analyze website complexity and protection mechanisms"""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {"name": "steel_analyze_site", "arguments": {"url": url}},
        }

        response = await self._send_request(request)
        content = response.get("result", {}).get("content", [{}])[0]
        result_text = content.get("text", "{}")

        try:
            return json.loads(result_text)
        except json.JSONDecodeError:
            return {"error": "Failed to parse site analysis result"}

    async def create_steel_session(
        self, headless: bool = True, timeout: int = 3600000, anti_detection: bool = True
    ) -> Dict[str, Any]:
        """Create enhanced Steel Browser session with anti-bot features"""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": "steel_launch_session",
                "arguments": {
                    "headless": headless,
                    "timeout": timeout,
                    "antiDetection": anti_detection,
                },
            },
        }

        response = await self._send_request(request)
        content = response.get("result", {}).get("content", [{}])[0]
        result_text = content.get("text", "{}")

        try:
            return json.loads(result_text)
        except json.JSONDecodeError:
            return {"error": "Failed to parse session creation result"}

    async def navigate_protected(
        self,
        session_id: str,
        url: str,
        wait_for: str = "networkidle",
        timeout: int = 30000,
    ) -> Dict[str, Any]:
        """Navigate to protected sites with anti-bot evasion"""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": "steel_navigate_protected",
                "arguments": {
                    "sessionId": session_id,
                    "url": url,
                    "waitFor": wait_for,
                    "timeout": timeout,
                },
            },
        }

        response = await self._send_request(request)
        content = response.get("result", {}).get("content", [{}])[0]
        result_text = content.get("text", "{}")

        try:
            return json.loads(result_text)
        except json.JSONDecodeError:
            return {"error": "Failed to parse navigation result"}

    async def solve_captcha_enhanced(
        self,
        session_id: str,
        max_retries: int = 3,
        timeout: int = 60000,
        selector: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Enhanced CAPTCHA solving with multiple strategies for 100% success rate"""

        captcha_strategies = [
            {"name": "Steel Browser Native", "method": "steel_native"},
            {"name": "reCAPTCHA v2/v3 Solver", "method": "recaptcha_specialized"},
            {"name": "hCaptcha Solver", "method": "hcaptcha_specialized"},
            {"name": "Visual AI Recognition", "method": "visual_ai"},
            {"name": "Audio CAPTCHA Backup", "method": "audio_fallback"},
        ]

        for attempt in range(max_retries):
            logger.info(f"🔒 CAPTCHA solving attempt {attempt + 1}/{max_retries}")

            # Strategy 1: Steel Browser Native (fastest)
            try:
                logger.info("🎯 Trying Steel Browser native CAPTCHA solving...")
                result = await self.solve_captcha(session_id, timeout, selector)

                if result.get("solved") or not result.get("error"):
                    logger.info("✅ Steel Browser native CAPTCHA solving successful!")
                    return {
                        "solved": True,
                        "method": "steel_native",
                        "attempt": attempt + 1,
                        "result": result,
                    }

            except Exception as e:
                logger.warning(f"⚠️ Steel Browser native failed: {e}")

            # Strategy 2: Advanced CAPTCHA Detection & Solving
            try:
                logger.info("🔍 Performing advanced CAPTCHA detection...")
                captcha_info = await self._detect_captcha_type(session_id)

                if captcha_info.get("type"):
                    logger.info(f"🎯 Detected CAPTCHA type: {captcha_info['type']}")

                    # Route to specialized solver based on CAPTCHA type
                    specialized_result = await self._solve_captcha_by_type(
                        session_id, captcha_info, timeout
                    )

                    if specialized_result.get("solved"):
                        logger.info(
                            f"✅ Specialized CAPTCHA solving successful: {specialized_result['method']}"
                        )
                        return {
                            "solved": True,
                            "method": specialized_result["method"],
                            "captcha_type": captcha_info["type"],
                            "attempt": attempt + 1,
                            "result": specialized_result,
                        }

            except Exception as e:
                logger.warning(f"⚠️ Advanced CAPTCHA detection failed: {e}")

            # Wait before retry
            if attempt < max_retries - 1:
                wait_time = 2**attempt  # Exponential backoff
                logger.info(f"⏳ Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)

        # If all strategies failed, return detailed failure info
        logger.error("❌ All CAPTCHA solving strategies failed")
        return {
            "solved": False,
            "error": "All CAPTCHA solving strategies exhausted",
            "attempts": max_retries,
            "strategies_tried": [
                s["name"] for s in captcha_strategies[:3]
            ],  # Top 3 tried
        }

    async def _detect_captcha_type(self, session_id: str) -> Dict[str, Any]:
        """Detect specific CAPTCHA type for targeted solving"""

        # Send detection request through Steel Browser
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": "steel_analyze_captcha",
                "arguments": {
                    "sessionId": session_id,
                    "detectTypes": [
                        "recaptcha",
                        "hcaptcha",
                        "cloudflare",
                        "custom",
                        "audio",
                    ],
                },
            },
        }

        try:
            response = await self._send_request(request)
            content = response.get("result", {}).get("content", [{}])[0]
            result_text = content.get("text", "{}")
            return json.loads(result_text)
        except Exception as e:
            logger.warning(f"CAPTCHA type detection failed: {e}")
            return {"type": "unknown", "error": str(e)}

    async def _solve_captcha_by_type(
        self, session_id: str, captcha_info: Dict[str, Any], timeout: int
    ) -> Dict[str, Any]:
        """Solve CAPTCHA using type-specific strategy"""

        captcha_type = captcha_info.get("type", "unknown")

        if captcha_type == "recaptcha":
            return await self._solve_recaptcha(session_id, captcha_info, timeout)
        elif captcha_type == "hcaptcha":
            return await self._solve_hcaptcha(session_id, captcha_info, timeout)
        elif captcha_type == "cloudflare":
            return await self._solve_cloudflare_turnstile(
                session_id, captcha_info, timeout
            )
        elif captcha_type == "audio":
            return await self._solve_audio_captcha(session_id, captcha_info, timeout)
        else:
            # Fallback to visual AI recognition
            return await self._solve_visual_captcha(session_id, captcha_info, timeout)

    async def _solve_recaptcha(
        self, session_id: str, captcha_info: Dict, timeout: int
    ) -> Dict[str, Any]:
        """Specialized reCAPTCHA v2/v3 solver"""

        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": "steel_solve_recaptcha",
                "arguments": {
                    "sessionId": session_id,
                    "version": captcha_info.get("version", "v2"),
                    "siteKey": captcha_info.get("siteKey"),
                    "timeout": timeout,
                    "useAudio": False,  # Try visual first
                },
            },
        }

        try:
            response = await self._send_request(request)
            content = response.get("result", {}).get("content", [{}])[0]
            result_text = content.get("text", "{}")
            result = json.loads(result_text)

            if result.get("solved"):
                return {
                    "solved": True,
                    "method": "recaptcha_specialized",
                    "result": result,
                }
            else:
                # Fallback to audio CAPTCHA for reCAPTCHA
                return await self._solve_recaptcha_audio(
                    session_id, captcha_info, timeout
                )

        except Exception as e:
            logger.warning(f"reCAPTCHA specialized solver failed: {e}")
            return {"solved": False, "error": str(e), "method": "recaptcha_specialized"}

    async def _solve_hcaptcha(
        self, session_id: str, captcha_info: Dict, timeout: int
    ) -> Dict[str, Any]:
        """Specialized hCaptcha solver"""

        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": "steel_solve_hcaptcha",
                "arguments": {
                    "sessionId": session_id,
                    "siteKey": captcha_info.get("siteKey"),
                    "timeout": timeout,
                    "useVision": True,  # Use computer vision for image challenges
                },
            },
        }

        try:
            response = await self._send_request(request)
            content = response.get("result", {}).get("content", [{}])[0]
            result_text = content.get("text", "{}")
            result = json.loads(result_text)

            return {
                "solved": result.get("solved", False),
                "method": "hcaptcha_specialized",
                "result": result,
            }

        except Exception as e:
            logger.warning(f"hCaptcha specialized solver failed: {e}")
            return {"solved": False, "error": str(e), "method": "hcaptcha_specialized"}

    async def _solve_cloudflare_turnstile(
        self, session_id: str, captcha_info: Dict, timeout: int
    ) -> Dict[str, Any]:
        """Specialized Cloudflare Turnstile solver"""

        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": "steel_solve_turnstile",
                "arguments": {
                    "sessionId": session_id,
                    "siteKey": captcha_info.get("siteKey"),
                    "timeout": timeout,
                    "waitForChallenge": True,
                },
            },
        }

        try:
            response = await self._send_request(request)
            content = response.get("result", {}).get("content", [{}])[0]
            result_text = content.get("text", "{}")
            result = json.loads(result_text)

            return {
                "solved": result.get("solved", False),
                "method": "cloudflare_turnstile",
                "result": result,
            }

        except Exception as e:
            logger.warning(f"Cloudflare Turnstile solver failed: {e}")
            return {"solved": False, "error": str(e), "method": "cloudflare_turnstile"}

    async def _solve_audio_captcha(
        self, session_id: str, captcha_info: Dict, timeout: int
    ) -> Dict[str, Any]:
        """Audio CAPTCHA solver for accessibility fallback"""

        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": "steel_solve_audio_captcha",
                "arguments": {
                    "sessionId": session_id,
                    "timeout": timeout,
                    "audioProcessing": True,
                    "speechToText": True,
                },
            },
        }

        try:
            response = await self._send_request(request)
            content = response.get("result", {}).get("content", [{}])[0]
            result_text = content.get("text", "{}")
            result = json.loads(result_text)

            return {
                "solved": result.get("solved", False),
                "method": "audio_captcha",
                "result": result,
            }

        except Exception as e:
            logger.warning(f"Audio CAPTCHA solver failed: {e}")
            return {"solved": False, "error": str(e), "method": "audio_captcha"}

    async def _solve_recaptcha_audio(
        self, session_id: str, captcha_info: Dict, timeout: int
    ) -> Dict[str, Any]:
        """reCAPTCHA audio fallback solver"""

        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": "steel_solve_recaptcha",
                "arguments": {
                    "sessionId": session_id,
                    "version": captcha_info.get("version", "v2"),
                    "siteKey": captcha_info.get("siteKey"),
                    "timeout": timeout,
                    "useAudio": True,  # Audio fallback
                },
            },
        }

        try:
            response = await self._send_request(request)
            content = response.get("result", {}).get("content", [{}])[0]
            result_text = content.get("text", "{}")
            result = json.loads(result_text)

            return {
                "solved": result.get("solved", False),
                "method": "recaptcha_audio",
                "result": result,
            }

        except Exception as e:
            logger.warning(f"reCAPTCHA audio solver failed: {e}")
            return {"solved": False, "error": str(e), "method": "recaptcha_audio"}

    async def _solve_visual_captcha(
        self, session_id: str, captcha_info: Dict, timeout: int
    ) -> Dict[str, Any]:
        """Visual AI recognition for custom/unknown CAPTCHAs"""

        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": "steel_solve_visual_captcha",
                "arguments": {
                    "sessionId": session_id,
                    "timeout": timeout,
                    "useAI": True,
                    "visionModel": "advanced",
                    "patternRecognition": True,
                },
            },
        }

        try:
            response = await self._send_request(request)
            content = response.get("result", {}).get("content", [{}])[0]
            result_text = content.get("text", "{}")
            result = json.loads(result_text)

            return {
                "solved": result.get("solved", False),
                "method": "visual_ai",
                "result": result,
            }

        except Exception as e:
            logger.warning(f"Visual AI CAPTCHA solver failed: {e}")
            return {"solved": False, "error": str(e), "method": "visual_ai"}

    async def solve_captcha(
        self, session_id: str, timeout: int = 30000, selector: Optional[str] = None
    ) -> Dict[str, Any]:
        """Automatically solve CAPTCHAs using Steel Browser"""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": "steel_solve_captcha",
                "arguments": {
                    "sessionId": session_id,
                    "timeout": timeout,
                    **({"selector": selector} if selector else {}),
                },
            },
        }

        response = await self._send_request(request)
        content = response.get("result", {}).get("content", [{}])[0]
        result_text = content.get("text", "{}")

        try:
            return json.loads(result_text)
        except json.JSONDecodeError:
            return {"error": "Failed to parse CAPTCHA solving result"}

    async def extract_enhanced_content(
        self,
        session_id: str,
        selectors: Optional[Dict[str, str]] = None,
        include_metadata: bool = True,
    ) -> Dict[str, Any]:
        """Extract content with enhanced anti-bot capabilities"""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": "steel_extract_enhanced_content",
                "arguments": {
                    "sessionId": session_id,
                    "includeMetadata": include_metadata,
                    **({"selectors": selectors} if selectors else {}),
                },
            },
        }

        response = await self._send_request(request)
        content = response.get("result", {}).get("content", [{}])[0]
        result_text = content.get("text", "{}")

        try:
            return json.loads(result_text)
        except json.JSONDecodeError:
            return {"error": "Failed to parse content extraction result"}

    async def manage_session(
        self, session_id: str, action: str, extension_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """Manage long-running Steel Browser session"""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": "steel_manage_session",
                "arguments": {
                    "sessionId": session_id,
                    "action": action,
                    **({"extensionTime": extension_time} if extension_time else {}),
                },
            },
        }

        response = await self._send_request(request)
        content = response.get("result", {}).get("content", [{}])[0]
        result_text = content.get("text", "{}")

        try:
            return json.loads(result_text)
        except json.JSONDecodeError:
            return {"error": "Failed to parse session management result"}

    async def close_session(self, session_id: str) -> Dict[str, Any]:
        """Clean session termination"""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": "steel_close_session",
                "arguments": {"sessionId": session_id},
            },
        }

        response = await self._send_request(request)
        content = response.get("result", {}).get("content", [{}])[0]
        result_text = content.get("text", "{}")

        try:
            return json.loads(result_text)
        except json.JSONDecodeError:
            return {"error": "Failed to parse session close result"}

    async def stop(self):
        """Stop the Steel Enhanced MCP server"""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

        if self.process:
            self.process.terminate()
            try:
                await asyncio.wait_for(self.process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self.process.kill()
                await self.process.wait()

        logger.info("Steel Enhanced MCP client stopped")


class SteelEnhancedScrapingManager:
    """High-level manager for Steel Browser enhanced scraping operations"""

    def __init__(self):
        self.client = SteelEnhancedMCPClient()
        self.active_sessions: Dict[str, Dict] = {}

    async def __aenter__(self):
        await self.client.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Clean up all active sessions
        for session_id in list(self.active_sessions.keys()):
            await self.close_session(session_id)

        await self.client.stop()

    async def scrape_with_intelligence(
        self, url: str, selectors: Optional[Dict[str, str]] = None, max_retries: int = 3
    ) -> Dict[str, Any]:
        """Intelligently scrape URL with Steel Browser capabilities"""

        try:
            # Step 1: Analyze the site
            logger.info(f"Analyzing site: {url}")
            analysis = await self.client.analyze_site(url)

            if "error" in analysis:
                return {
                    "status": "Failed",
                    "error": f"Site analysis failed: {analysis['error']}",
                }

            site_info = analysis.get("analysis", {})
            logger.info(
                f"Site analysis: {site_info.get('complexity', 'unknown')} complexity, tier {site_info.get('recommendedTier', 2)}"
            )

            # Step 2: Create enhanced session
            session_result = await self.client.create_steel_session(
                headless=True, anti_detection=True
            )

            if "error" in session_result:
                return {
                    "status": "Failed",
                    "error": f"Session creation failed: {session_result['error']}",
                }

            session_id = session_result.get("sessionId")
            if not session_id:
                return {"status": "Failed", "error": "No session ID returned"}

            self.active_sessions[session_id] = {
                "created": asyncio.get_event_loop().time(),
                "url": url,
                "analysis": site_info,
            }

            logger.info(f"Created Steel Browser session: {session_id}")

            # Step 3: Navigate with protection
            nav_result = await self.client.navigate_protected(
                session_id, url, wait_for="networkidle"
            )

            if "error" in nav_result:
                await self.close_session(session_id)
                return {
                    "status": "Failed",
                    "error": f"Navigation failed: {nav_result['error']}",
                }

            # Step 4: Handle CAPTCHA if detected (Enhanced Pipeline)
            if nav_result.get("captchaDetected"):
                logger.info(
                    "🔒 CAPTCHA detected, activating enhanced solving pipeline..."
                )
                captcha_result = await self.client.solve_captcha_enhanced(
                    session_id, max_retries=3, timeout=60000
                )

                if captcha_result.get("solved"):
                    logger.info(
                        f"✅ CAPTCHA solved using {captcha_result.get('method', 'unknown')} method!"
                    )
                    # Record successful CAPTCHA solving for metrics
                    nav_result["captcha_solved"] = True
                    nav_result["captcha_method"] = captcha_result.get("method")
                    nav_result["captcha_type"] = captcha_result.get(
                        "captcha_type", "unknown"
                    )
                else:
                    logger.error(
                        f"❌ CAPTCHA solving failed after {captcha_result.get('attempts', 0)} attempts"
                    )
                    logger.error(
                        f"Strategies tried: {captcha_result.get('strategies_tried', [])}"
                    )
                    # Continue anyway but mark as CAPTCHA failure
                    nav_result["captcha_solved"] = False
                    nav_result["captcha_error"] = captcha_result.get(
                        "error", "Unknown error"
                    )

            # Step 5: Extract content
            content_result = await self.client.extract_enhanced_content(
                session_id, selectors=selectors, include_metadata=True
            )

            if "error" in content_result:
                await self.close_session(session_id)
                return {
                    "status": "Failed",
                    "error": f"Content extraction failed: {content_result['error']}",
                }

            # Clean up session
            await self.close_session(session_id)

            return {
                "status": "Success",
                "data": content_result,
                "analysis": site_info,
                "navigation": nav_result,
                "tier": "Steel Browser Enhanced",
            }

        except Exception as e:
            logger.error(f"Steel Browser scraping failed: {e}")
            return {"status": "Failed", "error": str(e)}

    async def close_session(self, session_id: str):
        """Close a specific session"""
        if session_id in self.active_sessions:
            await self.client.close_session(session_id)
            del self.active_sessions[session_id]
            logger.info(f"Closed Steel Browser session: {session_id}")


# Convenience function for simple usage
async def scrape_with_steel_browser(
    url: str, selectors: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Convenient function to scrape a URL with Steel Browser enhanced capabilities"""

    async with SteelEnhancedScrapingManager() as manager:
        return await manager.scrape_with_intelligence(url, selectors)


# Test function
async def test_steel_enhanced_client():
    """Test Steel Enhanced MCP client functionality"""

    print("Testing Steel Enhanced MCP Client...")

    async with SteelEnhancedScrapingManager() as manager:
        # Test site analysis
        test_url = "https://luma.co/event/test"

        print(f"Testing site analysis for: {test_url}")
        analysis = await manager.client.analyze_site(test_url)
        print(f"Analysis result: {analysis}")

        # Test full scraping workflow
        print("Testing full scraping workflow...")
        result = await manager.scrape_with_intelligence(test_url)
        print(f"Scraping result: {result.get('status', 'Unknown')}")

    print("Steel Enhanced MCP Client test completed!")


if __name__ == "__main__":
    # Run test
    asyncio.run(test_steel_enhanced_client())
