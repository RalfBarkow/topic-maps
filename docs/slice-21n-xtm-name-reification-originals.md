# Slice 21N — Drei Name-Reification-Originalverträge registrieren

## Ausgangszustand und Umfang

Branch: `codex/xtm-slice-21n`. Ausgangscommit und Parent:
`9daceb816dbd75446ecb8ec0ef4cb5413d381588`.
Der vorgefundene Branch war `codex/xtm-slice-21m`; Index und Arbeitsbaum waren sauber.
[initial-state.json](../reports/slice-21n/initial-state.json) erhält die damaligen SHA-256 aller versionierten Dateien.

**Keine Produktionscodeänderung.** Reader, TMDM, CTM, CXTM und XML bleiben bytegenau unverändert.
Die drei aus Slice 21M bekannten Erfolge werden hier mit neuen öffentlichen Reader-Aufrufen,
nativen Modellprüfungen und vollständigen Originalvergleichen dauerhaft registriert.
Historische Beobachtungen werden weder ersetzt noch rückwirkend als registrierte PASS gewertet.

Vor allen Repository-Änderungen liefen der vollständige Ausgangstest und die 124 Diagnosen
in frischen SBCL-2.5.4-Prozessen, ohne System-/Benutzerinitialisierung, mit Netzwerk-
und Repository-Schreibsperre. Der Ausgangsreport reproduziert **2157 XTM-Prüfungen**
und **XTM 65 PASS / 0 FAIL / 59 NOT-RUN** exakt zu Slice 21M. Auch die vollständige
CTM-/TMDM-/CXTM-Regression reproduziert **CTM 262 PASS / 4 FAIL / 7 NOT-RUN**.
Alle 124 Diagnosen und 48 Nicht-XTM-Teilberichte stimmen strukturell überein.
Siehe [baseline-execution.json](../reports/slice-21n/baseline-execution.json),
[baseline.log](../reports/slice-21n/baseline.log),
[baseline-xtm.json](../reports/slice-21n/baseline-xtm.json),
[baseline-regression.log](../reports/slice-21n/baseline-regression.log),
[baseline-retained/](../reports/slice-21n/baseline-retained/) und
[baseline-ctm.validation.json](../reports/slice-21n/baseline-ctm.validation.json).

## Drei unveränderte Originalquellen und Baselines

Alle Aussagen unten sind neu beobachtete Ausführungsbefunde. Grundlage sind die
unveränderten Quellen und Baselines des gepinnten Korpus
`cd165b150176c1d6842b37be9cc9051b40d4996b`.

| Originalquelle | Quellbytes | Name-Elemente | Besonderheit | CXTM Ist/Soll | Ergebnis |
| --- | ---: | ---: | --- | ---: | --- |
| [name-duplicate-reified2.xtm](../vendor/cxtm/xtm2/in/name-duplicate-reified2.xtm) | 397 | 2 | Variant am ersten Name | **701/701** | PASS |
| [name-duplicate-reified3.xtm](../vendor/cxtm/xtm2/in/name-duplicate-reified3.xtm) | 286 | 2 | `#name` am ersten Name | **497/497** | PASS |
| [name-duplicate-reified4.xtm](../vendor/cxtm/xtm2/in/name-duplicate-reified4.xtm) | 286 | 2 | `#name` am zweiten Name | **497/497** | PASS |

| Original | SHA-256 Quelle | SHA-256 Baseline = tatsächliche Ausgabe |
| --- | --- | --- |
| `name-duplicate-reified2.xtm` | `27784c98583ec549d0572ad655fd052598525918f0aaa956bf4a4c8dab186ebb` | `38ba091848a16e79c529088e5554e689c15d6ccbc34ae032434ee193fcce90fd` |
| `name-duplicate-reified3.xtm` | `454f3dd3f062f5cd2569f043ea87a9e9f3c571087c7999e4508f834ac94131ff` | `bf6cf3cbff769f3c1f23ab4227db60492d55651806cd316201137df7da5b2331` |
| `name-duplicate-reified4.xtm` | `562d1f8f781ff394d3c699046d727b03e38426eb78c231f830bf7edc1bf90207` | `bf6cf3cbff769f3c1f23ab4227db60492d55651806cd316201137df7da5b2331` |

