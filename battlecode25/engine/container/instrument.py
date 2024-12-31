import dis
import math
from types import CodeType
from .instruction import Instruction

class Instrument:
    """
    A class for instrumenting specific methods (e.g. sort) as well as instrumenting competitor code
    """
    def __init__(self, runner):
        self.runner = runner

    def instrumented_sorted(self, iterable, key=None, reverse=False):
        cost = len(iterable) * int(math.log(len(iterable)))
        self.runner.multinstrument_call(cost)
        if not key and not reverse:
            return sorted(iterable)
        elif not reverse:
            return sorted(iterable, key=key)
        elif not key:
            return sorted(iterable, reverse=reverse)
        return sorted(iterable, key=key, reverse=reverse)

    @staticmethod
    def instrument(bytecode: CodeType):
        """
        The primary method of instrumenting code, which involves injecting a bytecode counter between every instruction to be executed

        :param bytecode: a code object, the bytecode submitted by the player
        :return: a new code object that has been injected with our bytecode counter
        """

        # Ensure all code constants (e.g. list comprehensions) are also instrumented.
        new_consts = []
        for i, constant in enumerate(bytecode.co_consts):
            if type(constant) == CodeType:
                new_consts.append(Instrument.instrument(constant))
            else:
                new_consts.append(constant)
        new_consts = tuple(new_consts)

        instructions = list(dis.get_instructions(bytecode, show_caches=True))

        print("instruction list:")
        for i in instructions:
            print(i.opname)

        #The lowest bit of the argument to LOAD_GLOBAL is whether NULL should be pushed to the stack. The higher bits are the index of the global
        #to load. We will append the instrument function as the last global in the co_names list.

        instrument_name_index = (len(bytecode.co_names) << 1) | 1
        # function_name_index = (len(bytecode.co_names))

        instrument_name_index_2 = (len(bytecode.co_names))

        # the injection, which consists of a function call to an __instrument__ method which increments bytecode
        # these three instructions will be inserted between every line of instrumented code

        # As of Python 3.11, there are cache instructions after certain instructions. Each opcode has a specific number of cache instructions
        # that should go after it.
        injection = [
            dis.Instruction(opcode=116, opname='LOAD_GLOBAL', arg=instrument_name_index%256, argval='__instrument__', argrepr='__instrument__', offset=None, starts_line=None, is_jump_target=False),
            dis.Instruction(opcode=0, opname='CACHE', arg=0, argval=0, argrepr=0, offset=None, starts_line=None, is_jump_target=False),
            dis.Instruction(opcode=0, opname='CACHE', arg=0, argval=0, argrepr=0, offset=None, starts_line=None, is_jump_target=False),
            dis.Instruction(opcode=0, opname='CACHE', arg=0, argval=0, argrepr=0, offset=None, starts_line=None, is_jump_target=False),
            dis.Instruction(opcode=0, opname='CACHE', arg=0, argval=0, argrepr=0, offset=None, starts_line=None, is_jump_target=False),
            dis.Instruction(opcode=171, opname='CALL', arg=0, argval=0, argrepr=0, offset=None, starts_line=None, is_jump_target=False),
            dis.Instruction(opcode=0, opname='CACHE', arg=0, argval=0, argrepr=0, offset=None, starts_line=None, is_jump_target=False),
            dis.Instruction(opcode=0, opname='CACHE', arg=0, argval=0, argrepr=0, offset=None, starts_line=None, is_jump_target=False),
            dis.Instruction(opcode=0, opname='CACHE', arg=0, argval=0, argrepr=0, offset=None, starts_line=None, is_jump_target=False),
            dis.Instruction(opcode=1, opname='POP_TOP', arg=None, argval=None, argrepr=None, offset=None, starts_line=None, is_jump_target=False)
        ]

        injection_2 = [
            dis.Instruction(opcode=2, opname='PUSH_NULL', arg=0, argval=0, argrepr=0, offset=None, starts_line=None, is_jump_target=False),
            dis.Instruction(opcode=101, opname='LOAD_NAME', arg=instrument_name_index_2%256, argval='__instrument__', argrepr='__instrument__', offset=None, starts_line=None, is_jump_target=False),
            dis.Instruction(opcode=171, opname='CALL', arg=0, argval=0, argrepr=0, offset=None, starts_line=None, is_jump_target=False),
            dis.Instruction(opcode=0, opname='CACHE', arg=0, argval=0, argrepr=0, offset=None, starts_line=None, is_jump_target=False),
            dis.Instruction(opcode=0, opname='CACHE', arg=0, argval=0, argrepr=0, offset=None, starts_line=None, is_jump_target=False),
            dis.Instruction(opcode=0, opname='CACHE', arg=0, argval=0, argrepr=0, offset=None, starts_line=None, is_jump_target=False),
            dis.Instruction(opcode=1, opname='POP_TOP', arg=None, argval=None, argrepr=None, offset=None, starts_line=None, is_jump_target=False)
        ]
        #extends the opargs so that it can store the index of __instrument__
        while instrument_name_index > 255: #(255 = 2^8 -1 = 1 oparg)
            instrument_name_index >>= 8
            injection = [
                dis.Instruction(
                    opcode=144,
                    opname='EXTENDED_ARG',
                    arg=instrument_name_index%256,
                    argval=instrument_name_index%256,
                    argrepr=instrument_name_index%256,
                    offset=None,
                    starts_line=None,
                    is_jump_target=False
                )
            ] + injection

        # For maintenance we add an empty jump_to field to each instruction
        for i, instruction in enumerate(instructions):
            instructions[i] = Instruction(instruction)

        # Next, we cache a reference to the jumpers to each jump target in the targets
        for i, instruction in enumerate(instructions):

            

            # We're only looking for jumpers
            if not instruction.is_jumper():
                continue

            print("argval:", instruction.argval)

            target = [t for t in instructions if instruction.argval == t.offset][0]
            instruction.jump_to = target

            # If any targets jump to themselves, that's not kosher.
            if instruction == target:
                raise SyntaxError('No self-referential loops.')

        unsafe = {0, 110, 113, 114, 115, 116, 120, 124, 125, 131, 172}  # bytecode ops that break the instrument

        #110 - 115 jump instructions
        #116 load_global



        # print("instructions:")
        # for i in instructions:
        #     print(i.opname)
        # print()

        # We then inject the injection before every call, except for those following an EXTENDED_ARGS.
        cur_index = -1
        for (cur, last) in zip(instructions[:], [None]+instructions[:-1]):
            cur_index += 1

            if cur_index == 0: #why were we injecting a bytecode counter as the first thing? this will mess up RESUME instruction.
                continue

            if last.opcode == 151: # don't instrument following the resume instruction
                continue

            if last is not None and last.opcode == 144: #EXTEND_ARG
                continue

            if last is not None and last.opcode in unsafe:
                continue

            if cur.opcode == 0: #If we insert on a cache instruction, we will separate the cache instruction from the instruction it's tied to. Bad.
                continue

            for j, inject in enumerate(injection_2):
                injected_instruction = Instruction(inject)
                injected_instruction.was_there = False # keeping track of the instructions added by us
                instructions.insert(cur_index + j, injected_instruction)
            cur_index += len(injection_2)

        # print("after inserting:")
        # for i in instructions:
        #     print(i.opname)
        # print() 


        # Iterate through instructions. If it's a jumper, calculate the new correct offset. For each new offset, if it
        # is too large to fit in the current number of EXTENDED_ARGS, inject a new EXTENDED_ARG before it. If you never
        # insert a new EXTENDED_ARGS, break out of the loop.
        fixed = False
        while not fixed:
            fixed = True

            i = 0
            for instruction in instructions[:]:
                instruction.offset = 2 * i

                if not instruction.is_jumper():
                    i += 1
                    continue

                correct_offset = instruction.calculate_offset(instructions)
                instruction.arg = correct_offset % 256
                correct_offset >>= 8

                extended_args = 0
                while correct_offset > 0:
                    # Check if there is already an EXTENDED_ARGS behind
                    if i > extended_args and instructions[i - extended_args - 1].opcode == 144:
                        instructions[i - extended_args - 1].arg = correct_offset % 256

                    # Otherwise, insert a new one
                    else:
                        instructions.insert(i, Instruction.ExtendedArgs(correct_offset % 256))
                        instruction.extra_extended_args += 1
                        i += 1
                        fixed = False

                    correct_offset >>= 8
                    extended_args += 1
                i += 1

        # print("after fix jump:")
        # for i in instructions:
        #     print(i.opname)
        # print()

        #Maintaining correct line info ( traceback bug fix)
        #co_lnotab stores line information in Byte form
        # It stores alterantively, the number of instructions to the next increase in line number and
        # the increase in line number then
        #We need to ensure that these are bytes (You might want to break an increase into two see the article or code below)
        #The code did not update these bytes, we need to update the number of instructions before the beginning of each line
        #It should be similar to the way the jump to statement were fixed, I tried to mimick them but failed, I feel like I do not inderstand instruction.py
        # I am overestimating the number of instructions before the start of the line in this fix
        # you might find the end of this article helpful: https://towardsdatascience.com/understanding-python-bytecode-e7edaae8734d
        # old_lnotab = {} #stores the old right info in a more usefull way (maps instruction num to line num)
        # i = 0
        # line_num = 0 #maintains line number by adding differences
        # instruction_num = 0 #maintains the instruction num by addind differences
        # while 2*i < len(bytecode.co_lnotab):
        #     instruction_num += bytecode.co_lnotab[2 * i]
        #     line_num += bytecode.co_lnotab[2 * i + 1]
        #     old_lnotab[instruction_num] = line_num
        #     i += 1
        # #Construct a map from old instruction numbers, to new ones.
        # num_injected = 0
        # instruction_index = 0
        # old_to_new_instruction_num = {}
        # for instruction in instructions:
        #     if instruction.was_there:
        #         old_to_new_instruction_num[2 * (instruction_index - num_injected)] = 2 * instruction_index
        #     instruction_index += 1
        #     if not instruction.was_there:
        #         num_injected += 1
        # new_lnotab = {}
        # for key in old_lnotab:
        #     new_lnotab[old_to_new_instruction_num[key]] = old_lnotab[key]

        # #Creating a differences list of integers, while ensuring integers in it are bytes
        # pairs = sorted(new_lnotab.items())
        # new_lnotab = []
        # previous_pair = (0, 0)
        # for pair in pairs:
        #     num_instructions = pair[0] - previous_pair[0]
        #     num_lines = pair[1] - previous_pair[1]
        #     while num_instructions > 127:
        #         new_lnotab.append(127)
        #         new_lnotab.append(0)
        #         num_instructions -= 127
        #     new_lnotab.append(num_instructions)
        #     while num_lines > 127:
        #         new_lnotab.append(127)
        #         new_lnotab.append(0)
        #         num_lines -= 127
        #     new_lnotab.append(num_lines)
        #     previous_pair = pair
        # #tranfer to bytes and we are good :)
        # new_lnotab = bytes(new_lnotab)

        print("instruction list after instrument:")
        for i in instructions:
            print(i.opname, i.arg, i.was_there)
        print()

        # Finally, we repackage up our instructions into a byte string and use it to build a new code object
        byte_array = [[inst.opcode, 0 if inst.arg is None else inst.arg % 256] for inst in instructions]
        new_code = bytes(sum(byte_array, []))
        # print(byte_array)
        # print(new_code)
        # print(len(new_code))

        # Make sure our code can locate the __instrument__ call
        new_names = tuple(bytecode.co_names) + ('instrument', )

        new_lnotab = bytecode.co_linetable

        compiled = Instrument.build_code(bytecode, new_code, new_names, new_consts, new_lnotab)

        # print("compiled result:")
        # print(dis.dis(compiled))
        # print()

        return compiled

    @staticmethod
    def build_code(old_code: CodeType, new_code, new_names, new_consts, new_lnotab):

        old_code.co_lines
        """Helper method to build a new code object because Python does not allow us to modify existing code objects"""
        return CodeType(old_code.co_argcount,
                        old_code.co_posonlyargcount,
                        old_code.co_kwonlyargcount,
                        old_code.co_nlocals,
                        old_code.co_stacksize + 100,
                        old_code.co_flags,
                        new_code,
                        new_consts,
                        new_names,
                        old_code.co_varnames,
                        old_code.co_filename,
                        old_code.co_name,
                        old_code.co_qualname,
                        old_code.co_firstlineno,
                        old_code.co_linetable,
                        old_code.co_exceptiontable,
                        old_code.co_freevars,
                        old_code.co_cellvars)
    
    '''
    class CodeType(
    argcount: int,
    posonlyargcount: int,
    kwonlyargcount: int,
    nlocals: int,
    stacksize: int,
    flags: int,
    codestring: bytes,
    constants: tuple[object, ...],
    names: tuple[str, ...],
    varnames: tuple[str, ...],
    filename: str,
    name: str,
    qualname: str,
    firstlineno: int,
    linetable: bytes,
    exceptiontable: bytes,
    freevars: tuple[str, ...] = ...,
    cellvars: tuple[str, ...] = ...,
    '''
