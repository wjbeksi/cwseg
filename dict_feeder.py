#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dictionary feeder for lexicon building.  Given a dictionary file of 
Chinese characters encoded in UTF-8, add each word definition to the 
lexicon dictionary.  Note that the lexicon building program (segmenter.py) 
must be in the same directory as this script.
"""
import os
import sys
import signal
import argparse
from segmenter import is_chinese, is_space, is_comma, is_vline, add_word, read_dict, write_dict

nwords = 0

def signal_handler(signal, frame):
    sys.exit(0)

def parse_line(data, lex_dict):
    global nwords

    d = data.decode('utf-8', errors='ignore')
    l = len(d)
    word = ''

    for c in d:
        if is_chinese(c):
            word += c
        elif is_space(c) or is_comma(c) or is_vline(c) or c == '\n':
            if len(word) > 0:
                add_word(word, 1, lex_dict)
                nwords += 1
                word = ''

def main():
    lex_dict = {}
    dictname = 'lex_dict.p'

    parser = argparse.ArgumentParser(description='Dictionary feeder for lexicon building')
    parser.add_argument('-d', '--dict', action='store', dest='dfilename',
                        help="dictionary input file, e.g. 'cedict_ts.u8'")
    parser.add_argument('-l', '--lexdict', action='store', dest='lfilename',
                        help="lexicon dictionary file")
    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose',
                        help="enable verbose mode")

    args = parser.parse_args()
    dfilename = args.dfilename
    lfilename = args.lfilename
    verbose = args.verbose

    signal.signal(signal.SIGINT, signal_handler)

    if lfilename:
        dictname = lfilename

    if os.path.exists(dictname):
        if verbose:
            print 'Reading lexicon dictionary \'%s\' ...' % dictname,
        lex_dict = read_dict(dictname)
        if verbose:
            print 'done.'

    f = open(dfilename, 'rU')
    for line in f:
        parse_line(line, lex_dict)
    f.close

    if verbose:
        print 'Writing lexicon dictionary to \'%s\' ...' % dictname,
    write_dict(lex_dict, dictname)
    if verbose:
        print 'done.'

    if verbose:
        print "words processed:", nwords

if __name__ == '__main__':
    sys.exit(main())
