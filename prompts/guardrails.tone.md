# Tone Guardrails

Check the draft for appropriate editorial tone and length compliance.

## Requirements

- **Length**: 300-600 words target, 900 words hard cap
- **Tone**: Neutral, professional, editorial
- **Tags**: 3-6 lowercase tags
- **Structure**: Clear sections with proper formatting

## Issues to Detect

- **Too Short**: Under 300 words (unless exceptional content)
- **Too Long**: Over 900 words (hard cap violation)
- **Inappropriate Tone**: 
  - Overly casual or slang
  - Excessive enthusiasm or marketing speak
  - Personal opinions presented as facts
  - Inflammatory or divisive language
- **Poor Structure**:
  - Missing clear sections
  - No concrete takeaways
  - Rambling or unfocused content
- **Tag Issues**:
  - Wrong count (not 3-6)
  - Not lowercase
  - Too generic or too specific

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

- For length issues: trim or expand content appropriately
- For tone issues: rewrite problematic sections
- For structure: add missing sections or reorganize
- For tags: provide corrected tag list

## Examples

**Issue**: "This is AMAZING and you NEED to try it!!!"
**Patch**: "This approach shows significant potential and is worth considering."

**Issue**: "Tags: ['AI', 'MACHINE LEARNING', 'DEEP LEARNING']"
**Patch**: "Tags: ['ai', 'machine-learning', 'technology']"
