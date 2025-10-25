from abc import ABC, abstractmethod
from typing import Any, Type, TypeVar

_T = TypeVar("_T")

class Codec(ABC):
    """Base interface for all dataclass codecs."""
    
    @abstractmethod
    def encode(self, obj: Any, **kwargs: Any) -> Any:
        """Encode a dataclass instance to the target format."""
        pass
    
    @abstractmethod
    def decode(self, cls: Type[_T], data: Any, **kwargs: Any) -> _T:
        """Decode data to a dataclass instance."""
        pass
