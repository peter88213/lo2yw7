"""Convert odt/ods to yw7. 

Version 1.2.4
Requires Python 3.6+
Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/lo2yw7
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import uno
from com.sun.star.awt.MessageBoxType import MESSAGEBOX, INFOBOX, WARNINGBOX, ERRORBOX, QUERYBOX
from com.sun.star.awt.MessageBoxButtons import BUTTONS_OK, BUTTONS_OK_CANCEL, BUTTONS_YES_NO, BUTTONS_YES_NO_CANCEL, BUTTONS_RETRY_CANCEL, BUTTONS_ABORT_IGNORE_RETRY

CTX = uno.getComponentContext()
SM = CTX.getServiceManager()


def create_instance(name, with_context=False):
    if with_context:
        instance = SM.createInstanceWithContext(name, CTX)
    else:
        instance = SM.createInstance(name)
    return instance


import os
import sys
import gettext
import locale

__all__ = ['Error',
           '_',
           'LOCALE_PATH',
           'CURRENT_LANGUAGE',
           'norm_path',
           'string_to_list',
           'list_to_string',
           ]


class Error(Exception):
    """Base class for exceptions."""


#--- Initialize localization.
oPackageInfoProvider = CTX.getByName("/singletons/com.sun.star.deployment.PackageInformationProvider")
sPackageLocation = oPackageInfoProvider.getPackageLocation("org.peter88213.lo2yw7")
packagePath = uno.fileUrlToSystemPath(sPackageLocation)
LOCALE_PATH = f'{packagePath}/lo2yw7/locale/'
try:
    CURRENT_LANGUAGE = locale.getlocale()[0][:2]
except:
    # Fallback for old Windows versions.
    CURRENT_LANGUAGE = locale.getdefaultlocale()[0][:2]
try:
    t = gettext.translation('pywriter', LOCALE_PATH, languages=[CURRENT_LANGUAGE])
    _ = t.gettext
except:

    def _(message):
        return message


def norm_path(path):
    if path is None:
        path = ''
    return os.path.normpath(path)


def string_to_list(text, divider=';'):
    """Convert a string into a list with unique elements.
    
    Positional arguments:
        text -- string containing divider-separated substrings.
        
    Optional arguments:
        divider -- string that divides the substrings.
    
    Split a string into a list of strings. Retain the order, but discard duplicates.
    Remove leading and trailing spaces, if any.
    Return a list of strings.
    If an error occurs, return an empty list.
    """
    elements = []
    try:
        tempList = text.split(divider)
        for element in tempList:
            element = element.strip()
            if element and not element in elements:
                elements.append(element)
        return elements

    except:
        return []


def list_to_string(elements, divider=';'):
    """Join strings from a list.
    
    Positional arguments:
        elements -- list of elements to be concatenated.
        
    Optional arguments:
        divider -- string that divides the substrings.
    
    Return a string which is the concatenation of the 
    members of the list of strings "elements", separated by 
    a comma plus a space. The space allows word wrap in 
    spreadsheet cells.
    If an error occurs, return an empty string.
    """
    try:
        text = divider.join(elements)
        return text

    except:
        return ''

# The setup script will patch the pywriter_globals code, using constants defined above.


def msgbox(message, title=_('Export to yw7'), buttons=BUTTONS_OK, type_msg=INFOBOX):
    """ Create message box
        type_msg: MESSAGEBOX, INFOBOX, WARNINGBOX, ERRORBOX, QUERYBOX

        MSG_BUTTONS: BUTTONS_OK, BUTTONS_OK_CANCEL, BUTTONS_YES_NO, 
        BUTTONS_YES_NO_CANCEL, BUTTONS_RETRY_CANCEL, BUTTONS_ABORT_IGNORE_RETRY

        MSG_RESULTS: OK, YES, NO, CANCEL

        http://api.libreoffice.org/docs/idl/ref/interfacecom_1_1sun_1_1star_1_1awt_1_1XMessageBoxFactory.html
    """
    toolkit = create_instance('com.sun.star.awt.Toolkit')
    parent = toolkit.getDesktopWindow()
    mb = toolkit.createMessageBox(parent, type_msg, buttons, title, str(message))
    return mb.execute()



def open_document(document):
    """Open a document with the operating system's standard application."""
    try:
        os.startfile(norm_path(document))
        # Windows
    except:
        try:
            os.system('xdg-open "%s"' % norm_path(document))
            # Linux
        except:
            try:
                os.system('open "%s"' % norm_path(document))
                # Mac
            except:
                pass


class Ui:
    """Base class for UI facades, implementing a 'silent mode'.
    
    Public methods:
        ask_yes_no(text) -- return True or False.
        set_info_what(message) -- show what the converter is going to do.
        set_info_how(message) -- show how the converter is doing.
        start() -- launch the GUI, if any.
        show_warning(message) -- Stub for displaying a warning message.
        
    Public instance variables:
        infoWhatText -- buffer for general messages.
        infoHowText -- buffer for error/success messages.
    """

    def __init__(self, title):
        """Initialize text buffers for messaging.
        
        Positional arguments:
            title -- application title.
        """
        self.infoWhatText = ''
        self.infoHowText = ''

    def ask_yes_no(self, text):
        """Return True or False.
        
        Positional arguments:
            text -- question to be asked. 
            
        This is a stub used for "silent mode".
        The application may use a subclass for confirmation requests.    
        """
        return True

    def set_info_what(self, message):
        """Show what the converter is going to do.
        
        Positional arguments:
            message -- message to be buffered. 
        """
        self.infoWhatText = message

    def set_info_how(self, message):
        """Show how the converter is doing.
        
        Positional arguments:
            message -- message to be buffered.
            
        Print the message to stderr, replacing the error marker, if any.
        """
        if message.startswith('!'):
            message = f'FAIL: {message.split("!", maxsplit=1)[1].strip()}'
            sys.stderr.write(message)
        self.infoHowText = message

    def start(self):
        """Launch the GUI, if any.
        
        To be overridden by subclasses requiring
        special action to launch the user interaction.
        """

    def show_warning(self, message):
        """Stub for displaying a warning message."""
import re


class BasicElement:
    """Basic element representation (may be a project note).
    
    Public instance variables:
        title -- str: title (name).
        desc -- str: description.
        kwVar -- dict: custom keyword variables.
    """

    def __init__(self):
        """Initialize instance variables."""
        self.title = None
        # str
        # xml: <Title>

        self.desc = None
        # str
        # xml: <Desc>

        self.kwVar = {}
        # dictionary
        # Optional key/value instance variables for customization.

LANGUAGE_TAG = re.compile('\[lang=(.*?)\]')


class Novel(BasicElement):
    """Novel representation.

    This class represents a novel with additional 
    attributes and structural information (a full set or a subset
    of the information included in an yWriter project file).

    Public methods:
        get_languages() -- Determine the languages used in the document.
        check_locale() -- Check the document's locale (language code and country code).

    Public instance variables:
        authorName -- str: author's name.
        author bio -- str: information about the author.
        fieldTitle1 -- str: scene rating field title 1.
        fieldTitle2 -- str: scene rating field title 2.
        fieldTitle3 -- str: scene rating field title 3.
        fieldTitle4 -- str: scene rating field title 4.
        chapters -- dict: (key: ID; value: chapter instance).
        scenes -- dict: (key: ID, value: scene instance).
        srtChapters -- list: the novel's sorted chapter IDs.
        locations -- dict: (key: ID, value: WorldElement instance).
        srtLocations -- list: the novel's sorted location IDs.
        items -- dict: (key: ID, value: WorldElement instance).
        srtItems -- list: the novel's sorted item IDs.
        characters -- dict: (key: ID, value: character instance).
        srtCharacters -- list: the novel's sorted character IDs.
        projectNotes -- dict:  (key: ID, value: projectNote instance).
        srtPrjNotes -- list: the novel's sorted project notes.
    """

    def __init__(self):
        """Initialize instance variables.
            
        Extends the superclass constructor.          
        """
        super().__init__()

        self.authorName = None
        # str
        # xml: <PROJECT><AuthorName>

        self.authorBio = None
        # str
        # xml: <PROJECT><Bio>

        self.fieldTitle1 = None
        # str
        # xml: <PROJECT><FieldTitle1>

        self.fieldTitle2 = None
        # str
        # xml: <PROJECT><FieldTitle2>

        self.fieldTitle3 = None
        # str
        # xml: <PROJECT><FieldTitle3>

        self.fieldTitle4 = None
        # str
        # xml: <PROJECT><FieldTitle4>

        self.wordTarget = None
        # int
        # xml: <PROJECT><wordTarget>

        self.wordCountStart = None
        # int
        # xml: <PROJECT><wordCountStart>

        self.wordTarget = None
        # int
        # xml: <PROJECT><wordCountStart>

        self.chapters = {}
        # dict
        # xml: <CHAPTERS><CHAPTER><ID>
        # key = chapter ID, value = Chapter instance.
        # The order of the elements does not matter (the novel's order of the chapters is defined by srtChapters)

        self.scenes = {}
        # dict
        # xml: <SCENES><SCENE><ID>
        # key = scene ID, value = Scene instance.
        # The order of the elements does not matter (the novel's order of the scenes is defined by
        # the order of the chapters and the order of the scenes within the chapters)

        self.languages = None
        # list of str
        # List of non-document languages occurring as scene markup.
        # Format: ll-CC, where ll is the language code, and CC is the country code.

        self.srtChapters = []
        # list of str
        # The novel's chapter IDs. The order of its elements corresponds to the novel's order of the chapters.

        self.locations = {}
        # dict
        # xml: <LOCATIONS>
        # key = location ID, value = WorldElement instance.
        # The order of the elements does not matter.

        self.srtLocations = []
        # list of str
        # The novel's location IDs. The order of its elements
        # corresponds to the XML project file.

        self.items = {}
        # dict
        # xml: <ITEMS>
        # key = item ID, value = WorldElement instance.
        # The order of the elements does not matter.

        self.srtItems = []
        # list of str
        # The novel's item IDs. The order of its elements corresponds to the XML project file.

        self.characters = {}
        # dict
        # xml: <CHARACTERS>
        # key = character ID, value = Character instance.
        # The order of the elements does not matter.

        self.srtCharacters = []
        # list of str
        # The novel's character IDs. The order of its elements corresponds to the XML project file.

        self.projectNotes = {}
        # dict
        # xml: <PROJECTNOTES>
        # key = note ID, value = note instance.
        # The order of the elements does not matter.

        self.srtPrjNotes = []
        # list of str
        # The novel's projectNote IDs. The order of its elements corresponds to the XML project file.

        self.languageCode = None
        # str
        # Language code acc. to ISO 639-1.

        self.countryCode = None
        # str
        # Country code acc. to ISO 3166-2.

    def get_languages(self):
        """Determine the languages used in the document.
        
        Populate the self.languages list with all language codes found in the scene contents.        
        Example:
        - language markup: 'Standard text [lang=en-AU]Australian text[/lang=en-AU].'
        - language code: 'en-AU'
        """

        def languages(text):
            """Return a generator object with the language codes appearing in text.
            
            Example:
            - language markup: 'Standard text [lang=en-AU]Australian text[/lang=en-AU].'
            - language code: 'en-AU'
            """
            if text:
                m = LANGUAGE_TAG.search(text)
                while m:
                    text = text[m.span()[1]:]
                    yield m.group(1)
                    m = LANGUAGE_TAG.search(text)

        self.languages = []
        for scId in self.scenes:
            text = self.scenes[scId].sceneContent
            if text:
                for language in languages(text):
                    if not language in self.languages:
                        self.languages.append(language)

    def check_locale(self):
        """Check the document's locale (language code and country code).
        
        If the locale is missing, set the system locale.  
        If the locale doesn't look plausible, set "no language".        
        """
        if not self.languageCode:
            # Language isn't set.
            try:
                sysLng, sysCtr = locale.getlocale()[0].split('_')
            except:
                # Fallback for old Windows versions.
                sysLng, sysCtr = locale.getdefaultlocale()[0].split('_')
            self.languageCode = sysLng
            self.countryCode = sysCtr
            return

        try:
            # Plausibility check: code must have two characters.
            if len(self.languageCode) == 2:
                if len(self.countryCode) == 2:
                    return
                    # keep the setting
        except:
            # code isn't a string
            pass
        # Existing language or country field looks not plausible
        self.languageCode = 'zxx'
        self.countryCode = 'none'



class YwCnvUi:
    """Base class for Novel file conversion with user interface.

    Public methods:
        export_from_yw(sourceFile, targetFile) -- Convert from yWriter project to other file format.
        create_yw(sourceFile, targetFile) -- Create target from source.
        import_to_yw(sourceFile, targetFile) -- Convert from any file format to yWriter project.

    Instance variables:
        ui -- Ui (can be overridden e.g. by subclasses).
        newFile -- str: path to the target file in case of success.   
    """

    def __init__(self):
        """Define instance variables."""
        self.ui = Ui('')
        # Per default, 'silent mode' is active.
        self.newFile = None
        # Also indicates successful conversion.

    def export_from_yw(self, source, target):
        """Convert from yWriter project to other file format.

        Positional arguments:
            source -- YwFile subclass instance.
            target -- Any Novel subclass instance.

        Operation:
        1. Send specific information about the conversion to the UI.
        2. Convert source into target.
        3. Pass the message to the UI.
        4. Save the new file pathname.

        Error handling:
        - If the conversion fails, newFile is set to None.
        """
        self.ui.set_info_what(
            _('Input: {0} "{1}"\nOutput: {2} "{3}"').format(source.DESCRIPTION, norm_path(source.filePath), target.DESCRIPTION, norm_path(target.filePath)))
        try:
            self.check(source, target)
            source.novel = Novel()
            source.read()
            target.novel = source.novel
            target.write()
        except Error as ex:
            message = f'!{str(ex)}'
            self.newFile = None
        else:
            message = f'{_("File written")}: "{norm_path(target.filePath)}".'
            self.newFile = target.filePath
        finally:
            self.ui.set_info_how(message)

    def create_yw7(self, source, target):
        """Create target from source.

        Positional arguments:
            source -- Any Novel subclass instance.
            target -- YwFile subclass instance.

        Operation:
        1. Send specific information about the conversion to the UI.
        2. Convert source into target.
        3. Pass the message to the UI.
        4. Save the new file pathname.

        Error handling:
        - Tf target already exists as a file, the conversion is cancelled,
          an error message is sent to the UI.
        - If the conversion fails, newFile is set to None.
        """
        self.ui.set_info_what(
            _('Create a yWriter project file from {0}\nNew project: "{1}"').format(source.DESCRIPTION, norm_path(target.filePath)))
        if os.path.isfile(target.filePath):
            self.ui.set_info_how(f'!{_("File already exists")}: "{norm_path(target.filePath)}".')
        else:
            try:
                self.check(source, target)
                source.novel = Novel()
                source.read()
                target.novel = source.novel
                target.write()
            except Error as ex:
                message = f'!{str(ex)}'
                self.newFile = None
            else:
                message = f'{_("File written")}: "{norm_path(target.filePath)}".'
                self.newFile = target.filePath
            finally:
                self.ui.set_info_how(message)

    def import_to_yw(self, source, target):
        """Convert from any file format to yWriter project.

        Positional arguments:
            source -- Any Novel subclass instance.
            target -- YwFile subclass instance.

        Operation:
        1. Send specific information about the conversion to the UI.
        2. Convert source into target.
        3. Pass the message to the UI.
        4. Delete the temporay file, if exists.
        5. Save the new file pathname.

        Error handling:
        - If the conversion fails, newFile is set to None.
        """
        self.ui.set_info_what(
            _('Input: {0} "{1}"\nOutput: {2} "{3}"').format(source.DESCRIPTION, norm_path(source.filePath), target.DESCRIPTION, norm_path(target.filePath)))
        self.newFile = None
        try:
            self.check(source, target)
            target.novel = Novel()
            target.read()
            source.novel = target.novel
            source.read()
            target.novel = source.novel
            target.write()
        except Error as ex:
            message = f'!{str(ex)}'
        else:
            message = f'{_("File written")}: "{norm_path(target.filePath)}".'
            self.newFile = target.filePath
            if target.scenesSplit:
                self.ui.show_warning(_('New scenes created during conversion.'))
        finally:
            self.ui.set_info_how(message)

    def _confirm_overwrite(self, filePath):
        """Return boolean permission to overwrite the target file.
        
        Positional arguments:
            fileName -- path to the target file.
        
        Overrides the superclass method.
        """
        return self.ui.ask_yes_no(_('Overwrite existing file "{}"?').format(norm_path(filePath)))

    def _open_newFile(self):
        """Open the converted file for editing and exit the converter script."""
        open_document(self.newFile)
        sys.exit(0)

    def check(self, source, target):
        """Error handling:
        
        - Check if source and target are correctly initialized.
        - Ask for permission to overwrite target.
        - Raise the "Error" exception in case of error. 
        """
        if source.filePath is None:
            raise Error(f'{_("File type is not supported")}.')

        if not os.path.isfile(source.filePath):
            raise Error(f'{_("File not found")}: "{norm_path(source.filePath)}".')

        if target.filePath is None:
            raise Error(f'{_("File type is not supported")}.')

        if os.path.isfile(target.filePath) and not self._confirm_overwrite(target.filePath):
            raise Error(f'{_("Action canceled by user")}.')



class FileFactory:
    """Base class for conversion object factory classes.
    """

    def __init__(self, fileClasses=[]):
        """Write the parameter to a "private" instance variable.

        Optional arguments:
            _fileClasses -- list of classes from which an instance can be returned.
        """
        self._fileClasses = fileClasses


class ExportSourceFactory(FileFactory):
    """A factory class that instantiates a yWriter object to read.

    Public methods:
        make_file_objects(self, sourcePath, **kwargs) -- return conversion objects.
    """

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a source object for conversion from a yWriter project.

        Positional arguments:
            sourcePath -- str: path to the source file to convert.

        Return a tuple with two elements:
        - sourceFile: a YwFile subclass instance
        - targetFile: None

        Raise the "Error" exception in case of error. 
        """
        __, fileExtension = os.path.splitext(sourcePath)
        for fileClass in self._fileClasses:
            if fileClass.EXTENSION == fileExtension:
                sourceFile = fileClass(sourcePath, **kwargs)
                return sourceFile, None

        raise Error(f'{_("File type is not supported")}: "{norm_path(sourcePath)}".')


class ExportTargetFactory(FileFactory):
    """A factory class that instantiates a document object to write.

    Public methods:
        make_file_objects(self, sourcePath, **kwargs) -- return conversion objects.
    """

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a target object for conversion from a yWriter project.

        Positional arguments:
            sourcePath -- str: path to the source file to convert.

        Required keyword arguments: 
            suffix -- str: target file name suffix.

        Return a tuple with two elements:
        - sourceFile: None
        - targetFile: a FileExport subclass instance
        
        Raise the "Error" exception in case of error.          
        """
        fileName, __ = os.path.splitext(sourcePath)
        suffix = kwargs['suffix']
        for fileClass in self._fileClasses:
            if fileClass.SUFFIX == suffix:
                if suffix is None:
                    suffix = ''
                targetFile = fileClass(f'{fileName}{suffix}{fileClass.EXTENSION}', **kwargs)
                return None, targetFile

        raise Error(f'{_("Export type is not supported")}: "{suffix}".')


class ImportSourceFactory(FileFactory):
    """A factory class that instantiates a documente object to read.

    Public methods:
        make_file_objects(self, sourcePath, **kwargs) -- return conversion objects.
    """

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a source object for conversion to a yWriter project.       

        Positional arguments:
            sourcePath -- str: path to the source file to convert.

        Return a tuple with two elements:
        - sourceFile: a Novel subclass instance, or None in case of error
        - targetFile: None

        Raise the "Error" exception in case of error. 
        """
        for fileClass in self._fileClasses:
            if fileClass.SUFFIX is not None:
                if sourcePath.endswith(f'{fileClass.SUFFIX }{fileClass.EXTENSION}'):
                    sourceFile = fileClass(sourcePath, **kwargs)
                    return sourceFile, None

        raise Error(f'{_("This document is not meant to be written back")}.')


class ImportTargetFactory(FileFactory):
    """A factory class that instantiates a yWriter object to write.

    Public methods:
        make_file_objects(self, sourcePath, **kwargs) -- return conversion objects.
    """

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a target object for conversion to a yWriter project.

        Positional arguments:
            sourcePath -- str: path to the source file to convert.

        Required keyword arguments: 
            suffix -- str: target file name suffix.

        Return a tuple with two elements:
        - sourceFile: None
        - targetFile: a YwFile subclass instance

        Raise the "Error" exception in case of error. 
        """
        fileName, __ = os.path.splitext(sourcePath)
        sourceSuffix = kwargs['suffix']
        if sourceSuffix:
            # Remove the suffix from the source file name.
            # This should also work if the file name already contains the suffix,
            # e.g. "test_notes_notes.odt".
            e = fileName.split(sourceSuffix)
            if len(e) > 1:
                e.pop()
            ywPathBasis = ''.join(e)
        else:
            ywPathBasis = fileName

        # Look for an existing yWriter project to rewrite.
        for fileClass in self._fileClasses:
            if os.path.isfile(f'{ywPathBasis}{fileClass.EXTENSION}'):
                targetFile = fileClass(f'{ywPathBasis}{fileClass.EXTENSION}', **kwargs)
                return None, targetFile

        raise Error(f'{_("No yWriter project to write")}.')


class YwCnvFf(YwCnvUi):
    """Class for Novel file conversion using factory methods to create target and source classes.

    Public methods:
        run(sourcePath, **kwargs) -- create source and target objects and run conversion.

    Class constants:
        EXPORT_SOURCE_CLASSES -- list of YwFile subclasses from which can be exported.
        EXPORT_TARGET_CLASSES -- list of FileExport subclasses to which export is possible.
        IMPORT_SOURCE_CLASSES -- list of Novel subclasses from which can be imported.
        IMPORT_TARGET_CLASSES -- list of YwFile subclasses to which import is possible.

    All lists are empty and meant to be overridden by subclasses.

    Instance variables:
        exportSourceFactory -- ExportSourceFactory.
        exportTargetFactory -- ExportTargetFactory.
        importSourceFactory -- ImportSourceFactory.
        importTargetFactory -- ImportTargetFactory.
        newProjectFactory -- FileFactory (a stub to be overridden by subclasses).
    """
    EXPORT_SOURCE_CLASSES = []
    EXPORT_TARGET_CLASSES = []
    IMPORT_SOURCE_CLASSES = []
    IMPORT_TARGET_CLASSES = []

    def __init__(self):
        """Create strategy class instances.
        
        Extends the superclass constructor.
        """
        super().__init__()
        self.exportSourceFactory = ExportSourceFactory(self.EXPORT_SOURCE_CLASSES)
        self.exportTargetFactory = ExportTargetFactory(self.EXPORT_TARGET_CLASSES)
        self.importSourceFactory = ImportSourceFactory(self.IMPORT_SOURCE_CLASSES)
        self.importTargetFactory = ImportTargetFactory(self.IMPORT_TARGET_CLASSES)
        self.newProjectFactory = FileFactory()

    def run(self, sourcePath, **kwargs):
        """Create source and target objects and run conversion.

        Positional arguments: 
            sourcePath -- str: the source file path.
        
        Required keyword arguments: 
            suffix -- str: target file name suffix.

        This is a template method that calls superclass methods as primitive operations by case.
        """
        self.newFile = None
        if not os.path.isfile(sourcePath):
            self.ui.set_info_how(f'!{_("File not found")}: "{norm_path(sourcePath)}".')
            return

        try:
            source, __ = self.exportSourceFactory.make_file_objects(sourcePath, **kwargs)
        except Error:
            # The source file is not a yWriter project.
            try:
                source, __ = self.importSourceFactory.make_file_objects(sourcePath, **kwargs)
            except Error:
                # A new yWriter project might be required.
                try:
                    source, target = self.newProjectFactory.make_file_objects(sourcePath, **kwargs)
                except Error as ex:
                    self.ui.set_info_how(f'!{str(ex)}')
                else:
                    self.create_yw7(source, target)
            else:
                # Try to update an existing yWriter project.
                kwargs['suffix'] = source.SUFFIX
                try:
                    __, target = self.importTargetFactory.make_file_objects(sourcePath, **kwargs)
                except Error as ex:
                    self.ui.set_info_how(f'!{str(ex)}')
                else:
                    self.import_to_yw(source, target)
        else:
            # The source file is a yWriter project.
            try:
                __, target = self.exportTargetFactory.make_file_objects(sourcePath, **kwargs)
            except Error as ex:
                self.ui.set_info_how(f'!{str(ex)}')
            else:
                self.export_from_yw(source, target)
