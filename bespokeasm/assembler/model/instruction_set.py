from bespokeasm.assembler.model.instruction import Instruction
from bespokeasm.assembler.model.operand_set import OperandSetCollection

class InstructionSet(dict):
    def __init__(self, config_dict: dict, operand_set_collection: OperandSetCollection):
        self._config = config_dict
        for mnemonic, instr_config in self._config.items():
            mnemonic = mnemonic.lower()
            self[mnemonic] = Instruction(mnemonic, instr_config, operand_set_collection)

    def get(self, mnemonic:str) -> Instruction:
        return super().get(mnemonic, None)