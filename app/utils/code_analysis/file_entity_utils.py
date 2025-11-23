from tree_sitter import Parser, Node, Query, Tree, Language
from tree_sitter_language_pack import get_language
from typing import Dict, List, Tuple, Optional
from pathlib import Path

from app.utils.code_analysis.grammar_loader import extract_rule_names
from app.utils.code_analysis.parse_code_utils import detect_language,map_language_for_treesitter,extract_contents

def classify_node_types(rule_names: List[str]) -> Tuple[List[str], List[str], List[str]]:
    """
    Classify grammar rule names into class, function, and component node types
    using a hybrid strategy:
      - naive substring matching (language-agnostic)
      - accuracy filters (exclude internal patterns/types/helpers)
    """

    # Language-agnostic keyword groups
    class_keywords = ["class", "struct", "interface", "trait", "enum"]
    function_keywords = ["function", "method", "def", "lambda"]

    component_primary = {
        "component", "component_definition", "component_declaration", "component_render",
        "jsx_opening_element", "jsx_self_closing_element", "jsx_element", "jsx_fragment",
        "tsx_opening_element", "tsx_self_closing_element", "tsx_element",
        "template", "slot", "widget", "view"
    }
    component_generic = {"element", "tag"}

    class_nodes = []
    function_nodes = []
    component_nodes = []

    lowered = {r.lower() for r in rule_names}
    has_primary = any(any(p in r for p in component_primary) for r in lowered)

    for rule in rule_names:
        rl = rule.lower()
        # Skip internal helpers / structural patterns
        if (
            rl.startswith('_') or rl.endswith('_pattern') or rl.endswith('_type') or
            any(bad in rl for bad in ["parameter", "argument", "name_list", "decorator_list", "annotation_list", "identifier_list", "property_list"])
        ):
            continue
        # Class nodes
        if any(k in rl for k in class_keywords):
            class_nodes.append(rule)
            continue

        # Skip decorated wrappers from function types (they should be treated as wrappers)
        # e.g @classmethod
        if rl.startswith("decorated_"):
            continue
        
        # Function nodes (narrow to actual definitions, skip pure name tokens)
        if any(k in rl for k in function_keywords) and not rl.endswith('_name') and not rl.endswith('decorated_definition'):
            function_nodes.append(rule)
            continue

        # Component nodes
        if any(p in rl for p in component_primary):
            component_nodes.append(rule)
            continue
        if rl in component_generic and has_primary:
            component_nodes.append(rule)

    return class_nodes, function_nodes, component_nodes

def get_parser(file_content: str, ts_lang: str)-> Tree:
    parser = Parser()
    parser.language = ts_lang
    tree = parser.parse(file_content.encode())
    return tree

# ------ Class methods -------
# ---- Helper methods for extract_classes ----
def walk_class_nodes(node: Node, text: str, class_types: set, function_types: set, out: List[dict], file_path: Path):
    """
    DFS scan of the AST to collect class nodes.
    """
    if node.type in class_types:
        out.append(extract_single_class(node, text, function_types, file_path))

    for child in node.children:
        walk_class_nodes(child, text, class_types, function_types, out, file_path)
        
def extract_single_class(node: Node, text: str, function_types: set, file_path: Path) -> dict:
    """Extract class name + methods using provided function_types."""

    # Get class names
    class_names = extract_class_names(node, text)

    # 2. Extract methods
    methods = extract_methods_from_class(node, text, function_types, file_path)

    return {
        "name": class_names[0] if class_names else None,
        "methods": methods
    }
    
