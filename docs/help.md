[Project home page](https://peter88213.github.io/lo2yw7/) > Main help page

------------------------------------------------------------------------

# Export to yw7

## Command reference

### "Files" menu

-   [Export to yWriter](#export-to-ywriter) 

### "Format" menu

-   [Replace scene dividers with blank lines](#replace-scene-dividers-with-blank-lines)
-   [Indent paragraphs that start with '> '](#indent-paragraphs-that-start-with)
-   [Replace list strokes with bullets](#replace-list-strokes-with-bullets)

------------------------------------------------------------------------

## General

### About formatting text

It is assumed that very few types of text markup are needed for a fictional text:

- *Emphasized* (usually shown as italics).
- *Strongly emphasized* (usually shown as capitalized).
- *Citation* (paragraph visually distinguished from body text).

When exporting to yw7 format, the converter replaces these formattings as follows: 

- *Emphasized* is converted to *italics*.
- *Strongly emphasized* is converted to *bold*. 
- *Quotations* paragraphs are prefixed with `"> "`.


### About document language handling

ODF documents are generally assigned a language that determines spell checking and country-specific character substitutions. In addition, Office Writer lets you assign text passages to languages other than the document language to mark foreign language usage or to suspend spell checking. 

#### Document overall

- If a document language (Language code acc. to ISO 639-1 and country code acc. to ISO 3166-2) is detected in the source document during conversion to yw7 format, these codes are set as yWriter project variables. 

#### Text passages in scenes

If text markups for other languages are detected during conversion to the yw7 format, they are converted and transferred to the yWriter scene. 

This then looks like this, for example:

`xxx xxxx [lang=en-AU]yyy yyyy yyyy[/lang=en-AU] xxx xxx` 

To prevent these text markups from interfering with *yWriter*, they are automatically set as project variables in such a way that *yWriter* interprets them as HTML instructions during document export. 

For the example shown above, the project variable definition for the opening tag looks like this: 

- *Variable Name:* `lang=en-AU` 
- *Value/Text:* `<HTM <SPAN LANG="en-AU"> /HTM>`

The point of this is that such language assignments are preserved even after multiple conversions in both directions, so they are always effective for spell checking in the ODT document.

It is recommended not to modify such markups in yWriter to avoid unwanted nesting and broken enclosing. 

## HowTo

## How to set up a work in progress for export

A work in progress has no third level heading.

-   *Heading 1* → New chapter title (beginning a new section).
-   *Heading 2* → New chapter title.
-   `* * *` → Scene divider (not needed for the first scenes in a
    chapter).
-   Comments right at the scene beginning are considered scene titles.
-   All other text is considered scene content.

## How to set up an outline for export

An outline has at least one third level heading.

-   *Heading 1* → New chapter title (beginning a new section).
-   *Heading 2* → New chapter title.
-   *Heading 3* → New scene title.
-   All other text is considered to be chapter/scene description.

[Top of page](#top)

------------------------------------------------------------------------

## Export to yWriter

This writes back the document's content to the yWriter project file.

-   Make sure not to change a generated document's file name before
    writing back to yWriter format.
-   The yWriter 7 project to rewrite must exist in the same folder as
    the document.
-   If the document's file name has no suffix, the document is
    considered a [Work in
    progress](#how-to-set-up-a-work-in-progress-for-export) or an
    [Outline](#how-to-set-up-an-outline-for-export) to be exported into
    a newly created yWriter project. **Note:** Existing yWriter projects
    will not be overwritten.

[Top of page](#top)

------------------------------------------------------------------------

## Replace scene dividers with blank lines

This will replace the three-line "* * *" scene dividers
with single blank lines. The style of the scene-dividing
lines will be changed from  _Heading 4_  to  _Heading 5_.

[Top of page](#top)

------------------------------------------------------------------------

## Indent paragraphs that start with '> '

This will select all paragraphs that start with "> "
and change their paragraph style to _Quotations_.

Note: When exporting to yWriter, _Quotations_ style paragraphs will
automatically marked with "> " at the beginning.

[Top of page](#top)

------------------------------------------------------------------------

## Replace list strokes with bullets

This will select all paragraphs that start with "- "
and apply a list paragraph style.

Note: When exporting to yWriter, Lists will
automatically marked with "- " list strokes.

[Top of page](#top)

------------------------------------------------------------------------

