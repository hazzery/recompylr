.PHONY: run thread process processThread clean

COMPILER_FLAGS := -Wall -Werror -Wextra -Wpedantic
LINKER_FLAGS := -lm -lpthread

all:
	python3 build_all.py

run:
	python3 execute_all.py

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
	rm -r build/
	rm -f processThread.out
	rm -f process.out
	rm -f thread.out

