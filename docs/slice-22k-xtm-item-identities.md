# Slice 22K — XTM Item Identity für Occurrences, Associations und Roles

Die neun beauftragten unveränderten Originalverträge werden über den produktiven
XTM-Reader deserialisiert, nativ geprüft und bytegenau bestanden. Identifier
werden ausschließlich durch die vorhandene TMDM-Operation `add-item-identifier`
zugewiesen. Es entsteht keine neue Identifier- oder Objektverwaltung.

Ausgangscommit und Commit-Parent:
`cc1a0e02803a5705c97fb5457f6e93ad22f8b347`.
Branch: `codex/xtm-slice-22k`. Beim Beginn waren Index und Arbeitsbaum sauber,
Ausgangsbranch `codex/xtm-slice-22j`. Der tatsächlich gespeicherte Harness wies
XTM **98 PASS, 0 FAIL, 26 NOT-RUN** und CTM **262 PASS, 4 FAIL, 7 NOT-RUN** aus.
[initial-state.json](../reports/slice-22k/initial-state.json) enthält die SHA-256
aller 9396 verfolgten Ausgangsdateien.

## Normative Grundlage und Editionsgrenze

**Normativ abgeleitet:** [XTM 2.0 §§4.3.3–4.3.4 und 4.6](https://www.isotopicmaps.org/sam/sam-xtm/)
ordnet den aufgelösten `itemIdentity/@href`-Locator dem durch das Parent-Element
repräsentierten Item zu. Prozentkodierung wird als UTF-8 dekodiert und relativ
zur Document IRI aufgelöst. `itemIdentity*` steht gemäß §§4.15, 4.18–4.19 und
Annex A vor Type, Scope und weiteren Kindern. Die explizite Topic-Merge-Anweisung
in §4.6 ist auf Topics bezogen; für die drei neuen Parent-Typen ersetzt II keine
fachliche Gleichheitsentscheidung.

**Normativ abgeleitet:** [TMDM 2006 §§5.1, 5.6–5.8 und 6.5–6.7](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/)
verbietet gleiche Item-Identifier auf verschiedenen Information Items.
Gleiche Occurrences, Associations oder Roles werden anhand ihrer bestehenden
fachlichen Eigenschaften normalisiert; ihre II-Mengen werden dabei vereinigt.
Identifier sind kein Ersatz für Parent, Type, Scope, Value/Datatype oder Player.
Role-Parent bleibt Teil der Role-Gleichheit. Locatorgleichheit folgt §4.3.

**Geprüfte Editionsgrenze:** Die [korrigierte Onlinefassung von 2008](https://www.isotopicmaps.org/sam/sam-model/)
weist ausdrücklich auf Abweichungen zur ISO-Ausgabe hin. Die
[publizierten Errata](https://www.isotopicmaps.org/sam/errata.html) betreffen den
Default-Name-Type (§7.5) und die Variant-Vereinigung beim Name-Merge (§6.3).
Für die hier verwendeten II-Eindeutigkeits- und Merge-Regeln wurde keine relevante
Editionsabweichung festgestellt. Es werden keine zusätzlichen Anforderungen aus
2008 eingeführt und keine bestehenden TMDM-Regeln geändert.

## Produktive Reader-Operationen

Die einzige Produktionsänderung liegt in `src/xtm/reader.lisp`:

- `validate-source` akzeptiert `itemIdentity*` bei Occurrence, Association und
  Role. Der gemeinsame Locator-/Leaf-Pfad prüft die Quelle. Reihenfolge,
  Kardinalitäten und zulässige Parent-Kontexte bleiben strikt.
- `read-item-identities` verwendet `leaf-href` und `add-item-identifier` für alle
  fünf unterstützten Nicht-Topic-Parent-Typen. Die bisherigen Name-/Variant-
  Schleifen werden damit ohne Semantikänderung wiederverwendet.
- `read-occurrence` erzeugt beziehungsweise normalisiert zuerst das native Item
  und weist ihm anschließend seine Identifier zu.
- `read-association` erzeugt die vollständige native Association, die bereits
  Associations und Roles normalisieren kann. Association-II gehen an den
  kanonischen Parent. Jede Quell-Role wird innerhalb dieses Parents anhand des
  kanonischen Role Type und Player wiedergefunden und erhält dann ihre II.
  XML-Reihenfolge und II entscheiden nicht über die Role-Zuordnung.

Die temporären Listen sind Konstruktorargumente und XML-Quellknoten. TMDM besitzt
weiterhin die alleinige Modellrepräsentation, Normalisierung und Handles.
Identifier-Zuweisung erzeugt keine Topics. SI, SL und II bleiben getrennt.
Keine Änderung an TMDM, CTM, CXTM, XML oder der Map-Item-Identitätssemantik.

## Neun tatsächliche Originalvergleiche

Alle Dateien liegen unverändert unter `vendor/cxtm/xtm2/in/`; die vollständigen
Quellbytes, Texte, SHA-256 und Baselines stehen in
[originals-before.json](../reports/slice-22k/originals-before.json).
Die tatsächlichen Modelle, Handles, Quellkontexte und CXTM-Vergleiche stehen in
[original-contracts.json](../reports/slice-22k/after/original-contracts.json).

| Original | Actual/Baseline Bytes | Item mit II | Erhaltene lokale II |
|---|---:|---|---|
| itemid-occurrence.xtm | 443/443 | Occurrence | `#the-occurrence` |
| occurrence-duplicate-iid.xtm | 443/443 | kanonische Occurrence | `#the-occurrence` |
| itemid-association.xtm | 580/580 | Association | `#the-association` |
| association-duplicate-iid.xtm | 580/580 | kanonische Association | `#the-association` |
| association-duplicate-iid2.xtm | 617/617 | kanonische Association | `#the-association`, `#the-association2` |
| association-duplicate-iid3.xtm | 617/617 | kanonische Association | `#the-association`, `#the-association2` |
| itemid-role.xtm | 573/573 | Role | `#the-role` |
| role-duplicate-iid.xtm | 573/573 | kanonische Role | `#the-role` |
| role-duplicate-iid2.xtm | 573/573 | Role der kanonischen Association | `#the-role` |

Alle neun Ergebnisse sind **PASS**, Condition `null`, erste abweichende Byteposition
`null`. Die vollständigen erzeugten Ausgaben sind unter
[actual/](../reports/slice-22k/after/actual/) gesichert. Keine Ersatzmap und keine
nachträgliche Änderung der CXTM-Ausgaben.

Jeder Originaltest verwendet `topic-maps.xtm:deserialize-octets` und genau einen
qualifizierten Parseraufruf mit den tatsächlichen Original-Octets.
Document IRI ist
`https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/`
plus vollständiger Case-ID. Source Key ist die Case-ID. Erneutes tatsächliches
Deserialisieren mit einem anderen diagnostischen Key liefert identische native
Eigenschaften und CXTM-Bytes. Vor der Registrierung werden II-Eigentümer,
Topiczahlen, Parent, Type, Scope, Value/Datatype, Player, inverse Roles und
kanonische EQ-Referenzen geprüft. Ein Locator gehört jeweils genau einem aktuellen
Item; bloße II-Zuweisung fügt weder Topics noch SI/SL hinzu.

## Native Normalisierung und Konflikte

**Beobachtet:** Gleiche Items mit unterschiedlichen II normalisieren bei allen
drei Itemtypen zu einem Item mit der vollständigen II-Vereinigung. Ein einzelnes
Item unterstützt einen, mehrere und wiederholte II als Menge. Relative,
absolute und prozentkodierte Unicode-IRIs werden über den bestehenden Pfad
aufgelöst.

Die zusätzliche Role-Gegenprobe verwendet zwei äquivalente Associations mit
vertauschter Rollenreihenfolge. II `urn:r1`/`urn:r3` landen ausschließlich bei
Role Type `#r`, Player `#p`; `urn:r2`/`urn:r4` bei `#rr`, `#q`. Die Association
behält `urn:as1` und `urn:as2`. Das prüft gezielt die Metadatenzuordnung nach der
bereits im Konstruktor erfolgten Normalisierung.

Späte SI-, SL- und II-Merges werden getrennt ausgeführt. Zunächst bestehen zwei
Occurrence-Parents, Association Types, Role Types, Players und Scope-Themes.
Nach Identitätszusammenführung bestehen jeweils eine Occurrence, Association und
Role mit zwei erhaltenen II; ihre Referenzen und alten Handles sind kanonisch
auflösbar. Wiederholte CXTM-Kanonisierung verändert weder Modell, Identifier noch
Handles. Die Beobachter filtern private TMDM-Preflight-Graphs anhand der tatsächlichen
zurückgegebenen Map und ändern keine Modelloperation.

Die Gegenproben enthalten Kollisionen mit dem Map-Item, zwischen unterschiedlichen
Occurrences/Associations/Roles, über Itemtypgrenzen, bei gleichen Role-Signaturen
in verschiedenen Parents und nach bereits erfolgtem Topic-Merging. Sie erreichen
jeweils **`ITEM-IDENTIFIER-ERROR / duplicate-item-identifier`**. Die gescheiterte
native Zuweisung verändert ihren vor dem Aufruf beobachteten Graph nicht. Items
werden nicht allein wegen gleicher II zusammengeführt.

Die neue reale XTM-Mergemap-Gegenprobe importiert Occurrence-, Association- und
Role-II über die vorhandene Importoperation. Native Referenzen, Identifier und
Quellmap bleiben korrekt; Root-Map-Metadaten werden nicht übernommen. Eine
kollidierende Child-Association erreicht **`XTM-RESOURCE-ERROR /
mergemap-import-failure` bei 1:131**, mit ursprünglicher nativer
`ITEM-IDENTIFIER-ERROR / duplicate-item-identifier` als Cause.

## Tatsächliche Fehlerdiagnosen und Evidenzgrenzen

Der aktuelle [XTM-Bericht](../reports/slice-22k/after/xtm.json) enthält unter
`itemIdentityControls` **46** strukturierte Beobachtungen: 16 positive
Normalisierungs-/Identitätsproben und 30 Fehler-/Grenzbeobachtungen. Der zusätzliche
positive Import steht in `mergemapControls`. Jede neue negative Quelle wird durch
den produktiven Reader verarbeitet; ein beliebiger Fehler genügt nie.

Repräsentative tatsächlich beobachtete Conditions; Positionseinheit ist
approximative SAX-Zeile/-Spalte, kein Byteoffset:

| Ursache | Condition / Code | Position |
|---|---|---|
| Occurrence-II `%ZZ` | XTM-REJECTION / invalid-percent-escape | 1:115 |
| Association-II `%C3%28` | XTM-REJECTION / invalid-percent-utf8 | 1:105 |
| Role-II `a#b#c` | XTM-REJECTION / invalid-iri | 1:144 |
| Occurrence-II nach Type | XTM-REJECTION / element-order | 1:151 |
| Association-II nach Type | XTM-REJECTION / element-order | 1:138 |
| Role-II nach Type | XTM-REJECTION / element-order | 1:178 |
| II innerhalb von Type | XTM-REJECTION / unexpected-element | 1:110 |
| II innerhalb von Scope | XTM-REJECTION / unexpected-element | 1:145 |
| Nichtleeres itemIdentity | XTM-REJECTION / unexpected-child | 1:103 |
| Fehlendes href | XTM-REJECTION / missing-attribute | 1:91 |
| Fehlerhafte XML-Struktur | XTM-XML-ERROR / xml-not-well-formed | 1:117 |
| Occurrence-Reification | XTM-UNSUPPORTED / unsupported-construct | 1:102 |
| Unterschiedliche Items mit gleicher II | ITEM-IDENTIFIER-ERROR / duplicate-item-identifier | native Slots nicht vorhanden |

XTM-/XML-Conditions behalten Document IRI, Source Key und verfügbare SAX-Position;
XML- und Ressourcenfehler behalten ihre ursprüngliche Cause. Native TMDM-
Identifier-Conditions werden wie bisher unverändert propagiert. Sie besitzen
selbst keine Source-/Positionsslots und werden nicht als positionsbehaftete
XTM-Rejections ausgegeben. Die Evidenz hält dafür die tatsächlich ausgeführte
Quelle, Document IRI, Source Key, native Klasse/Code und atomare Zuweisungsprüfung
separat fest. Positionen werden nicht erfunden.

**Explizit ausgeschlossen:** `occurrence-duplicate-iid2.xtm` enthält zwei
`topic`-Elemente mit XML-ID `topic`. Nach Wegfall des früheren Unsupported bei
der ersten Occurrence erreicht die bestehende Source-Prüfung die zweite ID:
**XTM-REJECTION / duplicate-id bei 11:21**. Die XML-ID-Soundness wird nicht geändert.
Die weitergehende normative Qualifikation und jede Registrierung dieses positiven
Korpusvertrags bleiben außerhalb des Slices; sein registrierter Status bleibt
**NOT-RUN**. Auch Reification, `xsd:anyType`, zyklische Mergemap-Semantik,
`mergemap-itemid` und XTM 2.1 bleiben ausgeschlossen.

## Erhaltene Kontrollen und Originaldiagnosen

[retargetings.json](../reports/slice-22k/retargetings.json) dokumentiert drei
bestehende Unsupported-Kontrollen mit exakten Quellzeilen vor/nach der Anpassung:
`item-identity` im Occurrence-Test sowie `association-II` und `role-II` im
Association-Test. Sie behalten ihre ursprünglichen II und vollständigen übrigen
Quellen, erhalten jeweils einen Reifier am betreffenden Parent und prüfen damit
weiter eine bekannte, ausgeschlossene Metadatenfähigkeit. Erwartete Klasse,
Code, Checklabels und Kontextprüfungen bleiben erhalten. Neue positive II-Tests
prüfen zusätzlich die nun erfüllten Sprachfähigkeiten.

Alle **113 bestehenden Executor-Fehlerkontrollen** verwenden denselben unveränderten
Fault-Treiber. Ihre Case Records, Outcomes und Checklisten stimmen mit Slice 22J
überein. Absichtlich gescheiterte ASDF-Läufe werden nicht als Original-PASS gezählt.

[all-124-original-statuses.json](../reports/slice-22k/after/all-124-original-statuses.json)
und [diagnostic-changes.json](../reports/slice-22k/after/diagnostic-changes.json)
zeigen: **10 Diagnosedifferenzen**, davon neun neue erfolgreiche Originalvergleiche
und die beschriebene ausgeschlossene Duplicate-ID-Diagnose. **114 Diagnosen**
bleiben identisch. Sämtliche bisherigen **98 registrierten XTM-PASS** bleiben
unverändert; nur die neun beauftragten Originale wechseln zu PASS.

## Vollständige Offline-Abnahme

[execution.json](../reports/slice-22k/after/execution.json) und
[runs.json](../reports/slice-22k/after/runs.json) sichern alle **119 Prozesse** mit
Kommandos, Laufzeiten, erwarteten/tatsächlichen Exitcodes und SHA-256.
Der unveränderte Collector `scripts/validate-slice-22d.py::collect` führt die
bestehende Testarchitektur aus; `scripts/validate-slice-22k.py` auditierte die
Ergebnisse. `--audit-only` prüft gespeicherte Ausführung und startet keine Tests.

SBCL **2.5.4**, frische Prozesse ohne System-/Benutzerinitialisierung. Alle
Test-Kindprozesse laufen mit Netzwerksperre und Schreibsperre für Repository und
HyperDoc. Die Abhängigkeiten stammen ausschließlich aus vorhandenen lokalen Pins.

- **12100** bisherige Kernchecks und sämtliche bisherigen Slice-20-/22-Stufen.
- **3339 XTM-Checks**, davon **3130** bisherige Labels erhalten und **209** neue.
- **146** XML-Qualifikationschecks.
- CTM/XTM-Mergemap mit **217** Checks und sämtliche bisherigen XTM-Mergemap-Tests.
- **501** unveränderte Äquivalenzchecks über **28** tatsächliche Reader-Paare.
- **113/113** erwartete ASDF-Ablehnungen der Executor-Fehlerkontrollen.
- **2 Python-Tests** und **16294 NFC-Oracle-Vergleiche**.
- **49 Nicht-XTM-Berichte byteidentisch**, einschließlich des Äquivalenzberichts.

Tatsächlich registrierter Abschlussstand:

| Korpus | PASS | FAIL | NOT-RUN |
|---|---:|---:|---:|
| XTM 2.0 | 107 | 0 | 17 |
| CTM | 262 | 4 | 7 |

Die vier bekannten CTM-DateTime-/Include-FAILs bleiben sichtbar und unverändert.
[integrity.json](../reports/slice-22k/after/integrity.json) belegt Größe und SHA-256
aller **2006 gepinnten Korpusdateien** sowie **7100 historischen Reportdateien**.
Originalquellen, Baselines und historische Berichte bleiben unverändert.
Keine HyperDoc-/Fremdrepository-Änderungen, Downloads, Pushes, Deployments oder
Änderungen an langlebigen Lisp-Images. Der Slice endet mit dem lokalen Commit.
