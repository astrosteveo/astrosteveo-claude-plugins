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

Design test cases:
```
Should trigger:
- "[obvious request matching skill purpose]"
- "[paraphrased version of the request]"
- "[another variation]"

Should NOT trigger:
- "[unrelated topic]"
- "[similar but out-of-scope request]"
- "[request for a different skill]"
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