import zipfile
from html import unescape
from datetime import datetime
import xml.etree.ElementTree as ET


class Chapter(BasicElement):
    """yWriter chapter representation.
    
    Public instance variables:
        chLevel -- int: chapter level (part/chapter).
        chType -- int: chapter type (Normal/Notes/Todo/Unused).
        suppressChapterTitle -- bool: uppress chapter title when exporting.
        isTrash -- bool: True, if the chapter is the project's trash bin.
        suppressChapterBreak -- bool: Suppress chapter break when exporting.
        srtScenes -- list of str: the chapter's sorted scene IDs.        
    """

    def __init__(self):
        """Initialize instance variables.
        
        Extends the superclass constructor.
        """
        super().__init__()

        self.chLevel = None
        # int
        # xml: <SectionStart>
        # 0 = chapter level
        # 1 = section level ("this chapter begins a section")

        self.chType = None
        # int
        # 0 = Normal
        # 1 = Notes
        # 2 = Todo
        # 3= Unused
        # Applies to projects created by yWriter version 7.0.7.2+.
        #
        # xml: <ChapterType>
        # xml: <Type>
        # xml: <Unused>
        #
        # This is how yWriter 7.1.3.0 reads the chapter type:
        #
        # Type   |<Unused>|<Type>|<ChapterType>|chType
        # -------+--------+------+--------------------
        # Normal | N/A    | N/A  | N/A         | 0
        # Normal | N/A    | 0    | N/A         | 0
        # Notes  | x      | 1    | N/A         | 1
        # Unused | -1     | 0    | N/A         | 3
        # Normal | N/A    | x    | 0           | 0
        # Notes  | x      | x    | 1           | 1
        # Todo   | x      | x    | 2           | 2
        # Unused | -1     | x    | x           | 3
        #
        # This is how yWriter 7.1.3.0 writes the chapter type:
        #
        # Type   |<Unused>|<Type>|<ChapterType>|chType
        #--------+--------+------+-------------+------
        # Normal | N/A    | 0    | 0           | 0
        # Notes  | -1     | 1    | 1           | 1
        # Todo   | -1     | 1    | 2           | 2
        # Unused | -1     | 1    | 0           | 3

        self.suppressChapterTitle = None
        # bool
        # xml: <Fields><Field_SuppressChapterTitle> 1
        # True: Chapter heading not to be displayed in written document.
        # False: Chapter heading to be displayed in written document.

        self.isTrash = None
        # bool
        # xml: <Fields><Field_IsTrash> 1
        # True: This chapter is the yw7 project's "trash bin".
        # False: This chapter is not a "trash bin".

        self.suppressChapterBreak = None
        # bool
        # xml: <Fields><Field_SuppressChapterBreak> 0

        self.srtScenes = []
        # list of str
        # xml: <Scenes><ScID>
        # The chapter's scene IDs. The order of its elements
        # corresponds to the chapter's order of the scenes.

#--- Regular expressions for counting words and characters like in LibreOffice.
# See: https://help.libreoffice.org/latest/en-GB/text/swriter/guide/words_count.html

ADDITIONAL_WORD_LIMITS = re.compile('--|—|–')
# this is to be replaced by spaces, thus making dashes and dash replacements word limits

NO_WORD_LIMITS = re.compile('\[.+?\]|\/\*.+?\*\/|-|^\>', re.MULTILINE)
# this is to be replaced by empty strings, thus excluding markup and comments from
# word counting, and making hyphens join words

NON_LETTERS = re.compile('\[.+?\]|\/\*.+?\*\/|\n|\r')
# this is to be replaced by empty strings, thus excluding markup, comments, and linefeeds
# from letter counting


class Scene(BasicElement):
    """yWriter scene representation.
    
    Public instance variables:
        sceneContent -- str: scene content (property with getter and setter).
        wordCount - int: word count (derived; updated by the sceneContent setter).
        letterCount - int: letter count (derived; updated by the sceneContent setter).
        scType -- int: Scene type (Normal/Notes/Todo/Unused).
        doNotExport -- bool: True if the scene is not to be exported to RTF.
        status -- int: scene status (Outline/Draft/1st Edit/2nd Edit/Done).
        notes -- str: scene notes in a single string.
        tags -- list of scene tags. 
        field1 -- int: scene ratings field 1.
        field2 -- int: scene ratings field 2.
        field3 -- int: scene ratings field 3.
        field4 -- int: scene ratings field 4.
        appendToPrev -- bool: if True, append the scene without a divider to the previous scene.
        isReactionScene -- bool: if True, the scene is "reaction". Otherwise, it's "action". 
        isSubPlot -- bool: if True, the scene belongs to a sub-plot. Otherwise it's main plot.  
        goal -- str: the main actor's scene goal. 
        conflict -- str: what hinders the main actor to achieve his goal.
        outcome -- str: what comes out at the end of the scene.
        characters -- list of character IDs related to this scene.
        locations -- list of location IDs related to this scene. 
        items -- list of item IDs related to this scene.
        date -- str: specific start date in ISO format (yyyy-mm-dd).
        time -- str: specific start time in ISO format (hh:mm).
        minute -- str: unspecific start time: minutes.
        hour -- str: unspecific start time: hour.
        day -- str: unspecific start time: day.
        lastsMinutes -- str: scene duration: minutes.
        lastsHours -- str: scene duration: hours.
        lastsDays -- str: scene duration: days. 
        image -- str:  path to an image related to the scene. 
    """
    STATUS = (None, 'Outline', 'Draft', '1st Edit', '2nd Edit', 'Done')
    # Emulate an enumeration for the scene status
    # Since the items are used to replace text,
    # they may contain spaces. This is why Enum cannot be used here.

    ACTION_MARKER = 'A'
    REACTION_MARKER = 'R'
    NULL_DATE = '0001-01-01'
    NULL_TIME = '00:00:00'

    def __init__(self):
        """Initialize instance variables.
        
        Extends the superclass constructor.
        """
        super().__init__()

        self._sceneContent = None
        # str
        # xml: <SceneContent>
        # Scene text with yW7 raw markup.

        self.wordCount = 0
        # int # xml: <WordCount>
        # To be updated by the sceneContent setter

        self.letterCount = 0
        # int
        # xml: <LetterCount>
        # To be updated by the sceneContent setter

        self.scType = None
        # Scene type (Normal/Notes/Todo/Unused).
        #
        # xml: <Unused>
        # xml: <Fields><Field_SceneType>
        #
        # This is how yWriter 7.1.3.0 reads the scene type:
        #
        # Type   |<Unused>|Field_SceneType>|scType
        #--------+--------+----------------+------
        # Notes  | x      | 1              | 1
        # Todo   | x      | 2              | 2
        # Unused | -1     | N/A            | 3
        # Unused | -1     | 0              | 3
        # Normal | N/A    | N/A            | 0
        # Normal | N/A    | 0              | 0
        #
        # This is how yWriter 7.1.3.0 writes the scene type:
        #
        # Type   |<Unused>|Field_SceneType>|scType
        #--------+--------+----------------+------
        # Normal | N/A    | N/A            | 0
        # Notes  | -1     | 1              | 1
        # Todo   | -1     | 2              | 2
        # Unused | -1     | 0              | 3

        self.doNotExport = None
        # bool
        # xml: <ExportCondSpecific><ExportWhenRTF>

        self.status = None
        # int
        # xml: <Status>
        # 1 - Outline
        # 2 - Draft
        # 3 - 1st Edit
        # 4 - 2nd Edit
        # 5 - Done
        # See also the STATUS list for conversion.

        self.notes = None
        # str
        # xml: <Notes>

        self.tags = None
        # list of str
        # xml: <Tags>

        self.field1 = None
        # str
        # xml: <Field1>

        self.field2 = None
        # str
        # xml: <Field2>

        self.field3 = None
        # str
        # xml: <Field3>

        self.field4 = None
        # str
        # xml: <Field4>

        self.appendToPrev = None
        # bool
        # xml: <AppendToPrev> -1

        self.isReactionScene = None
        # bool
        # xml: <ReactionScene> -1

        self.isSubPlot = None
        # bool
        # xml: <SubPlot> -1

        self.goal = None
        # str
        # xml: <Goal>

        self.conflict = None
        # str
        # xml: <Conflict>

        self.outcome = None
        # str
        # xml: <Outcome>

        self.characters = None
        # list of str
        # xml: <Characters><CharID>

        self.locations = None
        # list of str
        # xml: <Locations><LocID>

        self.items = None
        # list of str
        # xml: <Items><ItemID>

        self.date = None
        # str (yyyy-mm-dd)
        # xml: <SpecificDateMode>-1
        # xml: <SpecificDateTime>1900-06-01 20:38:00

        self.time = None
        # str (hh:mm:ss)
        # xml: <SpecificDateMode>-1
        # xml: <SpecificDateTime>1900-06-01 20:38:00

        self.day = None
        # str
        # xml: <Day>

        self.lastsMinutes = None
        # str
        # xml: <LastsMinutes>

        self.lastsHours = None
        # str
        # xml: <LastsHours>

        self.lastsDays = None
        # str
        # xml: <LastsDays>

        self.image = None
        # str
        # xml: <ImageFile>

        self.scnArcs = None
        # str
        # xml: <Field_SceneArcs>
        # Semicolon-separated arc titles.
        # Example: 'A' for 'A-Storyline'.
        # If the scene is "Todo" type, an assigned single arc
        # should be defined by it.

        self.scnStyle = None
        # str
        # xml: <Field_SceneStyle>
        # May be 'explaining', 'descriptive', or 'summarizing'.
        # None is the default, meaning 'staged'.

    @property
    def sceneContent(self):
        return self._sceneContent

    @sceneContent.setter
    def sceneContent(self, text):
        """Set sceneContent updating word count and letter count."""
        self._sceneContent = text
        text = ADDITIONAL_WORD_LIMITS.sub(' ', text)
        text = NO_WORD_LIMITS.sub('', text)
        wordList = text.split()
        self.wordCount = len(wordList)
        text = NON_LETTERS.sub('', self._sceneContent)
        self.letterCount = len(text)


class WorldElement(BasicElement):
    """Story world element representation (may be location or item).
    
    Public instance variables:
        image -- str: image file path.
        tags -- list of tags.
        aka -- str: alternate name.
    """

    def __init__(self):
        """Initialize instance variables.
        
        Extends the superclass constructor.
        """
        super().__init__()

        self.image = None
        # str
        # xml: <ImageFile>

        self.tags = None
        # list of str
        # xml: <Tags>

        self.aka = None
        # str
        # xml: <AKA>



class Character(WorldElement):
    """yWriter character representation.

    Public instance variables:
        notes -- str: character notes.
        bio -- str: character biography.
        goals -- str: character's goals in the story.
        fullName -- str: full name (the title inherited may be a short name).
        isMajor -- bool: True, if it's a major character.
    """
    MAJOR_MARKER = 'Major'
    MINOR_MARKER = 'Minor'

    def __init__(self):
        """Extends the superclass constructor by adding instance variables."""
        super().__init__()

        self.notes = None
        # str
        # xml: <Notes>

        self.bio = None
        # str
        # xml: <Bio>

        self.goals = None
        # str
        # xml: <Goals>

        self.fullName = None
        # str
        # xml: <FullName>

        self.isMajor = None
        # bool
        # xml: <Major>
from urllib.parse import quote


