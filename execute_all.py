import os
import pprint
import toml
import asyncio
import subprocess
import matplotlib


BUILD_SPECIFICATION_FILE = "build_specification.toml"

map: dict[tuple[str, int, int], list[str]] = {}


def execution_command(file_name: str) -> list[str]:
    return ["time", "-p", build_spec["directory"] + "/" + file_name]


async def execute_binary(file_name: str) -> None:
    program_name, thread_count, process_count = file_name.rstrip(
        build_spec["extension"]
    ).split(build_spec["delimeter"])

    binary_identifier = (
        program_name,
        int(thread_count.rstrip("t")),
        int(process_count.rstrip("p")),
    )

    command = execution_command(file_name)
    print(*command)

    with open(build_spec["example_input_file"], "rb") as input_file:
        process_input = input_file.read()

    result = subprocess.run(command, capture_output=True, input=process_input)
    map[binary_identifier] = result.stderr.decode().splitlines()


async def main() -> None:
    tasks = [
        execute_binary(file_name) for file_name in os.listdir(build_spec["directory"])
    ]

    await asyncio.gather(*tasks)

    pprint.pprint(map)


if __name__ == "__main__":
    build_spec = toml.load(BUILD_SPECIFICATION_FILE)["config"]

    asyncio.run(main())
