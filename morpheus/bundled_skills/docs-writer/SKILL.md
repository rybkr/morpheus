---
name: docs-writer
description: Write and revise clear, accurate, task-oriented documentation for software projects. Use when your agent needs to create or improve README files, setup guides, CLI docs, onboarding docs, feature docs, troubleshooting guides, migration notes, or other developer/user documentation where correctness, usefulness, and maintainability matter.
---

# Docs Writer

Write documentation that helps a reader complete a task with minimal confusion.

## Workflow

1. Inspect the code, commands, config, and existing docs before drafting. Do not invent behavior, flags, file paths, or workflows.
2. Identify the document's audience and job:
   - onboarding and installation
   - task execution
   - feature explanation
   - troubleshooting
   - migration or release notes
3. Gather the facts that matter most:
   - prerequisites
   - exact commands
   - expected inputs and outputs
   - important constraints, defaults, and failure cases
4. Organize for fast scanning:
   - start with the task or purpose
   - keep prerequisites near the top
   - present steps in the order the reader performs them
   - separate reference material from procedural steps
5. Prefer concrete examples over abstract explanation. Use real command names, paths, flags, and sample outputs when verified.
6. Keep the tone direct and plain. Remove filler, marketing language, and repeated context.
7. Verify consistency after writing:
   - commands match the codebase
   - file paths and env vars exist
   - headings reflect the actual content
   - links and cross-references are correct

## Writing Rules

- Prefer imperative, task-oriented headings such as `Install`, `Run locally`, `Configure auth`, `Troubleshoot startup failures`.
- State assumptions explicitly when they affect outcomes.
- Put important warnings immediately before the step they affect.
- Explain why only when it helps the reader avoid a mistake or choose between options.
- Keep examples minimal but runnable.
- Preserve existing project terminology unless it is clearly wrong or inconsistent.

## Accuracy Rules

- Re-read source material before documenting nuanced behavior.
- If behavior cannot be verified locally, say what is confirmed and what remains uncertain.
- When multiple workflows exist, label who each workflow is for and when to use it.
- When editing existing docs, keep valid context that users still need; do not compress away critical setup or caveats.

## Common Patterns

### README or landing doc

- Lead with what the project does.
- Follow with the fastest path to first success.
- Link out to deeper reference material instead of overloading the top-level file.

### Setup or install guide

- List prerequisites first.
- Separate install, configuration, and verification.
- Include a clear success check.

### CLI or command docs

- Show command shape, required inputs, common examples, and notable failure modes.
- Prefer grouped examples by task instead of alphabetized flag dumps when possible.

### Troubleshooting guide

- Organize by symptom.
- For each issue, give likely cause, how to verify it, and how to fix it.

### Migration notes

- State who must act.
- Show what changed, why it matters, and exactly what actions are required.
- Call out breaking changes early.

## Completion Checklist

- Confirm the doc matches the current code and repo structure.
- Remove stale steps, dead links, and ambiguous wording.
- Make the first successful path obvious.
- Leave the document easier to maintain than before.
