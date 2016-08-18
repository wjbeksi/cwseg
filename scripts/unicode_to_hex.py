#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Print the hexidecimal value of a Unicode character 
#
import sys

if len(sys.argv) != 2:
    print "Usage: unicode_to_hex char"
    sys.exit()

str = sys.argv[1]
utf16_str = str.decode('utf-8')
hex = ''.join(["%02x" % ord(c) for c in str])

print 'UTF-8:  0x%s' % hex
print 'UTF-16: 0x%x' % ord(utf16_str)
