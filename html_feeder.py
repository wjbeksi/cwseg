#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HTML feeder for lexicon building.  Given a top level directory of HTML files 
this program will recurse down each directory feeding HTML files to the lexicon 
builder.  Note that the lexicon building program (segmenter.py) must be in the 
same directory as this script.
"""
import os
import sys
import signal
import smtplib
import argparse
import datetime
from os.path import join, getsize
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.Utils import COMMASPACE, formatdate
from segmenter import build_lexicon, read_dict, write_dict

def signal_handler(signal, frame):
    sys.exit(0)

def escape_chars(s):
    special_chars = '()$\'' 
    for c in special_chars:
        s = s.replace(c, '\\' + c)
    return s 

def send_mail(nfiles, nbytes, send_to):
    """Send an email notification to a list of recipients"""
    server = 'mail.cs.umn.edu'

    msg = MIMEMultipart()
    msg['From'] = send_from = 'html_feeder@cs.umn.edu'
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = 'HTML feeder'

    now = datetime.datetime.now()
    text = ('HTML feeder run finished on %s.\n\nNumber of files processed: %s\nNumber of bytes processed: %s'
           % (now.strftime('%Y-%m-%d at %H:%M'), nfiles, nbytes))

    msg.attach(MIMEText(text))
    smtp = smtplib.SMTP(server)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()

def main():
    lex_dict = {}
    dictname = 'lex_dict.p'

    parser = argparse.ArgumentParser(description='HTML feeder for lexicon building')
    parser.add_argument('-d', '--directory', action='store', dest='dirpath',
                        help="top level directory containing HTML files")
    parser.add_argument('-e', '--email', action="append", dest="emaillist",
                         help="send an notification to a user, e.g. \
                         'username@cs.umn.edu'")
    parser.add_argument('-f', '--file', action='store', dest='filepath',
                        help="parse an HTML file list")
    parser.add_argument('-m', '--maxlen', action='store', dest='maxlen',
                        type=int, default=2,
                        help="maximum word length parsed (default: 2)")
    parser.add_argument('-l', '--lexdict', action='store', dest='lfilename',
                        help="lexicon dictionary file")
    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose',
                        help="enable verbose mode")

    args = parser.parse_args()
    dirpath = args.dirpath
    filepath = args.filepath
    maxlen = args.maxlen
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

    nbytes = nfiles = 0
    if filepath:
        f1 = open(filepath, 'rU')
        list = f1.readlines()
        for file in list:
            file = file.rstrip()
            size = getsize(file)
            nbytes += size
            if verbose:
                print "processing", file, "of size", size, "bytes"
            #file = escape_chars(file)
            if file.endswith('.html') or file.endswith('.htm'):
                build_lexicon(file, lex_dict, maxlen, 0)
                nfiles += 1
        f1.close()
    elif dirpath:
        if os.path.exists(dirpath):
            for root, dirs, files in os.walk(dirpath):
                for name in files:
                    if name.endswith('.html') or name.endswith('.htm'):
                        size = getsize(join(root, name))
                        nbytes += size
                        nfiles += 1
                        fname = join(root, name)
                        if verbose:
                            print "processing", fname, "of size", size, "bytes"
                        #fname = escape_chars(fname)
                        build_lexicon(fname, lex_dict, maxlen, 0)

    if filepath or dirpath:
        if verbose:
            print 'Writing lexicon dictionary to \'%s\' ...' % dictname,
        write_dict(lex_dict, dictname)
        if verbose:
            print 'done.'

    if verbose and nfiles > 0:
        print "files processed:", nfiles
        print "bytes processed:", nbytes

    if args.emaillist is not None:
        if args.verbose:
            print 'Sending email notification ...',
        send_mail(nfiles, nbytes, args.emaillist)
        if args.verbose:
            print 'done.'

if __name__ == '__main__':
    sys.exit(main())
