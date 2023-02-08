"""Convert odt/ods to yw7. 

Version @release
Requires Python 3.6+
Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/lo2yw7
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from lo2yw7lib.uno_tools import *
from pywriter.pywriter_globals import *
from pywriter.converter.yw7_importer import Yw7Importer
from lo2yw7lib.ui_uno import UiUno


def main(sourcePath):
    """Convert an odt/ods document to yw7.
    
    - If yw7 project file exists, update it from odt/ods.
    - Otherwise, create a new yw7 project.
    
    Positional arguments:
        sourcePath -- document to convert. 
    """
    converter = Yw7Importer()
    converter.ui = UiUno(_('Export to yw7'))
    kwargs = {'suffix': None}
    converter.run(sourcePath, **kwargs)

