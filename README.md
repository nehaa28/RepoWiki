# RepoWiki — Turn Any Codebase Into a Knowledge Hub

> **Two ways to document your code: instant via Claude's `/create-readme` skill, or full offline site via the Python library.**

---

## Problem Statement

Every developer has faced this: you land in an unfamiliar codebase and there's no map.

- No architecture overview — where does the flow start?
- Outdated or missing documentation
- No glossary for domain-specific terms
- Tribal knowledge locked in teammates' heads

Writing documentation from scratch is slow and goes stale. **RepoWiki solves this with two complementary tools built in this repo.**

---

## Two Approaches, One Goal

```
┌─────────────────────────────────────────────┐     ┌─────────────────────────────────────────────┐
│        Approach 1 — Claude Skill            │     │       Approach 2 — Python Library           │
│                                             │     │                                             │
│  Developer types /create-readme             │     │  python -m projwiki ./myrepo                │
│                 │                           │     │                 │                           │
│                 ▼                           │     │                 ▼                           │
│  Claude reads codebase files                │     │  AST parser + AI summarizer                 │
│                 │                           │     │  (optional SAP AI Core)                     │
│                 ▼                           │     │                 │                           │
│  Generates README.md with                   │     │                 ▼                           │
│  inline Mermaid diagrams                    │     │  Full HTML site:                            │
│                                             │     │  index, files, diagrams, glossary           │
└──────────────────┬──────────────────────────┘     └──────────────────┬──────────────────────────┘
                   │                                                    │
                   └────────────────────┬───────────────────────────────┘
                                        ▼
                           ┌────────────────────────────┐
                           │  Any codebase →            │
                           │  Browsable knowledge hub   │
                           └────────────────────────────┘
```

| | `create-claude-skill/` | `py-implementation/` |
|---|---|---|
| **What it produces** | Single `README.md` | Full static HTML site |
| **Diagrams** | Mermaid (GitHub-native) | PlantUML `.puml` files |
| **Requires Claude** | ✅ Yes (Claude Code) | ❌ No |
| **Requires Python** | ❌ No | ✅ Yes (3.8+) |
| **AI optional?** | N/A | ✅ Offline fallback built-in |
| **Best for** | Quick README, any language | Deep docs, Python projects |

---

## Folder Structure

```
prj1/
├── create-claude-skill/         ← Approach 1: Claude Code slash-command skill
│   ├── README.md                ← How to install and use the skill
│   └── .claude/
│       └── skills/
│           └── create-readme.md ← The skill definition (install this)
│
├── py-implementation/           ← Approach 2: Python CLI + library (RepoWiki / ProjWiki)
│   ├── README.md                ← Full usage docs
│   ├── projwiki/                ← Main Python package
│   │   ├── cli/                 ← Click CLI entry point
│   │   ├── parser/              ← AST code analysis
│   │   ├── ai/                  ← SAP AI Core summarizer (optional)
│   │   ├── diagram/             ← PlantUML diagram generator
│   │   └── generator/           ← Static HTML site builder
│   ├── example_usage.py         ← Programmatic API example
│   ├── requirements.txt
│   └── setup.py
│
└── README.md                    ← This file
```

---

## Approach 1 — Claude Code Skill (`create-claude-skill/`)

A single `.md` skill file you install once into Claude Code. After that, `/create-readme` works in any project, any language.

### What It Generates

- Problem statement + solution summary (inferred from code)
- Architecture diagram — Mermaid flowchart (renders on GitHub/GitLab natively)
- Data flow / sequence diagram — Mermaid
- Module dependency graph — Mermaid
- Installation, usage, config, commands reference
- Troubleshooting section (derived from error handling in the code)
- Security section if credentials or secrets are present

### Install

```bash
# Windows
copy create-claude-skill\.claude\skills\create-readme.md "%USERPROFILE%\.claude\skills\create-readme.md"

# macOS / Linux
cp create-claude-skill/.claude/skills/create-readme.md ~/.claude/skills/create-readme.md
```

Restart Claude Code, then navigate to any project and run:

```
/create-readme
```

### Why Mermaid?

```
┌──────────────────────┐                         ┌──────────────────────┐
│   Mermaid diagrams   │                         │  PlantUML diagrams   │
└──────────┬───────────┘                         └──────────┬───────────┘
           │                                                │
     ┌─────┴──────┐                                  ┌─────┴──────┐
     ▼            ▼                                  ▼            ▼
┌─────────┐  ┌─────────┐                       ┌─────────┐  ┌─────────┐
│ GitHub  │  │ GitLab  │                       │ GitHub  │  │ GitLab  │
│         │  │         │                       │         │  │         │
│ ✅      │  │ ✅      │                       │ ❌      │  │ ❌      │
│ Renders │  │ Renders │                       │ Raw     │  │ Plugin  │
│ natively│  │ natively│                       │ text    │  │ required│
└─────────┘  └─────────┘                       └─────────┘  └─────────┘
```

Mermaid renders directly in GitHub and GitLab with zero reader setup — no Java, no copy-pasting into plantuml.com. The skill generates **Mermaid only**.

---

## Approach 2 — Python Library (`py-implementation/`)

