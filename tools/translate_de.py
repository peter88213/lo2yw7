"""Generate German translation files for GNU gettext.

- Update the project's 'de.po' translation file.
- Generate the language specific 'pywriter.mo' dictionary.

Usage: 
translate_de.py

File structure:

├── PyWriter/
│   ├── i18n/
│   │   └── de.json
│   └── src/
│       ├── translations.py
│       └── msgfmt.py
└── lo2yw7/
    ├── src/ 
    ├── tools/ 
    │   └── translate_de.py
    └── i18n/
        ├── messages.pot
        ├── de.po
        └── locale/
            └─ de/
               └─ LC_MESSAGES/
                  └─ pywriter.mo
    
Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/lo2yw7
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import sys
sys.path.insert(0, f'{os.getcwd()}/../../PyWriter/src')
import translations
import msgfmt

APP_NAME = 'lo2yw7'
PO_PATH = '../i18n/de.po'
MO_PATH = '../i18n/locale/de/LC_MESSAGES/pywriter.mo'


def main(version='unknown'):
    if translations.main('de', app=APP_NAME, appVersion=version):
        print(f'Writing "{MO_PATH}" ...')
        msgfmt.make(PO_PATH, MO_PATH)
    else:
        sys.exit(1)


if __name__ == '__main__':
    try:
        main(sys.argv[1])
    except:
        main()