class File:
    """Abstract yWriter project file representation.

    This class represents a file containing a novel with additional 
    attributes and structural information (a full set or a subset
    of the information included in an yWriter project file).

    Public methods:
        read() -- Parse the file and get the instance variables.
        write() -- Write instance variables to the file.

    Public instance variables:
        projectName -- str: URL-coded file name without suffix and extension. 
        projectPath -- str: URL-coded path to the project directory. 
        filePath -- str: path to the file (property with getter and setter). 

    Public class constants:
        PRJ_KWVAR -- List of the names of the project keyword variables.
        CHP_KWVAR -- List of the names of the chapter keyword variables.
        SCN_KWVAR -- List of the names of the scene keyword variables.
        CRT_KWVAR -- List of the names of the character keyword variables.
        LOC_KWVAR -- List of the names of the location keyword variables.
        ITM_KWVAR -- List of the names of the item keyword variables.
        PNT_KWVAR -- List of the names of the project note keyword variables.
    """
    DESCRIPTION = _('File')
    EXTENSION = None
    SUFFIX = None
    # To be extended by subclass methods.

    PRJ_KWVAR = []
    CHP_KWVAR = []
    SCN_KWVAR = []
    CRT_KWVAR = []
    LOC_KWVAR = []
    ITM_KWVAR = []
    PNT_KWVAR = []
    # Keyword variables for custom fields in the .yw7 XML file.

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.

        Positional arguments:
            filePath -- str: path to the file represented by the File instance.
            
        Optional arguments:
            kwargs -- keyword arguments to be used by subclasses.  
            
        Extends the superclass constructor.          
        """
        super().__init__()
        self.novel = None

        self._filePath = None
        # str
        # Path to the file. The setter only accepts files of a supported type as specified by EXTENSION.

        self.projectName = None
        # str
        # URL-coded file name without suffix and extension.

        self.projectPath = None
        # str
        # URL-coded path to the project directory.

        self.filePath = filePath

    @property
    def filePath(self):
        return self._filePath

    @filePath.setter
    def filePath(self, filePath):
        """Setter for the filePath instance variable.
                
        - Format the path string according to Python's requirements. 
        - Accept only filenames with the right suffix and extension.
        """
        if self.SUFFIX is not None:
            suffix = self.SUFFIX
        else:
            suffix = ''
        if filePath.lower().endswith(f'{suffix}{self.EXTENSION}'.lower()):
            self._filePath = filePath
            head, tail = os.path.split(os.path.realpath(filePath))
            self.projectPath = quote(head.replace('\\', '/'), '/:')
            self.projectName = quote(tail.replace(f'{suffix}{self.EXTENSION}', ''))

    def read(self):
        """Parse the file and get the instance variables.
        
        Raise the "Error" exception in case of error. 
        This is a stub to be overridden by subclass methods.
        """
        raise Error(f'Read method is not implemented.')

    def write(self):
        """Write instance variables to the file.
        
        Raise the "Error" exception in case of error. 
        This is a stub to be overridden by subclass methods.
        """
        raise Error(f'Write method is not implemented.')

    def _convert_to_yw(self, text):
        """Return text, converted from source format to yw7 markup.
        
        Positional arguments:
            text -- string to convert.
        
        This is a stub to be overridden by subclass methods.
        """
        return text.rstrip()

    def _convert_from_yw(self, text, quick=False):
        """Return text, converted from yw7 markup to target format.
        
        Positional arguments:
            text -- string to convert.
        
        Optional arguments:
            quick -- bool: if True, apply a conversion mode for one-liners without formatting.
        
        This is a stub to be overridden by subclass methods.
        """
        return text.rstrip()



def create_id(elements):
    """Return an unused ID for a new element.
    
    Positional arguments:
        elements -- list or dictionary containing all existing IDs
    """
    i = 1
    while str(i) in elements:
        i += 1
    return str(i)



def indent(elem, level=0):
    """xml pretty printer

    Kudos to to Fredrik Lundh. 
    Source: http://effbot.org/zone/element-lib.htm#prettyprint
    """
    i = f'\n{level * "  "}'
    if elem:
        if not elem.text or not elem.text.strip():
            elem.text = f'{i}  '
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


class Yw7File(File):
    """yWriter 7 project file representation.

    Public methods: 
        read() -- parse the yWriter xml file and get the instance variables.
        write() -- write instance variables to the yWriter xml file.
        is_locked() -- check whether the yw7 file is locked by yWriter.
        remove_custom_fields() -- Remove custom fields from the yWriter file.

    Public instance variables:
        tree -- xml element tree of the yWriter project
        scenesSplit -- bool: True, if a scene or chapter is split during merging.
        
    Public class constants:
        PRJ_KWVAR -- List of the names of the project keyword variables.
        SCN_KWVAR -- List of the names of the scene keyword variables.
    """
    DESCRIPTION = _('yWriter 7 project')
    EXTENSION = '.yw7'
    _CDATA_TAGS = ['Title', 'AuthorName', 'Bio', 'Desc',
                   'FieldTitle1', 'FieldTitle2', 'FieldTitle3',
                   'FieldTitle4', 'LaTeXHeaderFile', 'Tags',
                   'AKA', 'ImageFile', 'FullName', 'Goals',
                   'Notes', 'RTFFile', 'SceneContent',
                   'Outcome', 'Goal', 'Conflict']
    # Names of xml elements containing CDATA.
    # ElementTree.write omits CDATA tags, so they have to be inserted afterwards.

    PRJ_KWVAR = [
        'Field_LanguageCode',
        'Field_CountryCode',
        ]
    SCN_KWVAR = [
        'Field_SceneArcs',
        'Field_SceneStyle',
        ]

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.
        
        Positional arguments:
            filePath -- str: path to the yw7 file.
            
        Optional arguments:
            kwargs -- keyword arguments (not used here).            
        
        Extends the superclass constructor.
        """
        super().__init__(filePath)
        self.tree = None
        self.scenesSplit = False

    def read(self):
        """Parse the yWriter xml file and get the instance variables.
        
        Raise the "Error" exception in case of error. 
        Overrides the superclass method.
        """

        def read_project(root):
            #--- Read attributes at project level from the xml element tree.
            prj = root.find('PROJECT')

            if prj.find('Title') is not None:
                self.novel.title = prj.find('Title').text

            if prj.find('AuthorName') is not None:
                self.novel.authorName = prj.find('AuthorName').text

            if prj.find('Bio') is not None:
                self.novel.authorBio = prj.find('Bio').text

            if prj.find('Desc') is not None:
                self.novel.desc = prj.find('Desc').text

            if prj.find('FieldTitle1') is not None:
                self.novel.fieldTitle1 = prj.find('FieldTitle1').text

            if prj.find('FieldTitle2') is not None:
                self.novel.fieldTitle2 = prj.find('FieldTitle2').text

            if prj.find('FieldTitle3') is not None:
                self.novel.fieldTitle3 = prj.find('FieldTitle3').text

            if prj.find('FieldTitle4') is not None:
                self.novel.fieldTitle4 = prj.find('FieldTitle4').text

            #--- Read word target data.
            if prj.find('WordCountStart') is not None:
                try:
                    self.novel.wordCountStart = int(prj.find('WordCountStart').text)
                except:
                    self.novel.wordCountStart = 0
            if prj.find('WordTarget') is not None:
                try:
                    self.novel.wordTarget = int(prj.find('WordTarget').text)
                except:
                    self.novel.wordTarget = 0

            #--- Initialize custom keyword variables.
            for fieldName in self.PRJ_KWVAR:
                self.novel.kwVar[fieldName] = None

            #--- Read project custom fields.
            for prjFields in prj.findall('Fields'):
                for fieldName in self.PRJ_KWVAR:
                    field = prjFields.find(fieldName)
                    if field is not None:
                        self.novel.kwVar[fieldName] = field.text

            # This is for projects written with v7.6 - v7.10:
            if self.novel.kwVar['Field_LanguageCode']:
                self.novel.languageCode = self.novel.kwVar['Field_LanguageCode']
            if self.novel.kwVar['Field_CountryCode']:
                self.novel.countryCode = self.novel.kwVar['Field_CountryCode']

        def read_locations(root):
            #--- Read locations from the xml element tree.
            self.novel.srtLocations = []
            # This is necessary for re-reading.
            for loc in root.iter('LOCATION'):
                lcId = loc.find('ID').text
                self.novel.srtLocations.append(lcId)
                self.novel.locations[lcId] = WorldElement()

                if loc.find('Title') is not None:
                    self.novel.locations[lcId].title = loc.find('Title').text

                if loc.find('ImageFile') is not None:
                    self.novel.locations[lcId].image = loc.find('ImageFile').text

                if loc.find('Desc') is not None:
                    self.novel.locations[lcId].desc = loc.find('Desc').text

                if loc.find('AKA') is not None:
                    self.novel.locations[lcId].aka = loc.find('AKA').text

                if loc.find('Tags') is not None:
                    if loc.find('Tags').text is not None:
                        tags = string_to_list(loc.find('Tags').text)
                        self.novel.locations[lcId].tags = self._strip_spaces(tags)

                #--- Initialize custom keyword variables.
                for fieldName in self.LOC_KWVAR:
                    self.novel.locations[lcId].kwVar[fieldName] = None

                #--- Read location custom fields.
                for lcFields in loc.findall('Fields'):
                    for fieldName in self.LOC_KWVAR:
                        field = lcFields.find(fieldName)
                        if field is not None:
                            self.novel.locations[lcId].kwVar[fieldName] = field.text

        def read_items(root):
            #--- Read items from the xml element tree.
            self.novel.srtItems = []
            # This is necessary for re-reading.
            for itm in root.iter('ITEM'):
                itId = itm.find('ID').text
                self.novel.srtItems.append(itId)
                self.novel.items[itId] = WorldElement()

                if itm.find('Title') is not None:
                    self.novel.items[itId].title = itm.find('Title').text

                if itm.find('ImageFile') is not None:
                    self.novel.items[itId].image = itm.find('ImageFile').text

                if itm.find('Desc') is not None:
                    self.novel.items[itId].desc = itm.find('Desc').text

                if itm.find('AKA') is not None:
                    self.novel.items[itId].aka = itm.find('AKA').text

                if itm.find('Tags') is not None:
                    if itm.find('Tags').text is not None:
                        tags = string_to_list(itm.find('Tags').text)
                        self.novel.items[itId].tags = self._strip_spaces(tags)

                #--- Initialize custom keyword variables.
                for fieldName in self.ITM_KWVAR:
                    self.novel.items[itId].kwVar[fieldName] = None

                #--- Read item custom fields.
                for itFields in itm.findall('Fields'):
                    for fieldName in self.ITM_KWVAR:
                        field = itFields.find(fieldName)
                        if field is not None:
                            self.novel.items[itId].kwVar[fieldName] = field.text

        def read_characters(root):
            #--- Read characters from the xml element tree.
            self.novel.srtCharacters = []
            # This is necessary for re-reading.
            for crt in root.iter('CHARACTER'):
                crId = crt.find('ID').text
                self.novel.srtCharacters.append(crId)
                self.novel.characters[crId] = Character()

                if crt.find('Title') is not None:
                    self.novel.characters[crId].title = crt.find('Title').text

                if crt.find('ImageFile') is not None:
                    self.novel.characters[crId].image = crt.find('ImageFile').text

                if crt.find('Desc') is not None:
                    self.novel.characters[crId].desc = crt.find('Desc').text

                if crt.find('AKA') is not None:
                    self.novel.characters[crId].aka = crt.find('AKA').text

                if crt.find('Tags') is not None:
                    if crt.find('Tags').text is not None:
                        tags = string_to_list(crt.find('Tags').text)
                        self.novel.characters[crId].tags = self._strip_spaces(tags)

                if crt.find('Notes') is not None:
                    self.novel.characters[crId].notes = crt.find('Notes').text

                if crt.find('Bio') is not None:
                    self.novel.characters[crId].bio = crt.find('Bio').text

                if crt.find('Goals') is not None:
                    self.novel.characters[crId].goals = crt.find('Goals').text

                if crt.find('FullName') is not None:
                    self.novel.characters[crId].fullName = crt.find('FullName').text

                if crt.find('Major') is not None:
                    self.novel.characters[crId].isMajor = True
                else:
                    self.novel.characters[crId].isMajor = False

                #--- Initialize custom keyword variables.
                for fieldName in self.CRT_KWVAR:
                    self.novel.characters[crId].kwVar[fieldName] = None

                #--- Read character custom fields.
                for crFields in crt.findall('Fields'):
                    for fieldName in self.CRT_KWVAR:
                        field = crFields.find(fieldName)
                        if field is not None:
                            self.novel.characters[crId].kwVar[fieldName] = field.text

        def read_projectnotes(root):
            #--- Read project notes from the xml element tree.
            self.novel.srtPrjNotes = []
            # This is necessary for re-reading.

            try:
                for pnt in root.find('PROJECTNOTES'):
                    if pnt.find('ID') is not None:
                        pnId = pnt.find('ID').text
                        self.novel.srtPrjNotes.append(pnId)
                        self.novel.projectNotes[pnId] = BasicElement()
                        if pnt.find('Title') is not None:
                            self.novel.projectNotes[pnId].title = pnt.find('Title').text
                        if pnt.find('Desc') is not None:
                            self.novel.projectNotes[pnId].desc = pnt.find('Desc').text

                    #--- Initialize project note custom fields.
                    for fieldName in self.PNT_KWVAR:
                        self.novel.projectNotes[pnId].kwVar[fieldName] = None

                    #--- Read project note custom fields.
                    for pnFields in pnt.findall('Fields'):
                        field = pnFields.find(fieldName)
                        if field is not None:
                            self.novel.projectNotes[pnId].kwVar[fieldName] = field.text
            except:
                pass

        def read_projectvars(root):
            #--- Read relevant project variables from the xml element tree.
            try:
                for projectvar in root.find('PROJECTVARS'):
                    if projectvar.find('Title') is not None:
                        title = projectvar.find('Title').text
                        if title == 'Language':
                            if projectvar.find('Desc') is not None:
                                self.novel.languageCode = projectvar.find('Desc').text

                        elif title == 'Country':
                            if projectvar.find('Desc') is not None:
                                self.novel.countryCode = projectvar.find('Desc').text

                        elif title.startswith('lang='):
                            try:
                                __, langCode = title.split('=')
                                if self.novel.languages is None:
                                    self.novel.languages = []
                                self.novel.languages.append(langCode)
                            except:
                                pass
            except:
                pass

        def read_scenes(root):
            """ Read attributes at scene level from the xml element tree."""
            for scn in root.iter('SCENE'):
                scId = scn.find('ID').text
                self.novel.scenes[scId] = Scene()

                if scn.find('Title') is not None:
                    self.novel.scenes[scId].title = scn.find('Title').text

                if scn.find('Desc') is not None:
                    self.novel.scenes[scId].desc = scn.find('Desc').text

                if scn.find('SceneContent') is not None:
                    sceneContent = scn.find('SceneContent').text
                    if sceneContent is not None:
                        self.novel.scenes[scId].sceneContent = sceneContent

                #--- Read scene type.

                # This is how yWriter 7.1.3.0 reads the scene type:
                #
                # Type   |<Unused>|Field_SceneType>|scType
                #--------+--------+----------------+------
                # Notes  | x      | 1              | 1
                # Todo   | x      | 2              | 2
                # Unused | -1     | N/A            | 3
                # Unused | -1     | 0              | 3
                # Normal | N/A    | N/A            | 0
                # Normal | N/A    | 0              | 0

                self.novel.scenes[scId].scType = 0

                #--- Initialize custom keyword variables.
                for fieldName in self.SCN_KWVAR:
                    self.novel.scenes[scId].kwVar[fieldName] = None

                for scFields in scn.findall('Fields'):
                    #--- Read scene custom fields.
                    for fieldName in self.SCN_KWVAR:
                        field = scFields.find(fieldName)
                        if field is not None:
                            self.novel.scenes[scId].kwVar[fieldName] = field.text

                    # Read scene type, if any.
                    if scFields.find('Field_SceneType') is not None:
                        if scFields.find('Field_SceneType').text == '1':
                            self.novel.scenes[scId].scType = 1
                        elif scFields.find('Field_SceneType').text == '2':
                            self.novel.scenes[scId].scType = 2
                if scn.find('Unused') is not None:
                    if self.novel.scenes[scId].scType == 0:
                        self.novel.scenes[scId].scType = 3

                # Export when RTF.
                if scn.find('ExportCondSpecific') is None:
                    self.novel.scenes[scId].doNotExport = False
                elif scn.find('ExportWhenRTF') is not None:
                    self.novel.scenes[scId].doNotExport = False
                else:
                    self.novel.scenes[scId].doNotExport = True

                if scn.find('Status') is not None:
                    self.novel.scenes[scId].status = int(scn.find('Status').text)

                if scn.find('Notes') is not None:
                    self.novel.scenes[scId].notes = scn.find('Notes').text

                if scn.find('Tags') is not None:
                    if scn.find('Tags').text is not None:
                        tags = string_to_list(scn.find('Tags').text)
                        self.novel.scenes[scId].tags = self._strip_spaces(tags)

                if scn.find('Field1') is not None:
                    self.novel.scenes[scId].field1 = scn.find('Field1').text

                if scn.find('Field2') is not None:
                    self.novel.scenes[scId].field2 = scn.find('Field2').text

                if scn.find('Field3') is not None:
                    self.novel.scenes[scId].field3 = scn.find('Field3').text

                if scn.find('Field4') is not None:
                    self.novel.scenes[scId].field4 = scn.find('Field4').text

                if scn.find('AppendToPrev') is not None:
                    self.novel.scenes[scId].appendToPrev = True
                else:
                    self.novel.scenes[scId].appendToPrev = False

                #--- Scene start.
                if scn.find('SpecificDateTime') is not None:
                    dateTimeStr = scn.find('SpecificDateTime').text

                    # Check SpecificDateTime for ISO compliance.
                    try:
                        dateTime = datetime.fromisoformat(dateTimeStr)
                    except:
                        self.novel.scenes[scId].date = ''
                        self.novel.scenes[scId].time = ''
                    else:
                        startDateTime = dateTime.isoformat().split('T')
                        self.novel.scenes[scId].date = startDateTime[0]
                        self.novel.scenes[scId].time = startDateTime[1]
                else:
                    if scn.find('Day') is not None:
                        day = scn.find('Day').text

                        # Check if Day represents an integer.
                        try:
                            int(day)
                        except ValueError:
                            day = ''
                        self.novel.scenes[scId].day = day

                    hasUnspecificTime = False
                    if scn.find('Hour') is not None:
                        hour = scn.find('Hour').text.zfill(2)
                        hasUnspecificTime = True
                    else:
                        hour = '00'
                    if scn.find('Minute') is not None:
                        minute = scn.find('Minute').text.zfill(2)
                        hasUnspecificTime = True
                    else:
                        minute = '00'
                    if hasUnspecificTime:
                        self.novel.scenes[scId].time = f'{hour}:{minute}:00'

                #--- Scene duration.
                if scn.find('LastsDays') is not None:
                    self.novel.scenes[scId].lastsDays = scn.find('LastsDays').text

                if scn.find('LastsHours') is not None:
                    self.novel.scenes[scId].lastsHours = scn.find('LastsHours').text

                if scn.find('LastsMinutes') is not None:
                    self.novel.scenes[scId].lastsMinutes = scn.find('LastsMinutes').text

                if scn.find('ReactionScene') is not None:
                    self.novel.scenes[scId].isReactionScene = True
                else:
                    self.novel.scenes[scId].isReactionScene = False

                if scn.find('SubPlot') is not None:
                    self.novel.scenes[scId].isSubPlot = True
                else:
                    self.novel.scenes[scId].isSubPlot = False

                if scn.find('Goal') is not None:
                    self.novel.scenes[scId].goal = scn.find('Goal').text

                if scn.find('Conflict') is not None:
                    self.novel.scenes[scId].conflict = scn.find('Conflict').text

                if scn.find('Outcome') is not None:
                    self.novel.scenes[scId].outcome = scn.find('Outcome').text

                if scn.find('ImageFile') is not None:
                    self.novel.scenes[scId].image = scn.find('ImageFile').text

                if scn.find('Characters') is not None:
                    for characters in scn.find('Characters').iter('CharID'):
                        crId = characters.text
                        if crId in self.novel.srtCharacters:
                            if self.novel.scenes[scId].characters is None:
                                self.novel.scenes[scId].characters = []
                            self.novel.scenes[scId].characters.append(crId)

                if scn.find('Locations') is not None:
                    for locations in scn.find('Locations').iter('LocID'):
                        lcId = locations.text
                        if lcId in self.novel.srtLocations:
                            if self.novel.scenes[scId].locations is None:
                                self.novel.scenes[scId].locations = []
                            self.novel.scenes[scId].locations.append(lcId)

                if scn.find('Items') is not None:
                    for items in scn.find('Items').iter('ItemID'):
                        itId = items.text
                        if itId in self.novel.srtItems:
                            if self.novel.scenes[scId].items is None:
                                self.novel.scenes[scId].items = []
                            self.novel.scenes[scId].items.append(itId)

        def read_chapters(root):
            #--- Read attributes at chapter level from the xml element tree.
            self.novel.srtChapters = []
            # This is necessary for re-reading.
            for chp in root.iter('CHAPTER'):
                chId = chp.find('ID').text
                self.novel.chapters[chId] = Chapter()
                self.novel.srtChapters.append(chId)

                if chp.find('Title') is not None:
                    self.novel.chapters[chId].title = chp.find('Title').text

                if chp.find('Desc') is not None:
                    self.novel.chapters[chId].desc = chp.find('Desc').text

                if chp.find('SectionStart') is not None:
                    self.novel.chapters[chId].chLevel = 1
                else:
                    self.novel.chapters[chId].chLevel = 0

                # This is how yWriter 7.1.3.0 reads the chapter type:
                #
                # Type   |<Unused>|<Type>|<ChapterType>|chType
                # -------+--------+------+--------------------
                # Normal | N/A    | N/A  | N/A         | 0
                # Normal | N/A    | 0    | N/A         | 0
                # Notes  | x      | 1    | N/A         | 1
                # Unused | -1     | 0    | N/A         | 3
                # Normal | N/A    | x    | 0           | 0
                # Notes  | x      | x    | 1           | 1
                # Todo   | x      | x    | 2           | 2
                # Unused | -1     | x    | x           | 3

                self.novel.chapters[chId].chType = 0
                if chp.find('Unused') is not None:
                    yUnused = True
                else:
                    yUnused = False
                if chp.find('ChapterType') is not None:
                    # The file may be created with yWriter version 7.0.7.2+
                    yChapterType = chp.find('ChapterType').text
                    if yChapterType == '2':
                        self.novel.chapters[chId].chType = 2
                    elif yChapterType == '1':
                        self.novel.chapters[chId].chType = 1
                    elif yUnused:
                        self.novel.chapters[chId].chType = 3
                else:
                    # The file may be created with a yWriter version prior to 7.0.7.2
                    if chp.find('Type') is not None:
                        yType = chp.find('Type').text
                        if yType == '1':
                            self.novel.chapters[chId].chType = 1
                        elif yUnused:
                            self.novel.chapters[chId].chType = 3

                self.novel.chapters[chId].suppressChapterTitle = False
                if self.novel.chapters[chId].title is not None:
                    if self.novel.chapters[chId].title.startswith('@'):
                        self.novel.chapters[chId].suppressChapterTitle = True

                #--- Initialize custom keyword variables.
                for fieldName in self.CHP_KWVAR:
                    self.novel.chapters[chId].kwVar[fieldName] = None

                #--- Read chapter fields.
                for chFields in chp.findall('Fields'):
                    if chFields.find('Field_SuppressChapterTitle') is not None:
                        if chFields.find('Field_SuppressChapterTitle').text == '1':
                            self.novel.chapters[chId].suppressChapterTitle = True
                    self.novel.chapters[chId].isTrash = False
                    if chFields.find('Field_IsTrash') is not None:
                        if chFields.find('Field_IsTrash').text == '1':
                            self.novel.chapters[chId].isTrash = True
                    self.novel.chapters[chId].suppressChapterBreak = False
                    if chFields.find('Field_SuppressChapterBreak') is not None:
                        if chFields.find('Field_SuppressChapterBreak').text == '1':
                            self.novel.chapters[chId].suppressChapterBreak = True

                    #--- Read chapter custom fields.
                    for fieldName in self.CHP_KWVAR:
                        field = chFields.find(fieldName)
                        if field is not None:
                            self.novel.chapters[chId].kwVar[fieldName] = field.text

                #--- Read chapter's scene list.
                self.novel.chapters[chId].srtScenes = []
                if chp.find('Scenes') is not None:
                    for scn in chp.find('Scenes').findall('ScID'):
                        scId = scn.text
                        if scId in self.novel.scenes:
                            self.novel.chapters[chId].srtScenes.append(scId)

        #--- Begin reading.
        for field in self.PRJ_KWVAR:
            self.novel.kwVar[field] = None

        if self.is_locked():
            raise Error(f'{_("yWriter seems to be open. Please close first")}.')
        try:
            self.tree = ET.parse(self.filePath)
        except:
            raise Error(f'{_("Can not process file")}: "{norm_path(self.filePath)}".')

        root = self.tree.getroot()
        read_project(root)
        read_locations(root)
        read_items(root)
        read_characters(root)
        read_projectvars(root)
        read_projectnotes(root)
        read_scenes(root)
        read_chapters(root)
        self.adjust_scene_types()

        #--- Set custom instance variables.
        for scId in self.novel.scenes:
            self.novel.scenes[scId].scnArcs = self.novel.scenes[scId].kwVar.get('Field_SceneArcs', None)
            self.novel.scenes[scId].scnStyle = self.novel.scenes[scId].kwVar.get('Field_SceneStyle', None)

    def write(self):
        """Write instance variables to the yWriter xml file.
        
        Open the yWriter xml file located at filePath and replace the instance variables 
        not being None. Create new XML elements if necessary.
        Raise the "Error" exception in case of error. 
        Overrides the superclass method.
        """
        if self.is_locked():
            raise Error(f'{_("yWriter seems to be open. Please close first")}.')

        if self.novel.languages is None:
            self.novel.get_languages()

        #--- Get custom instance variables.
        for scId in self.novel.scenes:
            if self.novel.scenes[scId].scnArcs is not None:
                self.novel.scenes[scId].kwVar['Field_SceneArcs'] = self.novel.scenes[scId].scnArcs
            if self.novel.scenes[scId].scnStyle is not None:
                self.novel.scenes[scId].kwVar['Field_SceneStyle'] = self.novel.scenes[scId].scnStyle

        self._build_element_tree()
        self._write_element_tree(self)
        self._postprocess_xml_file(self.filePath)

    def is_locked(self):
        """Check whether the yw7 file is locked by yWriter.
        
        Return True if a .lock file placed by yWriter exists.
        Otherwise, return False. 
        """
        return os.path.isfile(f'{self.filePath}.lock')

    def _build_element_tree(self):
        """Modify the yWriter project attributes of an existing xml element tree."""

        def set_element(parent, tag, text, index):
            subelement = parent.find(tag)
            if subelement is None:
                if text is not None:
                    subelement = ET.Element(tag)
                    parent.insert(index, subelement)
                    subelement.text = text
                    index += 1
            elif text is not None:
                subelement.text = text
                index += 1
            return index

        def build_scene_subtree(xmlScn, prjScn):

            def remove_date_time():
                """Delete all scene start data."""
                if xmlScn.find('SpecificDateTime') is not None:
                    xmlScn.remove(xmlScn.find('SpecificDateTime'))

                if xmlScn.find('SpecificDateMode') is not None:
                    xmlScn.remove(xmlScn.find('SpecificDateMode'))

                if xmlScn.find('Day') is not None:
                    xmlScn.remove(xmlScn.find('Day'))

                if xmlScn.find('Hour') is not None:
                    xmlScn.remove(xmlScn.find('Hour'))

                if xmlScn.find('Minute') is not None:
                    xmlScn.remove(xmlScn.find('Minute'))

            i = 1
            i = set_element(xmlScn, 'Title', prjScn.title, i)

            if xmlScn.find('BelongsToChID') is None:
                for chId in self.novel.chapters:
                    if scId in self.novel.chapters[chId].srtScenes:
                        ET.SubElement(xmlScn, 'BelongsToChID').text = chId
                        break

            if prjScn.desc is not None:
                try:
                    xmlScn.find('Desc').text = prjScn.desc
                except(AttributeError):
                    if prjScn.desc:
                        ET.SubElement(xmlScn, 'Desc').text = prjScn.desc

            if xmlScn.find('SceneContent') is None:
                ET.SubElement(xmlScn, 'SceneContent').text = prjScn.sceneContent

            if xmlScn.find('WordCount') is None:
                ET.SubElement(xmlScn, 'WordCount').text = str(prjScn.wordCount)

            if xmlScn.find('LetterCount') is None:
                ET.SubElement(xmlScn, 'LetterCount').text = str(prjScn.letterCount)

            #--- Write scene type.
            #
            # This is how yWriter 7.1.3.0 writes the scene type:
            #
            # Type   |<Unused>|Field_SceneType>|scType
            #--------+--------+----------------+------
            # Normal | N/A    | N/A            | 0
            # Notes  | -1     | 1              | 1
            # Todo   | -1     | 2              | 2
            # Unused | -1     | 0              | 3

            scTypeEncoding = (
                (False, None),
                (True, '1'),
                (True, '2'),
                (True, '0'),
                )
            if prjScn.scType is None:
                prjScn.scType = 0
            yUnused, ySceneType = scTypeEncoding[prjScn.scType]

            # <Unused> (remove, if scene is "Normal").
            if yUnused:
                if xmlScn.find('Unused') is None:
                    ET.SubElement(xmlScn, 'Unused').text = '-1'
            elif xmlScn.find('Unused') is not None:
                xmlScn.remove(xmlScn.find('Unused'))

            # <Fields><Field_SceneType> (remove, if scene is "Normal")
            scFields = xmlScn.find('Fields')
            if scFields is not None:
                fieldScType = scFields.find('Field_SceneType')
                if ySceneType is None:
                    if fieldScType is not None:
                        scFields.remove(fieldScType)
                else:
                    try:
                        fieldScType.text = ySceneType
                    except(AttributeError):
                        ET.SubElement(scFields, 'Field_SceneType').text = ySceneType
            elif ySceneType is not None:
                scFields = ET.SubElement(xmlScn, 'Fields')
                ET.SubElement(scFields, 'Field_SceneType').text = ySceneType

            #--- Write scene custom fields.
            for field in self.SCN_KWVAR:
                if self.novel.scenes[scId].kwVar.get(field, None):
                    if scFields is None:
                        scFields = ET.SubElement(xmlScn, 'Fields')
                    try:
                        scFields.find(field).text = self.novel.scenes[scId].kwVar[field]
                    except(AttributeError):
                        ET.SubElement(scFields, field).text = self.novel.scenes[scId].kwVar[field]
                elif scFields is not None:
                    try:
                        scFields.remove(scFields.find(field))
                    except:
                        pass

            if prjScn.status is not None:
                try:
                    xmlScn.find('Status').text = str(prjScn.status)
                except:
                    ET.SubElement(xmlScn, 'Status').text = str(prjScn.status)

            if prjScn.notes is not None:
                try:
                    xmlScn.find('Notes').text = prjScn.notes
                except(AttributeError):
                    if prjScn.notes:
                        ET.SubElement(xmlScn, 'Notes').text = prjScn.notes

            if prjScn.tags is not None:
                try:
                    xmlScn.find('Tags').text = list_to_string(prjScn.tags)
                except(AttributeError):
                    if prjScn.tags:
                        ET.SubElement(xmlScn, 'Tags').text = list_to_string(prjScn.tags)

            if prjScn.field1 is not None:
                try:
                    xmlScn.find('Field1').text = prjScn.field1
                except(AttributeError):
                    if prjScn.field1:
                        ET.SubElement(xmlScn, 'Field1').text = prjScn.field1

            if prjScn.field2 is not None:
                try:
                    xmlScn.find('Field2').text = prjScn.field2
                except(AttributeError):
                    if prjScn.field2:
                        ET.SubElement(xmlScn, 'Field2').text = prjScn.field2

            if prjScn.field3 is not None:
                try:
                    xmlScn.find('Field3').text = prjScn.field3
                except(AttributeError):
                    if prjScn.field3:
                        ET.SubElement(xmlScn, 'Field3').text = prjScn.field3

            if prjScn.field4 is not None:
                try:
                    xmlScn.find('Field4').text = prjScn.field4
                except(AttributeError):
                    if prjScn.field4:
                        ET.SubElement(xmlScn, 'Field4').text = prjScn.field4

            if prjScn.appendToPrev:
                if xmlScn.find('AppendToPrev') is None:
                    ET.SubElement(xmlScn, 'AppendToPrev').text = '-1'
            elif xmlScn.find('AppendToPrev') is not None:
                xmlScn.remove(xmlScn.find('AppendToPrev'))

            #--- Write scene start.
            if (prjScn.date is not None) and (prjScn.time is not None):
                separator = ' '
                dateTime = f'{prjScn.date}{separator}{prjScn.time}'

                # Remove scene start data from XML, if date and time are empty strings.
                if dateTime == separator:
                    remove_date_time()

                elif xmlScn.find('SpecificDateTime') is not None:
                    if dateTime.count(':') < 2:
                        dateTime = f'{dateTime}:00'
                    xmlScn.find('SpecificDateTime').text = dateTime
                else:
                    ET.SubElement(xmlScn, 'SpecificDateTime').text = dateTime
                    ET.SubElement(xmlScn, 'SpecificDateMode').text = '-1'

                    if xmlScn.find('Day') is not None:
                        xmlScn.remove(xmlScn.find('Day'))

                    if xmlScn.find('Hour') is not None:
                        xmlScn.remove(xmlScn.find('Hour'))

                    if xmlScn.find('Minute') is not None:
                        xmlScn.remove(xmlScn.find('Minute'))

            elif (prjScn.day is not None) or (prjScn.time is not None):

                # Remove scene start data from XML, if day and time are empty strings.
                if not prjScn.day and not prjScn.time:
                    remove_date_time()

                else:
                    if xmlScn.find('SpecificDateTime') is not None:
                        xmlScn.remove(xmlScn.find('SpecificDateTime'))

                    if xmlScn.find('SpecificDateMode') is not None:
                        xmlScn.remove(xmlScn.find('SpecificDateMode'))
                    if prjScn.day is not None:
                        try:
                            xmlScn.find('Day').text = prjScn.day
                        except(AttributeError):
                            ET.SubElement(xmlScn, 'Day').text = prjScn.day
                    if prjScn.time is not None:
                        hours, minutes, seconds = prjScn.time.split(':')
                        try:
                            xmlScn.find('Hour').text = hours
                        except(AttributeError):
                            ET.SubElement(xmlScn, 'Hour').text = hours
                        try:
                            xmlScn.find('Minute').text = minutes
                        except(AttributeError):
                            ET.SubElement(xmlScn, 'Minute').text = minutes

            #--- Write scene duration.
            if prjScn.lastsDays is not None:
                try:
                    xmlScn.find('LastsDays').text = prjScn.lastsDays
                except(AttributeError):
                    if prjScn.lastsDays:
                        ET.SubElement(xmlScn, 'LastsDays').text = prjScn.lastsDays

            if prjScn.lastsHours is not None:
                try:
                    xmlScn.find('LastsHours').text = prjScn.lastsHours
                except(AttributeError):
                    if prjScn.lastsHours:
                        ET.SubElement(xmlScn, 'LastsHours').text = prjScn.lastsHours

            if prjScn.lastsMinutes is not None:
                try:
                    xmlScn.find('LastsMinutes').text = prjScn.lastsMinutes
                except(AttributeError):
                    if prjScn.lastsMinutes:
                        ET.SubElement(xmlScn, 'LastsMinutes').text = prjScn.lastsMinutes

            # Plot related information
            if prjScn.isReactionScene:
                if xmlScn.find('ReactionScene') is None:
                    ET.SubElement(xmlScn, 'ReactionScene').text = '-1'
            elif xmlScn.find('ReactionScene') is not None:
                xmlScn.remove(xmlScn.find('ReactionScene'))

            if prjScn.isSubPlot:
                if xmlScn.find('SubPlot') is None:
                    ET.SubElement(xmlScn, 'SubPlot').text = '-1'
            elif xmlScn.find('SubPlot') is not None:
                xmlScn.remove(xmlScn.find('SubPlot'))

            if prjScn.goal is not None:
                try:
                    xmlScn.find('Goal').text = prjScn.goal
                except(AttributeError):
                    if prjScn.goal:
                        ET.SubElement(xmlScn, 'Goal').text = prjScn.goal

            if prjScn.conflict is not None:
                try:
                    xmlScn.find('Conflict').text = prjScn.conflict
                except(AttributeError):
                    if prjScn.conflict:
                        ET.SubElement(xmlScn, 'Conflict').text = prjScn.conflict

            if prjScn.outcome is not None:
                try:
                    xmlScn.find('Outcome').text = prjScn.outcome
                except(AttributeError):
                    if prjScn.outcome:
                        ET.SubElement(xmlScn, 'Outcome').text = prjScn.outcome

            if prjScn.image is not None:
                try:
                    xmlScn.find('ImageFile').text = prjScn.image
                except(AttributeError):
                    if prjScn.image:
                        ET.SubElement(xmlScn, 'ImageFile').text = prjScn.image

            #--- Characters/locations/items
            if prjScn.characters is not None:
                characters = xmlScn.find('Characters')
                try:
                    for oldCrId in characters.findall('CharID'):
                        characters.remove(oldCrId)
                except(AttributeError):
                    characters = ET.SubElement(xmlScn, 'Characters')
                for crId in prjScn.characters:
                    ET.SubElement(characters, 'CharID').text = crId

            if prjScn.locations is not None:
                locations = xmlScn.find('Locations')
                try:
                    for oldLcId in locations.findall('LocID'):
                        locations.remove(oldLcId)
                except(AttributeError):
                    locations = ET.SubElement(xmlScn, 'Locations')
                for lcId in prjScn.locations:
                    ET.SubElement(locations, 'LocID').text = lcId

            if prjScn.items is not None:
                items = xmlScn.find('Items')
                try:
                    for oldItId in items.findall('ItemID'):
                        items.remove(oldItId)
                except(AttributeError):
                    items = ET.SubElement(xmlScn, 'Items')
                for itId in prjScn.items:
                    ET.SubElement(items, 'ItemID').text = itId

            ''' Removing empty characters/locations/items entries
            
            if prjScn.characters is not None:
                characters = xmlScn.find('Characters')
                if characters is not None:
                    for oldCrId in characters.findall('CharID'):
                        characters.remove(oldCrId)
                if prjScn.characters:
                    if characters is None:
                        characters = ET.SubElement(xmlScn, 'Characters')
                    for crId in prjScn.characters:
                        ET.SubElement(characters, 'CharID').text = crId
                elif characters is not None:
                    xmlScn.remove(xmlScn.find('Characters'))

            if prjScn.locations is not None:
                locations = xmlScn.find('Locations')
                if locations is not None:
                    for oldLcId in locations.findall('LocID'):
                        locations.remove(oldLcId)
                if prjScn.locations:
                    if locations is None:
                        locations = ET.SubElement(xmlScn, 'Locations')
                    for lcId in prjScn.locations:
                        ET.SubElement(locations, 'LocID').text = lcId
                elif locations is not None:
                    xmlScn.remove(xmlScn.find('Locations'))

            if prjScn.items is not None:
                items = xmlScn.find('Items')
                if items is not None:
                    for oldItId in items.findall('ItemID'):
                        items.remove(oldItId)
                if prjScn.items:
                    if items is None:
                        items = ET.SubElement(xmlScn, 'Items')
                    for itId in prjScn.items:
                        ET.SubElement(items, 'ItemID').text = itId
                elif items is not None:
                    xmlScn.remove(xmlScn.find('Items'))
            '''

        def build_chapter_subtree(xmlChp, prjChp, sortOrder):
            # This is how yWriter 7.1.3.0 writes the chapter type:
            #
            # Type   |<Unused>|<Type>|<ChapterType>|chType
            #--------+--------+------+-------------+------
            # Normal | N/A    | 0    | 0           | 0
            # Notes  | -1     | 1    | 1           | 1
            # Todo   | -1     | 1    | 2           | 2
            # Unused | -1     | 1    | 0           | 3

            chTypeEncoding = (
                (False, '0', '0'),
                (True, '1', '1'),
                (True, '1', '2'),
                (True, '1', '0'),
                )
            if prjChp.chType is None:
                prjChp.chType = 0
            yUnused, yType, yChapterType = chTypeEncoding[prjChp.chType]

            i = 1
            i = set_element(xmlChp, 'Title', prjChp.title, i)
            i = set_element(xmlChp, 'Desc', prjChp.desc, i)

            if yUnused:
                if xmlChp.find('Unused') is None:
                    elem = ET.Element('Unused')
                    elem.text = '-1'
                    xmlChp.insert(i, elem)
            elif xmlChp.find('Unused') is not None:
                xmlChp.remove(xmlChp.find('Unused'))
            if xmlChp.find('Unused') is not None:
                i += 1

            i = set_element(xmlChp, 'SortOrder', str(sortOrder), i)

            #--- Write chapter fields.
            chFields = xmlChp.find('Fields')
            if prjChp.suppressChapterTitle:
                if chFields is None:
                    chFields = ET.Element('Fields')
                    xmlChp.insert(i, chFields)
                try:
                    chFields.find('Field_SuppressChapterTitle').text = '1'
                except(AttributeError):
                    ET.SubElement(chFields, 'Field_SuppressChapterTitle').text = '1'
            elif chFields is not None:
                if chFields.find('Field_SuppressChapterTitle') is not None:
                    chFields.find('Field_SuppressChapterTitle').text = '0'

            if prjChp.suppressChapterBreak:
                if chFields is None:
                    chFields = ET.Element('Fields')
                    xmlChp.insert(i, chFields)
                try:
                    chFields.find('Field_SuppressChapterBreak').text = '1'
                except(AttributeError):
                    ET.SubElement(chFields, 'Field_SuppressChapterBreak').text = '1'
            elif chFields is not None:
                if chFields.find('Field_SuppressChapterBreak') is not None:
                    chFields.find('Field_SuppressChapterBreak').text = '0'

            if prjChp.isTrash:
                if chFields is None:
                    chFields = ET.Element('Fields')
                    xmlChp.insert(i, chFields)
                try:
                    chFields.find('Field_IsTrash').text = '1'
                except(AttributeError):
                    ET.SubElement(chFields, 'Field_IsTrash').text = '1'

            elif chFields is not None:
                if chFields.find('Field_IsTrash') is not None:
                    chFields.remove(chFields.find('Field_IsTrash'))

            #--- Write chapter custom fields.
            for field in self.CHP_KWVAR:
                if prjChp.kwVar.get(field, None):
                    if chFields is None:
                        chFields = ET.Element('Fields')
                        xmlChp.insert(i, chFields)
                    try:
                        chFields.find(field).text = prjChp.kwVar[field]
                    except(AttributeError):
                        ET.SubElement(chFields, field).text = prjChp.kwVar[field]
                elif chFields is not None:
                    try:
                        chFields.remove(chFields.find(field))
                    except:
                        pass
            if xmlChp.find('Fields') is not None:
                i += 1

            if xmlChp.find('SectionStart') is not None:
                if prjChp.chLevel == 0:
                    xmlChp.remove(xmlChp.find('SectionStart'))
            elif prjChp.chLevel == 1:
                elem = ET.Element('SectionStart')
                elem.text = '-1'
                xmlChp.insert(i, elem)
            if xmlChp.find('SectionStart') is not None:
                i += 1

            i = set_element(xmlChp, 'Type', yType, i)
            i = set_element(xmlChp, 'ChapterType', yChapterType, i)

            #--- Rebuild the chapter's scene list.
            xmlScnList = xmlChp.find('Scenes')

            # Remove the Scenes section.
            if xmlScnList is not None:
                xmlChp.remove(xmlScnList)

            # Rebuild the Scenes section in a modified sort order.
            if prjChp.srtScenes:
                xmlScnList = ET.Element('Scenes')
                xmlChp.insert(i, xmlScnList)
                for scId in prjChp.srtScenes:
                    ET.SubElement(xmlScnList, 'ScID').text = scId

        def build_location_subtree(xmlLoc, prjLoc, sortOrder):
            if prjLoc.title is not None:
                ET.SubElement(xmlLoc, 'Title').text = prjLoc.title

            if prjLoc.image is not None:
                ET.SubElement(xmlLoc, 'ImageFile').text = prjLoc.image

            if prjLoc.desc is not None:
                ET.SubElement(xmlLoc, 'Desc').text = prjLoc.desc

            if prjLoc.aka is not None:
                ET.SubElement(xmlLoc, 'AKA').text = prjLoc.aka

            if prjLoc.tags is not None:
                ET.SubElement(xmlLoc, 'Tags').text = list_to_string(prjLoc.tags)

            ET.SubElement(xmlLoc, 'SortOrder').text = str(sortOrder)

            #--- Write location custom fields.
            lcFields = xmlLoc.find('Fields')
            for field in self.LOC_KWVAR:
                if self.novel.locations[lcId].kwVar.get(field, None):
                    if lcFields is None:
                        lcFields = ET.SubElement(xmlLoc, 'Fields')
                    try:
                        lcFields.find(field).text = self.novel.locations[lcId].kwVar[field]
                    except(AttributeError):
                        ET.SubElement(lcFields, field).text = self.novel.locations[lcId].kwVar[field]
                elif lcFields is not None:
                    try:
                        lcFields.remove(lcFields.find(field))
                    except:
                        pass

        def build_prjNote_subtree(xmlPnt, prjPnt, sortOrder):
            if prjPnt.title is not None:
                ET.SubElement(xmlPnt, 'Title').text = prjPnt.title

            if prjPnt.desc is not None:
                ET.SubElement(xmlPnt, 'Desc').text = prjPnt.desc

            ET.SubElement(xmlPnt, 'SortOrder').text = str(sortOrder)

        def add_projectvariable(title, desc, tags):
            # Note:
            # prjVars, projectvars are caller's variables
            pvId = create_id(prjVars)
            prjVars.append(pvId)
            # side effect
            projectvar = ET.SubElement(projectvars, 'PROJECTVAR')
            ET.SubElement(projectvar, 'ID').text = pvId
            ET.SubElement(projectvar, 'Title').text = title
            ET.SubElement(projectvar, 'Desc').text = desc
            ET.SubElement(projectvar, 'Tags').text = tags

        def build_item_subtree(xmlItm, prjItm, sortOrder):
            if prjItm.title is not None:
                ET.SubElement(xmlItm, 'Title').text = prjItm.title

            if prjItm.image is not None:
                ET.SubElement(xmlItm, 'ImageFile').text = prjItm.image

            if prjItm.desc is not None:
                ET.SubElement(xmlItm, 'Desc').text = prjItm.desc

            if prjItm.aka is not None:
                ET.SubElement(xmlItm, 'AKA').text = prjItm.aka

            if prjItm.tags is not None:
                ET.SubElement(xmlItm, 'Tags').text = list_to_string(prjItm.tags)

            ET.SubElement(xmlItm, 'SortOrder').text = str(sortOrder)

            #--- Write item custom fields.
            itFields = xmlItm.find('Fields')
            for field in self.ITM_KWVAR:
                if self.novel.items[itId].kwVar.get(field, None):
                    if itFields is None:
                        itFields = ET.SubElement(xmlItm, 'Fields')
                    try:
                        itFields.find(field).text = self.novel.items[itId].kwVar[field]
                    except(AttributeError):
                        ET.SubElement(itFields, field).text = self.novel.items[itId].kwVar[field]
                elif itFields is not None:
                    try:
                        itFields.remove(itFields.find(field))
                    except:
                        pass

        def build_character_subtree(xmlCrt, prjCrt, sortOrder):
            if prjCrt.title is not None:
                ET.SubElement(xmlCrt, 'Title').text = prjCrt.title

            if prjCrt.desc is not None:
                ET.SubElement(xmlCrt, 'Desc').text = prjCrt.desc

            if prjCrt.image is not None:
                ET.SubElement(xmlCrt, 'ImageFile').text = prjCrt.image

            ET.SubElement(xmlCrt, 'SortOrder').text = str(sortOrder)

            if prjCrt.notes is not None:
                ET.SubElement(xmlCrt, 'Notes').text = prjCrt.notes

            if prjCrt.aka is not None:
                ET.SubElement(xmlCrt, 'AKA').text = prjCrt.aka

            if prjCrt.tags is not None:
                ET.SubElement(xmlCrt, 'Tags').text = list_to_string(prjCrt.tags)

            if prjCrt.bio is not None:
                ET.SubElement(xmlCrt, 'Bio').text = prjCrt.bio

            if prjCrt.goals is not None:
                ET.SubElement(xmlCrt, 'Goals').text = prjCrt.goals

            if prjCrt.fullName is not None:
                ET.SubElement(xmlCrt, 'FullName').text = prjCrt.fullName

            if prjCrt.isMajor:
                ET.SubElement(xmlCrt, 'Major').text = '-1'

            #--- Write character custom fields.
            crFields = xmlCrt.find('Fields')
            for field in self.CRT_KWVAR:
                if self.novel.characters[crId].kwVar.get(field, None):
                    if crFields is None:
                        crFields = ET.SubElement(xmlCrt, 'Fields')
                    try:
                        crFields.find(field).text = self.novel.characters[crId].kwVar[field]
                    except(AttributeError):
                        ET.SubElement(crFields, field).text = self.novel.characters[crId].kwVar[field]
                elif crFields is not None:
                    try:
                        crFields.remove(crFields.find(field))
                    except:
                        pass

        def build_project_subtree(xmlPrj):
            VER = '7'
            try:
                xmlPrj.find('Ver').text = VER
            except(AttributeError):
                ET.SubElement(xmlPrj, 'Ver').text = VER

            if self.novel.title is not None:
                try:
                    xmlPrj.find('Title').text = self.novel.title
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'Title').text = self.novel.title

            if self.novel.desc is not None:
                try:
                    xmlPrj.find('Desc').text = self.novel.desc
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'Desc').text = self.novel.desc

            if self.novel.authorName is not None:
                try:
                    xmlPrj.find('AuthorName').text = self.novel.authorName
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'AuthorName').text = self.novel.authorName

            if self.novel.authorBio is not None:
                try:
                    xmlPrj.find('Bio').text = self.novel.authorBio
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'Bio').text = self.novel.authorBio

            if self.novel.fieldTitle1 is not None:
                try:
                    xmlPrj.find('FieldTitle1').text = self.novel.fieldTitle1
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'FieldTitle1').text = self.novel.fieldTitle1

            if self.novel.fieldTitle2 is not None:
                try:
                    xmlPrj.find('FieldTitle2').text = self.novel.fieldTitle2
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'FieldTitle2').text = self.novel.fieldTitle2

            if self.novel.fieldTitle3 is not None:
                try:
                    xmlPrj.find('FieldTitle3').text = self.novel.fieldTitle3
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'FieldTitle3').text = self.novel.fieldTitle3

            if self.novel.fieldTitle4 is not None:
                try:
                    xmlPrj.find('FieldTitle4').text = self.novel.fieldTitle4
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'FieldTitle4').text = self.novel.fieldTitle4

            #--- Write word target data.
            if self.novel.wordCountStart is not None:
                try:
                    xmlPrj.find('WordCountStart').text = str(self.novel.wordCountStart)
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'WordCountStart').text = str(self.novel.wordCountStart)

            if self.novel.wordTarget is not None:
                try:
                    xmlPrj.find('WordTarget').text = str(self.novel.wordTarget)
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'WordTarget').text = str(self.novel.wordTarget)

            #--- Write project custom fields.

            # This is for projects written with v7.6 - v7.10:
            self.novel.kwVar['Field_LanguageCode'] = None
            self.novel.kwVar['Field_CountryCode'] = None

            prjFields = xmlPrj.find('Fields')
            for field in self.PRJ_KWVAR:
                setting = self.novel.kwVar.get(field, None)
                if setting:
                    if prjFields is None:
                        prjFields = ET.SubElement(xmlPrj, 'Fields')
                    try:
                        prjFields.find(field).text = setting
                    except(AttributeError):
                        ET.SubElement(prjFields, field).text = setting
                else:
                    try:
                        prjFields.remove(prjFields.find(field))
                    except:
                        pass

        TAG = 'YWRITER7'
        xmlScenes = {}
        xmlChapters = {}
        try:
            # Try processing an existing tree.
            root = self.tree.getroot()
            xmlPrj = root.find('PROJECT')
            locations = root.find('LOCATIONS')
            items = root.find('ITEMS')
            characters = root.find('CHARACTERS')
            prjNotes = root.find('PROJECTNOTES')
            scenes = root.find('SCENES')
            chapters = root.find('CHAPTERS')
        except(AttributeError):
            # Build a new tree.
            root = ET.Element(TAG)
            xmlPrj = ET.SubElement(root, 'PROJECT')
            locations = ET.SubElement(root, 'LOCATIONS')
            items = ET.SubElement(root, 'ITEMS')
            characters = ET.SubElement(root, 'CHARACTERS')
            prjNotes = ET.SubElement(root, 'PROJECTNOTES')
            scenes = ET.SubElement(root, 'SCENES')
            chapters = ET.SubElement(root, 'CHAPTERS')

        #--- Process project attributes.

        build_project_subtree(xmlPrj)

        #--- Process locations.

        # Remove LOCATION entries in order to rewrite
        # the LOCATIONS section in a modified sort order.
        for xmlLoc in locations.findall('LOCATION'):
            locations.remove(xmlLoc)

        # Add the new XML location subtrees to the project tree.
        sortOrder = 0
        for lcId in self.novel.srtLocations:
            sortOrder += 1
            xmlLoc = ET.SubElement(locations, 'LOCATION')
            ET.SubElement(xmlLoc, 'ID').text = lcId
            build_location_subtree(xmlLoc, self.novel.locations[lcId], sortOrder)

        #--- Process items.

        # Remove ITEM entries in order to rewrite
        # the ITEMS section in a modified sort order.
        for xmlItm in items.findall('ITEM'):
            items.remove(xmlItm)

        # Add the new XML item subtrees to the project tree.
        sortOrder = 0
        for itId in self.novel.srtItems:
            sortOrder += 1
            xmlItm = ET.SubElement(items, 'ITEM')
            ET.SubElement(xmlItm, 'ID').text = itId
            build_item_subtree(xmlItm, self.novel.items[itId], sortOrder)

        #--- Process characters.

        # Remove CHARACTER entries in order to rewrite
        # the CHARACTERS section in a modified sort order.
        for xmlCrt in characters.findall('CHARACTER'):
            characters.remove(xmlCrt)

        # Add the new XML character subtrees to the project tree.
        sortOrder = 0
        for crId in self.novel.srtCharacters:
            sortOrder += 1
            xmlCrt = ET.SubElement(characters, 'CHARACTER')
            ET.SubElement(xmlCrt, 'ID').text = crId
            build_character_subtree(xmlCrt, self.novel.characters[crId], sortOrder)

        #--- Process project notes.

        # Remove PROJECTNOTE entries in order to rewrite
        # the PROJECTNOTES section in a modified sort order.
        if prjNotes is not None:
            for xmlPnt in prjNotes.findall('PROJECTNOTE'):
                prjNotes.remove(xmlPnt)
            if not self.novel.srtPrjNotes:
                root.remove(prjNotes)
        elif self.novel.srtPrjNotes:
            prjNotes = ET.SubElement(root, 'PROJECTNOTES')
        if self.novel.srtPrjNotes:
            # Add the new XML prjNote subtrees to the project tree.
            sortOrder = 0
            for pnId in self.novel.srtPrjNotes:
                sortOrder += 1
                xmlPnt = ET.SubElement(prjNotes, 'PROJECTNOTE')
                ET.SubElement(xmlPnt, 'ID').text = pnId
                build_prjNote_subtree(xmlPnt, self.novel.projectNotes[pnId], sortOrder)

        #--- Process project variables.
        if self.novel.languages or self.novel.languageCode or self.novel.countryCode:
            self.novel.check_locale()
            projectvars = root.find('PROJECTVARS')
            if projectvars is None:
                projectvars = ET.SubElement(root, 'PROJECTVARS')
            prjVars = []
            # list of all project variable IDs
            languages = self.novel.languages.copy()
            hasLanguageCode = False
            hasCountryCode = False
            for projectvar in projectvars.findall('PROJECTVAR'):
                prjVars.append(projectvar.find('ID').text)
                title = projectvar.find('Title').text

                # Collect language codes.
                if title.startswith('lang='):
                    try:
                        __, langCode = title.split('=')
                        languages.remove(langCode)
                    except:
                        pass

                # Get the document's locale.
                elif title == 'Language':
                    projectvar.find('Desc').text = self.novel.languageCode
                    hasLanguageCode = True

                elif title == 'Country':
                    projectvar.find('Desc').text = self.novel.countryCode
                    hasCountryCode = True

            # Define project variables for the missing locale.
            if not hasLanguageCode:
                add_projectvariable('Language',
                                    self.novel.languageCode,
                                    '0')

            if not hasCountryCode:
                add_projectvariable('Country',
                                    self.novel.countryCode,
                                    '0')

            # Define project variables for the missing language code tags.
            for langCode in languages:
                add_projectvariable(f'lang={langCode}',
                                    f'<HTM <SPAN LANG="{langCode}"> /HTM>',
                                    '0')
                add_projectvariable(f'/lang={langCode}',
                                    f'<HTM </SPAN> /HTM>',
                                    '0')
                # adding new IDs to the prjVars list

        #--- Process scenes.

        # Save the original XML scene subtrees
        # and remove them from the project tree.
        for xmlScn in scenes.findall('SCENE'):
            scId = xmlScn.find('ID').text
            xmlScenes[scId] = xmlScn
            scenes.remove(xmlScn)

        # Add the new XML scene subtrees to the project tree.
        for scId in self.novel.scenes:
            if not scId in xmlScenes:
                xmlScenes[scId] = ET.Element('SCENE')
                ET.SubElement(xmlScenes[scId], 'ID').text = scId
            build_scene_subtree(xmlScenes[scId], self.novel.scenes[scId])
            scenes.append(xmlScenes[scId])

        #--- Process chapters.

        # Save the original XML chapter subtree
        # and remove it from the project tree.
        for xmlChp in chapters.findall('CHAPTER'):
            chId = xmlChp.find('ID').text
            xmlChapters[chId] = xmlChp
            chapters.remove(xmlChp)

        # Add the new XML chapter subtrees to the project tree.
        sortOrder = 0
        for chId in self.novel.srtChapters:
            sortOrder += 1
            if not chId in xmlChapters:
                xmlChapters[chId] = ET.Element('CHAPTER')
                ET.SubElement(xmlChapters[chId], 'ID').text = chId
            build_chapter_subtree(xmlChapters[chId], self.novel.chapters[chId], sortOrder)
            chapters.append(xmlChapters[chId])

        # Modify the scene contents of an existing xml element tree.
        for scn in root.iter('SCENE'):
            scId = scn.find('ID').text
            if self.novel.scenes[scId].sceneContent is not None:
                scn.find('SceneContent').text = self.novel.scenes[scId].sceneContent
                scn.find('WordCount').text = str(self.novel.scenes[scId].wordCount)
                scn.find('LetterCount').text = str(self.novel.scenes[scId].letterCount)
            try:
                scn.remove(scn.find('RTFFile'))
            except:
                pass

        indent(root)
        self.tree = ET.ElementTree(root)

    def _write_element_tree(self, ywProject):
        """Write back the xml element tree to a .yw7 xml file located at filePath.
        
        Raise the "Error" exception in case of error. 
        """
        backedUp = False
        if os.path.isfile(ywProject.filePath):
            try:
                os.replace(ywProject.filePath, f'{ywProject.filePath}.bak')
            except:
                raise Error(f'{_("Cannot overwrite file")}: "{norm_path(ywProject.filePath)}".')
            else:
                backedUp = True
        try:
            ywProject.tree.write(ywProject.filePath, xml_declaration=False, encoding='utf-8')
        except:
            if backedUp:
                os.replace(f'{ywProject.filePath}.bak', ywProject.filePath)
            raise Error(f'{_("Cannot write file")}: "{norm_path(ywProject.filePath)}".')

    def _postprocess_xml_file(self, filePath):
        '''Postprocess an xml file created by ElementTree.
        
        Positional argument:
            filePath -- str: path to xml file.
        
        Read the xml file, put a header on top, insert the missing CDATA tags,
        and replace xml entities by plain text (unescape). Overwrite the .yw7 xml file.
        Raise the "Error" exception in case of error. 
        
        Note: The path is given as an argument rather than using self.filePath. 
        So this routine can be used for yWriter-generated xml files other than .yw7 as well. 
        '''
        with open(filePath, 'r', encoding='utf-8') as f:
            text = f.read()
        lines = text.split('\n')
        newlines = ['<?xml version="1.0" encoding="utf-8"?>']
        for line in lines:
            for tag in self._CDATA_TAGS:
                line = re.sub(f'\<{tag}\>', f'<{tag}><![CDATA[', line)
                line = re.sub(f'\<\/{tag}\>', f']]></{tag}>', line)
            newlines.append(line)
        text = '\n'.join(newlines)
        text = text.replace('[CDATA[ \n', '[CDATA[')
        text = text.replace('\n]]', ']]')
        text = unescape(text)
        try:
            with open(filePath, 'w', encoding='utf-8') as f:
                f.write(text)
        except:
            raise Error(f'{_("Cannot write file")}: "{norm_path(filePath)}".')

    def _strip_spaces(self, lines):
        """Local helper method.

        Positional argument:
            lines -- list of strings

        Return lines with leading and trailing spaces removed.
        """
        stripped = []
        for line in lines:
            stripped.append(line.strip())
        return stripped

    def adjust_scene_types(self):
        """Make sure that scenes in non-"Normal" chapters inherit the chapter's type."""
        for chId in self.novel.srtChapters:
            if self.novel.chapters[chId].chType != 0:
                for scId in self.novel.chapters[chId].srtScenes:
                    self.novel.scenes[scId].scType = self.novel.chapters[chId].chType

