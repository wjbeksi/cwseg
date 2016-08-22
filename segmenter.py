#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
Chinese word segmenter and lexicon builder
================================================================================

This program runs in two modes: lexicon builder and word segmenter.  A 
significant lexicon needs to be built in order to do any meaningful word 
segmentation.  The lexicon building mode works by employing an HTML parser.  
Chinese words parsed from webpages are stored in a serialized dictionary.  This 
dictionary is persistent and is read in upon startup.  Words are stored along 
with their frequencies in the dictionary.  Support is included for pruning the 
dictionary of words that fall below a given threshold.  The word segmenter uses 
the dictionary along with a maximum matching algorithm in order to determine 
word boundaries.

Character sets:
    UTF-8 (supported)
    BIG5  (TBD)
    GB    (TBD)

Copyright 2012 William J. Beksi <beksi@cs.umn.edu>

This program is free software: you can redistribute it and/or modify it under 
the terms of the GNU Lesser General Public License as published by the Free 
Software Foundation, either version 3 of the License, or (at your option) any 
later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY 
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A 
PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along 
with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import re
import sys
import codecs
import signal
import os.path
import argparse
import cPickle as pickle
from HTMLParser import HTMLParser

def read_dict(filename):
    """Load the lexicon dictionary"""
    return pickle.load(open(filename, 'rb'))

def write_dict(lex_dict, filename):
    """Write the lexicon dictionary to disk"""
    pickle.dump(lex_dict, open(filename, 'wb'))

def dump_dict(filename):
    """Dump the lexicon dictionary"""
    lex_dict = read_dict(filename)
    for key, value in lex_dict.iteritems():
        print >>sys.stderr, key, value 

def info_dict(filename):
    """Show lexicon dictionary statistical information"""
    lex_dict = read_dict(filename)
    nwords = l1words = l2words = l3words = l4words = 0
    max_len = 0
    word = ''
    for key, value in lex_dict.iteritems():
        nwords += 1
        if len(key) == 1:
            l1words += 1
        elif len(key) == 2:
            l2words += 1
        elif len(key) == 3:
            l3words += 1
        elif len(key) == 4:
            l4words += 1
        if len(key) > max_len:
            max_len = len(key)
            word = key 
    print 'Total words:', nwords
    if l1words > 0:
        print '1 character words:', l1words,
        print ', % of dictionary:', format(float(l1words)/float(nwords)*100, '.2f')
    if l2words > 0:
        print '2 character words:', l2words, 
        print ', % of dictionary:', format(float(l2words)/float(nwords)*100, '.2f')
    if l3words > 0:
        print '3 character words:', l3words, 
        print ', % of dictionary:', format(float(l3words)/float(nwords)*100, '.2f')
    if l4words > 0:
        print '4 character words:', l4words, 
        print ', % of dictionary:', format(float(l4words)/float(nwords)*100, '.2f')
    print 'Longest word length:', max_len
    print 'Longest word:', word 

def prune_dict(t, filename, verbose):
    """Prune the lexicon dictionary of characters with frequency less than or 
       equal to the threshold t"""
    lex_dict = read_dict(filename)
    for char in lex_dict.keys():
        freq = lex_dict[char]['freq']
        if freq <= t:
            if verbose:
                print 'Removing %s from the dictionary' % char
            del lex_dict[char]
    write_dict(lex_dict, filename)

def is_chinese(c):
    """Check the Unicode character value"""
    v = ord(c)
    if ((v >= 0x4e00  and v <= 0x9fff) or  # common
        (v >= 0x3400  and v <= 0x4dff) or  # rare 
        (v >= 0x20000 and v <= 0x2a6df)):  # rare, historic 
        return 1
    return 0

def is_chinese_string(s):
    i = j = 0
    slen = len(s)
    while (i < slen):
        if is_chinese(s[i]):
            j += 1
        i += 1
    if j == slen:
        return 1;
    return 0

def is_latin(c):
    v = ord(c)
    if ((v >= 0x0000 and v <= 0x00ff) or 
       (v >= 0xff00 and v <= 0xffef)):  # full width Latin 
        return 1
    return 0

