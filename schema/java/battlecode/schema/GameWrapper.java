// automatically generated by the FlatBuffers compiler, do not modify

package battlecode.schema;

import com.google.flatbuffers.BaseVector;
import com.google.flatbuffers.BooleanVector;
import com.google.flatbuffers.ByteVector;
import com.google.flatbuffers.Constants;
import com.google.flatbuffers.DoubleVector;
import com.google.flatbuffers.FlatBufferBuilder;
import com.google.flatbuffers.FloatVector;
import com.google.flatbuffers.IntVector;
import com.google.flatbuffers.LongVector;
import com.google.flatbuffers.ShortVector;
import com.google.flatbuffers.StringVector;
import com.google.flatbuffers.Struct;
import com.google.flatbuffers.Table;
import com.google.flatbuffers.UnionVector;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;

/**
 * If events are not otherwise delimited, this wrapper structure
 * allows a game to be stored in a single buffer.
 * The first event will be a GameHeader; the last event will be a GameFooter.
 * matchHeaders[0] is the index of the 0th match header in the event stream,
 * corresponding to matchFooters[0]. These indices allow quick traversal of
 * the file.
 */
@SuppressWarnings("unused")
public final class GameWrapper extends Table {
  public static void ValidateVersion() { Constants.FLATBUFFERS_23_5_26(); }
  public static GameWrapper getRootAsGameWrapper(ByteBuffer _bb) { return getRootAsGameWrapper(_bb, new GameWrapper()); }
  public static GameWrapper getRootAsGameWrapper(ByteBuffer _bb, GameWrapper obj) { _bb.order(ByteOrder.LITTLE_ENDIAN); return (obj.__assign(_bb.getInt(_bb.position()) + _bb.position(), _bb)); }
  public void __init(int _i, ByteBuffer _bb) { __reset(_i, _bb); }
  public GameWrapper __assign(int _i, ByteBuffer _bb) { __init(_i, _bb); return this; }

  /**
   * The series of events comprising the game.
   */
  public battlecode.schema.EventWrapper events(int j) { return events(new battlecode.schema.EventWrapper(), j); }
  public battlecode.schema.EventWrapper events(battlecode.schema.EventWrapper obj, int j) { int o = __offset(4); return o != 0 ? obj.__assign(__indirect(__vector(o) + j * 4), bb) : null; }
  public int eventsLength() { int o = __offset(4); return o != 0 ? __vector_len(o) : 0; }
  public battlecode.schema.EventWrapper.Vector eventsVector() { return eventsVector(new battlecode.schema.EventWrapper.Vector()); }
  public battlecode.schema.EventWrapper.Vector eventsVector(battlecode.schema.EventWrapper.Vector obj) { int o = __offset(4); return o != 0 ? obj.__assign(__vector(o), 4, bb) : null; }
  /**
   * The indices of the headers of the matches, in order.
   */
  public int matchHeaders(int j) { int o = __offset(6); return o != 0 ? bb.getInt(__vector(o) + j * 4) : 0; }
  public int matchHeadersLength() { int o = __offset(6); return o != 0 ? __vector_len(o) : 0; }
  public IntVector matchHeadersVector() { return matchHeadersVector(new IntVector()); }
  public IntVector matchHeadersVector(IntVector obj) { int o = __offset(6); return o != 0 ? obj.__assign(__vector(o), bb) : null; }
  public ByteBuffer matchHeadersAsByteBuffer() { return __vector_as_bytebuffer(6, 4); }
  public ByteBuffer matchHeadersInByteBuffer(ByteBuffer _bb) { return __vector_in_bytebuffer(_bb, 6, 4); }
  /**
   * The indices of the footers of the matches, in order.
   */
  public int matchFooters(int j) { int o = __offset(8); return o != 0 ? bb.getInt(__vector(o) + j * 4) : 0; }
  public int matchFootersLength() { int o = __offset(8); return o != 0 ? __vector_len(o) : 0; }
  public IntVector matchFootersVector() { return matchFootersVector(new IntVector()); }
  public IntVector matchFootersVector(IntVector obj) { int o = __offset(8); return o != 0 ? obj.__assign(__vector(o), bb) : null; }
  public ByteBuffer matchFootersAsByteBuffer() { return __vector_as_bytebuffer(8, 4); }
  public ByteBuffer matchFootersInByteBuffer(ByteBuffer _bb) { return __vector_in_bytebuffer(_bb, 8, 4); }

  public static int createGameWrapper(FlatBufferBuilder builder,
      int eventsOffset,
      int matchHeadersOffset,
      int matchFootersOffset) {
    builder.startTable(3);
    GameWrapper.addMatchFooters(builder, matchFootersOffset);
    GameWrapper.addMatchHeaders(builder, matchHeadersOffset);
    GameWrapper.addEvents(builder, eventsOffset);
    return GameWrapper.endGameWrapper(builder);
  }

  public static void startGameWrapper(FlatBufferBuilder builder) { builder.startTable(3); }
  public static void addEvents(FlatBufferBuilder builder, int eventsOffset) { builder.addOffset(0, eventsOffset, 0); }
  public static int createEventsVector(FlatBufferBuilder builder, int[] data) { builder.startVector(4, data.length, 4); for (int i = data.length - 1; i >= 0; i--) builder.addOffset(data[i]); return builder.endVector(); }
  public static void startEventsVector(FlatBufferBuilder builder, int numElems) { builder.startVector(4, numElems, 4); }
  public static void addMatchHeaders(FlatBufferBuilder builder, int matchHeadersOffset) { builder.addOffset(1, matchHeadersOffset, 0); }
  public static int createMatchHeadersVector(FlatBufferBuilder builder, int[] data) { builder.startVector(4, data.length, 4); for (int i = data.length - 1; i >= 0; i--) builder.addInt(data[i]); return builder.endVector(); }
  public static void startMatchHeadersVector(FlatBufferBuilder builder, int numElems) { builder.startVector(4, numElems, 4); }
  public static void addMatchFooters(FlatBufferBuilder builder, int matchFootersOffset) { builder.addOffset(2, matchFootersOffset, 0); }
  public static int createMatchFootersVector(FlatBufferBuilder builder, int[] data) { builder.startVector(4, data.length, 4); for (int i = data.length - 1; i >= 0; i--) builder.addInt(data[i]); return builder.endVector(); }
  public static void startMatchFootersVector(FlatBufferBuilder builder, int numElems) { builder.startVector(4, numElems, 4); }
  public static int endGameWrapper(FlatBufferBuilder builder) {
    int o = builder.endTable();
    return o;
  }

  public static final class Vector extends BaseVector {
    public Vector __assign(int _vector, int _element_size, ByteBuffer _bb) { __reset(_vector, _element_size, _bb); return this; }

    public GameWrapper get(int j) { return get(new GameWrapper(), j); }
    public GameWrapper get(GameWrapper obj, int j) {  return obj.__assign(__indirect(__element(j), bb), bb); }
  }
}
