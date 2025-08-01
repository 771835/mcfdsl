# coding=utf-8
from abc import ABCMeta, abstractmethod
from typing import Callable

from transpiler.core.backend.ir_builder import IRBuilder
from transpiler.core.instructions import IRInstruction
from transpiler.core.symbols import Constant, Class, Function, Reference, Variable, Literal


class Library(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, builder: IRBuilder):
        pass

    @abstractmethod
    def __str__(self) -> str:
        """返回库的描述性字符串"""
        pass

    @abstractmethod
    def load(self) -> list[IRInstruction]:
        """加载库资源（如初始化状态、加载依赖等）"""
        pass

    @abstractmethod
    def get_functions(self) -> dict[Function, Callable[..., Variable | Constant | Literal]]:
        """获取函数及其处理函数的映射"""
        pass

    @abstractmethod
    def get_constants(self) -> dict[Constant, Reference]:
        """获取库中定义的所有常量"""
        pass

    def get_events(self) -> dict[str, Callable[..., list[IRInstruction]]]:
        """获取事件及其处理函数的映射"""
        return {}

    def get_annotations(self) -> dict[str, Callable[..., list[IRInstruction]]]:
        """获取注解及其处理函数的映射"""
        return {}

    def get_classes(self) -> list[Class]:
        """获取库中定义的所有类"""
        return []
