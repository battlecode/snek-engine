// automatically generated by the FlatBuffers compiler, do not modify

/* eslint-disable @typescript-eslint/no-unused-vars, @typescript-eslint/no-explicit-any, @typescript-eslint/no-non-null-assertion */

import * as flatbuffers from 'flatbuffers';

import { Action, unionToAction, unionListToAction } from '../../battlecode/schema/action';


export class Turn {
  bb: flatbuffers.ByteBuffer|null = null;
  bb_pos = 0;
  __init(i:number, bb:flatbuffers.ByteBuffer):Turn {
  this.bb_pos = i;
  this.bb = bb;
  return this;
}

static getRootAsTurn(bb:flatbuffers.ByteBuffer, obj?:Turn):Turn {
  return (obj || new Turn()).__init(bb.readInt32(bb.position()) + bb.position(), bb);
}

static getSizePrefixedRootAsTurn(bb:flatbuffers.ByteBuffer, obj?:Turn):Turn {
  bb.setPosition(bb.position() + flatbuffers.SIZE_PREFIX_LENGTH);
  return (obj || new Turn()).__init(bb.readInt32(bb.position()) + bb.position(), bb);
}

robotId():number {
  const offset = this.bb!.__offset(this.bb_pos, 4);
  return offset ? this.bb!.readInt32(this.bb_pos + offset) : 0;
}

health():number {
  const offset = this.bb!.__offset(this.bb_pos, 6);
  return offset ? this.bb!.readInt32(this.bb_pos + offset) : 0;
}

paint():number {
  const offset = this.bb!.__offset(this.bb_pos, 8);
  return offset ? this.bb!.readInt32(this.bb_pos + offset) : 0;
}

moveCooldown():number {
  const offset = this.bb!.__offset(this.bb_pos, 10);
  return offset ? this.bb!.readInt32(this.bb_pos + offset) : 0;
}

actionCooldown():number {
  const offset = this.bb!.__offset(this.bb_pos, 12);
  return offset ? this.bb!.readInt32(this.bb_pos + offset) : 0;
}

bytecodesUsed():number {
  const offset = this.bb!.__offset(this.bb_pos, 14);
  return offset ? this.bb!.readInt32(this.bb_pos + offset) : 0;
}

x():number {
  const offset = this.bb!.__offset(this.bb_pos, 16);
  return offset ? this.bb!.readUint8(this.bb_pos + offset) : 0;
}

y():number {
  const offset = this.bb!.__offset(this.bb_pos, 18);
  return offset ? this.bb!.readUint8(this.bb_pos + offset) : 0;
}

actionsType(index: number):Action|null {
  const offset = this.bb!.__offset(this.bb_pos, 20);
  return offset ? this.bb!.readUint8(this.bb!.__vector(this.bb_pos + offset) + index) : 0;
}

actionsTypeLength():number {
  const offset = this.bb!.__offset(this.bb_pos, 20);
  return offset ? this.bb!.__vector_len(this.bb_pos + offset) : 0;
}

actionsTypeArray():Uint8Array|null {
  const offset = this.bb!.__offset(this.bb_pos, 20);
  return offset ? new Uint8Array(this.bb!.bytes().buffer, this.bb!.bytes().byteOffset + this.bb!.__vector(this.bb_pos + offset), this.bb!.__vector_len(this.bb_pos + offset)) : null;
}

actions(index: number, obj:any):any|null {
  const offset = this.bb!.__offset(this.bb_pos, 22);
  return offset ? this.bb!.__union(obj, this.bb!.__vector(this.bb_pos + offset) + index * 4) : null;
}

actionsLength():number {
  const offset = this.bb!.__offset(this.bb_pos, 22);
  return offset ? this.bb!.__vector_len(this.bb_pos + offset) : 0;
}

static startTurn(builder:flatbuffers.Builder) {
  builder.startObject(10);
}

static addRobotId(builder:flatbuffers.Builder, robotId:number) {
  builder.addFieldInt32(0, robotId, 0);
}

static addHealth(builder:flatbuffers.Builder, health:number) {
  builder.addFieldInt32(1, health, 0);
}

static addPaint(builder:flatbuffers.Builder, paint:number) {
  builder.addFieldInt32(2, paint, 0);
}

static addMoveCooldown(builder:flatbuffers.Builder, moveCooldown:number) {
  builder.addFieldInt32(3, moveCooldown, 0);
}

static addActionCooldown(builder:flatbuffers.Builder, actionCooldown:number) {
  builder.addFieldInt32(4, actionCooldown, 0);
}

static addBytecodesUsed(builder:flatbuffers.Builder, bytecodesUsed:number) {
  builder.addFieldInt32(5, bytecodesUsed, 0);
}

static addX(builder:flatbuffers.Builder, x:number) {
  builder.addFieldInt8(6, x, 0);
}

static addY(builder:flatbuffers.Builder, y:number) {
  builder.addFieldInt8(7, y, 0);
}

static addActionsType(builder:flatbuffers.Builder, actionsTypeOffset:flatbuffers.Offset) {
  builder.addFieldOffset(8, actionsTypeOffset, 0);
}

static createActionsTypeVector(builder:flatbuffers.Builder, data:Action[]):flatbuffers.Offset {
  builder.startVector(1, data.length, 1);
  for (let i = data.length - 1; i >= 0; i--) {
    builder.addInt8(data[i]!);
  }
  return builder.endVector();
}

static startActionsTypeVector(builder:flatbuffers.Builder, numElems:number) {
  builder.startVector(1, numElems, 1);
}

static addActions(builder:flatbuffers.Builder, actionsOffset:flatbuffers.Offset) {
  builder.addFieldOffset(9, actionsOffset, 0);
}

static createActionsVector(builder:flatbuffers.Builder, data:flatbuffers.Offset[]):flatbuffers.Offset {
  builder.startVector(4, data.length, 4);
  for (let i = data.length - 1; i >= 0; i--) {
    builder.addOffset(data[i]!);
  }
  return builder.endVector();
}

static startActionsVector(builder:flatbuffers.Builder, numElems:number) {
  builder.startVector(4, numElems, 4);
}

static endTurn(builder:flatbuffers.Builder):flatbuffers.Offset {
  const offset = builder.endObject();
  return offset;
}

static createTurn(builder:flatbuffers.Builder, robotId:number, health:number, paint:number, moveCooldown:number, actionCooldown:number, bytecodesUsed:number, x:number, y:number, actionsTypeOffset:flatbuffers.Offset, actionsOffset:flatbuffers.Offset):flatbuffers.Offset {
  Turn.startTurn(builder);
  Turn.addRobotId(builder, robotId);
  Turn.addHealth(builder, health);
  Turn.addPaint(builder, paint);
  Turn.addMoveCooldown(builder, moveCooldown);
  Turn.addActionCooldown(builder, actionCooldown);
  Turn.addBytecodesUsed(builder, bytecodesUsed);
  Turn.addX(builder, x);
  Turn.addY(builder, y);
  Turn.addActionsType(builder, actionsTypeOffset);
  Turn.addActions(builder, actionsOffset);
  return Turn.endTurn(builder);
}
}