def is_number(c):
    v = ord(c)
    if (v == 0x25cb or  # ○
        v == 0x4e00 or  # 一
        v == 0x4e8c or  # 二
        v == 0x4e09 or  # 三
        v == 0x56db or  # 四
        v == 0x4e94 or  # 五
        v == 0x516d or  # 六
        v == 0x4e03 or  # 七
        v == 0x516b or  # 八
        v == 0x4e45 or  # 久
        v == 0x5341 or  # 十
        v == 0x5eff or  # 廿
        v == 0x5345 or  # 卅 
        v == 0x767e or  # 百
        v == 0x5343 or  # 千
        v == 0x842c or  # 萬 
        v == 0x4e07):   # 万 
        return 1
    return 0

def is_circle(c):
    v = ord(c)
    if v == 0x25cb:
        return 1
    return 0

def is_space(c):
    v = ord(c)
    if v == 0x0020 or v == 0x3000:  
        return 1
    return 0

def is_percent(c):
    v = ord(c)
    if v == 0x0025 or v == 0xff05:  
        return 1
    return 0

def is_stop(c):
    v = ord(c)
    if v == 0xff0e:  
        return 1
    return 0

def is_paren(c):
    v = ord(c)
    if v == 0xff08 or v == 0xff09:  # full width paren 
        return 1
    return 0

def is_lparen(c):
    v = ord(c)
    if v == 0xff08:  # full width paren 
        return 1
    return 0

def is_rparen(c):
    v = ord(c)
    if v == 0xff09:  # full width paren 
        return 1
    return 0

def is_lquote(c):
    v = ord(c)
    if v == 0x201c:
        return 1
    return 0

def is_rquote(c):
    v = ord(c)
    if v == 0x201d:
        return 1
    return 0

def is_comma(c):
    v = ord(c)
    if v == 0xff0c:  # full width comma
        return 1
    return 0

def is_vline(c):
    v = ord(c)
    if v == 0x7c:  # vertical line 
        return 1
    return 0

def is_colon(c):
    v = ord(c)
    # 0xff1a --> full width colon
    if v == 0x02d0 or v == 0xff1a:  
        return 1
    return 0

def add_word(word, is_dict, lex_dict):
    """Add a word to the lexicon dictionary or update the frequency"""
    if word not in lex_dict:
        if is_dict:
            lex_dict[word] = {'freq' : 0, 'dict' : 1}
        else:
            lex_dict[word] = {'freq' : 1, 'dict' : 0}
    else:
        if not is_dict:
            lex_dict[word]['freq'] += 1

def parse_chinese(data, lex_dict, maxlen, verbose):
    """Search for Chinese words based on string length, punctuation, and language"""
    d = data.decode('utf-8', errors='ignore')
    l = len(d) 
    word = ''

    for c in d:
        if is_chinese(c):
            word += c
        else:
            if len(word) > 0 and len(word) <= maxlen:
                if verbose:
                    print 'Adding word:', word 
                add_word(word, 0, lex_dict)
                word = ''
    if len(word) > 0 and len(word) <= maxlen:
        if verbose:
            print 'Adding word:', word 
        add_word(word, 0, lex_dict)

class parse_html(HTMLParser):
    def __init__(self, lex_dict, maxlen, verbose):
        self.lex_dict = lex_dict
        self.maxlen = maxlen
        self.verbose = verbose 
        HTMLParser.__init__(self) 
    #def handle_starttag(self, tag, attrs):
    #    print "Encountered a start tag:", tag
    #def handle_endtag(self, tag):
    #    print "Encountered an end tag:", tag
    def handle_data(self, data):
        parse_chinese(data, self.lex_dict, self.maxlen, self.verbose)

