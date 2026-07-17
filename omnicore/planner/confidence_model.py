from typing import Optional
from omnicore.ir.models import TaskIR
from omnicore.memory.procedural_memory import ProceduralMemory
from omnicore.memory.similarity import calculate_similarity

class PlannerConfidenceModel:
    """
    Predicts probability of success and overall confidence of a task execution,
    learning and adjusting based on historical records.
    """
    @staticmethod
    def predict_confidence(task_ir: TaskIR, memory: Optional[ProceduralMemory] = None) -> float:
        base_confidence = task_ir.confidence_score
        
        if memory is None:
            return round(base_confidence, 4)

        try:
            # Query similar historical records from storage
            records = memory.repository.list_records()
            if not records:
                return round(base_confidence, 4)

            # Find matching records by structural similarity
            matching_records = []
            for record in records:
                sim = calculate_similarity(task_ir, record.task_ir)
                if sim >= 0.85:
                    matching_records.append(record)

            if matching_records:
                # Average historical success rate
                avg_success = sum(r.success_rate for r in matching_records) / len(matching_records)
                # Weighted blend (70% compiler base estimate, 30% historical performance)
                predicted = (0.70 * base_confidence) + (0.30 * avg_success)
                return round(predicted, 4)
                
        except Exception:
            pass

        return round(base_confidence, 4)
