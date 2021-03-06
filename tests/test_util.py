'''
Copyright (C) 2011  Mihnea Dobrescu-Balaur

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
'''

def test_bz():
    from bugreporter.util.initBz import initBugzilla
    bz = initBugzilla()


def test_package_getInfo():
    from bugreporter.util import packageInfo

    tup = ('0.13.3-5.1', 'https://api.opensuse.org', 'openSUSE:11.4', 'rhythmbox')

    assert packageInfo.getInfo('rhythmbox') == tup
    assert packageInfo.getInfo('nothingExists') == None


def test_package_getAssignedPersons():
    from bugreporter.util import packageInfo
    pkg_info = packageInfo.getInfo('rhythmbox')

    tup = ('os.gnome.maintainers@gmail.com', [])
    assert packageInfo.getAssignedPersons(pkg_info) == tup


def test_bugReport():
    from bugreporter.util.bugReport import BugReport
    from bugreporter.util.initBz import initBugzilla
    from bugreporter.util import packageInfo

    data = {'assigned_to': 'os.gnome.maintainers@gmail.com',
             'cc': [],
              'component': 'GNOME',
               'description': 'Package: rhythmbox\nProject: openSUSE:11.4\nVersion: 0.13.3-5.1\nApiurl: https://api.opensuse.org\nSummary: [rhythmbox] testing\nProduct: openSUSE 11.4\nPlatform: x86-64\nComponent: GNOME\nSeverity: Normal\nAssigned to: os.gnome.maintainers@gmail.com\nCC: \n\n\ntest desc\n',
                'product': 'openSUSE 11.4',
                 'rep_platform': 'x86-64',
                  'severity': 'Normal',
                   'summary': '[rhythmbox] testing',
                'version': 'Final'}
    bz = initBugzilla()
    pkg_info = packageInfo.getInfo('rhythmbox')
    bug = BugReport(bz, 'rhythmbox', pkg_info, 'test', data)

    assert bug.apiurl == pkg_info[1]
