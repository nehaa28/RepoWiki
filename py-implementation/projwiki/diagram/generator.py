"""
Generate architecture diagrams using PlantUML.

Diagram type selection rules
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
The generator inspects the analysed project and picks the right diagram type:

  SEQUENCE   file_count â‰¤ 6  AND  single entry-point  AND  call chain is linear
             â†’ shows WHO calls WHOM in order. Clearest for small scripts/pipelines.

  WORKFLOW   default when not SEQUENCE (swimlane activity diagram)
             â†’ shows WHAT each module does, grouped by functional role.
             â†’ lanes assigned by module-name keywords (see LANE_RULES).
             â†’ execution order via topological sort of import graph.

  CLASS      generated when total_classes â‰¥ max(3, file_count Ã— 0.4)
             â†’ shows class hierarchy, public/private methods, relationships.

  COMPONENT  always generated
             â†’ shows module-level dependency arrows.
             â†’ uses `left to right direction` when edges > 6 to avoid crossings.
             â†’ uses `skinparam linetype ortho` and nodesep/ranksep for spacing.

  STRUCTURE  always generated
             â†’ recursive folder/file tree.

PlantUML syntax rules respected (FAQ fixes)
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
1.  Swimlane partition MUST be declared before `start` keyword.
2.  `note right â€¦ end note` must follow a step directly â€” never emitted after a
    lane-switch (which would orphan it outside an activity block).
3.  Empty `note` blocks are never emitted.
4.  `left to right direction` is only used in component/class diagrams, NOT in
    activity diagrams (where it is ignored or causes parse warnings).
5.  Module/class names with hyphens, dots, spaces are sanitized:
      - identifier use  â†’ hyphens â†’ underscores, spaces stripped
      - label use       â†’ wrapped in quotes, HTML-special chars escaped
6.  Empty folder/package blocks (%{}) are never emitted in structure diagrams.
7.  `skinparam linetype ortho` prevents crossed arrows in component diagrams.
8.  `!theme` directive omitted from activity diagrams to avoid parser quirks.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import subprocess


# â”€â”€ Swimlane lane assignment â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Order matters: first matching rule wins.
LANE_RULES: List[Tuple[str, List[str]]] = [
    ('Input / Config',  ['load', 'loader', 'reader', 'input', 'ingest', 'fetch',
                         'source', 'config', 'setting', 'env', 'parser', 'schema']),
    ('Processing',      ['chunk', 'chunking', 'process', 'transform', 'pipeline',
                         'analyz', 'analysis', 'filter', 'clean', 'preprocess',
                         'extract', 'tokeniz', 'splitter', 'util', 'helper']),
    ('AI / Model',      ['embed', 'embedding', 'model', 'llm', 'generat', 'infer',
                         'summariz', 'classif', 'predict', 'prompt', 'ai', 'nlp',
                         'neural', 'bert', 'gpt', 'agent']),
    ('Storage / Index', ['store', 'storage', 'vector', 'index', 'db', 'database',
                         'cache', 'retriev', 'search', 'memory', 'persist', 'repo',
                         'query', 'document']),
    ('Output / CLI',    ['output', 'render', 'builder', 'site', 'display', 'main',
                         'cli', 'diagram', 'report', 'export', 'writer', 'app',
                         'server', 'api', 'router', 'view']),
]


def _assign_lane(stem: str) -> str:
    lower = stem.lower()
    for lane, keywords in LANE_RULES:
        if any(kw in lower for kw in keywords):
            return lane
    return 'Processing'


# â”€â”€ Sanitization helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _sanitize_id(name: str) -> str:
    """Convert a module/class name to a safe PlantUML identifier.
    Replaces hyphens and spaces with underscores; strips dots."""
    return re.sub(r'[^A-Za-z0-9_]', '_', name)


def _sanitize_label(text: str) -> str:
    """Escape characters that break PlantUML label syntax."""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', "'"))


class DiagramGenerator:
    """Generate architecture and dependency diagrams"""

    def __init__(self, analysis_result: Dict):
        self.analysis = analysis_result
        self.diagrams = {}

    # â”€â”€ Public API â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def generate_all(self) -> Dict[str, str]:
        """Apply selection rules and generate the appropriate diagram set."""
        all_stems, edges = self._collect_stems_and_edges()
        diagram_type = self._select_flow_diagram_type(all_stems, edges)

        if diagram_type == 'sequence':
            self.diagrams['sequence'] = self._generate_sequence_diagram(all_stems, edges)
        else:
            self.diagrams['workflow'] = self._generate_workflow_diagram(all_stems, edges)

        self.diagrams['dependency'] = self._generate_dependency_diagram(all_stems, edges)

        # Class diagram when project is OOP-heavy
        files = self.analysis.get('files', [])
        total_classes = sum(len(f.get('classes', [])) for f in files)
        if total_classes >= max(3, len(all_stems) * 0.4):
            self.diagrams['classes'] = self._generate_class_diagram()

        self.diagrams['structure'] = self._generate_structure_diagram()
        return self.diagrams

    # â”€â”€ Diagram type selection rule engine â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _select_flow_diagram_type(self,
                                  stems: Set[str],
                                  edges: Set[Tuple[str, str]]) -> str:
        """
        Rule engine â€” returns 'sequence' or 'workflow'.

        SEQUENCE when ALL of:
          â€¢ file_count â‰¤ 6  (small enough to follow in a linear diagram)
          â€¢ exactly one entry-point module (main / app / run / server / cli)
          â€¢ call graph is mostly linear: no module has more than 2 callers
            (avoids spaghetti sequence diagrams)

        WORKFLOW (swimlane) otherwise â€” handles multi-lane, complex pipelines.
        """
        file_count = self.analysis.get('file_count', 0)
        if file_count > 6:
            return 'workflow'

        entry_keywords = ('main', 'app', 'run', 'server', 'cli', 'index', 'start')
        entry_points = [s for s in stems if s.lower() in entry_keywords]
        if len(entry_points) != 1:
            return 'workflow'

        # check max in-degree â‰¤ 2
        in_degree: Dict[str, int] = {}
        for _, dst in edges:
            in_degree[dst] = in_degree.get(dst, 0) + 1
        if any(v > 2 for v in in_degree.values()):
            return 'workflow'

        return 'sequence'

    # â”€â”€ Shared helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _collect_stems_and_edges(self) -> Tuple[Set[str], Set[Tuple[str, str]]]:
        """Return (all_module_stems, intra-project dependency edges)."""
        project_path = self.analysis.get('project_path', '')
        files = self.analysis.get('files', [])
        dependencies = self.analysis.get('dependencies', {})

        all_stems: Set[str] = set()
        for f in files:
            try:
                stem = Path(f['path']).relative_to(project_path).stem
                if stem not in ('__init__', '__main__'):
                    all_stems.add(stem)
            except ValueError:
                pass

        edges: Set[Tuple[str, str]] = set()
        for fp_str, imports in dependencies.items():
            try:
                src = Path(fp_str).relative_to(project_path).stem
            except ValueError:
                continue
            if src in ('__init__', '__main__') or src not in all_stems:
                continue
            for imp in imports:
                imp_clean = imp.lstrip('.')
                if not imp_clean:
                    continue
                for part in reversed(imp_clean.split('.')):
                    if part in all_stems and part != src:
                        edges.add((src, part))
                        break

        return all_stems, edges

    def _topo_sort(self, stems: Set[str], edges: Set[Tuple[str, str]]) -> List[str]:
        """Kahn topological sort â€” returns execution order (sources first)."""
        in_degree = {m: 0 for m in stems}
        adj: Dict[str, List[str]] = {m: [] for m in stems}
        for src, dst in edges:
            adj[src].append(dst)
            in_degree[dst] += 1

        queue = sorted(m for m in stems if in_degree[m] == 0)
        order: List[str] = []
        visited: Set[str] = set()
        while queue:
            node = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            order.append(node)
            for nxt in sorted(adj[node]):
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    queue.append(nxt)
        for m in sorted(stems):
            if m not in visited:
                order.append(m)
        return order

    def _get_pub_fns(self, f_data: Optional[Dict]) -> List[str]:
        """Return up to 3 public function/method names for a file's parsed data."""
        if not f_data:
            return []
        fns = [fn['name'] for fn in f_data.get('functions', [])
               if not fn['name'].startswith('_')][:3]
        for cls in f_data.get('classes', []):
            for m in cls.get('methods', []):
                name = m['name'] if isinstance(m, dict) else m
                if not name.startswith('_') and len(fns) < 3:
                    fns.append(name)
        return fns[:3]

    # â”€â”€ Sequence diagram â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _generate_sequence_diagram(self,
                                    stems: Set[str],
                                    edges: Set[Tuple[str, str]]) -> str:
        """
        Sequence diagram â€” used for small (â‰¤ 6 files) linear projects.

        Participants are listed in topological order.
        Arrows are drawn src â†’ dst for each dependency edge.
        """
        project_path = self.analysis.get('project_path', '')
        files = self.analysis.get('files', [])
        project_name = Path(project_path).name

        topo = self._topo_sort(stems, edges)
        file_map = {}
        for f in files:
            try:
                stem = Path(f['path']).relative_to(project_path).stem
                file_map[stem] = f
            except ValueError:
                pass

        uml = f"@startuml\ntitle {_sanitize_label(project_name)} â€” Call Sequence\n\n"
        uml += "skinparam ParticipantPadding 20\n"
        uml += "skinparam BoxPadding 10\n\n"

        for mod in topo:
            label = _sanitize_label(mod)
            uml += f'participant "{label}" as {_sanitize_id(mod)}\n'

        uml += "\n"

        # Draw edges in topo order
        seen: Set[Tuple[str, str]] = set()
        for src in topo:
            callees = sorted(dst for s, dst in edges if s == src)
            for dst in callees:
                if (src, dst) not in seen:
                    seen.add((src, dst))
                    fns = self._get_pub_fns(file_map.get(dst))
                    call_label = fns[0] + '()' if fns else ''
                    uml += f"{_sanitize_id(src)} -> {_sanitize_id(dst)}"
                    if call_label:
                        uml += f" : {_sanitize_label(call_label)}"
                    uml += "\n"

        uml += "@enduml"
        return uml

    # â”€â”€ Workflow (swimlane activity) diagram â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _generate_workflow_diagram(self,
                                    stems: Set[str],
                                    edges: Set[Tuple[str, str]]) -> str:
        """
        Swimlane activity diagram.

        FAQ rules applied:
        â€¢ First swimlane partition declared BEFORE `start`.
        â€¢ `note right â€¦ end note` emitted immediately after its step, never
          across a lane boundary (would break the activity block).
        â€¢ Empty notes suppressed.
        â€¢ `left to right direction` NOT used (not valid in activity diagrams).
        """
        project_path = self.analysis.get('project_path', '')
        files = self.analysis.get('files', [])
        project_name = Path(project_path).name

        if not stems:
            return "@startuml\nnote: No modules found\n@enduml"

        topo = self._topo_sort(stems, edges)
        file_map = {}
        for f in files:
            try:
                stem = Path(f['path']).relative_to(project_path).stem
                file_map[stem] = f
            except ValueError:
                pass

        uml = f"@startuml\ntitle {_sanitize_label(project_name)} â€” Module Workflow\n\n"

        # FAQ rule #1: first lane BEFORE start
        first_lane = _assign_lane(topo[0]) if topo else 'Processing'
        uml += f"|{first_lane}|\n"
        uml += "start\n"
        current_lane = first_lane

        for mod in topo:
            lane = _assign_lane(mod)
            pub_fns = self._get_pub_fns(file_map.get(mod))
            callees = sorted(dst for src, dst in edges if src == mod)

            # FAQ rule #2: emit note BEFORE switching lane, so it stays inside
            # the current activity block.
            label = _sanitize_label(mod)
            if pub_fns:
                label += '\\n(' + ', '.join(_sanitize_label(fn) for fn in pub_fns) + ')'

            if lane != current_lane:
                uml += f"\n|{lane}|\n"
                current_lane = lane

            uml += f":{label};\n"

            # FAQ rule #3: skip empty notes
            if callees:
                uml += "note right\n"
                uml += f"calls: {', '.join(_sanitize_label(c) for c in callees)}\n"
                uml += "end note\n"

        uml += "\nstop\n@enduml"
        return uml

    # â”€â”€ Component (dependency) diagram â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _generate_dependency_diagram(self,
                                      stems: Set[str],
                                      edges: Set[Tuple[str, str]]) -> str:
        """
        Component diagram.

        FAQ rules applied:
        â€¢ `left to right direction` only here (component diagram), not activity.
        â€¢ `skinparam linetype ortho` + nodesep/ranksep prevent crossing arrows.
        â€¢ Module names with special chars are quoted in component declarations.
        """
        direction = "left to right direction" if len(edges) > 6 else "top to bottom direction"

        uml = (
            "@startuml\n"
            "!theme plain\n"
            f"{direction}\n\n"
            "skinparam component {\n"
            "  BackgroundColor #EAF4FB\n"
            "  BorderColor #2980B9\n"
            "  FontSize 12\n"
            "}\n"
            "skinparam ArrowColor #2980B9\n"
            "skinparam linetype ortho\n"
            "skinparam nodesep 20\n"
            "skinparam ranksep 25\n\n"
            "' Module Dependency Diagram\n\n"
        )

        for stem in sorted(stems):
            safe = _sanitize_label(stem)
            uml += f'component "{safe}" as {_sanitize_id(stem)}\n'

        if edges:
            uml += "\n"
            for src, dst in sorted(edges):
                uml += f'{_sanitize_id(src)} --> {_sanitize_id(dst)}\n'

        uml += "@enduml"
        return uml

    # â”€â”€ Class diagram â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _generate_class_diagram(self) -> str:
        """
        Class diagram â€” generated when project is OOP-heavy.

        Shows classes, public (+) and private (-) methods,
        and uses-relationships inferred from imports.
        """
        project_path = self.analysis.get('project_path', '')
        files = self.analysis.get('files', [])
        project_name = Path(project_path).name

        uml = (
            "@startuml\n"
            "!theme plain\n"
            f"title {_sanitize_label(project_name)} â€” Class Structure\n\n"
            "skinparam class {\n"
            "  BackgroundColor #EAF4FB\n"
            "  BorderColor #2980B9\n"
            "  FontSize 12\n"
            "}\n"
            "skinparam linetype ortho\n\n"
        )

        class_to_file: Dict[str, str] = {}
        for f in files:
            try:
                stem = Path(f['path']).relative_to(project_path).stem
            except ValueError:
                stem = Path(f['path']).stem
            for cls in f.get('classes', []):
                cname = _sanitize_id(cls['name'])
                class_to_file[cname] = stem
                methods = cls.get('methods', [])
                uml += f"class {cname} {{\n"
                for m in methods:
                    name = m['name'] if isinstance(m, dict) else m
                    vis = '-' if name.startswith('_') else '+'
                    safe_name = _sanitize_label(name.lstrip('_'))
                    uml += f"  {vis}{safe_name}()\n"
                uml += "}\n\n"

        # Draw dependency arrows between classes based on import edges
        _, edges = self._collect_stems_and_edges()
        stem_to_classes: Dict[str, List[str]] = {}
        for cname, stem in class_to_file.items():
            stem_to_classes.setdefault(stem, []).append(cname)

        drawn: Set[Tuple[str, str]] = set()
        for src_stem, dst_stem in sorted(edges):
            src_classes = stem_to_classes.get(src_stem, [])
            dst_classes = stem_to_classes.get(dst_stem, [])
            for sc in src_classes:
                for dc in dst_classes:
                    if (sc, dc) not in drawn:
                        drawn.add((sc, dc))
                        uml += f"{sc} ..> {dc} : uses\n"

        uml += "@enduml"
        return uml

    # â”€â”€ Structure diagram â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _generate_structure_diagram(self) -> str:
        """Recursive folder/file tree. FAQ: empty folder blocks suppressed."""
        structure = self.analysis.get('structure', {})
        uml = "@startuml\n!theme plain\n\n' Project Structure\n\n"
        body = self._render_structure_node(structure, indent=0)
        if body.strip():
            uml += body
        else:
            uml += 'note "No structure data"\n'
        uml += "\n@enduml"
        return uml

    def _render_structure_node(self, node: Dict, indent: int) -> str:
        """Recursively render. FAQ: skip empty directory blocks."""
        pad = '  ' * indent
        name = _sanitize_label(node.get('name', ''))
        if node.get('type') == 'directory':
            children_src = ''.join(
                self._render_structure_node(c, indent + 1)
                for c in node.get('children', [])
            )
            # FAQ rule #6: never emit empty folder blocks
            if not children_src.strip():
                return ''
            return f'{pad}folder "{name}" {{\n{children_src}{pad}}}\n'
        else:
            return f'{pad}file "{name}"\n'

    # â”€â”€ Render to PNG â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def render_to_file(self, diagram_name: str, output_path: Path) -> bool:
        """Render a diagram to PNG via the plantuml CLI if available."""
        if diagram_name not in self.diagrams:
            return False
        temp_file = output_path.with_suffix('.puml')
        temp_file.write_text(self.diagrams[diagram_name], encoding='utf-8')
        try:
            subprocess.run(
                ['plantuml', str(temp_file), '-o', str(output_path.parent)],
                check=True, capture_output=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"Note: PlantUML not found. Source saved to {temp_file}")
            return False



