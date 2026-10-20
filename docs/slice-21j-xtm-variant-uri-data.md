# Slice 21J — Variant ResourceData mit xsd:anyURI

## Ausgangszustand und Norm

Branch: `codex/xtm-slice-21j`. Ausgangscommit und vorgesehener Parent:
`4d7adecb3c2d5df90579aa37dfa41128988cb56c`.
Der vorgefundene Branch war `codex/xtm-slice-21i`; Index und Arbeitsbaum waren
sauber. [initial-state.json](../reports/slice-21j/initial-state.json) sichert den
Zustand und die SHA-256-Werte aller ursprünglich versionierten Dateien.

Vor jeder Reader-Änderung reproduzierte ein frischer SBCL-Prozess alle 1557
XTM-Prüfungen und sämtliche 124 Originaldiagnosen. Der registrierte
Ausgangsstand ist **XTM 59 PASS, 0 FAIL, 65 NOT-RUN** und
**CTM 262 PASS, 4 FAIL, 7 NOT-RUN**. Die Ausgaben entsprechen Slice 21I.
Siehe [baseline.log](../reports/slice-21j/baseline.log),
[baseline-xtm.json](../reports/slice-21j/baseline-xtm.json) und
[before-diagnostics.json](../reports/slice-21j/before-diagnostics.json).

