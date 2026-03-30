# RepoWiki

> **Drop a repo → get a browsable, explorable knowledge hub. No internet required.**

---

## Problem Statement

When developers join a new project, they face a consistent wall:

- **No architecture overview** — where does the flow start? what calls what?
- **Scattered or outdated docs** — README says one thing, code does another
- **No glossary** — domain terms and class names are unexplained
- **Tribal knowledge** — understanding is locked in teammates' heads

Reading raw source files to reverse-engineer a system is slow, error-prone, and doesn't scale.

**RepoWiki solves this by analysing any codebase and auto-generating a self-contained, offline documentation site** — complete with architecture diagrams, file summaries, dependency maps, and a glossary — in one CLI command. No AI credentials needed for the core features.

---

## How It Works

```
Your Codebase
     │
     ▼
┌─────────────┐     ┌──────────────┐     ┌───────────────────┐     ┌──────────────────┐
│   Parser    │────▶│  AI Layer    │────▶│  Diagram Engine   │────▶│  Site Builder    │
│             │     │  (optional)  │     │                   │     │                  │
│ • AST parse │     │ • File summ. │     │ • Rule engine     │     │ • index.html     │
│ • imports   │     │ • Glossary   │     │ • Swimlane/seq/   │     │ • files.html     │
│ • classes   │     │ • Overview   │     │   component/class │     │ • diagrams.html  │
│ • docstrings│     │ (SAP AI Core)│     │ • Topo sort       │     │ • glossary.html  │
│ • tech stack│     │              │     │ • FAQ-safe output │     │ • README.md      │
└─────────────┘     └──────────────┘     └───────────────────┘     └──────────────────┘
                                                                            │
                                                                            ▼
                                                                   output/2026-03-30_20-43/
                                                                   (timestamped per run)
```

> The name "RepoWiki" reflects the goal: turn any git repository into its own Wikipedia.

---

## Folder Structure

```
repowiki/
│
├── projwiki/                        # Main package (rename folder to repowiki if publishing)
│   │
│   ├── __init__.py                  # Package entry, exports
│   ├── __main__.py                  # python -m projwiki entry point
│   │
│   ├── cli/
│   │   ├── __init__.py
│   │   └── main.py                  # Click CLI — parses args, orchestrates pipeline
│   │
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── analyzer.py              # Walks directory, builds full analysis dict
│   │   └── file_parser.py           # Per-file AST parse: classes, functions, docstrings
│   │
│   ├── ai/
│   │   ├── __init__.py
│   │   └── summarizer.py            # SAP AI Core OAuth2 + LLM calls (optional)
│   │
│   ├── diagram/
│   │   ├── __init__.py
│   │   └── generator.py             # Rule engine → PlantUML source for each diagram type
│   │
│   └── generator/
│       ├── __init__.py
│       └── site_builder.py          # Renders HTML pages + README.md from analysis data
│
├── output/                          # Generated docs (gitignored)
│   └── YYYY-MM-DD_HH-MM-SS/         # One folder per run (timestamped)
│       ├── index.html               # Project overview
│       ├── files.html               # Per-file details with classes/functions
│       ├── diagrams.html            # Links to PlantUML sources
│       ├── glossary.html            # Auto-extracted terms
│       ├── README.md                # Full technical markdown report
│       ├── data.json                # Raw analysis data (reusable)
│       ├── assets/
│       │   ├── style.css
│       │   └── main.js
│       └── diagrams/
│           ├── workflow.puml        # Swimlane or sequence diagram
│           ├── dependency.puml      # Component dependency arrows
│           ├── classes.puml         # Class diagram (OOP-heavy projects)
│           └── structure.puml       # Folder/file tree
│
├── example_usage.py                 # Programmatic API example
├── requirements.txt                 # Runtime dependencies
├── setup.py                         # Package install config
└── README.md                        # This file
```

---

## Tech Stack

| Layer | Library | Purpose | License |
|-------|---------|---------|---------|
| Language | Python 3.8+ | Core runtime | PSF |
| Parsing | `ast` (stdlib) | AST extraction — no deps | PSF |
| Graph analysis | `networkx` | Topological sort for diagram ordering | BSD-3 |
| Templating | `Jinja2` | HTML generation | BSD-3 |
| CLI | `click` | Argument parsing, flags | BSD-3 |
| Terminal UI | `rich` | Coloured output, progress spinner | MIT |
| HTTP | `requests` | SAP AI Core OAuth2 token + LLM calls | Apache-2.0 |
| Config | `pyyaml` | YAML utility parsing | MIT |
| Diagrams | PlantUML (text) | `.puml` source files, no binary dep | MIT |
| AI (optional) | SAP AI Core | LLM summarisation (offline fallback built-in) | Commercial |

