import uuid
import re
from typing import List, Dict, Any, Set, Tuple
import networkx as nx

from omnicore.ast.ast_nodes import ProgramAST, ASTNode, CommandNode, SequenceNode, ConjunctionNode
from omnicore.compiler.pass_manager import BasePass, CompilationContext
from omnicore.compiler.symbol_table import SymbolTable, Symbol
from omnicore.ir.enums import TaskIntent, Capability, Complexity, NodeStatus
from omnicore.ir.models import TaskIR, ExecutionNode, Dependency, ExecutionDAG

class SymbolResolutionPass(BasePass):
    """
    Pass 1: Walks the AST, registers execution nodes, assigns unique IDs,
    and populates the Symbol Table with inputs and outputs to establish dataflow.
    Applies type inference to assign default inputs and outputs if none are explicitly declared.
    """
    def run(self, context: CompilationContext) -> None:
        node_metadata = {}
        node_counter = {}

        # Helper to traverse and assign metadata
        def register_nodes(node: ASTNode):
            if isinstance(node, (SequenceNode, ConjunctionNode)):
                register_nodes(node.left)
                register_nodes(node.right)
            elif isinstance(node, CommandNode):
                # Map action category to name prefix
                prefix = node.action_verb.lower()
                node_counter[prefix] = node_counter.get(prefix, 0) + 1
                unique_id = f"{prefix}_{node_counter[prefix]}"
                
                # Check capability
                capability = self._map_verb_to_capability(node.action_verb, node.outputs)

                # Heuristic Type/Symbol Inference for inputs/outputs if empty
                inputs = list(node.inputs)
                outputs = list(node.outputs)
                if not outputs:
                    if capability == Capability.WEB_SEARCH:
                        outputs = ["findings"]
                    elif capability == Capability.COMPARISON:
                        outputs = ["comparison"]
                    elif capability == Capability.SUMMARIZATION:
                        outputs = ["summary"]
                    elif capability == Capability.PDF_GENERATION:
                        outputs = ["pdf"]
                    elif capability == Capability.EMAIL:
                        outputs = ["email_receipt"]
                    else:
                        outputs = [f"{unique_id}_out"]
                
                if not inputs:
                    if capability == Capability.COMPARISON:
                        inputs = ["findings"]
                    elif capability == Capability.SUMMARIZATION:
                        inputs = ["comparison"]
                    elif capability == Capability.PDF_GENERATION:
                        inputs = ["summary"]
                    elif capability == Capability.EMAIL:
                        inputs = ["summary"]

                # Store node id and mapping
                node_metadata[id(node)] = {
                    "node_id": unique_id,
                    "capability": capability,
                    "inputs": inputs,
                    "outputs": outputs
                }

                # Register outputs in Symbol Table
                for out in outputs:
                    context.symbol_table.insert(out, "data", producer_node_id=unique_id)

                # Register inputs in Symbol Table
                for inp in inputs:
                    context.symbol_table.add_consumer(inp, unique_id)

        # Traverse the AST
        register_nodes(context.ast.root)
        
        # Save mappings to context metadata
        context.metadata["node_metadata"] = node_metadata

    def _map_verb_to_capability(self, verb: str, outputs: List[str]) -> Capability:
        verb_lower = verb.lower()
        if verb_lower == "search":
            return Capability.WEB_SEARCH
        elif verb_lower == "compare":
            return Capability.COMPARISON
        elif verb_lower == "summarize":
            return Capability.SUMMARIZATION
        elif verb_lower == "generate":
            if any("pdf" in o.lower() for o in outputs):
                return Capability.PDF_GENERATION
            return Capability.REPORT_GENERATION
        elif verb_lower == "write":
            return Capability.REPORT_GENERATION
        elif verb_lower == "email":
            return Capability.EMAIL
        elif verb_lower == "extract":
            return Capability.RETRIEVAL
        elif verb_lower == "database_access":
            return Capability.DATABASE_ACCESS
        return Capability.REASONING


