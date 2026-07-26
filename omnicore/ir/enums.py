from enum import Enum

class TaskIntent(str, Enum):
    RESEARCH = "Research"
    AUTOMATION = "Automation"
    PROGRAMMING = "Programming"
    DATA_ANALYSIS = "Data Analysis"
    WRITING = "Writing"
    SCHEDULING = "Scheduling"
    INFORMATION_RETRIEVAL = "Information Retrieval"
    UNKNOWN = "Unknown"

class Capability(str, Enum):
    WEB_SEARCH = "web_search"
    CODE_GENERATION = "code_generation"
    SUMMARIZATION = "summarization"
    COMPARISON = "comparison"
    DATA_ANALYSIS = "data_analysis"
    TRANSLATION = "translation"
    REASONING = "reasoning"
    RETRIEVAL = "retrieval"
    REPORT_GENERATION = "report_generation"
    EMAIL = "email"
    PDF_GENERATION = "pdf_generation"
    DATABASE_ACCESS = "database_access"
    UNKNOWN = "unknown"


class Complexity(str, Enum):
    SIMPLE = "Simple"
    MEDIUM = "Medium"
    COMPLEX = "Complex"
    VERY_COMPLEX = "Very Complex"

class NodeStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "InProgress"
    COMPLETED = "Completed"
    FAILED = "Failed"
    SKIPPED = "Skipped"
