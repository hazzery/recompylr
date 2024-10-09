import pickle

from matplotlib import pyplot
from execute_all import ProgramName, BinarySpecifier, TimeReading


def main() -> None:
    with open("binary_execution_times.bin", "rb") as input_file:
        map: dict[ProgramName, dict[BinarySpecifier, TimeReading]]
        map = pickle.load(input_file)

    figure, axes = pyplot.subplots()

    for program_name, execution_times in map.items():
        for binary_specifier, time_reading in execution_times.items():
            print(program_name, binary_specifier, time_reading)

    x_axis = [thread_count for thread_count, _ in map["thread"]]
    y_axis = [real for real, _, _ in map["thread"].values()]
    axes.plot(x_axis, y_axis)
    pyplot.show()


if __name__ == "__main__":
    main()
