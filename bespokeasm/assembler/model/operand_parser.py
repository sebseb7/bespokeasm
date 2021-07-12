import sys

from bespokeasm.assembler.byte_code.parts import ByteCodePart
from bespokeasm.assembler.model.operand_set import OperandSet, OperandSetCollection

# Operand Parser
#
# An operand parser consists of:
#    - A list of 0 or more OperandSets, order is expected operand order
#    - A list of operand ID tuples representing operand combinations to not allow
#    - A list of zero or more specific operand tuples representing signatures of
#      operands not generable from the OperandSets
#
# The parsing of an operand list will be done in this order:
#    1. Determine if the operand list matches and specific operand tuples. If so
#       generate byte byte code and argument values and return
#    2. Determine if the operand list can match any operand signature generable from
#       the OperandSets. If so, ensure that signature does not match a disallowed signatre,
#       then generate byte byte code and argument values and return
#    3. Error
#


class OperandParser:
    def __init__(self, instruction_operands_config: dict, operand_set_collection: OperandSetCollection):
        if instruction_operands_config is not None:
            self._config = instruction_operands_config
        else:
            self._config = {'count': 0}
        self._operand_sets = []
        if 'operand_sets' in self._config:
            operand_sets = self._config['operand_sets']['list']
            self._operand_sets = [operand_set_collection.get_operand_set(k) for k in operand_sets]

    def __repr__(self) -> str:
        return str(self)
    def __str__(self) -> str:
        return f'OperandParser<{self._operand_sets}>'

    def validate(self, instruction: str):
        # check to make sure we as many operands configured as count.
        if self.operand_count != len(self._operand_sets):
            sys.exit(f'ERROR: CONFIGURATION - the number of properly configured operands ({len(self._operand_sets)}) does not match prescribed number ({self.operand_count}) for instruction "{instruction}"')

    @property
    def operand_count(self) -> int:
        return self._config['count']
    def reverse_argument_order(self) -> bool:
        '''Determines whether the order that the instruction's argument values
        emitted in machine code should be in the same order as the argument
        (false) or reversed (true)
        '''
        return self._config.get('reverse_argument_order', False)
    @property
    def _has_operand_sets(self):
        return ('operand_sets' in self._config)

    def generate_machine_code(self, line_num:int, operands: list[str]) -> tuple[list[ByteCodePart], list[ByteCodePart]]:
        bytecode_list = []
        argument_values = []
        if len(operands) == self.operand_count:
            if self.operand_count > 0 and self._has_operand_sets:
                bytecode_list, argument_values = self._find_operands_from_operand_sets(line_num, operands)
        else:
            sys.exit(f'ERROR: line {line_num} - INTERNAL - operand list wrongs size. Expected {self.operand_count}, got {len(operands)}')
        return (bytecode_list, argument_values)

    def _find_operands_from_operand_sets(self, line_num:int, operands: list[str]) -> tuple[list[ByteCodePart], list[ByteCodePart]]:
        bytecode_list = []
        argument_values = []
        operand_ids = []
        for i in range(self.operand_count):
            operand_id, bytecode_part, argument_part = self._operand_sets[i].parse_operand(line_num, operands[i])
            if bytecode_part is not None:
                bytecode_list.append(bytecode_part)
            if argument_part is not None:
                argument_values.append(argument_part)
            if bytecode_part is None and argument_part is None:
                # if there is an argument, something should be produced, so this is and error
                sys.exit(f'ERROR: line {line_num} - Unrecognized operand "{operands[i]}"')
            else:
                operand_ids.append(operand_id)
        # now check to ensure this is an allowed combo
        if 'disallowed_pairs' in self._config['operand_sets']:
            if operand_ids in self._config['operand_sets']['disallowed_pairs']:
                sys.exit(f'ERROR: line {line_num} - unallowed operands {operand_ids} for instruction')

        if self.reverse_argument_order and len(argument_values) > 1:
            argument_values.reverse()

        return (bytecode_list, argument_values)