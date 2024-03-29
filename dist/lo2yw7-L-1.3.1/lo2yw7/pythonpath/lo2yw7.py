"""Convert odt/ods to yw7. 

Version 1.3.1
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
    pass


oPackageInfoProvider = CTX.getByName("/singletons/com.sun.star.deployment.PackageInformationProvider")
sPackageLocation = oPackageInfoProvider.getPackageLocation("org.peter88213.lo2yw7")
packagePath = uno.fileUrlToSystemPath(sPackageLocation)
LOCALE_PATH = f'{packagePath}/lo2yw7/locale/'
try:
    CURRENT_LANGUAGE = locale.getlocale()[0][:2]
except:
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
    try:
        text = divider.join(elements)
        return text

    except:
        return ''



def msgbox(message, title=_('Export to yw7'), buttons=BUTTONS_OK, type_msg=INFOBOX):
    toolkit = create_instance('com.sun.star.awt.Toolkit')
    parent = toolkit.getDesktopWindow()
    mb = toolkit.createMessageBox(parent, type_msg, buttons, title, str(message))
    return mb.execute()



def open_document(document):
    try:
        os.startfile(norm_path(document))
    except:
        try:
            os.system('xdg-open "%s"' % norm_path(document))
        except:
            try:
                os.system('open "%s"' % norm_path(document))
            except:
                pass


class Ui:

    def __init__(self, title):
        self.infoWhatText = ''
        self.infoHowText = ''

    def ask_yes_no(self, text):
        return True

    def set_info_how(self, message):
        if message.startswith('!'):
            message = f'FAIL: {message.split("!", maxsplit=1)[1].strip()}'
            sys.stderr.write(message)
        self.infoHowText = message

    def set_info_what(self, message):
        self.infoWhatText = message

    def show_warning(self, message):
        pass

    def start(self):
        pass

import re
from typing import Iterator, Pattern


class BasicElement:

    def __init__(self):
        self.title: str = None

        self.desc: str = None

        self.kwVar: dict[str, str] = {}


class Chapter(BasicElement):

    def __init__(self):
        super().__init__()

        self.chLevel: int = None

        self.chType: int = None

        self.suppressChapterTitle: bool = None

        self.isTrash: bool = None

        self.suppressChapterBreak: bool = None

        self.srtScenes: list[str] = []
from typing import Pattern


ADDITIONAL_WORD_LIMITS: Pattern = re.compile('--|—|–')

NO_WORD_LIMITS: Pattern = re.compile('\[.+?\]|\/\*.+?\*\/|-|^\>', re.MULTILINE)

NON_LETTERS: Pattern = re.compile('\[.+?\]|\/\*.+?\*\/|\n|\r')


class Scene(BasicElement):
    STATUS: set = (None, 'Outline', 'Draft', '1st Edit', '2nd Edit', 'Done')

    ACTION_MARKER: str = 'A'
    REACTION_MARKER: str = 'R'
    NULL_DATE: str = '0001-01-01'
    NULL_TIME: str = '00:00:00'

    def __init__(self):
        super().__init__()

        self._sceneContent: str = None

        self.wordCount: int = 0

        self.letterCount: int = 0

        self.scType: int = None

        self.doNotExport: bool = None

        self.status: int = None

        self.notes: str = None

        self.tags: list[str] = None

        self.field1: str = None

        self.field2: str = None

        self.field3: str = None

        self.field4: str = None

        self.appendToPrev: bool = None

        self.isReactionScene: bool = None

        self.isSubPlot: bool = None

        self.goal: str = None

        self.conflict: str = None

        self.outcome: str = None

        self.characters: list[str] = None

        self.locations: list[str] = None

        self.items: list[str] = None

        self.date: str = None

        self.time: str = None

        self.day: str = None

        self.lastsMinutes: str = None

        self.lastsHours: str = None

        self.lastsDays: str = None

        self.image: str = None

        self.scnArcs: str = None

        self.scnStyle: str = None

    @property
    def sceneContent(self) -> str:
        return self._sceneContent

    @sceneContent.setter
    def sceneContent(self, text: str):
        self._sceneContent = text
        text = ADDITIONAL_WORD_LIMITS.sub(' ', text)
        text = NO_WORD_LIMITS.sub('', text)
        wordList = text.split()
        self.wordCount = len(wordList)
        text = NON_LETTERS.sub('', self._sceneContent)
        self.letterCount = len(text)


class WorldElement(BasicElement):

    def __init__(self):
        super().__init__()

        self.image: str = None

        self.tags: list[str] = None

        self.aka: str = None



class Character(WorldElement):
    MAJOR_MARKER: str = 'Major'
    MINOR_MARKER: str = 'Minor'

    def __init__(self):
        super().__init__()

        self.notes: str = None

        self.bio: str = None

        self.goals: str = None

        self.fullName: str = None

        self.isMajor: bool = None

LANGUAGE_TAG: Pattern = re.compile('\[lang=(.*?)\]')


class Novel(BasicElement):

    def __init__(self):
        super().__init__()

        self.authorName: str = None

        self.authorBio: str = None

        self.fieldTitle1: str = None

        self.fieldTitle2: str = None

        self.fieldTitle3: str = None

        self.fieldTitle4: str = None

        self.wordTarget: int = None

        self.wordCountStart: int = None

        self.wordTarget: int = None

        self.chapters: dict[str, Chapter] = {}

        self.scenes: dict[str, Scene] = {}

        self.languages: list[str] = None

        self.srtChapters: list[str] = []

        self.locations: dict[str, WorldElement] = {}

        self.srtLocations: list[str] = []

        self.items: dict[str, WorldElement] = {}

        self.srtItems: list[str] = []

        self.characters: dict[str, Character] = {}

        self.srtCharacters: list[str] = []

        self.projectNotes: dict[str, BasicElement] = {}

        self.srtPrjNotes: list[str] = []

        self.languageCode: str = None

        self.countryCode: str = None

    def get_languages(self):

        def languages(text: str) -> Iterator[str]:
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
        if not self.languageCode:
            try:
                sysLng, sysCtr = locale.getlocale()[0].split('_')
            except:
                sysLng, sysCtr = locale.getdefaultlocale()[0].split('_')
            self.languageCode = sysLng
            self.countryCode = sysCtr
            return

        try:
            if len(self.languageCode) == 2:
                if len(self.countryCode) == 2:
                    return
        except:
            pass
        self.languageCode = 'zxx'
        self.countryCode = 'none'



class YwCnvUi:

    def __init__(self):
        self.ui = Ui('')
        self.newFile = None

    def export_from_yw(self, source, target):
        self.ui.set_info_what(
            _('Input: {0} "{1}"\nOutput: {2} "{3}"').format(source.DESCRIPTION, norm_path(source.filePath), target.DESCRIPTION, norm_path(target.filePath)))
        try:
            self.check(source, target)
            source.novel = Novel()
            source.read()
            target.novel = source.novel
            target.write()
        except Exception as ex:
            message = f'!{str(ex)}'
            self.newFile = None
        else:
            message = f'{_("File written")}: "{norm_path(target.filePath)}".'
            self.newFile = target.filePath
        finally:
            self.ui.set_info_how(message)

    def create_yw7(self, source, target):
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
            except Exception as ex:
                message = f'!{str(ex)}'
                self.newFile = None
            else:
                message = f'{_("File written")}: "{norm_path(target.filePath)}".'
                self.newFile = target.filePath
            finally:
                self.ui.set_info_how(message)

    def import_to_yw(self, source, target):
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
        except Exception as ex:
            message = f'!{str(ex)}'
        else:
            message = f'{_("File written")}: "{norm_path(target.filePath)}".'
            self.newFile = target.filePath
            if source.scenesSplit:
                self.ui.show_warning(_('New scenes created during conversion.'))
        finally:
            self.ui.set_info_how(message)

    def _confirm_overwrite(self, filePath):
        return self.ui.ask_yes_no(_('Overwrite existing file "{}"?').format(norm_path(filePath)))

    def _open_newFile(self):
        open_document(self.newFile)
        sys.exit(0)

    def check(self, source, target):
        if source.filePath is None:
            raise Error(f'{_("File type is not supported")}.')

        if not os.path.isfile(source.filePath):
            raise Error(f'{_("File not found")}: "{norm_path(source.filePath)}".')

        if target.filePath is None:
            raise Error(f'{_("File type is not supported")}.')

        if os.path.isfile(target.filePath) and not self._confirm_overwrite(target.filePath):
            raise Error(f'{_("Action canceled by user")}.')



class FileFactory:

    def __init__(self, fileClasses=[]):
        self._fileClasses = fileClasses


class ExportSourceFactory(FileFactory):

    def make_file_objects(self, sourcePath, **kwargs):
        __, fileExtension = os.path.splitext(sourcePath)
        for fileClass in self._fileClasses:
            if fileClass.EXTENSION == fileExtension:
                sourceFile = fileClass(sourcePath, **kwargs)
                return sourceFile, None

        raise Error(f'{_("File type is not supported")}: "{norm_path(sourcePath)}".')


class ExportTargetFactory(FileFactory):

    def make_file_objects(self, sourcePath, **kwargs):
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

    def make_file_objects(self, sourcePath, **kwargs):
        for fileClass in self._fileClasses:
            if fileClass.SUFFIX is not None:
                if sourcePath.endswith(f'{fileClass.SUFFIX }{fileClass.EXTENSION}'):
                    sourceFile = fileClass(sourcePath, **kwargs)
                    return sourceFile, None

        raise Error(f'{_("This document is not meant to be written back")}.')


class ImportTargetFactory(FileFactory):

    def make_file_objects(self, sourcePath, **kwargs):
        fileName, __ = os.path.splitext(sourcePath)
        sourceSuffix = kwargs['suffix']
        if sourceSuffix:
            e = fileName.split(sourceSuffix)
            if len(e) > 1:
                e.pop()
            ywPathBasis = ''.join(e)
        else:
            ywPathBasis = fileName

        for fileClass in self._fileClasses:
            if os.path.isfile(f'{ywPathBasis}{fileClass.EXTENSION}'):
                targetFile = fileClass(f'{ywPathBasis}{fileClass.EXTENSION}', **kwargs)
                return None, targetFile

        raise Error(f'{_("No yWriter project to write")}.')


class YwCnvFf(YwCnvUi):
    EXPORT_SOURCE_CLASSES = []
    EXPORT_TARGET_CLASSES = []
    IMPORT_SOURCE_CLASSES = []
    IMPORT_TARGET_CLASSES = []

    def __init__(self):
        super().__init__()
        self.exportSourceFactory = ExportSourceFactory(self.EXPORT_SOURCE_CLASSES)
        self.exportTargetFactory = ExportTargetFactory(self.EXPORT_TARGET_CLASSES)
        self.importSourceFactory = ImportSourceFactory(self.IMPORT_SOURCE_CLASSES)
        self.importTargetFactory = ImportTargetFactory(self.IMPORT_TARGET_CLASSES)
        self.newProjectFactory = FileFactory()

    def run(self, sourcePath, **kwargs):
        self.newFile = None
        if not os.path.isfile(sourcePath):
            self.ui.set_info_how(f'!{_("File not found")}: "{norm_path(sourcePath)}".')
            return

        try:
            source, __ = self.exportSourceFactory.make_file_objects(sourcePath, **kwargs)
        except Error:
            try:
                source, __ = self.importSourceFactory.make_file_objects(sourcePath, **kwargs)
            except Error:
                try:
                    source, target = self.newProjectFactory.make_file_objects(sourcePath, **kwargs)
                except Error as ex:
                    self.ui.set_info_how(f'!{str(ex)}')
                else:
                    self.create_yw7(source, target)
            else:
                kwargs['suffix'] = source.SUFFIX
                try:
                    __, target = self.importTargetFactory.make_file_objects(sourcePath, **kwargs)
                except Error as ex:
                    self.ui.set_info_how(f'!{str(ex)}')
                else:
                    self.import_to_yw(source, target)
        else:
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
from urllib.parse import quote


class File:
    DESCRIPTION = _('File')
    EXTENSION = None
    SUFFIX = None

    PRJ_KWVAR = []
    CHP_KWVAR = []
    SCN_KWVAR = []
    CRT_KWVAR = []
    LOC_KWVAR = []
    ITM_KWVAR = []
    PNT_KWVAR = []

    def __init__(self, filePath, **kwargs):
        super().__init__()
        self.novel = None

        self._filePath = None

        self.projectName = None

        self.projectPath = None

        self.scenesSplit = False
        self.filePath = filePath

    @property
    def filePath(self):
        return self._filePath

    @filePath.setter
    def filePath(self, filePath):
        if self.SUFFIX is not None:
            suffix = self.SUFFIX
        else:
            suffix = ''
        if filePath.lower().endswith(f'{suffix}{self.EXTENSION}'.lower()):
            self._filePath = filePath
            try:
                head, tail = os.path.split(os.path.realpath(filePath))
            except:
                head, tail = os.path.split(filePath)
            self.projectPath = quote(head.replace('\\', '/'), '/:')
            self.projectName = quote(tail.replace(f'{suffix}{self.EXTENSION}', ''))

    def read(self):
        raise NotImplementedError

    def write(self):
        raise NotImplementedError

    def _convert_from_yw(self, text, quick=False):
        return text.rstrip()

    def _convert_to_yw(self, text):
        return text.rstrip()

from typing import Iterable


def create_id(elements: Iterable) -> str:
    i = 1
    while str(i) in elements:
        i += 1
    return str(i)



def indent(elem, level=0):
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
    DESCRIPTION = _('yWriter 7 project')
    EXTENSION = '.yw7'
    _CDATA_TAGS = ['Title', 'AuthorName', 'Bio', 'Desc',
                   'FieldTitle1', 'FieldTitle2', 'FieldTitle3',
                   'FieldTitle4', 'LaTeXHeaderFile', 'Tags',
                   'AKA', 'ImageFile', 'FullName', 'Goals',
                   'Notes', 'RTFFile', 'SceneContent',
                   'Outcome', 'Goal', 'Conflict']

    PRJ_KWVAR = [
        'Field_LanguageCode',
        'Field_CountryCode',
        ]
    SCN_KWVAR = [
        'Field_SceneArcs',
        'Field_SceneStyle',
        ]

    def __init__(self, filePath, **kwargs):
        super().__init__(filePath)
        self.tree = None

    def adjust_scene_types(self):
        for chId in self.novel.srtChapters:
            if self.novel.chapters[chId].chType != 0:
                for scId in self.novel.chapters[chId].srtScenes:
                    self.novel.scenes[scId].scType = self.novel.chapters[chId].chType

    def is_locked(self):
        return os.path.isfile(f'{self.filePath}.lock')

    def read(self):

        for field in self.PRJ_KWVAR:
            self.novel.kwVar[field] = None

        if self.is_locked():
            raise Error(f'{_("yWriter seems to be open. Please close first")}.')
        try:
            self.tree = ET.parse(self.filePath)
        except:
            raise Error(f'{_("Can not process file")}: "{norm_path(self.filePath)}".')

        root = self.tree.getroot()
        self._read_project(root)
        self._read_locations(root)
        self._read_items(root)
        self._read_characters(root)
        self._read_projectvars(root)
        self._read_projectnotes(root)
        self._read_scenes(root)
        self._read_chapters(root)
        self.adjust_scene_types()

        for scId in self.novel.scenes:
            self.novel.scenes[scId].scnArcs = self.novel.scenes[scId].kwVar.get('Field_SceneArcs', None)
            self.novel.scenes[scId].scnStyle = self.novel.scenes[scId].kwVar.get('Field_SceneStyle', None)

    def write(self):
        if self.is_locked():
            raise Error(f'{_("yWriter seems to be open. Please close first")}.')

        if self.novel.languages is None:
            self.novel.get_languages()

        for scId in self.novel.scenes:
            if self.novel.scenes[scId].scnArcs is not None:
                self.novel.scenes[scId].kwVar['Field_SceneArcs'] = self.novel.scenes[scId].scnArcs
            if self.novel.scenes[scId].scnStyle is not None:
                self.novel.scenes[scId].kwVar['Field_SceneStyle'] = self.novel.scenes[scId].scnStyle

        self._build_element_tree()
        self._write_element_tree(self)
        self._postprocess_xml_file(self.filePath)

    def _build_element_tree(self):

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

        def build_scene_subtree(xmlScene, prjScn):

            def remove_date_time():
                if xmlScene.find('SpecificDateTime') is not None:
                    xmlScene.remove(xmlScene.find('SpecificDateTime'))

                if xmlScene.find('SpecificDateMode') is not None:
                    xmlScene.remove(xmlScene.find('SpecificDateMode'))

                if xmlScene.find('Day') is not None:
                    xmlScene.remove(xmlScene.find('Day'))

                if xmlScene.find('Hour') is not None:
                    xmlScene.remove(xmlScene.find('Hour'))

                if xmlScene.find('Minute') is not None:
                    xmlScene.remove(xmlScene.find('Minute'))

            i = 1
            i = set_element(xmlScene, 'Title', prjScn.title, i)

            if xmlScene.find('BelongsToChID') is None:
                for chId in self.novel.chapters:
                    if scId in self.novel.chapters[chId].srtScenes:
                        ET.SubElement(xmlScene, 'BelongsToChID').text = chId
                        break

            if prjScn.desc is not None:
                try:
                    xmlScene.find('Desc').text = prjScn.desc
                except(AttributeError):
                    if prjScn.desc:
                        ET.SubElement(xmlScene, 'Desc').text = prjScn.desc

            if xmlScene.find('SceneContent') is None:
                ET.SubElement(xmlScene, 'SceneContent').text = prjScn.sceneContent

            if xmlScene.find('WordCount') is None:
                ET.SubElement(xmlScene, 'WordCount').text = str(prjScn.wordCount)

            if xmlScene.find('LetterCount') is None:
                ET.SubElement(xmlScene, 'LetterCount').text = str(prjScn.letterCount)


            scTypeEncoding = (
                (False, None),
                (True, '1'),
                (True, '2'),
                (True, '0'),
                )
            if prjScn.scType is None:
                prjScn.scType = 0
            yUnused, ySceneType = scTypeEncoding[prjScn.scType]

            if yUnused:
                if xmlScene.find('Unused') is None:
                    ET.SubElement(xmlScene, 'Unused').text = '-1'
            elif xmlScene.find('Unused') is not None:
                xmlScene.remove(xmlScene.find('Unused'))

            xmlSceneFields = xmlScene.find('Fields')
            if xmlSceneFields is not None:
                fieldScType = xmlSceneFields.find('Field_SceneType')
                if ySceneType is None:
                    if fieldScType is not None:
                        xmlSceneFields.remove(fieldScType)
                else:
                    try:
                        fieldScType.text = ySceneType
                    except(AttributeError):
                        ET.SubElement(xmlSceneFields, 'Field_SceneType').text = ySceneType
            elif ySceneType is not None:
                xmlSceneFields = ET.SubElement(xmlScene, 'Fields')
                ET.SubElement(xmlSceneFields, 'Field_SceneType').text = ySceneType

            if self.novel.scenes[scId].doNotExport is not None:
                xmlExportCondSpecific = xmlScene.find('ExportCondSpecific')
                xmlExportWhenRtf = xmlScene.find('ExportWhenRTF')
                if self.novel.scenes[scId].doNotExport:
                    if xmlExportCondSpecific is None:
                        xmlExportCondSpecific = ET.SubElement(xmlScene, 'ExportCondSpecific')
                    if xmlExportWhenRtf is not None:
                        xmlScene.remove(xmlExportWhenRtf)
                else:
                    if xmlExportCondSpecific is not None:
                        if xmlExportWhenRtf is None:
                            ET.SubElement(xmlScene, 'ExportWhenRTF').text = '-1'

            for field in self.SCN_KWVAR:
                if self.novel.scenes[scId].kwVar.get(field, None):
                    if xmlSceneFields is None:
                        xmlSceneFields = ET.SubElement(xmlScene, 'Fields')
                    try:
                        xmlSceneFields.find(field).text = self.novel.scenes[scId].kwVar[field]
                    except(AttributeError):
                        ET.SubElement(xmlSceneFields, field).text = self.novel.scenes[scId].kwVar[field]
                elif xmlSceneFields is not None:
                    try:
                        xmlSceneFields.remove(xmlSceneFields.find(field))
                    except:
                        pass

            if prjScn.status is not None:
                try:
                    xmlScene.find('Status').text = str(prjScn.status)
                except:
                    ET.SubElement(xmlScene, 'Status').text = str(prjScn.status)

            if prjScn.notes is not None:
                try:
                    xmlScene.find('Notes').text = prjScn.notes
                except(AttributeError):
                    if prjScn.notes:
                        ET.SubElement(xmlScene, 'Notes').text = prjScn.notes

            if prjScn.tags is not None:
                try:
                    xmlScene.find('Tags').text = list_to_string(prjScn.tags)
                except(AttributeError):
                    if prjScn.tags:
                        ET.SubElement(xmlScene, 'Tags').text = list_to_string(prjScn.tags)

            if prjScn.field1 is not None:
                try:
                    xmlScene.find('Field1').text = prjScn.field1
                except(AttributeError):
                    if prjScn.field1:
                        ET.SubElement(xmlScene, 'Field1').text = prjScn.field1

            if prjScn.field2 is not None:
                try:
                    xmlScene.find('Field2').text = prjScn.field2
                except(AttributeError):
                    if prjScn.field2:
                        ET.SubElement(xmlScene, 'Field2').text = prjScn.field2

            if prjScn.field3 is not None:
                try:
                    xmlScene.find('Field3').text = prjScn.field3
                except(AttributeError):
                    if prjScn.field3:
                        ET.SubElement(xmlScene, 'Field3').text = prjScn.field3

            if prjScn.field4 is not None:
                try:
                    xmlScene.find('Field4').text = prjScn.field4
                except(AttributeError):
                    if prjScn.field4:
                        ET.SubElement(xmlScene, 'Field4').text = prjScn.field4

            if prjScn.appendToPrev:
                if xmlScene.find('AppendToPrev') is None:
                    ET.SubElement(xmlScene, 'AppendToPrev').text = '-1'
            elif xmlScene.find('AppendToPrev') is not None:
                xmlScene.remove(xmlScene.find('AppendToPrev'))

            if (prjScn.date is not None) and (prjScn.time is not None):
                separator = ' '
                dateTime = f'{prjScn.date}{separator}{prjScn.time}'

                if dateTime == separator:
                    remove_date_time()

                elif xmlScene.find('SpecificDateTime') is not None:
                    if dateTime.count(':') < 2:
                        dateTime = f'{dateTime}:00'
                    xmlScene.find('SpecificDateTime').text = dateTime
                else:
                    ET.SubElement(xmlScene, 'SpecificDateTime').text = dateTime
                    ET.SubElement(xmlScene, 'SpecificDateMode').text = '-1'

                    if xmlScene.find('Day') is not None:
                        xmlScene.remove(xmlScene.find('Day'))

                    if xmlScene.find('Hour') is not None:
                        xmlScene.remove(xmlScene.find('Hour'))

                    if xmlScene.find('Minute') is not None:
                        xmlScene.remove(xmlScene.find('Minute'))

            elif (prjScn.day is not None) or (prjScn.time is not None):

                if not prjScn.day and not prjScn.time:
                    remove_date_time()

                else:
                    if xmlScene.find('SpecificDateTime') is not None:
                        xmlScene.remove(xmlScene.find('SpecificDateTime'))

                    if xmlScene.find('SpecificDateMode') is not None:
                        xmlScene.remove(xmlScene.find('SpecificDateMode'))
                    if prjScn.day is not None:
                        try:
                            xmlScene.find('Day').text = prjScn.day
                        except(AttributeError):
                            ET.SubElement(xmlScene, 'Day').text = prjScn.day
                    if prjScn.time is not None:
                        hours, minutes, __ = prjScn.time.split(':')
                        try:
                            xmlScene.find('Hour').text = hours
                        except(AttributeError):
                            ET.SubElement(xmlScene, 'Hour').text = hours
                        try:
                            xmlScene.find('Minute').text = minutes
                        except(AttributeError):
                            ET.SubElement(xmlScene, 'Minute').text = minutes

            if prjScn.lastsDays is not None:
                try:
                    xmlScene.find('LastsDays').text = prjScn.lastsDays
                except(AttributeError):
                    if prjScn.lastsDays:
                        ET.SubElement(xmlScene, 'LastsDays').text = prjScn.lastsDays

            if prjScn.lastsHours is not None:
                try:
                    xmlScene.find('LastsHours').text = prjScn.lastsHours
                except(AttributeError):
                    if prjScn.lastsHours:
                        ET.SubElement(xmlScene, 'LastsHours').text = prjScn.lastsHours

            if prjScn.lastsMinutes is not None:
                try:
                    xmlScene.find('LastsMinutes').text = prjScn.lastsMinutes
                except(AttributeError):
                    if prjScn.lastsMinutes:
                        ET.SubElement(xmlScene, 'LastsMinutes').text = prjScn.lastsMinutes

            if prjScn.isReactionScene:
                if xmlScene.find('ReactionScene') is None:
                    ET.SubElement(xmlScene, 'ReactionScene').text = '-1'
            elif xmlScene.find('ReactionScene') is not None:
                xmlScene.remove(xmlScene.find('ReactionScene'))

            if prjScn.isSubPlot:
                if xmlScene.find('SubPlot') is None:
                    ET.SubElement(xmlScene, 'SubPlot').text = '-1'
            elif xmlScene.find('SubPlot') is not None:
                xmlScene.remove(xmlScene.find('SubPlot'))

            if prjScn.goal is not None:
                try:
                    xmlScene.find('Goal').text = prjScn.goal
                except(AttributeError):
                    if prjScn.goal:
                        ET.SubElement(xmlScene, 'Goal').text = prjScn.goal

            if prjScn.conflict is not None:
                try:
                    xmlScene.find('Conflict').text = prjScn.conflict
                except(AttributeError):
                    if prjScn.conflict:
                        ET.SubElement(xmlScene, 'Conflict').text = prjScn.conflict

            if prjScn.outcome is not None:
                try:
                    xmlScene.find('Outcome').text = prjScn.outcome
                except(AttributeError):
                    if prjScn.outcome:
                        ET.SubElement(xmlScene, 'Outcome').text = prjScn.outcome

            if prjScn.image is not None:
                try:
                    xmlScene.find('ImageFile').text = prjScn.image
                except(AttributeError):
                    if prjScn.image:
                        ET.SubElement(xmlScene, 'ImageFile').text = prjScn.image

            if prjScn.characters is not None:
                xmlCharacters = xmlScene.find('Characters')
                try:
                    for oldCrId in xmlCharacters.findall('CharID'):
                        xmlCharacters.remove(oldCrId)
                except(AttributeError):
                    xmlCharacters = ET.SubElement(xmlScene, 'Characters')
                for crId in prjScn.characters:
                    ET.SubElement(xmlCharacters, 'CharID').text = crId

            if prjScn.locations is not None:
                xmlLocations = xmlScene.find('Locations')
                try:
                    for oldLcId in xmlLocations.findall('LocID'):
                        xmlLocations.remove(oldLcId)
                except(AttributeError):
                    xmlLocations = ET.SubElement(xmlScene, 'Locations')
                for lcId in prjScn.locations:
                    ET.SubElement(xmlLocations, 'LocID').text = lcId

            if prjScn.items is not None:
                xmlItems = xmlScene.find('Items')
                try:
                    for oldItId in xmlItems.findall('ItemID'):
                        xmlItems.remove(oldItId)
                except(AttributeError):
                    xmlItems = ET.SubElement(xmlScene, 'Items')
                for itId in prjScn.items:
                    ET.SubElement(xmlItems, 'ItemID').text = itId


        def build_chapter_subtree(xmlChapter, prjChp, sortOrder):

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
            i = set_element(xmlChapter, 'Title', prjChp.title, i)
            i = set_element(xmlChapter, 'Desc', prjChp.desc, i)

            if yUnused:
                if xmlChapter.find('Unused') is None:
                    elem = ET.Element('Unused')
                    elem.text = '-1'
                    xmlChapter.insert(i, elem)
            elif xmlChapter.find('Unused') is not None:
                xmlChapter.remove(xmlChapter.find('Unused'))
            if xmlChapter.find('Unused') is not None:
                i += 1

            i = set_element(xmlChapter, 'SortOrder', str(sortOrder), i)

            xmlChapterFields = xmlChapter.find('Fields')
            if prjChp.suppressChapterTitle:
                if xmlChapterFields is None:
                    xmlChapterFields = ET.Element('Fields')
                    xmlChapter.insert(i, xmlChapterFields)
                try:
                    xmlChapterFields.find('Field_SuppressChapterTitle').text = '1'
                except(AttributeError):
                    ET.SubElement(xmlChapterFields, 'Field_SuppressChapterTitle').text = '1'
            elif xmlChapterFields is not None:
                if xmlChapterFields.find('Field_SuppressChapterTitle') is not None:
                    xmlChapterFields.find('Field_SuppressChapterTitle').text = '0'

            if prjChp.suppressChapterBreak:
                if xmlChapterFields is None:
                    xmlChapterFields = ET.Element('Fields')
                    xmlChapter.insert(i, xmlChapterFields)
                try:
                    xmlChapterFields.find('Field_SuppressChapterBreak').text = '1'
                except(AttributeError):
                    ET.SubElement(xmlChapterFields, 'Field_SuppressChapterBreak').text = '1'
            elif xmlChapterFields is not None:
                if xmlChapterFields.find('Field_SuppressChapterBreak') is not None:
                    xmlChapterFields.find('Field_SuppressChapterBreak').text = '0'

            if prjChp.isTrash:
                if xmlChapterFields is None:
                    xmlChapterFields = ET.Element('Fields')
                    xmlChapter.insert(i, xmlChapterFields)
                try:
                    xmlChapterFields.find('Field_IsTrash').text = '1'
                except(AttributeError):
                    ET.SubElement(xmlChapterFields, 'Field_IsTrash').text = '1'

            elif xmlChapterFields is not None:
                if xmlChapterFields.find('Field_IsTrash') is not None:
                    xmlChapterFields.remove(xmlChapterFields.find('Field_IsTrash'))

            for field in self.CHP_KWVAR:
                if prjChp.kwVar.get(field, None):
                    if xmlChapterFields is None:
                        xmlChapterFields = ET.Element('Fields')
                        xmlChapter.insert(i, xmlChapterFields)
                    try:
                        xmlChapterFields.find(field).text = prjChp.kwVar[field]
                    except(AttributeError):
                        ET.SubElement(xmlChapterFields, field).text = prjChp.kwVar[field]
                elif xmlChapterFields is not None:
                    try:
                        xmlChapterFields.remove(xmlChapterFields.find(field))
                    except:
                        pass
            if xmlChapter.find('Fields') is not None:
                i += 1

            if xmlChapter.find('SectionStart') is not None:
                if prjChp.chLevel == 0:
                    xmlChapter.remove(xmlChapter.find('SectionStart'))
            elif prjChp.chLevel == 1:
                elem = ET.Element('SectionStart')
                elem.text = '-1'
                xmlChapter.insert(i, elem)
            if xmlChapter.find('SectionStart') is not None:
                i += 1

            i = set_element(xmlChapter, 'Type', yType, i)
            i = set_element(xmlChapter, 'ChapterType', yChapterType, i)

            xmlScnList = xmlChapter.find('Scenes')

            if xmlScnList is not None:
                xmlChapter.remove(xmlScnList)

            if prjChp.srtScenes:
                xmlScnList = ET.Element('Scenes')
                xmlChapter.insert(i, xmlScnList)
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

            xmlLocationFields = xmlLoc.find('Fields')
            for field in self.LOC_KWVAR:
                if self.novel.locations[lcId].kwVar.get(field, None):
                    if xmlLocationFields is None:
                        xmlLocationFields = ET.SubElement(xmlLoc, 'Fields')
                    try:
                        xmlLocationFields.find(field).text = self.novel.locations[lcId].kwVar[field]
                    except(AttributeError):
                        ET.SubElement(xmlLocationFields, field).text = self.novel.locations[lcId].kwVar[field]
                elif xmlLocationFields is not None:
                    try:
                        xmlLocationFields.remove(xmlLocationFields.find(field))
                    except:
                        pass

        def build_prjNote_subtree(xmlProjectnote, projectNote, sortOrder):
            if projectNote.title is not None:
                ET.SubElement(xmlProjectnote, 'Title').text = projectNote.title

            if projectNote.desc is not None:
                ET.SubElement(xmlProjectnote, 'Desc').text = projectNote.desc

            ET.SubElement(xmlProjectnote, 'SortOrder').text = str(sortOrder)

        def add_projectvariable(title, desc, tags):
            pvId = create_id(prjVars)
            prjVars.append(pvId)
            xmlProjectvar = ET.SubElement(xmlProjectvars, 'PROJECTVAR')
            ET.SubElement(xmlProjectvar, 'ID').text = pvId
            ET.SubElement(xmlProjectvar, 'Title').text = title
            ET.SubElement(xmlProjectvar, 'Desc').text = desc
            ET.SubElement(xmlProjectvar, 'Tags').text = tags

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

            xmlItemFields = xmlItm.find('Fields')
            for field in self.ITM_KWVAR:
                if self.novel.items[itId].kwVar.get(field, None):
                    if xmlItemFields is None:
                        xmlItemFields = ET.SubElement(xmlItm, 'Fields')
                    try:
                        xmlItemFields.find(field).text = self.novel.items[itId].kwVar[field]
                    except(AttributeError):
                        ET.SubElement(xmlItemFields, field).text = self.novel.items[itId].kwVar[field]
                elif xmlItemFields is not None:
                    try:
                        xmlItemFields.remove(xmlItemFields.find(field))
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

            xmlCharacterFields = xmlCrt.find('Fields')
            for field in self.CRT_KWVAR:
                if self.novel.characters[crId].kwVar.get(field, None):
                    if xmlCharacterFields is None:
                        xmlCharacterFields = ET.SubElement(xmlCrt, 'Fields')
                    try:
                        xmlCharacterFields.find(field).text = self.novel.characters[crId].kwVar[field]
                    except(AttributeError):
                        ET.SubElement(xmlCharacterFields, field).text = self.novel.characters[crId].kwVar[field]
                elif xmlCharacterFields is not None:
                    try:
                        xmlCharacterFields.remove(xmlCharacterFields.find(field))
                    except:
                        pass

        def build_project_subtree(xmlProject):
            VER = '7'
            try:
                xmlProject.find('Ver').text = VER
            except(AttributeError):
                ET.SubElement(xmlProject, 'Ver').text = VER

            if self.novel.title is not None:
                try:
                    xmlProject.find('Title').text = self.novel.title
                except(AttributeError):
                    ET.SubElement(xmlProject, 'Title').text = self.novel.title

            if self.novel.desc is not None:
                try:
                    xmlProject.find('Desc').text = self.novel.desc
                except(AttributeError):
                    ET.SubElement(xmlProject, 'Desc').text = self.novel.desc

            if self.novel.authorName is not None:
                try:
                    xmlProject.find('AuthorName').text = self.novel.authorName
                except(AttributeError):
                    ET.SubElement(xmlProject, 'AuthorName').text = self.novel.authorName

            if self.novel.authorBio is not None:
                try:
                    xmlProject.find('Bio').text = self.novel.authorBio
                except(AttributeError):
                    ET.SubElement(xmlProject, 'Bio').text = self.novel.authorBio

            if self.novel.fieldTitle1 is not None:
                try:
                    xmlProject.find('FieldTitle1').text = self.novel.fieldTitle1
                except(AttributeError):
                    ET.SubElement(xmlProject, 'FieldTitle1').text = self.novel.fieldTitle1

            if self.novel.fieldTitle2 is not None:
                try:
                    xmlProject.find('FieldTitle2').text = self.novel.fieldTitle2
                except(AttributeError):
                    ET.SubElement(xmlProject, 'FieldTitle2').text = self.novel.fieldTitle2

            if self.novel.fieldTitle3 is not None:
                try:
                    xmlProject.find('FieldTitle3').text = self.novel.fieldTitle3
                except(AttributeError):
                    ET.SubElement(xmlProject, 'FieldTitle3').text = self.novel.fieldTitle3

            if self.novel.fieldTitle4 is not None:
                try:
                    xmlProject.find('FieldTitle4').text = self.novel.fieldTitle4
                except(AttributeError):
                    ET.SubElement(xmlProject, 'FieldTitle4').text = self.novel.fieldTitle4

            if self.novel.wordCountStart is not None:
                try:
                    xmlProject.find('WordCountStart').text = str(self.novel.wordCountStart)
                except(AttributeError):
                    ET.SubElement(xmlProject, 'WordCountStart').text = str(self.novel.wordCountStart)

            if self.novel.wordTarget is not None:
                try:
                    xmlProject.find('WordTarget').text = str(self.novel.wordTarget)
                except(AttributeError):
                    ET.SubElement(xmlProject, 'WordTarget').text = str(self.novel.wordTarget)


            self.novel.kwVar['Field_LanguageCode'] = None
            self.novel.kwVar['Field_CountryCode'] = None

            xmlProjectFields = xmlProject.find('Fields')
            for field in self.PRJ_KWVAR:
                setting = self.novel.kwVar.get(field, None)
                if setting:
                    if xmlProjectFields is None:
                        xmlProjectFields = ET.SubElement(xmlProject, 'Fields')
                    try:
                        xmlProjectFields.find(field).text = setting
                    except(AttributeError):
                        ET.SubElement(xmlProjectFields, field).text = setting
                else:
                    try:
                        xmlProjectFields.remove(xmlProjectFields.find(field))
                    except:
                        pass

        TAG = 'YWRITER7'
        xmlNewScenes = {}
        xmlNewChapters = {}
        try:
            root = self.tree.getroot()
            xmlProject = root.find('PROJECT')
            xmlLocations = root.find('LOCATIONS')
            xmlItems = root.find('ITEMS')
            xmlCharacters = root.find('CHARACTERS')
            xmlProjectnotes = root.find('PROJECTNOTES')
            xmlScenes = root.find('SCENES')
            xmlChapters = root.find('CHAPTERS')
        except(AttributeError):
            root = ET.Element(TAG)
            xmlProject = ET.SubElement(root, 'PROJECT')
            xmlLocations = ET.SubElement(root, 'LOCATIONS')
            xmlItems = ET.SubElement(root, 'ITEMS')
            xmlCharacters = ET.SubElement(root, 'CHARACTERS')
            xmlProjectnotes = ET.SubElement(root, 'PROJECTNOTES')
            xmlScenes = ET.SubElement(root, 'SCENES')
            xmlChapters = ET.SubElement(root, 'CHAPTERS')


        build_project_subtree(xmlProject)


        for xmlLoc in xmlLocations.findall('LOCATION'):
            xmlLocations.remove(xmlLoc)

        sortOrder = 0
        for lcId in self.novel.srtLocations:
            sortOrder += 1
            xmlLoc = ET.SubElement(xmlLocations, 'LOCATION')
            ET.SubElement(xmlLoc, 'ID').text = lcId
            build_location_subtree(xmlLoc, self.novel.locations[lcId], sortOrder)


        for xmlItm in xmlItems.findall('ITEM'):
            xmlItems.remove(xmlItm)

        sortOrder = 0
        for itId in self.novel.srtItems:
            sortOrder += 1
            xmlItm = ET.SubElement(xmlItems, 'ITEM')
            ET.SubElement(xmlItm, 'ID').text = itId
            build_item_subtree(xmlItm, self.novel.items[itId], sortOrder)


        for xmlCrt in xmlCharacters.findall('CHARACTER'):
            xmlCharacters.remove(xmlCrt)

        sortOrder = 0
        for crId in self.novel.srtCharacters:
            sortOrder += 1
            xmlCrt = ET.SubElement(xmlCharacters, 'CHARACTER')
            ET.SubElement(xmlCrt, 'ID').text = crId
            build_character_subtree(xmlCrt, self.novel.characters[crId], sortOrder)


        if xmlProjectnotes is not None:
            for xmlProjectnote in xmlProjectnotes.findall('PROJECTNOTE'):
                xmlProjectnotes.remove(xmlProjectnote)
            if not self.novel.srtPrjNotes:
                root.remove(xmlProjectnotes)
        elif self.novel.srtPrjNotes:
            xmlProjectnotes = ET.SubElement(root, 'PROJECTNOTES')
        if self.novel.srtPrjNotes:
            sortOrder = 0
            for pnId in self.novel.srtPrjNotes:
                sortOrder += 1
                xmlProjectnote = ET.SubElement(xmlProjectnotes, 'PROJECTNOTE')
                ET.SubElement(xmlProjectnote, 'ID').text = pnId
                build_prjNote_subtree(xmlProjectnote, self.novel.projectNotes[pnId], sortOrder)

        xmlProjectvars = root.find('PROJECTVARS')
        if self.novel.languages or self.novel.languageCode or self.novel.countryCode:
            self.novel.check_locale()
            if xmlProjectvars is None:
                xmlProjectvars = ET.SubElement(root, 'PROJECTVARS')
            prjVars = []
            languages = self.novel.languages.copy()
            hasLanguageCode = False
            hasCountryCode = False
            for xmlProjectvar in xmlProjectvars.findall('PROJECTVAR'):
                prjVars.append(xmlProjectvar.find('ID').text)
                title = xmlProjectvar.find('Title').text

                if title.startswith('lang='):
                    try:
                        __, langCode = title.split('=')
                        languages.remove(langCode)
                    except:
                        pass

                elif title == 'Language':
                    xmlProjectvar.find('Desc').text = self.novel.languageCode
                    hasLanguageCode = True

                elif title == 'Country':
                    xmlProjectvar.find('Desc').text = self.novel.countryCode
                    hasCountryCode = True

            if not hasLanguageCode:
                add_projectvariable('Language',
                                    self.novel.languageCode,
                                    '0')

            if not hasCountryCode:
                add_projectvariable('Country',
                                    self.novel.countryCode,
                                    '0')

            for langCode in languages:
                add_projectvariable(f'lang={langCode}',
                                    f'<HTM <SPAN LANG="{langCode}"> /HTM>',
                                    '0')
                add_projectvariable(f'/lang={langCode}',
                                    f'<HTM </SPAN> /HTM>',
                                    '0')


        for xmlScene in xmlScenes.findall('SCENE'):
            scId = xmlScene.find('ID').text
            xmlNewScenes[scId] = xmlScene
            xmlScenes.remove(xmlScene)

        for scId in self.novel.scenes:
            if not scId in xmlNewScenes:
                xmlNewScenes[scId] = ET.Element('SCENE')
                ET.SubElement(xmlNewScenes[scId], 'ID').text = scId
            build_scene_subtree(xmlNewScenes[scId], self.novel.scenes[scId])
            xmlScenes.append(xmlNewScenes[scId])


        for xmlChapter in xmlChapters.findall('CHAPTER'):
            chId = xmlChapter.find('ID').text
            xmlNewChapters[chId] = xmlChapter
            xmlChapters.remove(xmlChapter)

        sortOrder = 0
        for chId in self.novel.srtChapters:
            sortOrder += 1
            if not chId in xmlNewChapters:
                xmlNewChapters[chId] = ET.Element('CHAPTER')
                ET.SubElement(xmlNewChapters[chId], 'ID').text = chId
            build_chapter_subtree(xmlNewChapters[chId], self.novel.chapters[chId], sortOrder)
            xmlChapters.append(xmlNewChapters[chId])

        for xmlScene in root.find('SCENES'):
            scId = xmlScene.find('ID').text
            if self.novel.scenes[scId].sceneContent is not None:
                xmlScene.find('SceneContent').text = self.novel.scenes[scId].sceneContent
                xmlScene.find('WordCount').text = str(self.novel.scenes[scId].wordCount)
                xmlScene.find('LetterCount').text = str(self.novel.scenes[scId].letterCount)
            try:
                xmlScene.remove(xmlScene.find('RTFFile'))
            except:
                pass

        indent(root)
        self.tree = ET.ElementTree(root)

    def _postprocess_xml_file(self, filePath):
        '''Postprocess an xml file created by ElementTree.
        
        Positional argument:
            filePath: str -- path to xml file.
        
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
        if not self.novel.chapters:
            text = text.replace('<CHAPTERS />', '<CHAPTERS></CHAPTERS>')
        text = unescape(text)
        try:
            with open(filePath, 'w', encoding='utf-8') as f:
                f.write(text)
        except:
            raise Error(f'{_("Cannot write file")}: "{norm_path(filePath)}".')

    def _read_project(self, root):
        xmlProject = root.find('PROJECT')

        if xmlProject.find('Title') is not None:
            self.novel.title = xmlProject.find('Title').text

        if xmlProject.find('AuthorName') is not None:
            self.novel.authorName = xmlProject.find('AuthorName').text

        if xmlProject.find('Bio') is not None:
            self.novel.authorBio = xmlProject.find('Bio').text

        if xmlProject.find('Desc') is not None:
            self.novel.desc = xmlProject.find('Desc').text

        if xmlProject.find('FieldTitle1') is not None:
            self.novel.fieldTitle1 = xmlProject.find('FieldTitle1').text

        if xmlProject.find('FieldTitle2') is not None:
            self.novel.fieldTitle2 = xmlProject.find('FieldTitle2').text

        if xmlProject.find('FieldTitle3') is not None:
            self.novel.fieldTitle3 = xmlProject.find('FieldTitle3').text

        if xmlProject.find('FieldTitle4') is not None:
            self.novel.fieldTitle4 = xmlProject.find('FieldTitle4').text

        if xmlProject.find('WordCountStart') is not None:
            try:
                self.novel.wordCountStart = int(xmlProject.find('WordCountStart').text)
            except:
                self.novel.wordCountStart = 0
        if xmlProject.find('WordTarget') is not None:
            try:
                self.novel.wordTarget = int(xmlProject.find('WordTarget').text)
            except:
                self.novel.wordTarget = 0

        for fieldName in self.PRJ_KWVAR:
            self.novel.kwVar[fieldName] = None

        for xmlProjectFields in xmlProject.findall('Fields'):
            for fieldName in self.PRJ_KWVAR:
                field = xmlProjectFields.find(fieldName)
                if field is not None:
                    self.novel.kwVar[fieldName] = field.text

        if self.novel.kwVar['Field_LanguageCode']:
            self.novel.languageCode = self.novel.kwVar['Field_LanguageCode']
        if self.novel.kwVar['Field_CountryCode']:
            self.novel.countryCode = self.novel.kwVar['Field_CountryCode']

    def _read_locations(self, root):
        self.novel.srtLocations = []
        for xmlLocation in root.find('LOCATIONS'):
            lcId = xmlLocation.find('ID').text
            self.novel.srtLocations.append(lcId)
            self.novel.locations[lcId] = WorldElement()

            if xmlLocation.find('Title') is not None:
                self.novel.locations[lcId].title = xmlLocation.find('Title').text

            if xmlLocation.find('ImageFile') is not None:
                self.novel.locations[lcId].image = xmlLocation.find('ImageFile').text

            if xmlLocation.find('Desc') is not None:
                self.novel.locations[lcId].desc = xmlLocation.find('Desc').text

            if xmlLocation.find('AKA') is not None:
                self.novel.locations[lcId].aka = xmlLocation.find('AKA').text

            if xmlLocation.find('Tags') is not None:
                if xmlLocation.find('Tags').text is not None:
                    tags = string_to_list(xmlLocation.find('Tags').text)
                    self.novel.locations[lcId].tags = self._strip_spaces(tags)

            for fieldName in self.LOC_KWVAR:
                self.novel.locations[lcId].kwVar[fieldName] = None

            for xmlLocationFields in xmlLocation.findall('Fields'):
                for fieldName in self.LOC_KWVAR:
                    field = xmlLocationFields.find(fieldName)
                    if field is not None:
                        self.novel.locations[lcId].kwVar[fieldName] = field.text

    def _read_items(self, root):
        self.novel.srtItems = []
        for xmlItem in root.find('ITEMS'):
            itId = xmlItem.find('ID').text
            self.novel.srtItems.append(itId)
            self.novel.items[itId] = WorldElement()

            if xmlItem.find('Title') is not None:
                self.novel.items[itId].title = xmlItem.find('Title').text

            if xmlItem.find('ImageFile') is not None:
                self.novel.items[itId].image = xmlItem.find('ImageFile').text

            if xmlItem.find('Desc') is not None:
                self.novel.items[itId].desc = xmlItem.find('Desc').text

            if xmlItem.find('AKA') is not None:
                self.novel.items[itId].aka = xmlItem.find('AKA').text

            if xmlItem.find('Tags') is not None:
                if xmlItem.find('Tags').text is not None:
                    tags = string_to_list(xmlItem.find('Tags').text)
                    self.novel.items[itId].tags = self._strip_spaces(tags)

            for fieldName in self.ITM_KWVAR:
                self.novel.items[itId].kwVar[fieldName] = None

            for xmlItemFields in xmlItem.findall('Fields'):
                for fieldName in self.ITM_KWVAR:
                    field = xmlItemFields.find(fieldName)
                    if field is not None:
                        self.novel.items[itId].kwVar[fieldName] = field.text

    def _read_characters(self, root):
        self.novel.srtCharacters = []
        for xmlCharacter in root.find('CHARACTERS'):
            crId = xmlCharacter.find('ID').text
            self.novel.srtCharacters.append(crId)
            self.novel.characters[crId] = Character()

            if xmlCharacter.find('Title') is not None:
                self.novel.characters[crId].title = xmlCharacter.find('Title').text

            if xmlCharacter.find('ImageFile') is not None:
                self.novel.characters[crId].image = xmlCharacter.find('ImageFile').text

            if xmlCharacter.find('Desc') is not None:
                self.novel.characters[crId].desc = xmlCharacter.find('Desc').text

            if xmlCharacter.find('AKA') is not None:
                self.novel.characters[crId].aka = xmlCharacter.find('AKA').text

            if xmlCharacter.find('Tags') is not None:
                if xmlCharacter.find('Tags').text is not None:
                    tags = string_to_list(xmlCharacter.find('Tags').text)
                    self.novel.characters[crId].tags = self._strip_spaces(tags)

            if xmlCharacter.find('Notes') is not None:
                self.novel.characters[crId].notes = xmlCharacter.find('Notes').text

            if xmlCharacter.find('Bio') is not None:
                self.novel.characters[crId].bio = xmlCharacter.find('Bio').text

            if xmlCharacter.find('Goals') is not None:
                self.novel.characters[crId].goals = xmlCharacter.find('Goals').text

            if xmlCharacter.find('FullName') is not None:
                self.novel.characters[crId].fullName = xmlCharacter.find('FullName').text

            if xmlCharacter.find('Major') is not None:
                self.novel.characters[crId].isMajor = True
            else:
                self.novel.characters[crId].isMajor = False

            for fieldName in self.CRT_KWVAR:
                self.novel.characters[crId].kwVar[fieldName] = None

            for xmlCharacterFields in xmlCharacter.findall('Fields'):
                for fieldName in self.CRT_KWVAR:
                    field = xmlCharacterFields.find(fieldName)
                    if field is not None:
                        self.novel.characters[crId].kwVar[fieldName] = field.text

    def _read_projectnotes(self, root):
        self.novel.srtPrjNotes = []

        try:
            for xmlProjectnote in root.find('PROJECTNOTES'):
                if xmlProjectnote.find('ID') is not None:
                    pnId = xmlProjectnote.find('ID').text
                    self.novel.srtPrjNotes.append(pnId)
                    self.novel.projectNotes[pnId] = BasicElement()
                    if xmlProjectnote.find('Title') is not None:
                        self.novel.projectNotes[pnId].title = xmlProjectnote.find('Title').text
                    if xmlProjectnote.find('Desc') is not None:
                        self.novel.projectNotes[pnId].desc = xmlProjectnote.find('Desc').text

                for fieldName in self.PNT_KWVAR:
                    self.novel.projectNotes[pnId].kwVar[fieldName] = None

                for pnFields in xmlProjectnote.findall('Fields'):
                    field = pnFields.find(fieldName)
                    if field is not None:
                        self.novel.projectNotes[pnId].kwVar[fieldName] = field.text
        except:
            pass

    def _read_projectvars(self, root):
        try:
            for xmlProjectvar in root.find('PROJECTVARS'):
                if xmlProjectvar.find('Title') is not None:
                    title = xmlProjectvar.find('Title').text
                    if title == 'Language':
                        if xmlProjectvar.find('Desc') is not None:
                            self.novel.languageCode = xmlProjectvar.find('Desc').text

                    elif title == 'Country':
                        if xmlProjectvar.find('Desc') is not None:
                            self.novel.countryCode = xmlProjectvar.find('Desc').text

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

    def _read_scenes(self, root):
        for xmlScene in root.find('SCENES'):
            scId = xmlScene.find('ID').text
            self.novel.scenes[scId] = Scene()

            if xmlScene.find('Title') is not None:
                self.novel.scenes[scId].title = xmlScene.find('Title').text

            if xmlScene.find('Desc') is not None:
                self.novel.scenes[scId].desc = xmlScene.find('Desc').text

            if xmlScene.find('SceneContent') is not None:
                sceneContent = xmlScene.find('SceneContent').text
                if sceneContent is not None:
                    self.novel.scenes[scId].sceneContent = sceneContent



            self.novel.scenes[scId].scType = 0

            for fieldName in self.SCN_KWVAR:
                self.novel.scenes[scId].kwVar[fieldName] = None

            for xmlSceneFields in xmlScene.findall('Fields'):
                for fieldName in self.SCN_KWVAR:
                    field = xmlSceneFields.find(fieldName)
                    if field is not None:
                        self.novel.scenes[scId].kwVar[fieldName] = field.text

                if xmlSceneFields.find('Field_SceneType') is not None:
                    if xmlSceneFields.find('Field_SceneType').text == '1':
                        self.novel.scenes[scId].scType = 1
                    elif xmlSceneFields.find('Field_SceneType').text == '2':
                        self.novel.scenes[scId].scType = 2
            if xmlScene.find('Unused') is not None:
                if self.novel.scenes[scId].scType == 0:
                    self.novel.scenes[scId].scType = 3

            if xmlScene.find('ExportCondSpecific') is None:
                self.novel.scenes[scId].doNotExport = False
            elif xmlScene.find('ExportWhenRTF') is not None:
                self.novel.scenes[scId].doNotExport = False
            else:
                self.novel.scenes[scId].doNotExport = True

            if xmlScene.find('Status') is not None:
                self.novel.scenes[scId].status = int(xmlScene.find('Status').text)

            if xmlScene.find('Notes') is not None:
                self.novel.scenes[scId].notes = xmlScene.find('Notes').text

            if xmlScene.find('Tags') is not None:
                if xmlScene.find('Tags').text is not None:
                    tags = string_to_list(xmlScene.find('Tags').text)
                    self.novel.scenes[scId].tags = self._strip_spaces(tags)

            if xmlScene.find('Field1') is not None:
                self.novel.scenes[scId].field1 = xmlScene.find('Field1').text

            if xmlScene.find('Field2') is not None:
                self.novel.scenes[scId].field2 = xmlScene.find('Field2').text

            if xmlScene.find('Field3') is not None:
                self.novel.scenes[scId].field3 = xmlScene.find('Field3').text

            if xmlScene.find('Field4') is not None:
                self.novel.scenes[scId].field4 = xmlScene.find('Field4').text

            if xmlScene.find('AppendToPrev') is not None:
                self.novel.scenes[scId].appendToPrev = True
            else:
                self.novel.scenes[scId].appendToPrev = False

            if xmlScene.find('SpecificDateTime') is not None:
                dateTimeStr = xmlScene.find('SpecificDateTime').text

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
                if xmlScene.find('Day') is not None:
                    day = xmlScene.find('Day').text

                    try:
                        int(day)
                    except ValueError:
                        day = ''
                    self.novel.scenes[scId].day = day

                hasUnspecificTime = False
                if xmlScene.find('Hour') is not None:
                    hour = xmlScene.find('Hour').text.zfill(2)
                    hasUnspecificTime = True
                else:
                    hour = '00'
                if xmlScene.find('Minute') is not None:
                    minute = xmlScene.find('Minute').text.zfill(2)
                    hasUnspecificTime = True
                else:
                    minute = '00'
                if hasUnspecificTime:
                    self.novel.scenes[scId].time = f'{hour}:{minute}:00'

            if xmlScene.find('LastsDays') is not None:
                self.novel.scenes[scId].lastsDays = xmlScene.find('LastsDays').text

            if xmlScene.find('LastsHours') is not None:
                self.novel.scenes[scId].lastsHours = xmlScene.find('LastsHours').text

            if xmlScene.find('LastsMinutes') is not None:
                self.novel.scenes[scId].lastsMinutes = xmlScene.find('LastsMinutes').text

            if xmlScene.find('ReactionScene') is not None:
                self.novel.scenes[scId].isReactionScene = True
            else:
                self.novel.scenes[scId].isReactionScene = False

            if xmlScene.find('SubPlot') is not None:
                self.novel.scenes[scId].isSubPlot = True
            else:
                self.novel.scenes[scId].isSubPlot = False

            if xmlScene.find('Goal') is not None:
                self.novel.scenes[scId].goal = xmlScene.find('Goal').text

            if xmlScene.find('Conflict') is not None:
                self.novel.scenes[scId].conflict = xmlScene.find('Conflict').text

            if xmlScene.find('Outcome') is not None:
                self.novel.scenes[scId].outcome = xmlScene.find('Outcome').text

            if xmlScene.find('ImageFile') is not None:
                self.novel.scenes[scId].image = xmlScene.find('ImageFile').text

            if xmlScene.find('Characters') is not None:
                for characters in xmlScene.find('Characters').iter('CharID'):
                    crId = characters.text
                    if crId in self.novel.srtCharacters:
                        if self.novel.scenes[scId].characters is None:
                            self.novel.scenes[scId].characters = []
                        self.novel.scenes[scId].characters.append(crId)

            if xmlScene.find('Locations') is not None:
                for locations in xmlScene.find('Locations').iter('LocID'):
                    lcId = locations.text
                    if lcId in self.novel.srtLocations:
                        if self.novel.scenes[scId].locations is None:
                            self.novel.scenes[scId].locations = []
                        self.novel.scenes[scId].locations.append(lcId)

            if xmlScene.find('Items') is not None:
                for items in xmlScene.find('Items').iter('ItemID'):
                    itId = items.text
                    if itId in self.novel.srtItems:
                        if self.novel.scenes[scId].items is None:
                            self.novel.scenes[scId].items = []
                        self.novel.scenes[scId].items.append(itId)

    def _read_chapters(self, root):
        self.novel.srtChapters = []
        for xmlChapter in root.find('CHAPTERS'):
            chId = xmlChapter.find('ID').text
            self.novel.chapters[chId] = Chapter()
            self.novel.srtChapters.append(chId)

            if xmlChapter.find('Title') is not None:
                self.novel.chapters[chId].title = xmlChapter.find('Title').text

            if xmlChapter.find('Desc') is not None:
                self.novel.chapters[chId].desc = xmlChapter.find('Desc').text

            if xmlChapter.find('SectionStart') is not None:
                self.novel.chapters[chId].chLevel = 1
            else:
                self.novel.chapters[chId].chLevel = 0


            self.novel.chapters[chId].chType = 0
            if xmlChapter.find('Unused') is not None:
                yUnused = True
            else:
                yUnused = False
            if xmlChapter.find('ChapterType') is not None:
                yChapterType = xmlChapter.find('ChapterType').text
                if yChapterType == '2':
                    self.novel.chapters[chId].chType = 2
                elif yChapterType == '1':
                    self.novel.chapters[chId].chType = 1
                elif yUnused:
                    self.novel.chapters[chId].chType = 3
            else:
                if xmlChapter.find('Type') is not None:
                    yType = xmlChapter.find('Type').text
                    if yType == '1':
                        self.novel.chapters[chId].chType = 1
                    elif yUnused:
                        self.novel.chapters[chId].chType = 3

            self.novel.chapters[chId].suppressChapterTitle = False
            if self.novel.chapters[chId].title is not None:
                if self.novel.chapters[chId].title.startswith('@'):
                    self.novel.chapters[chId].suppressChapterTitle = True

            for fieldName in self.CHP_KWVAR:
                self.novel.chapters[chId].kwVar[fieldName] = None

            for xmlChapterFields in xmlChapter.findall('Fields'):
                if xmlChapterFields.find('Field_SuppressChapterTitle') is not None:
                    if xmlChapterFields.find('Field_SuppressChapterTitle').text == '1':
                        self.novel.chapters[chId].suppressChapterTitle = True
                self.novel.chapters[chId].isTrash = False
                if xmlChapterFields.find('Field_IsTrash') is not None:
                    if xmlChapterFields.find('Field_IsTrash').text == '1':
                        self.novel.chapters[chId].isTrash = True
                self.novel.chapters[chId].suppressChapterBreak = False
                if xmlChapterFields.find('Field_SuppressChapterBreak') is not None:
                    if xmlChapterFields.find('Field_SuppressChapterBreak').text == '1':
                        self.novel.chapters[chId].suppressChapterBreak = True

                for fieldName in self.CHP_KWVAR:
                    field = xmlChapterFields.find(fieldName)
                    if field is not None:
                        self.novel.chapters[chId].kwVar[fieldName] = field.text

            self.novel.chapters[chId].srtScenes = []
            if xmlChapter.find('Scenes') is not None:
                for scn in xmlChapter.find('Scenes').findall('ScID'):
                    scId = scn.text
                    if scId in self.novel.scenes:
                        self.novel.chapters[chId].srtScenes.append(scId)

    def _strip_spaces(self, lines):
        stripped = []
        for line in lines:
            stripped.append(line.strip())
        return stripped

    def _write_element_tree(self, ywProject):
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

from xml import sax


class OdtParser(sax.ContentHandler):

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
                try:
                    meta = odfFile.read('meta.xml')
                except KeyError:
                    meta = None
        except:
            raise Error(f'{_("Cannot read file")}: "{norm_path(filePath)}".')

        root = ET.fromstring(styles)
        styles = root.find('office:styles', namespaces)
        for defaultStyle in styles.findall('style:default-style', namespaces):
            if defaultStyle.get(f'{{{namespaces["style"]}}}family') == 'paragraph':
                textProperties = defaultStyle.find('style:text-properties', namespaces)
                lngCode = textProperties.get(f'{{{namespaces["fo"]}}}language')
                ctrCode = textProperties.get(f'{{{namespaces["fo"]}}}country')
                self.handle_starttag('body', [('language', lngCode), ('country', ctrCode)])
                break

        if meta:
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

        sax.parseString(content, self)

    def characters(self, content):
        if self._commentParagraphCount is not None:
            if self._commentParagraphCount == 1:
                self._comment = f'{self._comment}{content}'
        elif self._paragraph:
            self.handle_data(content)
        elif self._heading is not None:
            self.handle_data(content)

    def endElement(self, name):
        if name == 'text:p':
            if self._commentParagraphCount is None:
                while self._span:
                    self.handle_endtag(self._span.pop())
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

    def startElement(self, name, attrs):
        xmlAttributes = {}
        for attribute in attrs.items():
            attrKey, attrValue = attribute
            xmlAttributes[attrKey] = attrValue
        style = xmlAttributes.get('text:style-name', '')
        if name == 'text:p':
            param = [()]
            if style in self._languageTags:
                param = [('lang', self._languageTags[style])]
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
            if style in self._emTags:
                self._span.append('em')
                self.handle_starttag('em', [()])
            if style in self._strongTags:
                self._span.append('strong')
                self.handle_starttag('strong', [()])
        elif name == 'text:span':
            if style in self._emTags:
                self._span.append('em')
                self.handle_starttag('em', [()])
            if style in self._strongTags:
                self._span.append('strong')
                self.handle_starttag('strong', [()])
            if style in self._languageTags:
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
            if xmlAttributes.get('fo:font-style', None) == 'italic':
                self._emTags.append(self._style)
            if xmlAttributes.get('fo:font-weight', None) == 'bold':
                self._strongTags.append(self._style)
            if xmlAttributes.get('fo:language', False):
                lngCode = xmlAttributes['fo:language']
                ctrCode = xmlAttributes['fo:country']
                if ctrCode != 'none':
                    locale = f'{lngCode}-{ctrCode}'
                else:
                    locale = lngCode
                self._languageTags[self._style] = locale
        elif name == 'text:s':
            self.handle_starttag('s', [()])

    def handle_comment(self, data):
        pass

    def handle_data(self, data):
        pass

    def handle_endtag(self, tag):
        pass

    def handle_starttag(self, tag, attrs):
        pass



class OdtReader(File, OdtParser):
    EXTENSION = '.odt'

    _TYPE = 0

    _COMMENT_START = '/*'
    _COMMENT_END = '*/'
    _SC_TITLE_BRACKET = '~'
    _BULLET = '-'
    _INDENT = '>'

    def __init__(self, filePath, **kwargs):
        super().__init__(filePath)
        self._lines = []
        self._scId = None
        self._chId = None
        self._newline = False
        self._language = ''
        self._skip_data = False

    def handle_comment(self, data):
        if self._scId is not None:
            self._lines.append(f'{self._COMMENT_START}{data}{self._COMMENT_END}')

    def handle_starttag(self, tag, attrs):
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
        elif tag == 's':
            self._lines.append(' ')

    def read(self):
        OdtParser.feed_file(self, self.filePath)

    def _convert_to_yw(self, text):
        text = text.replace('\n', ' ')
        text = text.replace('\r', ' ')
        text = text.replace('\t', ' ')
        while '  ' in text:
            text = text.replace('  ', ' ')

        return text



class Splitter:
    PART_SEPARATOR: str = '#'
    CHAPTER_SEPARATOR: str = '##'
    SCENE_SEPARATOR: str = '###'
    DESC_SEPARATOR: str = '|'
    _CLIP_TITLE: int = 20

    def split_scenes(self, file):

        def create_chapter(chapterId: str, title: str, desc: str, level: int):
            newChapter = Chapter()
            newChapter.title = title
            newChapter.desc = desc
            newChapter.chLevel = level
            newChapter.chType = 0
            file.novel.chapters[chapterId] = newChapter

        def create_scene(sceneId: str, parent: str, splitCount: int, title: str, desc: str):
            WARNING: str = '(!)'

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

        chIdMax = 0
        scIdMax = 0
        for chId in file.novel.srtChapters:
            if int(chId) > chIdMax:
                chIdMax = int(chId)
        for scId in file.novel.scenes:
            if int(scId) > scIdMax:
                scIdMax = int(scId)

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

                for line in lines:
                    heading = line.strip('# ').split(self.DESC_SEPARATOR)
                    title = heading[0]
                    try:
                        desc = heading[1]
                    except:
                        desc = ''
                    if line.startswith(self.SCENE_SEPARATOR):
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
                if inScene:
                    file.novel.scenes[sceneId].sceneContent = '\n'.join(newLines)
            file.novel.chapters[chapterId].srtScenes = srtScenes
        file.novel.srtChapters = srtChapters
        return scenesSplit


class OdtRFormatted(OdtReader):
    _COMMENT_START = '/*'
    _COMMENT_END = '*/'
    _SC_TITLE_BRACKET = '~'
    _BULLET = '-'
    _INDENT = '>'

    def read(self):
        self.novel.languages = []
        super().read()

        sceneSplitter = Splitter()
        self.scenesSplit = sceneSplitter.split_scenes(self)

    def _cleanup_scene(self, text):
        tags = ['i', 'b']
        for language in self.novel.languages:
            tags.append(f'lang={language}')
        for tag in tags:
            text = text.replace(f'[/{tag}][{tag}]', '')
            text = text.replace(f'[/{tag}]\n[{tag}]', '\n')
            text = text.replace(f'[/{tag}]\n> [{tag}]', '\n> ')

        return text



class OdtRImport(OdtRFormatted):
    DESCRIPTION = _('Work in progress')
    SUFFIX = ''
    _SCENE_DIVIDER = '* * *'
    _LOW_WORDCOUNT = 10

    def __init__(self, filePath, **kwargs):
        super().__init__(filePath)
        self._chCount = 0
        self._scCount = 0

    def handle_comment(self, data):
        if self._scId is not None:
            if not self._lines:
                try:
                    self.novel.scenes[self._scId].title = data.strip()
                except:
                    pass
                return

            self._lines.append(f'{self._COMMENT_START}{data.strip()}{self._COMMENT_END}')

    def handle_data(self, data):
        if self._scId is not None and self._SCENE_DIVIDER in data:
            self._scId = None
        else:
            self._lines.append(data)

    def handle_endtag(self, tag):
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

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            if self._scId is None and self._chId is not None:
                self._lines = []
                self._scCount += 1
                self._scId = str(self._scCount)
                self.novel.scenes[self._scId] = Scene()
                self.novel.chapters[self._chId].srtScenes.append(self._scId)
                self.novel.scenes[self._scId].status = '1'
                self.novel.scenes[self._scId].title = f'{_("Scene")} {self._scCount}'
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
        elif tag == 's':
            self._lines.append(' ')

    def read(self):
        self.novel.languages = []
        super().read()



class OdtROutline(OdtReader):
    DESCRIPTION = _('Novel outline')
    SUFFIX = ''

    def __init__(self, filePath, **kwargs):
        super().__init__(filePath)
        self._chCount = 0
        self._scCount = 0

    def handle_data(self, data):
        self._lines.append(data)

    def handle_endtag(self, tag):
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

    def handle_starttag(self, tag, attrs):
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
        elif tag == 's':
            self._lines.append(' ')


class NewProjectFactory(FileFactory):
    DO_NOT_IMPORT = ['_xref', '_brf_synopsis']

    def make_file_objects(self, sourcePath, **kwargs):
        if not self._canImport(sourcePath):
            raise Error(f'{_("This document is not meant to be written back")}.')

        fileName, __ = os.path.splitext(sourcePath)
        targetFile = Yw7File(f'{fileName}{Yw7File.EXTENSION}', **kwargs)
        if sourcePath.endswith('.odt'):
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
        fileName, __ = os.path.splitext(sourcePath)
        for suffix in self.DO_NOT_IMPORT:
            if fileName.endswith(suffix):
                return False

        return True


class OdtRProof(OdtRFormatted):
    DESCRIPTION = _('Tagged manuscript for proofing')
    SUFFIX = '_proof'

    def handle_data(self, data):
        try:
            if self._skip_data:
                self._skip_data = False
            elif '[ScID' in data:
                self._scId = re.search('[0-9]+', data).group()
                self._lines = []
            elif '[/ScID' in data:
                if self._scId in self.novel.scenes:
                    text = ''.join(self._lines)
                    self.novel.scenes[self._scId].sceneContent = self._cleanup_scene(text).strip()
                    self._lines = []
                self._scId = None
            elif self._scId is not None:
                self._lines.append(data)
        except:
            raise Error(f'{_("Corrupt marker")}: "{data}"')

    def handle_endtag(self, tag):
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

    def handle_starttag(self, tag, attrs):
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
        elif tag == 's':
            self._lines.append(' ')



class OdtRManuscript(OdtRFormatted):
    DESCRIPTION = _('Editable manuscript')
    SUFFIX = '_manuscript'

    def handle_comment(self, data):
        if self._scId is not None:
            if not self._lines:
                pass
            if self._SC_TITLE_BRACKET in data:
                try:
                    self.novel.scenes[self._scId].title = data.split(self._SC_TITLE_BRACKET)[1].strip()
                except:
                    pass
                return

            self._lines.append(f'{self._COMMENT_START}{data.strip()}{self._COMMENT_END}')

    def handle_data(self, data):
        if self._skip_data:
            self._skip_data = False
        elif self._scId is not None:
            if not data.isspace():
                self._lines.append(data)
        elif self._chId is not None:
            if self.novel.chapters[self._chId].title is None:
                self.chapters[self._chId].title = data.strip()

    def handle_endtag(self, tag):
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

    def handle_starttag(self, tag, attrs):
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
        elif tag == 's':
            self._lines.append(' ')



class OdtRNotes(OdtRManuscript):
    DESCRIPTION = _('Notes chapters')
    SUFFIX = '_notes'

    _TYPE = 1


class OdtRTodo(OdtRManuscript):
    DESCRIPTION = _('Todo chapters')
    SUFFIX = '_todo'

    _TYPE = 2


class OdtRSceneDesc(OdtReader):
    DESCRIPTION = _('Scene descriptions')
    SUFFIX = '_scenes'

    def handle_data(self, data):
        if self._scId is not None:
            self._lines.append(data)
        elif self._chId is not None:
            if not self.novel.chapters[self._chId].title:
                self.novel.chapters[self._chId].title = data.strip()

    def handle_endtag(self, tag):
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



class OdtRChapterDesc(OdtReader):
    DESCRIPTION = _('Chapter descriptions')
    SUFFIX = '_chapters'

    def handle_endtag(self, tag):
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
        if self._chId is not None:
            self._lines.append(data.strip())


class OdtRPartDesc(OdtRChapterDesc):
    DESCRIPTION = _('Part descriptions')
    SUFFIX = '_parts'


class OdtRCharacters(OdtReader):
    DESCRIPTION = _('Character descriptions')
    SUFFIX = '_characters'

    def __init__(self, filePath, **kwargs):
        super().__init__(filePath)
        self._crId = None
        self._section = None

    def handle_data(self, data):
        if self._section is not None:
            self._lines.append(data.strip())

    def handle_endtag(self, tag):
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

    def handle_starttag(self, tag, attrs):
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
        elif tag == 's':
            self._lines.append(' ')



class OdtRLocations(OdtReader):
    DESCRIPTION = _('Location descriptions')
    SUFFIX = '_locations'

    def __init__(self, filePath, **kwargs):
        super().__init__(filePath)
        self._lcId = None

    def handle_data(self, data):
        if self._lcId is not None:
            self._lines.append(data.strip())

    def handle_endtag(self, tag):
        if self._lcId is not None:
            if tag == 'div':
                self.novel.locations[self._lcId].desc = ''.join(self._lines).rstrip()
                self._lines = []
                self._lcId = None
            elif tag == 'p':
                self._lines.append('\n')

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            if attrs[0][0] == 'id':
                if attrs[0][1].startswith('LcID'):
                    self._lcId = re.search('[0-9]+', attrs[0][1]).group()
                    if not self._lcId in self.novel.locations:
                        self.novel.srtLocations.append(self._lcId)
                        self.novel.locations[self._lcId] = WorldElement()
        elif tag == 's':
            self._lines.append(' ')



class OdtRItems(OdtReader):
    DESCRIPTION = _('Item descriptions')
    SUFFIX = '_items'

    def __init__(self, filePath, **kwargs):
        super().__init__(filePath)
        self._itId = None

    def handle_data(self, data):
        if self._itId is not None:
            self._lines.append(data.strip())

    def handle_endtag(self, tag):
        if self._itId is not None:
            if tag == 'div':
                self.novel.items[self._itId].desc = ''.join(self._lines).rstrip()
                self._lines = []
                self._itId = None
            elif tag == 'p':
                self._lines.append('\n')

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            if attrs[0][0] == 'id':
                if attrs[0][1].startswith('ItID'):
                    self._itId = re.search('[0-9]+', attrs[0][1]).group()
                    if not self._itId in self.novel.items:
                        self.novel.srtItems.append(self._itId)
                        self.novel.items[self._itId] = WorldElement()
        elif tag == 's':
            self._lines.append(' ')

from string import Template


class Filter:

    def accept(self, source, eId):
        return True


class FileExport(File):
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
        super().__init__(filePath, **kwargs)
        self._sceneFilter = Filter()
        self._chapterFilter = Filter()
        self._characterFilter = Filter()
        self._locationFilter = Filter()
        self._itemFilter = Filter()

    def write(self):
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

    def _get_fileHeaderMapping(self):
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

    def _convert_from_yw(self, text, quick=False):
        if text is None:
            text = ''
        return(text)

    def _get_chapterMapping(self, chId, chapterNumber):
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

    def _get_chapters(self):
        lines = []
        chapterNumber = 0
        sceneNumber = 0
        wordsTotal = 0
        lettersTotal = 0
        for chId in self.novel.srtChapters:
            dispNumber = 0
            if not self._chapterFilter.accept(self, chId):
                continue

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
                if self.novel.chapters[chId].chLevel == 1:
                    if self._todoPartTemplate:
                        template = Template(self._todoPartTemplate)
                elif self._todoChapterTemplate:
                    template = Template(self._todoChapterTemplate)
            elif self.novel.chapters[chId].chType == 1:
                if self.novel.chapters[chId].chLevel == 1:
                    if self._notesPartTemplate:
                        template = Template(self._notesPartTemplate)
                elif self._notesChapterTemplate:
                    template = Template(self._notesChapterTemplate)
            elif self.novel.chapters[chId].chType == 3:
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

            sceneLines, sceneNumber, wordsTotal, lettersTotal = self._get_scenes(
                chId, sceneNumber, wordsTotal, lettersTotal, doNotExport)
            lines.extend(sceneLines)

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

    def _get_characterMapping(self, crId):
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

    def _get_characters(self):
        if self._characterSectionHeading:
            lines = [self._characterSectionHeading]
        else:
            lines = []
        template = Template(self._characterTemplate)
        for crId in self.novel.srtCharacters:
            if self._characterFilter.accept(self, crId):
                lines.append(template.safe_substitute(self._get_characterMapping(crId)))
        return lines

    def _get_fileHeader(self):
        lines = []
        template = Template(self._fileHeader)
        lines.append(template.safe_substitute(self._get_fileHeaderMapping()))
        return lines

    def _get_itemMapping(self, itId):
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

    def _get_items(self):
        if self._itemSectionHeading:
            lines = [self._itemSectionHeading]
        else:
            lines = []
        template = Template(self._itemTemplate)
        for itId in self.novel.srtItems:
            if self._itemFilter.accept(self, itId):
                lines.append(template.safe_substitute(self._get_itemMapping(itId)))
        return lines

    def _get_locationMapping(self, lcId):
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

    def _get_locations(self):
        if self._locationSectionHeading:
            lines = [self._locationSectionHeading]
        else:
            lines = []
        template = Template(self._locationTemplate)
        for lcId in self.novel.srtLocations:
            if self._locationFilter.accept(self, lcId):
                lines.append(template.safe_substitute(self._get_locationMapping(lcId)))
        return lines

    def _get_sceneMapping(self, scId, sceneNumber, wordsTotal, lettersTotal):

        if sceneNumber == 0:
            sceneNumber = ''
        if self.novel.scenes[scId].tags is not None:
            tags = list_to_string(self.novel.scenes[scId].tags, divider=self._DIVIDER)
        else:
            tags = ''

        try:
            sChList = []
            for crId in self.novel.scenes[scId].characters:
                sChList.append(self.novel.characters[crId].title)
            sceneChars = list_to_string(sChList, divider=self._DIVIDER)
            viewpointChar = sChList[0]
        except:
            sceneChars = ''
            viewpointChar = ''

        if self.novel.scenes[scId].locations is not None:
            sLcList = []
            for lcId in self.novel.scenes[scId].locations:
                sLcList.append(self.novel.locations[lcId].title)
            sceneLocs = list_to_string(sLcList, divider=self._DIVIDER)
        else:
            sceneLocs = ''

        if self.novel.scenes[scId].items is not None:
            sItList = []
            for itId in self.novel.scenes[scId].items:
                sItList.append(self.novel.items[itId].title)
            sceneItems = list_to_string(sItList, divider=self._DIVIDER)
        else:
            sceneItems = ''

        if self.novel.scenes[scId].isReactionScene:
            reactionScene = Scene.REACTION_MARKER
        else:
            reactionScene = Scene.ACTION_MARKER

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

        if self.novel.scenes[scId].time is not None:
            scTime = self.novel.scenes[scId].time.rsplit(':', 1)[0]
        else:
            scTime = ''

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

    def _get_scenes(self, chId, sceneNumber, wordsTotal, lettersTotal, doNotExport):
        lines = []
        firstSceneInChapter = True
        for scId in self.novel.chapters[chId].srtScenes:
            dispNumber = 0
            if not self._sceneFilter.accept(self, scId):
                continue

            sceneContent = self.novel.scenes[scId].sceneContent
            if sceneContent is None:
                sceneContent = ''

            if self.novel.scenes[scId].scType == 2:
                if self._todoSceneTemplate:
                    template = Template(self._todoSceneTemplate)
                else:
                    continue

            elif self.novel.scenes[scId].scType == 1:
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

    def _get_prjNoteMapping(self, pnId):
        itemMapping = dict(
            ID=pnId,
            Title=self._convert_from_yw(self.novel.projectNotes[pnId].title, True),
            Desc=self._convert_from_yw(self.novel.projectNotes[pnId].desc, True),
            ProjectName=self._convert_from_yw(self.projectName, True),
            ProjectPath=self.projectPath,
        )
        return itemMapping

    def _get_projectNotes(self):
        lines = []
        template = Template(self._projectNoteTemplate)
        for pnId in self.novel.srtPrjNotes:
            map = self._get_prjNoteMapping(pnId)
            lines.append(template.safe_substitute(map))
        return lines

    def _get_text(self):
        lines = self._get_fileHeader()
        lines.extend(self._get_chapters())
        lines.extend(self._get_characters())
        lines.extend(self._get_locations())
        lines.extend(self._get_items())
        lines.extend(self._get_projectNotes())
        lines.append(self._fileFooter)
        return ''.join(lines)

    def _remove_inline_code(self, text):
        if text:
            text = text.replace('<RTFBRK>', '')
            YW_SPECIAL_CODES = ('HTM', 'TEX', 'RTF', 'epub', 'mobi', 'rtfimg')
            for specialCode in YW_SPECIAL_CODES:
                text = re.sub(f'\<{specialCode} .+?\/{specialCode}\>', '', text)
        else:
            text = ''
        return text


class OdsParser:

    def __init__(self):
        super().__init__()
        self._rows = []
        self._cells = []
        self._inCell = None
        self.__cellsPerRow = 0

    def get_rows(self, filePath, cellsPerRow):
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
                    break

                i += 1
                if i >= cellsPerRow:
                    break

                attribute = cell.get(f'{{{namespaces["table"]}}}number-columns-repeated')
                if attribute:
                    repeat = int(attribute) - 1
                    for j in range(repeat):
                        if i >= cellsPerRow:
                            break

                        cells.append(content)
                        i += 1
            if cells:
                rows.append(cells)
        return rows



class OdsReader(File):
    EXTENSION = '.ods'
    _SEPARATOR = ','
    _rowTitles = []

    _DIVIDER = FileExport._DIVIDER

    def __init__(self, filePath, **kwargs):
        super().__init__(filePath)
        self._rows = []

    def read(self):
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
    DESCRIPTION = _('Scene list')
    SUFFIX = '_scenelist'
    _SCENE_RATINGS = ['2', '3', '4', '5', '6', '7', '8', '9', '10']
    _rowTitles = ['Scene link', 'Scene title', 'Scene description', 'Tags', 'Scene notes', 'A/R',
                 'Goal', 'Conflict', 'Outcome', 'Scene', 'Words total',
                 '$FieldTitle1', '$FieldTitle2', '$FieldTitle3', '$FieldTitle4',
                 'Word count', 'Letter count', 'Status', 'Characters', 'Locations', 'Items']

    def read(self):
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
                i += 1
                i += 1

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
                i += 1
                i += 1
                try:
                    self.novel.scenes[scId].status = Scene.STATUS.index(cells[i])
                except ValueError:
                    pass
                i += 1
                i += 1
                i += 1


class OdsRCharList(OdsReader):
    DESCRIPTION = _('Character list')
    SUFFIX = '_charlist'
    _rowTitles = ['ID', 'Name', 'Full name', 'Aka', 'Description', 'Bio', 'Goals', 'Importance', 'Tags', 'Notes']

    def read(self):
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
    DESCRIPTION = _('Location list')
    SUFFIX = '_loclist'
    _rowTitles = ['ID', 'Name', 'Description', 'Aka', 'Tags']

    def read(self):
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
    DESCRIPTION = _('Item list')
    SUFFIX = '_itemlist'
    _rowTitles = ['ID', 'Name', 'Description', 'Aka', 'Tags']

    def read(self):
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
        super().__init__()
        self.newProjectFactory = NewProjectFactory(self.CREATE_SOURCE_CLASSES)
from com.sun.star.awt.MessageBoxResults import OK, YES, NO, CANCEL
from com.sun.star.awt.MessageBoxButtons import BUTTONS_OK, BUTTONS_OK_CANCEL, BUTTONS_YES_NO, BUTTONS_YES_NO_CANCEL, BUTTONS_RETRY_CANCEL, BUTTONS_ABORT_IGNORE_RETRY
from com.sun.star.awt.MessageBoxType import MESSAGEBOX, INFOBOX, WARNINGBOX, ERRORBOX, QUERYBOX


class UiUno(Ui):

    def ask_yes_no(self, text):
        result = msgbox(text, buttons=BUTTONS_YES_NO, type_msg=WARNINGBOX)
        return result == YES

    def set_info_how(self, message):
        self.infoHowText = message
        if message.startswith('!'):
            message = message.split('!', maxsplit=1)[1].strip()
            msgbox(message, type_msg=ERRORBOX)
        else:
            msgbox(message, type_msg=INFOBOX)

    def show_warning(self, message):
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

