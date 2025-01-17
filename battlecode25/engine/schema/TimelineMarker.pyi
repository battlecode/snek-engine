from __future__ import annotations

import flatbuffers
import numpy as np

import flatbuffers
import typing

uoffset: typing.TypeAlias = flatbuffers.number_types.UOffsetTFlags.py_type

class TimelineMarker(object):
  @classmethod
  def GetRootAs(cls, buf: bytes, offset: int) -> TimelineMarker: ...
  @classmethod
  def GetRootAsTimelineMarker(cls, buf: bytes, offset: int) -> TimelineMarker: ...
  def Init(self, buf: bytes, pos: int) -> None: ...
  def Team(self) -> int: ...
  def Round(self) -> int: ...
  def ColorHex(self) -> int: ...
  def Label(self) -> str | None: ...
def TimelineMarkerStart(builder: flatbuffers.Builder) -> None: ...
def Start(builder: flatbuffers.Builder) -> None: ...
def TimelineMarkerAddTeam(builder: flatbuffers.Builder, team: int) -> None: ...
def TimelineMarkerAddRound(builder: flatbuffers.Builder, round: int) -> None: ...
def TimelineMarkerAddColorHex(builder: flatbuffers.Builder, colorHex: int) -> None: ...
def TimelineMarkerAddLabel(builder: flatbuffers.Builder, label: uoffset) -> None: ...
def TimelineMarkerEnd(builder: flatbuffers.Builder) -> uoffset: ...
def End(builder: flatbuffers.Builder) -> uoffset: ...

