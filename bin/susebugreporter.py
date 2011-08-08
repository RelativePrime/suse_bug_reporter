#!/usr/bin/env python

import sys
import argparse
import re
import pprint
import osc.conf

# name of the main package
pkg = 'suse_bug_reporter'

# name of the util package
u_pkg = 'util'

# name of the aid user package
a_pkg = 'aid_user'

# relevance threshold for similar bug search
rel_threshold = 0.75

# custom imports
import bugzilla
from suse_bug_reporter.util.console import print_list, yes_no, get_index, choice, pager, custom_input
from suse_bug_reporter.util import packageInfo, gather
from suse_bug_reporter.util.sortByKeywords import sortByKeywords
from suse_bug_reporter.util.bugReport import BugReport
from suse_bug_reporter.aid_user import find_app, find_package
from suse_bug_reporter.util.initBz import initBugzilla


def do_find_app(args=None):
    ans = find_app.find_app()
    if ans is None:
        print 'Nothing found.'
        return
    print ans[0]
    
    
def do_find_pkg(args=None):
    ans = find_package.find_package()
    if ans is None:
        print 'Nothing found.'
        return
    print ans[0]


def do_aid(args=None):

    msg = 'What module do you want to use?'
    AID_LIST = (
            "Find app - click on a window to find the application's name.",
            "Find package - enter an executable's name to find its package."
           )
    funcs = {
        0 : find_app.find_app,
        1 : find_package.find_package
    }

    print_list(AID_LIST, msg='Available modules:')
    idx = get_index(len(AID_LIST), msg='Which one?')

    ans = funcs.get(idx)()
    if ans is None:
        print 'Nothing found.'
    else:
        print ans[0]

    return ans[1]

    
def do_gather(args=None):

    print 'Gathering relevant system information...'

    data = gather.gather_data(gather.gather_from)

    pprint.pprint(data)


def do_submit(args=None, pkg=None):

    print "Welcome to the submit bug report module!"
    print ''

    # init osc
    try:
        osc.conf.get_config()
    except osc.oscerr.NoConfigfile:
        print 'You have to have a valid .oscrc file. Please do so by running osc.'
        sys.exit(1)

    # init bugzilla
    bz = initBugzilla()

    print ''
    print "If you don't know which package you want to file a bug to, you can"\
            " use the susebugreport aid command to get some help."

    print "Which is the package you want to file a report against?"
    print "If you are not sure, you can just type the beginning of the name and"\
            " use a '*' to invoke globbing."
    print "Also, you can type '?' to start the aid_user module that helps "\
            "finding the correct package name."
    
    print ''

    if pkg != None:
        name = pkg
    else:
        name = raw_input("Package name (or '?'): ")
    while '?' in name:
        ans = do_aid()
        name = custom_input("Package name (or '?'): ", ans)
    if name.strip() == '':
        print 'Package name cannot be blank!'
        sys.exit(1)
    if name == '*':
        print 'Invalid package name!'
        sys.exit(1)
    pkg_info = packageInfo.getInfo(name)

    if pkg_info == None:
        # no pkg found
        print "No installed package found, maybe try adding the '*' character?"
        sys.exit(1)

    name = pkg_info[3]

    print ''
    print "Package selected: " +  name + "."
    print "Please enter the bug summary (should be short!)"
    summary = raw_input('--> ')

    # check similar bug reports through query by package and then match keywords
    bug_list = bz.query({'summary': name})
    print len(bug_list)

    if len(bug_list) > 0:
        kw_list = re.findall(r'\w+', summary.lower())
        print kw_list
        if name in kw_list:
            del kw_list[kw_list.index(name)]
        bug_list = sortByKeywords(bug_list, kw_list, rel_threshold)

    print ''

    if len(bug_list) > 0:
        # if there are still relevant bugs in the list
        # ask the user to modify a similar bug report or create a new one
        idx = pager(bug_list, attr_list=('id', 'summary'),
                msg='Please check if your bug duplicates one of these: (if so, select it)')

        if idx != None:
            bug = bug_list[idx]
            print ''
            print 'You have selected bug #' + str(bug.id) + ' with the summary '\
                    + '"' + bug.summary + '"' + '.'
            print 'You can contribute to it at this URL: ' + bug.url

            sys.exit(0)

    else:
        print 'There were no similar bug reports found, you have to submit a new one.'

    # gather the rest of the required data and submit the bug
    print ''
    try:
        automat = BugReport(bz=bz, pkg=name, pkg_info=pkg_info, summary=summary)
        automat.main()
    except EOFError, eofe:
        return 0
    except (KeyboardInterrupt, SystemExit):
        return 1

    return 0


