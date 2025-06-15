#!/usr/bin/env python3
"""
Analyze Agent Forge Website Dark Mode Implementation
Uses PageScraperAgent to capture screenshot and analyze the dark mode styling
"""

import asyncio
import sys
import os
from datetime import datetime
import re

# Add the parent directory to Python path to import agent forge modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# For now, let's create a simpler screenshot agent without the complex dependencies
from playwright.async_api import async_playwright
import logging

class WebsiteDarkModeAnalyzer:
    """Simple agent that captures screenshots and analyzes dark mode"""
    
    def __init__(self, name="WebsiteDarkModeAnalyzer"):
        self.name = name
        self.logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(level=logging.INFO)
    
    async def analyze_dark_mode(self, url: str) -> dict:
        """
        Navigate to website, capture screenshot, and analyze dark mode implementation
        
        Args:
            url: The URL to analyze
            
        Returns:
            Dictionary with screenshot path and dark mode analysis
        """
        self.logger.info(f"[{self.name}] Starting dark mode analysis for: {url}")
        
        async with async_playwright() as p:
            browser = None
            try:
                # Launch browser
                browser = await p.chromium.launch(headless=False)  # Use headful mode to see what's happening
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    device_scale_factor=1
                )
                page = await context.new_page()
                
                # Navigate to the page
                self.logger.info(f"[{self.name}] Navigating to {url}...")
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Wait a bit for any animations to complete
                await asyncio.sleep(2)
                
                # Take screenshot
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshots_dir = os.path.join("results", "screenshots")
                os.makedirs(screenshots_dir, exist_ok=True)
                
                screenshot_filename = f"agent_forge_website_{timestamp}.png"
                screenshot_path = os.path.join(screenshots_dir, screenshot_filename)
                
                await page.screenshot(path=screenshot_path, full_page=True)
                self.logger.info(f"[{self.name}] Screenshot saved to {screenshot_path}")
                
                # Extract page content and styles for analysis
                analysis_results = await page.evaluate('''() => {
                    const body = document.body;
                    const computedStyles = window.getComputedStyle(body);
                    
                    // Get main content elements
                    const mainHeading = document.querySelector('h1');
                    const mainHeadingText = mainHeading ? mainHeading.textContent : 'No H1 found';
                    const mainHeadingColor = mainHeading ? window.getComputedStyle(mainHeading).color : 'N/A';
                    
                    const paragraphs = document.querySelectorAll('p');
                    const firstParagraphText = paragraphs[0] ? paragraphs[0].textContent : 'No paragraphs found';
                    const firstParagraphColor = paragraphs[0] ? window.getComputedStyle(paragraphs[0]).color : 'N/A';
                    
                    // Get buttons
                    const buttons = document.querySelectorAll('button, .button, [role="button"], a[class*="button"]');
                    const buttonInfo = Array.from(buttons).slice(0, 3).map(btn => ({
                        text: btn.textContent.trim(),
                        backgroundColor: window.getComputedStyle(btn).backgroundColor,
                        color: window.getComputedStyle(btn).color,
                        borderColor: window.getComputedStyle(btn).borderColor
                    }));
                    
                    // Check for dark mode indicators
                    const htmlClasses = document.documentElement.classList.toString();
                    const bodyClasses = body.classList.toString();
                    
                    return {
                        backgroundColor: computedStyles.backgroundColor,
                        color: computedStyles.color,
                        mainHeading: {
                            text: mainHeadingText,
                            color: mainHeadingColor
                        },
                        firstParagraph: {
                            text: firstParagraphText.substring(0, 100) + '...',
                            color: firstParagraphColor
                        },
                        buttons: buttonInfo,
                        darkModeClasses: {
                            html: htmlClasses,
                            body: bodyClasses
                        },
                        isDarkMode: computedStyles.backgroundColor.includes('rgb(0') || 
                                   computedStyles.backgroundColor.includes('#0') ||
                                   computedStyles.backgroundColor.includes('rgba(0') ||
                                   htmlClasses.includes('dark') ||
                                   bodyClasses.includes('dark')
                    };
                }''')
                
                # Analyze the colors to determine if dark mode is working
                def is_dark_color(color_string):
                    """Check if a color is dark based on RGB values"""
                    if not color_string:
                        return False
                    
                    # Extract RGB values
                    rgb_match = re.search(r'rgb[a]?\((\d+),\s*(\d+),\s*(\d+)', color_string)
                    if rgb_match:
                        r, g, b = map(int, rgb_match.groups())
                        # Calculate luminance
                        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
                        return luminance < 0.5
                    
                    # Check hex colors
                    if color_string.startswith('#'):
                        hex_color = color_string.lstrip('#')
                        if len(hex_color) == 6:
                            r = int(hex_color[0:2], 16)
                            g = int(hex_color[2:4], 16)
                            b = int(hex_color[4:6], 16)
                            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
                            return luminance < 0.5
                    
                    return False
                
                def is_light_color(color_string):
                    """Check if a color is light based on RGB values"""
                    return not is_dark_color(color_string) if color_string else False
                
                # Comprehensive dark mode analysis
                bg_is_dark = is_dark_color(analysis_results['backgroundColor'])
                text_is_light = is_light_color(analysis_results['color'])
                
                dark_mode_status = "Not Implemented"
                if bg_is_dark and text_is_light:
                    dark_mode_status = "Properly Implemented"
                elif bg_is_dark and not text_is_light:
                    dark_mode_status = "Partially Implemented (text color issue)"
                elif not bg_is_dark and analysis_results['isDarkMode']:
                    dark_mode_status = "CSS Classes Present but Not Applied"
                
                result = {
                    'success': True,
                    'url': url,
                    'screenshot_path': os.path.abspath(screenshot_path),
                    'dark_mode_analysis': {
                        'status': dark_mode_status,
                        'background_color': analysis_results['backgroundColor'],
                        'background_is_dark': bg_is_dark,
                        'text_color': analysis_results['color'],
                        'text_is_light': text_is_light,
                        'dark_mode_classes_found': analysis_results['isDarkMode'],
                        'css_classes': analysis_results['darkModeClasses']
                    },
                    'content_analysis': {
                        'main_heading': analysis_results['mainHeading'],
                        'first_paragraph': analysis_results['firstParagraph'],
                        'buttons': analysis_results['buttons']
                    },
                    'visual_quality': {
                        'contrast_adequate': bg_is_dark and text_is_light,
                        'readability': 'Good' if (bg_is_dark and text_is_light) else 'Poor',
                        'overall_implementation': dark_mode_status
                    }
                }
                
                return result
                
            except Exception as e:
                self.logger.error(f"[{self.name}] Error during analysis: {e}", exc_info=True)
                return {
                    'success': False,
                    'error': str(e),
                    'url': url
                }
            finally:
                if browser:
                    await browser.close()