Die Größen und Hashes wurden direkt an den gepinnten Dateien geprüft und zusätzlich
mit den historischen [Slice-21M-Beobachtungen](../reports/slice-21m/further-name-reification-observations.json)
verglichen. Der erfolgreiche historische Befund ersetzt keinen neuen Test.
Vollständige Quellen als Hex und Text sowie Baselines stehen in
[candidate-inventory.json](../reports/slice-21n/candidate-inventory.json);
[name-followup-originals.json](../reports/slice-21n/name-followup-originals.json) ergänzt
die neu ausgeführten Modelle, Traces, Conditions und vollständigen CXTM-Texte.
Die tatsächlichen Ausgabebytes bleiben in [actual/](../reports/slice-21n/actual/) erhalten.

Die Document IRI ist jeweils folgender Präfix plus Case-ID `xtm2/in/<Dateiname>`:

```text
https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/
```

Der primäre Source Key ist die Case-ID. Alle drei Eingaben gehen als unveränderte
Rohbytes an `topic-maps.xtm:deserialize-octets`. Die instrumentierte primäre
Vertragsausführung belegt genau einen Aufruf des qualifizierten XML-Parsers mit
dem originalen Bytevektor per EQ. Quellen und Baselines werden nicht umgeschrieben.

## Native Name-, Reifier-, Variant- und Identifier-Beziehungen

Alle drei Quellen enthalten genau ein Topic `id="topic"` mit zwei gleichwertigen
Name-Elementen. Beide haben Value `Topic`, keinen expliziten Type, leeren Scope
und dasselbe `reifier="#reifier1"`. Der Default-Type hat ausschließlich den SI
`http://psi.topicmaps.org/iso13250/model/topic-name`.

Die tatsächlichen TMDM-Objekte belegen:

- Genau ein kanonischer Name gehört zum Parent `DocumentIRI#topic`.
  `topic-name-parent` und Parent-Topic sowie `topic-name-type` und Default-Type
  sind jeweils EQ. Value ist exakt `Topic`, Name-Scope ist leer.
- `item-reifier(name)` ist EQ zum kanonischen `DocumentIRI#reifier1`-Topic.
  `topic-reified(reifier)` ist EQ zum selben Name. Parent, Type und Map werden
  durch diese Beziehung nicht reifiziert. Reifier-II und Parent-II bleiben getrennt;
  die Map hat keine Item Identifier. Es entstehen keine SL oder zusätzlichen SI.
- `name-duplicate-reified2.xtm` enthält vier Topics und genau einen erhaltenen
  Variant. Value ist exakt `topic`, Datatype ist
  `http://www.w3.org/2001/XMLSchema#string`. Sein Parent ist EQ zum kanonischen Name;
  sein Scope besteht ausschließlich aus dem kanonischen Theme `DocumentIRI#ahwell`.
  Der Theme-Topic hat ausschließlich diesen II. Der Variant hat weder II noch Reifier.
- `name-duplicate-reified3.xtm` und `name-duplicate-reified4.xtm` enthalten je drei
  Topics und keine Variants. Der aufgelöste II `DocumentIRI#name` gehört ausschließlich
  zum kanonischen Name. Die native Suche über alle Information Items liefert per EQ
  nur diesen Name; Parent, Reifier und Type erhalten den Locator nicht zusätzlich.
- Globale Identifier-Eindeutigkeit, kanonische Parent-/Type-/Scope-Referenzen und
  Reification-Inversen bestehen. Es gibt keine Associations, Occurrences oder Rollen.

Diese Prüfungen verwenden die vorhandenen nativen APIs und tatsächliche EQ-Referenzen.
Die CXTM-Ausgabe allein ist nicht ihr Identitätsnachweis.

## Reihenfolge, Normalisierung und erhaltene Handles

Ein gesonderter Gegenversuch verarbeitet die **ursprünglichen Name-Knoten** mit den
vorhandenen `read-name`-/TMDM-Operationen nacheinander. Der primäre Originalvertrag
bleibt immer die öffentliche Deserialisierung der vollständigen Originalbytes.
Der Gegenversuch erzeugt keine weiteren Case Records und zählt nicht als Ersatzmap.

