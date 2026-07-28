import re
from typing import List, Tuple
from omnicore.ast.ast_nodes import ASTNode, CommandNode, ConjunctionNode, SequenceNode, ParameterNode, ProgramAST

class ASTParser:
    """
    Parser that tokenizes and parses natural language instructions into an AST.
    """

    SEQUENCING_KEYWORDS = [
        r"\band then\b",
        r"\bthen\b",
        r"\bafter that\b",
        r"\bsubsequently\b",
        r"\bfollowed by\b",
        r"\bnext\b",
        r"\bafter which\b",
    ]

    CONJUNCTION_KEYWORDS = [
        r"\bwhile\b",
        r"\bsimultaneously\b",
        r"\bin parallel\b",
    ]

    VERBS = {
        "search": ["search", "searching", "searches", "research", "reasearch", "researching", "reasearching", "find", "finding", "finds", "query", "querying", "retrieve", "retrieving", "look up", "looking up", "fetch", "fetching"],
        "analyze": ["analyze", "analyzing", "analyzes", "analising", "analysing", "analysis", "analytics"],
        "compare": ["compare", "comparing", "compares", "evaluate", "evaluating", "contrast", "contrasting"],
        "summarize": ["summarize", "summarizing", "summarizes", "synthesize", "synthesizing", "condense", "condensing", "abstract", "abstracting"],
        "generate": ["generate", "generating", "generates", "create", "creating", "creates", "make", "making", "build", "building", "produce", "producing", "compile", "compiling"],
        "write": ["write", "writing", "writes", "draft", "drafting", "author", "authoring"],
        "email": ["email", "emailing", "send", "sending", "mail", "mailing"],
        "extract": ["extract", "extracting", "parse", "parsing", "scrape", "scraping"],
        "database_access": ["query database", "db search", "sql query", "fetch from database", "fetching from database"]
    }



    def parse(self, text: str) -> ProgramAST:
        """
        Parses raw query text into a ProgramAST.
        """
        if not text or not text.strip():
            return ProgramAST(
                root=CommandNode(raw_text="", action_verb="noop", target=""),
                global_constraints=[]
            )

        # 1. Detect global constraints
        global_constraints = self._extract_global_constraints(text)

        # 2. Split text into segments based on sequencing and conjunction keywords/delimiters
        segments = self._segment_text(text)

        if not segments:
            return ProgramAST(
                root=CommandNode(raw_text=text, action_verb="execute", target=text),
                global_constraints=global_constraints
            )

        # 3. Parse segments into AST nodes
        ast_nodes = [self._parse_segment(seg_text) for seg_text, _ in segments]

        # 4. Assemble the AST tree based on connector types
        root_node = ast_nodes[0]
        for i in range(1, len(ast_nodes)):
            # Use connector at index i which preceded ast_nodes[i]
            connector = segments[i][1]
            if connector == "conjunction":
                root_node = ConjunctionNode(left=root_node, right=ast_nodes[i])
            else:
                root_node = SequenceNode(left=root_node, right=ast_nodes[i])

        return ProgramAST(root=root_node, global_constraints=global_constraints)

    def _segment_text(self, text: str) -> List[Tuple[str, str]]:
        """
        Segments natural language into parts, returning a list of (segment_text, connector_type).
        """
        # If text contains newline-based list items, segment by lines
        lines = [line.strip().lstrip("-*• ").strip() for line in text.splitlines() if line.strip()]
        if len(lines) > 1:
            return [(line, "sequence") for line in lines]

        # Otherwise, segment by keywords and actions
        all_verbs = []
        for synonyms in self.VERBS.values():
            all_verbs.extend(synonyms)
        all_verbs.sort(key=len, reverse=True)

        temp_text = text
        for kw in self.SEQUENCING_KEYWORDS:
            temp_text = re.sub(kw, "||SEQ||", temp_text, flags=re.IGNORECASE)
        for kw in self.CONJUNCTION_KEYWORDS:
            temp_text = re.sub(kw, "||CONJ||", temp_text, flags=re.IGNORECASE)

        # Detect verb boundaries preceded by commas, "and", "by", "via", "through", "with", "using"
        for verb in all_verbs:
            temp_text = re.sub(rf",\s*(?:and\s+)?({re.escape(verb)})\b", r"||SEQ|| \1", temp_text, flags=re.IGNORECASE)
            temp_text = re.sub(rf"\b(?:and|by|via|through|with\s+help\s+of|with\s+the\s+help\s+of|with|using)\s+({re.escape(verb)})\b", r"||SEQ|| \1", temp_text, flags=re.IGNORECASE)



        # Replace remaining semicolons or periods with ||SEQ||
        temp_text = re.sub(r"[;.]", "||SEQ||", temp_text)

        # Split on placeholders
        parts = re.split(r"(\|\|SEQ\|\||\|\|CONJ\|\|)", temp_text)

        segments: List[Tuple[str, str]] = []
        current_connector = "sequence"

        for part in parts:
            part_str = part.strip()
            if not part_str:
                continue

            if part_str == "||SEQ||":
                current_connector = "sequence"
            elif part_str == "||CONJ||":
                current_connector = "conjunction"
            else:
                cleaned = re.sub(r"^,\s*|\s*,$", "", part_str).strip()
                if cleaned:
                    segments.append((cleaned, current_connector))
                    current_connector = "sequence"

        # Check for multi-intent AI dynamic decomposition if single segment returned
        if len(segments) == 1:
            decomposed = self._decompose_implicit_pipeline(segments[0][0])
            if decomposed and len(decomposed) > 1:
                return [(s, "sequence") for s in decomposed]

        # Expand multi-segment pipelines where retrieval leads into summary/pdf generation
        expanded_segments: List[Tuple[str, str]] = []
        for i, (seg_text, conn) in enumerate(segments):
            seg_lower = seg_text.lower()
            if i > 0 and expanded_segments:
                prev_text = expanded_segments[-1][0].lower()
                prev_is_retrieval = any(k in prev_text for k in ["search", "research", "find", "query", "fetch", "google"])
                curr_is_generation = any(k in seg_lower for k in ["pdf", "write", "generate", "create", "email"])
                curr_is_synthesis = any(k in seg_lower for k in ["summarize", "analyze", "compare", "synthesize"])
                mentions_summary = any(k in seg_lower for k in ["summary", "pdf summary", "information", "analysis"])

                if prev_is_retrieval and curr_is_generation and mentions_summary and not curr_is_synthesis:
                    synthesis_seg = "summarize research findings"
                    if "compare" in seg_lower or "vs" in seg_lower:
                        synthesis_seg = "compare research findings"
                    elif "analyze" in seg_lower:
                        synthesis_seg = "analyze research findings"
                    expanded_segments.append((synthesis_seg, "sequence"))

            expanded_segments.append((seg_text, conn))

        return expanded_segments

    def _decompose_implicit_pipeline(self, text: str) -> List[str]:
        """
        Dynamically decomposes a single prompt string containing implicit multi-step goals
        (e.g., retrieval + synthesis + document generation) into ordered execution segments.
        """
        text_lower = text.lower()

        # Check for retrieval intents
        has_retrieval = any(k in text_lower for k in ["search", "research", "find", "query", "fetch", "retrieve", "google"])
        # Check for synthesis/analysis intents
        has_synthesis = any(k in text_lower for k in ["information", "info", "summarize", "analyze", "compare", "findings", "details"])
        # Check for generation/delivery intents
        has_generation = any(k in text_lower for k in ["pdf", "report", "create", "generate", "write", "email", "document"])

        # If prompt specifies both retrieval and document/generation outputs
        if has_retrieval and has_generation:
            # Extract topic/query subject
            # Remove high-level verbs to isolate subject
            clean_text = text
            clean_text = re.sub(r"\b(?:create|generate|write|make|build|produce)\s+(?:a|an)?\s*(?:pdf|report|document|summary)?\s*(?:that|which)?\s*(?:contains|includes|has)?", "", clean_text, flags=re.IGNORECASE)

            # Build pipeline phases: Retrieval -> Data Analysis -> Summarization -> Generation
            retrieval_seg = f"search {clean_text.strip()}" if not clean_text.lower().startswith(("search", "find", "query")) else clean_text.strip()
            
            analysis_seg = "analyze research data"
            synthesis_seg = "summarize information"
            if "compare" in text_lower or "vs" in text_lower:
                synthesis_seg = "compare research findings"

            generation_seg = "create a pdf"
            if "pdf" in text_lower:
                generation_seg = "create a pdf"
            elif "email" in text_lower:
                generation_seg = "send email report"
            elif "report" in text_lower:
                generation_seg = "write a report"

            return [retrieval_seg, analysis_seg, synthesis_seg, generation_seg]

        return [text]

    def _parse_segment(self, segment: str) -> CommandNode:
        """
        Parses a single cleaned text segment into a CommandNode.
        """
        seg_lower = segment.lower()
        action_verb = "execute"
        matched_category = "execute"

        # Find action verb by selecting the match that appears earliest in the segment text
        best_match_pos = float('inf')
        for category, synonyms in self.VERBS.items():
            for syn in synonyms:
                match = re.search(rf"\b{re.escape(syn)}\b", seg_lower)
                if match:
                    pos = match.start()
                    if pos < best_match_pos:
                        best_match_pos = pos
                        action_verb = syn
                        matched_category = category

        # Remove the verb from target to isolate the object of action
        target = segment
        if action_verb != "execute":
            target = re.sub(rf"^\s*{action_verb}\b(?:\s+(?:for|to|at|in|on|with|from|the|top))?", "", segment, flags=re.IGNORECASE).strip()

        # Extract parameters
        parameters = []
        limit_match = re.search(r"\b(?:top|limit)\s+(?:five|ten|\d+)\b", segment, re.IGNORECASE)
        if limit_match:
            val_str = re.search(r"(?:five|ten|\d+)", limit_match.group(0), re.IGNORECASE).group(0)
            val = {"five": "5", "ten": "10"}.get(val_str.lower(), val_str)
            parameters.append(ParameterNode(name="limit", value=val))

        inputs = []
        outputs = []

        # All keywords that could be inputs or outputs
        keywords = ["findings", "results", "repositories", "data", "info", "information", "documents", "summary", "comparison", "report", "pdf", "email"]

        # Parse inputs by checking words following input prepositions: "using", "with", "from", "of"
        input_matches = re.findall(r"\b(?:using|with|from|of)\s+([a-z0-9_\s]{1,30})\b", seg_lower)
        for match in input_matches:
            for kw in keywords:
                if kw in match:
                    inputs.append(kw)

        # Parse outputs by checking words following output verbs/prepositions: "generate", "create", "write", "to", "produce"
        output_matches = re.findall(r"\b(?:generate|create|write|to|produce|into)\s+([a-z0-9_\s]{1,30})\b", seg_lower)
        for match in output_matches:
            for kw in keywords:
                if kw in match:
                    outputs.append(kw)

        # Fallback keyword scan if no inputs/outputs matched by patterns
        if not inputs and not outputs:
            for kw in keywords:
                if re.search(rf"\b{kw}\b", seg_lower):
                    if kw in ["pdf", "report", "summary", "email"]:
                        outputs.append(kw)
                    else:
                        inputs.append(kw)
        else:
            if not inputs:
                for kw in keywords:
                    if kw not in outputs and re.search(rf"\b{kw}\b", seg_lower):
                        inputs.append(kw)
            if not outputs:
                for kw in keywords:
                    if kw not in inputs and re.search(rf"\b{kw}\b", seg_lower):
                        if kw in ["pdf", "report", "summary", "email", "comparison"]:
                            outputs.append(kw)

        # De-duplicate
        inputs = list(dict.fromkeys(inputs))
        outputs = list(dict.fromkeys(outputs))

        # Extract local constraints
        constraints = []
        format_match = re.search(r"\b(?:in|using)\s+(python|markdown|latex|json|csv)\b", segment, re.IGNORECASE)
        if format_match:
            constraints.append(format_match.group(0))

        return CommandNode(
            raw_text=segment,
            action_verb=matched_category,
            target=target,
            inputs=inputs,
            outputs=outputs,
            constraints=constraints,
            parameters=parameters
        )

    def _extract_global_constraints(self, text: str) -> List[str]:
        """
        Extracts global constraints from the prompt.
        """
        constraints = []
        text_lower = text.lower()

        if "pdf" in text_lower:
            constraints.append("Output must be PDF format")
        if "markdown" in text_lower or "md" in text_lower:
            constraints.append("Output must be Markdown format")
        if "latest" in text_lower:
            constraints.append("Use latest information")

        max_len_match = re.search(r"\b(?:max|maximum)\s+(\d+|one|two|three)\s*(?:pages|paragraphs|words|sentences)\b", text_lower)
        if max_len_match:
            constraints.append(f"Length constraint: {max_len_match.group(0)}")

        return constraints
