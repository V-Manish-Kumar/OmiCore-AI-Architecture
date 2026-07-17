import re
from typing import Set, List
from omnicore.ir.models import TaskIR

def generate_signature(task_ir: TaskIR) -> str:
    """
    Generates a deterministic string signature representing the structure and capabilities
    of a TaskIR. Matches identical semantics under different names.
    """
    intent_val = task_ir.primary_intent.value
    sorted_caps = sorted(c.value for c in task_ir.required_capabilities)
    sorted_constraints = sorted(task_ir.constraints)
    
    # Hash-friendly normalized signature
    return f"intent:{intent_val}|caps:{','.join(sorted_caps)}|constraints:{','.join(sorted_constraints)}"

def _get_normalized_keywords(text: str) -> Set[str]:
    """Cleans text and extracts core semantic keyword tokens, removing stop words."""
    # Clean string
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    words = text.split()
    
    # Stop words list
    stop_words = {
        "the", "a", "an", "this", "that", "of", "and", "or", "but", "in", "on", 
        "at", "to", "for", "with", "is", "are", "was", "were", "be", "been", "have", "has"
    }
    
    # Semantic mapping for synonyms
    synonym_map = {
        "search": "find", "retrieve": "find", "fetch": "find", "get": "find",
        "summarize": "summary", "summarisation": "summary", "condense": "summary",
        "compare": "comparison", "correlation": "comparison", "correlate": "comparison",
        "write": "generate", "create": "generate", "pdf": "document", "report": "document"
    }
    
    keywords = set()
    for w in words:
        if w not in stop_words:
            # Map synonyms to normalize wording differences
            mapped = synonym_map.get(w, w)
            keywords.add(mapped)
    return keywords

def calculate_similarity(t1: TaskIR, t2: TaskIR) -> float:
    """
    Calculates a similarity score between 0.0 and 1.0 for two TaskIRs using:
    - Intent match (30% weight)
    - Capability overlap Jaccard index (40% weight)
    - Word keyword Jaccard index (20% weight)
    - Constraints Jaccard index (10% weight)
    """
    # 1. Intent similarity
    intent_score = 0.0
    if t1.primary_intent == t2.primary_intent:
        intent_score = 1.0
        # Boost slightly if secondary intents match
        if t1.secondary_intent and t1.secondary_intent == t2.secondary_intent:
            intent_score = 1.0
        elif not t1.secondary_intent and not t2.secondary_intent:
            intent_score = 1.0
        else:
            intent_score = 0.9

    # 2. Capability overlap Jaccard
    cap_set1 = set(t1.required_capabilities)
    cap_set2 = set(t2.required_capabilities)
    if not cap_set1 and not cap_set2:
        cap_score = 1.0
    else:
        cap_score = len(cap_set1.intersection(cap_set2)) / len(cap_set1.union(cap_set2))

    # 3. Normalized Goal text keyword overlap
    words1 = _get_normalized_keywords(t1.user_goal)
    words2 = _get_normalized_keywords(t2.user_goal)
    if not words1 and not words2:
        word_score = 1.0
    else:
        word_score = len(words1.intersection(words2)) / len(words1.union(words2))

    # 4. Constraints overlap Jaccard
    const1 = set(t1.constraints)
    const2 = set(t2.constraints)
    if not const1 and not const2:
        const_score = 1.0
    else:
        const_score = len(const1.intersection(const2)) / len(const1.union(const2))

    # Weighted sum
    total_score = (
        (0.30 * intent_score) +
        (0.40 * cap_score) +
        (0.20 * word_score) +
        (0.10 * const_score)
    )
    return round(total_score, 4)