def extract_class_names(node: Node, text: str) -> List[str]:
    """
    Extract ALL class names from a class node.
    """
    CLASS_IDENTIFIERS = ["identifier", "type_identifier", "name", "constant", "scoped_identifier",
                         "class_name", "type_name", "module_identifier", "namespace_identifier"]
    names = []
    for child in node.children:
        if child.type in CLASS_IDENTIFIERS:
            name = text[child.start_byte:child.end_byte]
            names.append(name)
            continue
        if getattr(child, "children", None):
                # If child is a container node like “scoped_identifier” or “qualified_name”
                # explore only one more layer
                for grand in child.children:
                    if grand.type in CLASS_IDENTIFIERS:
                        name = text[grand.start_byte:grand.end_byte]
                        names.append(name)
    return names

def extract_classes(root: Node, file_content: str, class_node_types: List[str], function_node_types: List[str], file_path: Path)->List[dict]:
    """
    Extract class-level entities (name, methods list).
    """
    results: List[dict] = []
    walk_class_nodes(root, file_content, set(class_node_types), set(function_node_types), results, file_path)
    # Deduplicate classes by (name) to reduce false repeats (language-agnostic heuristic)
    dedup = []
    seen = set()
    for cls in results:
        key = (cls.get("name"), tuple(sorted(m.get("name") for m in cls.get("methods", []))))
        if key not in seen:
            seen.add(key)
            dedup.append(cls)
    return dedup

def extract_entities(tree: Tree, file_content: str, class_node_types: List[str], function_node_types: List[str], component_node_types: List[str], file_path: Path)->Dict[str, List[dict]]:
    """
    Main entry point for extracting structured entities from a single file.
    """
    class_entities = extract_classes(tree.root_node, file_content, class_node_types, function_node_types, file_path)
    function_entities = extract_functions(tree.root_node, file_content, function_node_types, class_node_types, file_path)
    component_entities = extract_components(tree.root_node, file_content, component_node_types, file_path)

    # --- Pruning stage ---
    # Classes: remove entries where name is None AND methods list is empty.
    class_entities = [c for c in class_entities if not (c.get("name") is None and len(c.get("methods", [])) == 0)]
    
    # Functions: remove entries lacking a name OR trivial one-line stubs (likely fields / signatures) with no params & no meaningful calls.
    def _is_trivial_function(f: dict) -> bool:
        name = f.get("name")
        if not name:
            return True
        loc = f.get("lines_of_code", 0)
        params = f.get("parameters", [])
        calls = f.get("calls", [])
        if loc == 0 and not params and not calls:
            return True
        return False
    function_entities = [f for f in function_entities if not _is_trivial_function(f)]

    # Components: remove unnamed records and low-signal HTML tag elements.
    HTML_TAGS = {
        'div','span','p','h1','h2','h3','h4','h5','h6','a','button','input','form','img','ul','li','ol','nav','header','footer','section','article','aside','main','label','select','option','textarea','script','style'
    }
    def _keep_component(comp: dict) -> bool:
        name = comp.get("name")
        if not name:
            return False
        # If PascalCase, keep.
        if name[0].isupper():
            return True
        # Remove raw html tags and generic template/tag when no enrichment.
        if name.lower() in HTML_TAGS:
            return False
        # Keep if it has any semantic enrichment (state/hooks/props) beyond empty lists.
        if comp.get("state_variables") or comp.get("hooks_used") or comp.get("props"):
            return True
        return False
    component_entities = [comp for comp in component_entities if _keep_component(comp)]

    return {
        "classes": class_entities,
        "functions": function_entities,
        "components": component_entities
    }
    
