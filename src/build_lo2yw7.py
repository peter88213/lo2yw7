""" Build python script for the LibreOffice "convert yWriter" script.
        
In order to distribute single scripts without dependencies, 
this script "inlines" all modules imported from the pywriter package.

For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import sys
sys.path.insert(0, f'{os.getcwd()}/../../PyWriter/src')
import inliner

SRC = '../src/'
BUILD = '../test/'
SOURCE_FILE = f'{SRC}lo2yw7_.py'
TARGET_FILE = f'{BUILD}lo2yw7.py'

SCRIPT_CODE = """LOCALE_PATH = f'{os.path.dirname(sys.argv[0])}/locale/'"""
UNO_CODE = """from urllib import parse
oPackageInfoProvider = CTX.getByName("/singletons/com.sun.star.deployment.PackageInformationProvider")
sPackageLocation = oPackageInfoProvider.getPackageLocation("org.peter88213.lo2yw7")
packagePath = parse.unquote(sPackageLocation).replace('file:///', '')
LOCALE_PATH = f'{packagePath}/lo2yw7/locale/'"""


def main():
    inliner.run(SOURCE_FILE, TARGET_FILE, 'lo2yw7lib', '../src/')
    inliner.run(TARGET_FILE, TARGET_FILE, 'pywriter', '../../PyWriter/src/')

    # This is a hack to get the script's location within the UNO context:
    with open(TARGET_FILE, 'r') as f:
        text = f.read()
        text = text.replace(SCRIPT_CODE, UNO_CODE)
    with open(TARGET_FILE, 'w') as f:
        f.write(text)
    print('Done.')


if __name__ == '__main__':
    main()
