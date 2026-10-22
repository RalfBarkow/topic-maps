# Slice 22G — XTM 2.0 Occurrence-Kern

Die elf freigegebenen Originalverträge bestehen nach tatsächlicher Deserialisierung, nativen Modellprüfungen und vollständigem CXTM-Bytevergleich. Sie sind im vorhandenen Harness dauerhaft registriert. Der vollständige Offline-Lauf besteht mit **2.869 XTM-Checks**, davon 165 neu. Die bisherigen 72 Original-PASS bleiben erhalten; der registrierte Stand beträgt jetzt **83 PASS, 0 FAIL, 41 NOT-RUN** für XTM und unverändert **262 PASS, 4 FAIL, 7 NOT-RUN** für CTM.

Ausgangscommit ist `b50a9d7950c5407b2ec02e1caccd76f73018b45f`, dessen Parent `aeebbc7c6fdbf26642db0b7b5a358a3d04d62cca`. Zu Beginn waren Index und Arbeitsbaum auf `codex/ctm-xtm-slice-22f` sauber. Der Arbeitsbranch heißt `codex/xtm-slice-22g`. [initial-state.json](../reports/slice-22g/initial-state.json) sichert alle 8.465 versionierten Ausgangsdateien. Commit und sauberer Endzustand werden nach dem abschließenden Artefakt-/Indexaudit separat geliefert.

## Normative Grundlage und Verantwortlichkeiten

