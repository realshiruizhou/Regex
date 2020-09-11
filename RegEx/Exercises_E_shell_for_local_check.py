import sys, re

file = open("wordsC.txt")
dic = ''.join(file.readlines())

#Example 1: find words ending with bt
pattern = "^(?!(.)+.*\1).{10,}"  #
print(re.findall(pattern, dic, re.MULTILINE))

# #Example 2: find the longest word
# pattern = ".{23,}" #
# print(re.findall(pattern, dic, re.MULTILINE))
#
# #Example 3: Find the longest word where no vowel appears more than twice.
# pattern = r'^(?!.*([aeiou])(\w*\1){2})\w{19,}'
# regex = re.compile(pattern, re.M)
# re_list = [dic[m.start():m.end()] for m in regex.finditer(dic)]
# print(re_list)

