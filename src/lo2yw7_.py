"""Convert odt/ods to yw7. 

Version @release
Requires Python 3.6+
Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/lo2yw7
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import uno
from com.sun.star.awt.MessageBoxType import MESSAGEBOX, INFOBOX, WARNINGBOX, ERRORBOX, QUERYBOX
from com.sun.star.beans import PropertyValue
import os
from lo2yw7lib.uno_tools import *
from pywriter.pywriter_globals import *
from pywriter.converter.yw7_importer import Yw7Importer
from lo2yw7lib.ui_uno import UiUno


def export_yw():
    """Export the currently loaded document to a yWriter 7 project."""
    ThisComponent = XSCRIPTCONTEXT.getDocument()

    # Get document's filename
    # document = XSCRIPTCONTEXT.getDocument().CurrentController.Frame
    document = ThisComponent.CurrentController.Frame
    documentPath = XSCRIPTCONTEXT.getDocument().getURL()
    # documentPath = ThisComponent.getURL()

    # Save the document.
    if ThisComponent.isModified():
        ThisComponent.store()

    # Convert the saved document.
    if documentPath.endswith('.odt') or documentPath.endswith('.ods'):
        targetPath = uno.fileUrlToSystemPath(documentPath)
    else:
        msgbox(f'{_("File type is not supported")}: "{norm_path(documentPath)}".', type_msg=ERRORBOX)
        return

    converter = Yw7Importer()
    converter.ui = UiUno(_('Export to yw7'))
    kwargs = {'suffix': None}
    converter.run(targetPath, **kwargs)

