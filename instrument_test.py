from RestrictedPython import compile_restricted
from types import CodeType
import dis

with open("./players/examplefuncsplayer/bot.py") as f:
    code_str = f.read()

bytecode: CodeType = compile_restricted(code_str, "bot.py", "exec")

print("ORIGINAL:")
print(dis.dis(bytecode, show_caches=True))

instructions = list(dis.get_instructions(bytecode))

byte_array = [[inst.opcode, 0 if inst.arg is None else inst.arg % 256] for inst in instructions]
new_code = bytes(sum(byte_array, []))

new_bytecode = CodeType(bytecode.co_argcount,
                        bytecode.co_posonlyargcount,
                        bytecode.co_kwonlyargcount,
                        bytecode.co_nlocals,
                        bytecode.co_stacksize,
                        bytecode.co_flags,
                        new_code,
                        bytecode.co_consts,
                        bytecode.co_names,
                        bytecode.co_varnames,
                        bytecode.co_filename,
                        bytecode.co_name,
                        bytecode.co_qualname,
                        bytecode.co_firstlineno,
                        bytecode.co_linetable,
                        bytecode.co_exceptiontable,
                        bytecode.co_freevars,
                        bytecode.co_cellvars)
    
print("INSTRUMENTED:")
print(dis.dis(new_bytecode, show_caches=True))
print(dis.opmap)
