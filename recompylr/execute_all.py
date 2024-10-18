import asyncio
import os
import pickle
import shutil
import subprocess

import toml

BUILD_SPECIFICATION_FILE = "build_specification.toml"

ProgramName = str
BinarySpecifier = tuple[str, ...]
TimeReading = tuple[float, float, float]

map: dict[ProgramName, dict[BinarySpecifier, TimeReading]] = {}


def execution_command(file_name: str) -> list[str]:
    """Generate the command used to time execution of the specified binary.

    :param file_name: The name of the binary to time execution of.
    :return: The execution command as a list of strings.
    """
    return [
        "time",
        "--portability",
        f"--output=txt/{file_name}.txt",
        f"{build_spec['compilation']['binary_output_directory']}/{file_name}",
    ]


async def time_binary_execution(file_name: str) -> None:
    """Time the execution of the specified binary executable.

    :param file_name: The name of the binary file to execute.
    """
    program_name, *definitions = file_name.removesuffix(
        build_spec["compilation"]["binary_file_extension"]
    ).split(build_spec["compilation"]["binary_file_definition_delimeter"])

    binary_specifier = tuple(definition.split("=")[-1] for definition in definitions)

    command = execution_command(file_name)
    print(*command)

    with open(build_spec["example_input_file"], "rb") as input_file:
        process_input = input_file.read()

    subprocess.run(command, input=process_input, check=False)

    with open(f"txt/{file_name}.txt") as output_file:
        real, user, sys = output_file.read().splitlines()

    print(real, user, sys)
    real_time = float(real.removeprefix("real "))
    user_time = float(user.removeprefix("user "))
    sys_time = float(sys.removeprefix("sys "))

    if program_name not in map:
        map[program_name] = {}

    map[program_name][binary_specifier] = (real_time, user_time, sys_time)


async def main() -> None:
    """Execute all binaries specified in the build specification."""
    tasks = [
        time_binary_execution(file_name)
        for file_name in os.listdir(
            build_spec["compilation"]["binary_output_directory"]
        )
    ]

    os.makedirs("txt", exist_ok=True)

    await asyncio.gather(*tasks)

    try:
        shutil.rmtree("txt")
    except OSError:
        pass

    with open("binary_execution_times.bin", "wb") as output_file:
        pickle.dump(map, output_file)


if __name__ == "__main__":
    build_spec = toml.load(BUILD_SPECIFICATION_FILE)

    asyncio.run(main())
