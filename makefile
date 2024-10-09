.PHONY: run thread process processThread clean draw

COMPILER_FLAGS := -Wall -Werror -Wextra -Wpedantic
LINKER_FLAGS := -lm -lpthread

all:
	python3 build_all.py

run:
	python3 execute_all.py

draw:
	python3 draw_graphs.py

%.out: %.c
	gcc $^ $(COMPILER_FLAGS) -D MAX_CHILDREN=12 -D NUMBER_OF_THREADS=12 -o $@ $(LINKER_FLAGS)


serial: serial.out exampleTestCases.txt
	./serial.out < exampleTestCases.txt

thread: thread.out exampleTestCases.txt
	./thread.out < exampleTestCases.txt

process: process.out exampleTestCases.txt
	./process.out < exampleTestCases.txt

processThread: processThread.out exampleTestCases.txt
	./processThread.out < exampleTestCases.txt

clean:
	rm **/*.out