# ---------------- New helper methods for method extraction -----------------
def extract_methods_from_class(class_node: Node, text: str, function_types: set, file_path: Path) -> List[dict]:
    """
    Return list of method entity dictionaries found within the given class node.
    """
    methods: List[dict] = []
    
    CLASS_BODY_TYPES = {"class_body", "block", "suite", "member_declaration_list", "declaration_list"}
    WRAPPER_TYPES = {"decorated_definition", "annotation", "attribute_declaration"}

    def handle_child(n: Node):
        # Direct function definition
        if n.type in function_types:
            methods.append(extract_single_method(n, text, file_path))
            return
        # Decorator/annotation wrapper: search only immediate children for function
        if n.type in WRAPPER_TYPES:
            for ch in n.children:
                if ch.type in function_types:
                    methods.append(extract_single_method(ch, text, file_path))
                    return

    # Iterate over the class's children
    for child in class_node.children: 
        # If this node represents a body block, process its inner nodes
        if child.type in CLASS_BODY_TYPES:
            for grand in child.children:
                handle_child(grand)
        else:
            # Otherwise process the node directly
            handle_child(child)

    # Deduplicate by (name, span)
    dedup: List[dict] = []
    seen = set()
    for m in methods:
        key = (m.get("name"), m.get("lines_of_code"))
        if key not in seen:
            seen.add(key)
            dedup.append(m)
    return dedup

def extract_single_method(method_node: Node, text: str, file_path: Path) -> dict:
    """Build method entity dictionary including name, params, LOC, calls."""
    
    if method_node.type == "decorated_definition": #checking that the node identified have definitions like @staticmethod
        for ch in method_node.children:
            # Common underlying function node type names across grammars
            if ch.type in {"function_definition", "method_definition", "function_declaration", "method_declaration"}:
                method_node = ch
                break
    name = extract_method_name(method_node, text)
    params = extract_method_parameters(method_node, text)
    loc = (method_node.end_point[0] - method_node.start_point[0]) + 1
    calls = extract_method_calls(method_node, text)
    return {
        "name": name,
        "parameters": params,
        "lines_of_code": loc,
        "calls": calls
    }

def extract_method_name(method_node: Node, text: str) -> Optional[str]:
    """Locate method/function name token among immediate or one-level nested children."""
    
    # Possible node types that can represent a method/function name across languages
    CANDIDATE_NAME_TYPES = {"identifier", "name", "function_name", "method_name", "property_identifier"}

    # Look through direct children of the method node
    for child in method_node.children:
        # If this child is a name-bearing node, return its corresponding text
        if child.type in CANDIDATE_NAME_TYPES:
            return text[child.start_byte:child.end_byte]

        # Some grammars nest the name under another wrapper node (e.g., a declarator),
        # so inspect one level deeper if needed.
        for grand in getattr(child, 'children', []):
            if grand.type in CANDIDATE_NAME_TYPES:
                return text[grand.start_byte:grand.end_byte]

    # No name token found at expected locations
    return None

def extract_method_parameters(method_node: Node, text: str) -> List[str]:
    """Collect parameter identifier tokens within recognized parameter container nodes.

    Performs recursive descent within each container; duplicates and trivial
    implicit references (self/this) are removed.
    """

    # Node types that may contain parameter declarations across different languages
    PARAM_CONTAINER_TYPES = {"parameters", "parameter_list", "formal_parameters"}

    # Node types representing parameter names or declarators
    PARAM_NAME_TYPES = {"identifier", "name", "parameter", "variable_declarator"}

    params = []

    # Recursively traverse nodes inside a parameter container and collect names
    def collect_param_names(node: Node):
        for ch in node.children:
            # If this child represents some form of parameter identifier, capture it
            if ch.type in PARAM_NAME_TYPES:
                params.append(text[ch.start_byte:ch.end_byte])
            # Continue descending to catch deeply nested declarators
            collect_param_names(ch)

    # Search immediate children of the method node for parameter containers
    for child in method_node.children:
        if child.type in PARAM_CONTAINER_TYPES:
            collect_param_names(child)
        else:
            # Some grammars nest parameter containers under wrapper nodes (e.g., declarators)
            for grand in getattr(child, 'children', []):
                if grand.type in PARAM_CONTAINER_TYPES:
                    collect_param_names(grand)

    # Cleanup: remove duplicates and ignore language-specific implicit parameters
    cleaned = []
    seen = set()
    for p in params:
        p_clean = p.strip()
        # Skip empty tokens and implicit receiver parameters
        if not p_clean or p_clean in ("self", "this"):
            continue
        # Maintain insertion order by tracking what we've already kept
        if p_clean not in seen:
            seen.add(p_clean)
            cleaned.append(p_clean)

    return cleaned

