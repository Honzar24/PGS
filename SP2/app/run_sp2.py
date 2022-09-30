import getopt
import re
import sys
import xml.etree.cElementTree as ET
from datetime import datetime

# time stamp format
datetimeformatpattern = '%Y-%m-%d %H:%M:%S,%f'


# load file as list of lines with whitespaces striped
def loadfilelines(__filename):
    with open(__filename) as f:
        lines = [line.rstrip() for line in f]
    return lines


# create sublist of lines containing some text
def filterlines(__lines, __text):
    __ret = []
    for line in __lines:
        if __text in line:
            __ret.append(line)
    return __ret


# produce list of lines that contains given pattern filed with numbers form 1 to number of found elements is 0
def seperatenumbers(__lines, __pattern):
    __ret = []
    i = 1
    last = filterlines(__lines, __pattern.format(i))
    while len(last) > 0:
        __ret.append(last)
        i += 1
        last = filterlines(__lines, __pattern.format(i))
    return __ret


# sum values extracted with regex for given lines
def sumfromlines(__lines, __regex='.*(\\d+).*'):
    __sum = 0
    for test in __lines:
        __sum += int(re.search(__regex, test).group(1))
    return __sum


def main(__inputfilename, __outputfilename):
    print("Inputfile:", __inputfilename)
    print("Outputfile", __outputfilename)

    lines = loadfilelines(__inputfilename)
    workerlines = filterlines(lines, "r:Worker")
    listofworkerslines = seperatenumbers(workerlines, "Worker {} ")
    lorrylines = filterlines(lines, "r:Lorry")
    listoflorryslines = seperatenumbers(lorrylines, "Lorry {} ")

    controllines = filterlines(lines, "r:Chief")

    start = datetime.strptime(re.search('ts:(.*) r:', controllines[0]).group(1), datetimeformatpattern)
    end = datetime.strptime(re.search('ts:(.*) r:', controllines[1]).group(1), datetimeformatpattern)
    duration = (end - start)
    YZ = int(duration.days * 86_400_000 + duration.seconds * 1000 + duration.microseconds / 1000)
    print('Stimulation duration:', YZ, 'ms')
    Esimulation = ET.Element('Simulation', {'duration': str(YZ)})

    # block data
    blocklines = filterlines(lines, "Query block")
    AB = len(blocklines)
    CD = sumfromlines(blocklines, 'in (\\d+) ms') / AB
    print('number of blocks:', AB)
    print('blockAverageDuration:', CD, 'ms')
    ET.SubElement(Esimulation, 'blockAverageDuration', {'totalCount': str(AB)}).text = str(CD)

    # resource data
    resourcelines = filterlines(workerlines, "one resource ")
    EF = len(resourcelines)
    GH = sumfromlines(resourcelines, 'in (\\d+) ms') / EF
    print('number of resources:', EF)
    print('resourceAverageDuration:', GH, 'ms')
    ET.SubElement(Esimulation, 'resourceAverageDuration', {'totalCount': str(EF)}).text = str(GH)

    # ferry data
    ferrylines = filterlines(lines, "r:Ferry ")
    IJ = len(ferrylines)
    KL = sumfromlines(ferrylines, 'after (\\d+) ms') / IJ
    print('number of ferry trip:', IJ)
    print('ferryAverageWait:', KL, 'ms')
    ET.SubElement(Esimulation, 'ferryAverageWait', {'trips': str(IJ)}).text = str(KL)

    # workers data
    Eworkers = ET.SubElement(Esimulation, 'Workers')
    MN = 1
    for workerslines in listofworkerslines:
        workerresourcelines = filterlines(workerslines, "one resource ")
        OP = len(workerresourcelines)
        QR = sumfromlines(workerresourcelines, 'in (\\d+) ms')
        Eworker = ET.SubElement(Eworkers, 'Worker', {'id': str(MN)})
        ET.SubElement(Eworker, 'resources').text = str(OP)
        ET.SubElement(Eworker, 'workDuration').text = str(QR)
        MN += 1

    # lorryes data
    ELorryes = ET.SubElement(Esimulation, 'Vehicles')
    ST = 1
    for lorryslines in listoflorryslines:
        UV = sumfromlines(filterlines(lorryslines, 'loaded'), 'after (\\d+) ms')
        WX = sumfromlines(filterlines(lorryslines, 'travel time'), 'travel time (\\d+) ms') + KL
        Elorry = ET.SubElement(ELorryes, 'Vehicle', {'id': str(ST)})
        ET.SubElement(Elorry, 'loadTime').text = str(UV)
        ET.SubElement(Elorry, 'transportTime').text = str(WX)
        ST += 1

    # file output
    ET.ElementTree(Esimulation).write(__outputfilename)


def printhelp():
    print("Program arguments:")
    print("input file with log flag: -i filename or --input=filename")
    print("output file with xml format flag: -o filename or --output=filename")
    print("to print this help use flag: -h or --help")


if __name__ == '__main__':
    (flags, arguments) = getopt.getopt(sys.argv[1:], 'i:o:h', ['input=', 'output=', 'help'])

    inputfilename = ""
    outputfilename = ""

    # print(flags)
    for flag in flags:
        if flag.__contains__('--help'):
            printhelp()
            sys.exit()

        if flag.__contains__('-i'):
            inputfilename = flag[1]
        elif flag.__contains__('--input'):
            inputfilename = flag[1]

        if flag.__contains__('-o'):
            outputfilename = flag[1]
        elif flag.__contains__('--output'):
            outputfilename = flag[1]

    if inputfilename.__eq__("") or outputfilename.__eq__(""):
        print("Fill the input arguments to get program working.")
        printhelp()
        sys.exit()

    main(inputfilename, outputfilename)
