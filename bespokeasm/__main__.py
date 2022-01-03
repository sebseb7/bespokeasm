import click
import os
import sys

from bespokeasm import BESPOKEASM_VERSION_STR
from bespokeasm.assembler import Assembler
from bespokeasm.configgen.vscode import VSCodeConfigGenerator

@click.group()
@click.version_option(BESPOKEASM_VERSION_STR)
def main():
    """A Bespoke ISA Assembler"""
    pass

@main.command(short_help='compile an assembly file into bytecode')
@click.argument('asm_file')
@click.option('--config-file', '-c', required=True, help='The filepath to the instruction set configuration file,')
@click.option('--output-file', '-o', help='The filepath to where the binary image will be written. Defaults to the input file name with a *.bin extension.')
@click.option('--binary-min-address', '-s', default=0, help='The start address that will be included in the binary output. Useful for building ROM images in a given address range. Defaults to 0.')
@click.option('--binary-max-address', '-e', default=-1, help='The maximum address that will be included in the binary output. Useful for building ROM images in a given address range. Defaults to address of last generated byte code.')
@click.option('--binary-fill', '-f', default=0, help='The byte value that should be used to fill empty addresses when generating binary image of a specific size.')
@click.option('--pretty-print', '-p', is_flag=True, default=False, help='if true, a pretty print version of the compilation will be produced.')
@click.option('--pretty-print-output',  default='stdout', help='if pretty-print is enabled, this specifies the output file. Defaults to stdout.')
@click.option('--verbose', '-v', count=True, help='Verbosity of logging')
@click.option('--include-path', '-I', multiple=True, default=[], help='Path to use when searching for included asm files. Multiple paths can be seperately specified.')
def compile(asm_file, config_file, output_file, binary_min_address, binary_max_address, binary_fill, pretty_print, pretty_print_output, verbose, include_path):
    if output_file is None:
        output_file = os.path.splitext(asm_file)[0] + '.bin'
    if verbose:
        click.echo(f'The file to assemble is: {asm_file}')
        click.echo(f'The binary image will be written to: {output_file}')
        if int(binary_min_address) > 0:
            click.echo(f'  with the starting address written: {binary_min_address}')
        if int(binary_max_address) >= 0:
            click.echo(f'  with the maximum address written: {binary_max_address}')

    asm = Assembler(
        asm_file, config_file, output_file,
        int(binary_min_address), int(binary_max_address) if int(binary_max_address) >= 0 else None,
        binary_fill,
        pretty_print, pretty_print_output, verbose,
        include_path,
    )
    asm.assemble_bytecode()

@main.group(short_help='generate a language syntax highlighting extension')
def generate_extension():
    pass


@generate_extension.command(short_help='generate for VisualStudio Code')
@click.option('--config-file', '-c', required=True, help='The filepath to the instruction set configuration file,')
@click.option('--verbose', '-v', count=True, help='Verbosity of logging')
@click.option('--vscode-config-dir', '-d', default='~/.vscode/', help="The file path the Visual Studo Code configuration directory containing the extensions directory.")
@click.option('--language-name', '-l', help="The name of the language in the Visual Studio Code configuration file. Defaults to value provide in instruction set configuration file.")
@click.option('--language-version', '-k', help="The version of the language in the Visual Studio Code configuration file. Defaults to value provide in instruction set configuration file.")
@click.option('--code-extension', '-x', default='asm', help="The file extension for aassembly code files for this languuage configuraton.")
def vscode(config_file, verbose, vscode_config_dir, language_name, language_version, code_extension):
    config_file = os.path.abspath(os.path.expanduser(config_file))
    vscode_config_dir = os.path.abspath(os.path.expanduser(vscode_config_dir))
    generator = VSCodeConfigGenerator(config_file, verbose, vscode_config_dir, language_name, language_version, code_extension)
    generator.generate()

if __name__ == '__main__':
    args = sys.argv
    if "--help" in args or len(args) == 1:
        click.echo("bespokeasm")
    main(auto_envvar_prefix='BESPOKEASM')