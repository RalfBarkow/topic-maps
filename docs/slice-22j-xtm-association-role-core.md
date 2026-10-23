# Slice 22J — XTM 2.0 Association-/Role-Kern

Der produktive XTM-Reader verarbeitet explizite Associations und Roles über die
bestehende native TMDM-API. Die neun beauftragten positiven Originale bestehen
bytegenau; der negative Originalvertrag erreicht seine beabsichtigte
`topicRef`-Ablehnung. Es entstehen zehn zusätzliche registrierte Original-PASS.

Ausgangscommit und Commit-Parent dieses Slices:
`f27f0af85e49cf25948bc4f2325fb02e77698de9`.
Arbeitsbranch: `codex/xtm-slice-22j`.
Beim Beginn waren Index und Arbeitsbaum sauber; der Ausgangsbranch war
`codex/xtm-slice-22h`. Der vollständige Hashbestand der 9086 verfolgten Dateien
steht in [initial-state.json](../reports/slice-22j/initial-state.json).

## Normative Herleitung und Editionsgrenze

**Aus der Norm abgeleitet:** [XTM 2.0 §§4.13–4.14, 4.18–4.20 und Annex A](https://www.isotopicmaps.org/sam/sam-xtm/)
fordert `association { reifiable, type, scope?, role+ }` und
`role { reifiable, type, topicRef }`. Scope ist eine Topic-Menge. Type und Player
verwenden die gemeinsame Referenzauflösung; `topicRef` benötigt ein
Shorthand-Fragment. Ein vorhandener SI-/II-Treffer wird wiederverwendet; nur bei
fehlendem Treffer entsteht ein Topic mit dem Referenzlocator als II. Relative
IRIs folgen §4.3. Importierte Inhalte folgen dem vorhandenen §4.21-Pfad.

**Aus der Norm abgeleitet:** [TMDM 2006 §§5.7–5.8, 6.2 und 6.6–6.7](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/)
legt Association-Parent, Type, Scope und nichtleere Role-Menge sowie Role-Parent,
Type und Player fest. Association-Gleichheit berücksichtigt Type, Scope und
Role-Menge; Role-Gleichheit berücksichtigt auch ihren Parent. Deshalb dürfen
ähnliche Roles verschiedener Associations allein keinen Association-Merge
verursachen. Identitätsmerges müssen die Referenzen aktualisieren.

**Geprüfte Editionsgrenze:** Die [online korrigierte Fassung vom 2008-06-03](https://www.isotopicmaps.org/sam/sam-model/)
kennzeichnet sich ausdrücklich als vom ISO-Text abweichend. Die
[veröffentlichten Errata](https://www.isotopicmaps.org/sam/errata.html) nennen den
Default-Name-Type (§7.5) und die Variant-Vereinigung beim Name-Merge (§6.3).
Die oben verwendeten Association-/Role-Regeln unterscheiden sich in den
verglichenen datierten Abschnitten nicht. Dieser Slice führt daraus keine neue
Modellanforderung ab und ändert weder Core-Identifier noch Name-/Variant-Regeln.

**Aus der Norm abgeleitet:** [CXTM §§3.9–3.10 und 4.10–4.11](https://www.isotopicmaps.org/cxtm/cxtm.html)
ordnet Associations und Roles kanonisch. Rollenreihenfolge im XTM-Quelltext
ist kein TMDM-Gleichheitsmerkmal.

## Produktiver Pfad

`src/xtm/reader.lisp` enthält die einzige Produktionsänderung:

- `validate-source` prüft Association-/Role-Kontext, Namespace, Attribute,
  Reihenfolge und Kardinalitäten vor dem Modellaufbau. Genau ein Type, optional
  ein Scope und mindestens eine Role; jede Role hat genau einen Type und Player.
- `read-association` löst Type, Scope und Role-Referenzen mit dem bestehenden
  `reference-iri`/`find-reference-topic` auf und ruft einmal `make-association`
  mit den vollständigen nativen Role-Argumenten auf.
- `deserialize-document` dispatcht explizite Associations getrennt von Topics.

TMDM besitzt weiterhin allein Erzeugung, Gleichheit, Normalisierung,
Forwarding-Handles und inverse `rolesPlayed`-Beziehungen. Es gibt keine zweite
Objektverwaltung und keine Änderung an TMDM, CTM, CXTM oder XML.
Die bestehende `instanceOf`-Verarbeitung nutzt dieselbe native Association-API.

Association-/Role-II und -Reification bleiben ausdrücklich `XTM-UNSUPPORTED`.
Die Source-Prüfung beansprucht weiterhin keine vollständige Schemaqualifikation
der ausgeschlossenen Untergrammatiken. Occurrence-Metadaten, `xsd:anyType`,
zyklische Mergemap-Semantik und XTM 2.1 bleiben ausgeschlossen.

## Zehn ausgeführte Originalverträge

Alle Eingaben sind unveränderte Originalbytes unter `vendor/cxtm/xtm2/`.
[originals-before.json](../reports/slice-22j/originals-before.json) enthält
Quelltext, vollständige Hexbytes, SHA-256 und Baselines.
[original-contracts.json](../reports/slice-22j/after/original-contracts.json)
enthält die tatsächlichen Modellbeobachtungen und Vergleiche;
[actual/](../reports/slice-22j/after/actual/) die vollständigen erzeugten CXTM-Dateien.

| Original unter `in/` | Actual/Baseline Bytes | Native Associations/Roles | Ergebnis |
|---|---:|---:|---|
| association.xtm | 507/507 | 1/1 | PASS |
| association-binary.xtm | 833/833 | 1/2 | PASS |
| association-binary-duplicate.xtm | 833/833 | 1/2 | PASS |
| association-ternary.xtm | 1157/1157 | 1/3 | PASS |
| association-scope.xtm | 991/991 | 1/2 | PASS |
| association-duplicate-role.xtm | 1157/1157 | 1/3 | PASS |
| association-instanceof-duplicate.xtm | 1167/1167 | 1/2 | PASS |
| association-instanceof-scope.xtm | 1320/1320 | 1/2 | PASS |
| merge-itemid-with-association.xtm | 904/904 | 1/2 | PASS |

Bei allen neun Vergleichen ist die erste abweichende Byteposition `null`.
Vor der PASS-Registrierung werden native Eigenschaften, kanonische interne
EQ-Referenzen, ursprüngliche Parser-Octets, auflösbare alte Handles, reine
wiederholte CXTM-Kanonisierung und Source-Key-Unabhängigkeit geprüft.

Der negative Vertrag `invalid/topicref-no-fragment-id.xtm` ist XML-wohlgeformt,
verwendet im Association-Scope aber `href="scopingtopic"` ohne Fragment.
Beobachtet: `XTM-REJECTION`, Code `invalid-topic-ref`, Detail
`topicRef requires an XPointer shorthand fragment.`, approximative SAX-Position
**7:38**, Cause `null`. Document IRI und Source Key entsprechen dem Original.
Die beabsichtigte Ablehnung ist erreicht; kein vorgelagertes Unsupported.
Der bestehende negative Harness verwendet dafür seinen historischen generischen
Outcome-Token `ctm-rejection`; die Ausführung erfolgte tatsächlich durch XTM.

Document-IRI-Konvention für jedes Original:
`https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/`
plus vollständiger Case-ID. Der Source Key ist die Case-ID; eine erneute
Deserialisierung mit anderem diagnostischem Key erzeugt denselben Modellzustand
und dieselben CXTM-Bytes. Document-lokale II werden regulär kanonisiert, nicht
nachträglich entfernt oder ersetzt.

## Native Normalisierung und Gegenproben

**Beobachtet:** Vor-/Nach-Normalisierung gezählte native Items:

- Doppelte binäre Associations: 2 Associations/4 Roles werden zu 1/2.
- `association-duplicate-role`: 1/4 wird zu 1/3.
- `association-instanceof-duplicate`: explizite und implizite Association bleiben
  zunächst 2/4; spätere Core-SI-Definitionen normalisieren zu 1/2.
- Item-Identifier-Merge des Originalplayers: beide Topic-IDs und
  `http://example.org/#topic` bleiben am kanonischen Topic; Associations 2/4 → 1/2.
- Zusätzliche späte SI-, SL- und II-Merges von Type, Role Type, Player und Theme:
  jeweils 2/2 → 1/1. Zusammenfall zweier Players innerhalb einer Association:
  1/2 → 1/1. Alle tatsächlich gehaltenen alten Handles bleiben auflösbar.
- Vertauschte Rollenreihenfolge normalisiert zu 1/2. Abweichende Association
  Types, Players, Role Types oder Scopes bleiben jeweils 2/4; unterschiedliche
  Arity bleibt 2/3. Rollen gleicher Signatur in verschiedenen Parents verursachen
  damit keine falsche Zusammenführung.

Der passive Testbeobachter erfasst `normalize-associations` pro tatsächlicher
Map. Private Schattenmaps der bestehenden atomaren Core-Preflights sind eigene
Graphs und zählen nicht als Handles des Reader-Ergebnisses. Ein anfänglicher
Beobachter vermischte diese Graphs; korrigiert wurde ausschließlich die
Beobachtung, nicht das Modell. Lokale Klammer-/Fixture-Korrekturen vor dem
Abnahmelauf zählen nicht als erfolgreiche Tests.

46 neue strukturierte Kontrollbeobachtungen stehen in `associationControls` des
[aktuellen XTM-Berichts](../reports/slice-22j/after/xtm.json): Gleichheit,
Forward References, SI-Treffer ohne zusätzliche II, absolute/relative Referenzen,
Scope-Mengen, späte Merges, Syntaxfehler, XML-Fehler und ausgeschlossene Features.
Der reale native Core-Identitätskonflikt bleibt `CORE-SUBJECT-ERROR` mit
`core-subject-conflict`. Wie bisher besitzt diese native Condition selbst keine
Source-Key-/Document-IRI-/Positionsslots; die Evidenz hält ihre konkrete Quelle
und Klasse separat fest. XTM-/XML-Conditions erhalten Kontext und SAX-Position;
XML-Fehler behalten ihre ursprüngliche Cause.

Der zusätzliche verschachtelte Import läuft ohne manuelle Ersatzmap:
Root → `mid.xtm` → `leaf.xtm`; jede Ressource durchläuft den qualifizierten
XML-Parser mit eigener Document IRI und rein diagnostischem Source Key.
Native Association-/Role-Objekte werden durch `import-map-content` übertragen;
SI-Merging des Players, Scope/Type/Parent und inverse Roles bleiben kanonisch.
Die Resolve-Handles beziehen sich bei jedem Schritt auf dessen jeweilige Zielmap.
Beide Quellmaps und ihre CXTM bleiben unverändert. Der Kind-Map-II wird nicht
übernommen. Exakte Resolverargumente stehen in `mergemapControls`.

## Erhaltene Prüfzwecke und Diagnosen

[retargetings.json](../reports/slice-22j/retargetings.json) dokumentiert die zwei
bestehenden Unsupported-Quellen vollständig vor/nach der Anpassung. Sie behalten
Label, Klasse, Code und Kontextprüfungen; nur ein Association-Reifier macht die
bisher einfache, jetzt unterstützte Quelle wieder zu einer tatsächlich
außerhalb des Slices liegenden Fähigkeit. Die bestehende Reification-Kontrolle
benötigt keine Quelländerung, erhält aber die präzisere Diagnose.

Das bestehende Äquivalenz-Gap `explicit-association` verwendet unveränderte
CTM-/XTM-Quellen und läuft nun durch `run-pair`: native TMDM-Eigenschaften gleich,
interne EQ-Prüfungen bestanden, CXTM **493/493 Bytes**, erste Differenz `null`.
Alle bisherigen 27 Paare, drei Kontraste und zwei weiteren Gaps bleiben erhalten.
Nun 28 tatsächliche Paare, 501 Checks; daraus folgt kein weiterer Original-PASS.

[all-124-original-statuses.json](../reports/slice-22j/after/all-124-original-statuses.json)
und [diagnostic-changes.json](../reports/slice-22j/after/diagnostic-changes.json)
vergleichen sämtliche Originale: **28 Diagnosedifferenzen**, davon zehn
beauftragte Ergebnisse und 18 präzisere Unsupported-Grenzen für Association-/Role-II
oder -Reification. Die übrigen **96 Diagnosen** bleiben identisch. Alle bisherigen
**88 registrierten PASS** bleiben erhalten; nur die zehn beauftragten Fälle
wechseln registriert von NOT-RUN zu PASS. Insbesondere bleiben `mergemap-itemid`
und `mergemap-loop` unverändert offen.

## Vollständige Offline-Abnahme

[execution.json](../reports/slice-22j/after/execution.json) und
[runs.json](../reports/slice-22j/after/runs.json) sichern alle 119 Prozesse mit
Befehlen, Laufzeiten, Exitcodes, Source-/Log-/Report-Hashes. Bestehender Collector:
`scripts/validate-slice-22d.py::collect`; Audit: `scripts/validate-slice-22j.py`.
SBCL **2.5.4**, frische Prozesse, ohne System-/Benutzerinitialisierung;
Kindprozesse mit gesperrtem Netzwerk und Schreibsperre für Repository/HyperDoc.
Abhängigkeiten ausschließlich aus vorhandenen lokalen Pins.

- 12100 bisherige Kernchecks und sämtliche CTM-/Slice-20-Stufen erhalten.
- XTM: **3130 Checks**, davon 2965 bisherige Labels erhalten und 165 neue.
- XML-Qualifikation: **146 PASS**.
- CTM/XTM-Mergemap: **217 Checks**; bestehende XTM-Mergemap- und
  Occurrence-Normalisierungstests erhalten.
- CTM/XTM-Äquivalenz: **501 Checks**, **28 tatsächliche Reader-Paare**.
- **113/113 Executor-Fehlerkontrollen** erreichen ihre erwartete ASDF-Ablehnung;
  Case Records, Outcomes und Kontrollchecks bleiben gleich. Eine absichtliche
  Fault-Ausführung wird niemals als neuer positiver Originalvergleich gezählt.
- Python: **2 Tests**; NFC-Oracle: **16294 Vergleiche**.
- 48 Nicht-XTM-Berichte bleiben byteidentisch; der zusätzliche Äquivalenzbericht
  ändert das nun erfüllte Association-Gap und dessen Prüfungen sowie die präzisere
  Unsupported-Meldung des unverändert ausgeschlossenen Reification-Gaps.

Tatsächlich registrierter Abschlussstand:

| Korpus | PASS | FAIL | NOT-RUN |
|---|---:|---:|---:|
| XTM 2.0 | 98 | 0 | 26 |
| CTM | 262 | 4 | 7 |

Die vier bekannten CTM-DateTime-/Include-FAILs bleiben sichtbar und unverändert.
[integrity.json](../reports/slice-22j/after/integrity.json) bestätigt Größe/SHA-256
aller **2006 gepinnten Korpusdateien**, **6793 historischen Reportdateien** und
sämtlicher geschützter Ausgangsdateien. Originale, Baselines und historische
Berichte werden nicht geändert. Kein Download, Push, Deployment oder Zugriff auf
langlebige Lisp-Images. Der Slice endet mit dem lokalen Commit.