def build_lexicon(filename, lex_dict, maxlen, verbose):
    """Parse the input file for Chinese characters and save them to a 
       dictionary"""
    parser = parse_html(lex_dict, maxlen, verbose)
    charset_regexp = '\s+charset=(utf-8)'

    f = open(filename, 'rU')
    text = f.read()

    # Make sure we have UTF-8
    #charset_match = re.search(charset_regexp, text, re.IGNORECASE)
    #if not charset_match:
    #    sys.stderr.write('Character set not supported\n')
    #    sys.exit(1)

    #E4 B8 AD
    #unicode(u'中')
    #d = u'中' 
    #parser.feed(text)
    try:
        parser.feed(text)
    except UnicodeDecodeError:
        f.close()
        return 
    f.close()

def in_dict(word, freq_threshold, lex_dict):
    if word in lex_dict:
        if lex_dict[word]['dict']:
            return 1
        elif lex_dict[word]['freq'] > freq_threshold:
            return 1
    return 0

def maximum_match(line, space, freq_threshold, lex_dict):
    """Given a line of text, segment based on the longest length word found in 
       the dictionary"""
    input = line.decode('utf-8')
    input_len = len(input) 
    output = ''
    word = ''
    prev_c = ''

    # No space between numbers, decimal point
    # No space between year/month character following numbers
    i = 0
    j = input_len 
    while i < input_len:
        if is_chinese(input[i]): 
            if len(prev_c) and is_stop(prev_c):
                output = output.rstrip()
                prev_c = ''

            if len(prev_c) and (is_number(prev_c) and is_number(input[i])):
                output = output.rstrip()
                word += input[i]
            else:
                # Find the longest match starting from the end
                j = input_len
                while j > i:
                    k = i
                    word = ''
                    while k < j:
                        word += input[k]
                        k += 1
                    if in_dict(word, freq_threshold, lex_dict):
                        break
                    elif word in lex_dict and lex_dict[word]['freq'] > 10:
                        if len(word) == 2:
                            if ((lex_dict[word[0]]['dict'] and lex_dict[word[1]]['dict']) and
                                (lex_dict[word[0]]['freq'] > lex_dict[word]['freq']) and
                                (lex_dict[word[1]]['freq'] > lex_dict[word]['freq'])):
                                continue
                        else:
                            break

                    j -= 1
            output += word + space 
            i += len(word) 
            prev_c = word[-1]
            word = ''
        else:
            if is_latin(input[i]):
                prev_c = ''
                while i < input_len and is_latin(input[i]):
                    if is_stop(input[i]) and len(prev_c) == 0:
                        output = output.rstrip()
                        word += input[i]
                    elif len(prev_c) and (is_percent(prev_c) or is_paren(prev_c) or is_paren(input[i])):
                        word += space + input[i]
                    elif is_stop(input[i]):
                        word += space + input[i]
                    elif is_comma(input[i]):
                        word += space + input[i]
                    elif is_percent(input[i]):
                        output += word
                        word = ''
                        output = output.rstrip()
                        word = input[i]
                    else:
                        word += input[i]
                    prev_c = input[i]
                    i += 1
                output += word + space 
                word = ''
            else:
                if is_circle(input[i]):
                    output = output.rstrip()
                output += input[i] + space 
                i += 1
    if len(word):
        output += word
    output = output.rstrip()
    print >>sys.stderr, output 

def simple_maximum_match(line, space, freq_threshold, lex_dict):
    """Given a line of text, segment based on the longest length word found in 
       the dictionary"""
    input = line.decode('utf-8')
    input_len = len(input) 
    output = ''
    word = ''
    prev_c = ''

    # No space between numbers, decimal point
    # No space between year/month char following numbers
    i = 0
    j = input_len 
    while i < input_len:
        if is_chinese(input[i]): 
            # Find the longest match starting from the end
            j = input_len
            while j > i:
                k = i
                word = ''
                while k < j:
                    word += input[k]
                    k += 1
                if in_dict(word, freq_threshold, lex_dict):
                    break
                j -= 1
            output += word + space 
            i += len(word) 
            prev_c = word[-1]
            word = ''
        else:
            if is_latin(input[i]):
                prev_c = ''
                while i < input_len and is_latin(input[i]):
                    word += input[i]
                    prev_c = input[i]
                    i += 1
                output += word + space 
                word = ''
            else:
                output += input[i] + space 
                i += 1
    if len(word):
        output += word
    output = output.rstrip()
    print >>sys.stderr, output 

