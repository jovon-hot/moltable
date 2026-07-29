"""Repository abstract base class for CRUD operations"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class Repository(ABC):
    """Abstract repository — defines the contract for memory persistence"""

    @abstractmethod
    def insert(self, user_id: str, content: str, embedding: List[float],
               category: str = "fact", source: str = "manual",
               confidence: float = 1.0, tags: List[str] | None = None) -> Dict:
        ...

    @abstractmethod
    def get(self, memory_id: str, user_id: str) -> Optional[Dict]:
        ...

    @abstractmethod
    def list(self, user_id: str, category: Optional[str] = None,
             limit: int = 50) -> List[Dict]:
        ...

    @abstractmethod
    def update(self, memory_id: str, user_id: str, **kwargs) -> bool:
        ...

    @abstractmethod
    def delete(self, memory_id: str, user_id: str) -> bool:
        ...

    @abstractmethod
    def search(self, user_id: str, query_embedding: List[float],
               top_k: int = 5, threshold: float = 0.5,
               category: Optional[str] = None) -> List[Dict]:
        ...

    @abstractmethod
    def find_conflicts(self, user_id: str, query_embedding: List[float],
                       top_k: int = 3) -> List[Dict]:
        ...

    @abstractmethod
    def stats(self, user_id: str) -> Dict:
        ...

    @abstractmethod
    def migrate_user(self, from_user_id: str, to_user_id: str) -> int:
        ...
