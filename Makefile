# How to Makefile
# https://www.cs.colby.edu/maxwell/courses/tutorials/maketutor/

CC=gcc
CFLAGS=-I.
DEPS = neighbours_graph.h
OBJ = main.o neighbours_graph.o

DEBUG = no
OPTIMIZATION = -O3

ifeq ($(DEBUG), yes)
	CFLAGS += -g
	OPTIMIZATION = -O0
endif

CFLAGS += $(OPTIMIZATION)

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

lpath: $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS)

.PHONY: clean

clean:
	rm -f lpath *.o
