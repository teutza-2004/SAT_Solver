CFLAGS=-Wall 

.PHONY: clean build run

build: ./src/main.c
	gcc ./src/main.c ./src/functions.c $(CFLAGS) -o main

run: main
	./main $(INPUT) $(OUTPUT)

clean:
	rm -f main
