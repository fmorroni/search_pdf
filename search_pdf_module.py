import pdftotext
import PyPDF2
import re
import sys
from termcolor import colored
import textwrap


def main():
    commands, filePaths = separateCommandsFromArgv(sys.argv)

    # The first element is the name of the python script, I don't need it.
    filePaths.pop(0)
    searchTerm = filePaths.pop(-1)

    if len(filePaths) > 0 and len(searchTerm) > 0:
        searchTermRe = parseCommands(commands, searchTerm)

    else:
        raise AttributeError(textwrap.dedent("""\
            Usage: search_pdf path/to/file1.pdf ... path/to/fileN.pdf [-option1option2...optionN] searchTerm
            Options:
                -r: regex search
                -i: case insensitive
                -w: ignore tildes
            Options can be combined or ignored."""))

    return filePaths, commands, searchTerm, searchTermRe
    # print(colored('From annotations', attrs=['underline', 'bold']) + ':', end='\n\n')
    # search_pdf_annots(filePaths, commands, searchTerm, searchTermRe, contextLength=-1)
    # print(colored('-'*60, 'blue', attrs=['bold']), end='\n\n')
    # print(colored('From text', attrs=['underline', 'bold']) + ':', end='\n\n')
    # search_pdf_text(filePaths, commands, searchTerm, searchTermRe, contextLength=50)


def separateCommandsFromArgv(argv):
    commands = []
    otherArgs = []
    stopConsideringCommands = False
    for arg in argv:
        if arg == '--':
            stopConsideringCommands = True
            continue

        if re.match(r'^-\w+', arg) and not stopConsideringCommands:
            commands.extend([comm for comm in arg if comm.isalpha()])
        else:
            otherArgs.append(arg)

    return (commands, otherArgs)


def ignoreTildes(str):
    tildePairs = [('a', 'á'), ('e', 'é'), ('i', 'í'), ('o', 'ó'), ('u', 'ú'),
                  ('A', 'Á'), ('E', 'É'), ('I', 'Í'), ('O', 'Ó'), ('U', 'Ú')]
    findTildePair = lambda letter: f"[{''.join(next((pair for pair in tildePairs if letter.group(0) in pair), ''))}]"
    return re.sub(r'[aeiouáéíóú]', findTildePair, str, flags=re.IGNORECASE)


def commandsToReFlags(commands):
    flags = 0
    if 'i' in commands:
        flags |= re.IGNORECASE
    # if 'otherFlagBasedCommand' in commands:
    #     flags |= re.OtherFlag

    return flags


def parseCommands(commands, searchTerm):
    reFlags = commandsToReFlags(commands)
    if 'r' not in commands:
        searchTerm = re.escape(searchTerm)
    else:
        # Make all groups into non-capturing groups because they are annoying for the split part of the program and I don't need them.
        searchTerm = re.sub(r'(?<!\\)\((?![?])', '(?:', searchTerm)

    if 'w' in commands:
        searchTerm = ignoreTildes(searchTerm)

    # Put searchTerm in a capturing group for use in the split.
    return re.compile(f'({searchTerm})', reFlags)


def printMatchMessage(pageNumber, path, commands, searchTerm, annotType=None):
    print(colored(f'In page {pageNumber + 1} of file "{path}", -{"".join(commands)} match for "', 'yellow', 'on_grey'), end='')
    print(colored(searchTerm, 'green', 'on_grey'), end='')
    print(colored('"', 'yellow', 'on_grey'), end='')
    if annotType != None:
        print(colored(f'in {annotType}', 'yellow', 'on_grey'), end='')
    print()


def printMatches(text, searchTermRe, contextLength=30):
    # contextLenght defines how much context should be printed before and after the match.
    # If contextLengt < 0 it prints the whole text.

    # With split I will get the matches for searchTerm and the rest of the text as elements in a list.
    matchSplit = searchTermRe.split(text)
    separator = '   [...]   '
    for index, ele in enumerate(matchSplit):
        if contextLength > 0:
            if index%2 != 0:
                # Matches will be in the odd elements of the list.
                print(colored(ele, 'green', attrs=['underline', 'bold']), end='')
            elif index == 0:
                if len(ele) > contextLength:
                    print(separator.lstrip(), end='')
                print(ele[-contextLength:].lstrip(), end='')
            else:
                if index < len(matchSplit) - 1:
                    if len(ele) > 2*contextLength:
                        print(ele[:contextLength].rstrip(), ele[-contextLength:].lstrip(), sep=separator, end='')
                        # print(ele[:contextLength].rstrip(), end=rightSeparator)
                        # print()
                        # print(leftSeparator, end=ele[-contextLength:].lstrip())
                    else:
                        print(ele, end='')
                else:
                    print(ele[:contextLength].rstrip(), end='')
                    print(separator.rstrip())
        else:
            # Matches will be in the odd elements of the list.
            if index%2 != 0:
                print(colored(ele, 'green', attrs=['underline', 'bold']), end='')
            else:
                print(ele, end='')
    print('\n')


def printNoMatchesFound(path, searchTerm):
    print(colored('No matches found for "', 'magenta', 'on_grey'), end='')
    print(colored(searchTerm, 'green', 'on_grey'), end='')
    print(colored('" in file:', 'magenta', 'on_grey'), end='')
    print(colored(f'"{path}"', "red", "on_grey"))