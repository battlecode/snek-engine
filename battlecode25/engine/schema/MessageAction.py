# automatically generated by the FlatBuffers compiler, do not modify

# namespace: schema

import flatbuffers
from flatbuffers.compat import import_numpy
from typing import Any
np = import_numpy()

# Visually indicate messaging from one robot to another
class MessageAction(object):
    __slots__ = ['_tab']

    @classmethod
    def SizeOf(cls) -> int:
        return 8

    # MessageAction
    def Init(self, buf: bytes, pos: int):
        self._tab = flatbuffers.table.Table(buf, pos)

    # Id of the message target
    # MessageAction
    def Id(self): return self._tab.Get(flatbuffers.number_types.Uint16Flags, self._tab.Pos + flatbuffers.number_types.UOffsetTFlags.py_type(0))
    # MessageAction
    def Data(self): return self._tab.Get(flatbuffers.number_types.Int32Flags, self._tab.Pos + flatbuffers.number_types.UOffsetTFlags.py_type(4))

def CreateMessageAction(builder, id, data):
    builder.Prep(4, 8)
    builder.PrependInt32(data)
    builder.Pad(2)
    builder.PrependUint16(id)
    return builder.Offset()
