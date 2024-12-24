# automatically generated by the FlatBuffers compiler, do not modify

# namespace: schema

import flatbuffers
from flatbuffers.compat import import_numpy
from typing import Any
np = import_numpy()

class Vec(object):
    __slots__ = ['_tab']

    @classmethod
    def SizeOf(cls) -> int:
        return 8

    # Vec
    def Init(self, buf: bytes, pos: int):
        self._tab = flatbuffers.table.Table(buf, pos)

    # Vec
    def X(self): return self._tab.Get(flatbuffers.number_types.Int32Flags, self._tab.Pos + flatbuffers.number_types.UOffsetTFlags.py_type(0))
    # Vec
    def Y(self): return self._tab.Get(flatbuffers.number_types.Int32Flags, self._tab.Pos + flatbuffers.number_types.UOffsetTFlags.py_type(4))

def CreateVec(builder, x, y):
    builder.Prep(4, 8)
    builder.PrependInt32(y)
    builder.PrependInt32(x)
    return builder.Offset()