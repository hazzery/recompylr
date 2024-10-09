import asyncio
import toml
import os
import subprocess

PROGRAM_NAMES = ["serial", "thread", "process", "processThread"]
COMPILER_NAME = "gcc"
COMPILER_FLAGS = ["-Wall", "-Werror", "-Wextra", "-Wpedantic"]
LINKER_FLAGS = ["-lm", "-lpthread"]

BUILD_SPECIFICATION_FILE = "build_specification.toml"


def sourceFile(program_name: str) -> str:
    return program_name + ".c"


def binaryFile(
    program_name: str,
    thread_count: int,
    process_count: int,
) -> str:
    return f"{build_spec['directory']}/{program_name}{build_spec['delimeter']}{thread_count}t-{process_count}p{build_spec['extension']}"


def compilation_command(
    program_name: str,
    thread_count: int,
    process_count: int,
) -> list[str]:
    macro_definitions = []

    if thread_count != 1:
        macro_definitions.append("-D NUMBER_OF_THREADS=" + str(thread_count))

    if process_count != 1:
        macro_definitions.append("-D MAX_CHILDREN=" + str(process_count))

    if build_spec["logging"]:
        macro_definitions.append("-D LOGGING")

    return (
        [COMPILER_NAME, sourceFile(program_name)]
        + COMPILER_FLAGS
        + macro_definitions
        + [
            "-o",
            binaryFile(program_name, thread_count, process_count),
        ]
        + LINKER_FLAGS
    )


async def compile_program(
    program_name: str,
    *,
    thread_count: int = 1,
    process_count: int = 1,
) -> None:
    task = compilation_command(program_name, thread_count, process_count)
    print(*task)
    subprocess.run(task)


async def main() -> None:
    tasks = [
        compile_program("thread", thread_count=thread_count)
        for thread_count in build_spec["thread_counts"]
    ]

    tasks += [
        compile_program("process", process_count=process_count)
        for process_count in build_spec["process_counts"]
    ]

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
    build_spec = toml.load(BUILD_SPECIFICATION_FILE)["config"]
    asyncio.run(main())
