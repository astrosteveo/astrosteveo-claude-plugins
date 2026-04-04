---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, or applications. Generates creative, polished code that avoids generic AI aesthetics.
---

# Frontend Design

Create distinctive, production-grade frontend interfaces. Every component should feel
intentionally designed — not assembled from generic templates.

## Hard Rules

These rules are non-negotiable. Violating any of them is a failure.

### NEVER use card-based layouts

Cards are the most overused pattern in AI-generated UI. They make everything look like
a dashboard template from 2019. Do NOT use them. This means:

- No rectangular containers with rounded corners, padding, and shadow used to group
  content into repeated uniform blocks
- No grid-of-boxes layouts where each box has a heading, body text, and optional icon
- No "card components" regardless of what they are called — even if named "tile",
  "panel", "block", "item", or "cell", if the result is visually a card, it is banned
- No card-like patterns in any disguise: bordered boxes with internal padding arranged
  in a repeating grid or list are cards

Instead of cards, use:

- **Tables** — for comparing structured data across rows
- **Inline lists** — horizontal or vertical arrangements without bounding boxes
- **Typography-driven layouts** — use size, weight, color, and spacing to create
  hierarchy without containers
- **Divided sections** — subtle horizontal rules, alternating backgrounds, or spatial
  grouping
- **Magazine/editorial layouts** — asymmetric grids, mixed media, varied content sizes
- **Accordion/disclosure patterns** — progressive reveal without boxing content
- **Tag/chip clusters** — for categories, filters, metadata
- **Timeline/feed layouts** — for sequential or chronological content
- **Canvas/freeform layouts** — for creative or spatial interfaces

If a design brief seems to demand cards, rethink the information architecture. There is
always a better alternative.

### No generic AI aesthetics

Avoid the telltale signs of AI-generated UI:

- No gratuitous gradients on every surface
- No oversized hero sections with vague placeholder text
- No uniform icon grids (icon + label + description, repeated 3-6 times)
- No "clean and modern" as a design goal — it means nothing
- No default component library styling without customization
- No symmetry for symmetry's sake — intentional asymmetry creates interest

### Accessibility is mandatory

Every component must meet WCAG 2.1 AA as a baseline:

- Color contrast ratios: 4.5:1 for normal text, 3:1 for large text
- All interactive elements are keyboard-navigable
- Semantic HTML elements used correctly (nav, main, article, section, button vs. div)
- ARIA attributes where semantic HTML is insufficient
- Focus indicators that are visible and distinct
- Form inputs have associated labels
- Images have meaningful alt text (or empty alt for decorative)

### Performance by default

- Prefer CSS over JavaScript for visual effects (transitions, animations, hover states)
- Use CSS Grid and Flexbox — no float-based layouts
- Lazy-load images and heavy assets below the fold
- Minimize DOM depth — deeply nested wrappers are a code smell

## Design Principles

### 1. Start from content, not containers

Read the content first. Let the information structure dictate the layout. If you reach
for a container before understanding what goes in it, you are designing wrong.

### 2. Typography is the primary design tool

80% of the web is text. Good typography carries a design:

- Establish a clear type scale (no more than 5-6 distinct sizes)
- Use font weight and color to create hierarchy, not just size
- Set comfortable line lengths (45-75 characters for body text)
- Use consistent vertical rhythm (line-height and margin relationships)

### 3. Whitespace is structure

Generous, intentional whitespace separates groups, establishes hierarchy, and gives
content room to breathe. Cramped layouts signal amateur work. Use spacing scales
(4px/8px/16px/24px/32px/48px/64px) for consistency.

### 4. Color with purpose

