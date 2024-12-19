# automatically generated by the FlatBuffers compiler, do not modify

# namespace: schema

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

# Update the indicator string for this robot
class IndicatorStringAction(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAs(cls, buf, offset=0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = IndicatorStringAction()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsIndicatorStringAction(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)
    # IndicatorStringAction
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # IndicatorStringAction
    def Value(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

def IndicatorStringActionStart(builder):
    builder.StartObject(1)

def Start(builder):
    IndicatorStringActionStart(builder)

def IndicatorStringActionAddValue(builder, value):
    builder.PrependUOffsetTRelativeSlot(0, flatbuffers.number_types.UOffsetTFlags.py_type(value), 0)

def AddValue(builder, value):
    IndicatorStringActionAddValue(builder, value)

def IndicatorStringActionEnd(builder):
    return builder.EndObject()

def End(builder):
    return IndicatorStringActionEnd(builder)
