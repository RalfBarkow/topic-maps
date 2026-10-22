# Slice 22H — Fünf XTM-mergeMap-Originalverträge registrieren

Genau die fünf beauftragten Originalverträge bestehen erneut mit ihren unveränderten Kindressourcen und CXTM-Baselines. Die reguläre ASDF-Testausführung registriert sie im bestehenden Konformitäts-Harness. Keine Produktionsdatei wurde geändert. Der abgenommene Stand beträgt **XTM 88 PASS, 0 FAIL, 36 NOT-RUN**, CTM unverändert **262 PASS, 4 FAIL, 7 NOT-RUN**.

Ausgangscommit: `7f4aa941293e555ccb9d96f0c05c651b0549a866`; Parent: `b50a9d7950c5407b2ec02e1caccd76f73018b45f`. Anfangsbranch `codex/xtm-slice-22g`, sauberer Index und Arbeitsbaum. Arbeitsbranch: `codex/xtm-slice-22h`. [initial-state.json](../reports/slice-22h/initial-state.json) sichert sämtliche 8.780 versionierten Ausgangsdateien. Commit und sauberer Endzustand werden nach dem Artefakt-/Indexaudit separat bestätigt.

## Originalbytes, Ressourcen und tatsächliche Vergleiche

[originals-before.json](../reports/slice-22h/originals-before.json) enthält vollständigen Quell-, Kind- und Baseline-Text, Hexbytes, Größen und SHA-256 vor der Registrierung. [original-contracts.json](../reports/slice-22h/after/original-contracts.json) enthält die erneuten wirklichen Ausführungen mit Modellen, Parser-/Resolvertrace, Conditions und vollständigen CXTM-Ausgaben. Alle fünf Conditions und ersten Byteabweichungen sind null.

| Original unter `xtm2/in/` | Originalbytes | Kindressource | Kindbytes | CXTM Ist/Soll |
|---|---:|---|---:|---:|
| `mergemap-merge.xtm` | 231 | `mergemap-merge.sub` | 159 | 1195/1195 |
| `mergemap-ontopia-issue-28-2.xtm` | 227 | `mergemap-ontopia-issue-28-2.sub` | 254 | 394/394 |
| `mergemap-ontopia-issue-28.xtm` | 301 | `mergemap-ontopia-issue-28.sub` | 178 | 392/392 |
| `mergemap-tm-reifier.xtm` | 156 | `mergemap-tm-reifier.sub` | 94 | 230/230 |
| `mergemap.xtm` | 145 | `mergemap.sub` | 111 | 217/217 |

Die tatsächlichen Dateien liegen unter `reports/slice-22h/after/actual/`. Die früheren explorativen Bytezahlen waren nur Auswahlgrundlage; jeder neue PASS beruht auf der hier erneut ausgeführten Originaldeserialisierung, nativen Prüfungen und vollständigen Bytegleichheit. Keine manuell konstruierte Ersatzmap wird als Originalvertrag gezählt.

## Tatsächlicher Resolver- und Importpfad

Jeder Primärimport ruft `topic-maps.xtm:deserialize-octets` mit den unveränderten Rootbytes auf. Die Document IRI ist `https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/<Dateiname>.xtm`. Jede ursprüngliche relative `href` verweist auf die gleichnamige `.sub`-Datei in diesem Verzeichnis.

Der explizite Resolver wird pro Original genau einmal aufgerufen, mit:

- absoluter Kind-IRI im selben Verzeichnis, Dateiendung `.sub`;
- `:purpose :mergemap`;
- `:from-document-iri` gleich der tatsächlichen Root-Document-IRI;
- `:notation "http://psi.topicmaps.org/iso13250/xtm"`.

Er liefert ausschließlich die vorher aus dem gepinnten Korpus gelesenen Kindbytes und die diagnostische Kind-Case-ID. Es gibt keine implizite Netzwerk-/Dateisystemauflösung durch den Reader. Die fünf relativen Originalverweise und ihre absoluten Resolverargumente werden unmittelbar geprüft; die bestehenden synthetischen Prüfungen für absolute hrefs und verschachtelte Imports laufen unverändert weiter.

