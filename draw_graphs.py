import pickle

import toml
from matplotlib import pyplot

from execute_all import BinarySpecifier, ProgramName, TimeReading

BUILD_SPECIFICATION_FILE = "build_specification.toml"


def draw_process(map: dict[ProgramName, dict[BinarySpecifier, TimeReading]]):
    figure, axes = pyplot.subplots()

    x_axis = sorted([process_count for _, process_count in map["process"]])
    y_axis = [map["process"][(1, process_count)][0] for process_count in x_axis]

    axes.set_title("process.c running times")
    axes.set_xlabel("Maximum number of children processes")
    axes.set_ylabel("Execution time (seconds)")
    axes.set_xticks(x_axis)
    axes.plot(x_axis, y_axis)

    figure.savefig("process_graph.png")


def draw_process_thread(map: dict[ProgramName, dict[BinarySpecifier, TimeReading]]):
    figure = pyplot.figure()
    axes = figure.add_subplot(projection="3d")

    y_axis = range(2, 21, 2)
    x_axis = range(20, 0, -2)
    colours = [
        "red",
        "yellow",
        "green",
        "blue",
        "indigo",
    ] * 2
    for colour, y_tick in zip(colours, y_axis):
        z_axis = [map["processThread"][(x_tick, y_tick)][0] for x_tick in x_axis]

        colour_row = [colour] * len(x_axis)
        axes.bar(x_axis, z_axis, zs=y_tick, zdir="y", color=colour_row, alpha=0.75)

    axes.set_title("processThread.c running times")
    axes.set_xlabel("Number of worker threads")
    axes.set_ylabel("Maximum number of children processes")
    axes.set_zlabel("Execution time (seconds)")
    axes.set_xticks(x_axis)
    axes.set_yticks(y_axis)

    figure.savefig("processThread_graph.png")


def draw_thread(map: dict[ProgramName, dict[BinarySpecifier, TimeReading]]):
    figure, axes = pyplot.subplots()

    x_axis = sorted([thread_count for thread_count, _ in map["thread"]])
    y_axis = [map["thread"][(thread_count, 1)][0] for thread_count in x_axis]

    axes.set_title("thread.c running times.")
    axes.set_xlabel("Number of worker threads")
    axes.set_ylabel("Execution time (seconds)")
    axes.set_xticks(x_axis)
    axes.plot(x_axis, y_axis)

    figure.savefig("thread_graph.png")


def main() -> None:
    with open("binary_execution_times.bin", "rb") as input_file:
        map: dict[ProgramName, dict[BinarySpecifier, TimeReading]]
        map = pickle.load(input_file)

    if "thread" not in build_spec["skip"]:
        draw_thread(map)

    if "process" not in build_spec["skip"]:
        draw_process(map)

    if "processThread" not in build_spec["skip"]:
        draw_process_thread(map)


if __name__ == "__main__":
    build_spec = toml.load(BUILD_SPECIFICATION_FILE)["config"]
    main()
