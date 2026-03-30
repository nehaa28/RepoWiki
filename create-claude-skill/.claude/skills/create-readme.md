---
name: create-readme
description: >
  Analyses any codebase and generates a professional README.md with inline Mermaid
  diagrams that render natively on GitHub and GitLab — no copy-pasting required.
  Use when the user wants to document a project, create a README from scratch, or
  update an outdated README. Works on any language Claude can read (Python, JS/TS,
  Java, Go, etc.). Always generates Mermaid diagrams, never PlantUML.
license: MIT
metadata:
  author: nehaa.bansal94@gmail.com
  version: "1.0"
  supported-agents: "Claude Code"
  diagram-format: "Mermaid (GitHub/GitLab native)"
  output: "README.md (or README-new.md if one already exists)"
compatibility: >
  Works in any project directory Claude Code can read. No external tools, APIs,
  or dependencies required. Offline — no internet access needed during generation.
allowed-tools: Read Glob Write
---

# Task

You are invoked when the user wants to generate a README.md file for their project.

## Instructions

1. **Analyze the current working directory:**
   - Read the project structure to find all relevant files
   - Identify the programming language(s) used
   - Look for configuration files (package.json, requirements.txt, setup.py, pyproject.toml, Cargo.toml, etc.)
   - Find any existing documentation files
   - Identify the entry point (main.py, index.js, app.py, etc.)

2. **Read key files to understand the project:**
   - Main source files
   - Configuration files
   - Any existing documentation
   - Package/dependency manifests

3. **Generate a comprehensive README.md that includes:**
   - Project title (derived from folder name or package name)
   - Brief description (1-2 sentences)
   - Problem statement (what problem does this solve?)
   - Solution statement (what does this project achieve?)
   - Features list
   - Architecture overview with Mermaid diagram (renders on GitHub/GitLab natively)
   - Data flow or sequence diagram (Mermaid)
   - Dependency diagram showing module relationships (Mermaid)
   - Installation instructions
   - Usage instructions with examples
   - Tech stack/dependencies table
   - Configuration (if applicable)
   - Development setup
   - Commands reference
   - Troubleshooting (common errors + fixes, derived from code)
   - Security considerations (if credentials/secrets involved)
   - Contributing guidelines (if it's a collaborative project)
   - License information (if found)

4. **Generate Mermaid diagrams — NOT PlantUML:**

   Mermaid renders natively in GitHub, GitLab, Notion, and VS Code. PlantUML does NOT render
   in GitHub — it shows as raw text. Always use Mermaid.

   **a) Architecture Diagram (flowchart):**
   ```mermaid
   graph TD
       A[Entry Point] --> B[Module A]
       A --> C[Module B]
       B --> D[External API]
   ```

   **b) Data Flow / Sequence Diagram:**
   ```mermaid
   sequenceDiagram
       participant User
       participant App
       participant API
       User->>App: input
       App->>API: request
       API-->>App: response
       App-->>User: output
   ```

   **c) Dependency Graph (for complex projects):**
   ```mermaid
   graph LR
       main --> moduleA
       main --> moduleB
       moduleA --> utils
   ```

   **d) Class Diagram (for OOP projects):**
   ```mermaid
   classDiagram
       class MyClass {
           +method()
       }
   ```

   Rules for Mermaid diagrams:
   - Node IDs must not contain spaces or special characters — use underscores
   - Labels in quotes can contain spaces: `A["My Label"]`
   - Keep diagrams focused — max ~15 nodes per diagram
   - Use subgraphs to group related components
   - Always wrap in ```mermaid code fences (not ```plantuml)

5. **Formatting guidelines:**
   - Use clear, concise language
   - Include code blocks with proper syntax highlighting
   - Use emoji sparingly and only where it adds clarity (✅, 📦, 🚀)
   - Structure with proper markdown headers
   - Include a table of contents for longer READMEs
   - Diagrams must be inline Mermaid blocks — they render directly, no copy-paste needed

6. **Important:**
   - Do NOT overwrite an existing README.md without user confirmation
   - If a README exists, ask if they want to overwrite or create README-new.md
   - Focus on practical, actionable information
   - Avoid generic filler text
   - Base all content on actual code analysis, not assumptions
   - Generate diagrams based on actual imports and structure found in code
   - Never invent class names, function names, or module names not found in the code
   - If credentials are detected in the project, include a Security section reminding users
     to use .env files and never commit secrets

## Output

Write the generated README.md to the current working directory and show the user a brief summary of what was included.
