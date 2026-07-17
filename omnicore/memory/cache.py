from collections import OrderedDict
from typing import Dict, Any, Optional
from omnicore.models.cached_plan import CachedPlan

class PlanLRUCache:
    """
    In-memory Least Recently Used (LRU) Cache for execution plans.
    Tracks hit/miss statistics and enforces eviction on capacity limits.
    """
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.cache: OrderedDict[str, CachedPlan] = OrderedDict()
        
        # Stats
        self.hits = 0
        self.misses = 0

    def get(self, plan_id: str) -> Optional[CachedPlan]:
        """
        Retrieves a plan from the cache. Updates LRU order on hit.
        """
        if plan_id in self.cache:
            self.hits += 1
            # Move to end to mark as most recently used
            self.cache.move_to_end(plan_id)
            return self.cache[plan_id]
        
        self.misses += 1
        return None

    def put(self, plan: CachedPlan) -> None:
        """
        Saves a plan in the cache. Evicts LRU item if capacity is exceeded.
        """
        plan_id = plan.plan_id
        if plan_id in self.cache:
            self.cache[plan_id] = plan
            self.cache.move_to_end(plan_id)
        else:
            self.cache[plan_id] = plan
            if len(self.cache) > self.capacity:
                # Pop least recently used item (first item in OrderedDict)
                self.cache.popitem(last=False)

    def invalidate(self, plan_id: str) -> None:
        """Removes a plan from the cache."""
        if plan_id in self.cache:
            del self.cache[plan_id]

    def clear(self) -> None:
        """Clears the cache and resets stats."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_statistics(self) -> Dict[str, Any]:
        """Returns cache metric statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total) if total > 0 else 0.0
        return {
            "current_size": len(self.cache),
            "capacity": self.capacity,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate, 4)
        }
class EmptyCache(PlanLRUCache):
    """Fallback cache of zero capacity."""
    def __init__(self):
        super().__init__(capacity=0)
    def put(self, plan: CachedPlan) -> None:
        pass
