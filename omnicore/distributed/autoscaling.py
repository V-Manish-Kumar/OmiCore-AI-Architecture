from typing import Dict, Any, List

class Autoscaler:
    """
    Decides when to trigger worker scale-up or scale-down events based on queue depths.
    """
    def __init__(self, scale_up_threshold: int = 4, scale_down_idle_count: int = 1):
        self.scale_up_threshold = scale_up_threshold
        self.scale_down_idle_count = scale_down_idle_count
        self.scale_actions: List[str] = []

    def evaluate(self, queue_depth: int, active_workers: List[Dict[str, Any]]) -> List[str]:
        actions = []
        
        # 1. Scale up check: queue backlog is large
        if queue_depth >= self.scale_up_threshold:
            msg = f"ScaleUpTriggered: Queue depth {queue_depth} exceeds threshold {self.scale_up_threshold}."
            actions.append(msg)
            self.scale_actions.append(msg)

        # 2. Scale down check: idle worker count is high
        idle_count = 0
        for w in active_workers:
            if w.get("active_tasks", 0) == 0:
                idle_count += 1
                
        if idle_count > self.scale_down_idle_count and len(active_workers) > 1:
            msg = f"ScaleDownTriggered: Idle workers count {idle_count} exceeds threshold {self.scale_down_idle_count}."
            actions.append(msg)
            self.scale_actions.append(msg)

        return actions
