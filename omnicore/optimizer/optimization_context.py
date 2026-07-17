from enum import Enum
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, ConfigDict
from omnicore.ir.enums import Capability, TaskIntent, Complexity, NodeStatus
from omnicore.ir.models import TaskIR, ExecutionNode, ExecutionDAG, Dependency

class DiagnosticSeverity(str, Enum):
    ERROR = "Error"
    WARNING = "Warning"
    SUGGESTION = "Suggestion"
    NOTE = "Note"

class Diagnostic(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    severity: DiagnosticSeverity
    pass_name: str
    message: str
    node_id: Optional[str] = None
    suggestion: Optional[str] = None

# --- Capability Descriptors ---
class CapabilityDescriptor(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    name: str
    capability_type: Capability
    required_inputs: List[str] = Field(default_factory=list)
    produced_outputs: List[str] = Field(default_factory=list)
    description: str

class SearchCapability(CapabilityDescriptor):
    name: str = "SearchCapability"
    capability_type: Capability = Capability.WEB_SEARCH
    description: str = "Query web engines and fetch search results"

class CodeGenCapability(CapabilityDescriptor):
    name: str = "CodeGenCapability"
    capability_type: Capability = Capability.CODE_GENERATION
    description: str = "Synthesize or modify executable source code"

class SummarizationCapability(CapabilityDescriptor):
    name: str = "SummarizationCapability"
    capability_type: Capability = Capability.SUMMARIZATION
    description: str = "Condense long-form text content into key takeaways"

class ComparisonCapability(CapabilityDescriptor):
    name: str = "ComparisonCapability"
    capability_type: Capability = Capability.COMPARISON
    description: str = "Correlate and find differences/similarities between inputs"

class TranslationCapability(CapabilityDescriptor):
    name: str = "TranslationCapability"
    capability_type: Capability = Capability.TRANSLATION
    description: str = "Convert text from one language/format to another"

class ReasoningCapability(CapabilityDescriptor):
    name: str = "ReasoningCapability"
    capability_type: Capability = Capability.REASONING
    description: str = "Chain-of-thought analysis and problem solving"

class RetrievalCapability(CapabilityDescriptor):
    name: str = "RetrievalCapability"
    capability_type: Capability = Capability.RETRIEVAL
    description: str = "Retrieve matching segments from localized knowledge sources"

class ReportGenerationCapability(CapabilityDescriptor):
    name: str = "ReportGenerationCapability"
    capability_type: Capability = Capability.REPORT_GENERATION
    description: str = "Format structured findings into textual documents"

class EmailCapability(CapabilityDescriptor):
    name: str = "EmailCapability"
    capability_type: Capability = Capability.EMAIL
    description: str = "Compose and transmit email messages"

class PDFGenerationCapability(CapabilityDescriptor):
    name: str = "PDFGenerationCapability"
    capability_type: Capability = Capability.PDF_GENERATION
    description: str = "Compile text and assets into a PDF document binary"

class DatabaseAccessCapability(CapabilityDescriptor):
    name: str = "DatabaseAccessCapability"
    capability_type: Capability = Capability.DATABASE_ACCESS
    description: str = "Execute structured queries against external databases"

class UnknownCapability(CapabilityDescriptor):
    name: str = "UnknownCapability"
    capability_type: Capability = Capability.UNKNOWN
    description: str = "Fallback for unrecognized or abstract task types"

# Mapping from enum to descriptor type
CAPABILITY_DESCRIPTOR_MAP: Dict[Capability, type[CapabilityDescriptor]] = {
    Capability.WEB_SEARCH: SearchCapability,
    Capability.CODE_GENERATION: CodeGenCapability,
    Capability.SUMMARIZATION: SummarizationCapability,
    Capability.COMPARISON: ComparisonCapability,
    Capability.TRANSLATION: TranslationCapability,
    Capability.REASONING: ReasoningCapability,
    Capability.RETRIEVAL: RetrievalCapability,
    Capability.REPORT_GENERATION: ReportGenerationCapability,
    Capability.EMAIL: EmailCapability,
    Capability.PDF_GENERATION: PDFGenerationCapability,
    Capability.DATABASE_ACCESS: DatabaseAccessCapability,
    Capability.UNKNOWN: UnknownCapability,
}

# --- Optimized Nodes & DAGs ---
class OptimizedExecutionNode(ExecutionNode):
    resolved_capability: Optional[CapabilityDescriptor] = None
    estimated_tokens: int = 0
    estimated_memory: float = 0.0  # in MB
    parallel_group_id: Optional[str] = None
    
    # We allow arbitrary types in metadata or fields to enable flexibility
    model_config = ConfigDict(arbitrary_types_allowed=True)

class OptimizedExecutionDAG(ExecutionDAG):
    # Override nodes list to support OptimizedExecutionNode type
    nodes: List[OptimizedExecutionNode] = Field(default_factory=list)
    stages: List[List[str]] = Field(default_factory=list)  # list of stages (each stage is a list of node_ids)
    critical_path: List[str] = Field(default_factory=list)
    estimated_runtime: float = 0.0
    estimated_cost: float = 0.0
    estimated_tokens: int = 0
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

# --- Immutable Optimizer State ---
class OptimizerState(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
    
    task_ir: TaskIR
    execution_dag: OptimizedExecutionDAG
    diagnostics: List[Diagnostic] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    passes_run: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

class OptimizationReport(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
    
    original_nodes: List[str]
    optimized_nodes: List[str]
    removed_nodes: List[str]
    merged_nodes: Dict[str, str]
    parallel_groups: List[List[str]]
    critical_path: List[str]
    estimated_runtime: float
    estimated_cost: float
    estimated_tokens: int
    optimization_passes_applied: List[str]
    warnings: List[str]
    compiler_diagnostics: List[Diagnostic]

