# coding=utf-8
from __future__ import annotations

from typing import Optional
from typing import TYPE_CHECKING

from attrs import define, field, validators

from transpiler.core.enums import ClassType, DataTypeBase
from .base import NewSymbol

if TYPE_CHECKING:
    from . import Reference,Constant,Function,Variable


@define(slots=True)
class Class(NewSymbol, DataTypeBase):
    name: str = field(validator=validators.instance_of(str))
    methods: set[Function] = field(validator=validators.instance_of(set))
    interface: Optional[Class] = field(validator=validators.instance_of(Optional[DataTypeBase]))
    parent: Optional[Class] = field(validator=validators.instance_of(Optional[DataTypeBase]))
    constants: set[Reference[Constant]] = field(validator=validators.instance_of(set))
    variables: set[Reference[Variable]] = field(validator=validators.instance_of(set))
    type: ClassType = field(default=ClassType.CLASS, validator=validators.instance_of(ClassType))

    def get_name(self) -> str:
        return self.name

    def __hash__(self):
        return hash((self.name, tuple(self.methods), id(self.interface), id(self.parent), tuple(self.constants),
                     tuple(self.variables), self.type))
