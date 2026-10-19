# Slice 21I — XTM Variant ResourceRef

## Ausgangszustand und begrenzte Änderung

Branch: `codex/xtm-slice-21i`. Ausgangscommit und vorgesehener Parent:
`034d2c14fbf6a58a062351e4b64680283d241d22`.
Der vorgefundene Branch war `codex/xtm-slice-21h`; Index und Arbeitsbaum waren
sauber. [initial-state.json](../reports/slice-21i/initial-state.json) sichert alle
ursprünglich versionierten Dateien über SHA-256.

Vor der Reader-Änderung wurden die 1414 XTM-Prüfungen und alle 124
Originaldiagnosen in einem frischen Offline-Prozess reproduziert. Die Ergebnisse
sind identisch zu Slice 21H: **XTM 57 PASS, 0 FAIL, 67 NOT-RUN** und
**CTM 262 PASS, 4 FAIL, 7 NOT-RUN**.
Siehe [baseline.log](../reports/slice-21i/baseline.log),
[baseline-xtm.json](../reports/slice-21i/baseline-xtm.json) und
[before-diagnostics.json](../reports/slice-21i/before-diagnostics.json).

Nur `src/xtm/reader.lisp` enthält eine Produktionsänderung:

- `validate-source` akzeptiert die bereits eingeordnete Variant-Alternative
  `resourceRef` nach der vorhandenen `leaf-href`-Validierung.
- `read-variant` verwendet für `resourceRef` denselben `leaf-href`-/IRI-Pfad und
  übergibt dessen absoluten Locator sowie `iri-datatype` an `add-variant`.
  Für textuelles `resourceData` bleibt der Wertpfad mit `string-datatype` erhalten.
- Scope-Vereinigung, echte Obermengenbedingung, Normalisierung und kanonische
  Handles verwenden weiterhin die bestehenden TMDM-Operationen. Die
  Topic-Referenzauflösung `reference-iri` wird weiterhin nur für die Scope-Topics
  verwendet; der Ressourcenlocator löst keine Topic-Suche oder Erzeugung aus.

Es gibt keine Produktionsänderung an TMDM, CTM, CXTM oder XML und keine zweite
IRI-Implementierung. `resourceData` mit `xsd:anyURI`, andere neue Datentypen,
Variant-Item-Identifier, Reification, Occurrences, explizite Associations/Roles,
XTM-`mergeMap` und XTM 2.1 bleiben außerhalb des implementierten Umfangs.

## Normative Herleitung