from xml import sax


class OdtParser(sax.ContentHandler):
    """An ODT document parser, emulating the html.parser.HTMLParser API.
    
    Public methods:
        feed_file(filePath) -- Feed an ODT file to the parser.
    
      HTMLParser compatible API
        handle_starttag -- Stub for a start tag handler to be implemented in a subclass.
        handle_endtag -- Stub for an end tag handler to be implemented in a subclass.
        handle_data -- Stub for a data handler to be implemented in a subclass.
        handle_comment -- Stub for a comment handler to be implemented in a subclass.
        
      Methods overriding xml.sax.ContentHandler methods (not meant to be overridden by subclasses)
        startElement -- Signals the start of an element in non-namespace mode.
        endElement -- Signals the end of an element in non-namespace mode.
        characters -- Receive notification of character data.
    """

    def __init__(self):
        super().__init__()
        self._emTags = ['Emphasis']
        self._strongTags = ['Strong_20_Emphasis']
        self._blockquoteTags = ['Quotations']
        self._languageTags = {}
        self._headingTags = {}
        self._heading = None
        self._paragraph = False
        self._commentParagraphCount = None
        self._blockquote = False
        self._list = False
        self._span = []
        self._style = None

    def feed_file(self, filePath):
        """Feed an ODT file to the parser.
        
        Positional arguments:
            filePath -- str: ODT document path.
        
        First unzip the ODT file located at self.filePath, 
        and get languageCode, countryCode, title, desc, and authorName,        
        Then call the sax parser for content.xml.
        """
        namespaces = dict(
            office='urn:oasis:names:tc:opendocument:xmlns:office:1.0',
            style='urn:oasis:names:tc:opendocument:xmlns:style:1.0',
            fo='urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0',
            dc='http://purl.org/dc/elements/1.1/',
            meta='urn:oasis:names:tc:opendocument:xmlns:meta:1.0'
            )

        try:
            with zipfile.ZipFile(filePath, 'r') as odfFile:
                content = odfFile.read('content.xml')
                styles = odfFile.read('styles.xml')
                meta = odfFile.read('meta.xml')
        except:
            raise Error(f'{_("Cannot read file")}: "{norm_path(filePath)}".')

        #--- Get language and country from 'styles.xml'.
        root = ET.fromstring(styles)
        styles = root.find('office:styles', namespaces)
        for defaultStyle in styles.findall('style:default-style', namespaces):
            if defaultStyle.get(f'{{{namespaces["style"]}}}family') == 'paragraph':
                textProperties = defaultStyle.find('style:text-properties', namespaces)
                lngCode = textProperties.get(f'{{{namespaces["fo"]}}}language')
                ctrCode = textProperties.get(f'{{{namespaces["fo"]}}}country')
                self.handle_starttag('body', [('language', lngCode), ('country', ctrCode)])
                break

        #--- Get title, description, and author from 'meta.xml'.
        root = ET.fromstring(meta)
        meta = root.find('office:meta', namespaces)
        title = meta.find('dc:title', namespaces)
        if title is not None:
            if title.text:
                self.handle_starttag('title', [()])
                self.handle_data(title.text)
                self.handle_endtag('title')
        author = meta.find('meta:initial-creator', namespaces)
        if author is not None:
            if author.text:
                self.handle_starttag('meta', [('', 'author'), ('', author.text)])
        desc = meta.find('dc:description', namespaces)
        if desc is not None:
            if desc.text:
                self.handle_starttag('meta', [('', 'description'), ('', desc.text)])

        #--- Parse 'content.xml'.
        sax.parseString(content, self)

    def startElement(self, name, attrs):
        """Signals the start of an element in non-namespace mode.
        
        Overrides the xml.sax.ContentHandler method             
        """
        xmlAttributes = {}
        for attribute in attrs.items():
            attrKey, attrValue = attribute
            xmlAttributes[attrKey] = attrValue
        style = xmlAttributes.get('text:style-name', '')
        if name == 'text:p':
            if style in self._languageTags:
                param = [('lang', self._languageTags[style])]
            else:
                param = [()]
            if self._commentParagraphCount is not None:
                self._commentParagraphCount += 1
            elif style in self._blockquoteTags:
                self.handle_starttag('blockquote', param)
                self._paragraph = True
                self._blockquote = True
            elif style.startswith('Heading'):
                self._heading = f'h{style[-1]}'
                self.handle_starttag(self._heading, [()])
            elif style in self._headingTags:
                self._heading = self._headingTags[style]
                self.handle_starttag(self._heading, [()])
            elif self._list:
                self.handle_starttag('li', [()])
                self._paragraph = True
            else:
                self.handle_starttag('p', param)
                self._paragraph = True
        elif name == 'text:span':
            if style in self._emTags:
                self._span.append('em')
                self.handle_starttag('em', [()])
            elif style in self._strongTags:
                self._span.append('strong')
                self.handle_starttag('strong', [()])
            elif style in self._languageTags:
                self._span.append('lang')
                self.handle_starttag('lang', [('lang', self._languageTags[style])])
        elif name == 'text:section':
            sectionId = xmlAttributes['text:name']
            self.handle_starttag('div', [('id', sectionId)])
        elif name == 'office:annotation':
            self._commentParagraphCount = 0
            self._comment = ''
        elif name == 'text:h':
            try:
                self._heading = f'h{xmlAttributes["text:outline-level"]}'
            except:
                self._heading = f'h{style[-1]}'
            self.handle_starttag(self._heading, [()])
        elif name == 'text:list-item':
            self._list = True
        elif name == 'style:style':
            self._style = xmlAttributes.get('style:name', None)
            styleName = xmlAttributes.get('style:parent-style-name', '')
            if styleName.startswith('Heading'):
                self._headingTags[self._style] = f'h{styleName[-1]}'
            elif styleName == 'Quotations':
                self._blockquoteTags.append(self._style)
        elif name == 'style:text-properties':
            if xmlAttributes.get('style:font-style', None) == 'italic':
                self._emTags.append(self._style)
            if xmlAttributes.get('style:font-weight', None) == 'bold':
                self._strongTags.append(self._style)
            if xmlAttributes.get('fo:language', False):
                lngCode = xmlAttributes['fo:language']
                ctrCode = xmlAttributes['fo:country']
                if ctrCode != 'none':
                    locale = f'{lngCode}-{ctrCode}'
                else:
                    locale = lngCode
                self._languageTags[self._style] = locale

    def endElement(self, name):
        """Signals the end of an element in non-namespace mode.
        
        Overrides the xml.sax.ContentHandler method     
        """
        if name == 'text:p':
            if self._commentParagraphCount is None:
                if self._blockquote:
                    self.handle_endtag('blockquote')
                    self._blockquote = False
                elif self._heading:
                    self.handle_endtag(self._heading)
                    self._heading = None
                else:
                    self.handle_endtag('p')
                self._paragraph = False
        elif name == 'text:span':
            if self._span:
                self.handle_endtag(self._span.pop())
        elif name == 'text:section':
            self.handle_endtag('div')
        elif name == 'office:annotation':
            self.handle_comment(self._comment)
            self._commentParagraphCount = None
        elif name == 'text:h':
            self.handle_endtag(self._heading)
            self._heading = None
        elif name == 'text:list-item':
            self._list = False
        elif name == 'style:style':
            self._style = None

    def characters(self, content):
        """Receive notification of character data.
        
        Overrides the xml.sax.ContentHandler method             
        """
        if self._commentParagraphCount is not None:
            if self._commentParagraphCount == 1:
                self._comment = f'{self._comment}{content}'
        elif self._paragraph:
            self.handle_data(content)
        elif self._heading is not None:
            self.handle_data(content)

    def handle_starttag(self, tag, attrs):
        """Stub for a start tag handler to be implemented in a subclass.
        
        Positional arguments:
            tag -- str: name of the tag converted to lower case.
            attrs -- list of (name, value) pairs containing the attributes found inside the tag’s <> brackets.
        """

    def handle_endtag(self, tag):
        """Stub for an end tag handler to be implemented in a subclass.
        
        Positional arguments:
            tag -- str: name of the tag converted to lower case.
        """

    def handle_data(self, data):
        """Stub for a data handler to be implemented in a subclass.

        Positional arguments:
            data -- str: text to be stored. 
        """

    def handle_comment(self, data):
        """Stub for a comment handler to be implemented in a subclass.
        
        Positional arguments:
            data -- str: comment text. 
        """