def extract_method_calls(method_node: Node, text: str) -> List[str]:
    """
    Extract unique method/function names invoked within a method body.
    """
     # Node types representing call expressions across various grammars
    CALL_NODE_TYPES = {"call", "call_expression", "function_call", "method_invocation"}

    # Node types that may hold the callee name itself
    NAME_NODE_TYPES = {"identifier", "name", "property_identifier"}

    calls = []

    def walk(n: Node):
        # Detect call-like nodes
        if n.type in CALL_NODE_TYPES:
            # Attempt to extract the callee from the call's first child
            if n.children:
                callee = n.children[0]

                # Direct name-based callee (e.g., identifier or simple name)
                if callee.type in NAME_NODE_TYPES:
                    calls.append(text[callee.start_byte:callee.end_byte])

                else:
                    # Nested/attribute expressions: search child nodes for the first name
                    for ch in callee.children:
                        if ch.type in NAME_NODE_TYPES:
                            calls.append(text[ch.start_byte:ch.end_byte])
                            break

        # Continue walking all descendant nodes
        for ch in n.children:
            walk(ch)

    # Begin recursive traversal from the method node
    walk(method_node)

    # Remove duplicates while preserving order
    dedup = []
    seen = set()
    for c in calls:
        c_clean = c.strip()
        # Filter obvious non-call identifiers (single char, purely numeric)
        if not c_clean or len(c_clean) == 1 or c_clean.isdigit():
            continue
        if c_clean and c_clean not in seen:
            seen.add(c_clean)
            dedup.append(c_clean)

    return dedup

# ---------------- New helper methods for free-standing function extraction -----------------
def walk_function_nodes(node: Node, text: str, function_types: set, class_types: set, in_class: bool, out: List[dict], file_path: Path):
    """Collect free-standing functions (not linked to a class)"""
    WRAPPER_TYPES = {"decorated_definition", "annotation", "attribute_declaration"}

    if not in_class:
        if node.type in WRAPPER_TYPES:
            for ch in node.children:
                if ch.type in function_types:
                    out.append(extract_single_method(ch, text, file_path))
                    return
        elif node.type in function_types:
            out.append(extract_single_method(node, text, file_path))

    # Structural fallback: if classification missed function types, detect by presence of parameter & body containers
    if not in_class and node.type not in function_types:
        PARAM_HINTS = {"parameters", "parameter_list", "formal_parameters"}
        BODY_HINTS = {"block", "suite", "body", "compound_statement"}
        has_params = any(ch.type in PARAM_HINTS for ch in node.children)
        has_body = any(ch.type in BODY_HINTS for ch in node.children)
        if has_params and has_body:
            out.append(extract_single_method(node, text, file_path))
            return

    next_in_class = in_class or (node.type in class_types)
    # Limit descent: do not descend inside function definitions
    # Do not retrieve nested functions
    if node.type in function_types:
        return
    for child in node.children:
        walk_function_nodes(child, text, function_types, class_types, next_in_class, out, file_path)

def extract_functions(root: Node, file_content: str, function_node_types: List[str], class_node_types: List[str], file_path: Path) -> List[dict]:
    """
    Extract free-standing (module-level) functions.
    Free-standing: it is not nested inside any class
    """
    results: List[dict] = []
    walk_function_nodes(root, file_content, set(function_node_types), set(class_node_types), False, results, file_path)
    return results

# ---------------- Component extraction -----------------
def _node_text_generic(text: str, n: Node) -> str:
    return text[n.start_byte:n.end_byte]

def _contains_jsx(text: str, n: Node) -> bool:
    jsx_types = {"jsx_opening_element", "jsx_self_closing_element", "jsx_element", "jsx_fragment"}
    found = False
    def walk(x: Node):
        nonlocal found
        if x.type in jsx_types:
            found = True
            return
        for c in x.children:
            if found:
                break
            walk(c)
    walk(n)
    return found

