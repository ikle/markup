#!/usr/bin/env python3
# coding: utf-8

import markup

tests = """foreword

#  section text
*  list item test string
   indented line
+  some other test string
yet another line
12. enumeration test
    long
    enum item
13. bla-bla
17. ooops!
15. beep, beep, beep!
    call a planet!

    no response...
      Wake up, Neo!
[tag] tagged line
with continuation

## sample subsection
 with continuation

just another
paragraph text

and second one

 and just indented
 paragraph


 beep
"""

for i in markup.parse (tests.split ('\n')):
	print (i)
