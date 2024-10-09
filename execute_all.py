import os
import pprint
import toml
import asyncio
import subprocess
import pickle


BUILD_SPECIFICATION_FILE = "build_specification.toml"

ProgramName = str
BinarySpecifier = tuple[int, int]
TimeReading = tuple[float, float, float]

map: dict[ProgramName, dict[BinarySpecifier, TimeReading]] = {}


def execution_command(file_name: str) -> list[str]:
    return [
        "time",
        "--portability",
        f"--output=txt/{file_name}.txt",
        f"{build_spec['directory']}/{file_name}",
    ]


async def time_binary_execution(file_name: str) -> None:
    program_name, thread_count, process_count = file_name.removesuffix(
        build_spec["extension"]
    ).split(build_spec["delimeter"])

    binary_specifier = (
        int(thread_count.removesuffix("t")),
        int(process_count.removesuffix("p")),
    )

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
    tasks = [
        time_binary_execution(file_name)
        for file_name in os.listdir(build_spec["directory"])
    ]

    await asyncio.gather(*tasks)

    with open("binary_execution_times.bin", "wb") as output_file:
        pickle.dump(map, output_file)

    pprint.pprint(map)


if __name__ == "__main__":
    build_spec = toml.load(BUILD_SPECIFICATION_FILE)["config"]

    asyncio.run(main())
