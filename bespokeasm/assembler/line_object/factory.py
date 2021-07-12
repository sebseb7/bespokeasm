import re

from bespokeasm.assembler.model import AssemblerModel
from bespokeasm.assembler.line_object import LineObject
from bespokeasm.assembler.line_object.label_line import LabelLine
from bespokeasm.assembler.line_object.directive_line import DirectiveLine
from bespokeasm.assembler.line_object.instruction_line import InstructionLine

class LineOjectFactory:
    PATTERN_COMMENTS = re.compile(
        r'((?<=\;).*)$',
        flags=re.IGNORECASE|re.MULTILINE
    )
    PATTERN_INSTRUCTION_CONTENT = re.compile(
        r'^([^\;\n]*)',
        flags=re.IGNORECASE|re.MULTILINE
    )

    @classmethod
    def parse_line(cls, line_num: int, line_str: str, model: AssemblerModel) -> LineObject:
        # find comments
        comment_str = ''
        comment_match = re.search(LineOjectFactory.PATTERN_COMMENTS, line_str)
        if comment_match is not None:
            comment_str = comment_match.group(1).strip()

        # find instruction
        instruction_str = ''
        instruction_match = re.search(LineOjectFactory.PATTERN_INSTRUCTION_CONTENT, line_str)
        if instruction_match is not None:
            instruction_str = instruction_match.group(1).strip()

        # parse instruction
        if len(instruction_str) > 0:
            # try label
            line_obj = LabelLine.factory(line_num, instruction_str, comment_str, model.registers)
            if line_obj is not None:
                return line_obj

            # try directives
            line_obj = DirectiveLine.factory(line_num, instruction_str, comment_str, model.endian)
            if line_obj is not None:
                return line_obj

            # try instruction
            line_obj = InstructionLine.factory(line_num, instruction_str, comment_str, model)
            if line_obj is not None:
                return line_obj

        # if we got here, the line is only a comment
        line_obj = LineObject(line_num, instruction_str, comment_str)
        return line_obj