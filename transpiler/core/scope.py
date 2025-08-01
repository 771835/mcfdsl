# coding=utf-8
from __future__ import annotations

from transpiler.core.enums import StructureType
from transpiler.core.symbols.base import NewSymbol


class Scope:
    def __init__(self, name: str, parent: Scope | None,
                 structure_type: StructureType):
        self.name = name
        self.parent = parent
        self.type = structure_type
        self.symbols: dict[str, NewSymbol] = dict()  # 符号表（变量/函数/类）
        self.children: list[Scope] = list()  # 子作用域

    def get_name(self):
        return self.name

    def get_unique_name(self):
        if self.type == StructureType.GLOBAL or self.type is None:
            return "global"
        return self.parent.get_unique_name() + '/' + self.name

    def create_child(self, name: str, type_: StructureType) -> Scope:
        child = Scope(name, self, type_)
        self.children.append(child)
        return child

    def add_symbol(self, symbol: NewSymbol, force=False) -> bool:
        if symbol.get_name() in self.symbols and not force:
            return False
        self.symbols[symbol.get_name()] = symbol
        return True

    def has_symbol(self, name: str):
        return name in self.symbols

    def set_symbol(self, symbol: NewSymbol, force=False):
        if symbol.get_name() not in self.symbols and not force:
            raise NameError(
                f"Symbol {symbol.get_name()} does not exist in this scope")
        self.symbols[symbol.get_name()] = symbol

    def resolve_symbol(self, name: str) -> NewSymbol:
        """逐级向上查找符号"""
        name = str(name)
        current = self
        while current:
            if name in current.symbols:
                return current.symbols[name]
            current = current.parent
        raise ValueError(f"Undefined symbol: {name}")

    def find_symbol(self, name: str) -> NewSymbol:
        """只在单层查找符号"""
        name = str(name)
        if name in self.symbols:
            return self.symbols[name]
        else:
            raise ValueError(f"Undefined symbol: {name}")

    def find_scope(self, name: str) -> Scope:
        """只在单层查找作用域"""
        name = str(name)
        for i in self.children:
            if i.name == name:
                return i
        raise ValueError(f"Undefined symbol: {name}")

    def resolve_scope(self, name: str) -> Scope:
        """逐级向上查找该作用域可访问到的作用域"""
        name = str(name)
        current = self
        while current:
            if name in [i.name for i in current.children]:
                return [i for i in current.children if i.name == name][0]
            current = current.parent
        raise ValueError(f"Undefined scope: {name}")

    def get_parent(self) -> Scope:
        if self.parent:
            return self.parent
        else:
            return self

    def exist_parent(self) -> bool:
        if self.parent:
            return True
        else:
            return False