| Original | Name-II nach erstem Knoten | Name-II nach zweitem Knoten | Variant nach beiden Knoten |
| --- | --- | --- | --- |
| `name-duplicate-reified2.xtm` | leer | leer | dasselbe ursprüngliche Variant-Objekt |
| `name-duplicate-reified3.xtm` | `DocumentIRI#name` | `DocumentIRI#name` | keiner |
| `name-duplicate-reified4.xtm` | leer | `DocumentIRI#name` | keiner |

In jedem Fall liefern beide `read-name`-Aufrufe **denselben Handle per EQ**.
Der aktuelle Name und `canonical-topic-name` dieses Handles sind EQ. Der zuerst
festgehaltene Reifier bleibt EQ zum aktuellen Name-Reifier und seine inverse
Beziehung bezeichnet weiterhin denselben Name. Im Variant-Fall bleibt das zuerst
festgehaltene Variant-Objekt per EQ erhalten, einschließlich kanonischem Parent.
Das vollständige Endmodell des Gegenversuchs entspricht dem öffentlichen Originalmodell.
JSON enthält `afterFirstName`, `afterSecondName` und die tatsächlich berechneten EQ-Befunde.

Wiederholte CXTM-Kanonisierung erhält vollständigen Modellzustand, native
Identifier und aktuelle wie festgehaltene Handles. Ein anderer diagnostischer
Source Key bei gleicher Document IRI erzeugt dasselbe vollständige Modell und
dieselben CXTM-Bytes. Die beiden Identifier-Reihenfolgen ergeben auch denselben
vollständigen kanonischen CXTM-Text; beide unabhängigen Originalvergleiche sind bytegenau.

## Bestehender Harness und genau drei Registrierungen

[tests/xtm-name-reification-originals.lisp](../tests/xtm-name-reification-originals.lisp)
ist ein weiterer Bestandteil des bestehenden ASDF-Testsystems. Die neue Funktion
wird ausdrücklich von `run-tests` aufgerufen. Sie verwendet dieselben Case Records,
`record-original-result`, öffentlichen Reader und Bytevergleiche wie Slice 21M.
Es gibt keine zweite Testarchitektur und keine Änderung der Ergebnissemantik.

Jeder der drei Verträge erhält genau einen Case Record und genau eine primäre
Vertragsausführung. Source-Key- und Normalisierungsgegenproben sind ausdrücklich
separate Beobachtungen ohne weitere Registrierung. Erst nach tatsächlicher
Deserialisierung, nativen Modellprüfungen und vollständiger Bytegleichheit wird PASS registriert.
Alle drei Conditions und `firstDifferentByte` sind null.

Insgesamt gibt es **68 eindeutige Case Records: 60 positive und acht negative Originale**.
Alle 65 bisherigen Originalergebnisse und alle bisherigen Berichtsfelder außer
Scope/Statistik/Checkliste/Case-Liste bleiben exakt identisch zu Slice 21M.
Der reguläre Lauf besteht mit **2204 eindeutigen XTM-Prüfungen**:
**2157 erhaltene ohne Umbenennung** und **47 neue**.
Die relative Reihenfolge aller alten Prüflabel bleibt erhalten.

## Unveränderte Diagnosen, neue Registrierung

Alle **124 ursprünglichen Reader-Diagnosen sind vor und nach dieser Aufgabe
vollständig identisch** zu Slice 21M, einschließlich Condition-Klassen, Codes,
Positionen, Causes und CXTM-Ausgaben. [diagnostic-changes.json](../reports/slice-21n/diagnostic-changes.json)
ist die leere Liste; [diagnostics.json](../reports/slice-21n/diagnostics.json) trennt
die unveränderte erfolgreiche Beobachtung von den drei neuen Konformitätsregistrierungen.
Es gibt keine neue Sprachunterstützung und keinen verschobenen Unsupported-Befund.
Alle bisherigen acht negativen Originale und deren Ursachen bleiben unverändert.
Die drei offenen negativen Verträge bleiben unregistriert.

## Vollständige Offline-Abnahme und Integrität

