import json
from typing import Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class Serializer:
    """
    Standard serializer mapping cluster messages to/from JSON strings.
    """
    @staticmethod
    def serialize(message: BaseModel) -> str:
        return message.model_dump_json()

    @staticmethod
    def deserialize(data: str, cls: Type[T]) -> T:
        return cls.model_validate_json(data)