Der qualifizierte XML-Parser erhält genau zwei Aufrufe: Root und Kind. Die Octet-Vektoren sind jeweils `EQ` mit den unveränderten tatsächlich gelesenen Vektoren. `qualifiedParserTrace` zeichnet die wirklichen dynamischen Document IRIs, Source Keys, Bytezahlen und EQ-Nachweise auf. Das Kind wird mit eigener Document IRI und eigenem XTM-Kontext verarbeitet; nach seiner Deserialisierung wird sein Inhalt durch das unveränderte `topic-maps.tmdm:import-map-content` übernommen.

Ein zweiter tatsächlicher Import jedes Originals verwendet `diagnostic:parent` und `diagnostic:child` als abweichende Source Keys bei denselben Document IRIs. Native Modelle und vollständige CXTM-Bytes müssen identisch bleiben. Source Keys werden nicht in Modellidentitäten umgewandelt.

## Native TMDM-Objekte und EQ-Nachweise

[tests/xtm-mergemap-originals.lisp](../tests/xtm-mergemap-originals.lisp) verwendet den bestehenden `mm-call`-Testpfad und dessen passive Parser-/Importbeobachter. Alle Beobachter werden wiederhergestellt und geben die tatsächlichen Ergebnisse unverändert zurück; der optionale native Augmentierungsweg wird für diese Originale nicht verwendet.

| Original | Tatsächliches Zielmodell |
|---|---|
| `mergemap-merge.xtm` | Sechs Topics, ein Name `Type`, eine Type–Instance-Association, zwei Roles. Das importierte `Kind-IRI#type` ist `EQ` zum Type-Player. Root-Topic ist `EQ` zum Instance-Player. Name-Parent, Default-Name-Type, Role-Parents und inverse Roles-Played sind kanonisch. |
| `mergemap-ontopia-issue-28-2.xtm` | Ein Topic nach SI/II-Cross-Merging. Zwei SI (`http` und `ftp`) und drei II: Root `#topic`, Kind `#sub-topic`, gemeinsame HTTP-IRI. Root-/Kind-Referenzen sind `EQ`. |
| `mergemap-ontopia-issue-28.xtm` | Dasselbe Identitätsmuster in umgekehrter SI/II-Richtung; ebenfalls ein kanonisches Topic mit beiden SI und allen drei II. |
| `mergemap-tm-reifier.xtm` | Zwei verschiedene Topics: Root `#topic` und Kind `#reifier`. Die Zielmap hat keinen Reifier; das importierte Reifier-Topic reifiziert dort kein Item. Die Quellmap behält ihre ursprüngliche Reification samt inverser Referenz. |
| `mergemap.xtm` | Zwei verschiedene Topics mit Root- beziehungsweise Kind-Document-II. Gleiche lokale Schreibweise `topic` führt bei verschiedenen Document IRIs nicht zum Merging. |

Keine der fünf Kindressourcen enthält Associations. Die Association im ersten Original entsteht durch das lokale `instanceOf` des Rootdokuments. Bereits vorhandene Importgegenproben für Associations und weitere unterstützte Inhalte laufen weiterhin mit; daraus werden keine zusätzlichen Original-PASS abgeleitet. SL-Merging wird durch bestehende Tests erhalten; die beiden Ontopia-Originale untersuchen konkret SI/II-Cross-Merging.

Für jedes importierte native Information Item wird der tatsächliche vom Importer zurückgegebene Resolver aufgerufen. Er liefert auch nach späteren lokalen Topic-Merges den aktuellen kanonischen Zielrepräsentanten (`EQ`). Quell- und Zielitems sind unterschiedliche Objekte mit jeweils korrekter Map-Zugehörigkeit. Quellmapzustand und ihre gehaltenen Handles sowie ihre CXTM-Bytes bleiben vor/nach Import und späterer Rootverarbeitung unverändert. Wiederholte Zielkanonisierung erhält Modell und Bytes.

## Map-Item-Identität und ausgeschlossene Originale

