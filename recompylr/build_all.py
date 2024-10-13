import asyncio
import itertools
import os
import pathlib
import subprocess
from typing import Any, Sequence

import toml

BUILD_SPECIFICATION_FILE = "build_specification.toml"


def source_file(program_name: str) -> str:
    """Get the name of the source file for the given program.

    :program_name: The name of the program to find the source file of.

    :return: The name of the source file as a string.
    """
    return program_name + ".c"


def binary_file(
    program_name: str,
    thread_count: int,
    process_count: int,
) -> str:
    """Create the name of the binary file to generate for a given program.

    :program_name: The name of the source file to compile.
    :thread_count: The number of threads to allow the program to use.
    :process_count: The maximum number of children process to allow the program to spawn.

    :return: The name of the file as a string.
    """
    return f"{build_spec['directory']}/{program_name}{build_spec['delimeter']}{thread_count}t-{process_count}p{build_spec['extension']}"


def compilation_command(
    program_name: str,
    thread_count: int,
    process_count: int,
) -> list[str]:
    """Generate the command used to compile the specified program.

    :program_name: The name of the source file to compile.
    :thread_count: The number of threads to allow the program to use.
    :process_count: The maximum number of children process to allow the program to spawn.

    :return: The shell command as a list of strings
    """
    macro_definitions = []

    if thread_count != 1:
        macro_definitions.append("-D NUMBER_OF_THREADS=" + str(thread_count))

    if process_count != 1:
        macro_definitions.append("-D MAX_CHILDREN=" + str(process_count))

    if build_spec["logging"]:
        macro_definitions.append("-D LOGGING")

    return [
        build_spec["compiler"],
        source_file(program_name),
        *build_spec["compilation_flags"],
        *macro_definitions,
        "-o",
        binary_file(program_name, thread_count, process_count),
        *build_spec["linker_flags"],
    ]


async def compile_program(
    program_name: str,
    *,
    thread_count: int = 1,
    process_count: int = 1,
) -> None:
    """Execute the compilation of the specified program.

    :program_name: The name of the source file to compile.
    :thread_count: The number of threads to allow the program to use.
    :process_count: The maximum number of children process to allow the program to spawn.
    """
    task = compilation_command(program_name, thread_count, process_count)
    print(*task)
    subprocess.run(task, check=False)


def list_program_definitions() -> dict[str, dict[str, Any]]:
    programs = {}

    global_definitions: dict[str, Any] = build_spec["compilation"]["definitions"]
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


def list_all_binaries(program_definitions: dict[str, dict[str, Any]]) -> list[str]:
    for program_name, definitions in program_definitions.items():
        plural_definitions = filter(
            lambda definition: isinstance(definition, Sequence), definitions.values()
        )

        print(program_name, *itertools.product(plural_definitions))
    return []


async def main() -> None:
    tasks = []

    if "thread" not in build_spec["skip"]:
        tasks += [
            compile_program("thread", thread_count=thread_count)
            for thread_count in build_spec["thread_counts"]
        ]

    if "process" not in build_spec["skip"]:
        tasks += [
            compile_program("process", process_count=process_count)
            for process_count in build_spec["process_counts"]
        ]

    if "processThread" not in build_spec["skip"]:
        tasks += [
            compile_program(
                "processThread", thread_count=thread_count, process_count=process_count
            )
            for thread_count in build_spec["thread_counts"]
            for process_count in build_spec["process_counts"]
        ]

    os.makedirs(build_spec["directory"], exist_ok=True)
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    build_spec = toml.load(BUILD_SPECIFICATION_FILE)
    program_definitions = list_program_definitions()
    list_all_binaries(program_definitions)
    # asyncio.run(main())
