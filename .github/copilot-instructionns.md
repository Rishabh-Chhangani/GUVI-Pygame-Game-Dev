# Ninja Collector Development Instructions

## General
- Work as a project-level development assistant.
- I understand the overall architecture and programming fundamentals.
- Do not explain basic Python syntax unless explicitly asked.
- Before making significant changes, explain what part of the architecture is affected and why.
- Prefer small, targeted changes over unnecessary rewrites or redesigns.
- Preserve the existing architecture unless there is a clear reason to change it.
- Inspect the existing code before proposing changes.

## Development
- Use pygame-ce 2.5.8.
- Follow the existing project structure and naming conventions.
- Keep configuration values in `src/config.py` where appropriate.
- Use the existing `AssetManager` for asset loading.
- Keep game lifecycle responsibilities in `Game`.
- Keep entity-specific behavior inside the relevant entity modules.
- Avoid duplicating existing systems.

## Debugging
- Identify the root cause before modifying code.
- Explain significant architectural or behavioral implications of fixes.
- Do not rewrite unrelated code while fixing a bug.

## AI Assistance
- Do not blindly generate large amounts of code.
- For non-trivial features, first describe the implementation approach and affected files.
- When code is changed, explain the important decisions rather than explaining every line.