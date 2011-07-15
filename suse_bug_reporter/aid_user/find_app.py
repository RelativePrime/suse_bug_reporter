#!/usr/bin/env python

from subprocess import Popen, PIPE


def find_app():
    ''' returns a string that represents the name of the application
        clicked by the user '''

    print "Please click on the window of which you want to find the app name."

    output = Popen(('xprop', 'WM_CLASS'), stdout=PIPE).communicate()[0]
    output = output.split()
    output = output[3].lower()
    output = output.replace('"', '')

    return "The app's name is " + output + "."


if __name__ == '__main__':
    print find_app()