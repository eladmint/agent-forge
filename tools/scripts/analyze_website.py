#!/usr/bin/env python3
"""
Website Analysis Agent
Uses direct HTTP access to analyze the Agent Forge website
"""

import asyncio
import aiohttp
import sys
import re
from datetime import datetime
from typing import Dict, Any

class WebsiteAnalysisAgent:
    """Agent to analyze the Agent Forge website content"""
    
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def analyze_website(self, url: str = "http://localhost:3001") -> Dict[str, Any]:
        """
        Analyze the website content and structure
        
        Args:
            url: The URL to analyze
            
        Returns:
            Dictionary with analysis results
        """
        try:
            print(f"🔍 Analyzing website: {url}")
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    return {
                        'success': False,
                        'error': f'HTTP {response.status}: {response.reason}',
                        'url': url
                    }
                
                content = await response.text()
                
                # Perform content analysis
                analysis = self._analyze_content(content, url)
                analysis['success'] = True
                analysis['url'] = url
                analysis['timestamp'] = datetime.now().isoformat()
                
                return analysis
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    def _analyze_content(self, content: str, url: str) -> Dict[str, Any]:
        """Analyze the HTML content"""
        
        analysis = {
            'content_length': len(content),
            'content_type': 'HTML',
        }
        
        # Extract title
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
        analysis['page_title'] = title_match.group(1).strip() if title_match else 'Unknown'
        
        # Extract main heading
        h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', content, re.IGNORECASE)
        analysis['main_heading'] = h1_match.group(1).strip() if h1_match else 'Not found'
        
        # Count key elements
        analysis['element_counts'] = {
            'headings_h1': len(re.findall(r'<h1[^>]*>', content, re.IGNORECASE)),
            'headings_h2': len(re.findall(r'<h2[^>]*>', content, re.IGNORECASE)),
            'headings_h3': len(re.findall(r'<h3[^>]*>', content, re.IGNORECASE)),
            'paragraphs': len(re.findall(r'<p[^>]*>', content, re.IGNORECASE)),
            'links': len(re.findall(r'<a[^>]*href=', content, re.IGNORECASE)),
            'buttons': len(re.findall(r'<button[^>]*>', content, re.IGNORECASE)),
            'images': len(re.findall(r'<img[^>]*>', content, re.IGNORECASE)),
            'forms': len(re.findall(r'<form[^>]*>', content, re.IGNORECASE)),
        }
        
        # Brand analysis
        analysis['brand_elements'] = {
            'agent_forge_mentions': len(re.findall(r'agent.forge', content, re.IGNORECASE)),
            'sacred_smithy_mentions': len(re.findall(r'sacred.smithy', content, re.IGNORECASE)),
            'ancient_gold_color': 'F59E0B' in content,
            'nuru_purple_color': '7C3AED' in content,
            'ancient_bronze_color': 'CD7F32' in content,
        }
        
        # Framework features
        analysis['framework_features'] = {
            'steel_browser_mentioned': 'steel browser' in content.lower(),
            'mcp_integration_mentioned': 'mcp' in content.lower(),
            'ai_agent_mentioned': 'ai agent' in content.lower(),
            'python_framework_mentioned': 'python framework' in content.lower(),
            'browser_automation_mentioned': 'browser automation' in content.lower(),
        }
        
        # Navigation analysis
        nav_links = re.findall(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>', content, re.IGNORECASE)
        analysis['navigation'] = {
            'total_links': len(nav_links),
            'internal_links': len([link for link, text in nav_links if link.startswith('/') or 'localhost' in link]),
            'external_links': len([link for link, text in nav_links if link.startswith('http') and 'localhost' not in link]),
            'key_sections': []
        }
        
        # Look for key navigation sections
        for link, text in nav_links:
            text_clean = text.strip()
            if text_clean.lower() in ['documentation', 'docs', 'examples', 'getting started', 'use cases']:
                analysis['navigation']['key_sections'].append({
                    'text': text_clean,
                    'href': link
                })
        
        # Performance indicators
        analysis['performance_indicators'] = {
            'has_inline_styles': '<style' in content,
            'has_external_stylesheets': 'rel="stylesheet"' in content,
            'has_scripts': '<script' in content,
            'content_size_kb': round(len(content) / 1024, 2),
            'estimated_load_elements': analysis['element_counts']['images'] + analysis['element_counts']['links']
        }
        
        # Accessibility indicators
        analysis['accessibility'] = {
            'has_alt_attributes': 'alt=' in content,
            'has_aria_labels': 'aria-label' in content,
            'has_semantic_html': any(tag in content.lower() for tag in ['<main', '<nav', '<header', '<footer', '<section', '<article']),
            'has_headings_structure': analysis['element_counts']['headings_h1'] > 0 and analysis['element_counts']['headings_h2'] > 0
        }
        
        return analysis

async def main():
    """Main function to run website analysis"""
    print("🔥 Agent Forge Website Analysis")
    print("=" * 50)
    
    # Check for command line URL argument
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3001"
    
    async with WebsiteAnalysisAgent() as agent:
        result = await agent.analyze_website(url)
        
        if result['success']:
            print("✅ Website analysis completed!")
            print()
            
            # Basic info
            print("📄 Basic Information:")
            print(f"   • Page Title: {result['page_title']}")
            print(f"   • Main Heading: {result['main_heading']}")
            print(f"   • Content Size: {result['content_length']:,} characters ({result['performance_indicators']['content_size_kb']} KB)")
            print()
            
            # Element counts
            print("📊 Content Structure:")
            for element, count in result['element_counts'].items():
                print(f"   • {element.replace('_', ' ').title()}: {count}")
            print()
            
            # Brand analysis
            print("🎨 Brand Analysis:")
            brand = result['brand_elements']
            print(f"   • Agent Forge mentions: {brand['agent_forge_mentions']}")
            print(f"   • Sacred Smithy mentions: {brand['sacred_smithy_mentions']}")
            print(f"   • Brand colors detected: {sum([brand['ancient_gold_color'], brand['nuru_purple_color'], brand['ancient_bronze_color']])}/3")
            print()
            
            # Framework features
            print("🔧 Framework Features:")
            features = result['framework_features']
            for feature, present in features.items():
                status = "✅" if present else "❌"
                feature_name = feature.replace('_', ' ').replace('mentioned', '').title()
                print(f"   {status} {feature_name}")
            print()
            
            # Navigation
            print("🧭 Navigation Analysis:")
            nav = result['navigation']
            print(f"   • Total links: {nav['total_links']}")
            print(f"   • Internal links: {nav['internal_links']}")
            print(f"   • External links: {nav['external_links']}")
            print(f"   • Key sections found: {len(nav['key_sections'])}")
            for section in nav['key_sections']:
                print(f"     - {section['text']} ({section['href']})")
            print()
            
            # Accessibility
            print("♿ Accessibility Check:")
            accessibility = result['accessibility']
            for check, passed in accessibility.items():
                status = "✅" if passed else "❌"
                check_name = check.replace('_', ' ').replace('has ', '').title()
                print(f"   {status} {check_name}")
            print()
            
            # Overall assessment
            print("🎯 Overall Assessment:")
            
            # Brand implementation score
            brand_score = sum([
                brand['agent_forge_mentions'] > 0,
                brand['sacred_smithy_mentions'] > 0,
                brand['ancient_gold_color'],
                brand['nuru_purple_color'],
                brand['ancient_bronze_color']
            ]) / 5 * 100
            
            # Feature completeness score
            feature_score = sum(features.values()) / len(features) * 100
            
            # Accessibility score
            accessibility_score = sum(accessibility.values()) / len(accessibility) * 100
            
            print(f"   • Brand Implementation: {brand_score:.0f}%")
            print(f"   • Feature Completeness: {feature_score:.0f}%")
            print(f"   • Accessibility: {accessibility_score:.0f}%")
            print(f"   • Overall Score: {(brand_score + feature_score + accessibility_score) / 3:.0f}%")
            
        else:
            print("❌ Website analysis failed!")
            print(f"🚨 Error: {result['error']}")
            
        return result

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result.get('success') else 1)