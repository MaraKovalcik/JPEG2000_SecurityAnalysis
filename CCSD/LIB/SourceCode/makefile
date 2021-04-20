# My attempt to produce a working makefile for the CCSDS image compression software from U. Nebraska

# Compiler:
CC = gcc

BPEFLAGS = -O2 -c -Wall

BPEFILES = AC_BitPlaneCoding.c StagesCodingGaggles.c header.c AdjustOutput.c bitsIO.c lifting_97M.c BPEBlockCoding.c bpe_decoder.c lifting_97f.c CoeffGroup.c bpe_encoder.c main.c DC_EnDeCoding.c errorhandle.c ricecoding.c PatternCoding.c getopt.c waveletbpe.c

bpe: ${BPEFILES}

bpe: ${BPEFILES}
	${CC} ${BPEFLAGS} ${BPEFILES}
	${CC} *.o -o bpe -lm
	rm AC_BitPlaneCoding.o DC_EnDeCoding.o bpe_decoder.o header.o ricecoding.o AdjustOutput.o PatternCoding.o bpe_encoder.o lifting_97M.o waveletbpe.o BPEBlockCoding.o StagesCodingGaggles.o errorhandle.o lifting_97f.o CoeffGroup.o bitsIO.o getopt.o main.o
	


# Linker:
#LDFLAGS = -lm

# Default rule