HOOK_NAMES = {
    "usestate","useeffect","usecontext","usereducer","usememo","usecallback","useref",
    "uselayouteffect","useimperativehandle","usetransition","usedeferredvalue","useid"
}

def _collect_hooks(text: str, n: Node) -> List[str]:
    hooks: List[str] = []
    def walk(x: Node):
        if x.type == "call_expression" and x.children:
            callee = x.children[0]
            name_candidate = None
            if callee.type == "identifier":
                name_candidate = _node_text_generic(text, callee)
            else:
                for ch in callee.children:
                    if ch.type == "identifier":
                        name_candidate = _node_text_generic(text, ch)
                        break
            if name_candidate and name_candidate.lower() in HOOK_NAMES and name_candidate not in hooks:
                hooks.append(name_candidate)
        for ch in x.children:
            walk(ch)
    walk(n)
    return hooks

def _collect_state_vars(text: str, n: Node) -> List[str]:
    state_vars: List[str] = []
    def walk(x: Node):
        if x.type == "variable_declarator" and x.children:
            init_call = None
            array_pattern = None
            for ch in x.children:
                if ch.type == "call_expression":
                    init_call = ch
                if ch.type in {"array_pattern","destructuring_pattern","pattern"}:
                    array_pattern = ch
            if init_call and array_pattern and init_call.children:
                callee = init_call.children[0]
                callee_name = None
                if callee.type == "identifier":
                    callee_name = _node_text_generic(text, callee)
                else:
                    for cc in callee.children:
                        if cc.type == "identifier":
                            callee_name = _node_text_generic(text, cc)
                            break
                if callee_name and callee_name.lower() == "usestate":
                    for ap_child in array_pattern.children:
                        if ap_child.type == "identifier":
                            name = _node_text_generic(text, ap_child)
                            if name and name not in state_vars:
                                state_vars.append(name)
        for ch in x.children:
            walk(ch)
    walk(n)
    return state_vars

def _collect_props_member_access(text: str, n: Node, root_param_name: str) -> List[str]:
    props: List[str] = []
    def walk(x: Node):
        if x.type == "member_expression" and x.children:
            obj = x.children[0]
            prop = None
            for ch in x.children[1:]:
                if ch.type in {"property_identifier","identifier"}:
                    prop = ch
                    break
            if obj.type == "identifier" and _node_text_generic(text, obj) == root_param_name and prop:
                pname = _node_text_generic(text, prop)
                if pname and pname not in props:
                    props.append(pname)
        for ch in x.children:
            walk(ch)
    walk(n)
    return props

def _extract_function_component(text: str, fn: Node) -> Optional[dict]:
    name = extract_method_name(fn, text)
    if not name or not name[0].isupper():
        return None
    if not _contains_jsx(text, fn):
        return None
    params: List[str] = []
    props_root_name = None
    for child in fn.children:
        if child.type in {"parameters","parameter_list","formal_parameters"}:
            for p in child.children:
                if p.type in {"identifier","name"}:
                    pname = _node_text_generic(text, p)
                    if pname == "props":
                        props_root_name = pname
                    if pname and pname not in {"self","this"}:
                        params.append(pname)
    inferred_props: List[str] = []
    if props_root_name:
        inferred_props = _collect_props_member_access(text, fn, props_root_name)
    return {
        "name": name,
        "props": inferred_props or params,
        "state_variables": _collect_state_vars(text, fn),
        "hooks_used": _collect_hooks(text, fn)
    }

