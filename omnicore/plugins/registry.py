from typing import Dict, Any, Optional

class PluginRegistry:
    """
    Extensible plugin manager allowing registration of custom optimization passes,
    schedulers, planners, and cost models without editing the core system.
    """
    _instance: Optional["PluginRegistry"] = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PluginRegistry, cls).__new__(cls)
            cls._instance.optimizer_passes = {}
            cls._instance.schedulers = {}
            cls._instance.planners = {}
            cls._instance.cost_models = {}
        return cls._instance

    @classmethod
    def get_instance(cls) -> "PluginRegistry":
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def register_optimizer_pass(self, name: str, pass_class: Any) -> None:
        self.optimizer_passes[name] = pass_class

    def get_optimizer_pass(self, name: str) -> Optional[Any]:
        return self.optimizer_passes.get(name)

    def register_scheduler(self, name: str, scheduler_class: Any) -> None:
        self.schedulers[name] = scheduler_class

    def get_scheduler(self, name: str) -> Optional[Any]:
        return self.schedulers.get(name)

    def register_planner(self, name: str, planner_class: Any) -> None:
        self.planners[name] = planner_class

    def get_planner(self, name: str) -> Optional[Any]:
        return self.planners.get(name)

    def register_cost_model(self, name: str, cost_model_class: Any) -> None:
        self.cost_models[name] = cost_model_class

    def get_cost_model(self, name: str) -> Optional[Any]:
        return self.cost_models.get(name)

    def clear(self) -> None:
        self.optimizer_passes.clear()
        self.schedulers.clear()
        self.planners.clear()
        self.cost_models.clear()
