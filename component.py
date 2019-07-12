from __future__ import annotations

from typing import Any, ClassVar, Type


class Component:
    component_type: ClassVar[Type[Component]]

    def __init_subclass__(cls, base_component: bool = False, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)  # type: ignore
        if base_component:
            cls.component_type = cls