class OdtReader(File, OdtParser):
    """Generic ODT file reader.
    
    Public methods:
        handle_starttag(tag, attrs) -- Identify scenes and chapters.
        handle_endtag(tag) -- Stub for an end tag handler.
        handle_data(data) -- Stub for a data handler.
        handle comment(data) -- Process inline comments within scene content.
        read() -- Parse the file and get the instance variables.
    """
    EXTENSION = '.odt'

    _TYPE = 0

    _COMMENT_START = '/*'
    _COMMENT_END = '*/'
    _SC_TITLE_BRACKET = '~'
    _BULLET = '-'
    _INDENT = '>'

    def __init__(self, filePath, **kwargs):
        """Initialize the ODT parser and local instance variables for parsing.
        
        Positional arguments:
            filePath -- str: path to the file represented by the File instance.
            
        Optional arguments:
            kwargs -- keyword arguments to be used by subclasses.            

        The ODT parser works like a state machine. 
        Scene ID, chapter ID and processed lines must be saved between the transitions.         
        Extends the superclass constructor.
        """
        super().__init__(filePath)
        self._lines = []
        self._scId = None
        self._chId = None
        self._newline = False
        self._language = ''
        self._skip_data = False

    def _convert_to_yw(self, text):
        """Convert html formatting tags to yWriter 7 raw markup.
        
        Positional arguments:
            text -- string to convert.
        
        Return a yw7 markup string.
        Overrides the superclass method.
        """
        #--- Put everything in one line.
        text = text.replace('\n', ' ')
        text = text.replace('\r', ' ')
        text = text.replace('\t', ' ')
        while '  ' in text:
            text = text.replace('  ', ' ')

        return text

    def handle_starttag(self, tag, attrs):
        """Identify scenes and chapters.
        
        Positional arguments:
            tag -- str: name of the tag converted to lower case.
            attrs -- list of (name, value) pairs containing the attributes found inside the tag’s <> brackets.
        
        Overrides the superclass method. 
        This method is applicable to ODT files that are divided into chapters and scenes. 
        For differently structured ODT files  do override this method in a subclass.
        """
        if tag == 'div':
            if attrs[0][0] == 'id':
                if attrs[0][1].startswith('ScID'):
                    self._scId = re.search('[0-9]+', attrs[0][1]).group()
                    if not self._scId in self.novel.scenes:
                        self.novel.scenes[self._scId] = Scene()
                        self.novel.chapters[self._chId].srtScenes.append(self._scId)
                    self.novel.scenes[self._scId].scType = self._TYPE
                elif attrs[0][1].startswith('ChID'):
                    self._chId = re.search('[0-9]+', attrs[0][1]).group()
                    if not self._chId in self.novel.chapters:
                        self.novel.chapters[self._chId] = Chapter()
                        self.novel.chapters[self._chId].srtScenes = []
                        self.novel.srtChapters.append(self._chId)
                    self.novel.chapters[self._chId].chType = self._TYPE

    def handle_comment(self, data):
        """Process inline comments within scene content.
        
        Positional arguments:
            data -- str: comment text. 
        
        Overrides the superclass method.
        """
        if self._scId is not None:
            self._lines.append(f'{self._COMMENT_START}{data}{self._COMMENT_END}')

    def read(self):
        OdtParser.feed_file(self, self.filePath)


class Splitter:
    """Helper class for scene and chapter splitting.
    
    When importing scenes to yWriter, they may contain manually inserted scene and chapter dividers.
    The Splitter class updates a Novel instance by splitting such scenes and creating new chapters and scenes. 
    
    Public methods:
        split_scenes(novel) -- Split scenes by inserted chapter and scene dividers.
        
    Public class constants:
        PART_SEPARATOR -- marker indicating the beginning of a new part, splitting a scene.
        CHAPTER_SEPARATOR -- marker indicating the beginning of a new chapter, splitting a scene.
        DESC_SEPARATOR -- marker separating title and description of a chapter or scene.
    """
    PART_SEPARATOR = '#'
    CHAPTER_SEPARATOR = '##'
    SCENE_SEPARATOR = '###'
    DESC_SEPARATOR = '|'
    _CLIP_TITLE = 20
    # Maximum length of newly generated scene titles.

    def split_scenes(self, file):
        """Split scenes by inserted chapter and scene dividers.
        
        Update a Novel instance by generating new chapters and scenes 
        if there are dividers within the scene content.
        
        Positional argument: 
            file -- File instance to update.
        
        Return True if the sructure has changed, 
        otherwise return False.        
        """

        def create_chapter(chapterId, title, desc, level):
            """Create a new chapter and add it to the file.novel.
            
            Positional arguments:
                chapterId -- str: ID of the chapter to create.
                title -- str: title of the chapter to create.
                desc -- str: description of the chapter to create.
                level -- int: chapter level (part/chapter).           
            """
            newChapter = Chapter()
            newChapter.title = title
            newChapter.desc = desc
            newChapter.chLevel = level
            newChapter.chType = 0
            file.novel.chapters[chapterId] = newChapter

        def create_scene(sceneId, parent, splitCount, title, desc):
            """Create a new scene and add it to the file.novel.
            
            Positional arguments:
                sceneId -- str: ID of the scene to create.
                parent -- Scene instance: parent scene.
                splitCount -- int: number of parent's splittings.
                title -- str: title of the scene to create.
                desc -- str: description of the scene to create.
            """
            WARNING = '(!)'

            # Mark metadata of split scenes.
            newScene = Scene()
            if title:
                newScene.title = title
            elif parent.title:
                if len(parent.title) > self._CLIP_TITLE:
                    title = f'{parent.title[:self._CLIP_TITLE]}...'
                else:
                    title = parent.title
                newScene.title = f'{title} Split: {splitCount}'
            else:
                newScene.title = f'{_("New Scene")} Split: {splitCount}'
            if desc:
                newScene.desc = desc
            if parent.desc and not parent.desc.startswith(WARNING):
                parent.desc = f'{WARNING}{parent.desc}'
            if parent.goal and not parent.goal.startswith(WARNING):
                parent.goal = f'{WARNING}{parent.goal}'
            if parent.conflict and not parent.conflict.startswith(WARNING):
                parent.conflict = f'{WARNING}{parent.conflict}'
            if parent.outcome and not parent.outcome.startswith(WARNING):
                parent.outcome = f'{WARNING}{parent.outcome}'

            # Reset the parent's status to Draft, if not Outline.
            if parent.status > 2:
                parent.status = 2
            newScene.status = parent.status
            newScene.scType = parent.scType
            newScene.date = parent.date
            newScene.time = parent.time
            newScene.day = parent.day
            newScene.lastsDays = parent.lastsDays
            newScene.lastsHours = parent.lastsHours
            newScene.lastsMinutes = parent.lastsMinutes
            file.novel.scenes[sceneId] = newScene

        # Get the maximum chapter ID and scene ID.
        chIdMax = 0
        scIdMax = 0
        for chId in file.novel.srtChapters:
            if int(chId) > chIdMax:
                chIdMax = int(chId)
        for scId in file.novel.scenes:
            if int(scId) > scIdMax:
                scIdMax = int(scId)

        # Process chapters and scenes.
        scenesSplit = False
        srtChapters = []
        for chId in file.novel.srtChapters:
            srtChapters.append(chId)
            chapterId = chId
            srtScenes = []
            for scId in file.novel.chapters[chId].srtScenes:
                srtScenes.append(scId)
                if not file.novel.scenes[scId].sceneContent:
                    continue

                sceneId = scId
                lines = file.novel.scenes[scId].sceneContent.split('\n')
                newLines = []
                inScene = True
                sceneSplitCount = 0

                # Search scene content for dividers.
                for line in lines:
                    heading = line.strip('# ').split(self.DESC_SEPARATOR)
                    title = heading[0]
                    try:
                        desc = heading[1]
                    except:
                        desc = ''
                    if line.startswith(self.SCENE_SEPARATOR):
                        # Split the scene.
                        file.novel.scenes[sceneId].sceneContent = '\n'.join(newLines)
                        newLines = []
                        sceneSplitCount += 1
                        scIdMax += 1
                        sceneId = str(scIdMax)
                        create_scene(sceneId, file.novel.scenes[scId], sceneSplitCount, title, desc)
                        srtScenes.append(sceneId)
                        scenesSplit = True
                        inScene = True
                    elif line.startswith(self.CHAPTER_SEPARATOR):
                        # Start a new chapter.
                        if inScene:
                            file.novel.scenes[sceneId].sceneContent = '\n'.join(newLines)
                            newLines = []
                            sceneSplitCount = 0
                            inScene = False
                        file.novel.chapters[chapterId].srtScenes = srtScenes
                        srtScenes = []
                        chIdMax += 1
                        chapterId = str(chIdMax)
                        if not title:
                            title = _('New Chapter')
                        create_chapter(chapterId, title, desc, 0)
                        srtChapters.append(chapterId)
                        scenesSplit = True
                    elif line.startswith(self.PART_SEPARATOR):
                        # start a new part.
                        if inScene:
                            file.novel.scenes[sceneId].sceneContent = '\n'.join(newLines)
                            newLines = []
                            sceneSplitCount = 0
                            inScene = False
                        file.novel.chapters[chapterId].srtScenes = srtScenes
                        srtScenes = []
                        chIdMax += 1
                        chapterId = str(chIdMax)
                        if not title:
                            title = _('New Part')
                        create_chapter(chapterId, title, desc, 1)
                        srtChapters.append(chapterId)
                    elif not inScene:
                        # Append a scene without heading to a new chapter or part.
                        newLines.append(line)
                        sceneSplitCount += 1
                        scIdMax += 1
                        sceneId = str(scIdMax)
                        create_scene(sceneId, file.novel.scenes[scId], sceneSplitCount, '', '')
                        srtScenes.append(sceneId)
                        scenesSplit = True
                        inScene = True
                    else:
                        newLines.append(line)
                file.novel.scenes[sceneId].sceneContent = '\n'.join(newLines)
            file.novel.chapters[chapterId].srtScenes = srtScenes
        file.novel.srtChapters = srtChapters
        return scenesSplit