Die [öffentliche XTM-2.0-Fassung](https://www.isotopicmaps.org/sam/sam-xtm/) §§4.13–4.17 und 4.20 beschreibt Type-/Scope-Referenzen, Occurrence-Parent und Ressourcenwerte; §§4.3.3–4.3.4 bestimmen die IRI-Auflösung. [TMDM](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/) §§5.6 und 6.5 definiert Eigenschaften und Normalisierung; Gleichheit berücksichtigt Parent, Type, Scope, Value und Datatype.

Die öffentlichen Texte von XTM (19.06.2006) und TMDM (18.06.2006) erklären ihre Identität mit der Veröffentlichung. Es wurde keine zusätzliche ISO-Datei beschafft. Die Editionsgrenzen aus Slice 22C und dessen 13 historischen Entscheidungen bleiben unverändert. [Normative Einordnung](../reports/slice-22g/normative-review.json).

Vor Änderungen wurden die tatsächlichen Operationen und ihre Verträge gelesen. Die einzige Produktionsänderung liegt in [src/xtm/reader.lisp](../src/xtm/reader.lisp), mit insgesamt 48 hinzugefügten Zeilen:

- `validate-source` prüft Occurrence-Kontext, Attribute, Reihenfolge, genau einen Type, optional genau einen nichtleeren Scope und genau eine Ressourcenwertform. Die vorhandene Namespace-/Versions-, Referenz- und Ressourcenvalidierung wird wiederverwendet.
- `read-occurrence` löst Topics durch `find-reference-topic` auf, übernimmt Value/Datatype aus `read-resource-value` und übergibt alles an `add-occurrence`. Der Rückgabewert ist `canonical-occurrence`.
- `read-topic` ruft diese Operation für ein validiertes Occurrence-Kind auf.

`read-resource-value`, IRI-Auflösung, XML-Parser, TMDM und CXTM bleiben unverändert. TMDM übernimmt kanonische Parents/Types/Themes, Mengenbildung und Normalisierung. Es gibt kein zweites Occurrence-Modell und keinen Topic-Lookup anhand einer Datentyp-IRI. `resourceRef` und URI-Werte werden nicht als Aufforderung zu einem Ressourcenabruf behandelt.

## Originalverträge: tatsächlich gelesene Bytes und Ergebnisse

Die Originalquellen und Baselines wurden vor der Implementierung vollständig gelesen. [originals-before.json](../reports/slice-22g/originals-before.json) enthält Text, Hexbytes, Größen und SHA-256. [original-contracts.json](../reports/slice-22g/after/original-contracts.json) enthält die tatsächlichen Ausgaben, Modelle, Parsernachweise und Ergebnis-Hashes. Die elf tatsächlichen CXTM-Dateien liegen unter `reports/slice-22g/after/actual/`.

Jeder Primärimport verwendet `topic-maps.xtm:deserialize-octets` mit Originalbytes, genau einen qualifizierten Parseraufruf und einem zum ursprünglichen Octet-Vektor `EQ`en Parserargument. Document IRI ist jeweils `https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/<Dateiname>`. Der Source Key ist die Case-ID und kein Modell-Identifier. Ein zweiter wirklicher Import mit anderer Diagnosekennung muss dieselben nativen Eigenschaften und CXTM-Bytes liefern.

Für alle folgenden Fälle sind Condition und erste Byteabweichung null. Jeder ist nach bestandener Modellprüfung durch den vorhandenen `record-original-result` als PASS registriert.

| Datei unter `xtm2/in/` | Originalbytes | CXTM Ist/Soll | Occurrences im Endmodell |
|---|---:|---:|---:|
| `occurrence.xtm` | 265 | 371/371 | 1 |
| `occurrence-datatype-unknown.xtm` | 284 | 339/339 | 1 |
| `occurrence-duplicate.xtm` | 421 | 371/371 | 1 |
| `occurrence-scope.xtm` | 330 | 524/524 | 1 |
| `occurrence-scope-duplicate.xtm` | 366 | 524/524 | 1 |
| `occurrence-scope-duplicate-merged.xtm` | 611 | 547/547 | 1 |
| `occurrence-resourcedata-uri.xtm` | 347 | 381/381 | 1 |
| `occurrence-resourcedata-uri-relative.xtm` | 303 | 358/358 | 1 |
| `occurrence-resourceref.xtm` | 268 | 381/381 | 1 |
| `occurrence-resourceref-relative.xtm` | 245 | 358/358 | 1 |
| `merge-itemid-with-occurrences.xtm` | 541 | 586/586 | 2 |

Alle Originalmaps haben genau Owner- und Type-Topic; die Scope-Fälle zusätzlich ein Theme-Topic. Es gibt dort keine Names, Variants, Associations, Reifier oder Map-II. Jede Occurrence hat Parent `EQ #topic`, Type `EQ #occtype`, den erwarteten Scope, exakten Wert/Datentyp und keine eigenen II/Reifier. Datentypen erzeugen keine zusätzlichen Topics.

Der Standardwert lautet `Testing resource data.` mit `xsd:string`; der benutzerdefinierte Fall enthält `BOGUS` mit `http://example.com/bogus`. Absolute Ressourcenwerte sind `http://www.isotopicmaps.org/cxtm`, relative Werte lösen zu `photo.jpg` im Verzeichnis der expliziten Document IRI auf; Datentyp ist jeweils `xsd:anyURI`.

`merge-itemid-with-occurrences.xtm` hat weiterhin zwei Topics: Owner und Type. Am Owner bleiben beide dokumentlokalen II `#topic` und `#topic2` sowie `http://example.org/#topic` erhalten. Die beiden Werte `Some data` und `Some more data` bleiben zwei verschiedene Occurrences. Im Scope-Merging-Original bleiben sowohl `#english` als auch `#en` am gemeinsamen Theme erhalten.

## Native Normalisierung und gehaltene Handles

[tests/xtm-occurrences.lisp](../tests/xtm-occurrences.lisp) beobachtet reale Aufrufe des produktiven `read-occurrence`; die Beobachter geben dessen Ergebnis unverändert zurück und werden stets wiederhergestellt. Sie bauen keine Ersatzmap für Originalverträge auf. Der maschinenlesbare Bericht enthält den Occurrence-Bestand nach jedem gelesenen Element sowie kanonische Gruppen und Weiterleitungen sämtlicher gehaltener Rückgabehandles.

| Situation | Bestand nach den Reader-Aufrufen | Endbestand | Gehaltene Handles |
|---|---|---:|---|
| identische Occurrences am selben Parent | 1, 1 | 1 | zwei verschiedene Rückgabehandles; erster ersetzt, letzter aktuell; beide kanonisch gleich |
| zunächst unterschiedliche Scopes im Original | 1, 2 | 1 | beide alten Handles ersetzt; beide lösen zum selben Enditem auf |
| verschiedene Werte nach Parent-Merging im Original | 1, 2 | 2 | beide Handles bleiben aktuell und verschieden |
| neun zusätzliche späte Merging-Proben | jeweils 1, 2 | jeweils 1 | beide alten Handles ersetzt; beide lösen zum selben Enditem auf |

Die neun Proben kombinieren getrennt **Parent, Type und Scope** mit späterem **SI-, SL- oder II-Merging**. Die zunächst verschiedenen Topics werden erst nach dem Lesen beider Occurrences durch weitere wirkliche Topic-Definitionen zusammengeführt. Die Tests prüfen zwei tatsächlich verschiedene alte Occurrence-Handles, ihre nativen Weiterleitungen, die gemeinsamen kanonischen Topic-Referenzen und den endgültigen Bestand.

Eine weitere Gegenprobe variiert Parent, Type, Scope, Value und Datatype getrennt. Von sieben gelesenen Occurrences normalisiert nur das identische Paar; sechs verschiedene Items bleiben erhalten. Eine gemischte Map prüft erhaltene Names, Variants und die über `instanceOf` erzeugte Type–Instance-Association samt zwei Roles.

Alle 19 positiven Gegenproben prüfen kanonische native Referenzen sowie wiederholte CXTM-Kanonisierung mit unverändertem Modell und unveränderten aktuellen Handles. Die [Kontrollevidenz](../reports/slice-22g/after/native-and-negative-controls.json) enthält alle 46 zusätzlichen Kontrollen: 19 positive und 27 negative. Die vorherigen CTM/XTM-Äquivalenztests bleiben unverändert eingebunden.

## Negative Gegenproben und Unterstützungsgrenzen

Die Quellen der negativen Gegenproben werden tatsächlich durch den öffentlichen Reader verarbeitet. Die folgende Tabelle enthält die beobachteten Conditions; SAX-Positionen sind näherungsweise einsbasierte Zeile/Spalte. Native TMDM-Conditions besitzen keine SAX-Position; diese wird nicht erfunden.

| Gegenprobe | Condition / Code | Position |
|---|---|---|
| `missing-type` | `XTM-REJECTION / :missing-occurrence-type` | 1:103 |
| `missing-resource` | `XTM-REJECTION / :missing-occurrence-resource` | 1:89 |
| `two-resources` | `XTM-REJECTION / :occurrence-resource-cardinality` | 1:180 |
| `two-types` | `XTM-REJECTION / :duplicate-occurrence-type` | 1:129 |
| `empty-type` | `XTM-REJECTION / :type-cardinality` | 1:96 |
| `two-type-refs` | `XTM-REJECTION / :type-cardinality` | 1:95 |
| `bad-type-ref` | `XTM-REJECTION / :invalid-topic-ref` | 1:115 |
| `empty-scope` | `XTM-REJECTION / :empty-scope` | 1:131 |
| `bad-scope-ref` | `XTM-REJECTION / :invalid-topic-ref` | 1:154 |
| `two-scopes` | `XTM-REJECTION / :duplicate-occurrence-scope` | 1:166 |
| `wrong-order` | `XTM-REJECTION / :element-order` | 1:160 |
| `early-scope` | `XTM-REJECTION / :missing-occurrence-type` | 1:96 |
| `bad-child` | `XTM-REJECTION / :unexpected-element` | 1:97 |
| `foreign-namespace` | `XTM-REJECTION / :invalid-namespace` | 1:110 |
| `bad-attribute` | `XTM-REJECTION / :unexpected-attribute` | 1:100 |
| `text-child` | `XTM-REJECTION / :unexpected-text` | 1:89 |
| `relative-datatype` | `XTM-REJECTION / :invalid-resource-data-datatype` | 1:157 |
| `embedded-without-anyType` | `XTM-REJECTION / :unexpected-child` | 1:157 |
| `anyType-text` | `XTM-UNSUPPORTED / :resource-data-datatype` | 1:189 |
| `anyType-XML` | `XTM-UNSUPPORTED / :resource-data-datatype` | 1:189 |
| `item-identity` | `XTM-UNSUPPORTED / :unsupported-construct` | 1:117 |
| `reification` | `XTM-UNSUPPORTED / :unsupported-construct` | 1:102 |
| `invalid-parent-context` | `XTM-REJECTION / :unexpected-element` | 1:76 |
| `invalid-parent-context` | `XTM-REJECTION / :unexpected-element` | 1:112 |
| `real-XML-error` | `XTM-XML-ERROR / :xml-not-well-formed` | 1:11 |
| `occurrence-native-conflict` | `OCCURRENCE-ERROR / :invalid-integer-value` | keine native SAX-Position |
| `occurrence-native-conflict` | `OCCURRENCE-IDENTIFIER-ERROR / :duplicate-item-identifier` | keine native SAX-Position |

Die beiden nativen Fehler werden durch wirkliche Modelloperationen ausgelöst: ein ungültiger `xsd:integer`-Wert sowie die Kollision eines Map-II mit dem beim Type-Lookup benötigten Topic-II. Sie sind keine künstlich signalisierten Ersatzconditions. Der Reader erhält die nativen Condition-Klassen und Fehlercodes.

Occurrence-II und Occurrence-Reification bleiben gültige, noch nicht implementierte Fähigkeiten mit spezifischem Meldungstext und `XTM-UNSUPPORTED/:unsupported-construct`. `xsd:anyType` bleibt ein gültiger normativer Datentyp mit fehlender XML-Kanonisierung und wird weiterhin spezifisch als Unsupported abgelehnt. Fremdes XML unter gewöhnlichem textuellem `resourceData` ist dagegen ein Syntaxfehler. Explizite Associations/Roles, deren Reification, zyklische MergeMap-Semantik und Map-Item-Identität werden nicht erweitert.

`occurrence-duplicate-iid2.xtm` bleibt unregistriert und scheitert jetzt präzise am ausgeschlossenen Occurrence-II. Seine doppelte XML-ID und die dazu dokumentierte normative Qualifikationsfrage werden durch diesen Slice weder korrigiert noch entschieden. Auch `reifier-collision.xtm` bleibt mangels Occurrence-Reification offen; eine vorgelagerte Unsupported-Ablehnung zählt nicht als negativer Original-PASS.

## Bestehende Fehlerkontrollen und Diagnosedifferenzen

Vier bestehende Testquellen werden von einfachem Occurrence auf **Occurrence mit `reifier='#r'`** umgestellt. Das ursprüngliche Prüfziel bleibt die tatsächliche Unterscheidung von Unsupported, Syntax und nativen Konflikten. Alle bisherigen Checklabels und Assertionen bleiben erhalten. [retargetings.json](../reports/slice-22g/retargetings.json) enthält jede exakte alte/neue Quellzeile, Prüfzweck, erwartete und tatsächlich geprüfte Klasse/Code sowie Ausgangs-/Endhash des jeweiligen Testfiles.

| Datei | Bestehende Kontrolle | Neues tatsächlich geprüftes Ergebnis |
|---|---|---|
| `tests/xtm-identity.lisp` | `unsupported-occurrence` | `XTM-UNSUPPORTED/:unsupported-construct`, Occurrence-Reification |
| `tests/xtm-name-scopes.lisp` | `occurrence-stays-unsupported` | dieselbe Klasse/Code, mit erhaltenem Scope-Kontext |
| `tests/xtm-resource-datatypes.lisp` | `datatype:occurrence-remains-unsupported` | dieselbe Klasse/Code, mit erhaltenem benutzerdefiniertem Ressourcenwert |
| `tests/xtm-mergemap.lisp` | `occurrence-XML-still-unsupported` | dieselbe Klasse/Code als erhaltene Kindressourcen-Cause |

Bereits vorher auf Occurrence-Reification gerichtete Kontrollen ändern ihre Quelle nicht; ihr Meldungstext wird präzisiert. [retargeted-observations.json](../reports/slice-22g/after/retargeted-observations.json) bewahrt sämtliche tatsächlichen Vorher-/Nachher-Differenzen der bisherigen XTM-Berichte. Die CTM/XTM-Adapterquellen und der alte Executor-Treiber bleiben unverändert.

Der Vergleich aller **124 Originaldiagnosen** ergibt genau **17 Änderungen, 107 unveränderte Diagnosen**. Elf Änderungen sind die freigegebenen positiven Originale, deren Deserialisierung und Baselinevergleich jetzt bestehen. Die übrigen sechs sind ausschließlich die präzisierten Ausschlussgrenzen:

| Original | Vorher | Nachher |
|---|---|---|
| `xtm2/in/itemid-occurrence.xtm` | `unsupported-construct` bei 3:17 | `unsupported-construct` bei 4:45; XTM occurrence item identifiers are not implemented in this subset. |
| `xtm2/in/occurrence-duplicate-iid.xtm` | `unsupported-construct` bei 3:17 | `unsupported-construct` bei 4:45; XTM occurrence item identifiers are not implemented in this subset. |
| `xtm2/in/occurrence-duplicate-iid2.xtm` | `unsupported-construct` bei 3:17 | `unsupported-construct` bei 4:45; XTM occurrence item identifiers are not implemented in this subset. |
| `xtm2/in/occurrence-duplicate-reifier.xtm` | `unsupported-construct` bei 3:36 | `unsupported-construct` bei 3:36; XTM occurrence reification is not implemented in this subset. |
| `xtm2/in/occurrence-reifier.xtm` | `unsupported-construct` bei 3:36 | `unsupported-construct` bei 3:36; XTM occurrence reification is not implemented in this subset. |
| `xtm2/invalid/reifier-collision.xtm` | `unsupported-construct` bei 3:36 | `unsupported-construct` bei 3:36; XTM occurrence reification is not implemented in this subset. |

[diagnostic-changes.json](../reports/slice-22g/after/diagnostic-changes.json) enthält die vollständigen Originaldiagnosen beider Seiten mit Cause, Position und Ausgaben. Kein bisheriger Original-PASS verschlechtert sich. Andere historische Diagnosen bleiben unverändert.

Alle **113 vorhandenen Executor-Fehlerkontrollen** werden unverändert durch den bestehenden Treiber ausgeführt. Jeder Prozess liefert den erwarteten Exit 1; sämtliche bisherigen Case Records, Status und Outcomes bleiben gleich. Der Audit vergleicht auch die Anzahl der ausgeführten Checks. Kein Fault wird als PASS gewertet.

Ihre Berichte sind wegen der neuen Scope-Beschreibung, zweier leerer neuer Berichtsfelder und der dokumentierten Kontrollmeldungen nicht vollständig byteidentisch. Der Audit erlaubt ausschließlich diese konkret festgestellten Differenzpfade. Unverändert bleiben insbesondere die ursprünglichen Fehlerklassen/-codes und die Case-Outcomes aller 113 Fault-Prozesse. [failure-controls.json](../reports/slice-22g/after/failure-controls.json).

## Vollständige Offline-Regression

Die Abnahme beruht auf dem vollständigen Lauf vom **22.10.2026, 13:17:17 bis 13:20:51 UTC**. Es gibt 119 isolierte Prozesse: sechs reguläre Prozesse mit Exit 0 und 113 erwartete Fehlerprozesse mit Exit 1. SBCL 2.5.4 startet jeweils frisch ohne System-/Benutzerinitialisierung; Netzwerk und Schreibzugriffe auf Topic Maps/HyperDoc sind in den Testkindprozessen gesperrt. Die Abhängigkeiten stammen aus den vorhandenen lokalen Pins. Keine Downloads oder langlebigen Image-Loads.

| Teil | Tatsächliches Ergebnis |
|---|---:|
| TMDM / CTM / CXTM einschließlich Include / Mergemap | 12.100 Checks |
| XTM | 2.869 Checks, davon 165 neu; 75 positive und acht negative Original-PASS |
| CTM/XTM-Mergemap | 217 Checks |
| CTM/XTM-Äquivalenz | 487 Checks, 27 positive Reader-Paare |
| registrierte CTM-Originale positiv / negativ | 286 / 25 Checks |
| Prolog / empty2 / CTM-Integer / Triple / Encoding | 171 / 13 / 112 / 226 / 722 Checks |
| XML-Qualifikation | 146 PASS |
| Python / NFC-Oracle | zwei Tests / 16.294 Vergleiche |
| Executor-Fehlerkontrollen | 113; alle erwarteten Exit 1 |

Die Quellen, nativen Modelle und vollständigen CXTM-Ausgaben der 27 bisherigen Äquivalenzpaare sowie die drei absichtlichen Unterschiedsproben bleiben identisch. Die einzige Änderung im Äquivalenzbericht ist der präzisierte Meldungstext der weiterhin ausgeschlossenen Occurrence-Reification-Gegenprobe. [equivalence-preservation.json](../reports/slice-22g/after/equivalence-preservation.json). Alle weiteren 48 bisherigen Nicht-XTM-Berichte bleiben byteidentisch.

[execution.json](../reports/slice-22g/after/execution.json) enthält Abnahme, Gesamtzahlen und Prozesse; [runs.json](../reports/slice-22g/after/runs.json) enthält Kommandos, Zeitpunkte, Exitcodes, Sourcehashes und Log-/Rohberichtshashes. `--audit-only` prüft diese gespeicherte Ausführung und behauptet keinen erneuten Testlauf. Die zwei korrigierten testinternen Klammerfehler während der Entwicklung sind [separat dokumentiert](../reports/slice-22g/development-events.json) und wurden nicht als erfolgreiche Ausführung gezählt.

| Registrierter Korpus | PASS | FAIL | NOT-RUN |
|---|---:|---:|---:|
| XTM 2.0 | 83 | 0 | 41 |
| CTM | 262 | 4 | 7 |

Die vier bekannten CTM-FAILs bleiben `include-template.ctm`, `include-wildcard2.ctm`, `occurrence-datetime-timezone2.ctm` und `occurrence-datetime2.ctm`. Die fünf in der vorherigen read-only Untersuchung beobachteten MergeMap-Erfolge werden hier nicht zusätzlich registriert.

## Integrität und Reproduktion

[Integritätsaudit](../reports/slice-22g/after/integrity.json): Alle **2.006 gepinnten Korpusdateien** stimmen in Größe und SHA-256 mit dem Corpus Lock überein. Alle **6.178 historischen Reportdateien** sowie insgesamt **8.459 geschützte Ausgangsdateien** bleiben unverändert. TMDM, CTM, CXTM, XML, Originalquellen, Baselines und Corpus Lock sind unverändert. Keine HyperDoc-Integration oder andere Workspace-Arbeit, kein Push oder Deployment.

Das [Abschlussaudit](../reports/slice-22g/final-audit.json) prüft zusätzlich Artefaktumfang und SHA-256 aller neuen Berichte, Quellen und tatsächlichen Ausgaben. Die ASDF-Integration verwendet weiterhin `topic-maps/xtm/tests` und ruft die neue Originalregistrierung und die Gegenproben tatsächlich auf. Die elf Originale werden erst nach den bisherigen 72 Verträgen ergänzt; alte Stufenzähler und Fehlerkontroll-Präfixe bleiben überprüfbar.

Reproduktion mit einem neuen Ausgabeordner außerhalb des Repositories:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate-slice-22g.py --output /private/tmp/topic-maps-22g-reproduction
```

Für einen vorhandenen vollständigen Ausgabeordner prüft `--audit-only` dessen Integrität, ohne Tests erneut zu starten. Slice 22G endet mit dem lokalen Commit von Reader, dauerhaften Tests und dieser Evidenz.
