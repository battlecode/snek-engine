// automatically generated by the FlatBuffers compiler, do not modify

/* eslint-disable @typescript-eslint/no-unused-vars, @typescript-eslint/no-explicit-any, @typescript-eslint/no-non-null-assertion */

import * as flatbuffers from 'flatbuffers';

import { GameMap } from '../../battlecode/schema/game-map';


/**
 * Sent to start a match.
 */
export class MatchHeader {
  bb: flatbuffers.ByteBuffer|null = null;
  bb_pos = 0;
  __init(i:number, bb:flatbuffers.ByteBuffer):MatchHeader {
  this.bb_pos = i;
  this.bb = bb;
  return this;
}

static getRootAsMatchHeader(bb:flatbuffers.ByteBuffer, obj?:MatchHeader):MatchHeader {
  return (obj || new MatchHeader()).__init(bb.readInt32(bb.position()) + bb.position(), bb);
}

static getSizePrefixedRootAsMatchHeader(bb:flatbuffers.ByteBuffer, obj?:MatchHeader):MatchHeader {
  bb.setPosition(bb.position() + flatbuffers.SIZE_PREFIX_LENGTH);
  return (obj || new MatchHeader()).__init(bb.readInt32(bb.position()) + bb.position(), bb);
}

map(obj?:GameMap):GameMap|null {
  const offset = this.bb!.__offset(this.bb_pos, 4);
  return offset ? (obj || new GameMap()).__init(this.bb!.__indirect(this.bb_pos + offset), this.bb!) : null;
}

maxRounds():number {
  const offset = this.bb!.__offset(this.bb_pos, 6);
  return offset ? this.bb!.readInt32(this.bb_pos + offset) : 0;
}

static startMatchHeader(builder:flatbuffers.Builder) {
  builder.startObject(2);
}

static addMap(builder:flatbuffers.Builder, mapOffset:flatbuffers.Offset) {
  builder.addFieldOffset(0, mapOffset, 0);
}

static addMaxRounds(builder:flatbuffers.Builder, maxRounds:number) {
  builder.addFieldInt32(1, maxRounds, 0);
}

static endMatchHeader(builder:flatbuffers.Builder):flatbuffers.Offset {
  const offset = builder.endObject();
  return offset;
}

static createMatchHeader(builder:flatbuffers.Builder, mapOffset:flatbuffers.Offset, maxRounds:number):flatbuffers.Offset {
  MatchHeader.startMatchHeader(builder);
  MatchHeader.addMap(builder, mapOffset);
  MatchHeader.addMaxRounds(builder, maxRounds);
  return MatchHeader.endMatchHeader(builder);
}
}