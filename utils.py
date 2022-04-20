from ctypes import Union
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class OperandType(str, Enum):
    MOVE = "move"
    F_MOVE = "!F"
    VAR = "variable"
    OP = 'operator'
    SET_TID = 'set_tid'


class VarType(BaseModel):
    name: str = Union['string', 'int', 'double']
    cnt: int
    value = Optional[Union[str, int, float]]
