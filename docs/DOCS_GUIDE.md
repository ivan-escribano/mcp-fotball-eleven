# Docs Guide — How to structure documentation

Every major version of the project gets its own folder: `v1/`, `v2/`, `v3/`, etc.

## Folder structure (same for every version)

```
docs/
├── DOCS_GUIDE.md              ← This file (shared across versions)
├── v1/
├── v2/
│   ├── specs/                 What to build (feature specifications)
│   ├── plans/                 How to build it (implementation plans)
│   ├── explanations/          Deep dives on how things work
│   ├── improvements/          What changed and why
│   ├── images/                Diagrams, screenshots, demo videos
│   └── changelog.md           Log of everything done in this version
└── v3/                        (same folders)
```

## Naming conventions

| Folder | File naming | Example |
|--------|------------|---------|
| `specs/` | `<feature-name>.md` | `mcp-eleven-specs-v2.md` |
| `plans/` | `<NN>-<feature-name>.md` | `01-player-context.md` |
| `explanations/` | `<topic>.md` | `why-mcp-prompt-not-working.md` |
| `improvements/` | `<NN>-<description>.md` | `01-search-improvements.md` |
| `images/` | Subfolders as needed | `demo/`, `diagrams/` |

- Plans are numbered (`01-`, `02-`...) to keep order
- Improvements are numbered to track sequence
- Use kebab-case for all file names
- One topic per file, keep them focused

## When to create a new version

Create `v3/` (or next) when:
- You start a new major phase of the project
- The scope or architecture changes significantly
- You want a clean slate for planning

Previous versions stay as-is for reference.

## changelog.md format

```markdown
# vN Changelog

| Date       | Spec | Change |
|------------|------|--------|
| YYYY-MM-DD | NN   | Brief description of what was done |
```
