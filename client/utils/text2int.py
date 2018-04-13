#!/usr/bin/env python
# vim: sw=4 ai expandtab
# Utility funtion to convert written words to integers
# Shamelessly stolen from https://stackoverflow.com/questions/493174/is-there-a-way-to-convert-number-words-to-integers

units = [ "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
          "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
          "sixteen", "seventeen", "eighteen", "nineteen", ]

tens = [ "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety" ]

scales = [ "hundred", "thousand", "million", "billion", "trillion" ]

def text2int(textnum, numwords={}):
    if not numwords:

      numwords["and"] = (1, 0)
      for idx, word in enumerate(units):    numwords[word] = (1, idx)
      for idx, word in enumerate(tens):     numwords[word] = (1, (idx+2) * 10)
      for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0
    for word in textnum.lower().split():
        if word not in numwords:
          raise ValueError("Illegal word: " + word)

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current
