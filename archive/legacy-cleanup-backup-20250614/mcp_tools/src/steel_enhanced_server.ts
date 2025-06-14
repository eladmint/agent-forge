#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';

import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import RecaptchaPlugin from 'puppeteer-extra-plugin-recaptcha';
import { Browser, Page } from 'puppeteer';

// Configure Puppeteer with anti-bot plugins
puppeteer.use(StealthPlugin());
puppeteer.use(RecaptchaPlugin({
  provider: {
    id: '2captcha',
    token: process.env.RECAPTCHA_TOKEN || 'demo' // Configure in production
  },
  visualFeedback: true
}));

interface SteelSession {
  id: string;
  browser: Browser;
  page: Page;
  created: Date;
  lastUsed: Date;
  capabilities: string[];
}

interface SiteAnalysis {
  complexity: 'simple' | 'moderate' | 'high';
  hasCaptcha: boolean;
  hasAntiBot: boolean;
  recommendedTier: number;
  confidence: number;
}

class SteelEnhancedMCPServer {
  private server: Server;
  private sessions: Map<string, SteelSession> = new Map();
  private sessionCounter = 0;

  constructor() {
    this.server = new Server(
      {
        name: 'steel-enhanced-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
    this.setupCleanupTimer();
  }

  private setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'steel_analyze_site',
          description: 'Analyze website complexity and protection mechanisms',
          inputSchema: {
            type: 'object',
            properties: {
              url: {
                type: 'string',
                description: 'URL to analyze'
              }
            },
            required: ['url'],
          },
        },
        {
          name: 'steel_launch_session',
          description: 'Create enhanced Steel Browser session with anti-bot features',
          inputSchema: {
            type: 'object',
            properties: {
              headless: {
                type: 'boolean',
                description: 'Run browser in headless mode',
                default: true
              },
              timeout: {
                type: 'number',
                description: 'Session timeout in milliseconds',
                default: 3600000
              },
              antiDetection: {
                type: 'boolean',
                description: 'Enable advanced anti-detection features',
                default: true
              }
            },
          },
        },
        {
          name: 'steel_navigate_protected',
          description: 'Navigate to protected sites with anti-bot evasion',
          inputSchema: {
            type: 'object',
            properties: {
              sessionId: {
                type: 'string',
                description: 'Steel Browser session ID'
              },
              url: {
                type: 'string',
                description: 'URL to navigate to'
              },
              waitFor: {
                type: 'string',
                enum: ['load', 'networkidle', 'domcontentloaded'],
                description: 'Wait condition',
                default: 'networkidle'
              },
              timeout: {
                type: 'number',
                description: 'Navigation timeout in milliseconds',
                default: 30000
              }
            },
            required: ['sessionId', 'url'],
          },
        },
        {
          name: 'steel_solve_captcha',
          description: 'Automatically solve CAPTCHAs using Steel Browser',
          inputSchema: {
            type: 'object',
            properties: {
              sessionId: {
                type: 'string',
                description: 'Steel Browser session ID'
              },
              timeout: {
                type: 'number',
                description: 'CAPTCHA solving timeout in milliseconds',
                default: 30000
              },
              selector: {
                type: 'string',
                description: 'CAPTCHA element selector (optional)'
              }
            },
            required: ['sessionId'],
          },
        },
        {
          name: 'steel_extract_enhanced_content',
          description: 'Extract content with enhanced anti-bot capabilities',
          inputSchema: {
            type: 'object',
            properties: {
              sessionId: {
                type: 'string',
                description: 'Steel Browser session ID'
              },
              selectors: {
                type: 'object',
                description: 'CSS selectors for content extraction'
              },
              includeMetadata: {
                type: 'boolean',
                description: 'Include page metadata',
                default: true
              }
            },
            required: ['sessionId'],
          },
        },
        {
          name: 'steel_manage_session',
          description: 'Manage long-running Steel Browser session',
          inputSchema: {
            type: 'object',
            properties: {
              sessionId: {
                type: 'string',
                description: 'Steel Browser session ID'
              },
              action: {
                type: 'string',
                enum: ['refresh', 'extend', 'status'],
                description: 'Session management action'
              },
              extensionTime: {
                type: 'number',
                description: 'Additional time in milliseconds for extend action'
              }
            },
            required: ['sessionId', 'action'],
          },
        },
        {
          name: 'steel_close_session',
          description: 'Clean session termination',
          inputSchema: {
            type: 'object',
            properties: {
              sessionId: {
                type: 'string',
                description: 'Steel Browser session ID'
              }
            },
            required: ['sessionId'],
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      try {
        const { name, arguments: args } = request.params;

        switch (name) {
          case 'steel_analyze_site':
            return await this.handleAnalyzeSite(args);
          case 'steel_launch_session':
            return await this.handleLaunchSession(args);
          case 'steel_navigate_protected':
            return await this.handleNavigateProtected(args);
          case 'steel_solve_captcha':
            return await this.handleSolveCaptcha(args);
          case 'steel_extract_enhanced_content':
            return await this.handleExtractContent(args);
          case 'steel_manage_session':
            return await this.handleManageSession(args);
          case 'steel_close_session':
            return await this.handleCloseSession(args);
          default:
            throw new McpError(
              ErrorCode.MethodNotFound,
              `Unknown tool: ${name}`
            );
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        throw new McpError(ErrorCode.InternalError, errorMessage);
      }
    });
  }

  private async handleAnalyzeSite(args: any) {
    const { url } = args;
    
    try {
      const analysis: SiteAnalysis = {
        complexity: 'simple',
        hasCaptcha: false,
        hasAntiBot: false,
        recommendedTier: 1,
        confidence: 0.8
      };

      // Quick analysis based on URL patterns and known sites
      if (url.includes('luma.co') || url.includes('eventbrite.com')) {
        analysis.complexity = 'simple';
        analysis.recommendedTier = 1;
        analysis.confidence = 0.95;
      } else if (url.includes('facebook.com') || url.includes('instagram.com') || 
                 url.includes('linkedin.com') || url.includes('twitter.com')) {
        analysis.complexity = 'high';
        analysis.hasAntiBot = true;
        analysis.recommendedTier = 3;
        analysis.confidence = 0.9;
      } else {
        // Moderate complexity for unknown sites
        analysis.complexity = 'moderate';
        analysis.recommendedTier = 2;
        analysis.confidence = 0.6;
      }

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            analysis,
            message: `Site analyzed: ${analysis.complexity} complexity, recommended tier ${analysis.recommendedTier}`
          })
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            error: `Site analysis failed: ${error instanceof Error ? error.message : String(error)}`
          })
        }]
      };
    }
  }

  private async handleLaunchSession(args: any) {
    const { headless = true, timeout = 3600000, antiDetection = true } = args;
    
    try {
      const sessionId = `steel_${++this.sessionCounter}_${Date.now()}`;

      // Launch browser with enhanced anti-detection features
      const browser = await puppeteer.launch({
        headless: headless,
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-dev-shm-usage',
          '--disable-accelerated-2d-canvas',
          '--no-first-run',
          '--no-zygote',
          '--disable-gpu',
          '--disable-background-timer-throttling',
          '--disable-backgrounding-occluded-windows',
          '--disable-renderer-backgrounding',
          '--disable-features=TranslateUI',
          '--disable-ipc-flooding-protection',
          ...(antiDetection ? [
            '--disable-blink-features=AutomationControlled',
            '--no-default-browser-check',
            '--disable-web-security'
          ] : [])
        ]
      });

      const page = await browser.newPage();

      // Enhanced anti-detection setup
      if (antiDetection) {
        await page.evaluateOnNewDocument(() => {
          // Remove webdriver property
          delete (window.navigator as any).webdriver;
          
          // Override the plugins property to use a custom getter
          Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
          });
          
          // Override the languages property to use a custom getter
          Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
          });
          
          // Override the webGL vendor and renderer
          const getParameter = WebGLRenderingContext.prototype.getParameter;
          WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) {
              return 'Intel Inc.';
            }
            if (parameter === 37446) {
              return 'Intel Iris OpenGL Engine';
            }
            return getParameter.call(this, parameter);
          };
        });

        // Set realistic viewport
        await page.setViewport({ width: 1366, height: 768 });

        // Set user agent
        await page.setUserAgent(
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        );
      }

      const capabilities = [
        'anti-detection',
        'captcha-solving',
        'session-management',
        'stealth-navigation'
      ];

      const session: SteelSession = {
        id: sessionId,
        browser,
        page,
        created: new Date(),
        lastUsed: new Date(),
        capabilities
      };

      this.sessions.set(sessionId, session);

      // Set cleanup timeout
      setTimeout(() => {
        if (this.sessions.has(sessionId)) {
          this.cleanupSession(sessionId);
        }
      }, timeout);

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            sessionId,
            capabilities,
            status: 'created',
            message: `Steel Browser session created with enhanced anti-bot features`
          })
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            error: `Failed to launch Steel Browser session: ${error instanceof Error ? error.message : String(error)}`
          })
        }]
      };
    }
  }

  private async handleNavigateProtected(args: any) {
    const { sessionId, url, waitFor = 'networkidle', timeout = 30000 } = args;
    
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error(`Session ${sessionId} not found`);
    }

    try {
      session.lastUsed = new Date();

      // Navigate with enhanced protection
      const response = await session.page.goto(url, {
        waitUntil: waitFor === 'networkidle' ? 'networkidle2' : waitFor as any,
        timeout
      });

      // Check for CAPTCHA presence
      const captchaDetected = await this.detectCaptcha(session.page);

      const result = {
        status: 'success',
        url: session.page.url(),
        title: await session.page.title(),
        captchaDetected,
        responseStatus: response?.status() || 0,
        loadTime: Date.now() - session.lastUsed.getTime()
      };

      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result)
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            error: `Navigation failed: ${error instanceof Error ? error.message : String(error)}`,
            sessionId
          })
        }]
      };
    }
  }

  private async handleSolveCaptcha(args: any) {
    const { sessionId, timeout = 30000, selector } = args;
    
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error(`Session ${sessionId} not found`);
    }

    try {
      session.lastUsed = new Date();

      // Try to solve CAPTCHA using puppeteer-extra-plugin-recaptcha
      const result = await (session.page as any).solveRecaptchas();

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            solved: result.solved > 0,
            captchasSolved: result.solved,
            message: result.solved > 0 ? 'CAPTCHA solved successfully' : 'No CAPTCHAs found or solving failed'
          })
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            solved: false,
            error: `CAPTCHA solving failed: ${error instanceof Error ? error.message : String(error)}`
          })
        }]
      };
    }
  }

  private async handleExtractContent(args: any) {
    const { sessionId, selectors, includeMetadata = true } = args;
    
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error(`Session ${sessionId} not found`);
    }

    try {
      session.lastUsed = new Date();

      const content: any = {};

      // Extract basic content
      content.title = await session.page.title();
      content.url = session.page.url();
      content.html = await session.page.content();

      // Extract with custom selectors if provided
      if (selectors) {
        content.extracted = {};
        for (const [key, selector] of Object.entries(selectors)) {
          try {
            const elements = await session.page.$$(selector as string);
            content.extracted[key] = await Promise.all(
              elements.map(el => el.evaluate(node => node.textContent?.trim()))
            );
          } catch (e) {
            content.extracted[key] = null;
          }
        }
      }

      // Include metadata if requested
      if (includeMetadata) {
        content.metadata = {
          viewport: await session.page.viewport(),
          cookies: await session.page.cookies(),
          timestamp: new Date().toISOString(),
          userAgent: await session.page.evaluate(() => navigator.userAgent)
        };
      }

      return {
        content: [{
          type: 'text',
          text: JSON.stringify(content)
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            error: `Content extraction failed: ${error instanceof Error ? error.message : String(error)}`
          })
        }]
      };
    }
  }

  private async handleManageSession(args: any) {
    const { sessionId, action, extensionTime } = args;
    
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error(`Session ${sessionId} not found`);
    }

    try {
      switch (action) {
        case 'refresh':
          await session.page.reload();
          session.lastUsed = new Date();
          break;
        case 'extend':
          // Session extension would be handled by timeout management
          session.lastUsed = new Date();
          break;
        case 'status':
          break;
        default:
          throw new Error(`Unknown action: ${action}`);
      }

      const status = {
        sessionId,
        action,
        created: session.created,
        lastUsed: session.lastUsed,
        capabilities: session.capabilities,
        currentUrl: session.page.url(),
        uptime: Date.now() - session.created.getTime()
      };

      return {
        content: [{
          type: 'text',
          text: JSON.stringify(status)
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            error: `Session management failed: ${error instanceof Error ? error.message : String(error)}`
          })
        }]
      };
    }
  }

  private async handleCloseSession(args: any) {
    const { sessionId } = args;
    
    try {
      const cleaned = await this.cleanupSession(sessionId);
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            sessionId,
            status: cleaned ? 'closed' : 'not_found',
            message: cleaned ? 'Session closed successfully' : 'Session not found'
          })
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            error: `Session cleanup failed: ${error instanceof Error ? error.message : String(error)}`
          })
        }]
      };
    }
  }

  private async detectCaptcha(page: Page): Promise<boolean> {
    try {
      // Check for common CAPTCHA indicators
      const captchaSelectors = [
        '.g-recaptcha',
        '.h-captcha',
        '#cf-challenge-stage',
        '.captcha',
        '[data-captcha]'
      ];

      for (const selector of captchaSelectors) {
        const element = await page.$(selector);
        if (element) {
          return true;
        }
      }

      // Check for CAPTCHA text content
      const pageText = await page.evaluate(() => document.body.textContent?.toLowerCase() || '');
      const captchaKeywords = ['captcha', 'verify you are human', 'security check', 'prove you are not a robot'];
      
      return captchaKeywords.some(keyword => pageText.includes(keyword));
    } catch (error) {
      return false;
    }
  }

  private async cleanupSession(sessionId: string): Promise<boolean> {
    const session = this.sessions.get(sessionId);
    if (!session) {
      return false;
    }

    try {
      await session.browser.close();
      this.sessions.delete(sessionId);
      return true;
    } catch (error) {
      console.error(`Error cleaning up session ${sessionId}:`, error);
      this.sessions.delete(sessionId);
      return true;
    }
  }

  private setupCleanupTimer() {
    // Clean up stale sessions every 30 minutes
    setInterval(() => {
      const now = Date.now();
      const maxAge = 30 * 60 * 1000; // 30 minutes

      for (const [sessionId, session] of this.sessions.entries()) {
        if (now - session.lastUsed.getTime() > maxAge) {
          this.cleanupSession(sessionId);
        }
      }
    }, 30 * 60 * 1000);
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Steel Enhanced MCP Server running on stdio');
  }
}

const server = new SteelEnhancedMCPServer();
server.run().catch(console.error);