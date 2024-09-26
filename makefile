.PHONY: run thread process processThread

all: run

thread.out: thread.c
	gcc thread.c -Wall -Werror -Wextra -Wpedantic -o thread.out -lm -lpthread

serial.out: serial.c
	gcc thread.c -Wall -Werror -Wextra -Wpedantic -o thread.out -lm -lpthread

process.out: process.c
	gcc process.c -Wall -Werror -Wextra -Wpedantic -o process.out -lm -lpthread

processThread.out: processThread.c
	gcc processThread.c -Wall -Werror -Wextra -Wpedantic -o processThread.out -lm -lpthread

thread: thread.out serial.out exampleTestCases.txt
	./thread.out < exampleTestCases.txt
	./serial.out < exampleTestCases.txt

process: process.out exampleTestCases.txt
	./process.out < exampleTestCases.txt

processThread: processThread.out exampleTestCases.txt
	./processThread.out < exampleTestCases.txt

run: processThread
