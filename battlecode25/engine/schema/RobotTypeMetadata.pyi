from __future__ import annotations

import flatbuffers
import numpy as np

import flatbuffers
import typing
from ..schema.RobotType import RobotType

uoffset: typing.TypeAlias = flatbuffers.number_types.UOffsetTFlags.py_type

class RobotTypeMetadata(object):
  @classmethod
  def GetRootAs(cls, buf: bytes, offset: int) -> RobotTypeMetadata: ...
  @classmethod
  def GetRootAsRobotTypeMetadata(cls, buf: bytes, offset: int) -> RobotTypeMetadata: ...
  def Init(self, buf: bytes, pos: int) -> None: ...
  def Type(self) -> typing.Literal[RobotType.NONE, RobotType.PAINT_TOWER, RobotType.MONEY_TOWER, RobotType.DEFENSE_TOWER, RobotType.SOLDIER, RobotType.SPLASHER, RobotType.MOPPER]: ...
  def ActionCooldown(self) -> int: ...
  def MovementCooldown(self) -> int: ...
  def BaseHealth(self) -> int: ...
  def BasePaint(self) -> int: ...
  def MaxPaint(self) -> int: ...
  def ActionRadiusSquared(self) -> int: ...
  def VisionRadiusSquared(self) -> int: ...
  def MessageRadiusSquared(self) -> int: ...
  def BytecodeLimit(self) -> int: ...
def RobotTypeMetadataStart(builder: flatbuffers.Builder) -> None: ...
def Start(builder: flatbuffers.Builder) -> None: ...
def RobotTypeMetadataAddType(builder: flatbuffers.Builder, type: typing.Literal[RobotType.NONE, RobotType.PAINT_TOWER, RobotType.MONEY_TOWER, RobotType.DEFENSE_TOWER, RobotType.SOLDIER, RobotType.SPLASHER, RobotType.MOPPER]) -> None: ...
def RobotTypeMetadataAddActionCooldown(builder: flatbuffers.Builder, actionCooldown: int) -> None: ...
def RobotTypeMetadataAddMovementCooldown(builder: flatbuffers.Builder, movementCooldown: int) -> None: ...
def RobotTypeMetadataAddBaseHealth(builder: flatbuffers.Builder, baseHealth: int) -> None: ...
def RobotTypeMetadataAddBasePaint(builder: flatbuffers.Builder, basePaint: int) -> None: ...
def RobotTypeMetadataAddMaxPaint(builder: flatbuffers.Builder, maxPaint: int) -> None: ...
def RobotTypeMetadataAddActionRadiusSquared(builder: flatbuffers.Builder, actionRadiusSquared: int) -> None: ...
def RobotTypeMetadataAddVisionRadiusSquared(builder: flatbuffers.Builder, visionRadiusSquared: int) -> None: ...
def RobotTypeMetadataAddMessageRadiusSquared(builder: flatbuffers.Builder, messageRadiusSquared: int) -> None: ...
def RobotTypeMetadataAddBytecodeLimit(builder: flatbuffers.Builder, bytecodeLimit: int) -> None: ...
def RobotTypeMetadataEnd(builder: flatbuffers.Builder) -> uoffset: ...
def End(builder: flatbuffers.Builder) -> uoffset: ...

