import re
from typing import List, Optional
import networkx as nx

class EntityResolver:
    """
    Resolves pronoun references (e.g. 'it', 'them', 'the report') to concrete entities
    using chronological context, action verb hints, and Knowledge Graph types.
    """
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def resolve_reference(self, query: str, symbol_context: List[str]) -> Optional[str]:
        """
        Resolves pronouns in query using recency and semantic verb matching.
        """
        query_lower = query.lower()
        
        # Identify if query contains referencing pronouns or nouns
        pronoun_pattern = re.compile(r"\b(it|them|this|that|file|report|summary|result|document)\b")
        if not pronoun_pattern.search(query_lower):
            # Check if query directly references any symbol name
            for symbol in symbol_context:
                if symbol.lower() in query_lower:
                    return symbol
            return None

        if not symbol_context:
            return None

        # Determine semantic verb targets
        is_delivery = any(v in query_lower for v in ["email", "send", "mail", "dispatch", "export"])
        is_analysis = any(v in query_lower for v in ["summarize", "summarise", "condense", "analyze", "compare"])

        # Prioritize candidates from context in reverse order (most recent first)
        candidates = list(reversed(symbol_context))

        # Pass 1: Delivery action - strictly check for physical files or PDFs first
        if is_delivery:
            for cand in candidates:
                if self.graph.has_node(cand):
                    attrs = self.graph.nodes[cand]
                    entity_type = attrs.get("entity_type", "")
                    name = attrs.get("name", cand).lower()
                    if entity_type == "file" or "pdf" in name:
                        return cand
            # Fallback to general summaries if no files exist
            for cand in candidates:
                if self.graph.has_node(cand):
                    attrs = self.graph.nodes[cand]
                    name = attrs.get("name", cand).lower()
                    if "summary" in name:
                        return cand

        # Pass 2: Analysis action - strictly check for source files first
        if is_analysis:
            for cand in candidates:
                if self.graph.has_node(cand):
                    attrs = self.graph.nodes[cand]
                    entity_type = attrs.get("entity_type", "")
                    name = attrs.get("name", cand).lower()
                    if entity_type == "file" or any(ext in name for ext in ["csv", "doc", "txt", "pdf"]):
                        return cand

        # General/Default Fallback Pass
        for cand in candidates:
            # Fetch node attributes from NetworkX graph
            node_type = ""
            node_name = cand.lower()
            entity_type = ""
            
            if self.graph.has_node(cand):
                node_attrs = self.graph.nodes[cand]
                node_type = node_attrs.get("type", "")
                entity_type = node_attrs.get("entity_type", "")
                node_name = node_attrs.get("name", cand).lower()

            # Rule 1: Email/delivery actions
            if is_delivery:
                if entity_type == "file" or "pdf" in node_name or "summary" in node_name:
                    return cand

            # Rule 2: Analysis/Summarize actions
            if is_analysis:
                if entity_type == "file" or "csv" in node_name or "doc" in node_name or "txt" in node_name:
                    return cand

            # Default structural entity match
            if node_type == "entity" or entity_type in ["file", "symbol", "parameter"]:
                return cand

        # Fallback to the absolute most recent symbol in context
        return symbol_context[-1]
