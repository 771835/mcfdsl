# coding=utf-8
from typing import Any

from transpiler.core.enums import StructureType, CompareOps, BinaryOps, UnaryOps, DataType
from transpiler.core.safe_enum import SafeEnum
from transpiler.core.symbols import Literal
from transpiler.core.symbols.class_ import Class
from transpiler.core.symbols.constant import Constant
from transpiler.core.symbols.function import Function
from transpiler.core.symbols.reference import Reference
from transpiler.core.symbols.variable import Variable


class IROpCode(SafeEnum):
    # ===== 控制流指令 (0x00-0x1F) =====
    JUMP = 0x00  # 无条件跳转
    COND_JUMP = 0x01  # 条件跳转
    FUNCTION = 0x02  # 函数定义
    CALL = 0x03  # 函数调用
    RETURN = 0x04  # 函数返回
    SCOPE_BEGIN = 0x05  # 作用域开始
    SCOPE_END = 0x06  # 作用域结束
    BREAK = 0x07  # 跳出循环
    CONTINUE = 0x08  # 继续循环
    # 预留 0x09-0x1F 用于控制流扩展

    # ===== 变量操作指令 (0x20-0x3F) =====
    DECLARE = 0x20  # 变量声明
    VAR_RELEASE = 0x21  # 变量释放
    ASSIGN = 0x22  # 赋值操作
    UNARY_OP = 0x23  # 一元运算
    OP = 0x24  # 二元运算
    COMPARE = 0x25  # 比较运算
    CAST = 0x26  # 显式类型转换
    # 预留 0x27-0x3F 用于变量操作扩展

    # ===== 面向对象指令 (0x40-0x5F) =====
    CLASS = 0x40  # 类定义
    NEW_OBJ = 0x41  # 对象实例化
    GET_FIELD = 0x42  # 获取字段
    SET_FIELD = 0x43  # 设置字段
    CALL_METHOD = 0x44  # 方法调用
    # 预留 0x45-0x5F 用于OOP扩展

    # ===== 特殊指令 (0x60-0x7F) =====
    RAW_CMD = 0x60  # 原始命令输出
    DEBUG_INFO = 0x61  # 调试元数据

    # 预留 0x62-0x7F 用于命令扩展

    # ==== 扩展指令集 (0x80-0xFF) ====
    # 预留 0x80-0xFF 用于未来补充

    # ==== 其他指令集 (0x100+) ====
    # 预留 0x100+ 用于用户自行使用

    def __hash__(self):
        return hash(self.value)


class IRInstruction:
    def __init__(self, opcode: IROpCode,
                 operands: list[Any], line: int = -1, column: int = -1, filename: str = None, debug: bool = False):
        self.filename = filename
        self.column = column
        self.line = line
        self.operands = operands
        self.opcode = opcode
        self.debug = debug

    def __repr__(self):
        ops = ", ".join(f"{op=}" for op in self.operands)
        return \
            f"{self.opcode}({ops})"

    def __hash__(self):
        return hash((self.opcode, tuple(self.operands)))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def get_operands(self):
        return self.operands


# 具体指令实现
class IRJump(IRInstruction):
    def __init__(self, scope: str, line: int = -1,
                 column: int = -1, filename: str = None):
        operands = [
            scope
        ]
        super().__init__(IROpCode.JUMP, operands, line, column, filename)


class IRCondJump(IRInstruction):
    def __init__(self, cond: Variable, true_scope: str, false_scope: str = None, line: int = -1, column: int = -1,
                 filename: str = None):
        assert cond.dtype == DataType.BOOLEAN

        operands = [
            cond,
            true_scope,
            false_scope
        ]
        super().__init__(IROpCode.COND_JUMP, operands, line, column, filename)


class IRFunction(IRInstruction):
    def __init__(self, function: Function, line: int = -1, column: int = -1,
                 filename: str = None):
        operands = [
            function
        ]
        super().__init__(IROpCode.FUNCTION, operands, line, column, filename)


class IRReturn(IRInstruction):
    def __init__(self, value: Reference[Variable | Constant | Literal] = None, line: int = -1, column: int = -1,
                 filename: str = None):
        operands = [
            value
        ]
        super().__init__(IROpCode.RETURN, operands, line, column, filename)


class IRCall(IRInstruction):
    def __init__(self, result: Variable | Constant, func: Function,
                 args: list[Reference[Variable | Constant | Literal]] = None, line: int = -1, column: int = -1,
                 filename: str = None, opcode: IROpCode = None):
        if args is None:
            args = []
        operands = [
            result,
            func,
            args
        ]
        super().__init__(opcode if opcode else IROpCode.CALL, operands, line, column, filename)

    def __hash__(self):
        return hash((self.operands[0], self.operands[1], tuple(self.operands[2])))


class IRScopeBegin(IRInstruction):
    def __init__(self, name: str, stype: StructureType,
                 line: int = -1, column: int = -1, filename: str = None):
        operands = [
            name,
            stype
        ]
        super().__init__(IROpCode.SCOPE_BEGIN, operands, line, column, filename)