class ClassifierPass(BasePass):
    """
    Pass 2: Semantic Intent and Domain Classification.
    """
    def run(self, context: CompilationContext) -> None:
        text = context.raw_input.lower()
        
        # Simple rule-based scoring for domain & intent
        scores = {
            TaskIntent.RESEARCH: 0,
            TaskIntent.AUTOMATION: 0,
            TaskIntent.PROGRAMMING: 0,
            TaskIntent.DATA_ANALYSIS: 0,
            TaskIntent.WRITING: 0,
            TaskIntent.SCHEDULING: 0,
            TaskIntent.INFORMATION_RETRIEVAL: 0,
        }

        # Match patterns
        if re.search(r"\b(?:search|compare|research|survey|literature|study)\b", text):
            scores[TaskIntent.RESEARCH] += 3
        if re.search(r"\b(?:automate|script|workflow|run|trigger|execute)\b", text):
            scores[TaskIntent.AUTOMATION] += 2
        if re.search(r"\b(?:program|code|compiler|develop|software|java|python|rust)\b", text):
            scores[TaskIntent.PROGRAMMING] += 4
        if re.search(r"\b(?:analyze|data|database|sql|pandas|plot|chart|graph)\b", text):
            scores[TaskIntent.DATA_ANALYSIS] += 3
        if re.search(r"\b(?:write|generate|summarize|pdf|report|draft|author)\b", text):
            scores[TaskIntent.WRITING] += 2
        if re.search(r"\b(?:schedule|calendar|time|meeting|appointment|remind)\b", text):
            scores[TaskIntent.SCHEDULING] += 4
        if re.search(r"\b(?:find|get|retrieve|fetch|extract)\b", text):
            scores[TaskIntent.INFORMATION_RETRIEVAL] += 2

        # Sort scores
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_scores[0][0] if sorted_scores[0][1] > 0 else TaskIntent.UNKNOWN
        secondary = sorted_scores[1][0] if sorted_scores[1][1] > 0 else None

        context.metadata["primary_intent"] = primary
        context.metadata["secondary_intent"] = secondary

        # Determine domain
        if primary == TaskIntent.PROGRAMMING:
            context.metadata["domain"] = "Software Engineering"
        elif primary == TaskIntent.DATA_ANALYSIS:
            context.metadata["domain"] = "Data Science"
        elif primary == TaskIntent.SCHEDULING:
            context.metadata["domain"] = "Personal Assistant"
        elif primary == TaskIntent.RESEARCH:
            context.metadata["domain"] = "Academic/Market Research"
        else:
            context.metadata["domain"] = "General Automation"


class CapabilityConstraintPass(BasePass):
    """
    Pass 3: Resolves required capabilities and collects constraints across the compilation unit.
    """
    def run(self, context: CompilationContext) -> None:
        node_metadata = context.metadata.get("node_metadata", {})
        capabilities = set()
        for meta in node_metadata.values():
            capabilities.add(meta["capability"])

        # Collect constraints
        constraints = list(context.ast.global_constraints)

        # Collect local constraints from command nodes
        def gather_local_constraints(node: ASTNode):
            if isinstance(node, (SequenceNode, ConjunctionNode)):
                gather_local_constraints(node.left)
                gather_local_constraints(node.right)
            elif isinstance(node, CommandNode):
                for c in node.constraints:
                    if c not in constraints:
                        constraints.append(c)

        gather_local_constraints(context.ast.root)

        context.metadata["required_capabilities"] = list(capabilities)
        context.metadata["constraints"] = constraints


class IRLoweringPass(BasePass):
    """
    Pass 4: Lowers AST, Symbol Table, and Metadata to the logical TaskIR.
    """
    def run(self, context: CompilationContext) -> None:
        # Determine global inputs (inputs not produced by any node in this compilation)
        global_inputs = []
        global_outputs = []
        
        for symbol in context.symbol_table.get_all_symbols():
            if symbol.symbol_type == "data":
                if not symbol.producer_node_id:
                    global_inputs.append(symbol.name)
                if not symbol.consumers:
                    global_outputs.append(symbol.name)

        # Generate unique Task ID
        task_id = f"task_{uuid.uuid4().hex[:8]}"

        # Goal is the raw input
        goal = context.raw_input.strip()

        # Heuristic Complexity Estimation
        node_metadata = context.metadata.get("node_metadata", {})
        num_nodes = len(node_metadata)
        
        if num_nodes <= 1:
            complexity = Complexity.SIMPLE
        elif num_nodes <= 3:
            complexity = Complexity.MEDIUM
        elif num_nodes <= 5:
            complexity = Complexity.COMPLEX
        else:
            complexity = Complexity.VERY_COMPLEX

        # Confidence Score calculation
        # Lower confidence if there are many unlinked symbols or generic classification
        unresolved_symbols = sum(1 for sym in context.symbol_table.get_all_symbols() if not sym.producer_node_id and sym.consumers)
        confidence = max(0.5, 1.0 - (unresolved_symbols * 0.1))

        # Build Pydantic TaskIR
        context.task_ir = TaskIR(
            task_id=task_id,
            primary_intent=context.metadata.get("primary_intent", TaskIntent.UNKNOWN),
            secondary_intent=context.metadata.get("secondary_intent"),
            domain=context.metadata.get("domain", "general"),
            user_goal=goal,
            inputs=global_inputs,
            outputs=global_outputs,
            constraints=context.metadata.get("constraints", []),
            required_capabilities=context.metadata.get("required_capabilities", []),
            estimated_complexity=complexity,
            confidence_score=confidence,
            metadata={
                "raw_query": context.raw_input,
                "node_count": num_nodes
            }
        )