class OdtRFormatted(OdtReader):
    """ODT file reader.

    Provide methods and data for processing chapters with formatted text.
    """
    _COMMENT_START = '/*'
    _COMMENT_END = '*/'
    _SC_TITLE_BRACKET = '~'
    _BULLET = '-'
    _INDENT = '>'

    def read(self):
        """Parse the file and get the instance variables.
        
        Extends the superclass method.
        """
        self.novel.languages = []
        super().read()

        # Split scenes, if necessary.
        sceneSplitter = Splitter()
        self.scenesSplit = sceneSplitter.split_scenes(self)

    def _cleanup_scene(self, text):
        """Clean up yWriter markup.
        
        Positional arguments:
            text -- string to clean up.
        
        Return a yw7 markup string.
        """
        #--- Remove redundant tags.
        # In contrast to Office Writer, yWriter accepts markup reaching across linebreaks.
        tags = ['i', 'b']
        for language in self.novel.languages:
            tags.append(f'lang={language}')
        for tag in tags:
            text = text.replace(f'[/{tag}][{tag}]', '')
            text = text.replace(f'[/{tag}]\n[{tag}]', '\n')
            text = text.replace(f'[/{tag}]\n> [{tag}]', '\n> ')

        #--- Remove misplaced formatting tags.
        # text = re.sub('\[\/*[b|i]\]', '', text)
        return text



class OdtRImport(OdtRFormatted):
    """ODT 'work in progress' file reader.

    Import untagged chapters and scenes.
    """
    DESCRIPTION = _('Work in progress')
    SUFFIX = ''
    _SCENE_DIVIDER = '* * *'
    _LOW_WORDCOUNT = 10

    def __init__(self, filePath, **kwargs):
        """Initialize local instance variables for parsing.

        Positional arguments:
            filePath -- str: path to the file represented by the Novel instance.
            
        The ODT parser works like a state machine. 
        Chapter and scene count must be saved between the transitions.         
        Extends the superclass constructor.
        """
        super().__init__(filePath)
        self._chCount = 0
        self._scCount = 0

    def handle_starttag(self, tag, attrs):
        """Recognize the paragraph's beginning.
        
        Positional arguments:
            tag -- str: name of the tag converted to lower case.
            attrs -- list of (name, value) pairs containing the attributes found inside the tag’s <> brackets.
        
        Overrides the superclass method.
        """
        if tag == 'p':
            if self._scId is None and self._chId is not None:
                self._lines = []
                self._scCount += 1
                self._scId = str(self._scCount)
                self.novel.scenes[self._scId] = Scene()
                self.novel.chapters[self._chId].srtScenes.append(self._scId)
                self.novel.scenes[self._scId].status = '1'
                self.novel.scenes[self._scId].title = f'Scene {self._scCount}'
            try:
                if attrs[0][0] == 'lang':
                    self._language = attrs[0][1]
                    if not self._language in self.novel.languages:
                        self.novel.languages.append(self._language)
                    self._lines.append(f'[lang={self._language}]')
            except:
                pass
        elif tag == 'em':
            self._lines.append('[i]')
        elif tag == 'strong':
            self._lines.append('[b]')
        elif tag == 'lang':
            if attrs[0][0] == 'lang':
                self._language = attrs[0][1]
                if not self._language in self.novel.languages:
                    self.novel.languages.append(self._language)
                self._lines.append(f'[lang={self._language}]')
        elif tag in ('h1', 'h2'):
            self._scId = None
            self._lines = []
            self._chCount += 1
            self._chId = str(self._chCount)
            self.novel.chapters[self._chId] = Chapter()
            self.novel.chapters[self._chId].srtScenes = []
            self.novel.srtChapters.append(self._chId)
            self.novel.chapters[self._chId].chType = 0
            if tag == 'h1':
                self.novel.chapters[self._chId].chLevel = 1
            else:
                self.novel.chapters[self._chId].chLevel = 0
        elif tag == 'div':
            self._scId = None
            self._chId = None
        elif tag == 'meta':
            if attrs[0][1] == 'author':
                self.novel.authorName = attrs[1][1]
            if attrs[0][1] == 'description':
                self.novel.desc = attrs[1][1]
        elif tag == 'title':
            self._lines = []
        elif tag == 'body':
            for attr in attrs:
                if attr[0] == 'language':
                    if attr[1]:
                        self.novel.languageCode = attr[1]
                elif attr[0] == 'country':
                    if attr[1]:
                        self.novel.countryCode = attr[1]
        elif tag == 'li':
                self._lines.append(f'{self._BULLET} ')
        elif tag == 'blockquote':
            self._lines.append(f'{self._INDENT} ')
            try:
                if attrs[0][0] == 'lang':
                    self._language = attrs[0][1]
                    if not self._language in self.novel.languages:
                        self.novel.languages.append(self._language)
                    self._lines.append(f'[lang={self._language}]')
            except:
                pass

    def handle_endtag(self, tag):
        """Recognize the paragraph's end.
        
        Positional arguments:
            tag -- str: name of the tag converted to lower case.

        Overrides the superclass method.
        """
        if tag in ('p', 'blockquote'):
            if self._language:
                self._lines.append(f'[/lang={self._language}]')
                self._language = ''
            self._lines.append('\n')
            if self._scId is not None:
                sceneText = ''.join(self._lines).rstrip()
                sceneText = self._cleanup_scene(sceneText)
                self.novel.scenes[self._scId].sceneContent = sceneText
                if self.novel.scenes[self._scId].wordCount < self._LOW_WORDCOUNT:
                    self.novel.scenes[self._scId].status = Scene.STATUS.index('Outline')
                else:
                    self.novel.scenes[self._scId].status = Scene.STATUS.index('Draft')
        elif tag == 'em':
            self._lines.append('[/i]')
        elif tag == 'strong':
            self._lines.append('[/b]')
        elif tag == 'lang':
            if self._language:
                self._lines.append(f'[/lang={self._language}]')
                self._language = ''
        elif tag in ('h1', 'h2'):
            self.novel.chapters[self._chId].title = ''.join(self._lines)
            self._lines = []
        elif tag == 'title':
            self.novel.title = ''.join(self._lines)

    def handle_comment(self, data):
        """Process inline comments within scene content.
        
        Positional arguments:
            data -- str: comment text. 
        
        Use marked comments at scene start as scene titles.
        Overrides the superclass method.
        """
        if self._scId is not None:
            if not self._lines:
                # Comment is at scene start
                try:
                    self.novel.scenes[self._scId].title = data.strip()
                except:
                    pass
                return

            self._lines.append(f'{self._COMMENT_START}{data.strip()}{self._COMMENT_END}')

    def handle_data(self, data):
        """Collect data within scene sections.

        Positional arguments:
            data -- str: text to be stored. 
        
        Overrides the superclass method.
        """
        if self._scId is not None and self._SCENE_DIVIDER in data:
            self._scId = None
        else:
            self._lines.append(data)

    def read(self):
        self.novel.languages = []
        super().read()



class OdtROutline(OdtReader):
    """ODT outline file reader.

    Import an outline without chapter and scene tags.
    """
    DESCRIPTION = _('Novel outline')
    SUFFIX = ''

    def __init__(self, filePath, **kwargs):
        """Initialize local instance variables for parsing.

        Positional arguments:
            filePath -- str: path to the file represented by the Novel instance.
            
        The ODT parser works like a state machine. 
        Chapter and scene count must be saved between the transitions.         
        Extends the superclass constructor.
        """
        super().__init__(filePath)
        self._chCount = 0
        self._scCount = 0

    def handle_starttag(self, tag, attrs):
        """Recognize the paragraph's beginning.
        
        Positional arguments:
            tag -- str: name of the tag converted to lower case.
            attrs -- list of (name, value) pairs containing the attributes found inside the tag’s <> brackets.
        
        Overrides the superclass method.
        """
        if tag in ('h1', 'h2'):
            self._scId = None
            self._lines = []
            self._chCount += 1
            self._chId = str(self._chCount)
            self.novel.chapters[self._chId] = Chapter()
            self.novel.chapters[self._chId].srtScenes = []
            self.novel.srtChapters.append(self._chId)
            self.novel.chapters[self._chId].chType = 0
            if tag == 'h1':
                self.novel.chapters[self._chId].chLevel = 1
            else:
                self.novel.chapters[self._chId].chLevel = 0
        elif tag == 'h3':
            self._lines = []
            self._scCount += 1
            self._scId = str(self._scCount)
            self.novel.scenes[self._scId] = Scene()
            self.novel.chapters[self._chId].srtScenes.append(self._scId)
            self.novel.scenes[self._scId].sceneContent = ''
            self.novel.scenes[self._scId].status = Scene.STATUS.index('Outline')
        elif tag == 'div':
            self._scId = None
            self._chId = None
        elif tag == 'meta':
            if attrs[0][1] == 'author':
                self.novel.authorName = attrs[1][1]
            if attrs[0][1] == 'description':
                self.novel.desc = attrs[1][1]
        elif tag == 'title':
            self._lines = []
        elif tag == 'body':
            for attr in attrs:
                if attr[0] == 'language':
                    if attr[1]:
                        self.novel.languageCode = attr[1]
                elif attr[0] == 'country':
                    if attr[1]:
                        self.novel.countryCode = attr[1]

    def handle_endtag(self, tag):
        """Recognize the paragraph's end.
        
        Positional arguments:
            tag -- str: name of the tag converted to lower case.

        Overrides the superclass method.
        """
        text = ''.join(self._lines)
        if tag == 'p':
            text = f'{text.strip()}\n'
            self._lines = [text]
            if self._scId is not None:
                self.novel.scenes[self._scId].desc = text
            elif self._chId is not None:
                self.novel.chapters[self._chId].desc = text
        elif tag in ('h1', 'h2'):
            self.novel.chapters[self._chId].title = text.strip()
            self._lines = []
        elif tag == 'h3':
            self.novel.scenes[self._scId].title = text.strip()
            self._lines = []
        elif tag == 'title':
            self.novel.title = text.strip()

    def handle_data(self, data):
        """Collect data within scene sections.

        Positional arguments:
            data -- str: text to be stored. 
        
        Overrides the superclass method.
        """
        self._lines.append(data)


