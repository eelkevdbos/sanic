from __future__ import annotations

from collections import deque
from enum import IntEnum, auto
from itertools import count
from typing import Deque, Optional, Sequence, Union

from sanic.models.handler_types import MiddlewareType


class MiddlewareLocation(IntEnum):
    REQUEST = auto()
    RESPONSE = auto()


class Middleware:
    counter = count()

    __slots__ = ("func", "priority", "location", "definition")

    def __init__(
        self,
        func: MiddlewareType,
        location: MiddlewareLocation,
        priority: int = 0,
    ) -> None:
        self.func = func
        self.priority = priority
        self.location = location
        self.definition = next(Middleware.counter)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __repr__(self) -> str:
        name = getattr(self.func, "__name__", str(self.func))
        return (
            f"{self.__class__.__name__}("
            f"func=<function {name}>, "
            f"priority={self.priority}, "
            f"location={self.location.name})"
        )

    @property
    def order(self):
        return (self.priority, -self.definition)

    @classmethod
    def convert(
        cls,
        *middleware_collections: Sequence[Union[Middleware, MiddlewareType]],
        location: MiddlewareLocation,
    ) -> Deque[Middleware]:
        return deque(
            [
                middleware
                if isinstance(middleware, Middleware)
                else Middleware(middleware, location)
                for collection in middleware_collections
                for middleware in collection
            ]
        )