class DAGLoweringPass(BasePass):
    """
    Pass 5: Lowering the TaskIR to the physical ExecutionDAG, building nodes,
    adding dependencies, performing cycle detection, and topological sorting.
    """
    def run(self, context: CompilationContext) -> None:
        if not context.task_ir:
            context.errors.append("IR lowering must be completed before DAG lowering.")
            return

        node_metadata = context.metadata.get("node_metadata", {})
        nodes: List[ExecutionNode] = []
        dependencies: List[Dependency] = []

        # 1. Lower execution nodes
        def build_execution_nodes(node: ASTNode):
            if isinstance(node, (SequenceNode, ConjunctionNode)):
                build_execution_nodes(node.left)
                build_execution_nodes(node.right)
            elif isinstance(node, CommandNode):
                meta = node_metadata.get(id(node))
                if not meta:
                    return

                node_id = meta["node_id"]
                cap = meta["capability"]
                resolved_inputs = meta.get("inputs", [])
                resolved_outputs = meta.get("outputs", [])

                # Parallelizable heuristic
                parallelizable = cap not in (Capability.PDF_GENERATION, Capability.REPORT_GENERATION, Capability.EMAIL)

                # Cost and time heuristics
                estimated_time = 5.0
                if cap == Capability.WEB_SEARCH:
                    estimated_time = 10.0
                elif cap in (Capability.PDF_GENERATION, Capability.REPORT_GENERATION):
                    estimated_time = 15.0

                exec_node = ExecutionNode(
                    node_id=node_id,
                    name=f"{node.action_verb.capitalize()} Node",
                    description=node.raw_text,
                    capability=cap,
                    input=resolved_inputs,
                    output=resolved_outputs,
                    status=NodeStatus.PENDING,
                    estimated_cost=0.01 if cap == Capability.WEB_SEARCH else 0.0,
                    estimated_time=estimated_time,
                    parallelizable=parallelizable
                )
                nodes.append(exec_node)

        build_execution_nodes(context.ast.root)

        # 2. Extract dependencies
        # Strategy A: Dataflow dependencies from Symbol Table
        for symbol in context.symbol_table.get_all_symbols():
            if symbol.producer_node_id:
                for consumer in symbol.consumers:
                    if symbol.producer_node_id != consumer:
                        dependencies.append(Dependency(source=symbol.producer_node_id, target=consumer))

        # Strategy B: Control flow dependencies from AST Structure (SequenceNode)
        def build_control_dependencies(node: ASTNode) -> Tuple[List[str], List[str]]:
            """
            Returns (first_nodes, last_nodes) in the subgraph of node.
            """
            if isinstance(node, CommandNode):
                node_id = node_metadata[id(node)]["node_id"]
                return [node_id], [node_id]

            elif isinstance(node, ConjunctionNode):
                left_first, left_last = build_control_dependencies(node.left)
                right_first, right_last = build_control_dependencies(node.right)
                return left_first + right_first, left_last + right_last

            elif isinstance(node, SequenceNode):
                left_first, left_last = build_control_dependencies(node.left)
                right_first, right_last = build_control_dependencies(node.right)
                for l_node in left_last:
                    for r_node in right_first:
                        dependencies.append(Dependency(source=l_node, target=r_node))
                return left_first, right_last

            return [], []

        build_control_dependencies(context.ast.root)

        # De-duplicate dependencies
        unique_deps: Dict[Tuple[str, str], Dependency] = {}
        for dep in dependencies:
            key = dep.to_tuple()
            unique_deps[key] = dep
        dependencies = list(unique_deps.values())

        # 3. Create graph for Cycle & Topological checks using networkx
        g = nx.DiGraph()
        # Add all node IDs to graph
        for node in nodes:
            g.add_node(node.node_id)
        # Add dependency edges
        for dep in dependencies:
            if dep.source not in g:
                context.errors.append(f"Dependency source '{dep.source}' refers to an invalid node.")
                return
            if dep.target not in g:
                context.errors.append(f"Dependency target '{dep.target}' refers to an invalid node.")
                return
            g.add_edge(dep.source, dep.target)

        # Check for cycles
        if not nx.is_directed_acyclic_graph(g):
            cycle = nx.find_cycle(g)
            cycle_str = " -> ".join(f"{u}->{v}" for u, v in cycle)
            context.errors.append(f"Dependency cycle detected in execution graph: {cycle_str}")
            return

        # Perform topological sorting
        topological_order = list(nx.topological_sort(g))

        # Build ExecutionDAG
        context.execution_dag = ExecutionDAG(
            nodes=nodes,
            dependencies=dependencies,
            topological_order=topological_order
        )
