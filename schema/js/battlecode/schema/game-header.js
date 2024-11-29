"use strict";
// automatically generated by the FlatBuffers compiler, do not modify
Object.defineProperty(exports, "__esModule", { value: true });
exports.GameHeader = void 0;
/* eslint-disable @typescript-eslint/no-unused-vars, @typescript-eslint/no-explicit-any, @typescript-eslint/no-non-null-assertion */
var flatbuffers = require("flatbuffers");
var gameplay_constants_1 = require("../../battlecode/schema/gameplay-constants");
var robot_type_metadata_1 = require("../../battlecode/schema/robot-type-metadata");
var team_data_1 = require("../../battlecode/schema/team-data");
/**
 * The first event sent in the game. Contains all metadata about the game.
 */
var GameHeader = /** @class */ (function () {
    function GameHeader() {
        this.bb = null;
        this.bb_pos = 0;
    }
    GameHeader.prototype.__init = function (i, bb) {
        this.bb_pos = i;
        this.bb = bb;
        return this;
    };
    GameHeader.getRootAsGameHeader = function (bb, obj) {
        return (obj || new GameHeader()).__init(bb.readInt32(bb.position()) + bb.position(), bb);
    };
    GameHeader.getSizePrefixedRootAsGameHeader = function (bb, obj) {
        bb.setPosition(bb.position() + flatbuffers.SIZE_PREFIX_LENGTH);
        return (obj || new GameHeader()).__init(bb.readInt32(bb.position()) + bb.position(), bb);
    };
    GameHeader.prototype.specVersion = function (optionalEncoding) {
        var offset = this.bb.__offset(this.bb_pos, 4);
        return offset ? this.bb.__string(this.bb_pos + offset, optionalEncoding) : null;
    };
    GameHeader.prototype.teams = function (index, obj) {
        var offset = this.bb.__offset(this.bb_pos, 6);
        return offset ? (obj || new team_data_1.TeamData()).__init(this.bb.__indirect(this.bb.__vector(this.bb_pos + offset) + index * 4), this.bb) : null;
    };
    GameHeader.prototype.teamsLength = function () {
        var offset = this.bb.__offset(this.bb_pos, 6);
        return offset ? this.bb.__vector_len(this.bb_pos + offset) : 0;
    };
    GameHeader.prototype.robotTypeMetadata = function (index, obj) {
        var offset = this.bb.__offset(this.bb_pos, 8);
        return offset ? (obj || new robot_type_metadata_1.RobotTypeMetadata()).__init(this.bb.__indirect(this.bb.__vector(this.bb_pos + offset) + index * 4), this.bb) : null;
    };
    GameHeader.prototype.robotTypeMetadataLength = function () {
        var offset = this.bb.__offset(this.bb_pos, 8);
        return offset ? this.bb.__vector_len(this.bb_pos + offset) : 0;
    };
    GameHeader.prototype.constants = function (obj) {
        var offset = this.bb.__offset(this.bb_pos, 10);
        return offset ? (obj || new gameplay_constants_1.GameplayConstants()).__init(this.bb.__indirect(this.bb_pos + offset), this.bb) : null;
    };
    GameHeader.startGameHeader = function (builder) {
        builder.startObject(4);
    };
    GameHeader.addSpecVersion = function (builder, specVersionOffset) {
        builder.addFieldOffset(0, specVersionOffset, 0);
    };
    GameHeader.addTeams = function (builder, teamsOffset) {
        builder.addFieldOffset(1, teamsOffset, 0);
    };
    GameHeader.createTeamsVector = function (builder, data) {
        builder.startVector(4, data.length, 4);
        for (var i = data.length - 1; i >= 0; i--) {
            builder.addOffset(data[i]);
        }
        return builder.endVector();
    };
    GameHeader.startTeamsVector = function (builder, numElems) {
        builder.startVector(4, numElems, 4);
    };
    GameHeader.addRobotTypeMetadata = function (builder, robotTypeMetadataOffset) {
        builder.addFieldOffset(2, robotTypeMetadataOffset, 0);
    };
    GameHeader.createRobotTypeMetadataVector = function (builder, data) {
        builder.startVector(4, data.length, 4);
        for (var i = data.length - 1; i >= 0; i--) {
            builder.addOffset(data[i]);
        }
        return builder.endVector();
    };
    GameHeader.startRobotTypeMetadataVector = function (builder, numElems) {
        builder.startVector(4, numElems, 4);
    };
    GameHeader.addConstants = function (builder, constantsOffset) {
        builder.addFieldOffset(3, constantsOffset, 0);
    };
    GameHeader.endGameHeader = function (builder) {
        var offset = builder.endObject();
        return offset;
    };
    return GameHeader;
}());
exports.GameHeader = GameHeader;