[XTM §4.21](https://www.isotopicmaps.org/sam/sam-xtm/) beschreibt die Kinddeserialisierung und den anschließenden Import von Topics und Associations. Die neue Registrierung benutzt diese bereits vorhandene Operation und ergänzt keine Übertragung von Eigenschaften des Kind-Map-Items. Die normative Einordnung und Editionsgrenzen stehen in [normative-review.json](../reports/slice-22h/normative-review.json); der öffentliche XTM-Text vom 19.06.2006 erklärt seine Identität mit der ISO-Veröffentlichung. Keine weitere Normkopie wurde beschafft.

Die Ziel-Map-Items haben in allen fünf Fällen weder eigene II noch Reifier. Die Abbildung des Quell-Map-Items durch den nativen Importresolver ergibt ausdrücklich `MAP-IMPORT-ERROR/:not-imported`: Es ist kein importiertes Inhaltsitem. Beim Reifier-Original bleibt das Reifier-Topic Inhalt, während seine Reification der Quellmap nicht auf die Zielmap übertragen wird.

`mergemap-itemid.xtm` bleibt **NOT-RUN**. Die vorhandene Beobachtung mit Resolver bleibt unverändert: 224 tatsächliche gegenüber 314 Baselinebytes, erste Differenz Byte 12, ausschließlich zusätzliche Map-II der historischen Baseline. Keine Baseline- oder Modellanpassung.

`mergemap-loop.xtm` bleibt **NOT-RUN**. Die bestehende Schutzgrenze liefert mit Resolver nach einem Ressourcenabruf `XTM-UNSUPPORTED/:cyclic-mergemap`. Das ist weiterhin keine Entscheidung oder Implementierung normativer Zyklussemantik. Alle anderen NOT-RUN-Verträge sowie die bekannten CTM-FAILs bleiben unverändert.

## Registrierung und bestehende Testinfrastruktur

Das vorhandene ASDF-System `topic-maps/xtm/tests` lädt die neue Datei und ruft `registered-mergemap-original-contracts` nach den bestehenden Occurrence-Originalen und -Gegenproben tatsächlich auf. Die bisherigen 83 Case Records bleiben erhalten. Neue Case Records verwenden die Originalquelle, explizite Document IRI und Originalbaseline. `record-original-result` unterscheidet unverändert CXTM-Match, Mismatch, Unsupported und Ausführungsfehler.

Die neue fachliche Invariante prüft die **exakte angeforderte Menge**, einmalige Registrierung jeder ID und Erhaltung sämtlicher bisherigen Case-Record-Objekte und ihrer PASS-Status. Sie setzt keine starre Gesamtzahl des Katalogs voraus. Zwei ältere Guards für die ausgeschlossenen MergeMap-Originale wurden von einem zufälligen Stufenzähler auf die konkrete Abwesenheit dieser IDs umgestellt; die Ein-Abruf-Grenze der Zyklusprobe bleibt erhalten.

[test-integration-notes.json](../reports/slice-22h/test-integration-notes.json) enthält die exakten alten/neuen Guards und Dateihashes. Zwei vorhandene Occurrence-Testvariablen werden bereits vor Kompilierung des Haupttreibers deklariert; das behebt Compile-Reihenfolge-Warnungen ohne Änderung ihrer Laufzeitsemantik. Die Beschreibungen verweisen auf tatsächliche Case-Ergebnisse statt fest eingetragener Kataloggrößen. Kein bestehender Fehlerexecutor wurde geändert.

## Vollständige Offline-Regression

Der abgenommene Lauf fand von **2026-10-22T20:24:33.286406+00:00** bis **2026-10-22T20:27:51.995209+00:00** statt. Alle 119 Prozesse sind mit Befehlen, Zeitpunkten und Exitcodes in [runs.json](../reports/slice-22h/after/runs.json) dokumentiert.


Es sind sechs reguläre Prozesse mit Exit 0 und alle 113 bisherigen Executor-Fehlerkontrollen mit erwartetem Exit 1. SBCL 2.5.4 startet frisch, ohne System-/Benutzerinitialisierung. Netzwerk sowie Repository- und HyperDoc-Schreibzugriffe sind in den Testkindprozessen gesperrt. Abhängigkeiten kommen aus vorhandenen lokalen Pins. Keine Downloads oder langlebigen Image-Loads.

| Teil | Tatsächliches Ergebnis |
|---|---:|
| XTM | 2.965 Checks, davon 96 neu; 80 positive und acht negative Original-PASS |
| TMDM / CTM / CXTM einschließlich Include / Mergemap | 12.100 Checks |
| CTM/XTM-Mergemap | 217 Checks |
| CTM/XTM-Äquivalenz | 487 Checks, 27 Reader-Paare |
| CTM registrierte Originale positiv / negativ | 286 / 25 Checks |
| Prolog / empty2 / CTM-Integer / Triple / Encoding | 171 / 13 / 112 / 226 / 722 Checks |
| XML-Qualifikation | 146 PASS |
| Python / NFC | zwei Tests / 16.294 Vergleiche |
| Executor-Fehlerkontrollen | 113; alle erwarteten Exit 1 |

Alle bisherigen 2.869 XTM-Checklabels bleiben in ihrer relativen Reihenfolge erhalten. Die bisherigen 83 Case Records bleiben vollständig gleich. Alle bisherigen XTM-Fachberichte, insbesondere Slice 22G mit Occurrence-Normalisierung und die beiden ausgeschlossenen MergeMap-Beobachtungen, bleiben gleich. 49 bisherige Nicht-XTM-Berichte einschließlich des vollständigen CTM/XTM-Äquivalenzberichts sind byteidentisch.

Die 113 Fehlerkontrollen behalten ihre tatsächlichen Case Records, Status, Outcomes und ausgeführten Checklabels vollständig. Berichtsänderungen betreffen ausschließlich die beschreibende Scope-Zeichenkette und das neue, dort noch leere Feld `registeredMergemapOriginals`. Kein Fehler wird als erfolgreicher Originalvertrag gewertet. [failure-controls.json](../reports/slice-22h/after/failure-controls.json).

[execution.json](../reports/slice-22h/after/execution.json) enthält die vollständige Abnahme. Die vier bekannten CTM-FAILs bleiben `include-template.ctm`, `include-wildcard2.ctm`, `occurrence-datetime-timezone2.ctm` und `occurrence-datetime2.ctm`.

## Statusvergleich aller 124 Originalverträge

Die vollständige maschinenlesbare Zuordnung steht in [all-124-original-statuses.json](../reports/slice-22h/after/all-124-original-statuses.json). Genau fünf registrierte Status wechseln von NOT-RUN zu PASS; die anderen 119 Status bleiben unverändert.

Die **124 bisherigen Reader-Diagnosen sind byteidentisch zu Slice 22G**. Ihr alter explorativer Treiber konfiguriert absichtlich keinen Resolver und meldet deshalb bei MergeMap weiterhin `resource-resolver-required`. Diese Diagnose wird nicht zum PASS umgedeutet. Die neuen Originalverträge werden separat mit dem expliziten gepinnten Resolver ausgeführt und dokumentiert. [diagnostic-changes.json](../reports/slice-22h/after/diagnostic-changes.json).

| Korpus | PASS | FAIL | NOT-RUN |
|---|---:|---:|---:|
| XTM 2.0 | 88 | 0 | 36 |
| CTM | 262 | 4 | 7 |

## Integrität und Reproduktion

Alle **2.006 gepinnten Korpusdateien** stimmen in Größe und SHA-256 mit dem Corpus Lock überein. Alle **6.490 historischen Reportdateien** und insgesamt **8.777 geschützten Ausgangsdateien** bleiben unverändert. Das umfasst sämtliche Produktionsdateien unter `src/`, alle Originale und Baselines sowie sämtliche bisherigen Slice-22G- und Äquivalenz-Testdateien. [Integritätsaudit](../reports/slice-22h/after/integrity.json).

Geändert sind ausschließlich ASDF-Testintegration, Haupttesttreiber, zwei bestehende Testguards sowie die neue Originaltestdatei; hinzu kommen Untersuchungswerkzeug, Dokumentation und Ausführungsevidenz. Keine Reader-/TMDM-Implementierung, keine neuen Sprachfähigkeiten, keine Änderungen an HyperDoc oder anderen Repositories, kein Push oder Deployment.

Das [Abschlussaudit](../reports/slice-22h/final-audit.json) prüft die vollständige Artefaktmenge und ihre SHA-256. Es ist ein Audit gespeicherter Ausführung, kein zusätzlicher Testlauf. Reproduktion mit neuem Ausgabeordner außerhalb des Repositories:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate-slice-22h.py --output /private/tmp/topic-maps-22h-reproduction
```

`--audit-only` prüft eine vorhandene vollständige Ausführung, ohne Tests neu zu starten. Slice 22H endet mit dem lokalen Commit der Registrierung und Evidenz.

## Vollständige Statusliste

| Exakte Case-ID | Vorher | Nachher |
|---|---|---|
| `xtm2/in/association-binary-duplicate.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/association-binary.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/association-duplicate-iid.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/association-duplicate-iid2.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/association-duplicate-iid3.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/association-duplicate-reified.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/association-duplicate-reified2.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/association-duplicate-reified3.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/association-duplicate-reified4.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/association-duplicate-role.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/association-instanceof-duplicate.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/association-instanceof-scope.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/association-reifier.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/association-scope.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/association-ternary.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/association.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/empty.xtm` | PASS | PASS |
| `xtm2/in/itemid-association.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/itemid-duplicate.xtm` | PASS | PASS |
| `xtm2/in/itemid-fragment.xtm` | PASS | PASS |
| `xtm2/in/itemid-name.xtm` | PASS | PASS |
| `xtm2/in/itemid-occurrence.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/itemid-relative.xtm` | PASS | PASS |
| `xtm2/in/itemid-role.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/itemid-tm.xtm` | PASS | PASS |
| `xtm2/in/itemid-variant.xtm` | PASS | PASS |
| `xtm2/in/itemid.xtm` | PASS | PASS |
| `xtm2/in/merge-itemid-with-association.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/merge-itemid-with-names.xtm` | PASS | PASS |
| `xtm2/in/merge-itemid-with-occurrences.xtm` | PASS | PASS |
| `xtm2/in/merge-itemid-with-types.xtm` | PASS | PASS |
| `xtm2/in/merge-itemid-with-variants.xtm` | PASS | PASS |
| `xtm2/in/merge-itemid.xtm` | PASS | PASS |
| `xtm2/in/merge-subjid.xtm` | PASS | PASS |
| `xtm2/in/merge-subjloc.xtm` | PASS | PASS |
| `xtm2/in/merge-three-way.xtm` | PASS | PASS |
| `xtm2/in/mergemap-itemid.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/mergemap-loop.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/mergemap-merge.xtm` | NOT-RUN | PASS |
| `xtm2/in/mergemap-ontopia-issue-28-2.xtm` | NOT-RUN | PASS |
| `xtm2/in/mergemap-ontopia-issue-28.xtm` | NOT-RUN | PASS |
| `xtm2/in/mergemap-tm-reifier.xtm` | NOT-RUN | PASS |
| `xtm2/in/mergemap.xtm` | NOT-RUN | PASS |
| `xtm2/in/name-duplicate-iid.xtm` | PASS | PASS |
| `xtm2/in/name-duplicate-merge.xtm` | PASS | PASS |
| `xtm2/in/name-duplicate-reified.xtm` | PASS | PASS |
| `xtm2/in/name-duplicate-reified2.xtm` | PASS | PASS |
| `xtm2/in/name-duplicate-reified3.xtm` | PASS | PASS |
| `xtm2/in/name-duplicate-reified4.xtm` | PASS | PASS |
| `xtm2/in/name-duplicate.xtm` | PASS | PASS |
| `xtm2/in/name-escaping.xtm` | PASS | PASS |
| `xtm2/in/name-reifier.xtm` | PASS | PASS |
| `xtm2/in/name-scope-duplicate-merged.xtm` | PASS | PASS |
| `xtm2/in/name-scope-duplicate.xtm` | PASS | PASS |
| `xtm2/in/name-scope-multiple.xtm` | PASS | PASS |
| `xtm2/in/name-scope.xtm` | PASS | PASS |
| `xtm2/in/name-type-after-bad.xtm` | PASS | PASS |
| `xtm2/in/name-type-after.xtm` | PASS | PASS |
| `xtm2/in/name-type-before.xtm` | PASS | PASS |
| `xtm2/in/name-type-scope.xtm` | PASS | PASS |
| `xtm2/in/name-type.xtm` | PASS | PASS |
| `xtm2/in/name-unicode.xtm` | PASS | PASS |
| `xtm2/in/name.xtm` | PASS | PASS |
| `xtm2/in/occurrence-datatype-unknown.xtm` | PASS | PASS |
| `xtm2/in/occurrence-duplicate-iid.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/occurrence-duplicate-iid2.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/occurrence-duplicate-reifier.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/occurrence-duplicate.xtm` | PASS | PASS |
| `xtm2/in/occurrence-reifier.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/occurrence-resourcedata-uri-relative.xtm` | PASS | PASS |
| `xtm2/in/occurrence-resourcedata-uri.xtm` | PASS | PASS |
| `xtm2/in/occurrence-resourceref-relative.xtm` | PASS | PASS |
| `xtm2/in/occurrence-resourceref.xtm` | PASS | PASS |
| `xtm2/in/occurrence-scope-duplicate-merged.xtm` | PASS | PASS |
| `xtm2/in/occurrence-scope-duplicate.xtm` | PASS | PASS |
| `xtm2/in/occurrence-scope.xtm` | PASS | PASS |
| `xtm2/in/occurrence.xtm` | PASS | PASS |
| `xtm2/in/role-duplicate-iid.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/role-duplicate-iid2.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/role-duplicate-reified.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/role-duplicate-reified2.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/role-duplicate-reified3.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/role-duplicate-reified4.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/role-reifier.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/in/subjid-duplicate.xtm` | PASS | PASS |
| `xtm2/in/subjid-escaping.xtm` | PASS | PASS |
| `xtm2/in/subjid-escaping2.xtm` | PASS | PASS |
| `xtm2/in/subjid-fragment.xtm` | PASS | PASS |
| `xtm2/in/subjid-relative.xtm` | PASS | PASS |
| `xtm2/in/subjid-sameas-itemid.xtm` | PASS | PASS |
| `xtm2/in/subjid.xtm` | PASS | PASS |
| `xtm2/in/subjloc-duplicate.xtm` | PASS | PASS |
| `xtm2/in/subjloc-fragment.xtm` | PASS | PASS |
| `xtm2/in/subjloc-multiple.xtm` | PASS | PASS |
| `xtm2/in/subjloc-relative.xtm` | PASS | PASS |
| `xtm2/in/subjloc.xtm` | PASS | PASS |
| `xtm2/in/tm-reifier.xtm` | PASS | PASS |
| `xtm2/in/topic-type-duplicate.xtm` | PASS | PASS |
| `xtm2/in/topic-type.xtm` | PASS | PASS |
| `xtm2/in/topic.xtm` | PASS | PASS |
| `xtm2/in/variant-datatype-unknown.xtm` | PASS | PASS |
| `xtm2/in/variant-duplicate-iid.xtm` | PASS | PASS |
| `xtm2/in/variant-duplicate-reifier.xtm` | PASS | PASS |
| `xtm2/in/variant-duplicate-reifier2.xtm` | PASS | PASS |
| `xtm2/in/variant-duplicate.xtm` | PASS | PASS |
| `xtm2/in/variant-inherit.xtm` | PASS | PASS |
| `xtm2/in/variant-reifier.xtm` | PASS | PASS |
| `xtm2/in/variant-resourcedata-uri.xtm` | PASS | PASS |
| `xtm2/in/variant-resourceref-relative.xtm` | PASS | PASS |
| `xtm2/in/variant-resourceref.xtm` | PASS | PASS |
| `xtm2/in/variant-scope-duplicate.xtm` | PASS | PASS |
| `xtm2/in/variant-scope-multiple.xtm` | PASS | PASS |
| `xtm2/in/variant.xtm` | PASS | PASS |
| `xtm2/invalid/id-invalid.xtm` | PASS | PASS |
| `xtm2/invalid/itemid-collision.xtm` | PASS | PASS |
| `xtm2/invalid/no-version.xtm` | PASS | PASS |
| `xtm2/invalid/reifier-collision.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/invalid/reifier-elem-in-2.0.xtm` | PASS | PASS |
| `xtm2/invalid/role-duplicate-reified.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/invalid/subjid-ref-in-2.0.xtm` | PASS | PASS |
| `xtm2/invalid/subjloc-ref-in-2.0.xtm` | PASS | PASS |
| `xtm2/invalid/topic-no-id.xtm` | PASS | PASS |
| `xtm2/invalid/topicref-no-fragment-id.xtm` | NOT-RUN | NOT-RUN |
| `xtm2/invalid/variant-missing-scope-duplicate.xtm` | PASS | PASS |