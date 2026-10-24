# Slice 22P — XTM-2.0-Normabdeckung nach 22O

Stand: **24. Oktober 2026** (Europe/Zurich). Basis und vorgesehener Parent:
`85dca09c41c7d4a8ecea00cc2b474f74b2dbe6fa`.
Ausgangsbranch `codex/xtm-slice-22o`, Dokumentationsbranch
`codex/xtm-slice-22p`. Zu Beginn waren Index und Arbeitsbaum sauber.

**Ergebnis:** Die vorhandenen Unterlagen reichen für eine begründete Priorität
bereits aus. Die Grundkonstrukte sind in der aktuellen Implementierung belegt;
die ausdrücklich fehlende anyType/XML-Verarbeitung und ihr noch nicht
qualifizierter C14N-Pfad sind die deutlichste konkrete Austauschlücke. XML-Profil,
Editionsnachweis, vollständige Locator-Qualifikation und Zyklussemantik sind davon
getrennt. Die drei Korpus-Dispositionen aus 22O werden nicht neu aufgerollt.

Dieser Slice ergänzt ausschließlich diesen Bericht. Er führt keine Reader-,
ASDF-, Python-Test-, NFC- oder Regressionsläufe aus. Aktuell gelesen werden
Quellen, vorhandene Normreferenzen und gespeicherte Evidenz. Historische
Testergebnisse werden per Hash an den unveränderten Quellstand gebunden;
sie werden nicht als neue Ausführung ausgegeben. Die Matrix ist kein neuer
Case-Katalog und führt keine Konformitätsregistrierung ein.

## Normbasis und Nachweisgrenze

Maßgeblich bleiben ISO/IEC 13250-3:2007 (XTM 2.0), ISO/IEC 13250-2:2006
(TMDM) und für Modellvergleiche die vereinbarte CXTM-Ausgabe 2009.

