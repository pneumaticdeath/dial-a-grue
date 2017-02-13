# UNIX C makefile for the ZIP Infocom interpreter

CC = cc
# CFLAGS = -O -DPOSIX
# CFLAGS = -ggdb -DPOSIX
CFLAGS = -O -DPOSIX
LDFLAGS =
# LIBS = -ltermcap
LIBS = 

INC = ztypes.h
OBJS = zip.o control.o extern.o fileio.o input.o interpre.o math.o memory.o \
	object.o operand.o osdepend.o property.o ser_screen.o text.o variable.o ser_io.o
	# object.o operand.o osdepend.o property.o screen.o text.o variable.o unixio.o
	# unixio.o

zvm : $(OBJS)
	$(CC) -o $@ $(LDFLAGS) $(OBJS) $(LIBS)

$(OBJS) : $(INC) extern.c

clean :
	-rm -f *.o zvm core
