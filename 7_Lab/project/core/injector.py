from typing import Type, TypeVar, Dict, Any, Callable, Optional
import contextlib
from .lifecycle import LifeStyle

T = TypeVar('T')

class Injector:
    def __init__(self):
        self._registrations: Dict[Type, Dict[str, Any]] = {}
        self._singleton_instances: Dict[Type, Any] = {}
        self._scoped_instances: Dict[Type, Any] = {}
        self._in_scope = False

    def register(self,
               interface_type: Type[T],
               implementation: Type[T] | Callable[..., T],
               life_style: LifeStyle = LifeStyle.PER_REQUEST,
               params: Optional[Dict[str, Any]] = None) -> None:
        pass

    def get_instance(self, interface_type: Type[T]) -> T:
        pass

    @contextlib.contextmanager
    def scope(self):
        pass