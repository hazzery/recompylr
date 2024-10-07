import asyncio
import toml
import os
import subprocess

THREAD_COUNTS = [2, 4, 8, 16, 32, 64]
PROCESS_COUNTS = [2, 4, 6, 8, 10, 12]
PROGRAM_NAMES = ["serial", "thread", "process", "processThread"]
COMPILER_NAME = "gcc"
COMPILER_FLAGS = ["-Wall", "-Werror", "-Wextra", "-Wpedantic"]
LINKER_FLAGS = ["-lm", "-lpthread"]

BUILD_SPECIFICATION_FILE = "build_specification.toml"


def sourceFile(program_name: str) -> str:
    return program_name + ".c"


def binaryFile(
    program_name: str,
    *,
    thread_count: int | None = None,
    process_count: int | None = None,
) -> str:
    return f"{build_spec['directory']}/{program_name}{build_spec['delimeter']}{thread_count}t-{process_count}p{build_spec['extension']}"


def compilation_command(
    program_name: str,
    *,
    thread_count: int | None = None,
    process_count: int | None = None,
) -> list[str]:
    macro_definitions = ""

    if thread_count is not None:
        macro_definitions += "-D THREAD_COUNT=" + str(thread_count)

    if process_count is not None:
        macro_definitions += "-D PROCESS_COUNT=" + str(process_count)

    return (
        [COMPILER_NAME, sourceFile(program_name)]
        + COMPILER_FLAGS
        + [
            "-o",
            binaryFile(
                program_name, thread_count=thread_count, process_count=process_count
            ),
        ]
        + LINKER_FLAGS
    )


async def compile_program(
    program_name: str,
    *,
    thread_count: int | None = None,
    process_count: int | None = None,
) -> None:
    subprocess.run(
        compilation_command(
            program_name, thread_count=thread_count, process_count=process_count
        )
    )


async def main() -> None:
    tasks = [
        compile_program("thread", thread_count=thread_count)
        for thread_count in THREAD_COUNTS
    ]

    tasks += [
        compile_program("process", process_count=process_count)
        for process_count in PROCESS_COUNTS
    ]

    tasks += [
        compile_program(
            "processThread", thread_count=thread_count, process_count=process_count
        )
        for thread_count in THREAD_COUNTS
        for process_count in PROCESS_COUNTS
    ]

    os.makedirs(build_spec["directory"], exist_ok=True)
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    build_spec = toml.load(BUILD_SPECIFICATION_FILE)["config"]
    asyncio.run(main())