---

## Installation

```bash
# 1. Clone
git clone https://github.com/yourusername/repowiki.git
cd repowiki

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Install as CLI tool
pip install -e .
```

### AI Features Setup (optional)

AI-powered file summaries require SAP AI Core credentials. Without them, use `--offline` — all other features still work.

```bash
# macOS / Linux
cp .env.example .env

# Windows
copy .env.example .env
```

Open `.env` and fill in your values:

```env
AICORE_AUTH_URL=https://<your-subdomain>.authentication.<region>.hana.ondemand.com
AICORE_CLIENT_ID=<your-client-id>
AICORE_CLIENT_SECRET=<your-client-secret>
AICORE_BASE_URL=https://api.ai.<region>.aws.ml.hana.ondemand.com
AICORE_RESOURCE_GROUP=default
```

> `.env` is listed in `.gitignore` — your credentials will never be committed. Never commit `.env` directly or paste real keys into `.env.example`.

---

## Commands

```bash
# Analyse a project — offline mode (no AI, all features except LLM summaries)
python -m projwiki ./my-project --offline

# Analyse with AI summaries (requires SAP AI Core credentials in .env)
python -m projwiki ./my-project

# Control traversal depth (default: 5)
python -m projwiki ./my-project --depth 3

# Custom output directory (timestamped subfolder auto-appended)
python -m projwiki ./my-project --output ./docs

# Installed as CLI tool
repowiki ./my-project --offline
```

Output is always written to `<output-dir>/YYYY-MM-DD_HH-MM-SS/` so runs never overwrite each other.

**Open in browser:**
```bash
# Windows
start output\2026-03-30_20-43-15\index.html

# macOS / Linux
open output/2026-03-30_20-43-15/index.html
```

---

## Architecture Diagrams

Four diagram types are generated; the rule engine selects the right flow type automatically:

| Diagram | When generated | PlantUML type |
|---------|---------------|---------------|
| **Workflow** (swimlane) | Default — projects with multiple functional layers | Activity diagram |
| **Sequence** | Small projects (≤ 6 files) with a single linear entry point | Sequence diagram |
| **Dependency** | Always — module-level import arrows | Component diagram |
| **Classes** | When classes ≥ 40% of modules (OOP-heavy) | Class diagram |
| **Structure** | Always — folder/file tree | Deployment diagram |

