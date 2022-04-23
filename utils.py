from typing import Union
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel

DEBUG = False


class OperandType(str, Enum):
    MOVE = "move"
    F_MOVE = "!F"
    VAR = "variable"
    CONST = "const"
    OP = 'operator'
    FUNC = 'function'
    RETURN = 'return'
    SET_TID = 'set_tid'
    DEFINE = 'define'
    CAST = 'cast'


class VarType(BaseModel):
    type_name: str  # Union['string', 'int', 'double', 'void']
    cnt: int


class Variable(BaseModel):
    type: VarType
    value: Optional[Union[int, float, list, str]]
    par: Optional[list]
    name: Optional[str]


def copy_var(a: Variable):
    x = Variable(type=a.type, par=a.par, name=a.name)
    x.value = a.value
    return x
