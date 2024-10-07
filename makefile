.PHONY: run thread process processThread clean

COMPILER_FLAGS := -Wall -Werror -Wextra -Wpedantic
LINKER_FLAGS := -lm -lpthread

PROGRAMS := serial thread process processThread

all: PROGRAMS


*.out: *.c
	gcc $^ $(COMPILER_FLAGS) -o $@ $(LINKER_FLAGS)


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

