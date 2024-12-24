# automatically generated by the FlatBuffers compiler, do not modify

# namespace: schema

import flatbuffers
from flatbuffers.compat import import_numpy
from typing import Any
np = import_numpy()

class RobotTypeMetadata(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAs(cls, buf, offset: int = 0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = RobotTypeMetadata()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsRobotTypeMetadata(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)
    # RobotTypeMetadata
    def Init(self, buf: bytes, pos: int):
        self._tab = flatbuffers.table.Table(buf, pos)

    # RobotTypeMetadata
    def Type(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int8Flags, o + self._tab.Pos)
        return 0

    # RobotTypeMetadata
    def ActionCooldown(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int32Flags, o + self._tab.Pos)
        return 0

    # RobotTypeMetadata
    def MovementCooldown(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int32Flags, o + self._tab.Pos)
        return 0

    # RobotTypeMetadata
    def BaseHealth(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int32Flags, o + self._tab.Pos)
        return 0

    # RobotTypeMetadata
    def ActionRadiusSquared(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(12))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int32Flags, o + self._tab.Pos)
        return 0

    # RobotTypeMetadata
    def VisionRadiusSquared(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(14))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int32Flags, o + self._tab.Pos)
        return 0

    # RobotTypeMetadata
    def BytecodeLimit(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(16))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Int32Flags, o + self._tab.Pos)
        return 0

def RobotTypeMetadataStart(builder: flatbuffers.Builder):
    builder.StartObject(7)

def Start(builder: flatbuffers.Builder):
    RobotTypeMetadataStart(builder)

def RobotTypeMetadataAddType(builder: flatbuffers.Builder, type: int):
    builder.PrependInt8Slot(0, type, 0)

def AddType(builder: flatbuffers.Builder, type: int):
    RobotTypeMetadataAddType(builder, type)

def RobotTypeMetadataAddActionCooldown(builder: flatbuffers.Builder, actionCooldown: int):
    builder.PrependInt32Slot(1, actionCooldown, 0)

def AddActionCooldown(builder: flatbuffers.Builder, actionCooldown: int):
    RobotTypeMetadataAddActionCooldown(builder, actionCooldown)

def RobotTypeMetadataAddMovementCooldown(builder: flatbuffers.Builder, movementCooldown: int):
    builder.PrependInt32Slot(2, movementCooldown, 0)

def AddMovementCooldown(builder: flatbuffers.Builder, movementCooldown: int):
    RobotTypeMetadataAddMovementCooldown(builder, movementCooldown)

def RobotTypeMetadataAddBaseHealth(builder: flatbuffers.Builder, baseHealth: int):
    builder.PrependInt32Slot(3, baseHealth, 0)

def AddBaseHealth(builder: flatbuffers.Builder, baseHealth: int):
    RobotTypeMetadataAddBaseHealth(builder, baseHealth)

def RobotTypeMetadataAddActionRadiusSquared(builder: flatbuffers.Builder, actionRadiusSquared: int):
    builder.PrependInt32Slot(4, actionRadiusSquared, 0)

def AddActionRadiusSquared(builder: flatbuffers.Builder, actionRadiusSquared: int):
    RobotTypeMetadataAddActionRadiusSquared(builder, actionRadiusSquared)

def RobotTypeMetadataAddVisionRadiusSquared(builder: flatbuffers.Builder, visionRadiusSquared: int):
    builder.PrependInt32Slot(5, visionRadiusSquared, 0)

def AddVisionRadiusSquared(builder: flatbuffers.Builder, visionRadiusSquared: int):
    RobotTypeMetadataAddVisionRadiusSquared(builder, visionRadiusSquared)

def RobotTypeMetadataAddBytecodeLimit(builder: flatbuffers.Builder, bytecodeLimit: int):
    builder.PrependInt32Slot(6, bytecodeLimit, 0)

def AddBytecodeLimit(builder: flatbuffers.Builder, bytecodeLimit: int):
    RobotTypeMetadataAddBytecodeLimit(builder, bytecodeLimit)

def RobotTypeMetadataEnd(builder: flatbuffers.Builder) -> int:
    return builder.EndObject()

def End(builder: flatbuffers.Builder) -> int:
    return RobotTypeMetadataEnd(builder)