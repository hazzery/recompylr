import asyncio
import itertools
import os
import pathlib
import subprocess
from collections.abc import Iterable, Mapping
from typing import TypeAlias

import toml

BUILD_SPECIFICATION_FILE = "build_specification.toml"

TomlBaseDataType: TypeAlias = str | int | float | bool
DefinitionData: TypeAlias = TomlBaseDataType | list[TomlBaseDataType]


def source_file(program_name: str) -> str:
    """Get the name of the source file for the given program.

    :program_name: The name of the program to find the source file of.

    :return: The name of the source file as a string.
    """
    return (
        build_spec["compilation"]["source_file_directory"] + "/" + program_name + ".c"
    )


def binary_filename(
    program_name: str,
    definition_names: Iterable[str],
    definition_values: Iterable[DefinitionData],
) -> pathlib.Path:
    """Create the name of the binary file to generate for a given program.

    This function builds the filename which should be used for the
    compiled binary of program ``program_name`` with definitions
    ``defintion_names``.

    :program_name: The name of the source file to compile.
    :definition_names: An iterable of names to be defined.
    :definition_values: An iterable of the values each definition should have.

    :return: The name of the file as a string.
    """
    directory = build_spec["compilation"]["binary_output_directory"]
    delimiter = build_spec["compilation"]["binary_file_definition_delimeter"]
    extension = build_spec["compilation"]["binary_file_extension"]
    definitions = (
        f"{name}={value}" for name, value in zip(definition_names, definition_values)
    )
    return (
        pathlib.Path(directory)
        / f"{program_name}{delimiter}{delimiter.join(definitions)}{extension}"
    )


def compilation_command(
    program_name: str,
    definition_names: Iterable[str],
    definition_values: Iterable[DefinitionData],
) -> list[str]:
    """Generate the command used to compile the specified program.

    :program_name: The name of the source file to compile.
    :definition_names: An iterable of names to be defined.
    :definition_values: An iterable of the values each definition should have.

    :return: The shell command as a list of strings.
    """
    definitions = (
        f"-D {definition_name}={definition_value}"
        for definition_name, definition_value in zip(
            definition_names, definition_values
        )
    )
    return [
        build_spec["compilation"]["compiler"],
        source_file(program_name),
        *build_spec["compilation"]["compilation_flags"],
        *definitions,
        "-o",
        binary_filename(program_name, definition_names, definition_values),
        *build_spec["compilation"]["linker_flags"],
    ]


async def compile_program(
    program_name: str,
    definition_names: Iterable[str],
    definition_values: Iterable[DefinitionData],
) -> None:
    """Execute the compilation of the specified program.

    :program_name: The name of the source file to compile.
    :definition_names: An iterable of names to be defined.
    :definition_values: An iterable of the values each definition should have.

    The order of the values in the ``definition_values`` iterable should
    align with the order of the ``definition_names`` iterable. That is
    the name``next(iter(defintion_names))`` should be defined with the
    value ``next(iter(definition_values))``. More simply, if the
    provided iterables were sequences, ``definition_names[0]`` is
    defined with the value ``definition_values[0]``.
    """
    task = compilation_command(program_name, definition_names, definition_values)
    print(*task)
    subprocess.run(task, check=False)


def list_program_definitions() -> Mapping[str, Mapping[str, DefinitionData]]:
    """Generate a dictionary of all programs to compile and the relevant definitions to use.

    :return: A dictionary which maps from a program's name, to another
    dictionary which maps from a definition's name to its value.
    """
    programs = {}

    global_definitions: dict[str, DefinitionData] = build_spec["compilation"][
        "definitions"
    ]
    for path in pathlib.Path(
        build_spec["compilation"]["source_file_directory"]
    ).iterdir():
        program_specific_configuration = (
            build_spec["compilation"].get("programs", {}).get(path.stem, {})
        )

        if program_specific_configuration.get("skip", False):
            continue

        program_specific_definitions = global_definitions.copy()

        excluded_definitions = program_specific_configuration.get(
            "exclude_definitions", []
        )
        if isinstance(excluded_definitions, list):
            for excluded_definition in excluded_definitions:
                program_specific_definitions.pop(excluded_definition)
        else:
            program_specific_definitions.pop(excluded_definitions)

        programs[path.stem] = program_specific_definitions

    return programs


DefinitionNames: TypeAlias = tuple[str, ...]
DefinitionValues: TypeAlias = tuple[DefinitionData, ...]
ProgramName: TypeAlias = str


def list_all_binaries(
    program_definitions: Mapping[str, Mapping[str, DefinitionData]],
) -> dict[ProgramName, tuple[DefinitionNames, list[DefinitionValues]]]:
    """List all of the binaries ``BUILD_SPECIFICATION_FILE`` specifies should be generated.

    :program_definitions: A mapping from a program's name to a mapping
    from defintion name to its value.

    :return: A dictionary which maps from a programs name to a tuple
    containing a tuple of the names to be defined in that program's
    binary, and a list of all variations of the definition's values.
    """
    binaries = {}
    for program_name, definitions in program_definitions.items():
        plural_definitions = []
        inidividuals = []
        for definition in definitions.values():
            if isinstance(definition, list):
                plural_definitions.append(definition)
            else:
                inidividuals.append(definition)

        inidividual_definitions = tuple(inidividuals)
        binaries[program_name] = (
            tuple(definitions),
            [
                (*product, *inidividual_definitions)
                for product in itertools.product(*plural_definitions)
            ],
        )

    return binaries


def get_existing_binaries() -> set[pathlib.Path]:
    """Check the binary output directory for existing binaries.

    :return: A set containg filenames of all existing binaries.
    """
    return set(
        pathlib.Path(build_spec["compilation"]["binary_output_directory"]).iterdir()
    )


def list_binaries_to_compile() -> (
    dict[ProgramName, tuple[DefinitionNames, list[DefinitionValues]]]
):
    """List all binaries which should be compiled.

    :return: A dictionary which maps from a program's name to a tuple
    containing definition names and their values.
    """
    program_specific_definitions = list_program_definitions()
    binaries = list_all_binaries(program_specific_definitions)
    existing_binaries = get_existing_binaries()

    for program_name, (
        definition_names,
        all_definition_values,
    ) in binaries.copy().items():
        binaries[program_name] = (
            definition_names,
            [
                definition_values
                for definition_values in all_definition_values
                if binary_filename(program_name, definition_names, definition_values)
                not in existing_binaries
            ],
        )
    return binaries


async def main() -> None:
    """Compile all binaries as specified in ``BUILD_SPECIFICATION_FILE``."""
    binaries = list_binaries_to_compile()
    os.makedirs(build_spec["compilation"]["binary_output_directory"], exist_ok=True)

    tasks = (
        compile_program(program_name, definition_names, definition_values)
        for program_name, (definition_names, all_definition_values) in binaries.items()
        for definition_values in all_definition_values
    )

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    build_spec = toml.load(BUILD_SPECIFICATION_FILE)
    asyncio.run(main())
