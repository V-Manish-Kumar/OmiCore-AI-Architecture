from typing import List, Set
from omnicore.execution.execution_plan import ExecutionPlan
from omnicore.execution.execution_node import RuntimeNodeStatus
from omnicore.runtime.runtime_state import RuntimeState

class RuntimeScheduler:
    """
    Evaluates execution dependencies based on completed tasks to determine next runnable nodes.
    """
    def __init__(self, plan: ExecutionPlan):
        self.plan = plan

    def get_ready_nodes(self, state: RuntimeState) -> List[str]:
        """
        Returns a list of node IDs that are Ready (Pending and all dependencies are Completed).
        """
        ready_nodes = []
        completed_nodes = {nid for nid, status in state.node_statuses.items() if status == RuntimeNodeStatus.COMPLETED}
        
        # Build predecessor map
        pred_map = {nid: set() for nid in self.plan.nodes}
        for dep in self.plan.dependencies:
            pred_map[dep.target].add(dep.source)

        for nid, status in state.node_statuses.items():
            if status != RuntimeNodeStatus.PENDING:
                continue
            
            # Check dependencies
            preds = pred_map.get(nid, set())
            if preds.issubset(completed_nodes):
                ready_nodes.append(nid)

        return ready_nodes

    def check_cascade_failures(self, state: RuntimeState) -> List[str]:
        """
        Identifies nodes that can never run because one of their dependencies failed or was cancelled.
        Transitions their status to FAILED or CANCELLED in state.
        Returns the list of transitioned node IDs.
        """
        transitioned = []
        failed_or_cancelled = {
            nid for nid, status in state.node_statuses.items() 
            if status in (RuntimeNodeStatus.FAILED, RuntimeNodeStatus.CANCELLED)
        }
        
        # Build predecessor map
        pred_map = {nid: set() for nid in self.plan.nodes}
        for dep in self.plan.dependencies:
            pred_map[dep.target].add(dep.source)

        changed = True
        while changed:
            changed = False
            for nid, status in state.node_statuses.items():
                if status != RuntimeNodeStatus.PENDING:
                    continue
                
                preds = pred_map.get(nid, set())
                # If any predecessor is failed or cancelled
                if preds.intersection(failed_or_cancelled):
                    # Transition to FAILED/CANCELLED depending on reason (we'll use FAILED by default)
                    state.node_statuses[nid] = RuntimeNodeStatus.FAILED
                    node_state = state.node_states[nid]
                    node_state.status = RuntimeNodeStatus.FAILED
                    node_state.error_message = "Dependency execution failed."
                    
                    failed_or_cancelled.add(nid)
                    transitioned.append(nid)
                    changed = True
                    
        return transitioned
