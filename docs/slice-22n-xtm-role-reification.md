# Slice 22N — XTM 2.0 Role-Reification

Ausgangscommit und Commit-Parent:
`acc9eb65b0cce71409ad84841f082f5ca125c839`.
Ausgangsbranch `codex/xtm-slice-22m`, eigener Arbeitsbranch
`codex/xtm-slice-22n`. Beim Beginn waren Index und Arbeitsbaum sauber.
Slice 22M bleibt unverändert in der Historie. Der gespeicherte Ausgangsstand
ist XTM **115 PASS, 0 FAIL, 9 NOT-RUN**, CTM **262 PASS, 4 FAIL, 7 NOT-RUN**.
[initial-state.json](../reports/slice-22n/initial-state.json) enthält SHA-256
aller 10333 verfolgten Ausgangsdateien.

Vor Beginn benannter Umfang: ein natives TMDM-Gate; sechs unveränderte
Originale; anschließend ausschließlich XTM-Reader-Integration, bestehende
ASDF-Tests und Fehlerkontrollen, neue Dokumentation und Ausführungsevidenz.
Keine TMDM-, CTM-, CXTM-, XML- oder HyperDoc-Implementierung.

## Normativer Vertrag und Editionsgrenze

**Normativ abgeleitet:** [XTM 2.0 §§4.3.2, 4.6, 4.18–4.20](https://www.isotopicmaps.org/sam/sam-xtm/)
ordnet Role, Type, Player und eigenen II dem dargestellten Role-Item zu.
`reifier` bezeichnet dessen Topic über einen II-Locator. Die bestehende
IRI-Verarbeitung (§4.3.4) dekodiert Prozent-UTF-8 und löst relativ zur Document
IRI auf. II-Lookup beziehungsweise Topic-Erzeugung ist vom SI-/II-Lookup für
`topicRef` getrennt. Der Reifier-Locator wird kein Role- oder Association-II.

**Normativ abgeleitet:** [TMDM 2006 §§5.3.4–5.3.5, 5.8, 6.2 und 6.6–6.7](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/)
verlangt inverse Reification und Role-Gleichheit anhand Type, Player **und
Parent**. Bei gleichen zusammengeführten Roles werden II vereinigt und
gegebenenfalls ihre Reifier-Topics zusammengeführt. Association-Gleichheit
bleibt von Type, Scope und Role-Menge abhängig. Gemeinsame Reifier machen
verschiedene Parents oder Roles nicht fachlich gleich.

Die bisherigen Editionsgrenzen gelten fort. Die
[publizierten TMDM-Errata](https://www.isotopicmaps.org/sam/errata.html) benennen
Korrekturen zum Default-Name-Type und zum Name-/Variant-Merge; für die hier
verwendete Role-Reification ergibt sich daraus keine zusätzliche Anforderung.
Die [korrigierte Fassung von 2008](https://www.isotopicmaps.org/sam/sam-model/)
wird nicht stillschweigend zur neuen Modellbasis. Der CXTM-Vergleich verwendet
die bestehende Implementierung für ISO/IEC 13250-4:2009; offene Editionsfragen
aus Slice 22C werden nicht neu entschieden.

## Native-Gate vor der Reader-Änderung

**Beobachtet:** Der frische SBCL-2.5.4-Prozess führte **15 native Checks** aus,
ohne Reader-Aufruf oder neue Originalregistrierung. Verwendet wurden öffentliche
TMDM-Konstruktoren, Identifier-, Merge-, Reifier- und kanonische Handle-APIs.
Die vorhandenen Testbeobachter lesen deren echte Modellzustände.

Nachgewiesen sind Einzelzuweisung und Inverse, idempotenter gleicher Reifier,
Topic-Merging zweier Reifier derselben Role, normale Role-Duplikate sowie
SI-/SL-/II-Merging bei gleichen und verschiedenen Parent-Associations.
Association-/Role-II, Association-Reifier, inverse `rolesPlayed` und alte
Role-/Association-/Topic-Handles bleiben erhalten. Fünf atomare Reifier-
Konflikte und eine atomare Role-II-/Topic-II-Kollision werden zurückgewiesen.
Insbesondere bleiben verschiedene Parent-Associations bei gleichem Role Type
und Player verschieden.

[Native-Runner](../reports/slice-22n/api-preflight.lisp),
[15 Checklabels im Log](../reports/slice-22n/native-before/run.log),
[13 strukturierte Beobachtungen](../reports/slice-22n/native-before/report.json)
und [Ausführung mit Quellhashes](../reports/slice-22n/native-before-execution.json)
sind gesichert. Netzwerk und Repository-Schreibzugriff waren gesperrt;
`--no-sysinit --no-userinit` war gesetzt. Der Reader-Hash entspricht dem
Ausgangscommit; vor und nach dem Gate war der Produktionsdiff leer. Die
identischen nativen Tests werden im regulären ASDF-Lauf wiederholt.
Die lokale gepinnte Abhängigkeitsvorbereitung ist separat gesichert.

Vorbereitende Dateilisten-/Runnerprobleme und eine später korrigierte falsche
Condition-Untertyp-Erwartung sind unter [attempts/](../reports/slice-22n/attempts/)
dokumentiert. Sie zählen nicht als erfolgreiche Ausführung oder als Modellfehler.

## Minimale Reader-Integration

Die einzige geänderte Produktionsdatei ist `src/xtm/reader.lisp`:

1. `validate-source` akzeptiert Role-Reification und prüft weiterhin deren IRI.
2. `read-association` erzeugt und normalisiert die vollständige Association
   mit den vorhandenen TMDM-Operationen und weist Association-II zu.
3. Vor **jeder** XML-Role-Zuordnung wird der aktuelle Association-Handle aufgelöst.
4. Die XML-Role wird innerhalb dieses Parents anhand kanonischer Type-/Player-
   Referenzen gefunden. XML-Reihenfolge und II definieren keine Gleichheit.
5. `read-item-identities` weist Role-II zu; erst danach wird
   `read-item-reifier` auf die kanonische Role angewandt.
6. Nach allen Role-Metadaten folgt wie bisher Association-Reification. Der
   Reader liefert die aktuelle kanonische Association zurück.

Diese Reihenfolge ist wesentlich: Ein früherer Role-Reifier-Merge kann Topics
vereinigen und dadurch die Signaturen späterer Quell-Roles verändern. Eine
spezifische tatsächliche Reader-Probe erzeugt vier Quell-Roles: zwei gleiche
Roles mit Reifiern r/u sowie zwei spätere Roles mit diesen Topics als Players.
Das erste Reifier-Merging lässt auch die späteren Roles zusammenfallen. Deren
II und zusätzliche Reifier werden trotzdem dem richtigen aktuellen Role-Item
zugewiesen. Die endgültige Map hat zwei Roles mit jeweils vereinigten II und
korrekten Inversen. Es gibt keine zweite Role- oder Reifier-Verwaltung.

## Sechs unveränderte Originalverträge

Quelltext, Hexbytes, SHA-256 und Baselines wurden vor Implementierung gelesen
und in [originals-before.json](../reports/slice-22n/originals-before.json)
gesichert. Die fünf positiven Originale haben jeweils Association Type
`#assoctype`, leeren Scope, keine eigenen Association-/Role-II und keine
Association-Reification. Alle haben die Role `#roletype`/`#topic`, reifiziert
durch `#reifier`. Die letzten beiden haben zusätzlich `#roletype2`/`#topic2`;
nur im letzten Original wird auch diese Role durch `#reifier2` reifiziert.
Keine Quelle benötigt eine zusätzliche ausgeschlossene Sprachfähigkeit.

| Original unter `xtm2/` | Quellbytes | Actual/Baseline | Ergebnis / Normalisierung |
|---|---:|---:|---|
| `in/role-reifier.xtm` | 304 | **612/612** | PASS; 1 Association / 1 Role / 4 Topics |
| `in/role-duplicate-reified.xtm` | 534 | **612/612** | PASS; 2 gleiche Associations werden 1 / 1 Role |
| `in/role-duplicate-reified2.xtm` | 442 | **612/612** | PASS; 2 gleiche Roles innerhalb 1 Parent werden 1 Role |
| `in/role-duplicate-reified3.xtm` | 776 | **936/936** | PASS; 2 gleiche binäre Associations werden 1 / 2 Roles / 6 Topics |
| `in/role-duplicate-reified4.xtm` | 816 | **1042/1042** | PASS; wie zuvor, beide Roles reifiziert / 7 Topics |
| `invalid/role-duplicate-reified.xtm` | 672 | negativer Vertrag | PASS; beabsichtigter nativer Parent-/Reifier-Konflikt |

Alle positiven Conditions und ersten abweichenden Bytepositionen sind `null`.
Jedes Original geht mit unveränderten Octets über `deserialize-octets` und
jeweils genau einen qualifizierten XML-Parseraufruf. Document IRI ist
`https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/`
plus vollständiger Case-ID. Source Key ist separat die Case-ID. Eine zweite
echte Deserialisierung mit anderem Source Key liefert identische native
Eigenschaften und CXTM-Bytes. Kanonisierung wird wiederholt und erhält den
vollständigen Modellzustand sowie alle beobachteten Handles.

Native Prüfungen erfassen Parent, Type, Player, Scope, Reifier, `reified`,
`rolesPlayed` und kanonisches `EQ` innerhalb der Map. Die Duplikatfälle halten
auch vor der Normalisierung beobachtete Role-Handles und lösen sie danach auf.
Keine Ersatzmap zählt als Originalvergleich.
[Originalergebnisse](../reports/slice-22n/after/original-contracts.json) und
[tatsächlich erzeugte CXTM-Dateien](../reports/slice-22n/after/actual/) enthalten
die vollständige Evidenz.

### Negativer Vertrag: Parent bleibt Teil der Role-Gleichheit

**Vor Implementierung beobachtete Quelle:** Die zwei Roles haben denselben
Type `#roletype1`, denselben Player `#player1` und denselben Reifier
`#reifier1`. Die Parent-Associations unterscheiden sich durch ihren Type
`#assoctype` beziehungsweise `#assoctype2`. Der Kommentar benennt ausdrücklich
die ungleichen Parents. Daher darf keine Association-/Role-Vereinigung allein
wegen des Reifiers erfolgen.

**Tatsächlich erreicht:** `REIFICATION-ERROR`, Code `reifier-conflict`, Detail
`Topic already reifies a different information item.`. Der echte native
Zuweisungsframe zeigt `ASSOCIATION-ROLE` gegen `ASSOCIATION-ROLE`, genau zwei
Associations und zwei Roles, gleiche Type-/Player-Referenzen und verschiedene
Parents. Die Parent-Type-II sind dokumentqualifiziert `#assoctype2` und
`#assoctype`. Die fehlgeschlagene native Zuweisung verändert den beobachteten
Modellzustand nicht. Dies behauptet keine allgemein transaktionale
Deserialisierung.

Die native Condition besitzt keine Source-/Document-IRI-/Positions-/Cause-Slots;
diese Reportfelder bleiben `null`. Originalquelle und logischer Quellenkontext
stehen separat. Der bestehende Harness nennt seinen generischen negativen
Outcome historisch `ctm-rejection`; der gemeinsame Negativprüfer verlangt hier
die exakte native Reification-Condition und den vorgesehenen Konflikt. Eine
vorgelagerte Unsupported-Zurückweisung genügt nicht für PASS.

## Gegenproben und Fehlerdiagnostik

Die neuen Dateien sind serielle Komponenten des bestehenden ASDF-Testsystems
`topic-maps/xtm/tests`; dessen `run-tests` ruft Gate, Originale und Gegenproben
wirklich auf. Alle bisherigen 115 Case Records bleiben unverändert; die sechs
neuen Originale werden genau einmal registriert.

**17 positive Reader-Proben:** unbekannte/vorher/später definierte Reifier;
II-, SI- und SL-Abgrenzung bei der Reifier-Auflösung; URN und relative
prozentkodierte Unicode-IRI; getrennte Association-/Role-/Reifier-II; gleiche
Roles innerhalb eines Parents und gleicher Associations mit gleichen oder
verschiedenen Reifiern; Association- und Role-Reification gemeinsam; vertauschte
Role-Reihenfolge und Duplikate; Reifier-bedingter Signaturkollaps späterer Roles;
spätes SI-/SL-/II-Merging von Type, Player und Scope mit beiden Reifier-Arten.

**22 negative Reader-Proben:** genaue Syntax-/XML-/TMDM-Conditions und
weiterhin Unsupported für `xsd:anyType`. Die Tabelle stammt aus dem tatsächlichen
Lauf. XTM-Zeile/Spalte ist approximative SAX-Position; native Conditions haben
keine solchen Slots.

| Gegenprobe | Condition | Code | Position |
|---|---|---|---|
| `bad-percent` | `XTM-REJECTION` | `invalid-percent-escape` | 1:130 |
| `bad-percent-UTF8` | `XTM-REJECTION` | `invalid-percent-utf8` | 1:133 |
| `bad-IRI` | `XTM-REJECTION` | `invalid-iri` | 1:132 |
| `extra-attribute` | `XTM-REJECTION` | `unexpected-attribute` | 1:139 |
| `reifier-on-type` | `XTM-REJECTION` | `unexpected-attribute` | 1:135 |
| `reifier-on-topicRef` | `XTM-REJECTION` | `unexpected-attribute` | 1:185 |
| `malformed-XML` | `XTM-XML-ERROR` | `xml-not-well-formed` | 1:143 |
| `missing-Type` | `XTM-REJECTION` | `missing-type` | 1:150 |
| `missing-Player` | `XTM-REJECTION` | `missing-role-player` | 1:129 |
| `multiple-Players` | `XTM-REJECTION` | `role-player-cardinality` | 1:206 |
| `different-Parents-same-Type-Player-and-Reifier` | `REIFICATION-ERROR` | `reifier-conflict` | keine nativen Slots |
| `different-Players-same-Reifier` | `REIFICATION-ERROR` | `reifier-conflict` | keine nativen Slots |
| `different-Role-Types-same-Reifier` | `REIFICATION-ERROR` | `reifier-conflict` | keine nativen Slots |
| `Role-and-Association-same-Reifier` | `REIFICATION-ERROR` | `reifier-conflict` | keine nativen Slots |
| `Occurrence-and-Role-same-Reifier` | `REIFICATION-ERROR` | `reifier-conflict` | keine nativen Slots |
| `Map-and-Role-same-Reifier` | `REIFICATION-ERROR` | `reifier-conflict` | keine nativen Slots |
| `late-Reifier-conflict-subjectIdentifier` | `REIFICATION-ERROR` | `reifier-conflict` | keine nativen Slots |
| `late-Reifier-conflict-subjectLocator` | `REIFICATION-ERROR` | `reifier-conflict` | keine nativen Slots |
| `late-Reifier-conflict-itemIdentity` | `REIFICATION-ERROR` | `reifier-conflict` | keine nativen Slots |
| `Role-II-not-Reifier-II` | `OCCURRENCE-IDENTIFIER-ERROR` | `duplicate-item-identifier` | keine nativen Slots |
| `Role-II-not-Association-II` | `ITEM-IDENTIFIER-ERROR` | `duplicate-item-identifier` | keine nativen Slots |
| `anyType-still-Unsupported` | `XTM-UNSUPPORTED` | `resource-data-datatype` | 1:336 |

Beim Role-II-/Topic-II-Konflikt bleibt der vorhandene historische
`OCCURRENCE-IDENTIFIER-ERROR`-Pfad erhalten. Role-II gegen Association-II
signalisiert dagegen den öffentlichen generischen `ITEM-IDENTIFIER-ERROR`.
Beide haben `duplicate-item-identifier`. Die zunächst falsche neue
Untertyp-Erwartung wurde ausschließlich im Test korrigiert; das Modell blieb
unverändert. Native Reifier-Zuweisungsfehler werden auf ihren atomaren Zustand
beobachtet; Parser-Causes und echte XTM-Quellenpositionen bleiben erhalten.

Eine weitere Gegenprobe importiert eine scoped Association mit Association-
und Role-Reification sowie beiden II-Arten über den bestehenden XTM-Mergemap-
Pfad. Player-Merging, kanonische Referenzen, beide Inversen und die unveränderte
Quellmap werden geprüft. Map-Metadaten werden nicht zusätzlich übernommen.
Damit gibt es 40 neue Kontrolldatensätze: 17 positive, 22 negative und eine
Importbeobachtung. Quellen, Modelle und Conditions stehen in `after/xtm.json`,
Felder `roleReifierControls` und `mergemapControls`.

## Retargeting ohne Verlust des ursprünglichen Prüfzwecks

[retargetings.json](../reports/slice-22n/retargetings.json) dokumentiert zehn
bisherige Role-Unsupported-Quellen mit alter/neuer Quelle, ursprünglichem Zweck
und exakten erwarteten Klassen/Codes. In diesen Role-Quellen bleibt keine
entsprechende Unsupported-Fähigkeit übrig. Deshalb wird gezielt ein fehlerhafter
Role-Reifier mit `%GG` geprüft: `XTM-REJECTION / invalid-percent-escape` ersetzt
`XTM-UNSUPPORTED / unsupported-construct`. Association-Reifier, Scope, II und
Quellenkontexte bleiben erhalten; die bestehenden Checklabels bleiben als
historische Provenienz bestehen. Gültige Role-Gegenstücke werden zusätzlich
produktiv gelesen. Keine alte Kontrolle wird ersatzlos gelöscht.

Die allgemeinen Unsupported-Prüfungen für weiterhin nicht implementiertes
`xsd:anyType` und fehlenden expliziten Resolver bleiben bestehen. Die zehn
Quellenänderungen sind nicht als unverändert erfolgreiche Unsupported-Prüfungen
ausgegeben. Neun strukturierte Kontrollzeilen und eine ältere Identity-Kontrolle
mit vier tatsächlich ausgeführten Checklabels belegen das Retargeting.
[retargeted-control-observations.json](../reports/slice-22n/after/retargeted-control-observations.json)
enthält alle beobachteten strukturierten Unterschiede.

Die 113 bestehenden Executor-Fehlerkontrollen behalten den unveränderten
Treiber, ihre bisherigen Target-Case-Records, Outcomes, Status und Checklabels.
Jede muss den vorgesehenen ASDF-Fehlerausgang erreichen; keine wird als neuer
positiver Originalvergleich gezählt. Neue Originale werden in alten
Fehlerinjektionsläufen nicht fälschlich als ausgeführt ausgegeben.

## Grenze des Slices

Unverändert offen bleiben `mergemap-itemid.xtm`, `mergemap-loop.xtm` und
`occurrence-duplicate-iid2.xtm`. Keine Implementierung von Map-II-Übertragung,
normativer Zyklussemantik, anderer XML-ID-Soundness, `xsd:anyType` oder XTM 2.1.
Keine Änderungen an TMDM, CTM, CXTM, XML oder HyperDoc; keine Downloads, Pushes,
Deployments, SSH-Zugriffe oder Änderungen langlebiger Lisp-Images.

## Tatsächliche CTM/XTM-Äquivalenz

Die bisherigen unveränderten Quellen der Probe
`association-role-scope-reifiers` werden jetzt beide durch die produktiven
Reader verarbeitet. Die gemeinsame Document IRI folgt der vorhandenen
positiven Paar-Konvention
`https://equivalence.example.invalid/association-role-scope-reifiers/map`;
Source Keys bleiben getrennt `ctm:...` und `xtm:...`. Es entstehen sechs Topics,
eine scoped Association, eine Role und zwei unabhängig reifizierte Items.
Parent, Type, Player, Scope, Association-/Role-Reifier und Inversen stimmen
nativ überein; kanonisches EQ wird jeweils innerhalb einer Map geprüft.

**Beobachtet:** vollständige CXTM-Bytegleichheit **840/840 Bytes**, erste
abweichende Position `null`, beide Conditions `null`. Die CTM-Ausgabe bleibt
auch zur früheren Hilfsbeobachtung bytegleich. Es findet keine nachträgliche
Modell- oder CXTM-Bereinigung statt. Wiederholte Kanonisierung bleibt rein.

Die zwei alten Gap-Checks werden durch die vollständige positive Paarprüfung
ersetzt. Alle vorherigen 29 tatsächlichen Paare und drei Kontraste bleiben
unverändert; die Suite hat jetzt **30 Paare, 529 Checks und keine der drei
früher dokumentierten Fähigkeitslücken mehr**. Dies behauptet keine allgemeine
Vollständigkeit der Reader und erzeugt keinen zusätzlichen Original-PASS.
[Die vollständige Gegenüberstellung](../reports/slice-22n/after/equivalence-progress.json)
sichert alte Probe, neue tatsächliche Modelle, beide Quellen und volle Bytes.

## Vollständige Offline-Regression und Integrität

**Beobachtet und auditiert:** Alle 119 Prozesse des vollständigen bestehenden
Sammlers erreichen ihren erwarteten Exitcode. Die Lisp-Prozesse starten frisch
mit SBCL 2.5.4, `--no-sysinit --no-userinit`, lokalen gepinnten Abhängigkeiten
und gesperrtem Netzwerk. Repository- und HyperDoc-Schreibzugriffe sind für die
Testprozesse gesperrt. Einschließlich des vorangegangenen erfolgreichen nativen
Gate-Prozesses sind 120 erfolgreiche Ausführungen belegt; darin enthalten sind
auch Hilfsprozesse des vollständigen Sammlers. Die separat gesicherte lokale
Abhängigkeitsvorbereitung des Gates ist in der Zahl 120 nicht enthalten.
Vorbereitungsfehler und der fehlgeschlagene Entwicklungsversuch werden nicht
als erfolgreiche Abnahme gezählt.

| Prüfung | Tatsächliches Ergebnis |
|---|---:|
| Standalone-XTM | **3743 Checks**, alle vorherigen 3587 Checklabels erhalten |
| Native Role-Reification vor Reader-Änderung | **15 Checks**, 13 Beobachtungen |
| TMDM-/CTM-/CXTM-Kern | **12100 Checks** |
| XML-Qualifikation | **146 PASS, 0 FAIL** |
| CTM/XTM-Mergemap-Integration | **217 Checks** |
| CTM/XTM-Äquivalenz | **529 Checks, 30 Paare, 3 Kontraste** |
| Slice 20A / 20B | 286 / 25 Checks |
| Slice 20C / 20E | 171 / 13 Checks |
| Slice 20F / 20G / 20H | 112 / 226 / 722 Checks |
| Executor-Fehlerkontrollen | **113**, jeweils erwarteter ASDF-Fehlerausgang |
| Python / NFC-Oracle | **2 Tests / 16294 Vergleiche** |

Der reguläre ASDF-Lauf umfasst sämtliche bisherigen XTM- und Slice-20-/22-
Prüfungen einschließlich beider Mergemap-Pfade, Reification, Item Identity und
Normalisierung. **48 Nicht-XTM-Reports bleiben byteidentisch**; der weitere
Äquivalenzreport enthält den oben ausgewiesenen Fortschritt.

| Registrierter Korpus | Vorher PASS/FAIL/NOT-RUN | Nachher PASS/FAIL/NOT-RUN |
|---|---:|---:|
| XTM 2.0 | 115/0/9 | **121/0/3** |
| CTM | 262/4/7 | **262/4/7** |

[all-124-original-statuses.json](../reports/slice-22n/after/all-124-original-statuses.json)
vergleicht sämtliche alten/neuen Case-Status und tatsächlichen Reader-Diagnosen.
Genau sechs Originaldiagnosen ändern sich; **118 bleiben unverändert**.
Alle bisherigen 115 PASS bleiben erhalten. Die sechs neuen Entscheidungen
betreffen ausschließlich die beauftragten Originale.
[diagnostic-changes.json](../reports/slice-22n/after/diagnostic-changes.json)
sichert jede tatsächliche Änderung.

Die vier bekannten CTM-FAILs bleiben sichtbar und unverändert:
`include-template.ctm`, `include-wildcard2.ctm`,
`occurrence-datetime-timezone2.ctm`, `occurrence-datetime2.ctm`.

[integrity.json](../reports/slice-22n/after/integrity.json) prüft Größe und SHA-256
aller **2006 gepinnten Korpusdateien**, einschließlich aller Originalquellen und
Baselines. Alle **8026 historischen Reportdateien** bleiben hashidentisch.
Insgesamt bleiben **10324 geschützte Ausgangsdateien** unverändert. Corpus Lock,
TMDM, CTM, CXTM und XML bleiben unverändert; allein der XTM-Reader ändert
Produktionsverhalten.

[runs.json](../reports/slice-22n/after/runs.json) und
[execution.json](../reports/slice-22n/after/execution.json) enthalten genaue
Kommandos, Laufzeiten, Exitcodes und Loghashes.
[completion-audit.json](../reports/slice-22n/completion-audit.json) bindet
Implementierung, Tests, Dokumentation und alle neuen Evidenzdateien über
SHA-256 an den lokalen Commit-Inhalt. Der Parent ist oben benannt; die finale
Commit-ID wird nach Erstellung separat ausgegeben.

Reproduktion in ein neues Verzeichnis außerhalb des Repositorys:

```sh
python3 scripts/validate-slice-22n.py --output /private/tmp/topic-maps-22n-new
python3 scripts/validate-slice-22n.py --audit-only --output /private/tmp/topic-maps-22n-new
```

Der Validator verwendet den unveränderten Offline-Sammler aus Slice 22D.
Er prüft die historische Ausführung des Native-Gates auf dem ursprünglichen
Reader sowie die unveränderten Gate-Quellen/Hashes; ein neuer Lauf mit dem
fertigen Reader wird nicht als neuer Vorher-Nachweis ausgegeben. Die identischen
nativen Checks werden im ASDF-Lauf wiederholt. Ende Slice 22N.
