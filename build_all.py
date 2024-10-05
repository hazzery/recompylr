import asyncio
import subprocess

THREAD_COUNTS = [2, 4, 8, 16, 32, 64]
PROCESS_COUNTS = [2, 4, 6, 8, 10, 12]
PROGRAM_NAMES = ["serial", "thread", "process", "processThread"]
COMPILER_NAME = "gcc"
COMPILER_FLAGS = ["-Wall", "-Werror", "-Wextra", "-Wpedantic"]
LINKER_FLAGS = ["-lm", "-lpthread"]


def sourceFile(program_name: str) -> str:
    return program_name + ".c"


def binaryFile(
    program_name: str,
    thread_count: int,
    process_count: int,
) -> str:
    return f"{program_name}-{thread_count}t-{process_count}p.out"


def compilation_command(
    program_name: str,
    thread_count: int,
    process_count: int,
) -> list[str]:
    macro_definitions = ""

    if thread_count is not None:
        macro_definitions += "-D THREAD_COUNT=" + str(thread_count)

    if process_count is not None:
        macro_definitions += "-D PROCESS_COUNT=" + str(process_count)

    return (
        [COMPILER_NAME, sourceFile(program_name)]
        + COMPILER_FLAGS
        + ["-o", binaryFile(program_name, thread_count, process_count)]
        + LINKER_FLAGS
    )


async def compile_program(
    program_name: str,
    thread_count: int,
    process_count: int,
) -> None:
    subprocess.run(
        compilation_command(
            program_name, thread_count=thread_count, process_count=process_count
        )
    )


async def main() -> None:
    tasks = [
        compile_program(program_name, thread_count, process_count)
        for thread_count in THREAD_COUNTS
        for process_count in PROCESS_COUNTS
        for program_name in PROGRAM_NAMES
    ]

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
