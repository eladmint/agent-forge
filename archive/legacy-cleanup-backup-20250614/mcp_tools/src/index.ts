#!/usr/bin/env node

/**
 * TokenHunter Browser Control MCP Server
 * 
 * A Model Context Protocol server that provides browser automation capabilities
 * for enhanced web scraping. This server integrates with Playwright to offer
 * debugging and interactive exploration features for the TokenHunter scraping system.
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import { chromium, Browser, Page } from 'playwright';
import { Command } from 'commander';

/**
 * Browser Control MCP Server for TokenHunter
 * 
 * Provides tools for:
 * - Browser automation and debugging
 * - Interactive site exploration
 * - Screenshot and content extraction
 * - Network monitoring and analysis
 */
class BrowserControlServer {
  private server: Server;
  private browser: Browser | null = null;
  private pages: Map<string, Page> = new Map();

  constructor() {
    this.server = new Server(
      {
        name: 'tokenhunter-browser-control',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
    this.setupErrorHandling();
  }

  /**
   * Setup tool handlers for browser automation
   */
  private setupToolHandlers(): void {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'launch_browser',
            description: 'Launch a new browser instance for debugging',
            inputSchema: {
              type: 'object',
              properties: {
                headless: {
                  type: 'boolean',
                  description: 'Whether to run browser in headless mode',
                  default: true,
                },
                debug: {
                  type: 'boolean',
                  description: 'Enable debug mode with slower operations',
                  default: false,
                },
              },
            },
          },
          {
            name: 'navigate_to_url',
            description: 'Navigate to a specific URL and analyze the page',
            inputSchema: {
              type: 'object',
              properties: {
                url: {
                  type: 'string',
                  description: 'URL to navigate to',
                },
                waitFor: {
                  type: 'string',
                  description: 'Wait condition: networkidle, domcontentloaded, or load',
                  default: 'networkidle',
                },
                timeout: {
                  type: 'number',
                  description: 'Timeout in milliseconds',
                  default: 30000,
                },
              },
              required: ['url'],
            },
          },
          {
            name: 'extract_content',
            description: 'Extract content from the current page',
            inputSchema: {
              type: 'object',
              properties: {
                selector: {
                  type: 'string',
                  description: 'CSS selector to extract specific elements',
                },
                extractType: {
                  type: 'string',
                  enum: ['text', 'html', 'attributes'],
                  description: 'Type of content to extract',
                  default: 'text',
                },
              },
            },
          },
          {
            name: 'take_screenshot',
            description: 'Take a screenshot of the current page',
            inputSchema: {
              type: 'object',
              properties: {
                fullPage: {
                  type: 'boolean',
                  description: 'Take a full page screenshot',
                  default: true,
                },
                path: {
                  type: 'string',
                  description: 'Path to save the screenshot',
                },
              },
            },
          },
          {
            name: 'analyze_network',
            description: 'Analyze network requests for debugging',
            inputSchema: {
              type: 'object',
              properties: {
                includeRedirects: {
                  type: 'boolean',
                  description: 'Include redirect responses',
                  default: true,
                },
                filterUrl: {
                  type: 'string',
                  description: 'Filter requests by URL pattern',
                },
              },
            },
          },
          {
            name: 'close_browser',
            description: 'Close the browser instance',
            inputSchema: {
              type: 'object',
              properties: {},
            },
          },
        ],
      };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'launch_browser':
            return await this.launchBrowser(args);
          case 'navigate_to_url':
            return await this.navigateToUrl(args);
          case 'extract_content':
            return await this.extractContent(args);
          case 'take_screenshot':
            return await this.takeScreenshot(args);
          case 'analyze_network':
            return await this.analyzeNetwork(args);
          case 'close_browser':
            return await this.closeBrowser();
          default:
            throw new McpError(
              ErrorCode.MethodNotFound,
              `Unknown tool: ${name}`
            );
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        throw new McpError(
          ErrorCode.InternalError,
          `Tool execution failed: ${errorMessage}`
        );
      }
    });
  }

  /**
   * Setup error handling
   */
  private setupErrorHandling(): void {
    this.server.onerror = (error) => console.error('[MCP Error]', error);
    process.on('SIGINT', async () => {
      await this.cleanup();
      process.exit(0);
    });
  }

  /**
   * Launch browser instance
   */
  private async launchBrowser(args: any) {
    const { headless = true, debug = false } = args;

    if (this.browser) {
      await this.browser.close();
    }

    this.browser = await chromium.launch({
      headless,
      slowMo: debug ? 100 : 0,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-renderer-backgrounding',
      ],
    });

    const context = await this.browser.newContext({
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
      viewport: { width: 1920, height: 1080 },
    });

    const page = await context.newPage();
    this.pages.set('main', page);

    return {
      content: [
        {
          type: 'text',
          text: `Browser launched successfully. Headless: ${headless}, Debug: ${debug}`,
        },
      ],
    };
  }

  /**
   * Navigate to URL
   */
  private async navigateToUrl(args: any) {
    const { url, waitFor = 'networkidle', timeout = 30000 } = args;

    if (!this.browser) {
      throw new Error('Browser not launched. Call launch_browser first.');
    }

    const page = this.pages.get('main');
    if (!page) {
      throw new Error('No active page found.');
    }

    const response = await page.goto(url, {
      waitUntil: waitFor as any,
      timeout,
    });

    const title = await page.title();
    const currentUrl = page.url();

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            success: true,
            url: currentUrl,
            title,
            status: response?.status(),
            redirected: response?.url() !== url,
          }, null, 2),
        },
      ],
    };
  }

  /**
   * Extract content from page
   */
  private async extractContent(args: any) {
    const { selector, extractType = 'text' } = args;

    const page = this.pages.get('main');
    if (!page) {
      throw new Error('No active page found.');
    }

    let content;
    if (selector) {
      const elements = await page.$$(selector);
      if (extractType === 'text') {
        content = await Promise.all(
          elements.map(el => el.textContent())
        );
      } else if (extractType === 'html') {
        content = await Promise.all(
          elements.map(el => el.innerHTML())
        );
      } else if (extractType === 'attributes') {
        content = await Promise.all(
          elements.map(async el => {
            const tagName = await el.evaluate(node => node.tagName);
            const attributes: Record<string, string> = {};
            const attrNames = await el.evaluate((node: Element) => 
              Array.from(node.attributes).map((a: any) => a.name)
            );
            for (const attr of attrNames) {
              attributes[attr] = await el.getAttribute(attr) || '';
            }
            return { tagName, attributes };
          })
        );
      }
    } else {
      // Extract all page content
      if (extractType === 'text') {
        content = await page.textContent('body');
      } else if (extractType === 'html') {
        content = await page.content();
      }
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            selector: selector || 'body',
            extractType,
            content,
            elementCount: Array.isArray(content) ? content.length : 1,
          }, null, 2),
        },
      ],
    };
  }

  /**
   * Take screenshot
   */
  private async takeScreenshot(args: any) {
    const { fullPage = true, path } = args;

    const page = this.pages.get('main');
    if (!page) {
      throw new Error('No active page found.');
    }

    const screenshot = await page.screenshot({
      fullPage,
      path: path || `screenshot-${Date.now()}.png`,
    });

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            success: true,
            path: path || `screenshot-${Date.now()}.png`,
            size: screenshot.length,
            fullPage,
          }, null, 2),
        },
      ],
    };
  }

  /**
   * Analyze network requests
   */
  private async analyzeNetwork(args: any) {
    const { includeRedirects = true, filterUrl } = args;

    const page = this.pages.get('main');
    if (!page) {
      throw new Error('No active page found.');
    }

    const requests: any[] = [];
    
    // Set up network monitoring
    page.on('request', request => {
      const url = request.url();
      if (!filterUrl || url.includes(filterUrl)) {
        requests.push({
          url,
          method: request.method(),
          headers: request.headers(),
          timestamp: Date.now(),
        });
      }
    });

    page.on('response', response => {
      if (!includeRedirects && response.status() >= 300 && response.status() < 400) {
        return;
      }
      
      const url = response.url();
      if (!filterUrl || url.includes(filterUrl)) {
        const requestIndex = requests.findIndex(req => req.url === url);
        if (requestIndex >= 0) {
          requests[requestIndex] = {
            ...requests[requestIndex],
            status: response.status(),
            headers: response.headers(),
            contentType: response.headers()['content-type'],
          };
        }
      }
    });

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            message: 'Network monitoring enabled',
            currentRequests: requests.length,
            filter: filterUrl || 'none',
            includeRedirects,
          }, null, 2),
        },
      ],
    };
  }

  /**
   * Close browser
   */
  private async closeBrowser() {
    if (this.browser) {
      await this.browser.close();
      this.browser = null;
      this.pages.clear();
    }

    return {
      content: [
        {
          type: 'text',
          text: 'Browser closed successfully',
        },
      ],
    };
  }

  /**
   * Cleanup resources
   */
  private async cleanup(): Promise<void> {
    if (this.browser) {
      await this.browser.close();
    }
  }

  /**
   * Start the MCP server
   */
  async run(): Promise<void> {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('TokenHunter Browser Control MCP Server running on stdio');
  }
}

/**
 * CLI interface
 */
const program = new Command();

program
  .name('tokenhunter-browser-control')
  .description('Browser Control MCP Server for TokenHunter')
  .version('1.0.0')
  .action(async () => {
    const server = new BrowserControlServer();
    await server.run();
  });

program.parse();