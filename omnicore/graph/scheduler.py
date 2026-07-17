from typing import List, Dict, Any
from omnicore.graph.execution_graph import ExecutionGraph

class TaskScheduler:
    """
    Schedules execution nodes by stage analysis, identifies parallel groups,
    and isolates critical paths.
    """
    def __init__(self, graph: ExecutionGraph):
        self.graph = graph

    def get_schedule_stages(self) -> List[List[str]]:
        """Returns the list of execution stages, where each stage is a list of node IDs."""
        return self.graph.generate_execution_stages()

    def get_parallel_groups(self) -> List[List[str]]:
        """
        Groups nodes within each stage that are marked parallelizable together.
        Non-parallelizable nodes are grouped individually to run sequentially.
        """
        stages = self.get_schedule_stages()
        parallel_groups: List[List[str]] = []
        
        for stage in stages:
            stage_parallelizable = []
            for node_id in stage:
                node = self.graph.get_node(node_id)
                if node and node.parallelizable:
                    stage_parallelizable.append(node_id)
                else:
                    # Non-parallelizable nodes run on their own
                    parallel_groups.append([node_id])
            
            # If there are parallelizable nodes in the stage, they form a group
            if stage_parallelizable:
                parallel_groups.append(stage_parallelizable)
                
        return parallel_groups

    def get_critical_path(self) -> List[str]:
        """Calculates the sequence of node IDs along the critical execution path."""
        return self.graph.critical_path()
