/**
 * Playwright script for creating Substack drafts
 * Feature-flagged and only runs when create_draft=true
 */

import { chromium, Browser, Page } from 'playwright';

interface SubstackCredentials {
  email: string;
  password: string;
  host: string;
}

interface DraftData {
  title: string;
  content: string;
  tags: string[];
}

export class SubstackDraftCreator {
  private browser: Browser | null = null;
  private page: Page | null = null;
  private credentials: SubstackCredentials;

  constructor(credentials: SubstackCredentials) {
    this.credentials = credentials;
  }

  async initialize(): Promise<void> {
    this.browser = await chromium.launch({ headless: false });
    this.page = await this.browser.newPage();
    
    // Set viewport
    await this.page.setViewportSize({ width: 1280, height: 720 });
  }

  async login(): Promise<boolean> {
    if (!this.page) throw new Error('Page not initialized');

    try {
      // Navigate to login page
      const loginUrl = `${this.credentials.host}/login`;
      await this.page.goto(loginUrl);
      
      // Wait for login form
      await this.page.waitForSelector('input[type="email"]', { timeout: 10000 });
      
      // Fill credentials
      await this.page.fill('input[type="email"]', this.credentials.email);
      await this.page.fill('input[type="password"]', this.credentials.password);
      
      // Click login button
      await this.page.click('button[type="submit"]');
      
      // Wait for redirect to dashboard
      await this.page.waitForURL('**/dashboard**', { timeout: 15000 });
      
      // Save storage state for future use
      await this.page.context().storageState({ path: 'storageState.json' });
      
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  }

  async createDraft(draftData: DraftData): Promise<string | null> {
    if (!this.page) throw new Error('Page not initialized');

    try {
      // Navigate to new post page
      const newPostUrl = `${this.credentials.host}/new`;
      await this.page.goto(newPostUrl);
      
      // Wait for editor to load
      await this.page.waitForSelector('[data-testid="post-title"]', { timeout: 10000 });
      
      // Fill title
      await this.page.fill('[data-testid="post-title"]', draftData.title);
      
      // Wait for content editor
      await this.page.waitForSelector('.DraftEditor-root', { timeout: 5000 });
      
      // Click in content area and paste content
      await this.page.click('.DraftEditor-root');
      await this.page.keyboard.press('Control+a'); // Select all
      await this.page.keyboard.type(draftData.content);
      
      // Add tags if provided
      if (draftData.tags.length > 0) {
        // Look for tags input
        const tagsInput = await this.page.$('input[placeholder*="tag" i]');
        if (tagsInput) {
          for (const tag of draftData.tags) {
            await tagsInput.fill(tag);
            await this.page.keyboard.press('Enter');
          }
        }
      }
      
      // Save as draft
      const saveButton = await this.page.$('button:has-text("Save")');
      if (saveButton) {
        await saveButton.click();
        
        // Wait for save confirmation
        await this.page.waitForSelector('.notification, .toast', { timeout: 5000 });
        
        // Get current URL (should be the draft URL)
        const currentUrl = this.page.url();
        return currentUrl;
      }
      
      return null;
    } catch (error) {
      console.error('Draft creation failed:', error);
      return null;
    }
  }

  async close(): Promise<void> {
    if (this.browser) {
      await this.browser.close();
    }
  }
}

export async function createSubstackDraft(
  credentials: SubstackCredentials,
  draftData: DraftData
): Promise<string | null> {
  const creator = new SubstackDraftCreator(credentials);
  
  try {
    await creator.initialize();
    
    const loginSuccess = await creator.login();
    if (!loginSuccess) {
      throw new Error('Login failed');
    }
    
    const draftUrl = await creator.createDraft(draftData);
    return draftUrl;
  } finally {
    await creator.close();
  }
}

// CLI interface
if (require.main === module) {
  const credentials: SubstackCredentials = {
    email: process.env.SUBSTACK_EMAIL || '',
    password: process.env.SUBSTACK_PASSWORD || '',
    host: process.env.SUBSTACK_HOST || 'https://YOURNAME.substack.com'
  };

  const draftData: DraftData = {
    title: process.argv[2] || 'Test Draft',
    content: process.argv[3] || 'Test content',
    tags: (process.argv[4] || '').split(',').filter(t => t.trim())
  };

  createSubstackDraft(credentials, draftData)
    .then(url => {
      if (url) {
        console.log(`Draft created: ${url}`);
      } else {
        console.error('Failed to create draft');
        process.exit(1);
      }
    })
    .catch(error => {
      console.error('Error:', error);
      process.exit(1);
    });
}
