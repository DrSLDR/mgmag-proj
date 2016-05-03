#!/bin/bash

NAME="main"
USEBIBTEX=0

ifeq ($(USEBIBTEX),1)
all: compile bibtex check clean cleanbib
else
all: compile check clean
endif


compile:
	pdflatex $(NAME).tex

bibtex:
	bibtex $(NAME).aux
	pdflatex $(NAME).tex
	pdflatex $(NAME).tex

check:
	@echo $<`grep Overfull $(NAME).log`
	@echo $<`grep Underfull $(NAME).log`

ifeq ($(USEBIBTEX),1)
clean: cleanbib
else
clean:
endif
	rm -v *.aux *.log *.out

cleanbib:
	rm -v *.bbl *.blg

purge: clean
	rm -v *.pdf
