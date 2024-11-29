# automatically generated by the FlatBuffers compiler, do not modify

# namespace: schema

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

# Necessary due to flatbuffers requiring unions to be wrapped in tables.
class EventWrapper(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAs(cls, buf, offset=0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = EventWrapper()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsEventWrapper(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)
    # EventWrapper
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # EventWrapper
    def EType(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint8Flags, o + self._tab.Pos)
        return 0

    # EventWrapper
    def E(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            from flatbuffers.table import Table
            obj = Table(bytearray(), 0)
            self._tab.Union(obj, o)
            return obj
        return None

def EventWrapperStart(builder):
    builder.StartObject(2)

def Start(builder):
    EventWrapperStart(builder)

def EventWrapperAddEType(builder, eType):
    builder.PrependUint8Slot(0, eType, 0)

def AddEType(builder, eType):
    EventWrapperAddEType(builder, eType)

def EventWrapperAddE(builder, e):
    builder.PrependUOffsetTRelativeSlot(1, flatbuffers.number_types.UOffsetTFlags.py_type(e), 0)

def AddE(builder, e):
    EventWrapperAddE(builder, e)

def EventWrapperEnd(builder):
    return builder.EndObject()

def End(builder):
    return EventWrapperEnd(builder)