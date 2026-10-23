# Slice 22M — XTM 2.0 Association-Reification

Ausgangscommit und Commit-Parent:
`27bf0dc4e2ab1e5afefcc616df8afdd73f815607`.
Branch: `codex/xtm-slice-22m`, aus dem sauberen Branch `codex/xtm-slice-22l`.
Dessen Parent ist `c02207856f1927302ea064bc901e07183242f2da`.
Index und Arbeitsbaum waren zu Beginn sauber. Der gespeicherte Ausgangsharness
weist XTM **110 PASS, 0 FAIL, 14 NOT-RUN** und CTM **262 PASS, 4 FAIL, 7 NOT-RUN**
aus. [initial-state.json](../reports/slice-22m/initial-state.json) sichert SHA-256
aller 10017 verfolgten Ausgangsdateien.

## Normativer Vertrag und Editionsgrenze

**Normativ abgeleitet:** [XTM 2.0 §§4.3.2, 4.3.4, 4.6 und 4.18–4.20](https://www.isotopicmaps.org/sam/sam-xtm/)
ordnet das `reifier`-Attribut der dargestellten Association zu. Nach IRI-Auflösung
wird ein Topic anhand seines II gesucht beziehungsweise mit diesem II erzeugt.
Der Reifier-Locator ist kein Association-II. `reifiable` erlaubt daneben eigene
`itemIdentity`-Kinder. Role-Metadaten gehören zum jeweiligen Role-Item.
`topicRef` hat einen anderen Lookup-Vertrag als `reifier`.

**Normativ abgeleitet:** [TMDM 2006 §§5.1, 5.3.4–5.3.5, 5.7, 6.2 und 6.6](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/)
verlangt inverse Reifier-Beziehungen und verbietet einem Topic, verschiedene
Information Items zu reifizieren. Gleiche Associations bestimmen sich aus Type,
Scope und Role-Menge. Beim Merging werden II vereinigt; zwei vorhandene Reifier
werden als Topics zusammengeführt. Reifier und Identifier ersetzen keine
fachliche Association-Gleichheit. Alte Handles folgen dem bestehenden Modellpfad.

**Geprüfte Editionsgrenze:** Die [korrigierte Fassung von 2008](https://www.isotopicmaps.org/sam/sam-model/)
und [publizierten Errata](https://www.isotopicmaps.org/sam/errata.html) wurden
abgeglichen. Die dort benannten Korrekturen zu Default-Name-Type (§7.5) und
Variant-Vereinigung beim Name-Merge (§6.3) begründen keine neue Anforderung für
diesen Association-Reification-Vertrag. Die 2006er Regeln bleiben Grundlage;
TMDM wird nicht geändert.

## Tatsächlich vor der Reader-Änderung ausgeführtes Native-Gate

[api-preflight.lisp](../reports/slice-22m/api-preflight.lisp) lädt die vorhandenen
Systeme und ruft ausschließlich die nativen API-Proben auf. Der frische
SBCL-2.5.4-Prozess läuft ohne Benutzer-/Systeminitialisierung, mit gesperrtem
Netzwerk und Repository-Schreibzugriff. Er ruft keinen Reader auf und registriert
keine Originalverträge. [native-before-execution.json](../reports/slice-22m/native-before-execution.json)
belegt Befehle, Zeitpunkt und Quellhashes. Der Reader-Hash entspricht dem
Ausgangscommit; vor und nach dem Gate war der Produktionsdiff leer.

**Beobachtet:** Alle **12 Checks** bestanden. Drei getrennte SI-/SL-/II-Proben
vereinigen zunächst unterschiedliche Player-Topics und damit gleiche
Associations. Sie prüfen Association-/Role-II-Vereinigung, Reifier-Topic-Merging,
Type, Scope, Parent, Player, inverse Referenzen und alte Association-, Role- und
Topic-Handles. Eine weitere Probe normalisiert gleiche Associations mit demselben
Reifier. Vier Konfliktproben prüfen zwei verschiedene Associations, Association
gegen Occurrence beziehungsweise Map sowie späteres Reifier-Topic-Merging.
Eine zusätzliche Probe trennt Association-II von Reifier-Topic-II.
Alle fehlgeschlagenen nativen Operationen lassen den beobachteten Zustand gleich.

Die neun strukturierten Beobachtungen stehen im
[Native-Report](../reports/slice-22m/native-before/report.json), das tatsächliche
[Log](../reports/slice-22m/native-before/run.log) enthält die zwölf Checklabels.
Dieselben Funktionen und Beobachtungen werden im regulären ASDF-Lauf wiederholt.
Ein erster Testversuch verwendete die falsche `intern-topic`-Arity. Nach Prüfung
des vorhandenen Vertrags wurde ausschließlich der Test auf
`add-topic-identifier` korrigiert. Dieser erfolglose Versuch ist in
[attempts/](../reports/slice-22m/attempts/) erhalten und zählt nicht als bestandenes
Gate. Es lag kein nachgewiesener Modellfehler vor.

## Minimale Reader-Änderung und Reihenfolge

Nur `src/xtm/reader.lisp` ändert Produktionsverhalten:

1. `validate-source` prüft weiterhin die Reifier-IRI. Association-Reification
   wird akzeptiert, Role-Reification bleibt spezifisch Unsupported.
2. `read-association` löst die vorhandenen Type-, Scope- und Role-Referenzen auf.
3. `make-association` erzeugt beziehungsweise normalisiert die komplette native
   Association einschließlich gleicher Roles.
4. `read-item-identities` weist Association-II dem kanonischen Item zu.
5. Jede XML-Role wird anhand kanonischer Type-/Player-Signatur innerhalb dieser
   Association wiedergefunden und erhält über den vorhandenen Pfad ihre Role-II.
6. Erst danach wird `read-item-reifier` für die Association aufgerufen.
7. `canonical-association` liefert den aktuellen Handle nach möglichen weiteren
   Reifier-/Topic-/Association-Merges zurück.

Role-Reihenfolge und Identifier sind keine Gleichheitsschlüssel. Der vorhandene
Reifier-Pfad sucht nur nach Topic-II und verwendet bei einem Miss `intern-topic`;
mögliches anschließendes SI-/II-Cross-Merging bleibt native TMDM-Semantik.
Eine Gegenprobe fordert dabei die notwendige Topic-II-Ergänzung bei vorher nur
über SI identifiziertem Topic. Aus der Reifier-IRI werden keine SI oder SL
abgeleitet. Es entsteht keine zweite Reifier-, Association- oder Role-Verwaltung.

## Fünf tatsächliche Originalverträge

Alle Originalquellen, Hexbytes, SHA-256 und unveränderten Baselines stehen in
[originals-before.json](../reports/slice-22m/originals-before.json).
[original-contracts.json](../reports/slice-22m/after/original-contracts.json)
enthält die erneute produktive Deserialisierung, native Modelle, Handles und
vollständige Vergleiche. Tatsächlich erzeugte CXTM-Dateien stehen in
[actual/](../reports/slice-22m/after/actual/).

| Original unter `xtm2/in/` | Quellbytes | Actual/Baseline Bytes | Native Struktur |
|---|---:|---:|---|
| `association-reifier.xtm` | 304 | **612/612** | 4 Topics, 1 Association, 1 Role, Reifier `#reifier` |
| `association-duplicate-reified.xtm` | 796 | **941/941** | 6 Topics, 2 gleiche Quell-Associations, 1 kanonische Association mit 2 Roles, Reifier `#reifier1` |
| `association-duplicate-reified2.xtm` | 836 | **1010/1010** | wie zuvor; Association-II `#association` in erster Quell-Association |
| `association-duplicate-reified3.xtm` | 836 | **1010/1010** | bytegleich zu `association-duplicate-reified2.xtm`; separat ausgeführt |
| `association-duplicate-reified4.xtm` | 836 | **1010/1010** | Association-II `#association` in zweiter Quell-Association |

**Beobachtet:** Alle fünf sind PASS, Condition `null`, erste abweichende
Byteposition `null`. Der Association Type ist `#assoctype`, Scope jeweils leer.
Der einfache Vertrag hat Role Type `#roletype`, Player `#topic`; die vier
Duplikatverträge haben `#roletype1`/`#player1` und `#roletype2`/`#player2`.
Topics behalten ihre einzelnen dokumentlokalen II und haben keine SI/SL.
Es gibt keine Names oder Occurrences und keine Map-II. Roles haben keine eigenen
II oder Reifier in diesen Originalen. Die II auf Associations bleiben erhalten.

Die vier Duplikatquellen verwenden tatsächlich denselben Reifier `#reifier1`;
sie sind kein Ersatz für die zusätzlichen Gegenproben mit verschiedenen
Reifier-Topics. Keine der fünf Quellen benötigt Role-Reification oder andere
ausgeschlossene Fähigkeiten. Diese Umfangsprüfung erfolgte vor der Implementierung.

Jeder Vertrag verwendet unveränderte Octets, `deserialize-octets` und genau einen
qualifizierten XML-Parseraufruf pro Deserialisierung. Document IRI ist
`https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/`
plus vollständiger Case-ID; Source Key ist separat die Case-ID. Eine zweite echte
Deserialisierung mit anderem Key ergibt identische native Eigenschaften und Bytes.
Parent-, Type-, Player-, Scope-, Role- und Reifier-Referenzen sind innerhalb der
Map kanonisch `EQ`. Inverse `rolesPlayed` und `reified` sind geprüft.
Ersetzte Association- und Role-Handles bleiben auflösbar. Wiederholte vollständige
CXTM-Kanonisierung erhält Modell, Identifier, Reifier und Handles unverändert.

## Dauerhafte Gegenproben und Conditions

Die neuen Testdateien sind serielle Komponenten des vorhandenen
`topic-maps/xtm/tests`. `run-tests` führt Native-Gate, Originalverträge und
Gegenproben tatsächlich aus. Die fünf neuen Case Records werden genau einmal
registriert, ausschließlich nach nativen Prüfungen und tatsächlichem
Original-CXTM-Vergleich. Alle vorherigen 110 Records bleiben unverändert.

**15 positive Reader-Proben** prüfen unbekannte und vorher/später definierte
Reifier, II-Treffer und SI-Cross-Merging nach II-Miss, absolute URN und relative
prozentkodierte Unicode-IRI, Association-II neben Reification, gleiche
Associations mit gleichem beziehungsweise verschiedenem Reifier, beide
Reihenfolgen reifizierter/unreifizierter Duplikate, Role-II-Vereinigung,
vertauschte und doppelte Roles, Scope-Mengen sowie spätes SI-/SL-/II-Merging von
Association Type, Role Type, Player, Scope und Reifier.

**18 negative Reader-Proben** unterscheiden Syntax, XML, native TMDM-Konflikte
und weiterhin Unsupported. Die folgende Tabelle ist aus dem tatsächlich
ausgeführten Report abgeleitet. XTM-Zeile/Spalte ist approximative SAX-Position;
native Conditions erhalten keine erfundenen Positionsslots.

| Gegenprobe | Condition | Code | Position |
|---|---|---|---|
| `bad-percent` | `XTM-REJECTION` | `invalid-percent-escape` | 1:90 |
| `bad-percent-UTF8` | `XTM-REJECTION` | `invalid-percent-utf8` | 1:93 |
| `bad-IRI` | `XTM-REJECTION` | `invalid-iri` | 1:92 |
| `extra-attribute` | `XTM-REJECTION` | `unexpected-attribute` | 1:99 |
| `reifier-on-type` | `XTM-REJECTION` | `unexpected-attribute` | 1:95 |
| `reifier-on-topicRef` | `XTM-REJECTION` | `unexpected-attribute` | 1:185 |
| `malformed-XML` | `XTM-XML-ERROR` | `xml-not-well-formed` | 1:97 |
| `missing-Type` | `XTM-REJECTION` | `missing-type` | 1:95 |
| `missing-Roles` | `XTM-REJECTION` | `missing-roles` | 1:89 |
| `wrong-order` | `XTM-REJECTION` | `missing-type` | 1:95 |
| `different-Associations-same-Reifier` | `REIFICATION-ERROR` | `reifier-conflict` | keine nativen Slots |
| `Occurrence-and-Association-same-Reifier` | `REIFICATION-ERROR` | `reifier-conflict` | keine nativen Slots |
| `Map-and-Association-same-Reifier` | `REIFICATION-ERROR` | `reifier-conflict` | keine nativen Slots |
| `late-Reifier-conflict-subjectIdentifier` | `REIFICATION-ERROR` | `reifier-conflict` | keine nativen Slots |
| `late-Reifier-conflict-subjectLocator` | `REIFICATION-ERROR` | `reifier-conflict` | keine nativen Slots |
| `late-Reifier-conflict-itemIdentity` | `REIFICATION-ERROR` | `reifier-conflict` | keine nativen Slots |
| `Association-II-not-Reifier-Topic-II` | `OCCURRENCE-IDENTIFIER-ERROR` | `duplicate-item-identifier` | keine nativen Slots |
| `Role-Reification-remains-Unsupported` | `XTM-UNSUPPORTED` | `unsupported-construct` | 1:143 |

Native Reifier-Konflikte melden `Topic already reifies a different information
item.` beziehungsweise beim Topic-Merge `Topics reify different information
items.`. Der vorhandene generische Identifier-Konflikt wird historisch als
`OCCURRENCE-IDENTIFIER-ERROR` signalisiert, auch für Association gegen Topic;
sein Code ist `duplicate-item-identifier`. Es wird keine neue Condition eingeführt.
Native Conditions haben hier keine Source-/Document-IRI-/Positions-/Cause-Slots.
Quelltext, Document IRI und Source Key stehen separat im Kontrolldatensatz.
XML-Fehler behalten die ursprüngliche Parser-Cause, XTM-Fehler ihren echten
Quellenkontext. Konflikte bleiben native Conditions, keine künstlichen
XTM-Syntax- oder Unsupported-Fehler.

Die native Atomizität wird am Gate-Zustand vor und nach der jeweiligen
fehlgeschlagenen Operation geprüft. Zusätzlich beobachten Reader-Gegenproben
die tatsächliche fehlgeschlagene native Zuweisung und deren unveränderten
Modellzustand, soweit eine solche Zuweisung erreicht wird. Das ist keine
Behauptung allgemein transaktionaler XTM-Deserialisierung.

Eine weitere Probe durchläuft den bestehenden XTM-`mergeMap`-Pfad mit scoped,
reifizierter Association sowie Association- und Role-II. Player-Merging,
kanonische Parent-/Type-/Player-/Scope-/Reifier-Referenzen, inverse Beziehungen
und unveränderte Quellmap werden geprüft. Map-Metadaten werden nicht zusätzlich
übertragen. Die 34 neuen Kontrolldatensätze enthalten 15 positive, 18 negative
und eine Importbeobachtung. Vollständige Quellen und Modelle stehen in
`after/xtm.json`, Felder `associationReifierControls` und `mergemapControls`.

## Retargetings und bestehende Äquivalenz

[retargetings.json](../reports/slice-22m/retargetings.json) enthält jede Änderung
mit ursprünglichem Prüfzweck und alter/neuer Quelle. Fünf bisherige
Association-Unsupported-Quellen behalten ihre nun gültige Association-Reification
und verwenden zusätzlich die weiterhin normativ gültige, nicht implementierte
Role-Reification. Klasse `XTM-UNSUPPORTED` und Code `unsupported-construct`
bleiben erhalten. Scope, Association-II und diagnostische Kontexte bleiben
Bestandteil der jeweiligen Prüfung. Keine Gegenprobe wird entfernt.

Die bestehende Map-Reification-Kontrolle mit beiden Reifier-Attributen behält
ihre XML-Quelle; nun erreicht sie spezifisch die Role-Grenze. Ebenso bleibt die
XML-Quelle der sprachübergreifenden Probe `association-role-scope-reifiers`
unverändert. Ihr erwartetes fehlendes Element wird von `association` auf `role`
präzisiert. Das bezeichnet konkret **Role-Reification**, nicht einen fehlenden
Role-Kern. Die tatsächliche Condition nennt diese Fähigkeit ausdrücklich.

Alle bisherigen **29 tatsächlichen CTM/XTM-Paare und drei Kontraste** bleiben
unverändert. Die eine Fähigkeitslücke bleibt offen; sie ist kein bestandenes
Reader-Paar und kein neuer Original-PASS. Der Vergleich zählt weiterhin
515 Checks. Die genauen Reportdifferenzen stehen in
[retargeted-control-observations.json](../reports/slice-22m/after/retargeted-control-observations.json)
und [equivalence-boundary.json](../reports/slice-22m/after/equivalence-boundary.json).

Alle **113 Executor-Fehlerkontrollen** behalten den unveränderten Treiber,
ihre bisherigen Case Records, Outcomes, Status und Checklabels. Sie müssen
jeweils den vorgesehenen ASDF-Fehlerausgang erreichen und werden nicht als
bestandene Originale gezählt. Die fünf neuen Originale werden durch alte
Fehlerinjektionen nicht als ausgeführt ausgegeben.

## Umfangsgrenze

Role-Reification und `xtm2/invalid/role-duplicate-reified.xtm` bleiben außerhalb
dieses Slices. Keine Implementierung von `xsd:anyType`, zyklischer Mergemap-
Semantik, Map-II-Übertragung, anderer XML-ID-Soundness oder XTM 2.1.
TMDM, CTM, CXTM und XML werden nicht geändert. Keine HyperDoc-Änderungen,
Downloads, Pushes, Deployments oder Änderungen langlebiger Lisp-Images.

## Vollständige Offline-Abnahme

**Beobachtet und auditiert:** Alle 119 Prozesse des vollständigen Sammlers
haben den erwarteten Exitcode. Der frische SBCL 2.5.4 verwendet
`--no-sysinit --no-userinit`, ausschließlich lokal gepinnte Abhängigkeiten und
eine explizite Netzwerksperre. Repository- und HyperDoc-Schreibzugriffe sind
für die Testprozesse gesperrt. Einschließlich des erfolgreichen Native-Gates
sind 120 frische Prozesse belegt; die Zahl umfasst auch Hilfsprozesse zur
Vorbereitung und Python-Prüfung im vollständigen Sammler. Die zusätzliche lokale
Abhängigkeitsvorbereitung vor dem Native-Gate ist separat in
[native-before/dependency-preparation.json](../reports/slice-22m/native-before/dependency-preparation.json)
gesichert und in der Zahl 120 nicht enthalten. Fehlgeschlagene Entwicklungsversuche werden
nicht als erfolgreiche Abnahme gezählt.

Befehle, Laufzeiten, Exitcodes und SHA-256 der Logs stehen in
[runs.json](../reports/slice-22m/after/runs.json) und
[execution.json](../reports/slice-22m/after/execution.json).

| Prüfung | Tatsächliches Ergebnis |
|---|---:|
| Standalone-XTM | **3587 Checks**, vorherige 3447 erhalten |
| Native Association-Reification vor Reader-Änderung | **12 Checks** |
| TMDM-/CTM-/CXTM-Kern | **12100 Checks** |
| XML-Qualifikation | **146 PASS, 0 FAIL** |
| CTM/XTM-Mergemap-Integration | **217 Checks** |
| CTM/XTM-Äquivalenz | **515 Checks**, 29 Paare, 3 Kontraste, 1 verbleibende Lücke |
| Slice 20A | 286 Checks |
| Slice 20B | 25 Checks |
| Slice 20C | 171 Checks |
| Slice 20E | 13 Checks |
| Slice 20F | 112 Checks |
| Slice 20G | 226 Checks |
| Slice 20H | 722 Checks |
| Executor-Fehlerkontrollen | **113**, jeweils erwarteter Fehlerausgang |
| Python | **2 Tests** |
| NFC-Oracle | **16294 Vergleiche** |

Der reguläre ASDF-Lauf enthält sämtliche bisherigen XTM-Namen-, Scope-,
Variant-, Occurrence-, Association-/Role-, Item-Identifier-, Reification- und
Mergemap-Prüfungen. 48 Nicht-XTM-Reports bleiben byteidentisch zur letzten
Abnahme; beim weiteren Äquivalenzreport ändert sich ausschließlich die
präzisierte Role-Reification-Grenze. Checks, tatsächliche Paare und Kontraste
bleiben unverändert. Neue Featurefelder in alten Fault-Reports bleiben leer;
die übrigen Änderungen beschränken sich auf dokumentierte Retargetings.

| Registrierter Korpus | Vorher PASS/FAIL/NOT-RUN | Nachher PASS/FAIL/NOT-RUN |
|---|---:|---:|
| XTM 2.0 | 110/0/14 | **115/0/9** |
| CTM | 262/4/7 | **262/4/7** |

[all-124-original-statuses.json](../reports/slice-22m/after/all-124-original-statuses.json)
enthält alle registrierten Vorher-/Nachher-Status und Reader-Diagnosen.
[diagnostic-changes.json](../reports/slice-22m/after/diagnostic-changes.json)
belegt genau die fünf beauftragten Änderungen und **119 unveränderte Diagnosen**.
Alle bisherigen 110 PASS bleiben erhalten. Insbesondere
`xtm2/invalid/role-duplicate-reified.xtm` bleibt diagnostisch unverändert und
NOT-RUN. Kein weiterer Originalvertrag wird aufgrund einer Hilfsprobe
hochgestuft.

Die vier bekannten CTM-FAILs bleiben sichtbar:
`include-template.ctm`, `include-wildcard2.ctm`,
`occurrence-datetime-timezone2.ctm`, `occurrence-datetime2.ctm`.

## Integrität und lokale Lieferung

[integrity.json](../reports/slice-22m/after/integrity.json) prüft Größe und SHA-256
aller **2006 gepinnten Korpusdateien**, einschließlich Originalquellen und
Baselines. Alle **7714 historischen Reportdateien** bleiben hashidentisch.
Insgesamt sind **10010 geschützte Ausgangsdateien** unverändert. Corpus Lock,
TMDM, CTM, CXTM und XML sind unverändert; die einzige geänderte Produktionsdatei
ist der XTM-Reader.

[completion-audit.json](../reports/slice-22m/completion-audit.json) bindet
Implementierung, Tests, neue Dokumentation und sämtliche neuen Evidenzdateien
über SHA-256 an den vorgesehenen lokalen Commit-Inhalt. Der Parent ist oben
angegeben; die finale Commit-ID wird nach Erstellung separat ausgegeben.

Reproduktion in ein neues Verzeichnis außerhalb des Repositorys:

```sh
python3 scripts/validate-slice-22m.py --output /private/tmp/topic-maps-22m-new
python3 scripts/validate-slice-22m.py --audit-only --output /private/tmp/topic-maps-22m-new
```

Der Validator verwendet den unveränderten Offline-Sammler aus Slice 22D. Er
prüft den historisch vor der Reader-Änderung ausgeführten Gate-Prozess und dessen
Quellhashes; ein neuer Lauf mit dem fertigen Reader wird nicht als neuer
Vorher-Nachweis ausgegeben. Die identischen nativen Checks werden im ASDF-Lauf
wiederholt. Eine reine Audit-Formatkorrektur berücksichtigt, dass der bestehende
Äquivalenzreport den Condition-Text unter `message` statt `detail` speichert;
Tests und Reader wurden dafür nicht erneut verändert oder ausgeführt.
