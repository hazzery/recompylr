import pickle

from matplotlib import pyplot
from execute_all import ProgramName, BinarySpecifier, TimeReading


def main() -> None:
    with open("binary_execution_times.bin", "rb") as input_file:
        map: dict[ProgramName, dict[BinarySpecifier, TimeReading]]
        map = pickle.load(input_file)

    # Thread program graph
    figure, axes = pyplot.subplots()

    x_axis = sorted([thread_count for thread_count, _ in map["thread"]])
    y_axis = [map["thread"][(thread_count, 1)][0] for thread_count in x_axis]

    axes.set_xlabel("Number of worker threads")
    axes.set_ylabel("Execution time (seconds)")
    axes.plot(x_axis, y_axis)

    figure.savefig("thread_graph.png")

    # Process program graph
    figure, axes = pyplot.subplots()

    x_axis = sorted([process_count for _, process_count in map["process"]])
    y_axis = [map["process"][(1, process_count)][0] for process_count in x_axis]

    axes.set_xlabel("Maximum number of children processes")
    axes.set_ylabel("Execution time (seconds)")
    axes.plot(x_axis, y_axis)

    figure.savefig("process_graph.png")


if __name__ == "__main__":
    main()
