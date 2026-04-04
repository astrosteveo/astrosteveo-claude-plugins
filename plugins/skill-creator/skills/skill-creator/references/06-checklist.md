# Skill Validation Checklist

Use this checklist to validate a skill before and after upload.

## Before You Start

- [ ] Identified 2–3 concrete use cases
- [ ] Tools identified (built-in or MCP)
- [ ] Planned folder structure

## During Development

- [ ] Folder named in kebab-case
- [ ] SKILL.md file exists (exact spelling, case-sensitive)
- [ ] YAML frontmatter has `---` delimiters (top and bottom)
- [ ] Folder name is kebab-case (this IS the skill name — `name` field is optional)
- [ ] Folder name does not contain "claude" or "anthropic"
- [ ] `description` includes WHAT it does and WHEN to use it
- [ ] `description` is under 1024 characters
- [ ] No XML angle brackets (< >) anywhere in SKILL.md
- [ ] No `README.md` inside the skill folder
- [ ] Instructions are clear and actionable
- [ ] Error handling included for likely failure modes
- [ ] Examples provided for common scenarios
- [ ] References clearly linked (if using `references/`)
- [ ] SKILL.md is under 500 lines

## Trigger Quality

- [ ] Description includes 3+ trigger phrases users would actually say
- [ ] Description is specific enough to avoid false triggers
- [ ] Description mentions relevant file types (if applicable)
- [ ] Negative triggers included if needed (to prevent over-triggering)
- [ ] Description is written in third person (not first/second person)

## Before Upload

- [ ] Tested: triggers on obvious tasks
- [ ] Tested: triggers on paraphrased requests
- [ ] Verified: doesn't trigger on unrelated topics
- [ ] Functional tests pass
- [ ] Tool integration works (if applicable)

## After Upload

- [ ] Tested in real conversations
- [ ] Monitored for under/over-triggering
- [ ] Collected user feedback
- [ ] Iterated on description and instructions
- [ ] Updated version in metadata (if applicable)