[execution.json](../reports/slice-21n/execution.json) erhält alle **98** frischen
Prozessaufrufe mit Kommando, UTC-Zeiten und tatsächlichen/erwarteten Exitcodes.
Jeder Ausführungsprozess verwendet eine Netzwerk- und Repository-Schreibsperre.
SBCL ist exakt 2.5.4 mit `--no-sysinit --no-userinit`. Gepinnte lokale Quellen
und die bestehenden XML-Patches werden geprüft und temporär vorbereitet.
Die unveränderte native Name-Reifier-API-Vorprüfung aus Slice 21M wird erneut ausgeführt.
Kein Download, kein Nix-Rebuild und kein langlebiges Lisp-Image.
[validate-slice-21n.py](../scripts/validate-slice-21n.py) führt die vorhandene Validierungskette fort.

| Bereich | Tatsächliches Ergebnis |
| --- | ---: |
| Erhaltene TMDM-/CTM-/CXTM-Prüfungen | 12100 PASS |
| XML-Qualifikation | 146 PASS |
| XTM | 2204 PASS |
| CTM/XTM-Mergemap | 217 PASS |
| Slice 20A / 20B / 20C | 286 / 25 / 171 PASS |
| Slice 20E / 20F / 20G / 20H | 13 / 112 / 226 / 722 PASS |
| Python-Unittests | 2 PASS |
| NFC-Oracle | 16294 Vergleiche PASS |
| Executor-Fehlerkontrollen | 92 erwartete ASDF-Fehlschläge nachgewiesen |

Alle 77 bisherigen Executor-Kontrollen bleiben erhalten. Für **jeden** der drei
neuen positiven Verträge werden zusätzlich CXTM-Byteabweichung, XML-Fehler,
XTM-Fehler, Unsupported und ein tatsächlicher nativer Reification-Konflikt injiziert.
Die 15 neuen Kontrollen erhalten jeweils alle vorausgehenden korrekten PASS und
klassifizieren den beschädigten Vertrag niemals als PASS. Native Konflikte bleiben
`REIFICATION-ERROR/:reifier-conflict`; sie sind Ausführungsfehler des positiven Vertrags.
Die bestehenden falschen-Condition-Kontrollen bleiben ebenfalls erhalten.
Siehe [failure-controls.json](../reports/slice-21n/failure-controls.json),
[failure-controls.lisp](../reports/slice-21n/failure-controls.lisp) und die Einzelberichte/Logs.

[regression.log](../reports/slice-21n/regression.log) und [retained/](../reports/slice-21n/retained/)
belegen die vollständige Abnahme. Alle **48 bisherigen Nicht-XTM-Berichte**
sind strukturell identisch. Die bekannten CTM-Abweichungen bleiben unverändert:
`include-template.ctm`, `include-wildcard2.ctm`, `occurrence-datetime-timezone2.ctm`,
`occurrence-datetime2.ctm`.

Erst nach tatsächlicher Ausführung ermittelter registrierter Stand:
**XTM 68 PASS / 0 FAIL / 56 NOT-RUN**; **CTM 262 PASS / 4 FAIL / 7 NOT-RUN**.

[integrity.json](../reports/slice-21n/integrity.json) prüft **2006 gepinnte Korpusdateien**
nach Größe und SHA-256, **3138 historische Berichte** und
**5402 geschützte Dateien des Ausgangscommits**. Sämtlicher Produktionscode,
Originalquellen, Baselines, Corpus-Lock und historische Reports bleiben unverändert.
Ausgeführte Test- und Treiberquellen werden zusätzlich vor und nach der gesamten
Abnahme auf identische Hashes geprüft. [precommit-audit.json](../reports/slice-21n/precommit-audit.json)
und [artifacts.json](../reports/slice-21n/artifacts.json) erhalten die abschließende
Pfad-/Hashprüfung und SHA-256 aller neuen Artefakte, Manifest selbst ausgenommen.

[development-attempts.json](../reports/slice-21n/development-attempts.json) bewahrt
zwei nicht abgenommene Testentwicklungsversuche mit vollständigen Logs:
eine zusätzliche schließende Klammer und den anfangs falschen Zugriff auf den
bestehenden JSON-OBJECT-Typ. Beides wurde vor der abschließenden Abnahme korrigiert.

Keine Implementierung von Variant-/Occurrence-/Association-/Role-Reification.
Keine Produktionsänderung, Downloads, HyperDoc-Änderung, langlebige Lisp-Images,
Pushes oder Deployments. Slice 21N endet mit dem gemeinsamen lokalen Commit
von Testregistrierung, Dokumentation und Ausführungsevidenz.
