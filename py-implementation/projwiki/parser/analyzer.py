"""
Codebase analyzer - traverses and analyzes project structure
"""

import ast
from pathlib import Path
from typing import Dict, List, Set
import json

from .file_parser import FileParser


class CodebaseAnalyzer:
    """Analyzes a codebase and extracts structure, dependencies, and metadata"""

    # Common files/dirs to ignore
    IGNORE_PATTERNS = {
        '__pycache__', '.git', '.svn', 'node_modules', 'venv', '.venv',
        'env', '.env', 'dist', 'build', 'output', '.idea', '.vscode', '.pytest_cache',
        '*.pyc', '*.pyo', '*.so', '*.egg-info'
    }

    SUPPORTED_EXTENSIONS = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
        '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt'
    }

    def __init__(self, project_path: Path, max_depth: int = 5):
        self.project_path = Path(project_path)
        self.max_depth = max_depth
        self.file_parser = FileParser()

    def analyze(self) -> Dict:
        """
        Analyze the codebase and return structured data

        Returns:
            Dict containing:
                - files: List of parsed files
                - structure: Directory tree
                - dependencies: Dependency graph
                - tech_stack: Detected technologies
                - glossary_terms: Extracted terms
        """
        files = []
        dependencies = {}
        tech_stack = set()
        glossary_terms = {}

        # Traverse directory
        for file_path in self._traverse_directory():
            try:
                parsed = self.file_parser.parse(file_path)
                files.append(parsed)

                # Extract dependencies
                if parsed['imports']:
                    dependencies[str(file_path)] = parsed['imports']

                # Detect tech stack
                tech_stack.update(self._detect_tech_stack(file_path, parsed))

                # Extract glossary terms
                glossary_terms.update(self._extract_terms(parsed))

            except Exception as e:
                print(f"Warning: Failed to parse {file_path}: {e}")

        return {
            'project_path': str(self.project_path),
            'file_count': len(files),
            'files': files,
            'structure': self._build_structure(),
            'dependencies': dependencies,
            'tech_stack': sorted(list(tech_stack)),
            'glossary_terms': glossary_terms
        }

    def _traverse_directory(self) -> List[Path]:
        """Traverse directory and yield file paths"""
        files = []

        for path in self.project_path.rglob('*'):
            # Check depth
            try:
                relative = path.relative_to(self.project_path)
                if len(relative.parts) > self.max_depth:
                    continue
            except ValueError:
                continue

            # Check if should ignore
            if self._should_ignore(path):
                continue

            # Check if supported file
            if path.is_file() and path.suffix in self.SUPPORTED_EXTENSIONS:
                files.append(path)

        return files

    def _should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored"""
        for pattern in self.IGNORE_PATTERNS:
            if pattern.startswith('*'):
                if path.name.endswith(pattern[1:]):
                    return True
            elif pattern in path.parts:
                return True
        return False

    def _build_structure(self, path: Path = None, depth: int = 0) -> Dict:
        """Build directory tree structure recursively"""
        if path is None:
            path = self.project_path

        structure = {
            'name': path.name,
            'type': 'directory',
            'children': []
        }

        if depth >= self.max_depth:
            return structure

        try:
            for child_path in sorted(path.iterdir()):
                if self._should_ignore(child_path):
                    continue
                if child_path.is_dir():
                    structure['children'].append(
                        self._build_structure(child_path, depth + 1)
                    )
                else:
                    structure['children'].append({
                        'name': child_path.name,
                        'type': 'file',
                        'path': str(child_path.relative_to(self.project_path))
                    })
        except PermissionError:
            pass

        return structure

    def _detect_tech_stack(self, file_path: Path, parsed: Dict) -> Set[str]:
        """Detect technologies from file and imports"""
        tech = set()

        # By file extension
        ext_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'React',
            '.tsx': 'React TypeScript',
            '.java': 'Java',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.cs': 'C#',
            '.cpp': 'C++',
            '.c': 'C',
            '.php': 'PHP',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
        }

        if file_path.suffix in ext_map:
            tech.add(ext_map[file_path.suffix])

        # By imports — map root package name → technology label
        IMPORT_TECH_MAP = {
            # Web frameworks
            'django': 'Django',
            'flask': 'Flask',
            'fastapi': 'FastAPI',
            'starlette': 'Starlette',
            'tornado': 'Tornado',
            'aiohttp': 'aiohttp',
            'bottle': 'Bottle',
            'falcon': 'Falcon',
            'sanic': 'Sanic',
            # Data science / ML
            'numpy': 'NumPy',
            'pandas': 'Pandas',
            'scipy': 'SciPy',
            'sklearn': 'scikit-learn',
            'matplotlib': 'Matplotlib',
            'seaborn': 'Seaborn',
            'plotly': 'Plotly',
            'torch': 'PyTorch',
            'tensorflow': 'TensorFlow',
            'keras': 'Keras',
            'xgboost': 'XGBoost',
            'lightgbm': 'LightGBM',
            'transformers': 'HuggingFace Transformers',
            'langchain': 'LangChain',
            'openai': 'OpenAI SDK',
            # Databases / ORMs
            'sqlalchemy': 'SQLAlchemy',
            'pymongo': 'MongoDB (pymongo)',
            'motor': 'MongoDB (motor)',
            'redis': 'Redis',
            'elasticsearch': 'Elasticsearch',
            'psycopg2': 'PostgreSQL (psycopg2)',
            'pymysql': 'MySQL (pymysql)',
            'aiosqlite': 'SQLite (async)',
            'tortoise': 'Tortoise ORM',
            'peewee': 'Peewee ORM',
            # HTTP / networking
            'requests': 'Requests',
            'httpx': 'HTTPX',
            'aiohttp': 'aiohttp',
            'urllib3': 'urllib3',
            'websockets': 'WebSockets',
            # CLI / terminal
            'click': 'Click',
            'typer': 'Typer',
            'argparse': 'argparse',
            'rich': 'Rich',
            'colorama': 'Colorama',
            'tqdm': 'tqdm',
            # Templating / serialization
            'jinja2': 'Jinja2',
            'pydantic': 'Pydantic',
            'marshmallow': 'Marshmallow',
            'yaml': 'PyYAML',
            'toml': 'TOML',
            # Testing
            'pytest': 'pytest',
            'unittest': 'unittest',
            'hypothesis': 'Hypothesis',
            # Task queues / messaging
            'celery': 'Celery',
            'kafka': 'Kafka',
            'pika': 'RabbitMQ (pika)',
            # Cloud / infra
            'boto3': 'AWS (boto3)',
            'google.cloud': 'Google Cloud',
            'azure': 'Azure SDK',
            # Graphs / analysis
            'networkx': 'NetworkX',
            'igraph': 'igraph',
            # Build / packaging
            'setuptools': 'setuptools',
            'poetry': 'Poetry',
        }

        if file_path.suffix == '.py':
            for imp in parsed.get('imports', []):
                root = imp.lstrip('.').split('.')[0].lower()
                if root in IMPORT_TECH_MAP:
                    tech.add(IMPORT_TECH_MAP[root])

        return tech

    def _extract_terms(self, parsed: Dict) -> Dict[str, str]:
        """Extract potential glossary terms"""
        terms = {}

        for cls in parsed.get('classes', []):
            name = cls['name']
            if name and name[0].isupper():
                doc = cls.get('docstring', '')
                methods = cls.get('methods', [])
                public_methods = [
                    m['name'] if isinstance(m, dict) else m
                    for m in methods
                    if not (m['name'] if isinstance(m, dict) else m).startswith('_')
                ]
                desc = doc.split('\n')[0].strip() if doc else f"Class defined in {Path(parsed['path']).name}"
                if public_methods:
                    desc += f"\nPublic methods: {', '.join(public_methods[:6])}"
                terms[name] = desc

        for func in parsed.get('functions', []):
            name = func['name']
            if name and not name.startswith('_') and len(name) > 3:
                doc = func.get('docstring', '')
                args = [a for a in func.get('args', []) if a not in ('self', 'cls')]
                desc = doc.split('\n')[0].strip() if doc else f"Function defined in {Path(parsed['path']).name}"
                if args:
                    desc += f"\nParameters: {', '.join(args[:5])}"
                terms[name] = desc

        return terms