def word_segmenter(filename, space, freq_threshold, lex_dict, verbose):
    """Segment the text by using maximum matching"""
    f = open(filename, 'rU')
    text = f.readlines()

    for line in text:
        maximum_match(line, space, freq_threshold, lex_dict)
        #simple_maximum_match(line, space, freq_threshold, lex_dict)

    f.close()

def signal_handler(signal, frame):
    sys.exit(0)

def main():
    lex_dict = {}
    dictname = 'lex_dict.p'

    parser = argparse.ArgumentParser(description='Chinese word segmenter and lexicon builder')
    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', 
                        help="enable verbose mode")
    parser.add_argument('-f', '--freq', action='store', dest='freq_threshold',
                        type=int, default=1,
                        help="minimum dictionary word frequency threshold \
                        (default: 1)")
    parser.add_argument('-s', '--segment', action='store', dest='sfilename', 
                        help="word segment a file")
    parser.add_argument('-p', '--parse', action='store', dest='pfilename', 
                        help="parse an HTML file")
    parser.add_argument('-r', '--record', action='store_true', dest='record', 
                        help="record parsed words to dictionary")
    parser.add_argument('-m', '--maxlen', action='store', dest='maxlen', 
                        type=int, default=4,
                        help="maximum word length parsed (default: 2)")
    parser.add_argument('-d', '--dump', action='store_true', dest='dump', 
                        help="dump lexicon dictionary")
    parser.add_argument('-i', '--info', action='store_true', dest='info', 
                        help="lexicon dictionary statistical information")
    parser.add_argument('-l', '--lexdict', action='store', dest='lfilename', 
                        help="lexicon dictionary file")
    parser.add_argument('-t', '--threshold', action='store', dest='threshold', 
                        type=int,
                        help="prune words from a lexicon dictionary that are \
                        below a frequency threshold")
    parser.add_argument('-w', '--width', action='store', dest='widthtype', 
                        type=int, default=1,
                        help="space character type, e.g. ASCII space (1), ASCII \
                        double space (2), ideographic space (3), default: 1")

    args = parser.parse_args()
    verbose = args.verbose
    pfilename = args.pfilename
    sfilename = args.sfilename
    lfilename = args.lfilename
    record = args.record
    maxlen = args.maxlen
    dump = args.dump
    info = args.info
    threshold = args.threshold
    widthtype = args.widthtype
    freq_threshold = args.freq_threshold

    sys.stderr = codecs.getwriter('utf8')(sys.stderr)
    signal.signal(signal.SIGINT, signal_handler)

    if lfilename:
        dictname = lfilename

    if record: 
        if os.path.exists(dictname):
            if verbose:
                print 'Reading lexicon dictionary \'%s\' ...' % dictname, 
            lex_dict = read_dict(dictname)
            if verbose:
                print 'done.'
    if pfilename:
        if verbose:
            print 'Building lexicon dictionary ...'
        build_lexicon(pfilename, lex_dict, maxlen, verbose)
        if record:
            if verbose:
                print 'Writing lexicon dictionary to \'%s\' ...' % dictname,
            write_dict(lex_dict, dictname)
            if verbose:
                print 'done.'
    elif sfilename:
        if widthtype == 3:
            space = u'\u3000'
        elif widthtype == 2:
            space = u'\u0020' + u'\u0020'
        else:    
            space = u'\u0020'
        if verbose:
            print 'Segmenting %s using dictionary \'%s\' ...' % (sfilename, dictname)
        lex_dict = read_dict(dictname)
        word_segmenter(sfilename, space, freq_threshold, lex_dict, verbose)
        if verbose:
            print 'Finished segmenting'
        
    if dump:
        if verbose:
            print 'Dumping lexicon dictionary ...'
        dump_dict(lfilename)
    if info:
        if verbose:
            print 'Showing lexicon dictionary stats ...'
        info_dict(lfilename)
    if threshold:
        if verbose:
            print 'Pruning lexicon dictionary ...'
        prune_dict(threshold, lfilename, verbose)

if __name__ == '__main__':
    sys.exit(main())