A full Python CLI + library that walks any codebase, optionally calls an LLM, and outputs a self-contained, browsable HTML documentation site — **no internet required at read time**.

### Architecture

```
┌────────────┐     ┌──────────────────────┐
│    CLI     │────▶│       Parser         │
│            │     │                      │
│ projwiki   │     │ • AST analysis       │
│ ./myrepo   │     │ • imports / classes  │
└────────────┘     │ • docstrings         │
                   │ • tech stack         │
                   └──────────┬───────────┘
                              │
               ┌──────────────┴──────────────┐
               ▼                             ▼
┌──────────────────────┐       ┌──────────────────────┐
│      AI Layer        │       │    Diagram Engine    │
│      (optional)      │       │                      │
│ • SAP AI Core        │       │ • PlantUML rules     │
│ • OAuth2 + LLM       │       │ • swimlane / seq     │
│                      │       │ • component / class  │
└──────────┬───────────┘       └──────────┬───────────┘
           │                              │
           └──────────────┬───────────────┘
                          ▼
           ┌──────────────────────────┐
           │       Site Builder       │
           │                          │
           │ • Jinja2 templates       │
           │ • index.html             │
           │ • files.html             │
           │ • diagrams.html          │
           │ • glossary.html          │
           └──────────────┬───────────┘
                          │
                          ▼
           ┌──────────────────────────┐
           │  output/YYYY-MM-DD_      │
           │  HH-MM-SS/               │
           │  (timestamped per run)   │
           └──────────────────────────┘
```

### Quick Start

```bash
cd py-implementation

# Install dependencies
pip install -r requirements.txt

# Run on any folder (offline — no AI)
python -m projwiki /path/to/your/repo --offline

# Run with AI summaries (requires SAP AI Core credentials in .env)
python -m projwiki /path/to/your/repo

# Open the output
start output/index.html        # Windows
open output/index.html         # macOS
```

### Install as CLI Tool

```bash
cd py-implementation
pip install -e .

# Then from anywhere:
projwiki /path/to/repo --offline
```

### AI Setup (optional)

Copy `.env.example` to `.env` and fill in SAP AI Core credentials:

```env
AICORE_AUTH_URL=https://<subdomain>.authentication.<region>.hana.ondemand.com
AICORE_CLIENT_ID=<your-client-id>
AICORE_CLIENT_SECRET=<your-client-secret>
AICORE_BASE_URL=https://api.ai.<region>.aws.ml.hana.ondemand.com
AICORE_RESOURCE_GROUP=default
```

Without credentials, use `--offline`. All parse, diagram, and site-building features still work.

### Programmatic API

```python
from pathlib import Path
from projwiki.parser.analyzer import CodebaseAnalyzer
from projwiki.diagram.generator import DiagramGenerator
from projwiki.generator.site_builder import SiteBuilder

analyzer = CodebaseAnalyzer(Path("./myrepo"), max_depth=5)
analysis = analyzer.analyze()

diagram_gen = DiagramGenerator(analysis)
diagrams = diagram_gen.generate_all()

builder = SiteBuilder(Path("./output"))
builder.build(analysis, diagrams, summaries=None)
```

### Tech Stack

| Layer | Library | License |
|-------|---------|---------|
| Parsing | `ast` (stdlib) | PSF |
| Graph analysis | `networkx` | BSD-3 |
| Templating | `Jinja2` | BSD-3 |
| CLI | `click` | BSD-3 |
| Terminal UI | `rich` | MIT |
| HTTP | `requests` | Apache-2.0 |
| Config | `pyyaml` | MIT |
| AI (optional) | SAP AI Core | Commercial |
| Diagrams | PlantUML (text) | MIT |

All runtime dependencies are open source. No proprietary libraries required for core features.

---

## Choosing the Right Approach

```
                         ┌─────────────────────────┐
                         │   Do you use            │
                         │   Claude Code?          │
                         └────────────┬────────────┘
                                      │
                   ┌──────────────────┴──────────────────┐
                  Yes                                    No
                   │                                     │
                   ▼                                     ▼
    ┌──────────────────────────┐          ┌──────────────────────────────┐
    │  Do you want a full      │          │    Use the Python Library    │
    │  HTML docs site?         │          │    py-implementation/        │
    └────────────┬─────────────┘          │    → projwiki ./repo         │
                 │                        └──────────────────────────────┘
        ┌────────┴────────┐
       Yes               No
        │                 │
        ▼                 ▼
┌───────────────┐   ┌─────────────────────┐
│  Use Python   │   │  Python project?    │
│  Library      │   └──────────┬──────────┘
│  py-impl/     │              │
│  → projwiki   │       ┌──────┴──────┐
│    ./repo     │      Yes           No
└───────────────┘       │             │
                        ▼             ▼
              ┌─────────────────────────────┐
              │     Use the Claude Skill    │
              │     create-claude-skill/    │
              │     → /create-readme        │
              │     (works on any language) │
              └─────────────────────────────┘
```

---

## Contributing

- `create-claude-skill/` — Improve the skill definition in `.claude/skills/create-readme.md`
- `py-implementation/` — Add parsers, diagram types, or new HTML pages in `projwiki/`

---

## License

MIT — see individual sub-folders for details.