async def main():
    """Main function to run the dark mode analysis"""
    url = "https://storage.googleapis.com/tokenhunter-457310-agent-forge-website/index.html"
    
    print("🔍 Agent Forge Website Dark Mode Analysis")
    print("=" * 60)
    print(f"📸 Analyzing: {url}")
    print()
    
    # Create analyzer
    analyzer = WebsiteDarkModeAnalyzer(name="DarkModeAnalyzer")
    
    # Run analysis
    result = await analyzer.analyze_dark_mode(url)
    
    if result['success']:
        print("✅ Analysis Complete!")
        print()
        print(f"📸 Screenshot saved to: {result['screenshot_path']}")
        print()
        
        # Dark Mode Analysis
        dark_analysis = result['dark_mode_analysis']
        print("🌙 Dark Mode Analysis:")
        print(f"   Status: {dark_analysis['status']}")
        print(f"   Background Color: {dark_analysis['background_color']}")
        print(f"   Background is Dark: {'✅ Yes' if dark_analysis['background_is_dark'] else '❌ No'}")
        print(f"   Text Color: {dark_analysis['text_color']}")
        print(f"   Text is Light: {'✅ Yes' if dark_analysis['text_is_light'] else '❌ No'}")
        print(f"   Dark Mode Classes Found: {'✅ Yes' if dark_analysis['dark_mode_classes_found'] else '❌ No'}")
        
        if dark_analysis['css_classes']['html'] or dark_analysis['css_classes']['body']:
            print(f"   HTML Classes: {dark_analysis['css_classes']['html'] or 'None'}")
            print(f"   Body Classes: {dark_analysis['css_classes']['body'] or 'None'}")
        print()
        
        # Content Analysis
        content = result['content_analysis']
        print("📄 Content Analysis:")
        print(f"   Main Heading: {content['main_heading']['text']}")
        print(f"   Heading Color: {content['main_heading']['color']}")
        print(f"   First Paragraph: {content['first_paragraph']['text']}")
        print(f"   Paragraph Color: {content['first_paragraph']['color']}")
        print()
        
        # Button Analysis
        if content['buttons']:
            print("🔘 Button Analysis:")
            for i, btn in enumerate(content['buttons'], 1):
                print(f"   Button {i}: {btn['text']}")
                print(f"      Background: {btn['backgroundColor']}")
                print(f"      Text Color: {btn['color']}")
                print(f"      Border: {btn['borderColor']}")
            print()
        
        # Visual Quality Summary
        quality = result['visual_quality']
        print("⭐ Visual Quality Summary:")
        print(f"   Contrast Adequate: {'✅ Yes' if quality['contrast_adequate'] else '❌ No'}")
        print(f"   Readability: {quality['readability']}")
        print(f"   Overall Implementation: {quality['overall_implementation']}")
        print()
        
        # Recommendations
        print("💡 Recommendations:")
        if dark_analysis['status'] == "Properly Implemented":
            print("   ✅ Dark mode is properly implemented! No changes needed.")
        elif dark_analysis['status'] == "Not Implemented":
            print("   ❌ Dark mode is not implemented. Consider:")
            print("      - Adding dark background color (e.g., #0a0a0a or rgb(10, 10, 10))")
            print("      - Using light text color (e.g., #ffffff or rgb(255, 255, 255))")
            print("      - Adding 'dark' class to HTML or body element")
            print("      - Using CSS variables for theme switching")
        elif "Partially" in dark_analysis['status']:
            print("   ⚠️  Dark mode is partially implemented. Fix:")
            print("      - Ensure text colors are light for good contrast")
            print("      - Check all UI elements have appropriate dark theme colors")
        elif "CSS Classes Present" in dark_analysis['status']:
            print("   ⚠️  Dark mode classes found but not applied. Check:")
            print("      - CSS file is properly loaded")
            print("      - Dark mode styles are correctly defined")
            print("      - No CSS specificity conflicts")
            
    else:
        print("❌ Analysis failed!")
        print(f"Error: {result['error']}")
    
    return result

if __name__ == "__main__":
    # Run the analysis
    result = asyncio.run(main())
    
    # Open screenshot if successful
    if result.get('success') and result.get('screenshot_path'):
        import platform
        screenshot_path = result['screenshot_path']
        
        if platform.system() == 'Darwin':  # macOS
            os.system(f'open "{screenshot_path}"')
        elif platform.system() == 'Windows':
            os.system(f'start "" "{screenshot_path}"')
        else:  # Linux
            os.system(f'xdg-open "{screenshot_path}"')