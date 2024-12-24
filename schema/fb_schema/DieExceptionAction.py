# automatically generated by the FlatBuffers compiler, do not modify

# namespace: fb_schema

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

# Indicates that the robot died due to an uncaught exception
class DieExceptionAction(object):
    __slots__ = ['_tab']

    @classmethod
    def SizeOf(cls):
        return 1

    # DieExceptionAction
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # DieExceptionAction
    def Value(self): return self._tab.Get(flatbuffers.number_types.Int8Flags, self._tab.Pos + flatbuffers.number_types.UOffsetTFlags.py_type(0))

def CreateDieExceptionAction(builder, value):
    builder.Prep(1, 1)
    builder.PrependInt8(value)
    return builder.Offset()