def do_query(args=None):

    if args and args.package:
        name = args.package
    else:
        name = raw_input('Package to query --> ')

    if name.strip() == '':
        print 'Package name cannot be blank!'
        sys.exit(1)
    if name == '*':
        print 'Invalid package name!'
        sys.exit(1)

    bz = initBugzilla()
    
    pkg_info = packageInfo.getInfo(name)

    if pkg_info == None:
        # no pkg found
        print "No package found, maybe try adding the '*' character?"
        sys.exit(1)

    name = pkg_info[3]

    print ''
    print "Package selected: " +  name + "."
    
    if args and args.summary is not None:
        summary = args.summary
        print "Summary provided: " + summary
    else:
        print "Please enter the bug summary (should be short!)"
        print "You can leave blank to get _all_ the bugs matching that package"
        summary = raw_input()

    # check similar bug reports through query by package and then match keywords
    print ''
    print 'Searching Bugzilla...'
    bug_list = bz.query({'summary': name})

    if len(bug_list) > 0 and summary != '':
        kw_list = re.findall(r'\w+', summary.lower())
        if name in kw_list:
            del kw_list[kw_list.index(name)]
        bug_list = sortByKeywords(bug_list, kw_list, rel_threshold)

    print ''

    if len(bug_list) > 0:
        # if there are still relevant bugs in the list

        idx = pager(bug_list, attr_list=('id', 'summary'),
                msg='Which bug report are you interested in?')
        print ''

        if idx == None:
            msg =  "Since you are not interested in any of the existing bug reports,"\
                    " do you want to submit one? Yes/No"
            yes = yes_no(msg)
            if yes:
                do_submit(pkg=name)
            print "Bye bye then!"
            sys.exit(0)

        bug = bug_list[idx]
        print ''
        print 'You have selected bug #' + str(bug.id) + ' with the summary '\
                + '"' + bug.summary + '"' + '.'
        print 'You can contribute to it at this URL: ' + bug.url

    else:
        print "No bug report found. Why not create one?"

    sys.exit(0)


def do_menu(args=None):
        print 'Starting interactive mode..'

        msg = 'Welcome to the bug reporter! What do you want to do?'
        CHOICES = (
                "find app's name",
                "gather system data",
                "query a report",
                "submit a bug report"
                )
        idx = choice(msg, *CHOICES)
        funcs = {
            0 : do_aid,
            1 : do_gather,
            2 : do_query,
            3 : do_submit
        }
        funcs.get(idx)()


def main():

    if len(sys.argv) == 1:
        # run in submit mode
        do_submit()
        sys.exit(0)

    # creating the parser for the arguments
    desc = '''Bug reporting tool for openSUSE.
Can be run with no arguments, which starts it in submit bug report mode.'''
    parser = argparse.ArgumentParser(description=desc)
    commands = parser.add_subparsers()

    aid = commands.add_parser('aid', help='aid users to find the relevant app')
    aidp = aid.add_subparsers()
    f_app = aidp.add_parser('app', help="click on a window and find out the app's name")
    f_app.set_defaults(func=do_find_app)
    f_pkg = aidp.add_parser('pkg', help="enter an executable's name and find out it's package")
    f_pkg.set_defaults(func=do_find_pkg)

    gather = commands.add_parser('gather', help='gather relevant system info')
    gather.set_defaults(func=do_gather)

    submit = commands.add_parser('submit', help='submit a new bug')
    submit.set_defaults(func=do_submit)

    query = commands.add_parser('query', help='get a list of reports')
    query.set_defaults(func=do_query)
    query.add_argument('package', type=str, help='the name of the package to query')
    query.add_argument('-s', '--summary', help='summary of the bug, for filtering results', dest='summary')
    
    menu = commands.add_parser('menu', help='get a menu to choose a mode')
    menu.set_defaults(func=do_menu)


    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    try:
        main()
    except EOFError:
        print ''
        print 'Caught EOFError, exiting.'
        sys.exit(1)
    except KeyboardInterrupt:
        print ''
        print 'Caught KeyboardInterrupt, exiting.'
        sys.exit(1)