Render any `.puml` file online at [plantuml.com/plantuml](https://www.plantuml.com/plantuml/uml/) or with a VS Code PlantUML extension.

**PlantUML rules respected** (FAQ-safe output):
- Swimlane partition declared before `start`
- `note right` never emitted across lane boundaries
- Empty notes suppressed
- `left to right direction` only in component/class diagrams
- Special characters sanitized in identifiers and labels
- `linetype ortho` + `nodesep`/`ranksep` prevent arrow crossings

---

## Programmatic API

```python
from pathlib import Path
from projwiki.parser.analyzer import CodebaseAnalyzer   # rename import if package renamed
from projwiki.diagram.generator import DiagramGenerator
from projwiki.generator.site_builder import SiteBuilder

analyzer = CodebaseAnalyzer(Path("./my-project"), max_depth=5)
analysis = analyzer.analyze()

diagram_gen = DiagramGenerator(analysis)
diagrams = diagram_gen.generate_all()

builder = SiteBuilder(Path("./output"))
builder.build(analysis, diagrams)          # summaries=None → offline mode
```

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| AST parsing (not regex) | Accurate extraction of classes, functions, docstrings across nested scopes |
| Timestamped output folders | Every run preserved; easy to diff two analyses |
| Offline-first | Core features work with zero credentials; AI is additive |
| PlantUML text output | No binary rendering dependency; renderable anywhere |
| Topological sort for diagram order | Execution flow matches actual import graph, not alphabetical |
| Rule engine for diagram type | Sequence diagrams are cleaner for small linear scripts; swimlanes for complex pipelines |

---

## Supported File Types

RepoWiki detects files by extension. Only the following extensions are picked up during analysis:

| Extension | Language | Deep AST Parsing? |
|-----------|----------|-------------------|
| `.py` | Python | ✅ Yes — classes, functions, docstrings, imports |
| `.js` | JavaScript | ⚠️ Line count + imports only (no AST) |
| `.ts` | TypeScript | ⚠️ Line count + imports only |
| `.jsx` / `.tsx` | React | ⚠️ Line count + imports only |
| `.java` | Java | ⚠️ Line count + imports only |
| `.cpp` / `.c` / `.h` | C / C++ | ⚠️ Line count + imports only |
| `.cs` | C# | ⚠️ Line count + imports only |
| `.go` | Go | ⚠️ Line count + imports only |
| `.rs` | Rust | ⚠️ Line count + imports only |
| `.rb` | Ruby | ⚠️ Line count + imports only |
| `.php` | PHP | ⚠️ Line count + imports only |
| `.swift` | Swift | ⚠️ Line count + imports only |
| `.kt` | Kotlin | ⚠️ Line count + imports only |

**Files that are silently ignored:**  
`*.pyc`, `*.pyo`, `*.so`, `*.egg-info`, binary files, images, notebooks (`.ipynb`), lock files, and all contents of: `__pycache__`, `.git`, `node_modules`, `venv`, `.venv`, `env`, `dist`, `build`, `output`, `.idea`, `.vscode`, `.pytest_cache`.

> To add a new language with full AST support, extend `projwiki/parser/file_parser.py`.

---

## Where to Host the Generated Output

The output folder (`output/YYYY-MM-DD_HH-MM-SS/`) is a **fully static site** — just HTML, CSS, and JS. It requires no server, no database, and no build step. You can host it anywhere:

### Option 1 — Local (open directly)
```bash
# Windows
start output\2026-03-30_20-43-15\index.html

# macOS / Linux
open output/2026-03-30_20-43-15/index.html
```
No server needed. Works fully offline.

### Option 2 — GitHub Pages
```bash
# Copy output into a docs/ folder and push
cp -r output/2026-03-30_20-43-15/* docs/
git add docs/ && git commit -m "docs: update repowiki output"
git push
# Enable GitHub Pages → Settings → Pages → Source: /docs
```
Free. Your docs live at `https://<user>.github.io/<repo>/`.

### Option 3 — Netlify / Vercel (drag-and-drop)
1. Go to [app.netlify.com](https://app.netlify.com) or [vercel.com](https://vercel.com)
2. Drag the `output/YYYY-MM-DD_HH-MM-SS/` folder onto the deploy zone
3. Get a live HTTPS URL in under 30 seconds — free tier is sufficient

### Option 4 — AWS S3 Static Website
```bash
aws s3 sync output/2026-03-30_20-43-15/ s3://your-bucket-name/ --acl public-read
# Enable static website hosting in the S3 bucket settings
```

### Option 5 — Azure Blob Storage Static Website
```bash
az storage blob upload-batch \
  --source output/2026-03-30_20-43-15/ \
  --destination '\$web' \
  --account-name <your-storage-account>
# Enable static website in Azure Portal → Storage Account → Static website
```

### Option 6 — SharePoint / Confluence (embed)
Upload `index.html` and `assets/` as a page attachment, then embed via an iframe. Useful for internal corporate wikis where external hosting isn't allowed.

### Option 7 — Docker (serve locally or on any cloud)
```bash
# Serve with a one-liner using Python's built-in HTTP server
cd output/2026-03-30_20-43-15 && python -m http.server 8080
# Open http://localhost:8080
```
Or wrap in a minimal Nginx/Docker container for deployment to any cloud VM.

> **Recommendation for teams:** GitHub Pages is the simplest zero-cost option. Add a CI step to auto-regenerate and push on every merge to `main`.

---

## Known Limitations

- Parsing is Python-only at file level (AST); other languages produce line/import counts only
- AI summarisation requires valid SAP AI Core credentials and a deployed LLM
- PlantUML rendering to PNG requires local `plantuml` CLI or Java — text `.puml` files always generated
- Cyclic imports are handled (cycles appended at end of topo sort) but may produce unexpected diagram order

---

## Future Work

- [ ] **Multi-language parsing** — JavaScript/TypeScript (via Babel AST), Java, Go
- [ ] **Interactive diagrams** — render PlantUML to SVG in-browser via `plantuml-encoder` JS library
- [ ] **Diff mode** — `projwiki diff run1/ run2/` to show what changed between two analyses
- [ ] **Search across runs** — unified index over all timestamped outputs
- [ ] **LLM provider swap** — plug in OpenAI / Azure OpenAI / Ollama instead of SAP AI Core
- [ ] **GitHub Action** — run on every PR, post summary as comment
- [ ] **VS Code extension** — run ProjWiki from the command palette, view output in side panel
- [ ] **Config file** — `projwiki.yaml` for per-repo ignore patterns, custom lane rules, depth
- [ ] **Dependency vulnerability scan** — flag known-vulnerable imports during analysis
- [ ] **Metrics dashboard** — complexity trends, file churn, dead code indicators over time

---

## Contributing

```bash
# Dev install with test dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
flake8 projwiki/
black projwiki/
```

Contributions welcome for: new language parsers, additional diagram types, hosting integrations, and UI themes.

---

## License

MIT — see [LICENSE](LICENSE)

---

*RepoWiki — because every codebase deserves a Wikipedia.*
