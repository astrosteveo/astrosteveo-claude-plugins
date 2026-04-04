# Skill Design Patterns

These patterns emerged from skills created by early adopters and internal teams. Choose the one that best fits your skill's purpose.

## Choosing Your Approach

- **Problem-first:** "I need to set up a project workspace" — the skill orchestrates the right calls in the right sequence. Users describe outcomes; the skill handles the tools.
- **Tool-first:** "I have Linear MCP connected" — the skill teaches Claude the optimal workflows. Users have access; the skill provides expertise.

## Skill Categories

### Category 1: Document & Asset Creation

Output is a file, design, or artifact. Uses Claude's built-in capabilities.

**Key techniques:**
- Embedded style guides and brand standards
- Template structures for consistent output
- Quality checklists before finalizing
- No external tools required

### Category 2: Workflow Automation

Multi-step process with validation gates. May coordinate across tools.

**Key techniques:**
- Step-by-step workflow with validation gates
- Templates for common structures
- Built-in review and improvement suggestions
- Iterative refinement loops

### Category 3: MCP Enhancement

Workflow guidance layered on top of MCP tool access.

**Key techniques:**
- Coordinates multiple MCP calls in sequence
- Embeds domain expertise
- Provides context users would otherwise need to specify
- Error handling for common MCP issues

## Pattern 1: Sequential Workflow Orchestration

**Use when:** Users need multi-step processes in a specific order.

```markdown
## Workflow: Onboard New Customer

### Step 1: Create Account
Call MCP tool: `create_customer`
Parameters: name, email, company

### Step 2: Setup Payment
Call MCP tool: `setup_payment_method`
Wait for: payment method verification

### Step 3: Create Subscription
Call MCP tool: `create_subscription`
Parameters: plan_id, customer_id (from Step 1)
```

**Key techniques:** Explicit step ordering, dependencies between steps, validation at each stage, rollback instructions for failures.

## Pattern 2: Multi-MCP Coordination

**Use when:** Workflows span multiple services.

```markdown
### Phase 1: Design Export (Figma MCP)
1. Export design assets
2. Generate specifications
3. Create asset manifest

### Phase 2: Asset Storage (Drive MCP)
1. Create project folder
2. Upload assets
3. Generate shareable links

### Phase 3: Task Creation (Linear MCP)
1. Create development tasks
2. Attach asset links
3. Assign to team
```

**Key techniques:** Clear phase separation, data passing between MCPs, validation before next phase, centralized error handling.

## Pattern 3: Iterative Refinement

**Use when:** Output quality improves with iteration.

```markdown
### Initial Draft
1. Fetch data via MCP
2. Generate first draft
3. Save to temporary file

### Quality Check
1. Run validation script: `scripts/check_report.py`
2. Identify issues

### Refinement Loop
1. Address each issue
2. Regenerate affected sections
3. Re-validate
4. Repeat until quality threshold met
```

**Key techniques:** Explicit quality criteria, iterative improvement, validation scripts, know when to stop iterating.

## Pattern 4: Context-Aware Tool Selection

**Use when:** Same outcome, different tools depending on context.

```markdown
### Decision Tree
1. Check file type and size
2. Determine best location:
   - Large files (>10MB): cloud storage MCP
   - Collaborative docs: Notion/Docs MCP
   - Code files: GitHub MCP
   - Temporary files: local storage

### Execute
Based on decision, call appropriate tool with service-specific metadata.

### Explain
Tell the user why that storage was chosen.
```

**Key techniques:** Clear decision criteria, fallback options, transparency about choices.

## Pattern 5: Domain-Specific Intelligence

**Use when:** The skill adds specialized knowledge beyond tool access.

```markdown
### Before Processing (Compliance Check)
1. Fetch details via MCP
2. Apply compliance rules
3. Document decision

### Processing
IF compliance passed: process and apply checks
ELSE: flag for review, create case

### Audit Trail
- Log all checks
- Record decisions
- Generate audit report
```

**Key techniques:** Domain expertise embedded in logic, compliance before action, comprehensive documentation, clear governance.

## Pattern 6: Plan-Validate-Execute

**Use when:** Complex operations where mistakes are costly and verification matters.

```markdown
### Plan Phase
1. Analyze requirements
2. Generate structured execution plan
3. Save plan to temporary file

### Validate Phase
1. Run validation script: `scripts/validate-plan.py`
2. Check for: missing steps, invalid parameters, dependency conflicts
3. Present plan to user for approval

### Execute Phase
1. Execute each step from the validated plan
2. Verify output at each stage
3. Log results for audit trail
```

**Key techniques:** Structured plan output, script-based validation before execution, user confirmation gate, step-by-step verification.

## MCP Tool Naming

When referencing MCP tools in skill instructions, use **fully qualified names** in the format `ServerName:tool_name`. This avoids "tool not found" errors when multiple MCP servers are available.

```markdown
# Good — unambiguous
Use Linear:create_issue to file the bug.
Call BigQuery:bigquery_schema to retrieve table schemas.

# Risky — ambiguous if multiple servers provide similar tools
Use the create_issue tool to file the bug.
```

## Subagent Execution with context: fork

Skills can run in an isolated subagent using frontmatter:

```yaml
context: fork
agent: Explore    # or Plan, general-purpose
```

The skill content becomes the subagent's task prompt. The subagent does not have access to conversation history but does receive CLAUDE.md context.

**Important:** `context: fork` only works for skills with explicit task instructions. Skills containing only guidelines (e.g., "follow these API conventions") won't produce useful results — the subagent needs an actionable prompt.
