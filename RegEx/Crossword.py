import sys
import re
import random
s = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
BLOCKCHAR = '#'
OPENCHAR = '-'
PROTECTEDCHAR = '~'
xheight, xwidth, blockCt, dictSeen = 4, 4, 0, False
eng_freq = [.0817, .0149, .0278, .0425, .1270, .0223, .0202, .0609, .0697, .0015, .0077, .0403, .0241, .0675, .0751,
            .0193, .0010, .0599, .0633, .0906, .0276, .0098, .0236, .0015, .0197, .0007]
three = []
four = []
five = []
six = []
seven_or_more = []
words_length = {}


def illegal_final(xw):
    illegRE = r"#[-~][-~]?#"
    newH = len(xw) // (xwidth + 2)
    for turn in range(2):
        if re.search(illegRE, xw):
            return True
        xw = transpose(xw, len(xw) // newH)
        newH = len(xw) // newH
    return False


def illegal(xw):
    illegRE = r"[{}](.?[{}]|[{}].?)[{}]".format(BLOCKCHAR, PROTECTEDCHAR, PROTECTEDCHAR, BLOCKCHAR)
    newH = len(xw) // (xwidth + 2)
    for turn in range(2):
        if re.search(illegRE, xw):
            return True
        xw = transpose(xw, len(xw) // newH)
        newH = len(xw) // newH
    return False


def remove(xw):
    temp = ''
    for a in range(0, xheight):
        for b in range(0, xwidth):
            index = b + 1 + (a + 1) * (xwidth + 2)
            if xw[index] == PROTECTEDCHAR:
                temp = temp + OPENCHAR
            else:
                temp = temp + xw[index]
    return temp


def display(puzzle, width):
    count = 1
    for a in puzzle:
        if count % width == 0:
            print(a + " ")
        else:
            print(a + " ", end="", flush=True)
        count += 1


def transpose(xw, newWidth):
    return "".join([xw[col::newWidth] for col in range(0, newWidth)])


def fill(xw):
    substituteRegex = r"[{}]{}[{}]".format(BLOCKCHAR, OPENCHAR, BLOCKCHAR)
    subRE2 = r"[{}]{}{}[{}]".format(BLOCKCHAR, OPENCHAR, OPENCHAR, BLOCKCHAR)
    newH = len(xw) // (xwidth + 2)
    for counter in range(2):
        xw = re.sub(substituteRegex, BLOCKCHAR * 3, xw)
        xw = re.sub(subRE2, BLOCKCHAR * 4, xw)
        xw = transpose(xw, len(xw) // newH)
        newH = len(xw) // newH
    return xw


def protect(xw):
    substituteRegex = r"(?<=[{}]\w){}{}".format(BLOCKCHAR, OPENCHAR, OPENCHAR)
    subRE2 = r"(?<=[{}]\w\w){}".format(BLOCKCHAR, OPENCHAR)
    subRE3 = r"(?<=[{}]{}\w){}(?=[{}])".format(BLOCKCHAR, OPENCHAR, OPENCHAR, BLOCKCHAR)
    subRE4 = r"(?<=[{}]){}(?=\w{}[{}])".format(BLOCKCHAR, OPENCHAR, OPENCHAR, BLOCKCHAR)
    newH = len(xw) // (xwidth + 2)
    for counter in range(2):
        xw = re.sub(substituteRegex, PROTECTEDCHAR * 2, xw)
        xw = re.sub(subRE2, PROTECTEDCHAR, xw)
        xw = re.sub(subRE3, PROTECTEDCHAR, xw)
        xw = re.sub(subRE4, PROTECTEDCHAR, xw)
        xw = transpose(xw, len(xw) // newH)
        newH = len(xw) // newH
    return xw


def rotate(xw):
    temp = xw[::-1]
    for a in range(0, len(temp)):
        if temp[a] == xw[a]:
            continue
        if temp[a] == BLOCKCHAR:
            xw = xw[:a] + BLOCKCHAR + xw[a + 1:]
        elif temp[a].isalpha() and xw[a] == OPENCHAR:
            xw = xw[:a] + PROTECTEDCHAR + xw[a + 1:]
        elif temp[a] == PROTECTEDCHAR and xw[a] == OPENCHAR:
            xw = xw[:a] + PROTECTEDCHAR + xw[a + 1:]
    return xw


def replace_words(xw):
    for a in range(0, len(xw)):
        if xw[a].isalpha():
            xw = xw[:a] + PROTECTEDCHAR + xw[a + 1:]
    return xw


def connected(board, x, y):
    if x >= xwidth or y >= xheight or x < 0 or y < 0:
        return
    index = x + 1 + (xwidth + 2) * (y + 1)
    if board[index] == BLOCKCHAR or board[index] == "?":
        return
    board[index] = "?"
    connected(board, x + 1, y)
    connected(board, x - 1, y)
    connected(board, x, y + 1)
    connected(board, x, y - 1)


def available(xw):
    toReturn = set()
    for a in range(0, len(xw)):
        if xw[a] == OPENCHAR:
            toReturn.add(a)
    return toReturn


def available_fill(xw):
    toReturn = set()
    for a in range(0, len(xw)):
        if xw[a] == OPENCHAR or xw[a] == PROTECTEDCHAR:
            toReturn.add(a)
    return toReturn


def add_blocks(xw):
    num = blockCt + ((xwidth + 2) * 2 + 2 * xheight)
    xw = replace_words(xw)
    temp = xw
    while temp.count(BLOCKCHAR) < num:
        choose = random.choice(tuple(available(temp)))
        temp = temp[:choose] + BLOCKCHAR + temp[choose + 1:]
        temp = fill(temp)
        temp = rotate(temp)
        if temp.count(BLOCKCHAR) > num:
            temp = xw
            continue
        elif temp.count(BLOCKCHAR) == num:
            new_choice = random.choice(tuple(available_fill(temp)))
            x, y = new_choice % (xheight + 2) - 1, new_choice // (xheight + 2) - 1
            connected_test = list(temp)
            connected(connected_test, x, y)
            if PROTECTEDCHAR in connected_test or OPENCHAR in connected_test:
                temp = xw
                continue
            elif illegal_final(temp):
                temp = xw
    return temp


def most_constrained(xw):
    indexes = []
    for a in range(xwidth + 2, len(xw)):
        if (xw[a] == OPENCHAR or xw[a].isalpha) and xw[a - 1] == BLOCKCHAR:
            length = 1
            count = 1
            str = xw[a]
            constraints = 0
            if xw[a].isalpha():
                constraints += 1
            while xw[a + count] != BLOCKCHAR:
                if xw[a + count].isalpha():
                    constraints += 1
                length += 1
                str = str + xw[a + count]
            if constraints < length:
                indexes.append((constraints, "H", a, str, length))
    newH = len(xw) // (xwidth + 2)
    temp = transpose(xw, len(xw) // newH)
    for b in range(xheight + 2, len(temp)):
        if (temp[b] == OPENCHAR or temp[b].isalpha) and temp[b - 1] == BLOCKCHAR:
            length = 1
            count = 1
            str = temp[b]
            constraints = 0
            if temp[b].isalpha():
                constraints += 1
            while temp[b + count] != BLOCKCHAR:
                if temp[b + count].isalpha():
                    constraints += 1
                length += 1
                str = str + temp[b + count]
            if constraints < length:
                indexes.append((constraints, "V", b, str, length))
    return max(indexes)


# def bad_board(xw):
#     for a in range(xwidth + 2, len(xw) - (xwidth + 2)):
#         if xw[a] == BLOCKCHAR and xw[a + 1].isalpha():
#             count = 2
#             length = 1
#             str = xw[a + 1]
#             while xw[a + count] != BLOCKCHAR:
#                 length += 1
#                 str += xw[a + count]
#             if length < 7:
#                 if str not in words_length[length]:
#                     return False
#             else:
#                 if str not in seven_or_more:
#                     return False
#     temp = transpose(xw, xheight + 2)
#     for b in range(xheight + 2, len(temp) - (xheight + 2)):
#         if xw[b] == BLOCKCHAR and xw[b + 1].isalpha():
#             count = 2
#             length = 1
#             str = xw[b + 1]
#             while xw[b + count] != BLOCKCHAR:
#                 length += 1
#                 str += xw[b + count]
#             if length < 7:
#                 if str not in words_length[length]:
#                     return False
#             else:
#                 if str not in seven_or_more:
#                     return False
#     return True
#
#
# def addWords(xw):
#     if "-" not in xw:
#         if not bad_board(xw):
#             return xw
#         else:
#             return None
#     display(xw, xwidth + 2)
#     constraints, direction, start, word, length = most_constrained(xw)
#     new_string = xw
#     if direction == "H":
#         h_regex = r""
#         possible = []
#         for a in range(start, start + length):
#             if word[a].isalpha:
#                 h_regex = h_regex + word[a]
#             else:
#                 h_regex = h_regex + "."
#         if length < 7:
#             for string in words_length[length]:
#                 if len(string) == length and re.search(h_regex, string):
#                     possible.append(string)
#         else:
#             for string in seven_or_more:
#                 if re.search(h_regex, string):
#                     possible.append(string)
#         for b in possible:
#             for c in range(start, start + length):
#                 new_string = new_string[:c] + b[c - start] + new_string[c + 1:]
#             result = addWords(new_string)
#             if result is not None:
#                 return result
#             new_string = xw
#     else:
#         v_regex = r""
#         possible = []
#         for d in range(start, start + length * (xwidth + 2), xwidth + 2):
#             if word[d].isalpha:
#                 v_regex = v_regex + word[d]
#             else:
#                 v_regex = v_regex + "."
#         if length < 7:
#             for string in words_length[length]:
#                 if len(string) == length and re.search(v_regex, string):
#                     possible.append(string)
#         else:
#             for string in seven_or_more:
#                 if re.search(v_regex, string):
#                     possible.append(string)
#         for e in possible:
#             count = 0
#             for f in range(start, start + length * (xwidth + 2), xwidth + 2):
#                 new_string = new_string[:f] + e[count] + new_string[f + 1:]
#                 count += 1
#             result = addWords(new_string)
#             if result is not None:
#                 return result
#             new_string = xw
#     return None
def addWords(xw):
    for a in range(xwidth + 2, len(xw) - xwidth + 2):
        if xw[a] == BLOCKCHAR and (xw[a + 1] == PROTECTEDCHAR or xw[a + 1] == OPENCHAR):
            count = 2
            length = 1
            while xw[a + count] != BLOCKCHAR:
                length += 1
                count += 1
            if length < 7:
                word = random.choice(words_length[length])
            else:
                for c in range(0, len(seven_or_more)):
                    if len(seven_or_more[c]) == length:
                        word = seven_or_more[c]
                        break
            for b in range(0, length):
                xw = xw[0:a + b + 1] + word[b] + xw[a + b + 2:]
    return xw


def main():
    global xheight, xwidth, blockCt, dictSeen, three, four, five, six, seven_or_more, words_length
    intTest = [r"^(\d+)x(\d+)$", r"^\d+$", r"^(H|V)(\d+)x(\d+)(.+)$"]
    fixedWords = []
    args = sys.argv
    for arg in args:
        r = r".*txt"
        if re.match(r, arg):
            file = open(arg, 'r')
            for line in file:
                w = line.split()[0]
                if w.isalpha():
                    length = len(w)
                    if length == 3:
                        three.append(w)
                    elif length == 4:
                        four.append(w)
                    elif length == 5:
                        five.append(w)
                    elif length == 6:
                        six.append(w)
                    elif length >= 7:
                        seven_or_more.append(w)
            words_length = {3: three, 4: four, 5: five, 6: six}
            dictSeen = True
            continue
        for testNum, retest in enumerate(intTest):
            match = re.search(retest, arg, re.I)
            if not match:
                continue
            if testNum == 0:
                xheight, xwidth = int(match.group(1)), int(match.group(2))
            elif testNum == 1:
                blockCt = int(arg)
            else:
                vpos = int(match.group(2))
                hpos = int(match.group(3))
                word = match.group(4).upper()
                fixedWords.extend([arg[0].upper(), vpos, hpos, word])
    if not dictSeen:
        exit("whatever_..")
    if blockCt == xwidth * xheight:
        xword = BLOCKCHAR * xwidth * xwidth
        return xword
    else:
        xword = OPENCHAR * xwidth * xheight
    if xheight * xwidth % 2 == 1:
        middle_index = int(xwidth / 2) + (int(xheight / 2)) * xwidth
        if blockCt % 2 == 1:
            xword = xword[:middle_index] + BLOCKCHAR + xword[middle_index + 1:]
        else:
            xword = xword[:middle_index] + PROTECTEDCHAR + xword[middle_index + 1:]
    xw = BLOCKCHAR*(xwidth+3)
    xw += (BLOCKCHAR*2).join([xword[p:p+xwidth] for p in range(0, len(xword), xwidth)])
    xw += BLOCKCHAR*(xwidth+3)
    for b in range(0, int(len(fixedWords) / 4)):
        temp = fixedWords[b * 4: b * 4 + 4]
        direction, v, h, w = temp
        start_index = (v + 1) * (xwidth + 2) + h + 1
        xw = xw[:start_index] + w[0] + xw[start_index + 1:]
        if direction == "V":
            for c in range(1, len(w)):
                index = start_index + (xwidth + 2) * c
                xw = xw[:index] + w[c] + xw[index + 1:]
        else:
            for d in range(1, len(w)):
                index = start_index + d
                xw = xw[:index] + w[d] + xw[index + 1:]
    xw = fill(xw)
    xw = protect(xw)
    xw = rotate(xw)
    xw = add_blocks(xw)
    for b in range(0, int(len(fixedWords) / 4)):
        temp = fixedWords[b * 4: b * 4 + 4]
        direction, v, h, w = temp
        start_index = (v + 1) * (xwidth + 2) + h + 1
        xw = xw[:start_index] + w[0] + xw[start_index + 1:]
        if direction == "V":
            for c in range(1, len(w)):
                index = start_index + (xwidth + 2) * c
                xw = xw[:index] + w[c] + xw[index + 1:]
        else:
            for d in range(1, len(w)):
                index = start_index + d
                xw = xw[:index] + w[d] + xw[index + 1:]
    # display(xw, xwidth + 2)
    xw = addWords(xw)
    xw = remove(xw)
    # display(xw, xwidth)
    return xw


# main()
print(main())
# "4x4 0 wordlist.txt"
# "5x5 0 wordlist.txt V0x0Imbue"
# "7x7 11 wordlist.txt"
# "9x13 19 wordlist.txt V0x1Dog"
# "9x15 24 wordlist.txt V0x7con V6x7rum"
# "13x13 32 wordlist.txt V2x4# V1x9# V3x2# h8x2#moo# v5x5#two# h6x4#ten# v3x7#own# h4x6#orb# h0x5Easy"
# "15x15 42 wordlist.txt H0x0# V0x7### H3x3# H3x8# H3x13## H4x4# H4x10## H5x5# H5x9## H6x0### H6x6# H6x10# H7x0##"
# "15x15 42 wordlist.txt H0x0#MUFFIN#BRIOCHE V0x7## H3x3# H3x8# H3x13## H4x4# H4x10## H5x5# H5x9## H6x0### H6x6# H6x10# H7x0## H14x0BISCUIT#DANISH"
# "13x13 28 wordlist.txt"
