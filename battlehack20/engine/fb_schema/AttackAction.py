# automatically generated by the FlatBuffers compiler, do not modify

# namespace: schema

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

# Visually indicate an attack
class AttackAction(object):
    __slots__ = ['_tab']

    @classmethod
    def SizeOf(cls):
        return 2

    # AttackAction
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # AttackAction
    def Id(self): return self._tab.Get(flatbuffers.number_types.Uint16Flags, self._tab.Pos + flatbuffers.number_types.UOffsetTFlags.py_type(0))

def CreateAttackAction(builder, id):
    builder.Prep(2, 2)
    builder.PrependUint16(id)
    return builder.Offset()
