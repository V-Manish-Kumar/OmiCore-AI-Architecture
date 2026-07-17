class KnowledgeError(ValueError):
    """Base exception for all Knowledge Graph errors."""
    pass

class OntologyValidationError(KnowledgeError):
    """Raised when data added to the Knowledge Graph violates the ontology constraints."""
    pass
