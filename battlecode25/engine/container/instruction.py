import dis
from types import SimpleNamespace

class Instruction(SimpleNamespace):
    def __init__(self, instruction, in_dict=None):
        if in_dict is not None:
            super().__init__(**in_dict)
        else:
            super().__init__(**{a:b for a,b in zip(dis.Instruction._fields+('jump_to', 'was_there', 'extra_extended_args'), instruction + (None, True, 0))})

    def is_jumper(self):
        return self.is_abs_jumper() or self.is_rel_jumper()

    def is_rel_jumper(self):
        return self.opcode in dis.hasjrel

    def is_abs_jumper(self):
        return self.opcode in dis.hasjabs

    @classmethod
    def ExtendedArgs(self, value):
        return Instruction(None, in_dict={
            'opcode':144, 'opname':'EXTENDED_ARGS', 'arg':value,
            'argval':value, 'argrepr':value, 'offset':None,
            'starts_line':None, 'is_jump_target':False, 'was_there': False,
            'extra_extended_args': 0,
        })

    def calculate_offset(self, instructions):
        # Return the offset (rel or abs) to self.jump_to in instructions

        if self.opname == "JUMP_BACKWARD":
            print("backward instruction!")

        starting_loc = instructions.index(self) + 1
        while instructions[starting_loc].opcode == 0:
            print("advancing due to cache instruction")
            starting_loc += 1

        target_loc = instructions.index(self.jump_to) - self.jump_to.extra_extended_args

        if self.is_abs_jumper():
            return target_loc

        self_loc = instructions.index(self)

        # return target_loc - self_loc - 1

        if self.opname == "JUMP_BACKWARD":
            print("backward instruction!", target_loc, starting_loc)
            return starting_loc - target_loc

        return target_loc - starting_loc