Normativ hergeleitet aus
[XTM 2.0 §§4.3.4 und 4.16.1–4.16.2](https://www.isotopicmaps.org/sam/sam-xtm/):
Der textuelle `resourceData`-Inhalt mit Datentyp `xsd:anyURI` wird über die
XTM-Prozent-/UTF-8-Dekodierung und Auflösung gegen die Document IRI zum absoluten
Locator. Kindelemente sind dabei ein Fehler. Das `datatype`-Attribut bezeichnet
selbst eine absolute IRI und wird als Datentyp übernommen. Ohne Datentyp sowie
mit `xsd:string` bleibt der Textwert erhalten. §§4.12–4.13 und
[TMDM §5.5](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/) bestimmen
Parent, Scope-Vereinigung, echte Obermengenbedingung und Variant-Gleichheit.
Die folgenden Befunde sind tatsächliche Ausführungsergebnisse.

## Begrenzte Reader-Erweiterung

Nur `src/xtm/reader.lisp` enthält Produktionsänderungen:

- `validate-source` akzeptiert nun textuelles `resourceData` mit `xsd:anyURI`.
  Das Datentypattribut wird mit den vorhandenen Scheme-/IRI-Prüfungen als
  absolute IRI validiert; es wird weder relativ aufgelöst noch als gespeicherter
  Datentyp umgeschrieben. Relative oder ungültige Datentypattribute werden
  zurückgewiesen. Andere gültige, nicht unterstützte Datentypen bleiben
  `XTM-UNSUPPORTED/:resource-data-datatype`.
- Alle XML-Kindelemente unter anyURI-`resourceData` ergeben
  `XTM-REJECTION/:unexpected-child`, einschließlich fremder Namespaces.
- `read-variant` sammelt die XML-Zeicheninformationen unverändert und ruft für
  anyURI-Text den vorhandenen XTM-`resolve-iri` auf. Der absolute Wert und
  `iri-datatype` gehen an das bestehende `add-variant`. Es gibt keine
  zusätzliche Whitespace-Bereinigung und keine zweite IRI-Implementierung.
- Der `resourceRef`-Pfad bleibt `leaf-href` mit demselben Resolver. Der
  textuelle String-Pfad, Scope-Vereinigung, Normalisierung und kanonische
  Handles bleiben bestehen. Ressourcen werden nicht abgerufen.

TMDM, CTM, CXTM, XML und deren Produktionsdateien sind unverändert.
Weitere Datentypen, `xsd:anyType`/XML-Kanonisierung, Variant-Item-Identifier,
Reification, Occurrences, explizite Associations/Roles, XTM-`mergeMap` und
XTM 2.1 wurden nicht implementiert.

## Unveränderter Originalvertrag

Einziger neu registrierter Originalvertrag:
[variant-resourcedata-uri.xtm](../vendor/cxtm/xtm2/in/variant-resourcedata-uri.xtm).
Die vollständige Originalquelle hat **405 Bytes**, SHA-256
`9bfd355a4f3f4a8c5a1d9ca7af842e1f9330d10f0b0a3be6b4606f614b2c8ba0`. Der tatsächliche Inhalt lautet
`http://example.org/command.wav`; das tatsächliche Datentypattribut ist
`http://www.w3.org/2001/XMLSchema#anyURI`. Der Zeilenumbruch vor dem schließenden
Starttag gehört zur Attributdarstellung, nicht zum Ressourceninhalt.

Document IRI:
`https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/variant-resourcedata-uri.xtm`.
Source Key: `xtm2/in/variant-resourcedata-uri.xtm`.
Die unveränderten Rohbytes werden durch `topic-maps.xtm:deserialize-octets` und
den qualifizierten XML-Parser verarbeitet. Es ist keine weitere Sprachfähigkeit
für dieses Original nötig.

Das tatsächliche TMDM-Modell hat drei Topics, keine Associations, einen Name
`Topic` am Owner `DocumentIRI#topic` und genau einen Variant:

- Absoluter Value: **`http://example.org/command.wav`**.
- Datatype: **`http://www.w3.org/2001/XMLSchema#anyURI`**.
- Parent ist per `EQ` genau der tatsächliche kanonische Name. Name-Parent und
  Owner sind `EQ`; Name und Variant sind jeweils ihre kanonischen Handles.
- Name-Scope: leer. Variant-Scope: genau der kanonische `DocumentIRI#command`-
  Topic, per `EQ` geprüft. Der Default-Name-Type besitzt seinen vorgesehenen SI.
- Keine zusätzlichen Ressourcen-Topics, Subject Locators, Subject Identifier
  oder Item Identifier entstehen. Owner und Theme behalten ausschließlich
  ihre dokumentbezogenen Item Identifier. Name und Variant haben keine Item
  Identifier oder Reifier.

Die Originalbaseline hat **621 Bytes**. Tatsächlich erzeugt und vollständig
verglichen wurden **621/621 identische Bytes**, einschließlich abschließendem
LF. `firstDifferentByte` und tatsächliche Condition sind `null`.
Die [tatsächliche CXTM-Ausgabe](../reports/slice-21j/actual/variant-resourcedata-uri.xtm.cxtm)
und die [Originalbaseline](../vendor/cxtm/xtm2/baseline/variant-resourcedata-uri.xtm.cxtm)
haben beide SHA-256:

```text
d4df2bef650becff7918ee85af338631c87a4309ad65e64a26ee93edbb42a8bb
```

Die Kanonisierung ist deterministisch und verändert das native Modell oder die
Rohbytes nicht. Ein anderer Source Key bei gleicher Document IRI erzeugt
dasselbe Modell und dieselben CXTM-Bytes.

[variant-uri-data-original.json](../reports/slice-21j/variant-uri-data-original.json)
enthält alle Originalbytes als Hex und Text, vollständige Ist-/Soll-CXTM-Texte,
Hashes, Document IRI, Condition und tatsächliches Modell.
Der vorhandene Case-Record-Executor klassifiziert nach Deserialisierung und
nativen Modellprüfungen den vollständigen Bytevergleich. Das Original wird im
regulären ASDF-Testlauf genau einmal ausgeführt und als `cxtm-match`/PASS
registriert. Es gibt insgesamt 60 eindeutige Case Records: 52 positive und acht
ursachenqualifizierte negative Originalverträge. Die bisherigen 59 Ergebnisse
sind unverändert.

## ResourceData-/ResourceRef-Äquivalenz und native Gegenproben

Die synthetische Gegenprobe verwendet dieselbe Document IRI, denselben Name-
Scope `base`, denselben expliziten Scope `extra` und den Locatorinhalt
`relative-resource.wav` in beiden XML-Formen. Beide erzeugen denselben
absoluten Value:

```text
https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/relative-resource.wav
```

Das vollständige native Modell, `xsd:anyURI`, der vereinigte Scope und CXTM
sind gleich. Bei beiden XML-Formen gemeinsam entsteht durch Normalisierung
nur ein Variant; es bleiben vier Topics ohne zusätzliche Ressourcenidentität.
Eine weitere schrittweise Gegenprobe vereinigt zwei Parent-Topics über ihren
Item Identifier und prüft erhaltene Name-/Variant-Handles beider Formen mit
`canonical-topic-name`, `canonical-variant` und `EQ`.
Diese synthetischen Gegenproben zählen nicht als Originalverträge.

Die **58 neuen protokollierten Kontrollen** umfassen 14 positive XTM-Eingaben,
zehn schrittweise native Handle-Prüfungen, eine explizite Äquivalenzprüfung und
33 Fehler-/Unsupported-/Atomaritätsprüfungen. Sie decken absolute und relative
IRIs, Fragmente, leere Referenzen, Unicode, UTF-8-Prozentkodierung, reservierte
Zeichen, XML-Escaping, andere Document IRI, Datei-/Netzlocators ohne Abruf und
die Trennung von Ressourcenwerten und Topic-SI/SL/II ab.

Doppelte Variants normalisieren; unterschiedliche Values, Datatypes oder
Scopes bleiben getrennt. Scope-Vererbung, Forward References und alle neun
Kombinationen von Parent-/Name-Scope-/Variant-Scope-Merging mit SI/SL/II
behalten kanonische Parent-, Name-, Variant- und Theme-Referenzen. Drei native
Gegenproben belegen atomare Zurückweisung von Scope-Kollapsen ohne Änderung
vorhandener Zustände oder Handles. Ein Parse-Zähler belegt, dass eine externe
XML-Ressource nicht rekursiv deserialisiert wird. Auch ein nicht vorhandener
`file:`-Locator wird nur als Wert verarbeitet.

Die früheren `resourceRef`-Original- und Kontrollreports bleiben vollständig
identisch. Alle bisherigen XTM-Prüfungen bleiben in ihrer relativen Reihenfolge
erhalten; lediglich zwei Labels der umgestellten Unsupported-Gegenprobe
wurden umbenannt. Der reguläre Lauf besteht mit **1713
Prüfungen**, davon **156 neue** zusätzlich zu den bisherigen 1557.

## Tatsächliche Conditions und Syntaxgrenzen

Die folgende Tabelle stammt aus `variantResourceDataURIControls` in
[xtm.json](../reports/slice-21j/xtm.json). Die vollständigen Eingaben, Kontexte
und Causes sind dort erhalten. SAX-Zeilen/Spalten sind ungefähre
Zeichenpositionen; native TMDM-Conditions besitzen keine Quellposition.

| Gegenprobe | Condition | Fehlercode | Zeile:Spalte |
| --- | --- | --- | --- |
| `invalid-iri` | `XTM-REJECTION` | `invalid-iri` | 1:209 |
| `leading-space-not-trimmed` | `XTM-REJECTION` | `invalid-iri` | 1:209 |
| `trailing-space-not-trimmed` | `XTM-REJECTION` | `invalid-iri` | 1:209 |
| `tab-not-trimmed` | `XTM-REJECTION` | `invalid-iri` | 1:209 |
| `invalid-decoded-iri` | `XTM-REJECTION` | `invalid-iri` | 1:209 |
| `invalid-relative-iri` | `XTM-REJECTION` | `invalid-iri` | 1:209 |
| `percent-short` | `XTM-REJECTION` | `invalid-percent-escape` | 1:209 |
| `percent-hex` | `XTM-REJECTION` | `invalid-percent-escape` | 1:209 |
| `percent-incomplete-utf8` | `XTM-REJECTION` | `invalid-percent-utf8` | 1:209 |
| `percent-overlong-utf8` | `XTM-REJECTION` | `invalid-percent-utf8` | 1:209 |
| `percent-surrogate` | `XTM-REJECTION` | `invalid-percent-utf8` | 1:209 |
| `extra-attribute` | `XTM-REJECTION` | `unexpected-attribute` | 1:221 |
| `relative-datatype` | `XTM-REJECTION` | `invalid-resource-data-datatype` | 1:178 |
| `empty-datatype` | `XTM-REJECTION` | `invalid-resource-data-datatype` | 1:170 |
| `invalid-datatype-scheme` | `XTM-REJECTION` | `invalid-resource-data-datatype` | 1:183 |
| `invalid-datatype-IRI` | `XTM-REJECTION` | `invalid-iri` | 1:186 |
| `invalid-datatype-percent` | `XTM-REJECTION` | `invalid-percent-escape` | 1:178 |
| `foreign-child` | `XTM-REJECTION` | `unexpected-child` | 1:232 |
| `XTM-child` | `XTM-REJECTION` | `unexpected-child` | 1:216 |
| `mixed-resources` | `XTM-REJECTION` | `variant-resource-cardinality` | 1:256 |
| `multiple-data` | `XTM-REJECTION` | `variant-resource-cardinality` | 1:294 |
| `wrong-order` | `XTM-REJECTION` | `missing-variant-scope` | 1:173 |
| `scope-after-resource` | `XTM-REJECTION` | `element-order` | 1:236 |
| `integer-still-unsupported` | `XTM-UNSUPPORTED` | `resource-data-datatype` | 1:210 |
| `anyType-still-unsupported` | `XTM-UNSUPPORTED` | `resource-data-datatype` | 1:210 |
| `equal-scope` | `VARIANT-ERROR` | `invalid-variant-scope` | nicht vorhanden (TMDM) |
| `duplicate-scope-no-new-theme` | `VARIANT-ERROR` | `invalid-variant-scope` | nicht vorhanden (TMDM) |
| `SI-alias-adds-no-theme` | `VARIANT-ERROR` | `invalid-variant-scope` | nicht vorhanden (TMDM) |
| `forward-merge-collapses-proper-scope` | `VARIANT-ERROR` | `variant-scope-collapse` | nicht vorhanden (TMDM) |
| `invalid-raw-UTF8` | `XTM-XML-ERROR` | `xml-not-well-formed` | 1:7 |
| `collapse-SUBJECT-IDENTIFIER` | `VARIANT-ERROR` | `variant-scope-collapse` | nicht vorhanden (TMDM) |
| `collapse-SUBJECT-LOCATOR` | `VARIANT-ERROR` | `variant-scope-collapse` | nicht vorhanden (TMDM) |
| `collapse-ITEM-IDENTIFIER` | `VARIANT-ERROR` | `variant-scope-collapse` | nicht vorhanden (TMDM) |

Die rohe UTF-8-Fehleingabe bewahrt die XML-Cause
`WELL-FORMEDNESS-VIOLATION` zum ungültigen Startbyte `11111111`.
Beide anyURI-XML-Kindfälle erreichen ausdrücklich Syntaxfehler und kein
Unsupported. Gültiges `xsd:integer` mit Wert `42` und `xsd:anyType` mit fremdem
XML bleiben spezifisch Unsupported. Führende, folgende und eingebettete
Whitespace-Zeichen werden nicht stillschweigend entfernt. Die Tests bewahren
die Trennung von Syntaxfehlern, XML-Fehlern, Unsupported und TMDM-Conditions.

## Umgestellte Unsupported-Fixtures

Vorhandene Fixtures mit inzwischen unterstütztem anyURI-Inhalt wurden durch
gültiges `xsd:integer` mit lexikalischem Wert `42` ersetzt. Klasse und Code
bleiben `XTM-UNSUPPORTED/:resource-data-datatype`. Dies betrifft die
Klassifikationskontrollen, die Unsupported-Gegenproben für Names, Scope, Item
Identity und Variants sowie die entsprechende Testeingabe im CTM/XTM-Adapter.
Nur Tests wurden dabei angepasst; kein CTM-Produktionscode änderte sich.

Fünf vorhandene XTM-Kontrollzeilen erhalten neue Fixture-Eingaben und passende
Positionen; eine weitere Zeile zum unverändert ausgeschlossenen Datentyp
`urn:other` ändert ausschließlich die präzisierte Unsupported-Meldung.
Die Labels `variant-syntax:resourceData-anyURI:class-code` und
`variant-syntax:resourceData-anyURI:context-position` heißen jetzt entsprechend
`resourceData-integer`. Alle anderen alten Kontrollzeilen sind unverändert.
Die 48 übernommenen Nicht-XTM-Reports sind strukturell identisch zu Slice 21I.

## Vollständiger Diagnosevergleich aller 124 Originale

Es ändern sich genau zwei Beobachtungen:

1. `xtm2/in/variant-resourcedata-uri.xtm`: zuvor
   `XTM-UNSUPPORTED/:resource-data-datatype`, Position **10:24**; danach keine
   Condition und vollständiger 621-Byte-CXTM-Vergleich bestanden. Nur dieses
   Original wird neu registriert.
2. `xtm2/in/variant-datatype-unknown.xtm`: weiterhin
   `XTM-UNSUPPORTED/:resource-data-datatype`, Position **9:59**. Nur `detail`
   und der entsprechende Meldungsteil nennen nun `xsd:string` und
   `xsd:anyURI` als implementierte Datentypen. Klasse, Code, Position,
   Ablehnung und NOT-RUN-Registrierung bleiben unverändert.

Die übrigen **122 vollständigen Beobachtungen sind identisch**.
[diagnostic-changes.json](../reports/slice-21j/diagnostic-changes.json) enthält
beide vollständigen Vorher-/Nachher-Beobachtungen mit konkreter Ursache.
Aus Diagnoseerfolgen wird kein weiterer Originalvertrag registriert.

## Vollständige Offline-Abnahme

Alle Testprozesse laufen in frischem **SBCL 2.5.4** ohne System-/Benutzerinit.
Die bereits gepinnten lokalen Abhängigkeiten und vorhandenen XML-Patches werden
geprüft und temporär verwendet. Für Quellvorbereitung, Tests und Diagnose gilt
zusätzlich:

```text
(version 1)(allow default)(deny network*)(deny file-write* (subpath "/Users/rgb/workspace/topic-maps"))
```

Die reguläre `require_escalated`-Freigabe war erfolgreich. Die Konfiguration
und `~/.nix-profile` wurden nicht verändert. Es gibt keine neuen Downloads,
keinen Zugriff auf langlebige Lisp-Images und keinen vollständigen Nix-Neubau.
Letzterer ist ausdrücklich NOT-RUN; die frische Offline-SBCL-Regression wurde
vollständig ausgeführt.

| Bereich | Bestandene Prüfungen |
| --- | ---: |
| Bisherige Lisp-Regression einschließlich TMDM, CTM/CXTM, Include und Mergemap | 12100 |
| XTM einschließlich aller bisherigen und des neuen Originals | 1713 |
| XML-Qualifikation | 146 |
| XTM-MERGEMAP | 217 |
| REGISTERED-ORIGINALS | 286 |
| REGISTERED-NEGATIVES | 25 |
| PROLOG | 171 |
| EMPTY2 | 13 |
| CTM-INTEGER | 112 |
| TRIPLE | 226 |
| ENCODING | 722 |
| Python-Unittests | 2 |
| NFC-Oracle-Vergleiche | 16294 |
| Isolierte, erwartet scheiternde Executor-Kontrollen | 50 |

Die **50 Executor-Kontrollen** erhalten die bisherigen 45 Fehlerpfade und
fügen für das neue Original Byteabweichung, XML-Fehler, Unsupported, TMDM-Fehler
und eine falsche XTM-Condition hinzu. Alle erzeugen den erwarteten ASDF-Exit 1;
keine dieser Injektionen zählt als positiver PASS. Die zuvor registrierten
Originalergebnisse bleiben jeweils erhalten. Siehe
[failure-controls.json](../reports/slice-21j/failure-controls.json) und die
zugehörigen Logs und Einzelreports.

Nach tatsächlicher erfolgreicher Ausführung lautet der registrierte Stand:

| Korpus | PASS | FAIL | NOT-RUN |
| --- | ---: | ---: | ---: |
| XTM | 60 | 0 | 64 |
| CTM | 262 | 4 | 7 |

Die XTM-NOT-RUN-Zahl umfasst 61 positive und drei negative offene Originale.
Die vier bekannten CTM-FAILs bleiben unverändert: `include-template.ctm`,
`include-wildcard2.ctm`, `occurrence-datetime-timezone2.ctm` und
`occurrence-datetime2.ctm`.

## Integrität und Reproduktion

Alle **2006 gepinnten Korpusdateien** entsprechen
weiterhin in Größe und SHA-256 `references/corpus-lock.json`.
Alle **2319 historischen Reportdateien** und
**4564 geschützten Dateien** des Ausgangscommits
bleiben byteidentisch. Die Hashlisten sowie alle geprüften Ausführungsquellen
stehen in [integrity.json](../reports/slice-21j/integrity.json).

[execution.json](../reports/slice-21j/execution.json) enthält sämtliche Befehle,
UTC-Zeitpunkte, erwarteten und tatsächlichen Exitcodes sowie die registrierten
Stände. [precommit-audit.json](../reports/slice-21j/precommit-audit.json) sichert
den finalen Änderungsumfang;
[artifacts.json](../reports/slice-21j/artifacts.json) enthält Größen und
SHA-256-Werte aller neuen Artefakte.

Reproduktion mit unbenutztem Ausgabeverzeichnis außerhalb des Repositorys:

```sh
python3 scripts/validate-slice-21j.py --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl --output /private/tmp/topic-maps-21j-recheck
```

Reader-Erweiterung, Tests, Dokumentation und geprüfte Ausführungsevidenz werden
zusammen lokal committet. Slice 21J endet damit.