def _extract_class_component(text: str, cls: Node) -> Optional[dict]:
    COMPONENT_NAME_SUFFIXES = ("Component", "View", "Widget", "Page")
    LIFECYCLE_METHOD_PREFIXES = ("ngOn", "render", "mount", "unmount", "beforeMount", "afterMount")
    LIFECYCLE_INTERFACE_HINTS = ("OnInit", "IComponent", "ComponentInterface", "Renderable")

    name: Optional[str] = None
    decorators: List[str] = []
    interface_names: List[str] = []

    for child in cls.children:
        if child.type == "decorator":
            for dch in child.children:
                for g in ([dch] + getattr(dch, 'children', [])):
                    if g.type == "identifier":
                        decorators.append(_node_text_generic(text, g))
        if child.type in {"identifier", "type_identifier", "class_name"} and not name:
            name = _node_text_generic(text, child)
        if child.type in {"implements_clause", "class_heritage"}:
            for g in child.children:
                if g.type in {"identifier", "type_identifier"}:
                    interface_names.append(_node_text_generic(text, g))

    if not name or not name[0].isupper():
        return None

    has_suffix = any(name.endswith(suf) for suf in COMPONENT_NAME_SUFFIXES)
    has_decorator = any(dec.lower() in {"component", "view", "widget"} for dec in decorators)
    has_interface = any(iface in interface_names for iface in LIFECYCLE_INTERFACE_HINTS)

    props: List[str] = []
    state_vars: List[str] = []
    lifecycle_hooks: List[str] = []

    FIELD_TYPES = {"public_field_definition", "property_signature", "property_definition"}
    METHOD_TYPES = {"method_definition", "method_signature", "function_signature"}

    def walk_body(n: Node):
        if n.type in FIELD_TYPES:
            field_name = None
            field_decorators: List[str] = []
            for ch in n.children:
                if ch.type == "decorator":
                    for dch in ch.children:
                        for g in ([dch] + getattr(dch, 'children', [])):
                            if g.type == "identifier":
                                field_decorators.append(_node_text_generic(text, g))
                if ch.type in {"property_identifier", "identifier"} and field_name is None:
                    field_name = _node_text_generic(text, ch)
            if field_name:
                if any(d in {"Input", "Prop", "property"} for d in field_decorators):
                    if field_name not in props:
                        props.append(field_name)
                else:
                    if field_name not in state_vars:
                        state_vars.append(field_name)
        elif n.type in METHOD_TYPES:
            mname = None
            for ch in n.children:
                if ch.type in {"property_identifier", "identifier", "method_name"}:
                    mname = _node_text_generic(text, ch)
                    break
            if mname and any(mname.startswith(pref) for pref in LIFECYCLE_METHOD_PREFIXES):
                if mname not in lifecycle_hooks:
                    lifecycle_hooks.append(mname)
        for ch in n.children:
            walk_body(ch)

    for child in cls.children:
        if child.type == "class_body":
            for grand in child.children:
                walk_body(grand)
        else:
            walk_body(child)

    high_signal = has_suffix or has_decorator or has_interface or lifecycle_hooks
    if not high_signal:
        return None

    hooks_used = list(dict.fromkeys(_collect_hooks(text, cls) + lifecycle_hooks))
    return {
        "name": name,
        "props": props,
        "state_variables": state_vars,
        "hooks_used": hooks_used
    }

def extract_components(root: Node, file_content: str, component_node_types: List[str], file_path: Path) -> List[dict]:
    text = file_content
    component_type_set = set(component_node_types)
    FUNCTION_TYPES = {"function_definition", "function_declaration", "method_definition", "function_signature"}
    CLASS_TYPES = {"class", "class_declaration", "abstract_class_declaration"}
    results: List[dict] = []
    seen_names: set = set()

    def traverse(n: Node):
        comp: Optional[dict] = None
        if n.type in component_type_set:
            comp = extract_component_from_node_type(n, text)
        elif n.type in FUNCTION_TYPES:
            comp = _extract_function_component(text, n)
        elif n.type in CLASS_TYPES:
            comp = _extract_class_component(text, n)
        if comp:
            nm = comp.get("name")
            if nm and nm not in seen_names:
                seen_names.add(nm)
                results.append(comp)
        for ch in n.children:
            traverse(ch)
    traverse(root)
    return results