class NewProjectFactory(FileFactory):
    """A factory class that instantiates a document object to read, 
    and a new yWriter project.

    Public methods:
        make_file_objects(self, sourcePath, **kwargs) -- return conversion objects.

    Class constant:
        DO_NOT_IMPORT -- list of suffixes from file classes not meant to be imported.    
    """
    DO_NOT_IMPORT = ['_xref', '_brf_synopsis']

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a source and a target object for creation of a new yWriter project.

        Positional arguments:
            sourcePath -- str: path to the source file to convert.

        Return a tuple with two elements:
        - sourceFile: a Novel subclass instance
        - targetFile: a Novel subclass instance
        
        Raise the "Error" exception in case of error. 
        """
        if not self._canImport(sourcePath):
            raise Error(f'{_("This document is not meant to be written back")}.')

        fileName, __ = os.path.splitext(sourcePath)
        targetFile = Yw7File(f'{fileName}{Yw7File.EXTENSION}', **kwargs)
        if sourcePath.endswith('.odt'):
            # The source file might be an outline or a "work in progress".
            try:
                with zipfile.ZipFile(sourcePath, 'r') as odfFile:
                    content = odfFile.read('content.xml')
            except:
                raise Error(f'{_("Cannot read file")}: "{norm_path(sourcePath)}".')

            if bytes('Heading_20_3', encoding='utf-8') in content:
                sourceFile = OdtROutline(sourcePath, **kwargs)
            else:
                sourceFile = OdtRImport(sourcePath, **kwargs)
            return sourceFile, targetFile

        else:
            for fileClass in self._fileClasses:
                if fileClass.SUFFIX is not None:
                    if sourcePath.endswith(f'{fileClass.SUFFIX}{fileClass.EXTENSION}'):
                        sourceFile = fileClass(sourcePath, **kwargs)
                        return sourceFile, targetFile

            raise Error(f'{_("File type is not supported")}: "{norm_path(sourcePath)}".')

    def _canImport(self, sourcePath):
        """Check whether the source file can be imported to yWriter.
        
        Positional arguments: 
            sourcePath -- str: path of the file to be ckecked.
        
        Return True, if the file located at sourcepath is of an importable type.
        Otherwise, return False.
        """
        fileName, __ = os.path.splitext(sourcePath)
        for suffix in self.DO_NOT_IMPORT:
            if fileName.endswith(suffix):
                return False

        return True


class OdtRProof(OdtRFormatted):
    """ODT proof reading file reader.

    Import a manuscript with visibly tagged chapters and scenes.
    """
    DESCRIPTION = _('Tagged manuscript for proofing')
    SUFFIX = '_proof'

    def handle_starttag(self, tag, attrs):
        """Recognize the paragraph's beginning.
        
        Positional arguments:
            tag -- str: name of the tag converted to lower case.
            attrs -- list of (name, value) pairs containing the attributes found inside the tag’s <> brackets.
        
        Overrides the superclass method.
        """
        if tag == 'em':
            self._lines.append('[i]')
        elif tag == 'strong':
            self._lines.append('[b]')
        elif tag in ('lang', 'p'):
            try:
                if attrs[0][0] == 'lang':
                    self._language = attrs[0][1]
                    if not self._language in self.novel.languages:
                        self.novel.languages.append(self._language)
                    self._lines.append(f'[lang={self._language}]')
            except:
                pass
        elif tag == 'h2':
            self._lines.append(f'{Splitter.CHAPTER_SEPARATOR} ')
        elif tag == 'h1':
            self._lines.append(f'{Splitter.PART_SEPARATOR} ')
        elif tag == 'li':
            self._lines.append(f'{self._BULLET} ')
        elif tag == 'blockquote':
            self._lines.append(f'{self._INDENT} ')
            try:
                if attrs[0][0] == 'lang':
                    self._language = attrs[0][1]
                    if not self._language in self.novel.languages:
                        self.novel.languages.append(self._language)
                    self._lines.append(f'[lang={self._language}]')
            except:
                pass
        elif tag == 'body':
            for attr in attrs:
                if attr[0] == 'language':
                    if attr[1]:
                        self.novel.languageCode = attr[1]
                elif attr[0] == 'country':
                    if attr[1]:
                        self.novel.countryCode = attr[1]
        elif tag in ('br', 'ul'):
            self._skip_data = True
            # avoid inserting an unwanted blank

    def handle_endtag(self, tag):
        """Recognize the paragraph's end.      
        
        Positional arguments:
            tag -- str: name of the tag converted to lower case.

        Overrides the superclass method.
        """
        if tag in ['p', 'h2', 'h1', 'blockquote']:
            self._lines.append('\n')
            if self._language:
                self._lines.append(f'[/lang={self._language}]')
                self._language = ''
        elif tag == 'em':
            self._lines.append('[/i]')
        elif tag == 'strong':
            self._lines.append('[/b]')
        elif tag == 'lang':
            if self._language:
                self._lines.append(f'[/lang={self._language}]')
                self._language = ''

    def handle_data(self, data):
        """Parse the paragraphs and build the document structure.      

        Positional arguments:
            data -- str: text to be parsed. 
        
        Overrides the superclass method.
        """
        if self._skip_data:
            self._skip_data = False
        elif '[ScID' in data:
            self._scId = re.search('[0-9]+', data).group()
            if not self._scId in self.novel.scenes:
                self.novel.scenes[self._scId] = Scene()
                self.novel.chapters[self._chId].srtScenes.append(self._scId)
            self._lines = []
        elif '[/ScID' in data:
            text = ''.join(self._lines)
            self.novel.scenes[self._scId].sceneContent = self._cleanup_scene(text).strip()
            self._scId = None
        elif '[ChID' in data:
            self._chId = re.search('[0-9]+', data).group()
            if not self._chId in self.novel.chapters:
                self.novel.chapters[self._chId] = Chapter()
                self.novel.srtChapters.append(self._chId)
        elif '[/ChID' in data:
            self._chId = None
        elif self._scId is not None:
            self._lines.append(data)


class OdtRManuscript(OdtRFormatted):
    """ODT manuscript file reader.

    Import a manuscript with invisibly tagged chapters and scenes.
    """
    DESCRIPTION = _('Editable manuscript')
    SUFFIX = '_manuscript'

    def handle_starttag(self, tag, attrs):
        """Identify scenes and chapters.
        
        Positional arguments:
            tag -- str: name of the tag converted to lower case.
            attrs -- list of (name, value) pairs containing the attributes found inside the tag’s <> brackets.
        
        Extends the superclass method by processing inline chapter and scene dividers.
        """
        super().handle_starttag(tag, attrs)
        if self._scId is not None:
            if tag == 'em':
                self._lines.append('[i]')
            elif tag == 'strong':
                self._lines.append('[b]')
            elif tag in ('lang', 'p'):
                try:
                    if attrs[0][0] == 'lang':
                        self._language = attrs[0][1]
                        if not self._language in self.novel.languages:
                            self.novel.languages.append(self._language)
                        self._lines.append(f'[lang={self._language}]')
                except:
                    pass
            elif tag == 'h3':
                self._skip_data = True
                # this is for downward compatibility with "notes" and "todo"
                # documents generated with PyWriter v8 and before.
            elif tag == 'h2':
                self._lines.append(f'{Splitter.CHAPTER_SEPARATOR} ')
            elif tag == 'h1':
                self._lines.append(f'{Splitter.PART_SEPARATOR} ')
            elif tag == 'li':
                self._lines.append(f'{self._BULLET} ')
            elif tag == 'blockquote':
                self._lines.append(f'{self._INDENT} ')
                try:
                    if attrs[0][0] == 'lang':
                        self._language = attrs[0][1]
                        if not self._language in self.novel.languages:
                            self.novel.languages.append(self._language)
                        self._lines.append(f'[lang={self._language}]')
                except:
                    pass
        elif tag == 'body':
            for attr in attrs:
                if attr[0] == 'language':
                    if attr[1]:
                        self.novel.languageCode = attr[1]
                elif attr[0] == 'country':
                    if attr[1]:
                        self.novel.countryCode = attr[1]

    def handle_endtag(self, tag):
        """Recognize the end of the scene section and save data.
        
        Positional arguments:
            tag -- str: name of the tag converted to lower case.

        Overrides the superclass method.
        """
        if self._scId is not None:
            if tag in ('p', 'blockquote'):
                if self._language:
                    self._lines.append(f'[/lang={self._language}]')
                    self._language = ''
                self._lines.append('\n')
            elif tag == 'em':
                self._lines.append('[/i]')
            elif tag == 'strong':
                self._lines.append('[/b]')
            elif tag == 'lang':
                if self._language:
                    self._lines.append(f'[/lang={self._language}]')
                    self._language = ''
            elif tag == 'div':
                text = ''.join(self._lines)
                self.novel.scenes[self._scId].sceneContent = self._cleanup_scene(text).rstrip()
                self._lines = []
                self._scId = None
            elif tag == 'h1':
                self._lines.append('\n')
            elif tag == 'h2':
                self._lines.append('\n')
        elif self._chId is not None:
            if tag == 'div':
                self._chId = None

    def handle_comment(self, data):
        """Process inline comments within scene content.
        
        Positional arguments:
            data -- str: comment text. 
        
        Use marked comments at scene start as scene titles.
        Overrides the superclass method.
        """
        if self._scId is not None:
            if not self._lines:
                # Comment is at scene start
                pass
            if self._SC_TITLE_BRACKET in data:
                # Comment is marked as a scene title
                try:
                    self.novel.scenes[self._scId].title = data.split(self._SC_TITLE_BRACKET)[1].strip()
                except:
                    pass
                return

            self._lines.append(f'{self._COMMENT_START}{data.strip()}{self._COMMENT_END}')

    def handle_data(self, data):
        """Collect data within scene sections.

        Positional arguments:
            data -- str: text to be stored. 
        
        Overrides the superclass method.
        """
        if self._skip_data:
            self._skip_data = False
        elif self._scId is not None:
            if not data.isspace():
                self._lines.append(data)
        elif self._chId is not None:
            if self.novel.chapters[self._chId].title is None:
                self.chapters[self._chId].title = data.strip()


class OdtRNotes(OdtRManuscript):
    """ODT "Notes" chapters file reader.

    Import a manuscript with invisibly tagged chapters and scenes.
    """
    DESCRIPTION = _('Notes chapters')
    SUFFIX = '_notes'

    _TYPE = 1


class OdtRTodo(OdtRManuscript):
    """ODT "Todo" chapters file reader.

    Import a manuscript with invisibly tagged chapters and scenes.
    """
    DESCRIPTION = _('Todo chapters')
    SUFFIX = '_todo'

    _TYPE = 2


class OdtRSceneDesc(OdtReader):
    """ODT scene summaries file reader.

    Import a full synopsis with invisibly tagged scene descriptions.
    """
    DESCRIPTION = _('Scene descriptions')
    SUFFIX = '_scenes'

    def handle_endtag(self, tag):
        """Recognize the end of the scene section and save data.
        
        Positional arguments:
            tag -- str: name of the tag converted to lower case.

        Overrides the superclass method.
        """
        if self._scId is not None:
            if tag == 'div':
                text = ''.join(self._lines)
                if text.startswith(self._COMMENT_START):
                    try:
                        scTitle, scContent = text.split(
                            sep=self._COMMENT_END, maxsplit=1)
                        if self._SC_TITLE_BRACKET in scTitle:
                            self.novel.scenes[self._scId].title = scTitle.split(
                                self._SC_TITLE_BRACKET)[1].strip()
                        text = scContent
                    except:
                        pass
                self.novel.scenes[self._scId].desc = text.rstrip()
                self._lines = []
                self._scId = None
            elif tag == 'p':
                self._lines.append('\n')
        elif self._chId is not None:
            if tag == 'div':
                self._chId = None

    def handle_data(self, data):
        """Collect data within scene sections.

        Positional arguments:
            data -- str: text to be stored. 
        
        Overrides the superclass method.
        """
        if self._scId is not None:
            self._lines.append(data)
        elif self._chId is not None:
            if not self.novel.chapters[self._chId].title:
                self.novel.chapters[self._chId].title = data.strip()


class OdtRChapterDesc(OdtReader):
    """ODT chapter summaries file reader.

    Import a brief synopsis with invisibly tagged chapter descriptions.
    """
    DESCRIPTION = _('Chapter descriptions')
    SUFFIX = '_chapters'

    def handle_endtag(self, tag):
        """Recognize the end of the chapter section and save data.
        
        Positional arguments:
            tag -- str: name of the tag converted to lower case.

        Overrides the superclass method.
        """
        if self._chId is not None:
            if tag == 'div':
                self.novel.chapters[self._chId].desc = ''.join(self._lines).rstrip()
                self._lines = []
                self._chId = None
            elif tag == 'p':
                self._lines.append('\n')
            elif tag == 'h1' or tag == 'h2':
                if not self.novel.chapters[self._chId].title:
                    self.novel.chapters[self._chId].title = ''.join(self._lines)
                self._lines = []

    def handle_data(self, data):
        """Collect data within chapter sections.

        Positional arguments:
            data -- str: text to be stored. 
        
        Overrides the superclass method.
        """
        if self._chId is not None:
            self._lines.append(data.strip())


class OdtRPartDesc(OdtRChapterDesc):
    """ODT part summaries file reader.

    Parts are chapters marked in yWriter as beginning of a new section.
    Import a synopsis with invisibly tagged part descriptions.
    """
    DESCRIPTION = _('Part descriptions')
    SUFFIX = '_parts'


class OdtRCharacters(OdtReader):
    """ODT character descriptions file reader.

    Import a character sheet with invisibly tagged descriptions.
    """
    DESCRIPTION = _('Character descriptions')
    SUFFIX = '_characters'

    def __init__(self, filePath, **kwargs):
        """Initialize local instance variables for parsing.

        Positional arguments:
            filePath -- str: path to the file represented by the Novel instance.
            
        The ODT parser works like a state machine. 
        Character ID and section title must be saved between the transitions.         
        Extends the superclass constructor.
        """
        super().__init__(filePath)
        self._crId = None
        self._section = None

    def handle_starttag(self, tag, attrs):
        """Identify characters with subsections.
        
        Positional arguments:
            tag -- str: name of the tag converted to lower case.
            attrs -- list of (name, value) pairs containing the attributes found inside the tag’s <> brackets.
        
        Overrides the superclass method.
        """
        if tag == 'div':
            if attrs[0][0] == 'id':
                if attrs[0][1].startswith('CrID_desc'):
                    self._crId = re.search('[0-9]+', attrs[0][1]).group()
                    if not self._crId in self.novel.characters:
                        self.novel.srtCharacters.append(self._crId)
                        self.novel.characters[self._crId] = Character()
                    self._section = 'desc'
                elif attrs[0][1].startswith('CrID_bio'):
                    self._section = 'bio'
                elif attrs[0][1].startswith('CrID_goals'):
                    self._section = 'goals'
                elif attrs[0][1].startswith('CrID_notes'):
                    self._section = 'notes'

    def handle_endtag(self, tag):
        """Recognize the end of the character section and save data.
        
        Positional arguments:
            tag -- str: name of the tag converted to lower case.

        Overrides the superclass method.
        """
        if self._crId is not None:
            if tag == 'div':
                if self._section == 'desc':
                    self.novel.characters[self._crId].desc = ''.join(self._lines).rstrip()
                    self._lines = []
                    self._section = None
                elif self._section == 'bio':
                    self.novel.characters[self._crId].bio = ''.join(self._lines).rstrip()
                    self._lines = []
                    self._section = None
                elif self._section == 'goals':
                    self.novel.characters[self._crId].goals = ''.join(self._lines).rstrip()
                    self._lines = []
                    self._section = None
                elif self._section == 'notes':
                    self.novel.characters[self._crId].notes = ''.join(self._lines)
                    self._lines = []
                    self._section = None
            elif tag == 'p':
                self._lines.append('\n')

    def handle_data(self, data):
        """collect data within character sections.

        Positional arguments:
            data -- str: text to be stored. 
        
        Overrides the superclass method.
        """
        if self._section is not None:
            self._lines.append(data.strip())


class OdtRLocations(OdtReader):
    """ODT location descriptions file reader.

    Import a location sheet with invisibly tagged descriptions.
    """
    DESCRIPTION = _('Location descriptions')
    SUFFIX = '_locations'

    def __init__(self, filePath, **kwargs):
        """Initialize local instance variables for parsing.

        Positional arguments:
            filePath -- str: path to the file represented by the Novel instance.
            
        The ODT parser works like a state machine. 
        The location ID must be saved between the transitions.         
        Extends the superclass constructor.
        """
        super().__init__(filePath)
        self._lcId = None

    def handle_starttag(self, tag, attrs):
        """Identify locations.
        
        Positional arguments:
            tag -- str: name of the tag converted to lower case.
            attrs -- list of (name, value) pairs containing the attributes found inside the tag’s <> brackets.
        
        Overrides the superclass method.
        """
        if tag == 'div':
            if attrs[0][0] == 'id':
                if attrs[0][1].startswith('LcID'):
                    self._lcId = re.search('[0-9]+', attrs[0][1]).group()
                    if not self._lcId in self.novel.locations:
                        self.novel.srtLocations.append(self._lcId)
                        self.novel.locations[self._lcId] = WorldElement()

    def handle_endtag(self, tag):
        """Recognize the end of the location section and save data.
        
        Positional arguments:
            tag -- str: name of the tag converted to lower case.

        Overrides the superclass method.
        """
        if self._lcId is not None:
            if tag == 'div':
                self.novel.locations[self._lcId].desc = ''.join(self._lines).rstrip()
                self._lines = []
                self._lcId = None
            elif tag == 'p':
                self._lines.append('\n')

    def handle_data(self, data):
        """collect data within location sections.
        
        Positional arguments:
            data -- str: text to be stored. 
        
        Overrides the superclass method.
        """
        if self._lcId is not None:
            self._lines.append(data.strip())


class OdtRItems(OdtReader):
    """ODT item descriptions file reader.

    Import a item sheet with invisibly tagged descriptions.
    """
    DESCRIPTION = _('Item descriptions')
    SUFFIX = '_items'

    def __init__(self, filePath, **kwargs):
        """Initialize local instance variables for parsing.

        Positional arguments:
            filePath -- str: path to the file represented by the Novel instance.
            
        The ODT parser works like a state machine. 
        The item ID must be saved between the transitions.         
        Extends the superclass constructor.
        """
        super().__init__(filePath)
        self._itId = None

    def handle_starttag(self, tag, attrs):
        """Identify items.
        
        Positional arguments:
            tag -- str: name of the tag converted to lower case.
            attrs -- list of (name, value) pairs containing the attributes found inside the tag’s <> brackets.
        
        Overrides the superclass method.
        """
        if tag == 'div':
            if attrs[0][0] == 'id':
                if attrs[0][1].startswith('ItID'):
                    self._itId = re.search('[0-9]+', attrs[0][1]).group()
                    if not self._itId in self.novel.items:
                        self.novel.srtItems.append(self._itId)
                        self.novel.items[self._itId] = WorldElement()

    def handle_endtag(self, tag):
        """Recognize the end of the item section and save data.
        
        Positional arguments:
            tag -- str: name of the tag converted to lower case.

        Overrides the superclass method.
        """
        if self._itId is not None:
            if tag == 'div':
                self.novel.items[self._itId].desc = ''.join(self._lines).rstrip()
                self._lines = []
                self._itId = None
            elif tag == 'p':
                self._lines.append('\n')

    def handle_data(self, data):
        """collect data within item sections.

        Positional arguments:
            data -- str: text to be stored. 
        
        Overrides the superclass method.
        """
        if self._itId is not None:
            self._lines.append(data.strip())
from string import Template


class Filter:
    """Filter an entity (chapter/scene/character/location/item) by filter criteria.
    
    Public methods:
        accept(source, eId) -- check whether an entity matches the filter criteria.
    
    Strategy class, implementing filtering criteria for template-based export.
    This is a stub with no filter criteria specified.
    """

    def accept(self, source, eId):
        """Check whether an entity matches the filter criteria.
        
        Positional arguments:
            source -- Novel instance holding the entity to check.
            eId -- ID of the entity to check.       
        
        Return True if the entity is not to be filtered out.
        This is a stub to be overridden by subclass methods implementing filters.
        """
        return True


class FileExport(File):
    """Abstract yWriter project file exporter representation.
    
    Public methods:
        write() -- write instance variables to the export file.
    
    This class is generic and contains no conversion algorithm and no templates.
    """
    SUFFIX = ''
    _fileHeader = ''
    _partTemplate = ''
    _chapterTemplate = ''
    _notesPartTemplate = ''
    _todoPartTemplate = ''
    _notesChapterTemplate = ''
    _todoChapterTemplate = ''
    _unusedChapterTemplate = ''
    _notExportedChapterTemplate = ''
    _sceneTemplate = ''
    _firstSceneTemplate = ''
    _appendedSceneTemplate = ''
    _notesSceneTemplate = ''
    _todoSceneTemplate = ''
    _unusedSceneTemplate = ''
    _notExportedSceneTemplate = ''
    _sceneDivider = ''
    _chapterEndTemplate = ''
    _unusedChapterEndTemplate = ''
    _notExportedChapterEndTemplate = ''
    _notesChapterEndTemplate = ''
    _todoChapterEndTemplate = ''
    _characterSectionHeading = ''
    _characterTemplate = ''
    _locationSectionHeading = ''
    _locationTemplate = ''
    _itemSectionHeading = ''
    _itemTemplate = ''
    _fileFooter = ''
    _projectNoteTemplate = ''

    _DIVIDER = ', '

    def __init__(self, filePath, **kwargs):
        """Initialize filter strategy class instances.
        
        Positional arguments:
            filePath -- str: path to the file represented by the File instance.
            
        Optional arguments:
            kwargs -- keyword arguments to be used by subclasses.            

        Extends the superclass constructor.
        """
        super().__init__(filePath, **kwargs)
        self._sceneFilter = Filter()
        self._chapterFilter = Filter()
        self._characterFilter = Filter()
        self._locationFilter = Filter()
        self._itemFilter = Filter()

    def _get_fileHeaderMapping(self):
        """Return a mapping dictionary for the project section.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        projectTemplateMapping = dict(
            Title=self._convert_from_yw(self.novel.title, True),
            Desc=self._convert_from_yw(self.novel.desc),
            AuthorName=self._convert_from_yw(self.novel.authorName, True),
            AuthorBio=self._convert_from_yw(self.novel.authorBio, True),
            FieldTitle1=self._convert_from_yw(self.novel.fieldTitle1, True),
            FieldTitle2=self._convert_from_yw(self.novel.fieldTitle2, True),
            FieldTitle3=self._convert_from_yw(self.novel.fieldTitle3, True),
            FieldTitle4=self._convert_from_yw(self.novel.fieldTitle4, True),
            Language=self.novel.languageCode,
            Country=self.novel.countryCode,
        )
        return projectTemplateMapping

    def _get_chapterMapping(self, chId, chapterNumber):
        """Return a mapping dictionary for a chapter section.
        
        Positional arguments:
            chId -- str: chapter ID.
            chapterNumber -- int: chapter number.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        if chapterNumber == 0:
            chapterNumber = ''

        chapterMapping = dict(
            ID=chId,
            ChapterNumber=chapterNumber,
            Title=self._convert_from_yw(self.novel.chapters[chId].title, True),
            Desc=self._convert_from_yw(self.novel.chapters[chId].desc),
            ProjectName=self._convert_from_yw(self.projectName, True),
            ProjectPath=self.projectPath,
            Language=self.novel.languageCode,
            Country=self.novel.countryCode,
        )
        return chapterMapping

    def _get_sceneMapping(self, scId, sceneNumber, wordsTotal, lettersTotal):
        """Return a mapping dictionary for a scene section.
        
        Positional arguments:
            scId -- str: scene ID.
            sceneNumber -- int: scene number to be displayed.
            wordsTotal -- int: accumulated wordcount.
            lettersTotal -- int: accumulated lettercount.
        
        This is a template method that can be extended or overridden by subclasses.
        """

        #--- Create a comma separated tag list.
        if sceneNumber == 0:
            sceneNumber = ''
        if self.novel.scenes[scId].tags is not None:
            tags = list_to_string(self.novel.scenes[scId].tags, divider=self._DIVIDER)
        else:
            tags = ''

        #--- Create a comma separated character list.
        try:
            # Note: Due to a bug, yWriter scenes might hold invalid
            # viepoint characters
            sChList = []
            for crId in self.novel.scenes[scId].characters:
                sChList.append(self.novel.characters[crId].title)
            sceneChars = list_to_string(sChList, divider=self._DIVIDER)
            viewpointChar = sChList[0]
        except:
            sceneChars = ''
            viewpointChar = ''

        #--- Create a comma separated location list.
        if self.novel.scenes[scId].locations is not None:
            sLcList = []
            for lcId in self.novel.scenes[scId].locations:
                sLcList.append(self.novel.locations[lcId].title)
            sceneLocs = list_to_string(sLcList, divider=self._DIVIDER)
        else:
            sceneLocs = ''

        #--- Create a comma separated item list.
        if self.novel.scenes[scId].items is not None:
            sItList = []
            for itId in self.novel.scenes[scId].items:
                sItList.append(self.novel.items[itId].title)
            sceneItems = list_to_string(sItList, divider=self._DIVIDER)
        else:
            sceneItems = ''

        #--- Create A/R marker string.
        if self.novel.scenes[scId].isReactionScene:
            reactionScene = Scene.REACTION_MARKER
        else:
            reactionScene = Scene.ACTION_MARKER

        #--- Date or day.
        if self.novel.scenes[scId].date is not None and self.novel.scenes[scId].date != Scene.NULL_DATE:
            scDay = ''
            scDate = self.novel.scenes[scId].date
            cmbDate = self.novel.scenes[scId].date
        else:
            scDate = ''
            if self.novel.scenes[scId].day is not None:
                scDay = self.novel.scenes[scId].day
                cmbDate = f'Day {self.novel.scenes[scId].day}'
            else:
                scDay = ''
                cmbDate = ''

        #--- Time.
        if self.novel.scenes[scId].time is not None:
            scTime = self.novel.scenes[scId].time.rsplit(':', 1)[0]
            # remove seconds
        else:
            scTime = ''

        #--- Create a combined duration information.
        if self.novel.scenes[scId].lastsDays is not None and self.novel.scenes[scId].lastsDays != '0':
            lastsDays = self.novel.scenes[scId].lastsDays
            days = f'{self.novel.scenes[scId].lastsDays}d '
        else:
            lastsDays = ''
            days = ''
        if self.novel.scenes[scId].lastsHours is not None and self.novel.scenes[scId].lastsHours != '0':
            lastsHours = self.novel.scenes[scId].lastsHours
            hours = f'{self.novel.scenes[scId].lastsHours}h '
        else:
            lastsHours = ''
            hours = ''
        if self.novel.scenes[scId].lastsMinutes is not None and self.novel.scenes[scId].lastsMinutes != '0':
            lastsMinutes = self.novel.scenes[scId].lastsMinutes
            minutes = f'{self.novel.scenes[scId].lastsMinutes}min'
        else:
            lastsMinutes = ''
            minutes = ''
        duration = f'{days}{hours}{minutes}'

        sceneMapping = dict(
            ID=scId,
            SceneNumber=sceneNumber,
            Title=self._convert_from_yw(self.novel.scenes[scId].title, True),
            Desc=self._convert_from_yw(self.novel.scenes[scId].desc),
            WordCount=str(self.novel.scenes[scId].wordCount),
            WordsTotal=wordsTotal,
            LetterCount=str(self.novel.scenes[scId].letterCount),
            LettersTotal=lettersTotal,
            Status=Scene.STATUS[self.novel.scenes[scId].status],
            SceneContent=self._convert_from_yw(self.novel.scenes[scId].sceneContent),
            FieldTitle1=self._convert_from_yw(self.novel.fieldTitle1, True),
            FieldTitle2=self._convert_from_yw(self.novel.fieldTitle2, True),
            FieldTitle3=self._convert_from_yw(self.novel.fieldTitle3, True),
            FieldTitle4=self._convert_from_yw(self.novel.fieldTitle4, True),
            Field1=self.novel.scenes[scId].field1,
            Field2=self.novel.scenes[scId].field2,
            Field3=self.novel.scenes[scId].field3,
            Field4=self.novel.scenes[scId].field4,
            Date=scDate,
            Time=scTime,
            Day=scDay,
            ScDate=cmbDate,
            LastsDays=lastsDays,
            LastsHours=lastsHours,
            LastsMinutes=lastsMinutes,
            Duration=duration,
            ReactionScene=reactionScene,
            Goal=self._convert_from_yw(self.novel.scenes[scId].goal),
            Conflict=self._convert_from_yw(self.novel.scenes[scId].conflict),
            Outcome=self._convert_from_yw(self.novel.scenes[scId].outcome),
            Tags=self._convert_from_yw(tags, True),
            Image=self.novel.scenes[scId].image,
            Characters=sceneChars,
            Viewpoint=viewpointChar,
            Locations=sceneLocs,
            Items=sceneItems,
            Notes=self._convert_from_yw(self.novel.scenes[scId].notes),
            ProjectName=self._convert_from_yw(self.projectName, True),
            ProjectPath=self.projectPath,
            Language=self.novel.languageCode,
            Country=self.novel.countryCode,
        )
        return sceneMapping

    def _get_characterMapping(self, crId):
        """Return a mapping dictionary for a character section.
        
        Positional arguments:
            crId -- str: character ID.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        if self.novel.characters[crId].tags is not None:
            tags = list_to_string(self.novel.characters[crId].tags, divider=self._DIVIDER)
        else:
            tags = ''
        if self.novel.characters[crId].isMajor:
            characterStatus = Character.MAJOR_MARKER
        else:
            characterStatus = Character.MINOR_MARKER

        characterMapping = dict(
            ID=crId,
            Title=self._convert_from_yw(self.novel.characters[crId].title, True),
            Desc=self._convert_from_yw(self.novel.characters[crId].desc),
            Tags=self._convert_from_yw(tags),
            Image=self.novel.characters[crId].image,
            AKA=self._convert_from_yw(self.novel.characters[crId].aka, True),
            Notes=self._convert_from_yw(self.novel.characters[crId].notes),
            Bio=self._convert_from_yw(self.novel.characters[crId].bio),
            Goals=self._convert_from_yw(self.novel.characters[crId].goals),
            FullName=self._convert_from_yw(self.novel.characters[crId].fullName, True),
            Status=characterStatus,
            ProjectName=self._convert_from_yw(self.projectName),
            ProjectPath=self.projectPath,
        )
        return characterMapping

    def _get_locationMapping(self, lcId):
        """Return a mapping dictionary for a location section.
        
        Positional arguments:
            lcId -- str: location ID.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        if self.novel.locations[lcId].tags is not None:
            tags = list_to_string(self.novel.locations[lcId].tags, divider=self._DIVIDER)
        else:
            tags = ''

        locationMapping = dict(
            ID=lcId,
            Title=self._convert_from_yw(self.novel.locations[lcId].title, True),
            Desc=self._convert_from_yw(self.novel.locations[lcId].desc),
            Tags=self._convert_from_yw(tags, True),
            Image=self.novel.locations[lcId].image,
            AKA=self._convert_from_yw(self.novel.locations[lcId].aka, True),
            ProjectName=self._convert_from_yw(self.projectName, True),
            ProjectPath=self.projectPath,
        )
        return locationMapping

    def _get_itemMapping(self, itId):
        """Return a mapping dictionary for an item section.
        
        Positional arguments:
            itId -- str: item ID.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        if self.novel.items[itId].tags is not None:
            tags = list_to_string(self.novel.items[itId].tags, divider=self._DIVIDER)
        else:
            tags = ''

        itemMapping = dict(
            ID=itId,
            Title=self._convert_from_yw(self.novel.items[itId].title, True),
            Desc=self._convert_from_yw(self.novel.items[itId].desc),
            Tags=self._convert_from_yw(tags, True),
            Image=self.novel.items[itId].image,
            AKA=self._convert_from_yw(self.novel.items[itId].aka, True),
            ProjectName=self._convert_from_yw(self.projectName, True),
            ProjectPath=self.projectPath,
        )
        return itemMapping

    def _get_prjNoteMapping(self, pnId):
        """Return a mapping dictionary for a project note.
        
        Positional arguments:
            pnId -- str: project note ID.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        itemMapping = dict(
            ID=pnId,
            Title=self._convert_from_yw(self.novel.projectNotes[pnId].title, True),
            Desc=self._convert_from_yw(self.novel.projectNotes[pnId].desc, True),
            ProjectName=self._convert_from_yw(self.projectName, True),
            ProjectPath=self.projectPath,
        )
        return itemMapping

    def _get_fileHeader(self):
        """Process the file header.
        
        Apply the file header template, substituting placeholders 
        according to the file header mapping dictionary.
        Return a list of strings.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        lines = []
        template = Template(self._fileHeader)
        lines.append(template.safe_substitute(self._get_fileHeaderMapping()))
        return lines

    def _get_scenes(self, chId, sceneNumber, wordsTotal, lettersTotal, doNotExport):
        """Process the scenes.
        
        Positional arguments:
            chId -- str: chapter ID.
            sceneNumber -- int: number of previously processed scenes.
            wordsTotal -- int: accumulated wordcount of the previous scenes.
            lettersTotal -- int: accumulated lettercount of the previous scenes.
            doNotExport -- bool: scene belongs to a chapter that is not to be exported.
        
        Iterate through a sorted scene list and apply the templates, 
        substituting placeholders according to the scene mapping dictionary.
        Skip scenes not accepted by the scene filter.
        
        Return a tuple:
            lines -- list of strings: the lines of the processed scene.
            sceneNumber -- int: number of all processed scenes.
            wordsTotal -- int: accumulated wordcount of all processed scenes.
            lettersTotal -- int: accumulated lettercount of all processed scenes.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        lines = []
        firstSceneInChapter = True
        for scId in self.novel.chapters[chId].srtScenes:
            dispNumber = 0
            if not self._sceneFilter.accept(self, scId):
                continue

            sceneContent = self.novel.scenes[scId].sceneContent
            if sceneContent is None:
                sceneContent = ''

            # The order counts; be aware that "Todo" and "Notes" scenes are
            # always unused.
            if self.novel.scenes[scId].scType == 2:
                if self._todoSceneTemplate:
                    template = Template(self._todoSceneTemplate)
                else:
                    continue

            elif self.novel.scenes[scId].scType == 1:
                # Scene is "Notes" type.
                if self._notesSceneTemplate:
                    template = Template(self._notesSceneTemplate)
                else:
                    continue

            elif self.novel.scenes[scId].scType == 3 or self.novel.chapters[chId].chType == 3:
                if self._unusedSceneTemplate:
                    template = Template(self._unusedSceneTemplate)
                else:
                    continue

            elif self.novel.scenes[scId].doNotExport or doNotExport:
                if self._notExportedSceneTemplate:
                    template = Template(self._notExportedSceneTemplate)
                else:
                    continue

            elif sceneContent.startswith('<HTML>'):
                continue

            elif sceneContent.startswith('<TEX>'):
                continue

            else:
                sceneNumber += 1
                dispNumber = sceneNumber
                wordsTotal += self.novel.scenes[scId].wordCount
                lettersTotal += self.novel.scenes[scId].letterCount
                template = Template(self._sceneTemplate)
                if not firstSceneInChapter and self.novel.scenes[scId].appendToPrev and self._appendedSceneTemplate:
                    template = Template(self._appendedSceneTemplate)
            if not (firstSceneInChapter or self.novel.scenes[scId].appendToPrev):
                lines.append(self._sceneDivider)
            if firstSceneInChapter and self._firstSceneTemplate:
                template = Template(self._firstSceneTemplate)
            lines.append(template.safe_substitute(self._get_sceneMapping(
                        scId, dispNumber, wordsTotal, lettersTotal)))
            firstSceneInChapter = False
        return lines, sceneNumber, wordsTotal, lettersTotal

    def _get_chapters(self):
        """Process the chapters and nested scenes.
        
        Iterate through the sorted chapter list and apply the templates, 
        substituting placeholders according to the chapter mapping dictionary.
        For each chapter call the processing of its included scenes.
        Skip chapters not accepted by the chapter filter.
        Return a list of strings.
        This is a template method that can be extended or overridden by subclasses.
        """
        lines = []
        chapterNumber = 0
        sceneNumber = 0
        wordsTotal = 0
        lettersTotal = 0
        for chId in self.novel.srtChapters:
            dispNumber = 0
            if not self._chapterFilter.accept(self, chId):
                continue

            # The order counts; be aware that "Todo" and "Notes" chapters are
            # always unused.
            # Has the chapter only scenes not to be exported?
            sceneCount = 0
            notExportCount = 0
            doNotExport = False
            template = None
            for scId in self.novel.chapters[chId].srtScenes:
                sceneCount += 1
                if self.novel.scenes[scId].doNotExport:
                    notExportCount += 1
            if sceneCount > 0 and notExportCount == sceneCount:
                doNotExport = True
            if self.novel.chapters[chId].chType == 2:
                # Chapter is "Todo" type.
                if self.novel.chapters[chId].chLevel == 1:
                    # Chapter is "Todo Part" type.
                    if self._todoPartTemplate:
                        template = Template(self._todoPartTemplate)
                elif self._todoChapterTemplate:
                    template = Template(self._todoChapterTemplate)
            elif self.novel.chapters[chId].chType == 1:
                # Chapter is "Notes" type.
                if self.novel.chapters[chId].chLevel == 1:
                    # Chapter is "Notes Part" type.
                    if self._notesPartTemplate:
                        template = Template(self._notesPartTemplate)
                elif self._notesChapterTemplate:
                    template = Template(self._notesChapterTemplate)
            elif self.novel.chapters[chId].chType == 3:
                # Chapter is "unused" type.
                if self._unusedChapterTemplate:
                    template = Template(self._unusedChapterTemplate)
            elif doNotExport:
                if self._notExportedChapterTemplate:
                    template = Template(self._notExportedChapterTemplate)
            elif self.novel.chapters[chId].chLevel == 1 and self._partTemplate:
                template = Template(self._partTemplate)
            else:
                template = Template(self._chapterTemplate)
                chapterNumber += 1
                dispNumber = chapterNumber
            if template is not None:
                lines.append(template.safe_substitute(self._get_chapterMapping(chId, dispNumber)))

            #--- Process scenes.
            sceneLines, sceneNumber, wordsTotal, lettersTotal = self._get_scenes(
                chId, sceneNumber, wordsTotal, lettersTotal, doNotExport)
            lines.extend(sceneLines)

            #--- Process chapter ending.
            template = None
            if self.novel.chapters[chId].chType == 2:
                if self._todoChapterEndTemplate:
                    template = Template(self._todoChapterEndTemplate)
            elif self.novel.chapters[chId].chType == 1:
                if self._notesChapterEndTemplate:
                    template = Template(self._notesChapterEndTemplate)
            elif self.novel.chapters[chId].chType == 3:
                if self._unusedChapterEndTemplate:
                    template = Template(self._unusedChapterEndTemplate)
            elif doNotExport:
                if self._notExportedChapterEndTemplate:
                    template = Template(self._notExportedChapterEndTemplate)
            elif self._chapterEndTemplate:
                template = Template(self._chapterEndTemplate)
            if template is not None:
                lines.append(template.safe_substitute(self._get_chapterMapping(chId, dispNumber)))
        return lines

    def _get_characters(self):
        """Process the characters.
        
        Iterate through the sorted character list and apply the template, 
        substituting placeholders according to the character mapping dictionary.
        Skip characters not accepted by the character filter.
        Return a list of strings.
        This is a template method that can be extended or overridden by subclasses.
        """
        if self._characterSectionHeading:
            lines = [self._characterSectionHeading]
        else:
            lines = []
        template = Template(self._characterTemplate)
        for crId in self.novel.srtCharacters:
            if self._characterFilter.accept(self, crId):
                lines.append(template.safe_substitute(self._get_characterMapping(crId)))
        return lines

    def _get_locations(self):
        """Process the locations.
        
        Iterate through the sorted location list and apply the template, 
        substituting placeholders according to the location mapping dictionary.
        Skip locations not accepted by the location filter.
        Return a list of strings.
        This is a template method that can be extended or overridden by subclasses.
        """
        if self._locationSectionHeading:
            lines = [self._locationSectionHeading]
        else:
            lines = []
        template = Template(self._locationTemplate)
        for lcId in self.novel.srtLocations:
            if self._locationFilter.accept(self, lcId):
                lines.append(template.safe_substitute(self._get_locationMapping(lcId)))
        return lines

    def _get_items(self):
        """Process the items. 
        
        Iterate through the sorted item list and apply the template, 
        substituting placeholders according to the item mapping dictionary.
        Skip items not accepted by the item filter.
        Return a list of strings.
        This is a template method that can be extended or overridden by subclasses.
        """
        if self._itemSectionHeading:
            lines = [self._itemSectionHeading]
        else:
            lines = []
        template = Template(self._itemTemplate)
        for itId in self.novel.srtItems:
            if self._itemFilter.accept(self, itId):
                lines.append(template.safe_substitute(self._get_itemMapping(itId)))
        return lines

    def _get_projectNotes(self):
        """Process the project notes. 
        
        Iterate through the sorted project note list and apply the template, 
        substituting placeholders according to the item mapping dictionary.
        Skip items not accepted by the item filter.
        Return a list of strings.
        This is a template method that can be extended or overridden by subclasses.
        """
        lines = []
        template = Template(self._projectNoteTemplate)
        for pnId in self.novel.srtPrjNotes:
            map = self._get_prjNoteMapping(pnId)
            lines.append(template.safe_substitute(map))
        return lines

    def _get_text(self):
        """Call all processing methods.
        
        Return a string to be written to the output file.
        This is a template method that can be extended or overridden by subclasses.
        """
        lines = self._get_fileHeader()
        lines.extend(self._get_chapters())
        lines.extend(self._get_characters())
        lines.extend(self._get_locations())
        lines.extend(self._get_items())
        lines.extend(self._get_projectNotes())
        lines.append(self._fileFooter)
        return ''.join(lines)

    def write(self):
        """Write instance variables to the export file.
        
        Create a template-based output file. 
        Return a message in case of success.
        Raise the "Error" exception in case of error. 
        """
        text = self._get_text()
        backedUp = False
        if os.path.isfile(self.filePath):
            try:
                os.replace(self.filePath, f'{self.filePath}.bak')
            except:
                raise Error(f'{_("Cannot overwrite file")}: "{norm_path(self.filePath)}".')
            else:
                backedUp = True
        try:
            with open(self.filePath, 'w', encoding='utf-8') as f:
                f.write(text)
        except:
            if backedUp:
                os.replace(f'{self.filePath}.bak', self.filePath)
            raise Error(f'{_("Cannot write file")}: "{norm_path(self.filePath)}".')

    def _convert_from_yw(self, text, quick=False):
        """Return text, converted from yw7 markup to target format.
        
        Positional arguments:
            text -- string to convert.
        
        Optional arguments:
            quick -- bool: if True, apply a conversion mode for one-liners without formatting.
        
        Overrides the superclass method.
        """
        if text is None:
            text = ''
        return(text)

    def _remove_inline_code(self, text):
        """Remove inline raw code from text and return the result."""
        if text:
            text = text.replace('<RTFBRK>', '')
            YW_SPECIAL_CODES = ('HTM', 'TEX', 'RTF', 'epub', 'mobi', 'rtfimg')
            for specialCode in YW_SPECIAL_CODES:
                text = re.sub(f'\<{specialCode} .+?\/{specialCode}\>', '', text)
        else:
            text = ''
        return text


class OdsParser:
    """An ODS document parser.
    
    Public methods:
        get_rows(filePath, cellsPerRow) -- Return rows and cells from an ODS document.
           
    Return a list of rows, containing lists of column cells.
    The PyWriter csv import classes thus can be reused.
    """

    def __init__(self):
        super().__init__()
        self._rows = []
        self._cells = []
        self._inCell = None
        self.__cellsPerRow = 0

    def get_rows(self, filePath, cellsPerRow):
        """Return a nested list with rows and cells from an ODS document.
        
        Positional arguments:
            filePath -- str: ODS document path.
            cellsPerRow -- int: Number of cells per row.
        
        First unzip the ODS file located at self.filePath, then parse content.xml.
        """
        namespaces = dict(
            office='urn:oasis:names:tc:opendocument:xmlns:office:1.0',
            text='urn:oasis:names:tc:opendocument:xmlns:text:1.0',
            table='urn:oasis:names:tc:opendocument:xmlns:table:1.0',
            )
        try:
            with zipfile.ZipFile(filePath, 'r') as odfFile:
                content = odfFile.read('content.xml')
        except:
            raise Error(f'{_("Cannot read file")}: "{norm_path(filePath)}".')

        root = ET.fromstring(content)

        #--- Parse 'content.xml'.
        body = root.find('office:body', namespaces)
        spreadsheet = body.find('office:spreadsheet', namespaces)
        table = spreadsheet.find('table:table', namespaces)
        rows = []
        for row in table.findall('table:table-row', namespaces):
            cells = []
            i = 0
            for cell in row.findall('table:table-cell', namespaces):
                content = ''
                if cell.find('text:p', namespaces) is not None:
                    paragraphs = []
                    for par in cell.findall('text:p', namespaces):
                        strippedText = ''.join(par.itertext())
                        paragraphs.append(strippedText)
                    content = '\n'.join(paragraphs)
                    cells.append(content)
                elif i > 0:
                    cells.append(content)
                else:
                    # The ID cell is empty.
                    break

                i += 1
                if i >= cellsPerRow:
                    # The cell is excess, created by Calc.
                    break

                # Add repeated cells.
                attribute = cell.get(f'{{{namespaces["table"]}}}number-columns-repeated')
                if attribute:
                    repeat = int(attribute) - 1
                    for j in range(repeat):
                        if i >= cellsPerRow:
                            # The cell is excess, created by Calc.
                            break

                        cells.append(content)
                        i += 1
            if cells:
                rows.append(cells)
                # print(cells)
        return rows



class OdsReader(File):
    """Generic OpenDocument spreadsheet document reader.

    Public methods:
        read() -- parse the file and get the instance variables.

    """
    EXTENSION = '.ods'
    # overwrites File.EXTENSION
    _SEPARATOR = ','
    # delimits data fields within a record.
    _rowTitles = []

    _DIVIDER = FileExport._DIVIDER

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.

        Positional arguments:
            filePath -- str: path to the file represented by the File instance.
            
        Optional arguments:
            kwargs -- keyword arguments to be used by subclasses.            
        
        Extends the superclass constructor.
        """
        super().__init__(filePath)
        self._rows = []

    def read(self):
        """Parse the file and get the instance variables.
        
        Parse the ODS file located at filePath, fetching the rows.
        Check the number of fields in each row.
        Raise the "Error" exception in case of error. 
        Overrides the superclass method.
        """
        self._rows = []
        cellsPerRow = len(self._rowTitles)
        reader = OdsParser()
        self._rows = reader.get_rows(self.filePath, cellsPerRow)
        for row in self._rows:
            if len(row) != cellsPerRow:
                print(row)
                print(len(row), cellsPerRow)
                raise Error(f'{_("Wrong table structure")}.')



