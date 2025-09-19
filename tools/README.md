# Tools

This directory contains development and integration tools for the chat2substack pipeline.

## Playwright Integration

The `playwright/` directory contains Node.js dependencies and configuration for Substack integration via Playwright browser automation.

### Files

- `package.json` - Node.js package configuration
- `package-lock.json` - Dependency lock file
- `node_modules/` - Node.js dependencies

### Usage

To use Playwright for Substack integration:

```bash
cd tools/playwright
npm install
npx playwright install
```

### Note

This integration is feature-flagged and not required for basic pipeline operation. It's only used when `--create-draft=true` is specified.
