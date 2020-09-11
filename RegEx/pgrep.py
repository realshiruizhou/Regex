import sys, re, os
usage = "Usage: rex.py fileName.txt /regexPattern/options"

# Parse input arguments
if len(sys.argv) < 3: exit(usage)
if not os.path.isfile(sys.argv[1]): exit("'{}' was not found.\n  {}".format(sys.argv[1], usage))
regex = sys.argv[2].strip()
match = re.search(r"^/(.*)/([ismISM]*)$", regex)
if not match: exit("'{}' does not appear to be a proper regular expression\n  {}".format(regex, usage))

# Read in the file to be searched
lines = open(sys.argv[1],'r').read().splitlines()
text  = "\n".join(lines)      # neutralizes platform dependent newline issues

# Parse the search spec (ie. the regular expression)
options = {"s":re.S, "i":re.I, "m":re.M}
opt = sum(options[ltr] for ltr in {*match.group(2).lower()})
pattern = match.group(1)
try:
  if opt: rec = re.compile(pattern, opt)
  else:   rec = re.compile(pattern)
except Exception as exc:
  exit("'{}' is not a valid RegEx\n  {}".format(pattern, usage))

# Apply the regular expression
startEndLst = [(m.start(), m.end()) for m in rec.finditer(text)]
if not startEndLst: exit("No matches found")

# Make a lookup dictionary to identify idx to word number
basePos, idxToLine = 0, {0: 0}
for lineNum, line in enumerate(lines):
  idxToLine[basePos] = lineNum
  basePos += 1 + len(line) 

def idxToWordAndPos(idx, idxToLine):
  # identify the line (or word) number given an index position into the text
  for x in range(idx,-1,-1):
    if x in idxToLine:
      return (idxToLine[x], idx-x)
  exit("Got an error in idxToWordAndPos with idx {}".format(idx))

# Translate index positions in (word number, offset) tuple
sePairs = [(idxToWordAndPos(p[0], idxToLine), idxToWordAndPos(p[1], idxToLine)) for p in startEndLst]   # start end pairs

# Then identify each word
bigSet = set()
for p in sePairs:
  bigSet |= {*range(p[0][0], p[1][0] + (p[1][1]!=0))}
bigList = sorted(bigSet)

# And now print them
for wordNum in bigList: print(lines[wordNum])
print ("\n{} matches in {} lines".format(len(startEndLst), len(bigList)))


# References
# https://stackoverflow.com/questions/48445616/why-printing-in-color-in-a-windows-terminal-in-python-does-not-work
# https://stackoverflow.com/questions/12492810/python-how-can-i-make-the-ansi-escape-codes-to-work-also-in-windows
# https://pypi.org/project/colorama/
