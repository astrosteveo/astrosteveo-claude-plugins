# Testing and Iteration

Skills can be tested at varying levels of rigor. Choose the approach that matches your quality requirements.

## Testing Levels

1. **Manual testing in Claude.ai** — Run queries directly and observe behavior. Fast iteration, no setup.
2. **Scripted testing in Claude Code** — Automate test cases for repeatable validation.
3. **Programmatic testing via Skills API** — Build evaluation suites for systematic testing.

## Pro Tip

Iterate on a single challenging task until Claude succeeds, then extract the winning approach into a skill. This provides faster signal than broad testing. Once you have a working foundation, expand to multiple test cases.

## Three Testing Areas

### 1. Triggering Tests

**Goal:** Skill loads at the right times.

Default to 3 eval scenarios total (1 positive, 1 negative, 1 edge case). Only add more if the user explicitly requests broader coverage.

```
Should trigger:
- "[obvious request matching skill purpose]"

Should NOT trigger:
- "[unrelated topic with closest false-positive risk]"

Edge case:
- "[ambiguous query near the trigger boundary]"
```

### 2. Functional Tests

**Goal:** Skill produces correct outputs.

```
Test: [Describe the scenario]
Given: [Input/context]
When: Skill executes workflow
Then:
  - [Expected output 1]
  - [Expected output 2]
  - No errors
```

### 3. Performance Comparison

**Goal:** Prove the skill improves results vs. baseline.

Compare:
- Number of back-and-forth messages (fewer is better)
- Failed API calls requiring retry (zero is ideal)
- Token consumption (lower is better)
- Whether the user needs to correct Claude (never is ideal)

## Iteration Signals

### Under-Triggering (skill doesn't load when it should)

**Signals:** Users manually enabling it, support questions about when to use it.

**Fix:** Add more trigger phrases to the description, include relevant keywords and technical terms.

### Over-Triggering (skill loads for unrelated queries)

**Signals:** Users disabling it, skill loads for wrong topics.

**Fix:** Add negative triggers ("Do NOT use for..."), be more specific about scope.

### Execution Issues (skill loads but doesn't work well)

**Signals:** Inconsistent results, API failures, user corrections needed.

**Fix:** Improve instructions, add error handling, use scripts for critical validations.

## Debugging Approach

Ask Claude: "When would you use the [skill name] skill?" — Claude will quote the description back, revealing what's missing or overly broad.

## Success Criteria

Define how you'll know your skill is working. These are aspirational targets — rough benchmarks, not precise thresholds.

### Quantitative
- Skill triggers on ~90% of relevant queries (test with 10–20 queries)
- Completes workflow in expected number of tool calls (compare with and without skill)
- 0 failed API calls per workflow (monitor MCP server logs during tests)

### Qualitative
- Users don't need to prompt Claude about next steps
- Workflows complete without user correction
- Consistent results across sessions

## Evaluation-Driven Development

Build evaluations BEFORE writing extensive documentation:

1. Create evaluation criteria first
2. Establish baseline performance without the skill
3. Write minimal instructions to pass evaluations
4. Iterate based on real gaps, not assumptions

This prevents over-engineering your skill with instructions that don't improve outcomes.

## Context Budget

Skill descriptions are loaded into Claude's context at startup. With many skills, descriptions may exceed the character budget.

- Budget scales dynamically at **1% of context window** (fallback: 8,000 characters)
- Individual descriptions are truncated at ~250 characters in skill listings
- Run `/context` to check for warnings about excluded skills
- Override with: `export SLASH_COMMAND_TOOL_CHAR_BUDGET=32000`
- If budget exceeded: shorten descriptions, reduce enabled skills, or use skill "packs" for related capabilities