[XTM 2.0 §§4.3.3–4.3.4](https://www.isotopicmaps.org/sam/sam-xtm/)
verlangen UTF-8-Prozentdekodierung und absolute Auflösung gegen die Document
IRI. §4.17 ordnet den Ressourcenlocator dem Variant-Wert und `xsd:anyURI` dem
Datentyp zu. §§4.12–4.13 vereinigen den expliziten Scope mit dem Name-Scope.
Anders als `topicRef` braucht `resourceRef` keinen XPointer-Shorthand-Fragmentbezeichner.
[TMDM §5.5](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/)
verlangt einen Variant-Scope als echte Obermenge des Parent-Name-Scope und
bestimmt Variant-Gleichheit über Parent, Value, Datatype und Scope.
Die folgenden Befunde stammen aus der tatsächlichen Ausführung.

## Zwei unveränderte Originalverträge

| Original | Quellbytes | Tatsächliches `href` | CXTM-Ist/Soll-Bytes | Vergleich |
| --- | ---: | --- | ---: | --- |
| `variant-resourceref.xtm` | 324 | `http://example.org/command.wav` | 621/621 | PASS |
| `variant-resourceref-relative.xtm` | 311 | `topic-command.wav` | 608/608 | PASS |

Für jeden Vertrag lautet die Document IRI:
`https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/`
plus dessen Case-ID `xtm2/in/<Dateiname>`. Der Source Key ist die Case-ID.
Die unveränderten Rohbytes werden über `topic-maps.xtm:deserialize-octets` und
den qualifizierten XML-Parser deserialisiert.

Tatsächlich gespeicherte absolute Ressourcenwerte:

```text
http://example.org/command.wav
https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/topic-command.wav
```

Beide Variants haben den Datentyp
`http://www.w3.org/2001/XMLSchema#anyURI`.
Die relative Darstellung `topic-command.wav` in der zweiten CXTM-Baseline ist
eine Darstellung der Kanonisierung; im TMDM-Modell steht der oben geprüfte
absolute Locator. Beide vollständigen Originalvergleiche sind byteidentisch,
`firstDifferentByte` und tatsächliche Condition sind jeweils `null`.

Native Assertions prüfen für beide Originale:

- Genau drei Topics, keine Associations, ein Name mit Value `Topic` und ein
  Variant. Der Owner hat nur `DocumentIRI#topic` als Item Identifier, der
  Theme-Topic nur `DocumentIRI#command`. Der Default-Name-Type hat nur den
  vorgesehenen Subject Identifier. Es entstehen keine Ressourcen-Topics,
  Subject Locators oder zusätzlichen Subject/Item Identifier.
- Name-Parent und Owner sind `EQ`, Variant-Parent und Name sind `EQ`, Name-
  und Variant-Handles sind kanonisch. Der Name-Scope ist leer, der Variant-Scope
  enthält genau den kanonischen `command`-Topic. Keine Item Identifier oder
  Reifier entstehen an Name oder Variant.
- Die Kanonisierung ist deterministisch und lässt native Modellzustände und
  Rohbytes unverändert. Ein unabhängiger Source Key bei gleichem Document IRI
  ergibt dasselbe vollständige Modell und dieselben CXTM-Bytes.

Der bestehende Case-Record-Executor klassifiziert erst nach Deserialisierung,
nativen Prüfungen und Erzeugung der tatsächlichen CXTM-Bytes. Nur identische
Originalbytes/Baselines ergeben `cxtm-match` und PASS. Jeder der beiden Fälle
wird genau einmal im regulären ASDF-Lauf ausgeführt. Insgesamt sind es 59
verschiedene Case Records: 51 positive und acht ursachenqualifizierte negative
Originalverträge. Alle bisherigen 57 Originalergebnisse sind unverändert.

[variant-resource-ref-originals.json](../reports/slice-21i/variant-resource-ref-originals.json)
enthält Rohbytes als Hex und Text, Document IRI, tatsächliche Modelle, sämtliche
CXTM-Texte und Hashes. Die unveränderten Originalbaselines und die tatsächlichen
Ausgaben in [actual/](../reports/slice-21i/actual/) haben dieselben SHA-256-Werte:

| Original | SHA-256 Quelle | SHA-256 Baseline und tatsächliche Ausgabe |
| --- | --- | --- |
| `variant-resourceref.xtm` | `3ef9cc70f8738b2729d446c4e685bd9a60d39ecef7c222cb2932a307791008ad` | `d4df2bef650becff7918ee85af338631c87a4309ad65e64a26ee93edbb42a8bb` |
| `variant-resourceref-relative.xtm` | `7eac62ef6eb43dd582f6bdf2810529161bcbec2cb6704ffed1c7a5b20515ef4e` | `2b5d69bc4bc9bb0bf5c7c3846a19344560b28f7fbd5c20b651be5189911787f0` |

## Dauerhafte Gegenproben und tatsächliche Conditions

Der ASDF-Testlauf führt **1557 eindeutige XTM-Prüfungen** aus:
1414 bisherige Prüfungen, davon zwölf sinnvoll umbenannte
Unsupported-Gegenproben, und 143 neue Prüfungen. Die relative
Ausführungsreihenfolge der bisherigen Prüfungen bleibt erhalten.

Die **48 neuen protokollierten Kontrollen** umfassen 14 positive XTM-Eingaben,
neun schrittweise Merge-Prüfungen und 25 Syntax-/Modell-/XML-Fehlerprüfungen.
Geprüft werden absolute, relative, leere und Fragmentreferenzen, Unicode,
UTF-8-Prozentkodierung, reservierte Prozentzeichen, XML-Escaping, abweichende
Document IRI, Datei- und externe XML-Locators ohne Abruf sowie identische
Locatorstrings als Ressourcenwerte und vorhandene Topic-Identifikatoren.
Ein zusätzlicher Zähler weist genau einen primären XML-Parse nach; es findet
keine rekursive Deserialisierung der referenzierten XML-Ressource statt.
Die Tests laufen mit Netzwerksperre. Auch ein nicht vorhandener `file:`-Locator
wird als Wert akzeptiert, ohne die Datei zu öffnen.

Scope-Vererbung, Forward References, doppelte Themes, gleichwertige Variants,
Trennung bei verschiedenen Values/Datatypes/Scopes und SI-/SL-/II-Merging
werden an tatsächlichen Modellobjekten geprüft. Die vorhandene schrittweise
Merge-Prüfung hält alte Name-, Variant- und Theme-Handles fest; alle neun
Kombinationen aus Parent-/Name-Scope-/Variant-Scope-Merging und SI/SL/II behalten
kanonische `EQ`-Referenzen. Unzulässige Scope-Kollapse werden in drei nativen
SI-/SL-/II-Gegenproben atomar und ohne Verlust vorhandener Handles abgelehnt.

Die tatsächlichen Fehler sind in
[xtm.json](../reports/slice-21i/xtm.json), Feld `variantResourceRefControls`,
mit Eingabe, Kontext und gegebenenfalls Cause dokumentiert. SAX-Positionen sind
ungefähre Zeichenpositionen; TMDM-Conditions besitzen keine Quellposition.

| Gegenprobe | Condition | Code | Zeile:Spalte |
| --- | --- | --- | --- |
| `missing-href` | `XTM-REJECTION` | `missing-attribute` | 1:158 |
| `extra-attribute` | `XTM-REJECTION` | `unexpected-attribute` | 1:183 |
| `namespaced-attribute` | `XTM-REJECTION` | `unexpected-attribute` | 1:202 |
| `child` | `XTM-REJECTION` | `unexpected-child` | 1:170 |
| `text` | `XTM-REJECTION` | `unexpected-text` | 1:170 |
| `invalid-iri` | `XTM-REJECTION` | `invalid-iri` | 1:175 |
| `invalid-decoded-iri` | `XTM-REJECTION` | `invalid-iri` | 1:174 |
| `invalid-relative-iri` | `XTM-REJECTION` | `invalid-iri` | 1:179 |
| `percent-short` | `XTM-REJECTION` | `invalid-percent-escape` | 1:173 |
| `percent-hex` | `XTM-REJECTION` | `invalid-percent-escape` | 1:174 |
| `percent-incomplete-utf8` | `XTM-REJECTION` | `invalid-percent-utf8` | 1:174 |
| `percent-overlong-utf8` | `XTM-REJECTION` | `invalid-percent-utf8` | 1:177 |
| `percent-surrogate` | `XTM-REJECTION` | `invalid-percent-utf8` | 1:180 |
| `mixed-ref-data` | `XTM-REJECTION` | `variant-resource-cardinality` | 1:185 |
| `multiple-ref` | `XTM-REJECTION` | `variant-resource-cardinality` | 1:198 |
| `wrong-order` | `XTM-REJECTION` | `missing-variant-scope` | 1:135 |
| `scope-after-resource` | `XTM-REJECTION` | `element-order` | 1:178 |
| `equal-scope` | `VARIANT-ERROR` | `invalid-variant-scope` | nicht vorhanden (TMDM) |
| `duplicate-scope-no-new-theme` | `VARIANT-ERROR` | `invalid-variant-scope` | nicht vorhanden (TMDM) |
| `SI-alias-adds-no-theme` | `VARIANT-ERROR` | `invalid-variant-scope` | nicht vorhanden (TMDM) |
| `forward-merge-collapses-proper-scope` | `VARIANT-ERROR` | `variant-scope-collapse` | nicht vorhanden (TMDM) |
| `invalid-raw-UTF8` | `XTM-XML-ERROR` | `xml-not-well-formed` | 1:7 |
| `collapse-SUBJECT-IDENTIFIER` | `VARIANT-ERROR` | `variant-scope-collapse` | nicht vorhanden (TMDM) |
| `collapse-SUBJECT-LOCATOR` | `VARIANT-ERROR` | `variant-scope-collapse` | nicht vorhanden (TMDM) |
| `collapse-ITEM-IDENTIFIER` | `VARIANT-ERROR` | `variant-scope-collapse` | nicht vorhanden (TMDM) |

Die rohe ungültige UTF-8-Eingabe hat zusätzlich die Cause
`WELL-FORMEDNESS-VIOLATION` mit der Meldung über das ungültige Startbyte `11111111`.
Syntaxfehler, XML-Fehler, TMDM-Konflikte und Unsupported bleiben getrennte
Ergebnisklassen.

## Anpassung bestehender Unsupported-Gegenproben

Da `resourceRef` jetzt unterstützt wird, prüfen die vorhandenen Unsupported-
Kontrollen stattdessen gültiges, weiterhin ausgeschlossenes `resourceData` mit
Datentyp `xsd:anyURI`. Ihre konkrete Ablehnungsursache lautet
`XTM-UNSUPPORTED/:resource-data-datatype`. Fünf Zeilen der bestehenden
XTM-Kontrollreports ändern sich dadurch gezielt; alle übrigen alten
Kontrollzeilen und alle Originalergebnisse bleiben erhalten.

Der erste vollständige Regressionsversuch fand dieselbe veraltete Erwartung im
CTM/XTM-Testadapter. Nur dessen Testeingabe, Label und erwarteter spezifischer
Fehlercode wurden korrigiert; kein CTM-Produktionscode wurde geändert.
[preliminary-execution.json](../reports/slice-21i/preliminary-execution.json)
und [preliminary-regression.log](../reports/slice-21i/preliminary-regression.log)
erhalten den abgebrochenen Versuch ausdrücklich als nicht abgenommen.

Von 48 übernommenen Nicht-XTM-Reports sind **46 strukturell identisch** zu
Slice 21H. Zwei Mergemap-Reports unterscheiden sich ausschließlich in den fünf
zugehörigen Prüfungslabels und der einen Unsupported-Condition. Der Validator
prüft diese konkrete Transformation gegen historische Eingaben, ohne
historische Reportdateien umzuschreiben. Alle Original-Case-Records und
Konformitätszahlen dieser Reports bleiben unverändert.

## Alle 124 Diagnosedifferenzen

Die Vorher-/Nachher-Diagnose führt alle 124 Originalquellen aus. Genau zwei
Beobachtungen ändern sich:

| Original | Vorherige Condition und Position | Tatsächliches Ergebnis danach |
| --- | --- | --- |
| `variant-resourceref.xtm` | `XTM-UNSUPPORTED/:unsupported-construct`, 9:61 | keine Condition, 621/621 Bytes identisch |
| `variant-resourceref-relative.xtm` | `XTM-UNSUPPORTED/:unsupported-construct`, 9:48 | keine Condition, 608/608 Bytes identisch |

Ursache ist ausschließlich die nun unterstützte Variant-ResourceRef-Alternative.
Die übrigen **122 vollständigen Beobachtungen bleiben identisch**.
Insbesondere bleibt `variant-resourcedata-uri.xtm` unverändert
`XTM-UNSUPPORTED/:resource-data-datatype`.
[diagnostic-changes.json](../reports/slice-21i/diagnostic-changes.json) enthält
beide vollständigen Beobachtungen und deren konkrete Begründung.
Die Diagnose bewirkt keine weiteren Konformitätsregistrierungen.

## Erfolgreiche vollständige Offline-Abnahme

Alle Testprozesse verwenden frisches **SBCL 2.5.4** ohne System- oder
Benutzerinitialisierung. Die vorhandenen gepinnten lokalen Abhängigkeiten und
bestehenden XML-Patches werden in temporären Verzeichnissen qualifiziert.
Quellvorbereitung und Tests laufen zusätzlich unter:

```text
(version 1)(allow default)(deny network*)(deny file-write* (subpath "/Users/rgb/workspace/topic-maps"))
```

Die reguläre `require_escalated`-Freigabe war erfolgreich. Es gibt keine
Änderung an `~/.nix-profile` oder der Sandbox-Konfiguration. Es gab keine neuen
Abhängigkeitsdownloads, keinen Zugriff auf langlebige Lisp-Images und keinen
vollständigen Nix-Neubau. Letzterer ist ausdrücklich NOT-RUN; die geforderte
frische Offline-SBCL-Regression wurde vollständig ausgeführt.

| Bereich | Bestandene Prüfungen |
| --- | ---: |
| Bisherige Lisp-Regression einschließlich TMDM, CTM/CXTM, Include und Mergemap | 12100 |
| XTM einschließlich aller bisherigen Originale und neuer ResourceRef-Verträge | 1557 |
| XML-Qualifikation | 146 |
| XTM-MERGEMAP | 217 |
| REGISTERED-ORIGINALS | 286 |
| REGISTERED-NEGATIVES | 25 |
| PROLOG | 171 |
| EMPTY2 | 13 |
| CTM-INTEGER | 112 |
| TRIPLE | 226 |
| ENCODING | 722 |
| Python-Unit-Tests | 2 |
| NFC-Oracle-Vergleiche | 16294 |
| Isolierte, erwartet scheiternde Fehlerpfadkontrollen | 45 |

Die 45 Fehlerpfadkontrollen enthalten die bisherigen 35 Kontrollen sowie für
jedes neue Original fünf weitere: Byteabweichung, XML-Fehler, Unsupported,
TMDM-Fehler und falsche XTM-Condition. Alle bewirken den erwarteten ASDF-Exit 1
und werden niemals als positiver PASS gewertet. Die übrigen Original-PASS vor
dem jeweiligen Ziel bleiben erhalten. Siehe
[failure-controls.json](../reports/slice-21i/failure-controls.json) und die
zugehörigen einzelnen Logs und Case-Record-Reports.

Tatsächlich registrierter Stand nach erfolgreicher Abnahme:

| Korpus | PASS | FAIL | NOT-RUN |
| --- | ---: | ---: | ---: |
| XTM | 59 | 0 | 65 |
| CTM | 262 | 4 | 7 |

Die XTM-NOT-RUN-Zahl umfasst 62 positive und drei negative unregistrierte
Originalverträge. Die vier bekannten CTM-FAILs bleiben `include-template.ctm`,
`include-wildcard2.ctm`, `occurrence-datetime-timezone2.ctm` und
`occurrence-datetime2.ctm`.

## Integrität und Reproduktion

Alle **2006 gepinnten Korpusdateien** entsprechen
weiterhin in Größe und SHA-256 `references/corpus-lock.json`.
Alle **2154 historischen Reportdateien** und
**4396 geschützten Dateien** des Ausgangscommits
bleiben byteidentisch. Die vollständigen Hashlisten und Ausführungsquellen
stehen in [integrity.json](../reports/slice-21i/integrity.json).

[execution.json](../reports/slice-21i/execution.json) protokolliert sämtliche
Befehle, UTC-Zeitpunkte, Sandboxregeln, erwarteten und tatsächlichen Exitcodes,
Konformitätsstände und Retargeting-Listen.
[precommit-audit.json](../reports/slice-21i/precommit-audit.json) prüft den
finalen Änderungsumfang; [artifacts.json](../reports/slice-21i/artifacts.json)
sichert alle neuen Dateien über Größe und SHA-256.

Reproduktion mit unbenutztem Ausgabeverzeichnis außerhalb des Repositorys:

```sh
python3 scripts/validate-slice-21i.py --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl --output /private/tmp/topic-maps-21i-recheck
```

Reader-Erweiterung, Tests, Dokumentation und geprüfte Ausführungsevidenz werden
zusammen lokal committet. Slice 21I endet damit.
