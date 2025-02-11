from __future__ import annotations

import flatbuffers
import numpy as np

import flatbuffers
import typing
from ..schema.ProfilerEvent import ProfilerEvent

uoffset: typing.TypeAlias = flatbuffers.number_types.UOffsetTFlags.py_type

class ProfilerProfile(object):
  @classmethod
  def GetRootAs(cls, buf: bytes, offset: int) -> ProfilerProfile: ...
  @classmethod
  def GetRootAsProfilerProfile(cls, buf: bytes, offset: int) -> ProfilerProfile: ...
  def Init(self, buf: bytes, pos: int) -> None: ...
  def Name(self) -> str | None: ...
  def Events(self, i: int) -> ProfilerEvent | None: ...
  def EventsLength(self) -> int: ...
  def EventsIsNone(self) -> bool: ...
def ProfilerProfileStart(builder: flatbuffers.Builder) -> None: ...
def Start(builder: flatbuffers.Builder) -> None: ...
def ProfilerProfileAddName(builder: flatbuffers.Builder, name: uoffset) -> None: ...
def ProfilerProfileAddEvents(builder: flatbuffers.Builder, events: uoffset) -> None: ...
def ProfilerProfileStartEventsVector(builder: flatbuffers.Builder, num_elems: int) -> uoffset: ...
def StartEventsVector(builder: flatbuffers.Builder, num_elems: int) -> uoffset: ...
def ProfilerProfileEnd(builder: flatbuffers.Builder) -> uoffset: ...
def End(builder: flatbuffers.Builder) -> uoffset: ...

