#!/usr/bin/env python
#
# Print a random count of URIs from a given file.
#
import sys
import random

if len(sys.argv) != 3:
    print "Usage: pick_random count filename"
    sys.exit()

urls = []
count = int(sys.argv[1])
f = open(sys.argv[2], 'r')
for line in f:
    urls.append(line)

random.seed()
i = 0
while i < count:
    random_num = random.randrange(len(urls))
    print urls[random_num],
    i += 1