class IRScopeEnd(IRInstruction):
    def __init__(self, line: int = -1, column: int = -1, filename: str = None):
        operands = [
        ]
        super().__init__(IROpCode.SCOPE_END, operands, line, column, filename)


class IRBreak(IRInstruction):
    def __init__(self, scope_name: str, line: int = -1, column: int = -1, filename: str = None):
        operands = [
            scope_name
        ]
        super().__init__(IROpCode.BREAK, operands, line, column, filename)


class IRContinue(IRInstruction):
    def __init__(self, scope_name: str, line: int = -1, column: int = -1, filename: str = None):
        operands = [
            scope_name
        ]
        super().__init__(IROpCode.CONTINUE, operands, line, column, filename)


class IRDeclare(IRInstruction):
    def __init__(self, var: Variable | Constant, line: int = -1, column: int = -1,
                 filename: str = None):
        operands = [
            var
        ]
        super().__init__(IROpCode.DECLARE, operands, line, column, filename)


class IRVarRelease(IRInstruction):
    def __init__(self, name: str, line: int = -1,
                 column: int = -1, filename: str = None):
        operands = [
            name
        ]
        super().__init__(IROpCode.VAR_RELEASE, operands, line, column, filename)


class IRAssign(IRInstruction):
    def __init__(self, target: Variable | Constant, source: Reference[Variable | Constant | Literal], line: int = -1,
                 column: int = -1, filename: str = None):
        operands = [
            target,
            source
        ]
        super().__init__(IROpCode.ASSIGN, operands, line, column, filename)


class IRUnaryOp(IRInstruction):
    def __init__(self, result: Variable | Constant, op: UnaryOps, operand: Reference[Variable | Constant | Literal],
                 line: int = -1,
                 column: int = -1,
                 filename: str = None):
        operands = [
            result,
            op,
            operand
        ]
        super().__init__(IROpCode.UNARY_OP, operands, line, column, filename)


class IROp(IRInstruction):
    def __init__(self, result: Variable | Constant, op: BinaryOps, left: Reference[Variable | Constant | Literal],
                 right: Reference[Variable | Constant | Literal], line: int = -1, column: int = -1,
                 filename: str = None):
        operands = [
            result,
            op,
            left,
            right
        ]
        super().__init__(IROpCode.OP, operands, line, column, filename)


class IRCompare(IRInstruction):
    def __init__(self, result: Variable | Constant, op: CompareOps, left: Reference[Variable | Constant | Literal],
                 right: Reference[Variable | Constant | Literal], line: int = -1, column: int = -1,
                 filename: str = None):
        operands = [
            result,
            op,
            left,
            right
        ]
        super().__init__(IROpCode.COMPARE, operands, line, column, filename)


class IRCast(IRInstruction):
    def __init__(self, result: Variable | Constant, dtype: DataType | Class,
                 value: Reference[Variable | Constant | Literal], line: int = -1,
                 column: int = -1, filename: str = None):
        operands = [
            result,
            dtype,
            value
        ]
        super().__init__(IROpCode.CAST, operands, line, column, filename)


class IRClass(IRInstruction):
    def __init__(self, class_: Class, line: int = -1,
                 column: int = -1, filename: str = None):
        operands = [
            class_
        ]
        super().__init__(IROpCode.CLASS, operands, line, column, filename)


class IRNewObj(IRInstruction):
    def __init__(self, result: Variable, class_: Class, args: list[Reference[Variable | Constant | Literal]],
                 line: int = -1, column: int = -1,
                 filename: str = None):
        operands = [
            result,
            class_,
            args
        ]
        super().__init__(IROpCode.NEW_OBJ, operands, line, column, filename)


class IRGetField(IRInstruction):
    def __init__(self, result: Variable, obj: Reference[Variable | Constant], field: str, line: int = -1,
                 column: int = -1,
                 filename: str = None):
        operands = [
            result,
            obj,
            field
        ]
        super().__init__(IROpCode.GET_FIELD, operands, line, column, filename)


class IRSetField(IRInstruction):
    def __init__(self, obj: Variable, field: str, value: Reference[Variable | Constant | Literal], line: int = -1,
                 column: int = -1,
                 filename: str = None):
        operands = [
            obj,
            field,
            value
        ]
        super().__init__(IROpCode.SET_FIELD, operands, line, column, filename)


class IRCallMethod(IRInstruction):
    def __init__(self, result: Variable, obj: Reference[Variable | Constant], method: Function,
                 args: list[Reference] = None, line: int = -1,
                 column: int = -1, filename: str = None):
        operands = [
            result,
            obj,
            method,
            args
        ]
        super().__init__(IROpCode.CALL_METHOD, operands, line, column, filename)


class IRRawCmd(IRInstruction):
    def __init__(self, command: Reference[Variable | Constant | Literal], line: int = -1, column: int = -1,
                 filename: str = None):
        operands = [
            command
        ]
        super().__init__(IROpCode.RAW_CMD, operands, line, column, filename)


class IRDebugInfo(IRInstruction):
    def __init__(self, line: int = -1, column: int = -1,
                 filename: str = None):
        operands = [
        ]
        super().__init__(IROpCode.DEBUG_INFO, operands, line, column, filename)
