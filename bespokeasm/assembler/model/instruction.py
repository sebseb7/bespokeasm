import sys

from bespokeasm.assembler.line_identifier import LineIdentifier
from bespokeasm.assembler.byte_code.assembled import AssembledInstruction
from bespokeasm.assembler.model.operand_parser import OperandParser
from bespokeasm.assembler.model.operand_set import OperandSetCollection
from bespokeasm.assembler.byte_code.parts import NumericByteCodePart

# Instruction
#
# An instruction has two parts: mnemonic and zero or more operands. The instruction
# will generate machine code that consists first of the vyte code from the mnemonic
# then each of the operands (in order), and then followed by the data generated by each
# in order.
#


class Instruction:
    def __init__(self, mnemonic: str, instruction_config: dict, operand_set_collection: OperandSetCollection, default_endian: str):
        self._mnemonic = mnemonic
        self._config = instruction_config
        #validate config
        if 'byte_code' not in self._config:
            sys.exit(f'ERROR: configuration for inbstruction "{mnemonic}" does not have a cyte code configuration')

        self._operand_parser = OperandParser(self._config.get('operands', None), operand_set_collection, default_endian)
        self._operand_parser.validate(self._mnemonic)

    def __repr__(self) -> str:
        return str(self)
    def __str__(self) -> str:
        return f'Instruction<{self._mnemonic},{self._operand_parser}>'

    @property
    def mnemonic(self) -> str:
        return self._mnemonic
    @property
    def operand_count(self) -> int:
        return self._operand_parser.operand_count
    @property
    def base_bytecode_size(self) -> int:
        return self._config['byte_code']['size']
    @property
    def base_bytecode_value(self) -> int:
        return self._config['byte_code']['value']

    def generate_bytecode_parts(self, line_id: LineIdentifier, mnemonic: str, operands: str, default_endian: str) -> AssembledInstruction:
        if mnemonic != self.mnemonic:
            # this shouldn't happen
            sys.exit(f'ERROR: {line_id} - INTERNAL - Asked instruction {self} to parse mnemonic "{mnemonic}"')
        if operands is not None and operands != '':
            operand_list = operands.strip().split(',')
        else:
            operand_list = []

        # generate the machine code parts
        instruction_endian = self._config['byte_code'].get('endian', default_endian)
        machine_code = [NumericByteCodePart(self.base_bytecode_value, self.base_bytecode_size, True, instruction_endian)]


        operand_bytecode, operand_arguments = self._operand_parser.generate_machine_code(line_id, operand_list)
        if operand_bytecode is not None:
            machine_code.extend(operand_bytecode)
        if operand_arguments is not None:
            machine_code.extend(operand_arguments)

        return AssembledInstruction(line_id, machine_code)



