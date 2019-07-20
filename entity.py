from __future__ import annotations

from typing import Any, Dict, Iterable, Type, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from component import Component

T = TypeVar("T")


class Entity:
    """Object used to tie a variety of components to a location on a GameMap."""

    def __init__(self, components: Iterable[Component] = ()):
        self._components: Dict[Any, Any] = {}
        for component in components:
            self[component.component_type] = component

    def __getitem__(self, key: Type[T]) -> T:
        component: T = self._components[key]
        return component

    def __setitem__(self, key: Type[T], value: T) -> None:
        self._components[key] = value

    def __delitem__(self, key: Type[T]) -> None:
        del self._components[key]

    def __contains__(self, key: Type[T]) -> bool:
        return key in self._components