class OdsRSceneList(OdsReader):
    """ODS scene list reader. 
    
    Public methods:
        read() -- parse the file and get the instance variables.
    """
    DESCRIPTION = _('Scene list')
    SUFFIX = '_scenelist'
    _SCENE_RATINGS = ['2', '3', '4', '5', '6', '7', '8', '9', '10']
    # '1' is assigned N/A (empty table cell).
    _rowTitles = ['Scene link', 'Scene title', 'Scene description', 'Tags', 'Scene notes', 'A/R',
                 'Goal', 'Conflict', 'Outcome', 'Scene', 'Words total',
                 '$FieldTitle1', '$FieldTitle2', '$FieldTitle3', '$FieldTitle4',
                 'Word count', 'Letter count', 'Status', 'Characters', 'Locations', 'Items']

    def read(self):
        """Parse the file and get the instance variables.
        
        Parse the csv file located at filePath, fetching the Scene attributes contained.
        Extends the superclass method.
        """
        super().read()
        for cells in self._rows:
            i = 0
            if 'ScID:' in cells[i]:
                scId = re.search('ScID\:([0-9]+)', cells[0]).group(1)
                if not scId in self.novel.scenes:
                    self.novel.scenes[scId] = Scene()
                i += 1
                self.novel.scenes[scId].title = self._convert_to_yw(cells[i])
                i += 1
                self.novel.scenes[scId].desc = self._convert_to_yw(cells[i])
                i += 1
                if cells[i] or self.novel.scenes[scId].tags:
                    self.novel.scenes[scId].tags = string_to_list(cells[i], divider=self._DIVIDER)
                i += 1
                if cells[i] or self.novel.scenes[scId].notes:
                    self.novel.scenes[scId].notes = self._convert_to_yw(cells[i])
                i += 1
                if Scene.REACTION_MARKER.lower() in cells[i].lower():
                    self.novel.scenes[scId].isReactionScene = True
                else:
                    self.novel.scenes[scId].isReactionScene = False
                i += 1
                if cells[i] or self.novel.scenes[scId].goal:
                    self.novel.scenes[scId].goal = self._convert_to_yw(cells[i])
                i += 1
                if cells[i] or self.novel.scenes[scId].conflict:
                    self.novel.scenes[scId].conflict = self._convert_to_yw(cells[i])
                i += 1
                if cells[i] or self.novel.scenes[scId].outcome:
                    self.novel.scenes[scId].outcome = self._convert_to_yw(cells[i])
                i += 1
                # Don't write back sceneCount
                i += 1
                # Don't write back wordCount
                i += 1

                # Transfer scene ratings; set to 1 if deleted
                if cells[i] in self._SCENE_RATINGS:
                    self.novel.scenes[scId].field1 = self._convert_to_yw(cells[i])
                else:
                    self.novel.scenes[scId].field1 = '1'
                i += 1
                if cells[i] in self._SCENE_RATINGS:
                    self.novel.scenes[scId].field2 = self._convert_to_yw(cells[i])
                else:
                    self.novel.scenes[scId].field2 = '1'
                i += 1
                if cells[i] in self._SCENE_RATINGS:
                    self.novel.scenes[scId].field3 = self._convert_to_yw(cells[i])
                else:
                    self.novel.scenes[scId].field3 = '1'
                i += 1
                if cells[i] in self._SCENE_RATINGS:
                    self.novel.scenes[scId].field4 = self._convert_to_yw(cells[i])
                else:
                    self.novel.scenes[scId].field4 = '1'
                i += 1
                # Don't write back scene words total
                i += 1
                # Don't write back scene letters total
                i += 1
                try:
                    self.novel.scenes[scId].status = Scene.STATUS.index(cells[i])
                except ValueError:
                    pass
                    # Scene status remains None and will be ignored when
                    # writing back.
                i += 1
                # Can't write back character IDs, because self.characters is None.
                i += 1
                # Can't write back location IDs, because self.locations is None.
                i += 1
                # Can't write back item IDs, because self.items is None.


class OdsRCharList(OdsReader):
    """ODS character list reader. 
    
    Public methods:
        read() -- parse the file and get the instance variables.
    """
    DESCRIPTION = _('Character list')
    SUFFIX = '_charlist'
    _rowTitles = ['ID', 'Name', 'Full name', 'Aka', 'Description', 'Bio', 'Goals', 'Importance', 'Tags', 'Notes']

    def read(self):
        """Parse the file and get the instance variables.
        
        Parse the csv file located at filePath, fetching the Character attributes contained.
        Raise the "Error" exception in case of error. 
        Extends the superclass method.
        """
        super().read()
        self.novel.srtCharacters = []
        for cells in self._rows:
            if 'CrID:' in cells[0]:
                crId = re.search('CrID\:([0-9]+)', cells[0]).group(1)
                self.novel.srtCharacters.append(crId)
                if not crId in self.novel.characters:
                    self.novel.characters[crId] = Character()
                if self.novel.characters[crId].title or cells[1]:
                    self.novel.characters[crId].title = cells[1]
                if self.novel.characters[crId].fullName or cells[2]:
                    self.novel.characters[crId].fullName = cells[2]
                if self.novel.characters[crId].aka or cells[3]:
                    self.novel.characters[crId].aka = cells[3]
                if self.novel.characters[crId].desc or cells[4]:
                    self.novel.characters[crId].desc = self._convert_to_yw(cells[4])
                if self.novel.characters[crId].bio or cells[5]:
                    self.novel.characters[crId].bio = self._convert_to_yw(cells[5])
                if self.novel.characters[crId].goals  or cells[6]:
                    self.novel.characters[crId].goals = self._convert_to_yw(cells[6])
                if Character.MAJOR_MARKER in cells[7]:
                    self.novel.characters[crId].isMajor = True
                else:
                    self.novel.characters[crId].isMajor = False
                if self.novel.characters[crId].tags or cells[8]:
                    self.novel.characters[crId].tags = string_to_list(cells[8], divider=self._DIVIDER)
                if self.novel.characters[crId].notes or cells[9]:
                    self.novel.characters[crId].notes = self._convert_to_yw(cells[9])


class OdsRLocList(OdsReader):
    """ODS location list reader. 
    
    Public methods:
        read() -- parse the file and get the instance variables.
    """
    DESCRIPTION = _('Location list')
    SUFFIX = '_loclist'
    _rowTitles = ['ID', 'Name', 'Description', 'Aka', 'Tags']

    def read(self):
        """Parse the file and get the instance variables.
        
        Parse the csv file located at filePath, fetching the location attributes contained.
        Raise the "Error" exception in case of error. 
        Extends the superclass method.
        """
        super().read()
        self.novel.srtLocations = []
        for cells in self._rows:
            if 'LcID:' in cells[0]:
                lcId = re.search('LcID\:([0-9]+)', cells[0]).group(1)
                self.novel.srtLocations.append(lcId)
                if not lcId in self.novel.locations:
                    self.novel.locations[lcId] = WorldElement()
                if self.novel.locations[lcId].title or cells[1]:
                    self.novel.locations[lcId].title = self._convert_to_yw(cells[1])
                if self.novel.locations[lcId].desc or cells[2]:
                    self.novel.locations[lcId].desc = self._convert_to_yw(cells[2])
                if self.novel.locations[lcId].aka or cells[3]:
                    self.novel.locations[lcId].aka = self._convert_to_yw(cells[3])
                if self.novel.locations[lcId].tags or cells[4]:
                    self.novel.locations[lcId].tags = string_to_list(cells[4], divider=self._DIVIDER)


class OdsRItemList(OdsReader):
    """ODS item list reader.
    
    Public methods:
        read() -- parse the file and get the instance variables.
    """
    DESCRIPTION = _('Item list')
    SUFFIX = '_itemlist'
    _rowTitles = ['ID', 'Name', 'Description', 'Aka', 'Tags']

    def read(self):
        """Parse the file and get the instance variables.
        
        Parse the csv file located at filePath, fetching the item attributes contained.
        Raise the "Error" exception in case of error. 
        Extends the superclass method.
        """
        super().read()
        self.novel.srtItems = []
        for cells in self._rows:
            if 'ItID:' in cells[0]:
                itId = re.search('ItID\:([0-9]+)', cells[0]).group(1)
                self.novel.srtItems.append(itId)
                if not itId in self.novel.items:
                    self.novel.items[itId] = WorldElement()
                if self.novel.items[itId].title or cells[1]:
                    self.novel.items[itId].title = self._convert_to_yw(cells[1])
                if self.novel.items[itId].desc or cells[2]:
                    self.novel.items[itId].desc = self._convert_to_yw(cells[2])
                if self.novel.items[itId].aka or cells[3]:
                    self.novel.items[itId].aka = self._convert_to_yw(cells[3])
                if self.novel.items[itId].tags or cells[4]:
                    self.novel.items[itId].tags = string_to_list(cells[4], divider=self._DIVIDER)


class Yw7Importer(YwCnvFf):
    """A converter for universal import.

    Support yWriter 7 projects and most of the Novel subclasses 
    that can be read or written by OpenOffice/LibreOffice.

    Overrides the superclass constants EXPORT_SOURCE_CLASSES,
    EXPORT_TARGET_CLASSES, IMPORT_SOURCE_CLASSES, IMPORT_TARGET_CLASSES.

    Class constants:
        CREATE_SOURCE_CLASSES -- list of classes that - additional to HtmlImport
                        and HtmlOutline - can be exported to a new yWriter project.
    """
    EXPORT_SOURCE_CLASSES = [Yw7File]
    IMPORT_SOURCE_CLASSES = [OdtRProof,
                             OdtRManuscript,
                             OdtRSceneDesc,
                             OdtRChapterDesc,
                             OdtRPartDesc,
                             OdtRCharacters,
                             OdtRItems,
                             OdtRLocations,
                             OdtRNotes,
                             OdtRTodo,
                             OdsRCharList,
                             OdsRLocList,
                             OdsRItemList,
                             OdsRSceneList,
                             ]
    IMPORT_TARGET_CLASSES = [Yw7File]
    CREATE_SOURCE_CLASSES = []

    def __init__(self):
        """Change the newProjectFactory strategy.
        
        Extends the superclass constructor.
        """
        super().__init__()
        self.newProjectFactory = NewProjectFactory(self.CREATE_SOURCE_CLASSES)
from com.sun.star.awt.MessageBoxResults import OK, YES, NO, CANCEL
from com.sun.star.awt.MessageBoxButtons import BUTTONS_OK, BUTTONS_OK_CANCEL, BUTTONS_YES_NO, BUTTONS_YES_NO_CANCEL, BUTTONS_RETRY_CANCEL, BUTTONS_ABORT_IGNORE_RETRY
from com.sun.star.awt.MessageBoxType import MESSAGEBOX, INFOBOX, WARNINGBOX, ERRORBOX, QUERYBOX


class UiUno(Ui):
    """UI subclass implementing a LibreOffice UNO facade."""

    def ask_yes_no(self, text):
        result = msgbox(text, buttons=BUTTONS_YES_NO, type_msg=WARNINGBOX)
        return result == YES

    def set_info_how(self, message):
        """How's the converter doing?"""
        self.infoHowText = message
        if message.startswith('!'):
            message = message.split('!', maxsplit=1)[1].strip()
            msgbox(message, type_msg=ERRORBOX)
        else:
            msgbox(message, type_msg=INFOBOX)

    def show_warning(self, message):
        """Display a warning message box."""
        msgbox(message, buttons=BUTTONS_OK, type_msg=WARNINGBOX)



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

