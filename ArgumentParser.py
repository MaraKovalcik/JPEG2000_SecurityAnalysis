#usr/bin/python3

#
#   Author: Marek Kovalčík, xkoval14@stud.fit.vutbr.cz
#   Bachelor thesis - Error Resilience Analysis for JPEG 2000
#   2019
#

import sys
import re
import argparse

# Print help function
def printHelp():
    '''printing help'''
    print("""usage: python3 Analyzator2.py [--help | --directory DIR [ --library LIB ] ]
                            Error Resilience Analysis for JPEG 2000 programs optional arguments:
                            --help                  show this help message and exit
                            --directory DIR         DIR is directory with datasets
                            --library LIB           LIB can be 'kakadu' or 'openjpeg' (default lib is kakadu)""")

# return codes
class errorCodes:
    '''class with return codes'''
    OK = 0
    ARGS = 10
    DIR = 11


# Check program arguments
class ArgumentParser(argparse.ArgumentParser):
    '''class for check valid program arguments'''

    def error(self, message):
        self.print_help(sys.stderr)
        self.exit(errorCodes.ARGS)

    def checkArguments(args):
        '''function to check arguments'''

        print(args)

        if(len(args) == 2 and args[1] == "--help"):
            printHelp()
            exit(errorCodes.OK)

        elif(len(args) == 3 and args[1] == "--directory"):
                return args[2], None

        elif (len(args) == 5 and args[1] == "--directory" and args[3] == "--library"):
            return args[2], args[4]

        elif(len(args) == 2):
            sourceWithEqual = re.search("^--directory=", args[1])
            if sourceWithEqual:
                filename = str(args[1]).split("=", 1)
                return filename[1], None

        elif (len(args) == 5):

            filename, library = '', ''

            sourceWithEqual = re.search("^--directory=", args[1])
            if sourceWithEqual:
                filename = str(args[1]).split("=", 1)

            libWithEqual = re.search("^--library=", args[3])
            if libWithEqual:
                library = str(args[1]).split("=", 1)

            return filename[1], library[1]

        printHelp()
        exit(errorCodes.ARGS)