def extract_component_from_node_type(node: Node, file_content: str) -> Optional[dict]:
    """Attempt to extract a component entity purely from a matched component node type.

    Generic strategy:
      - Derive name from first suitable child (identifier / tag / element name)
      - Collect attribute/property names as props
      - Leave state_variables & hooks_used empty (grammar-level signal only)
    """
    text = file_content
    name = None
    NAME_TYPES = {"identifier", "jsx_identifier", "type_identifier", "tag_name", "element_name", "property_identifier"}
    ATTR_CONTAINER_TYPES = {"jsx_attribute", "attribute", "attribute_name"}
    props: List[str] = []

    for child in node.children:
        if not name and child.type in NAME_TYPES:
            name = text[child.start_byte:child.end_byte]
        if child.type in ATTR_CONTAINER_TYPES:
            attr_name = None
            for g in getattr(child, 'children', []):
                if g.type in NAME_TYPES:
                    attr_name = text[g.start_byte:g.end_byte]
                    break
            if attr_name is None:
                raw = text[child.start_byte:child.end_byte]
                attr_name = raw.split('=')[0].strip()
            if attr_name and attr_name not in props:
                props.append(attr_name)

    if not name:
        for child in node.children:
            for g in getattr(child, 'children', []):
                if g.type in NAME_TYPES:
                    name = text[g.start_byte:g.end_byte]
                    break
            if name:
                break
    if not name or not name[0].isalpha():
        return None
    return {
        "name": name,
        "props": props,
        "state_variables": [],
        "hooks_used": []
    }
    
language=detect_language(Path("tests/utils/code_analysis/test_parse_code_utils.py"))
language=map_language_for_treesitter(language)
file_content=extract_contents(Path("tests/utils/code_analysis/test_parse_code_utils.py"))
rule_names = extract_rule_names(Path(f"app/shared/grammars/{language}.js"))
class_nodes, func_nodes, component_nodes = classify_node_types(rule_names)

ts_lang = get_language(language)
tree = get_parser(file_content, ts_lang)
file_path= Path("tests/utils/code_analysis/test_parse_code_utils.py")
entities=extract_entities(tree, file_content, class_nodes,func_nodes,component_nodes,file_path)
print(entities)

print()
language=detect_language(Path("app/utils/code/flick.py"))
language=map_language_for_treesitter(language)
file_content=extract_contents(Path("app/utils/code/flick.py"))
rule_names = extract_rule_names(Path(f"app/shared/grammars/{language}.js"))
class_nodes, func_nodes, component_nodes = classify_node_types(rule_names)

ts_lang = get_language(language)
tree = get_parser(file_content, ts_lang)
file_path= Path("app/utils/code/flick.py")
entities=extract_entities(tree, file_content, class_nodes,func_nodes,component_nodes,file_path)
print(entities)

print()
language=detect_language(Path("app/utils/code/MainApp.java"))
language=map_language_for_treesitter(language)
file_content=extract_contents(Path("app/utils/code/MainApp.java"))
rule_names = extract_rule_names(Path(f"app/shared/grammars/{language}.js"))
class_nodes, func_nodes, component_nodes = classify_node_types(rule_names)

ts_lang = get_language(language)
tree = get_parser(file_content, ts_lang)
file_path= Path("app/utils/code/MainApp.java")
entities=extract_entities(tree, file_content, class_nodes,func_nodes,component_nodes,file_path)
print(entities)

print()
language=detect_language(Path("app/utils/code/mapper.cpp"))
language=map_language_for_treesitter(language)
file_content=extract_contents(Path("app/utils/code/mapper.cpp"))
rule_names = extract_rule_names(Path(f"app/shared/grammars/{language}.js"))
class_nodes, func_nodes, component_nodes = classify_node_types(rule_names)

