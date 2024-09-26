.PHONY: run thread

all: run

thread.out: thread.c
	gcc thread.c -Wall -Werror -Wextra -Wpedantic -o thread.out -lm -lpthread

serial.out: serial.c
	gcc thread.c -Wall -Werror -Wextra -Wpedantic -o thread.out -lm -lpthread

process.out: process.c
	gcc process.c -Wall -Werror -Wextra -Wpedantic -o process.out -lm -lpthread

thread: thread.out serial.out exampleTestCases.txt
	./thread.out < exampleTestCases.txt
	./serial.out < exampleTestCases.txt

process: process.out exampleTestCases.txt
	./process.out < exampleTestCases.txt

run: process