- Define a small palette: 1-2 primary colors, 1-2 neutrals, 1 accent
- Use color to convey meaning (status, emphasis, grouping) not decoration
- Dark mode is not "invert everything" — it requires its own palette tuning
- Avoid pure black (#000) on pure white (#fff) — use near-black and near-white for
  softer contrast

### 5. Motion with intent

Animation should communicate, not entertain:

- Micro-interactions: feedback on user actions (button press, toggle switch)
- Transitions: smooth state changes (page navigation, expanding content)
- Keep durations short: 150-300ms for micro-interactions, 300-500ms for transitions
- Use easing curves, never linear timing for UI motion
- Respect prefers-reduced-motion

### 6. Distinctive means opinionated

Generic designs come from avoiding decisions. Distinctive designs come from making bold,
specific choices:

- Pick a strong typographic voice — not just system fonts
- Commit to a layout philosophy (dense vs. spacious, symmetric vs. asymmetric)
- Use a color palette that could not belong to any other project
- Let the content's nature drive the UI patterns — a recipe app should not look like a
  SaaS dashboard

## Workflow

### Step 1: Understand the brief

Before writing any code:

1. Identify the content types — what data and text will be displayed?
2. Identify the user tasks — what actions will users take?
3. Identify the mood/brand — what should this feel like?
4. Identify constraints — responsive requirements, framework, existing design system?

If any of these are unclear, ask. Do not guess and produce something generic.

### Step 2: Choose layout strategy

Based on the content and tasks, select layout patterns. Reference the alternatives
listed in the card ban above. Mix patterns — a page rarely uses just one.

Think about information density:
- High density (data tables, dashboards): tight spacing, smaller type, dense grids
- Medium density (content sites, apps): balanced spacing, readable type
- Low density (landing pages, portfolios): generous spacing, large type, dramatic visuals

### Step 3: Build the type system first

Before touching layout, define:

- Font families (1-2 maximum)
- Type scale (size, weight, line-height for each level)
- Color tokens (foreground, background, accent, muted, border)

This creates the foundation everything else builds on.

### Step 4: Implement with semantic HTML

Write the HTML structure first using semantic elements. Then layer on styling.
Component structure should reflect content hierarchy, not visual hierarchy.

### Step 5: Style with CSS

Use modern CSS:

- Custom properties for design tokens
- Grid and Flexbox for layout
- Container queries where appropriate
- Logical properties (inline/block) for internationalization readiness
- Layer cascade with @layer when complexity warrants it

### Step 6: Add interactivity

Add JavaScript only for behavior that CSS cannot handle:

- State management
- Data fetching
- Complex interactions (drag and drop, virtual scrolling)
- Form validation beyond HTML5 constraints

### Step 7: Review against rules

Before delivering, verify:

1. Zero card patterns anywhere in the output
2. No generic AI aesthetic markers
3. WCAG 2.1 AA compliance
4. Keyboard navigation works
5. Responsive behavior at mobile/tablet/desktop breakpoints
6. Page loads and renders without layout shift

## Framework Guidance

When the user specifies a framework, follow its conventions:

- **React/Next.js** — functional components, hooks, CSS Modules or styled-components
- **Vue** — Composition API, scoped styles, single-file components
- **Svelte** — component-scoped styles, minimal boilerplate
- **Plain HTML/CSS** — vanilla JS only when needed, no jQuery
- **Tailwind** — use utility classes directly, avoid @apply for simple styles

When no framework is specified, default to plain HTML + CSS + minimal JS. This produces
the most portable, understandable output.

## Examples

### Example 1: Feature comparison page

Bad approach (card-based):
Three identical cards in a row, each with an icon, title, and bullet list.

Better approach:
A structured comparison table with clear column headers, alternating row backgrounds,
and highlighted recommended option. Feature differences called out with inline
badges rather than identical card layouts.

### Example 2: Team/people page

Bad approach (card-based):
Grid of cards with circular avatar, name, title.

Better approach:
Editorial layout — large feature photo of the first person with a pull quote,
then a compact list-style layout for the rest with small inline avatars, names as
links, and role as muted secondary text. Varies the presentation to reflect
the actual hierarchy or narrative.

### Example 3: Pricing page

Bad approach (card-based):
Three pricing cards side by side with headers, price, feature lists, and CTA buttons.

Better approach:
A comparison table with sticky headers, grouped feature rows, and a highlighted
column for the recommended plan. Price displayed prominently in the header row.
Toggle between monthly/annual above the table. Mobile: stacked sections with
disclosure triangles for feature details.