ts_lang = get_language(language)
tree = get_parser(file_content, ts_lang)
file_path= Path("app/utils/code/mapper.cpp")
entities=extract_entities(tree, file_content, class_nodes,func_nodes,component_nodes,file_path)
print(entities)

print()
language=detect_language(Path("app/utils/code/mapper.cs"))
language=map_language_for_treesitter(language)
file_content=extract_contents(Path("app/utils/code/mapper.cs"))
rule_names = extract_rule_names(Path(f"app/shared/grammars/{language}.js"))
class_nodes, func_nodes, component_nodes = classify_node_types(rule_names)

ts_lang = get_language(language)
tree = get_parser(file_content, ts_lang)
file_path= Path("app/utils/code/mapper.cs")
entities=extract_entities(tree, file_content, class_nodes,func_nodes,component_nodes,file_path)
print(entities)

print()
language=detect_language(Path("app/utils/code/user-card.component.ts"))
language=map_language_for_treesitter(language)
file_content=extract_contents(Path("app/utils/code/user-card.component.ts"))
rule_names = extract_rule_names(Path(f"app/shared/grammars/{language}.js"))
class_nodes, func_nodes, component_nodes = classify_node_types(rule_names)

ts_lang = get_language(language)
tree = get_parser(file_content, ts_lang)
file_path= Path("app/utils/code/user-card.component.ts")
entities=extract_entities(tree, file_content, class_nodes,func_nodes,component_nodes,file_path)
print(entities)

print()
language=detect_language(Path("app/utils/code/UserCard.jsx"))
language=map_language_for_treesitter(language)
file_content=extract_contents(Path("app/utils/code/UserCard.jsx"))
rule_names = extract_rule_names(Path(f"app/shared/grammars/{language}.js"))
class_nodes, func_nodes, component_nodes = classify_node_types(rule_names)

ts_lang = get_language(language)
tree = get_parser(file_content, ts_lang)
file_path= Path("app/utils/code/UserCard.jsx")
entities=extract_entities(tree, file_content, class_nodes,func_nodes,component_nodes,file_path)
print(entities)

print()
language=detect_language(Path("app/utils/code/testing.vue"))
language=map_language_for_treesitter(language)
file_content=extract_contents(Path("app/utils/code/testing.vue"))
rule_names = extract_rule_names(Path(f"app/shared/grammars/{language}.js"))
class_nodes, func_nodes, component_nodes = classify_node_types(rule_names)

ts_lang = get_language(language)
tree = get_parser(file_content, ts_lang)
file_path= Path("app/utils/code/testing.vue")
entities=extract_entities(tree, file_content, class_nodes,func_nodes,component_nodes,file_path)
print(entities)

print()
language=detect_language(Path("app/utils/code/app.component.ts"))
language=map_language_for_treesitter(language)
file_content=extract_contents(Path("app/utils/code/app.component.ts"))
rule_names = extract_rule_names(Path(f"app/shared/grammars/{language}.js"))
class_nodes, func_nodes, component_nodes = classify_node_types(rule_names)

ts_lang = get_language(language)
tree = get_parser(file_content, ts_lang)
file_path= Path("app/utils/code/app.component.ts")
entities=extract_entities(tree, file_content, class_nodes,func_nodes,component_nodes,file_path)
print(entities)

print()
language=detect_language(Path("app/utils/code/example.tsx"))
language=map_language_for_treesitter(language)
file_content=extract_contents(Path("app/utils/code/example.tsx"))
rule_names = extract_rule_names(Path(f"app/shared/grammars/{language}.js"))
class_nodes, func_nodes, component_nodes = classify_node_types(rule_names)

ts_lang = get_language(language)
tree = get_parser(file_content, ts_lang)
file_path= Path("app/utils/code/example.tsx")
entities=extract_entities(tree, file_content, class_nodes,func_nodes,component_nodes,file_path)
print(entities)