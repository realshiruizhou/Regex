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
possible = {}
matrix = []


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


def initial_list(xw):
    global possible, matrix
    board = []
    row = []
    for a in range(0, len(xw)):
        if a % xwidth == 0 and a != 0:
            matrix.append(row)
            row = []
        row.append(xw[a])
    matrix.append(row)
    words = []
    w = []
    for b in range(0, xheight):
        for c in range(0, xwidth):
            if matrix[b][c] == BLOCKCHAR and len(w) > 0:
                words.append(w)
                w = []
            elif matrix[b][c] == BLOCKCHAR:
                continue
            else:
                w.append((b, c))
        if len(w) > 0:
            words.append(w)
            w = []
    for d in range(0, xwidth):
        for e in range(0, xheight):
            if matrix[e][d] == BLOCKCHAR and len(w) > 0:
                words.append(w)
                w = []
            elif matrix[e][d] == BLOCKCHAR:
                continue
            else:
                w.append((e, d))
        if len(w) > 0:
            words.append(w)
            w = []
    for word in words:
        regex = ""
        string = ""
        for index in word:
            x, y = index
            string = string + matrix[x][y]
            if matrix[x][y].isalpha():
                regex = regex + matrix[x][y]
            else:
                regex = regex + "."
        possible_words = []
        if string in possible:
            possible_words = possible[string]
        elif OPENCHAR not in string:
            frequency = 0
            for c in string:
                frequency += eng_freq[ord(c.lower()) - 97]
            possible_words = [(frequency, string)]
            possible[string] = possible_words
        else:
            for thing in possible[len(string) * OPENCHAR]:
                freq, to_search = thing
                if re.search(regex, to_search):
                    possible_words.append(thing)
            possible[string] = possible_words
        whole = [len(possible_words), word, string, possible_words]
        board.append(whole)
    return board


# def update_list(changed, list):
#     chars = changed[1]
#     change = False
#     for a in list:
#         for b in range(0, len(a[1])):
#             if a[1][b] in chars:
#                 for c in range(0, len(chars)):
#                     if a[1][b] == chars[c]:
#                         updated = a[2][:b] + changed[2][c] + a[2][b + 1:]
#                         a[2] = updated
#                         change = True
#         if change:
#             regex = ""
#             new_possible = []
#             if a[2] in possible:
#                 new_possible = possible[a[2]]
#             else:
#                 for d in range(0, len(a[2])):
#                     if a[2][d].isalpha():
#                         regex = regex + a[2][d]
#                     else:
#                         regex = regex + "."
#                 for e in a[3]:
#                     freq, word = e
#                     if re.search(regex, word):
#                         new_possible.append(e)
#             a[0] = len(new_possible)
#             a[3] = new_possible
#     return list
#
#
# def add_words(list, completed):
#     if len(list) == 0:
#         return completed
#     next_word = min(list)
#     if next_word[0] == 0:
#         return None
#     while next_word[0] == 1:
#         completed.append(next_word)
#         list.remove(next_word)
#         if len(list) == 0:
#             return completed
#         next_word = min(list)
#     possible_words = next_word[3][:]
#     if len(possible_words) == 0:
#         return None
#     word = max(possible_words)
#     possible_words.remove(word)
#     next_word[3] = [word]
#     next_word[2] = word[1]
#     next_word[0] = 1
#     list = update_list(next_word, list)
#     result = add_words(list, completed)
#     while result is None:
#         if len(possible_words) == 0:
#             return None
#         word = max(possible_words)
#         possible_words.remove(word)
#         next_word[3] = [word]
#         next_word[2] = word[1]
#         next_word[0] = 1
#         list = update_list(next_word, list)
#         result = add_words(list, completed)
#     return result


def to_string(list):
    global matrix
    to_return = ""
    for a in list:
        chars = a[1]
        string = a[2]
        count = 0
        for b in chars:
            x, y = b
            matrix[x][y] = string[count]
            count += 1
    for c in matrix:
        for d in range(0, len(c)):
            to_return = to_return + c[d]
    return to_return


def temp_50(list):
    for a in list:
        if a[0] == 1:
            continue
        print(a)
        print(a[3])
        a[2] = random.choice(a[3])[1]
    return list


def main():
    global xheight, xwidth, blockCt, dictSeen, possible
    intTest = [r"^(\d+)x(\d+)$", r"^\d+$", r"^(H|V)(\d+)x(\d+)(.+)$"]
    fixedWords = []
    args = sys.argv
    for arg in args:
        r = r".*txt"
        if re.match(r, arg):
            file = open(arg, 'r')
            for line in file:
                w = line.split()[0]
                if not w.isalpha():
                    continue
                key = OPENCHAR * len(w)
                frequency = 0
                for c in w:
                    frequency += eng_freq[ord(c.lower()) - 97]
                if key in possible:
                    possible[key].append((frequency, w))
                else:
                    possible[key] = [(frequency, w)]
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
    xw = remove(xw)
    list_representation = initial_list(xw)
    # list_representation = add_words(list_representation, [])
    print(list_representation)
    list_representation = temp_50(list_representation)
    xw = to_string(list_representation)
    display(xw, xwidth)
    return xw


# main()
print(main())
# python test.py 4x4 0 wordlist.txt
# "5x5 0 wordlist.txt V0x0Imbue"
# "7x7 11 wordlist.txt"
# "9x13 19 wordlist.txt V0x1Dog"
# "9x15 24 wordlist.txt V0x7con V6x7rum"
# "13x13 32 wordlist.txt V2x4# V1x9# V3x2# h8x2#moo# v5x5#two# h6x4#ten# v3x7#own# h4x6#orb# h0x5Easy"
# "15x15 42 wordlist.txt H0x0# V0x7### H3x3# H3x8# H3x13## H4x4# H4x10## H5x5# H5x9## H6x0### H6x6# H6x10# H7x0##"
# "15x15 42 wordlist.txt H0x0#MUFFIN#BRIOCHE V0x7## H3x3# H3x8# H3x13## H4x4# H4x10## H5x5# H5x9## H6x0### H6x6# H6x10# H7x0## H14x0BISCUIT#DANISH"
# "13x13 28 wordlist.txt"