- [XTM-Referenztext vom 2006-06-19](https://www.isotopicmaps.org/sam/sam-xtm/):
  §§1–5 und normativer Anhang A. Die Einleitung erklärt Publikationsgleichheit;
  der Dokumentkopf nennt FDIS. Keine stille Umstellung auf XTM 2.1 oder 2013.
- [TMDM vom 2006-06-18](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/):
  insbesondere §§4.2–4.4, 5.1–5.8, 6.1–6.7 und 7.2/7.5. Die korrigierte
  2008-Fassung ersetzt die vereinbarte Ausgabe nicht automatisch.
- XTM §2 referenziert [XML 1.0 Third Edition, 2004-02-04](https://www.w3.org/TR/2004/REC-xml-20040204/),
  Namespaces 1999, Infoset 2004, XPointer 2003 sowie RFC 3986/3987.
  Für eingebettetes XML gilt [Canonical XML 1.0, 2001-03-15](https://www.w3.org/TR/2001/REC-xml-c14n-20010315),
  insbesondere §§2.1–2.4; C14N 1.1/2.0 sind kein Ersatz.
- [22A-Normreview](../reports/slice-22a/normative-review.json),
  [22C-Quellenreview](../reports/slice-22c/source-review.json) und
  [22C-Editionsentscheidungen](slice-22c-normative-decisions.md) werden übernommen.
  **Der unabhängige Abgleich mit den offiziellen ISO-Ausgaben und anwendbaren
  Berichtigungen bleibt ausstehend.** Öffentliche Referenztexte, Katalogangaben
  und historische Baselines ersetzen diesen Nachweis nicht.

Die Matrix ordnet vorhandene Implementierung und Evidenz konkreten Klauseln zu.
Sie bescheinigt keine lückenlose Erfüllung sämtlicher Eingaben einer Klausel.
TMDM hat keine eigene Processor-Conformance-Klausel; XTM §5 verlangt eine
separate Gesamtbeurteilung. Korpus-PASS, native Modellprüfungen und eine
Klauselabnahme sind verschiedene Nachweise.

## Klassifikation

| Kürzel | Bedeutung |
|---|---|
| **N** | Implementiert und im ausdrücklich bezeichneten Umfang durch tatsächlich ausgeführte gespeicherte Tests nachgewiesen. Kein pauschaler Vollständigkeitsbeweis. |
| **T** | Implementiert, aber für den bezeichneten weitergehenden Anspruch nicht hinreichend getestet/qualifiziert. Kein ohne Gegenprobe behaupteter Reader-Fehler. |
| **U** | Ausdrücklich nicht unterstützt; vorhandene Zurückweisung belegt die Grenze, nicht die Normerfüllung der gültigen Fähigkeit. |
| **F** | Benannte Implementierungsoperation fehlt. Kann die technische Ursache eines U-Eintrags sein. |
| **O** | Normative, editionsbezogene oder noch nicht ausdrücklich abgenommene Profilfrage offen. |

Mehrere Kürzel können verschiedene Aspekte derselben Anforderung betreffen.
Die Kürzel sind Dokumentationskategorien, keine Änderungen an PASS, FAIL,
NOT-RUN oder UNSUPPORTED des Harness.

## Leseschlüssel für Source und Evidenz

Source-Kürzel nennen die aktuellen Dateien; Zahlen in der Matrix sind deren
Zeilen im Ausgangscommit. Funktionsnamen bleiben zusätzlich angegeben.

| Kürzel | Aktuelle Source |
|---|---|
| R | [XTM-Reader](../src/xtm/reader.lisp) |
| I | [IRI-Verarbeitung](../src/xtm/iri.lisp) |
| X | [qualifizierte XML-Bytegrenze](../src/xml/parser.lisp) |
| P | [öffentliche XTM-API/Conditions](../src/xtm/package.lisp) |
| M | [Topic-/Name-Merging und Scope](../src/tmdm/merging.lisp) |
| II | [Item Identifier](../src/tmdm/item-identifiers.lisp) |
| V | [Variants](../src/tmdm/variants.lisp) |
| OC | [Occurrences](../src/tmdm/occurrences.lisp) |
| AS | [Associations/Roles](../src/tmdm/associations.lisp) |
| RF | [native Reification](../src/tmdm/reification.lisp) |
| IM | [quellmap-erhaltender Inhaltsimport](../src/tmdm/import.lisp) |
| C | [CXTM-Kanonisierung](../src/cxtm/canonicalizer.lisp) |

Die folgenden E-Nachweise beziehen sich auf den gespeicherten 22N-Lauf,
insbesondere [xtm.json](../reports/slice-22n/after/xtm.json).
Feldnamen sind vorhandene JSON-Schlüssel, keine neu berechneten Original-PASS.

| Evidenz | Ausführung und dauerhafte Testsource |
|---|---|
| E1 | `checks`, `cases`, Identitäts-/IRI-/Encoding-Kontrollen; [xtm-identity](../tests/xtm-identity.lisp), insbesondere Zeilen 283–454. |
| E2 | `nameOriginals`, `nameControls`, `scopeOriginals`, `scopeControls`; [Names](../tests/xtm-names.lisp), [Name Scope](../tests/xtm-name-scopes.lisp). |
| E3 | `variantOriginals`, `variantNegativeOriginals`, `variantControls`; [Variants](../tests/xtm-variants.lisp), dazu `variantResourceRefControls`/[resourceRef](../tests/xtm-variant-resourcerefs.lisp) und `variantResourceDataURIControls`/[anyURI](../tests/xtm-variant-uri-data.lisp). |
| E4 | `nameItemIdentityControls`, `variantItemIdentityControls`, `itemIdentityControls`; [Name-II](../tests/xtm-name-item-identities.lisp), [Variant-II](../tests/xtm-variant-item-identities.lisp), [Occurrence-/Association-/Role-II](../tests/xtm-item-identities.lisp). |
| E5 | `mapReifierControls`, `nameReifierControls`, `variantReifierControls`, `occurrenceReifierNative/Controls`, `associationReifierNative/Controls`, `roleReifierNative/Controls`; vorhandene [Map](../tests/xtm-map-reification.lisp)-, [Name](../tests/xtm-name-reification.lisp)-, [Variant](../tests/xtm-variant-reification.lisp)-, [Occurrence](../tests/xtm-occurrence-reification.lisp)-, [Association](../tests/xtm-association-reification.lisp)- und [Role](../tests/xtm-role-reification.lisp)-Tests. |
| E6 | `datatypeOriginals`, `datatypeControls` (37 Kontrolldatensätze), native Vorprüfung und Wert-/Datentyp-Erhaltung; [resource datatypes](../tests/xtm-resource-datatypes.lisp). |
| E7 | `occurrenceOriginals`, `occurrenceControls` (46 Kontrollen); [Occurrences](../tests/xtm-occurrences.lisp). |
| E8 | `associationOriginals`, `associationControls` (46 Kontrollen); [Associations/Roles](../tests/xtm-associations.lisp). |
| E9 | `mergemapControls` (54 Kontrollen), `mergemapOriginalObservations`, `registeredMergemapOriginals`; [mergeMap](../tests/xtm-mergemap.lisp), [registrierte Originale](../tests/xtm-mergemap-originals.lisp). |
| E10 | [XML-Qualifikationslog](../reports/slice-22n/after/xml.log), 146 Checks; [Parser-Proben](../tests/cxml-probe.lisp), [Encoding-Regressionsproben](../tests/cxml-encoding-regressions.lisp), qualifizierte [19D0B-Patches](slice-19d0b-cxml-encoding.md). |
| E11 | [CTM/XTM-Äquivalenzreport](../reports/slice-22n/after/retained/xtm-mergemap.equivalence.json), 30 tatsächlich gelesene Paare/529 Checks/3 Kontraste; [Änderungsnachweis](../reports/slice-22n/after/equivalence-progress.json), [Testsource](../tests/ctm-xtm-equivalence.lisp). |
| E12 | [22N-Ausführung](../reports/slice-22n/after/execution.json), [Prozess-/Reporthashes](../reports/slice-22n/after/runs.json): Kern 12100, XTM 3743, Executor-Fehlerkontrollen 113, XML 146; regulärer ASDF-Aufruf über [topic-maps.asd](../topic-maps.asd) und `run-tests` in E1. |
| E13 | [22A-Profilproben](../reports/slice-22a/investigation/profile-probes.json), [22D-anyType-Lücke](../reports/slice-22d/anytype-capability-gap.json) und aktuelle U-Kontrollen in E6/E7/E5. Alte Proben sind historische Befunde; aktuelle Fähigkeiten werden nicht aus dem alten Unsupported-Stand abgeleitet. |

N bedeutet deshalb mehr als bloße Dateiexistenz: Die Testdateien sind serielle
ASDF-Komponenten; `tests/xtm-identity.lisp:509` ruft die Funktionen wirklich auf.
E12 belegt den ausgeführten Stand, E1–E11 die fachlichen Prüfungen.
Keine nachträglich handgebaute Map ersetzt einen Original-Reader-Vertrag.

## XTM-Abdeckungsmatrix

Die Anforderungsspalte bezeichnet Klausel und Gegenstand. Die Implementierungs-
und Evidenzspalten beschreiben konkrete lokale Operationen, keinen Ersatztext
für die Norm. Globale Editionsgrenze O gilt für alle Zeilen zusätzlich.

| ID | XTM-Anforderung / Klausel | Status | Tatsächliche Reader-/Modelloperation | Vorhandene Evidenz / verbleibende Grenze |
|---|---|---|---|---|
| X01 | §§1,4.1,4.3.1,4.4: Namespace/Version | N | R:59 `check-namespace`, R:86 `validate-source`; Version 2.0, expandierte Namen. | E1: Prefixäquivalenz, falsche Namespace/Version, fehlende Attribute; E10 XML-Namespace-Proben. |
| X02 | §4.2: Document IRI und Quellidentität | N | I:120 `require-document-iri`, R:476 `deserialize-octets`; Source Key diagnostisch. | E1/E6/E9: gleiche Document IRI bei anderem Source Key, getrennte lokale II, Kind-IRI. Vollständige IRI-Syntax: G4. |
| X03 | §4.2: Ablauf und neue Items | N/T | R:490 `deserialize-document`, R:421 `read-topic`; native Konstruktoren. Vollständige Associations werden vor Role-Metadaten normalisiert (R:320). | E1/E5/E8/E9: Forward References, spätes Merging, mehrere Role-Reihenfolgen und Reifier-Kaskaden. Kein allgemeiner Beweis jeder Wechselwirkung der verzögerten Metadatenzuweisung; G6. |
| X04 | §§4.3.1,5,Anhang A: Struktur | N/T | R:75 `validate-source`, R:42 `attributes`, R:53 `elements`; Reihenfolge/Kardinalitäten im unterstützten Pfad. | E1–E9: konkrete positive und negative Strukturen. Keine vollständige Schema-Differentialqualifikation aller ausgeschlossenen Untergrammatiken; G5. Kein vorgeschriebener zusätzlicher Schema-Engine-Einsatz abgeleitet. |
| X05 | §4.3.2: Reifier | N | R:291 `read-item-reifier`, II-Lookup; RF:94 `set-item-reifier`; kanonische Handles nach Merging. | E5: alle sechs reifizierbaren Itemtypen, SI-/II-Abgrenzung, inverse EQ-Referenzen, alte Handles, Konflikte. |
| X06 | §§4.3.3–4.3.4: href/IRI | N/T | I:55 `resolve-iri`, I:93 `unescape-reference`, I:129 `validate-decoded-reference`; keine implizite Ressourcenabfrage. | E1/E3/E6/E9: relative/absolute IRIs, Dot-Segmente, Query, Prozent-UTF-8, Negativfälle; vollständige RFC-/IRI-Ablehnungsabdeckung nicht belegt, G4. |
| X07 | §4.4: Map-Item | N | R:490 neue native Map, R:303 Reifier, R:511 Root-II. | E4/E5/E9: Map-II/Reifier, Inhalts-/Map-Metadaten getrennt. |
| X08 | §4.5: Topic und Dokument-ID | N | R:101 ID-Eindeutigkeit/NCName, R:421 `read-topic`; M:192 `intern-topic`. | E1/E4: ID-Collapse, Unicode, doppelte ID, Kategorien, Transitivität; 22O-XML-ID bleibt unverändert. |
| X09 | §4.6: itemIdentity | N | R:314 `read-item-identities`, II:87 `add-item-identifier`; keine zusätzlichen Datentyp-/II-Topics. | E4/E5: Map/Topic/Name/Variant/Occurrence/Association/Role, Identifierunion, Kollisionen. |
| X10 | §4.7: subjectLocator | N | R:421 `read-topic`, M:171 `add-topic-identifier`. | E1/E3/E5/E7/E8: SL getrennt von SI/II, spätes SL-Merging. |
| X11 | §4.8: subjectIdentifier | N | R:421 `read-topic`, M:171; SI-/II-Identitätsregeln im Modell. | E1/E5/E7/E8: SI-Merging und SI-Referenztreffer ohne zusätzliche II. |
| X12 | §4.9: instanceOf | N | R:308 `read-instance-of`, R:305 `core-topic`, AS:50 `make-association`. | E1/E8/E11: native Core-SI, Typ-/Instanzroles, Zusammenfall mit expliziten Associations. |
| X13 | §4.10: name | N | R:378 `read-name`, M:211/236 Name/Default-Name. | E2/E4/E5: Type, Parent, Scope, II/Reifier, normalisierte Namen und Default-Type. |
| X14 | §4.11: value | N | R:269 Textprüfung, R:386 Unicode-Textverkettung. | E2: leere Werte, Whitespace, XML-Escaping, CDATA/Zeichenreferenzen und Zeilenenden. |
| X15 | §4.12: variant | N | R:366 `read-variant`, V:60 `add-variant`; Parent- und expliziter Scope. | E3/E5: Scope-Vererbung, echte Obermenge, Duplikate, Konflikte bei Scope-Kollaps, Handles. XML-Werte ausgenommen: X21/G1. |
| X16 | §4.13: scope | N | R:265 Struktur, Referenzen über R:282; M:45 `canonical-scope`. | E2/E3/E7/E8: Theme-Menge, wiederholte Themes, SI/SL/II-Merges. |
| X17 | §4.14: type | N | R:260 Type-Kardinalität, R:282 `find-reference-topic`; native Type-Handles. | E2/E7/E8: fehlende/mehrfache Types, Referenzen und spätes Merging. |
| X18 | §4.15: occurrence | N | R:404 `read-occurrence`, OC:46 `add-occurrence`; II vor Reifier. | E7/E4/E5: Parent/Type/Scope/Wert/Datatype, Normalisierung, eigene II und Reification. XML-Werte ausgenommen. |
| X19 | §§4.16.1–4.16.2: textuelle resourceData | N | R:246 `validate-source`, R:353 `read-resource-value`; Standardstring oder absolute Datentyp-IRI. | E6/E7: benutzerdefinierter Datentyp, exakter Text/Whitespace, keine Datentyp-Topics; fremde Elemente bei gewöhnlichem Text werden spezifisch abgelehnt. |
| X20 | §4.16.2: anyURI-Wert | N | R:362 vorhandene IRI-Auflösung, Datentyp bleibt anyURI. | E3/E7: relative/absolute Werte und Kind-Document-IRI, keine Ressourcenabfrage. |
| X21 | §§4.16.2–4.16.3: anyType | U | R:255 ausdrückliche `XTM-UNSUPPORTED/resource-data-datatype`-Grenze. | E6/E7/E5 belegen Text und eingebettetes XML als Unsupported; **keine** erfolgreiche anyType-Ausführung. Technische Lücke G1. |
| X22 | §4.16.3: XML-Projektion/Kanonisierung | F/T | R:6–25 Source-Handler verliert QName-/Namespace-Kontext; kein angeschlossener XTM-C14N-Pfad. | E13/22A beschreiben die Lücke. CXML-`:canonical` ist nur als Kandidat identifiziert, nicht für diesen XTM-Node-Set qualifiziert; G1. |
| X23 | §4.17: resourceRef | N | R:245 `leaf-href`, R:357 `read-resource-value`. | E3/E7: absolute/relative Werte, anyURI, keine automatischen Datei-/Netzzugriffe. |
| X24 | §4.18: association | N | R:208 Validierung, R:320 `read-association`, AS:50. | E8/E4/E5/E9: binär/ternär, Type/Scope/Roles, II/Reifier, Duplikate und Import. |
| X25 | §4.19: role | N | R:338 Parent-bezogene Signaturzuordnung; Role-II vor Reifier, AS:7/44 Normalisierung. | E8/E4/E5: Type/Player/Parent, Reihenfolge, inverse rolesPlayed, doppelte und ungleiche Parents. |
| X26 | §4.20: topicRef | N/T | R:69 `reference-iri`, R:282 Lookup über SI/II, bei Miss II-Topic. | E1/E8: Shorthand-Fragment, Forward/SI-Treffer ohne neue II, ungültiger Originalfall. Weitergehende Locator-/Namensqualifikation: G4/G5. |
| X27 | §4.21: nichtzyklischer mergeMap | N | R:436–475 expliziter Resolver/Kindparser, IM:77 `import-map-content`. | E9: relative/absolute IRIs, wiederholte und verschachtelte Imports, Source-Key-Trennung, Ursache, Inhalte und unveränderte Quellmap. Map-II-Konflikt gemäß 22O, keine fehlende Importoperation. |
| X28 | §4.21: zyklischer mergeMap | U/O | R:449 aktiver IRI-Pfad; kein normativer Zyklusabschluss. | E9: `cyclic-mergemap`, ein Kindabruf beim Original; Q-XTM-LOOP aus 22O bleibt offen, G3. |
| X29 | §5: Fehler und Isomorphie | N/T/O | R-Validierung und native Conditions, P-Quelldiagnostik, C:235 reine Modellkanonisierung. | E1–E12: Originalvergleiche, native EQ, 30 Äquivalenzpaare, 113 Executor-Kontrollen; kein Beweis aller XTM-Eingaben und kein Gesamt-Konformitätsabschluss. |
| X30 | §4.2: Serialisierungshinweis | F/O | P exportiert nur `deserialize-octets` und Conditions; kein XTM-Serializer im `src/xtm/`-Inventar. | CTM/XTM→TMDM→CXTM ist kein XTM-Export-/Roundtrip-Test. Keine daraus automatisch abgeleitete unbedingte Reader-Pflicht oder neue Freigabe für einen Serializer; G7. |

Anhang A ist normative Syntaxbasis (X04). Anhänge B/C sind informative alternative
Schemaformen; D/E begründen hier keine weiteren Reader-Operationen. §§1–3 und
§4.3.1 sind durch Scope, Versions-/Namespace- und Definitionszuordnung erfasst.
Die Referenzen aus §2 betreffen zusätzlich die folgenden Profil-/Evidenzgrenzen.

## TMDM-Voraussetzungen und tatsächliche Lückenlage

| Modellbereich / Normstellen | Vorhandene native Operation und Nachweis | Abgrenzung |
|---|---|---|
| Locators, Strings, Datentypen — §§4.2–4.4 | II:12, I; V:60, OC:46; E1/E6/E7 prüfen Wert/Datatype getrennt und Unicode-Erhaltung. | Allgemeine Speicherfähigkeit ist vorhanden. Kein Nachweis eines kanonisierten XML-Werts allein aus der Annahme einer beliebigen absoluten Datentyp-IRI; G1/G4. |
| Topic-Identität — §§5.1,5.3.5,6.2 | M:16/82/125/171/192; E1/E4/E5/E7/E8: SI/SL/II, alte Handles und Referenzumschreibung. | Keine neue XTM-spezifische Identitätsverwaltung erforderlich. XML-ID-Soundness bleibt separate Reader-Prüfung. |
| Mengen, Parent, Type, Scope — §§4.3,5.4–5.8 | M:45/57, V:8/60, OC:14/30, AS:3/20/44; E2/E3/E7/E8. | Echte Variant-Scope-Obermenge und Parent als Teil der Role-/Occurrence-Gleichheit sind belegt. |
| II-Konflikte und Erhaltung — §§5.1,6.3–6.7 | II:64/74/87; E4/E5: alle Itemtypen, Konflikte, normalisierte Identifierunion. | Gleiche II sind kein allgemeiner Ersatz für Gleichheitsregeln von Nicht-Topics. |
| Reification — §§5.3.4–5.3.5,6.2–6.7 | RF:94/116/121; E5 inklusive eigenständiger nativer Gates vor Reader-Integration. | Native Fehler und atomare Zuweisung sind belegt; keine pauschale Transaktionsgarantie jeder Deserialisierung. |
| Map und Import — §§5.2,6.1–6.2 | IM:12/67/77, native Kopie/Preflight, E9. | Importiert Inhalt statt Root-Metadaten. Zyklusabschluss ist keine fehlende TMDM-Merge-Regel. |
| Core-Subjects — §§7.2,7.5 und anwendbare Errata | R:305/308, M:236; E1/E2/E8/E11. | Default-Name-Type-/Name-Merge-Errata bleiben editionsbezogen auszuweisen; kein stiller Wechsel auf die gesamte 2008-Ausgabe. |

**Fazit zur Modellseite:** Für die nächste anyType-Vorprüfung ist keine fehlende
native Modelloperation nachgewiesen. String-/Datentyp-Speicherung und Merging
existieren. Eine spätere positive anyType-Integration muss deren konkrete
Werte, Handles und CXTM-Reinheit trotzdem nachweisen. TMDM wird nicht für eine
unbelegte Reader-/XML-Anforderung umgebaut.

## Verbleibende Lücken und offene Entscheidungen

### G1 — anyType/XML: explizite Reader-Lücke und fehlender qualifizierter Adapter

**Normstelle:** XTM §§4.16.2–4.16.3, TMDM §4.4; C14N 1.0 §§2.1–2.4.
**Source:** R:255/353 und R:6–25; X:19; V:60/OC:46; C:72.
**Status:** U für den öffentlichen Reader, F für dessen XML-Wertbildung,
T für die Eignung der vorhandenen Bibliothek. Ein gültiger XML-Datentyp ist
kein ungültiger Datentyp. Auch reines Text-anyType wird derzeit abgelehnt.

E6 dokumentiert beide Varianten bei ungefähr 1:210; E7 bei 1:189; die
22N-Role-Gegenprobe bei 1:336. Jeweils `XTM-UNSUPPORTED/resource-data-datatype`.
Das beweist korrekte Kennzeichnung einer fehlenden Fähigkeit, keinen positiven
XML-Wertvertrag. Der gepinnte XTM-Teilkorpus besitzt dafür keinen positiven
Originalfall; das beseitigt die Klauselanforderung nicht.

Der Source-Handler verwirft `qname` (R:11), speichert Attribute ohne Prefix und
hält keine Namespace-Mappings. Das reicht für aktuelle expandierte XTM-Namen,
aber nicht als Nachweis eines prefix-/kontexttreuen XML-Kanonisierers. Die
XML-Qualifikationsprobe E10 kann QName beobachten; das beweist nicht, dass der
produktive XTM-Sourcebaum ihn erhält. Eine vorhandene CXML-Sinkoption
`:canonical` ist laut 22A ein Kandidat, kein belegter Adapter für das selektierte
XTM-Node-Set. Diese Operation fehlt im verbundenen Reader-Pfad.

Fehlende positive Evidenz betrifft Element-/Attribut-/Text-Projektion,
Namespacekontext und dessen Filterung, Prefixerhaltung, Attribute/Escaping,
Whitespace sowie Ausschluss von PI/Kommentaren im vorgeschriebenen Teilbaum.
Der Wert muss im Modell als String mit eigenem Datentyp ankommen; ein
nachträgliches CXTM-Umschreiben würde die Lücke nicht schließen.

### G2 — XML-Eingabeprofil: bewusste Einschränkung, keine behauptete Syntaxungültigkeit

**Normstelle:** XTM §§4.2,4.21,5, XML Third Edition §§2.8,4,5.
**Source:** X:10/19–36, R:490–506. **Status:** U/O.
DOCTYPE wird vollständig abgewiesen, externe DTDs/Entities werden gesperrt,
Catalog und DTD-Cache-Fallback unterbunden. Die API nimmt qualifizierte Rohbytes
an; keine alternative Infoset-API ist freigegeben. Eine solche zusätzliche
öffentliche API wird hier auch nicht als eigenständige Normpflicht behauptet.

E10 und E1 belegen die Schutzregeln, einschließlich Resolver-Fallback-Gegenprobe.
22A beobachtet bereits das leere DOCTYPE als `doctype-forbidden`. Auch ein
solches XML-Dokument kann normativ zulässig sein. Eine Betriebsgrenze ist daher
keine allgemeine XTM-Ungültigkeitserklärung. Nichtvalidierende XML-Verarbeitung
an sich ist nicht die Lücke; das uneingeschränkte Ablehnen aller DOCTYPEs ist
als engeres Eingabeprofil auszuweisen. Zu entscheiden bleibt dessen ausdrückliche
Profilabnahme gegenüber einer uneingeschränkten Processor-Aussage. Es folgt
kein Auftrag zu Netzwerkzugriff, DTD-Downloads oder Entity-Aktivierung.

### G3 — Ressourcenauflösung, Zyklen und Tiefe

**Normstelle:** XTM §§4.3.3–4.3.4,4.21,5. **Source:** R:436–490, IM:77.
**Status:** N für nichtzyklische kontrolliert aufgelöste Ressourcen;
U/O für Zyklen und explizite Tiefenlimits.

Ein Resolver muss nicht automatisch Netzwerk oder Dateisystem benutzen. Der
vorhandene explizite Vertrag liefert Kind-Octets und optionalen Source Key;
Parser, Child-Document-IRI, Inhalte und Importkonflikte sind E9-belegt. Ein
fehlender Resolver ergibt `resource-resolver-required`; eine verweigerte
Ressource `resource-unavailable` beziehungsweise `resource-resolver-failure`.
Dies ist kein Beleg für eine fehlende nichtzyklische Importimplementierung.

Aktive Zyklen werden als `cyclic-mergemap` abgegrenzt, die konfigurierbare Tiefe
standardmäßig auf 32 begrenzt (`resource-depth-limit`). E9 belegt unmittelbare,
mittelbare, wiederholte und tiefe Fälle. Diese Betriebsgrenzen sind keine
normativ geforderten Ungültigkeitsregeln. Q-XTM-LOOP bleibt nach 22O offen;
kein Cache- oder Fixpunktverfahren wird aus einer Baseline abgeleitet.
Für uneingeschränkte Aussagen muss auch die endliche Tiefenbegrenzung als
implementierte Ressourcenpolicy ausgewiesen bleiben.

### G4 — IRI-Qualifikation: implementierte Auflösung, begrenzter Vollständigkeitsnachweis

**Normstelle:** XTM §§4.3.3–4.3.4,4.20, RFC 3986/3987, TMDM §§4.2–4.3.
**Source:** I:17/55/93/120/129, R:69/251, II:12. **Status:** N/T.
Die fünf direkten IRI-Proben in E1 und die vielen realen Referenz-/Ressourcen-
Kontrollen belegen die angewandte Auflösung und ausgewählte Ablehnungen.
Das ist nicht mit vollständiger RFC-Grammatikqualifikation gleichzusetzen.
`split-iri` zerlegt Komponenten; `absolute-locator-p` prüft nur die Schemeform,
weil das Modell validierte Locators erwartet. Der Reader prüft zusätzliche
Zeichen-/Prozent-/Fragmentbedingungen. Keine umfassende Authority-/IP-Literal-
oder gesamte Unicode-IRI-Grammatikabdeckung ist in den ausgewerteten Tests
nachgewiesen. Das bezeichnet eine konkrete Qualifikationsgrenze und keinen
hier frisch reproduzierten Akzeptanzfehler. Keine nachträgliche pauschale
Normalisierung von Identifier-Schreibweisen wird empfohlen.

### G5 — XML-/Unicode-Edition und Schema-Reichweite

**Normstelle:** XTM §2,§§4.1–4.2,5,Anhang A; XML Third Edition §§2.2–2.3,
2.11,3.3.3,4.3.3. **Source:** X:19, R:28/37/75; qualifizierte
[Parserpatches](slice-19d0b-cxml-encoding.md). **Status:** N/T/O.
E10 und E1 belegen UTF-8, UTF-16/BOM/LE/BE, fehlerhafte Sequenzen,
Supplementary Characters, Namespaces, Text- und Zeilenendenverarbeitung.
UTF-8/UTF-16 sind keine noch fehlende Reader-Fähigkeit. Andere deklarierte
Encodings sind nicht allein aufgrund ihres Namens zusätzliche Normpflichten.
Die CTM-Encoding-Grenze aus 22A ist kein XTM-Encoding-Befund.

19D0B verwendete ausdrücklich XML Fifth Edition und Unicode 16/RFC-Bezüge
für seine qualifizierten Fälle. Die Bindung an die hier vereinbarte Third
Edition, insbesondere deren Namens-/Zeichenklassen und Normalisierungen,
ist nicht durch eine pauschale Versionsgleichsetzung erledigt. Es liegen
viele positive/negative Einzeltests vor, aber kein vollständiger W3C-XML-
oder Schema-Konformitätslauf. E10 allein ist keine uneingeschränkte
XML-Processor-Zertifizierung; ebenso bedeutet fehlende Vollqualifikation
nicht, dass die getesteten Fälle unbelegt wären.

### G6 — Verfahrens-/Gesamtnachweis und Editionsfragen

**Normstelle:** XTM §§4.2,5; TMDM §§5–6. **Source:** R:320–352/378–420/490,
P; E1–E12. **Status:** N/T/O.
R liest Quelle in dokumentbezogener Reihenfolge, baut jedoch vollständige native
Konstrukte vor bestimmter II-/Reifier-Metadatenzuweisung. Reifier-induzierte
Merges, wechselnde Role-Signaturen und mehrere Reihenfolgen sind gezielt
geprüft. Die untersuchten Unterlagen belegen keinen Fehler dieser Integration,
aber auch keinen allgemeinen Beweis aller gleichzeitigen Identitäts-/Reifier-
Wechselwirkungen. Diese Grenze wird nicht als neue fehlende Modelloperation
oder als Auftrag zu einer zweiten Deserialisierungsarchitektur behandelt.

Der offizielle ISO-/Errata-Abgleich bleibt für jede Gesamtbehauptung nötig.
Die CTM-Fragen Q-CTM und die CXTM-Frage Q-CXTM aus 22C werden hier
**nicht** neu entschieden und bleiben offen. Auch gültig deserialisierte spezielle Date-/DateTime-Werte können an
bekannten CXTM-Kanonisierungsgrenzen liegen (22A-Profilproben). Das ist nicht
pauschal eine XTM-Lexerlücke. Ein bloßes Erreichen aller Korpusbaselines würde
keine dieser Grenzen automatisch aufheben.

### G7 — XTM-Ausgabe als gesonderter Umfang

**Normstelle:** XTM §4.2 (Serialisierungshinweis), Z3 als Nutzungsziel.
**Source:** P:1–7; `src/xtm/` enthält ausschließlich Package, IRI und Reader.
**Status:** F/O im gesonderten Ausgabepfad. Die aktuelle API bietet keinen
XTM-Serializer; es gibt daher keinen XTM-Ausgabe-/Wiedereinlese-Nachweis.
Ein CXTM-Vergleich unabhängiger Reader ist kein solcher Roundtrip.
Das begründet keinen automatisch beauftragten Serializer und keinen
zweifelsfreien Verstoß des vorhandenen Deserializers. Ob XTM-Ausgabe zum
konkret abzunehmenden Austauschumfang gehört, bleibt ausdrücklich festzulegen.
Diese Abgrenzung verändert keines der ursprünglichen Ziele Z1–Z6.

## Die drei verbleibenden Originale sind keine neue Feature-Liste

Die [22O-Disposition](slice-22o-qualified-xtm-corpus-disposition.md) bleibt erhalten:

| Original | Einordnung nach 22O; unveränderter Status |
|---|---|
| `occurrence-duplicate-iid2.xtm` | Dokument-ID-Verstoß, beabsichtigte `duplicate-id`-Ablehnung; Konflikt mit historisch positivem Vertrag. NOT-RUN. |
| `mergemap-itemid.xtm` | Inhaltsimport vorhanden; 224/314 Bytes, ausschließlich 90 zusätzliche Baselinebytes für Kind-Map-II. Kein fehlendes Map-II-Kopierfeature. NOT-RUN. |
| `mergemap-loop.xtm` | Unterstützungsgrenze `cyclic-mergemap`; normative Frage Q-XTM-LOOP offen. NOT-RUN. |

Weder die beiden Korpuskonflikte noch die fehlenden anyType-Originale erlauben
zusätzliche PASS. Keine Wiederholung der 22O-Untersuchung oder Statusänderung
war erforderlich.

## Genau eine Empfehlung für die nächste Arbeit

**Empfohlen wird ein begrenzter Vorabnachweis des vorhandenen XML-/C14N-Pfads
für XTM §4.16.3, vor jeder Reader-Erweiterung.**

Prioritätsgrund ist die belegte XML-Wertpflicht und ihre Bedeutung für den
verlustfreien Austausch von Ressourceninhalten (Z3), nicht Korpusgewinn.
Die Abhängigkeit ist konkret: fehlender Namespace-/QName-Kontext im produktiven
Sourcebaum, ungeprüfte Eignung der vorhandenen CXML-Kanonisierung und notwendige
Einbettung als nativer String-/Datentypwert. Das ist kein Auftrag, gleichzeitig
Zyklen, sämtliche XML-Profile, einen Serializer oder weitere Normgrenzen umzubauen.

Der kleinste sinnvolle Umfang dieser **einen** Folgearbeit wäre:

1. Die bereits gepinnte CXML-Node-Set-/Sink-Fähigkeit an der benannten Normbasis
   prüfen; keine neue Parser-/Kanonisierungsbibliothek beschaffen.
2. Kleine unabhängige XML-Teilbaum-Gegenproben für Text/Elemente/Attribute,
   Namespacevererbung/-Rebinding/-Filterung, Prefixe, Whitespace, Escaping sowie
   ausgeschlossene PI/Kommentare tatsächlich ausführen. Erwartete Bytes aus
   den Klauseln begründen, nicht aus einem zweiten Prozessor allein übernehmen.
3. Über öffentliche TMDM-APIs den kanonischen String mit anyType-Datentyp in
   Occurrence und Variant speichern; Werte, Parent/Scope, Normalisierung,
   kanonische Handles und reine wiederholte CXTM-Ausgabe prüfen.
4. Mit tatsächlichen Resultaten entscheiden, ob ein kleiner XTM-Adapter genügt.
   Bei notwendiger XML-/TMDM-/CXTM-Ausweitung stoppen und den konkreten Umfang
   gesondert freigeben lassen. Noch keine produktive Reader-Integration.

Abnahme: dokumentierte Norm-/Editionsbasis, tatsächlich ausgeführte Byteproben,
native Modellbeobachtungen und eine konkrete Aussage über den vorhandenen
Bibliothekspfad. Keine positiven Originalregistrierungen sind daraus zu erwarten.
Die historische Bezeichnung „22I“ in 22A/22D ist ein Planungsverweis, keine
heute automatisch erteilte Freigabe. Dieser Bericht beauftragt die Folgearbeit
nicht selbst. Der unabhängige ISO-Abgleich bleibt ausdrücklich offen.

Andere Einträge der Matrix sind bestehende Profil-/Nachweisgrenzen oder offene
Entscheidungen, keine zusätzliche priorisierte Aufgabenliste. Für die hier
verlangte Entscheidung liefern die vorhandenen Unterlagen bereits genug
Evidenz; zusätzliche explorative Reader-Läufe wurden nicht erzeugt.

## Gespeicherte Regression, Dokumentenaudit und unveränderter Stand

Die aktuelle Evidenz stammt aus dem abgeschlossenen 22N-Lauf mit frischem SBCL
2.5.4 und gesperrtem Netzwerk. E12 belegt 3743 XTM-Checks, 12100 Kernchecks,
146 XML-Checks, 30 Äquivalenzpaare/529 Checks/3 Kontraste und alle 113
Executor-Fehlerkontrollen. Das sind historische, in 22P nicht wiederholte Läufe.
Die neuen Beobachtungen sind ausschließlich Source-/Dokumenten- und Hashprüfungen.

| Korpus | PASS | FAIL | NOT-RUN | Originale |
|---|---:|---:|---:|---:|
| XTM 2.0 | **121** | **0** | **3** | 124 |
| CTM | **262** | **4** | **7** | 273 |
| Gesamt | **383** | **4** | **10** | 397 |

[22N-Inhaltsmanifest](../reports/slice-22n/completion-audit.json),
[geschützte Ausgangsdateien](../reports/slice-22n/after/integrity.json) und der
22O-Bericht wurden gegen aktuelle Bytes geprüft. Alle 10649 vor 22P verfolgten
Dateien bleiben unverändert. Die vorhandenen Hashnachweise umfassen die 2006
gepinnten Korpusdateien und 8026 vor 22N vorhandenen historischen Reports;
die späteren Reports bleiben über das 22N-Manifest gebunden. Dieser Slice
legt keine neuen Testreports an und ändert keine historischen Evidenzdateien.

Wesentliche geprüfte SHA-256:

| Source / Evidenz | SHA-256 |
|---|---|
| `src/xtm/reader.lisp` | `f7aa0575f8bb28913ee396060bb139b2804b3e4f5e0d5aa78341224c46b5bbff` |
| `src/xtm/iri.lisp` | `14766359c69e3c68a1201e76a31554a4872765afceec1c600048a27cf8bd6d36` |
| `src/xml/parser.lisp` | `fc91d297feb8d79ae137f29ec2a1198986dd377dbff1c56aa826e204388013c5` |
| `reports/slice-22n/after/execution.json` | `f142461408418081e1634e596e364a29ec213c0023d3ff2d79c818a156d1e7ca` |
| `reports/slice-22n/after/xtm.json` | `7d1b624aa37495423171bf725b7389261ca4ac0345d3b1b8396c496dbec320ce` |
| `reports/slice-22n/after/xml.log` | `013ca7af373eafeb553e7b50f087395f8827cbe343f871111466d80115ac1fed` |
| `docs/slice-22o-qualified-xtm-corpus-disposition.md` | `2d6ccae47a4f4533a2e5d841b94d697336aeb923841e52c1cecd4928dd4c7a95` |

| Abnahmetor aus 22A | Stand nach diesem Dokumentationsslice |
|---|---|
| A — normative Konformität | Offen: G1–G7 und Editionsnachweis erlauben keine uneingeschränkte Gesamtaussage. |
| B — qualifizierter Abschluss der 397 Originale | Offen: unverändert 4 FAIL und 10 NOT-RUN; 22O-Disposition ist keine zusätzliche Erfüllung. |
| C — HyperDoc-Integration | Nicht bearbeitet und hier nicht abgenommen; keine Integration aus Modell-/Reader-Tests ableiten. |

Der vorgesehene lokale Commit enthält ausschließlich diesen neuen Bericht.
Parent ist der oben bezeichnete 22O-Commit. Finale Commit-ID und sauberer
Index-/Arbeitsbaum werden nach dem Commit separat ausgegeben. Keine Reader-,
Modell-, Test-, Case-Record-, Korpus-, HyperDoc- oder historische Reportänderung;
keine Downloads, Pushes, Deployments oder Eingriffe in langlebige Images.
Keine automatische Implementierung. Ende Slice 22P.
