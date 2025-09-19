# Content Guardrails

Check the draft for content safety and legal compliance issues.

## Red Flags to Detect

- **PII Leakage**: Any remaining personal information after redaction
- **Doxxing**: Real names, addresses, phone numbers, social media handles
- **Career-Sensitive Content**: Unverified accusations, defamatory statements
- **Blocked Phrases**: Content from the blocked_phrases list in config
- **Unverified Claims**: Statements presented as fact without evidence

## Response Format

Return JSON with this structure:

```json
{
  "ok": boolean,
  "issues": ["list of specific issues found"],
  "patch": "optional text replacement to fix issues"
}
```

## Patch Guidelines

- Only provide patches for simple text replacements
- Remove problematic content, don't rewrite
- Preserve the original structure and flow
- If complex rewriting needed, set "ok": false and describe the issue

## Examples

**Issue**: "John Smith at john@example.com said..."
**Patch**: "A user said..."

**Issue**: "This company is definitely committing fraud"
**Patch**: "This company may have compliance issues"
