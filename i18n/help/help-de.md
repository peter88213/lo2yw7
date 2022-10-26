[Projekt-Homepage](https://peter88213.github.io/lo2yw7/) &gt;
Haupt-Hilfeseite

------------------------------------------------------------------------

# Export zu yw7


## Befehlsreferenz

### "Datei"-Menü

-   [Zu yWriter exportieren](#zu-ywriter-exportieren)

### "Format"-Menü

-   [Szenentrenner durch Leerzeilen
    ersetzen](#szenentrenner-durch-leerzeilen-ersetzen)
-   [Absätze einrücken, die mit '> ' beginnen'](#absätze-einrücken-die-mit-beginnen)
-   [Aufzählungsstriche ersetzen](#aufzählungsstriche-ersetzen)

------------------------------------------------------------------------

## Allgemeines


### Zur Textformatierung

Es wird davon ausgegangen, dass für einen fiktionalen Text nur sehr wenige Arten von Textauszeichnungen erforderlich sind:

- *Betont* (üblicherweise in Kursivschrift dargestellt).
- *Stark betont* (üblicherweise in Großbuchstaben dargestellt).
- *Zitat* (Absatz optisch vom Fließtext unterschieden).

Beim Exportieren in das yw7-Format ersetzt der Konverter diese Formatierungen wie folgt: 

- *Betont* wird zu *kursiv*.
- *Stark betont* wird zu *fett*. 
- *Zitat*-Absätzen wird `"> "` vorangestellt. 


### Zur Sprache des Dokuments

ODF-Dokumenten ist im allgemeinen eine Sprache zugeordnet, welche die Rechtschreibprüfung und länderspezifische Zeichenersetzungen bestimmt. Außerdem kann man in Office Writer Textpassagen von der Dokumentsprache abweichende Sprachen zuordnen, um Fremdsprachengebrauch zu markieren oder die Rechtschreibprüfung auszusetzen. 

#### Dokument insgesamt

- Wenn bei der Konvertierung in das yw7-Format eine Dokument-Sprache (Sprachencode gem. ISO 639-1 und Ländercode gem. ISO 3166-2) im Ausgangsdokument erkannt wird, werden diese Codes als yWriter-Projektvariablen eingetragen.
    
#### Textpassagen in Szenen  

Wenn bei der Konvertierung in das yw7-Format Textauszeichnungen für andere Sprachen erkannt werden, werden diese umgewandelt und in die yWriter-Szene übernommen. 

Das sieht dann beispielsweise so aus:

`xxx xxxx [lang=de-CH]yyy yyyy yyyy[/lang=de-CH] xxx xxx`

Damit diese Textauszeichnungen in *yWriter* nicht stören, werden sie automatisch als Projektvariablen eingetragen, und zwar so, dass *yWriter* sie beim Dokumentenexport als HTML-Anweisungen interpretiert. 

Für das oben gezeigte Beispiel sieht die Projektvariablen-Definition für das öffnende Tag so aus:

- *Variable Name:* `lang=de-CH` 
- *Value/Text:* `<HTM <SPAN LANG="de-CH"> /HTM>`

Der Sinn der Sache liegt darin, dass solche Sprachenzuweisungen auch bei mehrmaligem Konvertieren in beide Richtungen erhalten bleiben, also im ODT-Dokument immer für die Rechtschreibprüfung wirksam sind.

Es wird empfohlen, solche Auszeichnungen nicht in yWriter zu verändern, um ungewollte Verschachtelungen und unterbrochene Umschließungen zu vermeiden. 


## So wird's gemacht

## Ein Manuskript zum Export vorbereiten

Ein in Arbeit befindliches Dokument hat keine Überschrift auf der dritten Ebene.

- *Überschrift 1* → Neue Kapitelüberschrift (Beginn eines neuen Abschnitts).
- *Überschrift 2* → Neuer Kapiteltitel.
- `* * *` → Szenentrenner (nicht erforderlich für die ersten Szenen eines Kapitels).
- Kommentare direkt am Anfang einer Szene gelten als Szenentitel.
- Alle anderen Texte gelten als Szeneninhalt.

## Eine Gliederung zum Export vorbereiten

Eine Gliederung hat mindestens eine Überschrift auf der dritten Ebene.

- *Überschrift 1* → Neue Kapitelüberschrift (Beginn eines neuen Abschnitts).
- *Überschrift 2* → Neue Kapitelüberschrift.
- *Überschrift 3* → Neuer Szenentitel.
- Alle anderen Texte werden als Kapitel-/Szenenbeschreibung betrachtet.

[Zum Seitenbeginn](#top)

------------------------------------------------------------------------

## Zu yWriter exportieren

Dadurch wird der Inhalt des Dokuments in die yWriter-Projektdatei zurückgeschrieben.

-   Stellen Sie sicher, dass Sie den Dateinamen eines generierten Dokuments vor dem Zurückschreiben in das yWriter-Formanicht ändern.
-   Das zu überschreibende yWriter 7 Projekt muss sich im selben Ordner befinden wie das Dokument.
-   Wenn der Dateiname des Dokuments kein Suffix hat, dient das Dokument als [Manuskript in Arbeit](#ein-manuskript-zum-export-vorbereiten) oder eine [Gliederung](#eine-gliederung-zum-export-vorbereiten) zum Exportieren in ein neu zu erstellendes yWriter-Projekt. **Hinweis:** Bestehende  yWriter-Projekte werden nicht überschrieben.


[Zum Seitenbeginn](#top)

------------------------------------------------------------------------

## Szenentrenner durch Leerzeilen ersetzen

Dadurch werden die dreizeiligen "\* \* \*"-Szenentrennlinien durch einzelne Leerzeilen ersetzt. Der Stil der szenenunterteilenden Zeilen wird von *Überschrift 4* auf *Überschrift 5* geändert.

[Zum Seitenbeginn](#top)

------------------------------------------------------------------------

## Absätze einrücken, die mit '&gt;' beginnen'

Dadurch werden alle Absätze ausgewählt, die mit "&gt; " beginnen, und ihr Absatzstil wird in *Quotations* geändert.

Hinweis: Beim Export in yWriter werden Absätze im Stil *Quotations* automatisch mit "&gt; " am Anfang markiert.

[Zum Seitenbeginn](#top)

------------------------------------------------------------------------

## Aufzählungsstriche ersetzen

Dadurch werden alle Absätze, die mit "-" beginnen, ausgewählt und mit einem Listenabsatzstil versehen.

Hinweis: Beim Export in yWriter werden Listen automatisch mit "-"-Listenstrichen markiert.

[Zum Seitenbeginn](#top)

------------------------------------------------------------------------

