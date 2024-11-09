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
 * Generic action representing damage to a robot
 */
@SuppressWarnings("unused")
public final class DamageAction extends Struct {
  public void __init(int _i, ByteBuffer _bb) { __reset(_i, _bb); }
  public DamageAction __assign(int _i, ByteBuffer _bb) { __init(_i, _bb); return this; }

  public int id() { return bb.getShort(bb_pos + 0) & 0xFFFF; }
  public int damage() { return bb.getShort(bb_pos + 2) & 0xFFFF; }

  public static int createDamageAction(FlatBufferBuilder builder, int id, int damage) {
    builder.prep(2, 4);
    builder.putShort((short) damage);
    builder.putShort((short) id);
    return builder.offset();
  }

  public static final class Vector extends BaseVector {
    public Vector __assign(int _vector, int _element_size, ByteBuffer _bb) { __reset(_vector, _element_size, _bb); return this; }

    public DamageAction get(int j) { return get(new DamageAction(), j); }
    public DamageAction get(DamageAction obj, int j) {  return obj.__assign(__element(j), bb); }
  }
}
