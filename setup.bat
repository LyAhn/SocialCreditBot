@echo off
REM Creates two blank text files for you
type nul > token.txt 
type nul > keywords.txt

REM Sets up python environment
python -m venv venv
