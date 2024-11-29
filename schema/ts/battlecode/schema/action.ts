// automatically generated by the FlatBuffers compiler, do not modify

/* eslint-disable @typescript-eslint/no-unused-vars, @typescript-eslint/no-explicit-any, @typescript-eslint/no-non-null-assertion */

import { AttackAction } from '../../battlecode/schema/attack-action';
import { BuildAction } from '../../battlecode/schema/build-action';
import { DamageAction } from '../../battlecode/schema/damage-action';
import { IndicatorDotAction } from '../../battlecode/schema/indicator-dot-action';
import { IndicatorLineAction } from '../../battlecode/schema/indicator-line-action';
import { IndicatorStringAction } from '../../battlecode/schema/indicator-string-action';
import { MessageAction } from '../../battlecode/schema/message-action';
import { MopAction } from '../../battlecode/schema/mop-action';
import { PaintAction } from '../../battlecode/schema/paint-action';
import { SpawnAction } from '../../battlecode/schema/spawn-action';
import { TransferAction } from '../../battlecode/schema/transfer-action';
import { UnpaintAction } from '../../battlecode/schema/unpaint-action';
import { UpgradeAction } from '../../battlecode/schema/upgrade-action';


export enum Action {
  NONE = 0,
  DamageAction = 1,
  PaintAction = 2,
  UnpaintAction = 3,
  AttackAction = 4,
  MopAction = 5,
  BuildAction = 6,
  TransferAction = 7,
  MessageAction = 8,
  SpawnAction = 9,
  UpgradeAction = 10,
  IndicatorStringAction = 11,
  IndicatorDotAction = 12,
  IndicatorLineAction = 13
}

export function unionToAction(
  type: Action,
  accessor: (obj:AttackAction|BuildAction|DamageAction|IndicatorDotAction|IndicatorLineAction|IndicatorStringAction|MessageAction|MopAction|PaintAction|SpawnAction|TransferAction|UnpaintAction|UpgradeAction) => AttackAction|BuildAction|DamageAction|IndicatorDotAction|IndicatorLineAction|IndicatorStringAction|MessageAction|MopAction|PaintAction|SpawnAction|TransferAction|UnpaintAction|UpgradeAction|null
): AttackAction|BuildAction|DamageAction|IndicatorDotAction|IndicatorLineAction|IndicatorStringAction|MessageAction|MopAction|PaintAction|SpawnAction|TransferAction|UnpaintAction|UpgradeAction|null {
  switch(Action[type]) {
    case 'NONE': return null; 
    case 'DamageAction': return accessor(new DamageAction())! as DamageAction;
    case 'PaintAction': return accessor(new PaintAction())! as PaintAction;
    case 'UnpaintAction': return accessor(new UnpaintAction())! as UnpaintAction;
    case 'AttackAction': return accessor(new AttackAction())! as AttackAction;
    case 'MopAction': return accessor(new MopAction())! as MopAction;
    case 'BuildAction': return accessor(new BuildAction())! as BuildAction;
    case 'TransferAction': return accessor(new TransferAction())! as TransferAction;
    case 'MessageAction': return accessor(new MessageAction())! as MessageAction;
    case 'SpawnAction': return accessor(new SpawnAction())! as SpawnAction;
    case 'UpgradeAction': return accessor(new UpgradeAction())! as UpgradeAction;
    case 'IndicatorStringAction': return accessor(new IndicatorStringAction())! as IndicatorStringAction;
    case 'IndicatorDotAction': return accessor(new IndicatorDotAction())! as IndicatorDotAction;
    case 'IndicatorLineAction': return accessor(new IndicatorLineAction())! as IndicatorLineAction;
    default: return null;
  }
}

export function unionListToAction(
  type: Action, 
  accessor: (index: number, obj:AttackAction|BuildAction|DamageAction|IndicatorDotAction|IndicatorLineAction|IndicatorStringAction|MessageAction|MopAction|PaintAction|SpawnAction|TransferAction|UnpaintAction|UpgradeAction) => AttackAction|BuildAction|DamageAction|IndicatorDotAction|IndicatorLineAction|IndicatorStringAction|MessageAction|MopAction|PaintAction|SpawnAction|TransferAction|UnpaintAction|UpgradeAction|null, 
  index: number
): AttackAction|BuildAction|DamageAction|IndicatorDotAction|IndicatorLineAction|IndicatorStringAction|MessageAction|MopAction|PaintAction|SpawnAction|TransferAction|UnpaintAction|UpgradeAction|null {
  switch(Action[type]) {
    case 'NONE': return null; 
    case 'DamageAction': return accessor(index, new DamageAction())! as DamageAction;
    case 'PaintAction': return accessor(index, new PaintAction())! as PaintAction;
    case 'UnpaintAction': return accessor(index, new UnpaintAction())! as UnpaintAction;
    case 'AttackAction': return accessor(index, new AttackAction())! as AttackAction;
    case 'MopAction': return accessor(index, new MopAction())! as MopAction;
    case 'BuildAction': return accessor(index, new BuildAction())! as BuildAction;
    case 'TransferAction': return accessor(index, new TransferAction())! as TransferAction;
    case 'MessageAction': return accessor(index, new MessageAction())! as MessageAction;
    case 'SpawnAction': return accessor(index, new SpawnAction())! as SpawnAction;
    case 'UpgradeAction': return accessor(index, new UpgradeAction())! as UpgradeAction;
    case 'IndicatorStringAction': return accessor(index, new IndicatorStringAction())! as IndicatorStringAction;
    case 'IndicatorDotAction': return accessor(index, new IndicatorDotAction())! as IndicatorDotAction;
    case 'IndicatorLineAction': return accessor(index, new IndicatorLineAction())! as IndicatorLineAction;
    default: return null;
  }
}