#!/usr/bin/env python3
"""
Test script for validating Telegram bot conversational format using MCP browser control.

This script will:
1. Navigate to web.telegram.org
2. Open a chat with @jjumbybot
3. Send a test query about Cardano events at Token2049
4. Take a screenshot of the response
5. Analyze the response format to verify the new conversational style
"""

import asyncio
import json
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, Optional


class TelegramBotTester:
    """Test client for validating Telegram bot conversational format."""

    def __init__(self, mcp_server_path: str):
        """Initialize the Telegram bot tester.

        Args:
            mcp_server_path: Path to the MCP server executable
        """
        self.mcp_server_path = mcp_server_path
        self.process: Optional[subprocess.Popen] = None
        self.request_id = 0
        self.screenshots_dir = Path("telegram_test_screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)

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
                    "clientInfo": {"name": "telegram-bot-tester", "version": "1.0.0"},
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

    async def test_telegram_bot_interface(self) -> Dict[str, Any]:
        """Test the Telegram bot interface and validate conversational format."""

        results = {
            "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_url": "https://web.telegram.org",
            "bot_username": "@jjumbybot",
            "test_query": "what events did Cardano have in token2049?",
            "success": False,
            "screenshots": [],
            "response_analysis": {},
            "errors": [],
        }

        try:
            print("🚀 Starting Telegram bot interface test...")

            # Step 1: Launch browser (non-headless for manual interaction if needed)
            print("🌐 Launching browser...")
            await self.call_tool(
                "launch_browser",
                {
                    "headless": False,  # Set to False so we can see what's happening
                    "debug": True,
                },
            )

            # Step 2: Navigate to web.telegram.org
            print("📱 Navigating to web.telegram.org...")
            nav_result = await self.call_tool(
                "navigate_to_url",
                {
                    "url": "https://web.telegram.org",
                    "waitFor": "domcontentloaded",
                    "timeout": 30000,
                },
            )

            nav_data = json.loads(nav_result["content"][0]["text"])
            results["navigation"] = nav_data

            if not nav_data.get("success"):
                raise RuntimeError("Failed to navigate to web.telegram.org")

            # Step 3: Take initial screenshot
            print("📸 Taking initial screenshot...")
            timestamp = int(time.time())
            initial_screenshot = f"telegram_initial_{timestamp}.png"
            screenshot_path = str(self.screenshots_dir / initial_screenshot)

            await self.call_tool(
                "take_screenshot", {"fullPage": True, "path": screenshot_path}
            )
            results["screenshots"].append({"stage": "initial", "path": screenshot_path})

            # Step 4: Wait for page to fully load and login prompt
            print("⏳ Waiting for Telegram to load...")
            await asyncio.sleep(5)  # Give time for Telegram to fully load

            # Step 5: Take screenshot after load
            print("📸 Taking post-load screenshot...")
            post_load_screenshot = f"telegram_loaded_{timestamp}.png"
            screenshot_path = str(self.screenshots_dir / post_load_screenshot)

            await self.call_tool(
                "take_screenshot", {"fullPage": True, "path": screenshot_path}
            )
            results["screenshots"].append({"stage": "loaded", "path": screenshot_path})

            # Step 6: Extract page content to analyze current state
            print("🔍 Analyzing page content...")
            content_result = await self.call_tool(
                "extract_content", {"extractType": "text"}
            )
            content_data = json.loads(content_result["content"][0]["text"])
            page_text = content_data.get("content", "")

            # Check if we need to log in
            if "Log in" in page_text or "Phone Number" in page_text:
                print(
                    "⚠️  Web Telegram requires login. This test requires manual intervention."
                )
                print("📋 Manual steps needed:")
                print("1. Log in to Telegram Web in the opened browser")
                print("2. Search for '@jjumbybot' in the search bar")
                print("3. Open the chat with the bot")
                print(
                    "4. Send the test query: 'what events did Cardano have in token2049?'"
                )
                print("5. Wait for the bot response")
                print("6. Press Enter here to continue with screenshot capture...")

                # Wait for manual intervention
                input("Press Enter after completing the manual steps...")

                # Take screenshot of the final result
                print("📸 Taking final screenshot after manual interaction...")
                final_screenshot = f"telegram_bot_response_{timestamp}.png"
                screenshot_path = str(self.screenshots_dir / final_screenshot)

                await self.call_tool(
                    "take_screenshot", {"fullPage": True, "path": screenshot_path}
                )
                results["screenshots"].append(
                    {"stage": "bot_response", "path": screenshot_path}
                )

                # Extract the conversation content
                print("📄 Extracting conversation content...")
                final_content = await self.call_tool(
                    "extract_content", {"extractType": "text"}
                )
                final_data = json.loads(final_content["content"][0]["text"])
                conversation_text = final_data.get("content", "")

                # Analyze the response format
                analysis = self._analyze_response_format(conversation_text)
                results["response_analysis"] = analysis
                results["conversation_text"] = conversation_text

                results["success"] = True
                print("✅ Test completed successfully!")

            else:
                print("❌ Unable to proceed without login")
                results["errors"].append("Telegram Web requires authentication")

        except Exception as e:
            print(f"❌ Test failed: {e}")
            results["errors"].append(str(e))

            # Take error screenshot
            try:
                error_screenshot = f"telegram_error_{int(time.time())}.png"
                screenshot_path = str(self.screenshots_dir / error_screenshot)
                await self.call_tool(
                    "take_screenshot", {"fullPage": True, "path": screenshot_path}
                )
                results["screenshots"].append(
                    {"stage": "error", "path": screenshot_path}
                )
            except:
                pass

        finally:
            # Close browser
            try:
                await self.call_tool("close_browser", {})
            except Exception as e:
                print(f"⚠️ Warning: Failed to close browser: {e}")

        return results

    def _analyze_response_format(self, conversation_text: str) -> Dict[str, Any]:
        """Analyze the bot response to determine if it uses the new conversational format."""

        analysis = {
            "format_detected": "unknown",
            "has_conversational_intro": False,
            "has_progressive_disclosure": False,
            "button_count": 0,
            "event_count": 0,
            "format_indicators": [],
        }

        # Check for new conversational format indicators
        conversational_phrases = [
            "Here are some events I've found:",
            "Here are the events",
            "I found these events",
            "Found these Cardano events",
        ]

        for phrase in conversational_phrases:
            if phrase.lower() in conversation_text.lower():
                analysis["has_conversational_intro"] = True
                analysis["format_indicators"].append(
                    f"Found conversational intro: '{phrase}'"
                )
                break

        # Check for old progressive disclosure format
        progressive_phrases = ["🔍 Found", "Found X Events", "Events Found"]

        for phrase in progressive_phrases:
            if phrase in conversation_text:
                analysis["has_progressive_disclosure"] = True
                analysis["format_indicators"].append(
                    f"Found progressive disclosure: '{phrase}'"
                )
                break

        # Count event indicators
        event_indicators = ["⏰", "📍", "🔗", "Event Details"]
        for indicator in event_indicators:
            count = conversation_text.count(indicator)
            if count > 0:
                analysis["event_count"] = max(analysis["event_count"], count)
                analysis["format_indicators"].append(
                    f"Found {count} '{indicator}' indicators"
                )

        # Determine format
        if (
            analysis["has_conversational_intro"]
            and not analysis["has_progressive_disclosure"]
        ):
            analysis["format_detected"] = "new_conversational"
        elif (
            analysis["has_progressive_disclosure"]
            and not analysis["has_conversational_intro"]
        ):
            analysis["format_detected"] = "old_progressive_disclosure"
        elif (
            analysis["has_conversational_intro"]
            and analysis["has_progressive_disclosure"]
        ):
            analysis["format_detected"] = "mixed"
        else:
            analysis["format_detected"] = "unrecognized"

        # Check for button indicators (this is approximate)
        button_indicators = ["Show More", "More Details", "View Event", "See More"]
        for indicator in button_indicators:
            if indicator in conversation_text:
                analysis["button_count"] += conversation_text.count(indicator)

        return analysis

    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a detailed test report."""

        report = f"""
# Telegram Bot Interface Test Report

**Test Timestamp:** {results['test_timestamp']}
**Bot Username:** {results['bot_username']}
**Test Query:** "{results['test_query']}"
**Test Success:** {'✅ PASSED' if results['success'] else '❌ FAILED'}

## Test Results

### Navigation
- **Target URL:** {results['test_url']}
- **Navigation Success:** {'✅' if results.get('navigation', {}).get('success') else '❌'}

### Screenshots Captured
"""

        for screenshot in results["screenshots"]:
            report += f"- **{screenshot['stage'].title()}:** `{screenshot['path']}`\n"

        if results["success"] and "response_analysis" in results:
            analysis = results["response_analysis"]
            report += f"""
### Response Format Analysis

**Format Detected:** {analysis['format_detected'].upper()}

**Format Characteristics:**
- **Conversational Intro:** {'✅ YES' if analysis['has_conversational_intro'] else '❌ NO'}
- **Progressive Disclosure:** {'✅ YES' if analysis['has_progressive_disclosure'] else '❌ NO'}
- **Event Count:** {analysis['event_count']}
- **Button Count:** {analysis['button_count']}

**Format Indicators Found:**
"""
            for indicator in analysis["format_indicators"]:
                report += f"- {indicator}\n"

            # Determine if format meets expectations
            expected_format = analysis["format_detected"] == "new_conversational"
            max_buttons = analysis["button_count"] <= 2

            report += f"""
### Format Validation

**Expected Conversational Format:** {'✅ CONFIRMED' if expected_format else '❌ NOT CONFIRMED'}
**Maximum 2 Buttons:** {'✅ CONFIRMED' if max_buttons else f'❌ FAILED - Found {analysis["button_count"]} buttons'}

### Overall Assessment

"""
            if expected_format and max_buttons:
                report += "✅ **SUCCESS:** Bot is using the new conversational format with appropriate button limits."
            elif expected_format and not max_buttons:
                report += "⚠️  **PARTIAL SUCCESS:** Bot uses conversational format but has too many buttons."
            elif not expected_format and max_buttons:
                report += "⚠️  **PARTIAL SUCCESS:** Bot has appropriate button count but not using conversational format."
            else:
                report += "❌ **FAILURE:** Bot is not using the expected conversational format."

        if results.get("errors"):
            report += "\n### Errors Encountered\n"
            for error in results["errors"]:
                report += f"- {error}\n"

        report += """
## Manual Verification Required

Due to Telegram Web authentication requirements, this test involved manual interaction. 
Please verify the following in the screenshots:

1. **Conversational Introduction:** Look for "Here are some events I've found:" instead of "🔍 Found X Events"
2. **Event Format:** Each event should show:
   - **Event Name** (bold)
   - ⏰ [Date and time]
   - 📍 [Location]
   - [One sentence description]
   - 🔗 [Event Details](link)
3. **Button Count:** Should show maximum 2 buttons, not multiple progressive disclosure buttons
4. **Closing Statement:** Should end with "Would you like to see more details about any of these events?"

## Next Steps

If the test shows the old format:
1. Check the bot's response generation logic in `/Users/eladm/Projects/token/tokenhunter/chatbot_telegram/bot.py`
2. Verify the conversation format is properly implemented
3. Test again after any fixes

Generated by TokenHunter Telegram Bot Interface Tester
"""

        return report


async def main():
    """Main test function."""
    print("🧪 TokenHunter Telegram Bot Interface Tester")
    print("=" * 50)

    # Initialize tester
    mcp_server_path = "dist/index.js"
    tester = TelegramBotTester(mcp_server_path)

    try:
        # Start the MCP server
        print("🔧 Starting MCP server...")
        await tester.start_server()

        # Run the test
        results = await tester.test_telegram_bot_interface()

        # Generate and display report
        report = tester.generate_report(results)
        print("\n" + "=" * 50)
        print("📊 TEST REPORT")
        print("=" * 50)
        print(report)

        # Save report to file
        report_file = Path("telegram_bot_test_report.md")
        with open(report_file, "w") as f:
            f.write(report)

        print(f"\n📄 Full report saved to: {report_file}")
        print(f"📸 Screenshots saved to: {tester.screenshots_dir}")

    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Stop the MCP server
        print("🛑 Stopping MCP server...")
        await tester.stop_server()


if __name__ == "__main__":
    asyncio.run(main())
