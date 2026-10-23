# Slice 22L — XTM 2.0 Occurrence-Reification

Ausgangscommit und vorgesehener Commit-Parent:
`c02207856f1927302ea064bc901e07183242f2da`.
Branch: `codex/xtm-slice-22l`, aus dem sauberen Branch `codex/xtm-slice-22k`.
Der ursprüngliche Parent ist `cc1a0e02803a5705c97fb5457f6e93ad22f8b347`.
Der gespeicherte Ausgangsharness zählt XTM **107 PASS, 0 FAIL, 17 NOT-RUN** und
CTM **262 PASS, 4 FAIL, 7 NOT-RUN**. Der Ausgangsindex war leer.
[initial-state.json](../reports/slice-22l/initial-state.json) enthält die SHA-256
aller 9705 verfolgten Ausgangsdateien.

## Normativer Vertrag und Editionsgrenze

**Normativ abgeleitet:** [XTM 2.0 §§4.3.2, 4.3.4, 4.5 und 4.15](https://www.isotopicmaps.org/sam/sam-xtm/)
verlangt die Auflösung der Reifier-IRI gegen die Document IRI, die Suche nach
einem Topic mit entsprechendem Item Identifier und bei Fehlen dessen Erzeugung.
Das Topic reifiziert die durch das Element dargestellte Occurrence. Der Locator
ist kein Item Identifier dieser Occurrence. Die Lookup-Regel ist II-basiert;
sie entspricht nicht dem SI-/II-Suchpfad für `topicRef`.

**Normativ abgeleitet:** [TMDM 2006 §§5.1, 5.3.4–5.3.5, 5.6, 6.2 und 6.5](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/)
verknüpft Occurrence und Reifier invers. Gleiche Occurrences werden anhand ihrer
fachlichen Eigenschaften vereinigt; vorhandene Item Identifier bleiben erhalten
und ihre Reifier-Topics werden erforderlichenfalls zusammengeführt. Ein Topic
darf nicht zwei verschiedene Items reifizieren. Gleiche Item Identifier auf
verschiedenen Items bleiben ein Konflikt.

**Geprüfte Editionsgrenze:** Die [korrigierte Onlinefassung von 2008](https://www.isotopicmaps.org/sam/sam-model/)
und die [publizierten Errata](https://www.isotopicmaps.org/sam/errata.html) wurden
abgeglichen. Die dort benannten Korrekturen betreffen Default-Name-Type (§7.5)
und die Variant-Vereinigung beim Name-Merge (§6.3). Für den hier verwendeten
Reification-Vertrag wurde keine relevante neue Anforderung festgestellt.
Es erfolgt keine TMDM-Änderung und keine stillschweigende Übernahme einer anderen
Modellfassung.

## Tatsächlich vor der Reader-Änderung ausgeführtes Modell-Gate

[api-preflight.lisp](../reports/slice-22l/api-preflight.lisp) führt ausschließlich
native Modellprüfungen aus. Der frische SBCL-2.5.4-Prozess hat weder Reader
aufgerufen noch Originalverträge registriert. Netzwerk und Repository-Schreiben
waren gesperrt. Reader- und TMDM-Hashes wurden vor und nach der Ausführung geprüft;
zu diesem Zeitpunkt war der Produktionsdiff leer.
[native-before-execution.json](../reports/slice-22l/native-before-execution.json)
sichert Ablauf und Hashes; [Report](../reports/slice-22l/native-before/report.json)
und [Log](../reports/slice-22l/native-before/run.log) enthalten das Ergebnis.

**Beobachtet:** Alle neun Checks bestanden: inverse Einzelzuweisung; Vereinigung
gleicher Occurrences nach Parent-Merging mit einem beziehungsweise zwei Reifiern;
II-Vereinigung; auflösbare alte Handles; Zusammenführung beider Reifier-Topics;
atomare Ablehnung einer konfliktbehafteten Zuweisung, eines späteren Reifier-Topic-
Merges, einer Kollision zwischen Occurrence-II und Reifier-Topic-II sowie der
Map-/Occurrence-Kollision des negativen Originals. Sechs strukturierte
Beobachtungen werden im regulären ASDF-Lauf unverändert wiederholt.

## Minimale produktive Änderung

Nur `src/xtm/reader.lisp` ändert Produktionsverhalten:

- `validate-source` prüft die Reifier-IRI weiterhin, verwirft aber das gültige
  Occurrence-Attribut nicht länger als Unsupported.
- `read-occurrence` verwendet nach `add-occurrence` und `read-item-identities`
  den vorhandenen `read-item-reifier` und liefert `canonical-occurrence` zurück.

`read-item-reifier` verwendet den vorhandenen II-Lookup, `intern-topic` und
`set-item-reifier`. Ein II-Miss kann anschließend durch bestehendes TMDM-
Cross-Merging mit einem SI-Topic vereinigt werden; diese Folge ersetzt den
II-Lookup nicht. Eine Gegenprobe verlangt dabei den zusätzlichen Topic-II,
der bei einem fälschlich vorgezogenen SI-Treffer fehlen würde. Es werden keine
SI oder SL aus der Reifier-IRI erfunden. Modellrepräsentation, Fehlerbedingungen,
Normalisierung und Handle-Verwaltung bleiben im TMDM.

## Drei Originalverträge

Die unveränderten Bytes, Texte, SHA-256 und Baselines sind in
[originals-before.json](../reports/slice-22l/originals-before.json) gesichert.
Die erneuten tatsächlichen Ergebnisse stehen in
[original-contracts.json](../reports/slice-22l/after/original-contracts.json).

| Original unter `xtm2/` | Quellbytes | Actual/Baseline | Ergebnis |
|---|---:|---:|---|
| `in/occurrence-reifier.xtm` | 284 | 476/476 | PASS |
| `in/occurrence-duplicate-reifier.xtm` | 459 | 476/476 | PASS |
| `invalid/reifier-collision.xtm` | 353 | negativer Vertrag | PASS, vorgesehener nativer Konflikt |

Beide positiven Maps haben genau drei Topics mit den lokalen II `#topic`,
`#occtype`, `#reifier` und eine Occurrence: Parent `#topic`, Type `#occtype`,
Value `Testing resource data.`, Datatype `xsd:string`, leerer Scope, keine eigenen
Occurrence-II. Reifier und inverse `reified`-Referenz sind kanonisch `EQ`.
Das zweite Original enthält zwei gleiche Occurrences und normalisiert sie auf
eine; ein ersetztes Occurrence-Handle bleibt auflösbar. Die vollständigen
[erzeugten CXTM-Dateien](../reports/slice-22l/after/actual/) sind byteidentisch;
die erste abweichende Byteposition ist jeweils `null`.
Beide Baselines haben SHA-256
`3e948871c0c2729e2b1171acaa3a7efdc25564d81b3f2d82806b4dabac4ce34e`.

Die Originale gehen über `deserialize-octets` und den qualifizierten XML-Parser,
mit identischen Original-Octets und genau einem Parseraufruf je positiver
Deserialisierung. Document IRI ist
`https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/`
plus vollständiger Case-ID. Source Key ist getrennt die Case-ID; ein zweiter
Reader-Aufruf mit anderem Key liefert gleiche native Eigenschaften und Bytes.
Wiederholte Kanonisierung erhält den vollständigen Modellzustand und Handles.

**Beobachteter negativer Originalfall:** Die Root-Map trägt `reifier="#reifier"`;
eine enthaltene Occurrence fordert denselben Topic als Reifier. Es kollidieren
somit **Topic-Map-Item und Occurrence**, keine Association oder Role.
Die tatsächliche native Zuweisung löst `REIFICATION-ERROR`, Code
`:reifier-conflict`, Detail `Topic already reifies a different information item.`
aus. Der beobachtete Zuweisungsframe nennt `OCCURRENCE` und zuvor `TOPIC-MAP`.
Der Modellzustand vor und nach dieser fehlgeschlagenen nativen Zuweisung ist
gleich. Das behauptet keine allgemeine transaktionale Deserialisierung.

Die native Condition besitzt keine Source-, Document-IRI-, Positions- oder
Cause-Slots. Die entsprechenden Reportwerte bleiben `null`; XML-Quelle,
Document IRI und Source Key stehen separat im Beobachtungsdatensatz. Es wird
keine Fehlerposition erfunden. Der vorhandene Harness nennt seinen generischen
negativen Outcome historisch `ctm-rejection`; hier qualifiziert der gemeinsame
Negativprüfer ausdrücklich die originale native Reification-Condition.
Kein vorgelagerter Unsupported-Fehler wird als PASS gezählt.

## Dauerhafte Gegenproben und Beobachtungsgrenzen

Die beiden neuen Testdateien sind serielle Komponenten des vorhandenen
`topic-maps/xtm/tests` und werden von dessen `run-tests` wirklich ausgeführt.
Die Originale ergänzen bestehende Case Records genau einmal und erst nach
Modellprüfung und Originalvergleich. Alle bisherigen 107 PASS-Records bleiben
inhaltlich unverändert.

Vierzehn positive Reader-Proben prüfen unbekannte, vorher oder später definierte
Reifier, II-Treffer und SI-Cross-Merging nach II-Miss, URN sowie relative
prozentkodierte Unicode-IRIs, getrennte Occurrence-II, gleiche Occurrences mit
verschiedenen Reifiern, beide Reihenfolgen reifizierter/unreifizierter Duplikate,
`resourceRef` und spätes SI-/SL-/II-Merging von Parent, Type, Scope und Reifier.
Native Referenzen und Inversen sind `EQ`; alte Handles bleiben gültig.

Achtzehn negative Proben unterscheiden Syntax-, XML-, native Modellfehler und
weiterhin Unsupported. Die nachstehende Tabelle stammt aus dem tatsächlich
ausgeführten Report; XTM-Positionen sind approximative SAX-Zeile/Spalte.
Native Conditions besitzen hier keine solche Position.

| Gegenprobe | Condition | Code | Position |
|---|---|---|---|
| `bad-percent` | `XTM-REJECTION` | `invalid-percent-escape` | 1:103 |
| `bad-percent-UTF8` | `XTM-REJECTION` | `invalid-percent-utf8` | 1:106 |
| `bad-IRI` | `XTM-REJECTION` | `invalid-iri` | 1:105 |
| `extra-attribute` | `XTM-REJECTION` | `unexpected-attribute` | 1:112 |
| `reifier-on-type` | `XTM-REJECTION` | `unexpected-attribute` | 1:108 |
| `reifier-on-Topic` | `XTM-REJECTION` | `unexpected-attribute` | 1:91 |
| `reifier-on-scope` | `XTM-REJECTION` | `unexpected-attribute` | 1:143 |
| `malformed-XML` | `XTM-XML-ERROR` | `xml-not-well-formed` | 1:110 |
| `two-different-Occurrences-same-Reifier` | `REIFICATION-ERROR` | `reifier-conflict` | keine nativen Slots |
| `Name-and-Occurrence-same-Reifier` | `REIFICATION-ERROR` | `reifier-conflict` | keine nativen Slots |
| `Map-and-Occurrence-same-Reifier` | `REIFICATION-ERROR` | `reifier-conflict` | keine nativen Slots |
| `late-conflicting-Reifier-merge-subjectIdentifier` | `REIFICATION-ERROR` | `reifier-conflict` | keine nativen Slots |
| `late-conflicting-Reifier-merge-subjectLocator` | `REIFICATION-ERROR` | `reifier-conflict` | keine nativen Slots |
| `late-conflicting-Reifier-merge-itemIdentity` | `REIFICATION-ERROR` | `reifier-conflict` | keine nativen Slots |
| `Occurrence-own-II-cannot-be-Reifier-Topic-II` | `OCCURRENCE-IDENTIFIER-ERROR` | `duplicate-item-identifier` | keine nativen Slots |
| `anyType-remains-Unsupported` | `XTM-UNSUPPORTED` | `resource-data-datatype` | 1:202 |
| `Association-Reification-remains-Unsupported` | `XTM-UNSUPPORTED` | `unsupported-construct` | 1:89 |
| `Role-Reification-remains-Unsupported` | `XTM-UNSUPPORTED` | `unsupported-construct` | 1:129 |

Eine zusätzliche Importprobe durchläuft den bestehenden XTM-`mergeMap`-Pfad mit
reifizierter Occurrence, II und Scope. Sie prüft Parent-Merging, inverse
Beziehungen, kanonische Referenzen und den unveränderten Quellmap-Zustand.
Die 33 neuen Kontrolldatensätze enthalten somit 14 positive, 18 negative und
eine Importbeobachtung. Quellen, native Eigenschaften und Conditions stehen in
`after/xtm.json`, Feld `occurrenceReifierControls`; der Importpfad zusätzlich in
`mergemapControls`.

Die vorhandene sprachübergreifende Probe `occurrence-scope-reifier` wird von
einer dokumentierten Fähigkeitslücke zu einem tatsächlich deserialisierten
Vergleichspaar: vier Topics, eine Integer-Occurrence mit Scope und Reifier,
übereinstimmende native Eigenschaften, kanonisches EQ innerhalb jeder Map und
**588/588 CXTM-Bytes**. Es wird kein EQ zwischen unabhängigen Maps verlangt.
Alle bisherigen 28 Paare und drei Kontraste bleiben unverändert. Insgesamt
bestehen 29 Paare und 515 Checks; die Association-/Role-Reification-Lücke bleibt
sichtbar. Das zusätzliche Paar erhöht keine Original-PASS-Zahl.

## Erhaltene Unsupported- und Executor-Kontrollen

[retargetings.json](../reports/slice-22l/retargetings.json) dokumentiert elf
angepasste Eingaben einschließlich ursprünglichem Zweck, alter und neuer Quelle
sowie erwartetem Code. Occurrence-Reification ist nun gültig; die Quellen
verwenden deshalb das normativ gültige, weiterhin nicht implementierte
`xsd:anyType`. Reifier, II und Scope bleiben gegebenenfalls erhalten.
`XTM-UNSUPPORTED` bleibt die Klasse, der Code wechselt gezielt von
`unsupported-construct` zu `resource-data-datatype`. Positive Kontrollen für
beliebige absolute Datentypen bleiben erhalten.

Acht strukturierte XTM-Kontrollzeilen ändern sich entsprechend; zwei ältere
Identity-Kontrollen sind durch ihre tatsächlich ausgeführten Checklabels
belegt. Die elfte ist der CTM/XTM-Mergemap-Adapter: äußerer
`MERGEMAP-SOURCE-UNSUPPORTED`, originale `XTM-UNSUPPORTED`-Cause, Resource-IRI,
Source Key und XML-Position bleiben geprüft. Sein gespeicherter Report ändert
ausschließlich den erwarteten Code. Die realen Unterschiede stehen in
[retargeted-control-observations.json](../reports/slice-22l/after/retargeted-control-observations.json)
und [adapter-retargeting.json](../reports/slice-22l/after/adapter-retargeting.json).

Der erste vollständige Versuch scheiterte an genau dieser zusätzlichen,
zunächst übersehenen Adapterquelle. Er ist als **nicht abgenommen** mit Log in
[attempts/](../reports/slice-22l/attempts/) erhalten. Die anschließende Änderung
betrifft ausschließlich die Testquelle und erwartete Diagnose. Danach wurde
die vollständige Regression neu ausgeführt. Kein fehlgeschlagener Versuch
zählt als erfolgreiche Abnahme.

Alle **113** bestehenden Executor-Fehlerkontrollen verwenden denselben
unveränderten Treiber. Jede wird separat ausgeführt und muss den vorgesehenen
ASDF-Fehlerausgang erreichen. Ihre bisherigen Case Records, Outcomes, Status
und Checklabels bleiben gleich; sie werden nicht als erfolgreiche
Originalverträge gezählt. Die neuen Originaltests werden durch diese alten
Fehlerinjektionen nicht irrtümlich als PASS ausgegeben.

## Umfangsgrenze

Association-/Role-Reification, `xsd:anyType`, zyklische `mergeMap`-Semantik,
Map-II-Übertragung und XML-ID-Soundness bleiben unverändert außerhalb dieses
Slices. Keine Produktionsänderungen an TMDM, CTM, CXTM oder XML; keine Downloads,
HyperDoc-Änderungen, langlebigen Image-Loads, Pushes oder Deployments.

## Vollständige Offline-Abnahme und Integrität

**Beobachtet und auditiert:** Der frische SBCL-2.5.4-Lauf mit
`--no-sysinit --no-userinit`, ausschließlich lokalen gepinnten Abhängigkeiten,
Netzwerksperre sowie gesperrten Schreibzugriffen auf Repository und HyperDoc ist
vollständig bestanden. Die 119 Prozesse des vollständigen Sammlers erreichen
jeweils ihren erwarteten Exitcode. Mit dem vorangegangenen nativen Gate sind
120 frische Prozesse belegt; darunter sind auch Hilfsprozesse zur lokalen
Vorbereitung und Python-Prüfung. Befehle, Laufzeiten, Exitcodes und Loghashes
stehen in [runs.json](../reports/slice-22l/after/runs.json) und
[execution.json](../reports/slice-22l/after/execution.json).

| Prüfung | Tatsächliches Ergebnis |
|---|---:|
| Standalone-XTM | 3447 Checks, bisherige 3339 erhalten |
| Native Occurrence-Reification vor Reader-Änderung | 9 Checks |
| TMDM-/CTM-/CXTM-Kern | 12100 Checks |
| XML-Qualifikation | 146 PASS, 0 FAIL |
| CTM/XTM-Mergemap-Integration | 217 Checks |
| CTM/XTM-Äquivalenz | 515 Checks, 29 Paare, 3 Kontraste, 1 verbleibende Lücke |
| Registrierte Slice-20A-Originale | 286 Checks |
| Slice-20B-Negativfälle | 25 Checks |
| Slice-20C-Prolog | 171 Checks |
| Slice-20E-empty2 | 13 Checks |
| Slice-20F-Integer | 112 Checks |
| Slice-20G-Triple-Strings | 226 Checks |
| Slice-20H-Encoding | 722 Checks |
| Executor-Fehlerkontrollen | alle 113, erwarteter Fehlerausgang |
| Python | 2 Tests |
| NFC-Oracle | 16294 Vergleiche |

Alle weiteren bisherigen XTM-Names-, Scopes-, Variants-, II-, Association-/Role-,
Reification- und Mergemap-Prüfungen laufen im regulären ASDF-Testsystem.
47 Nicht-XTM-Reports bleiben byteidentisch. Die zwei weiteren Reports enthalten
exakt die dokumentierte Adapter-Codeänderung beziehungsweise die neue tatsächliche
Äquivalenzprobe. Neue Featurefelder in alten Fault-Reports sind leer; deren
Kontrolländerungen beschränken sich auf die qualifizierten Retargetings.

| Registrierter Korpus | Vorher PASS/FAIL/NOT-RUN | Nachher PASS/FAIL/NOT-RUN |
|---|---:|---:|
| XTM 2.0 | 107/0/17 | **110/0/14** |
| CTM | 262/4/7 | **262/4/7** |

[all-124-original-statuses.json](../reports/slice-22l/after/all-124-original-statuses.json)
enthält jede alte/neue Registrierung und tatsächliche Diagnose.
[diagnostic-changes.json](../reports/slice-22l/after/diagnostic-changes.json)
belegt genau drei Änderungen und 121 unveränderte Diagnosen. Keine bisherige
PASS-Registrierung geht verloren. Der zyklische Mergemap-Vertrag, die Map-II-
Baselinefrage und alle anderen offenen Verträge werden nicht hochgestuft.

Die vier bekannten CTM-FAILs bleiben sichtbar:
`include-template.ctm`, `include-wildcard2.ctm`,
`occurrence-datetime-timezone2.ctm`, `occurrence-datetime2.ctm`.

[integrity.json](../reports/slice-22l/after/integrity.json) prüft Größe und SHA-256
aller **2006 gepinnten Korpusdateien**, einschließlich Originalquellen und
Baselines. Außerdem bleiben sämtliche **7406 historischen Reportdateien** und
alle geschützten Ausgangsdateien hashidentisch. Corpus Lock und alte Berichte
werden nicht verändert. Die einzige geänderte Produktionsdatei ist der
XTM-Reader. TMDM, CTM, CXTM und XML bleiben byteidentisch zum Ausgangscommit.

Der neue Validator verwendet den unveränderten Offline-Sammler aus Slice 22D.
Reproduktion in ein neues Ausgabeverzeichnis außerhalb des Repositorys:

```sh
python3 scripts/validate-slice-22l.py --output /private/tmp/topic-maps-22l-new
python3 scripts/validate-slice-22l.py --audit-only --output /private/tmp/topic-maps-22l-new
```

Das gespeicherte native Vorab-Gate ist historische Ausführungsevidenz vor der
Reader-Änderung; seine identischen Prüfungen werden bei der Reproduktion im
ASDF-Lauf wiederholt. Der Validator prüft Gate-Hashes, Produktionsausgang und
Reihenfolge der ursprünglichen Ausführung. Er behauptet nicht, ein neuer Lauf
mit dem fertigen Reader sei selbst vor dessen Änderung erfolgt.

[completion-audit.json](../reports/slice-22l/completion-audit.json) bindet die
abgenommenen Quellen, Dokumentation und sämtliche neuen Evidenzdateien über
SHA-256 an den lokalen Commit-Inhalt. Der Bericht nennt den Parent; die finale
Commit-ID wird nach Erstellung separat ausgegeben.
