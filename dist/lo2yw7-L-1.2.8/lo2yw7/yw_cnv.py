"""Starter script for the odt/ods to yw7 converter. 

Version 1.2.8
Requires Python 3.6+
Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/lo2yw7
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import uno
import lo2yw7


def export_yw():
    """Save the document if modified, and call the converter script."""
    thisComponent = XSCRIPTCONTEXT.getDocument()

    if thisComponent.isModified():
        thisComponent.store()

    documentUrl = thisComponent.getURL()
    if documentUrl:
        sourcePath = uno.fileUrlToSystemPath(documentUrl)
    else:
        sourcePath = ''
    lo2yw7.main(sourcePath)
