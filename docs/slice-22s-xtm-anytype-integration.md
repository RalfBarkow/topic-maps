# Slice 22S — produktive XTM-2.0-anyType-Integration

## Ergebnis und Ausgangspunkt

Basis `c1fa847c85017d4edf5c2439c772d903261e5a12` (22R), Parent
`0cb182ebab1b90dd871048c031612acd9d302678`; Index und Arbeitsbaum waren sauber.
Neuer Branch `codex/xtm-slice-22s`.
[Ausgangszustand und Quellenhashes](../reports/slice-22s/initial-state.json).

`resourceData` mit `http://www.w3.org/2001/XMLSchema#anyType` wird nun über den
produktiven XTM-Reader zu einem kanonischen Unicode-String und anschließend
über die bisherigen Konstruktoren zu einer nativen Occurrence oder Variant.
Die API `deserialize-octets` bleibt unverändert. Der C14N-Algorithmus und die
TMDM-, CTM-, CXTM- sowie XML-Quellen bleiben byteidentisch.

Normbasis bleibt [XTM §§4.3.1, 4.16.2–4.16.3](https://www.isotopicmaps.org/sam/sam-xtm/)
und die [in 22R qualifizierte C14N-1.0-Infrastruktur](slice-22r-xml-resource-c14n.md).
**Normativ abgeleitet:** anyType verwendet die kanonische XML-Stringrepräsentation;
sonstige textuelle Datentypen erlauben keine Kindelemente. Eingebettetes Markup
schließt Elemente im XTM-Namespace auf jeder Tiefe aus. Diese Integration
ändert weder Datentyp-IRIs noch native Identitäts-/Gleichheitsregeln.
Die unabhängige Prüfung gegen die offiziellen ISO-Ausgaben bleibt ausstehend;
Abnahmetore A, B und C werden durch diesen Slice nicht pauschal abgeschlossen.

## Integrationsvertrag — vor der Reader-Änderung ausgeführt

[Vorabnachweis](../reports/slice-22s/integration-preflight.json),
[Run mit unverändertem Reader-Hash](../reports/slice-22s/integration-preflight-run.json),
[Log](../reports/slice-22s/integration-preflight.log) und
[damals ausgeführtes Werkzeug](../reports/slice-22s/integration-preflight.lisp).
Der Run fand vor der Reader-Änderung statt: UTF-8, UTF-16LE und UTF-16BE;
zwölf unabhängig erwartete indexierte Werte; gemischte Datentypen, mehrere
Ressourcen und verschachteltes fremdes `resourceData`.
Dieses historische Vorabwerkzeug ist vor Reader-Änderungen auszuführen und
wird nicht als erneuter Vorabnachweis des jetzt geänderten Readers ausgegeben.

**Beobachtet:** Die vorhandene XML-API stellt keine introspektierbare Provenienz
des opaken Kontexts bereit. Gleiche Anzahl allein genügt deshalb nicht.
**Durch Konstruktion gesichert und ausführbar geprüft:** Ein Kontext wird
innerhalb eines privaten Dokumentrahmens ausschließlich aus dessen ursprünglichen
Octets erzeugt; der Reader nimmt keinen von außen gelieferten Kontext entgegen.
Die Kopie wird vor dem ersten Parsing angelegt. Der bisherige SAX-Einstieg
bekommt weiterhin das Originalvector-Objekt; die C14N-Anbindung dessen bytegleichen
Snapshot. Die Bytes müssen vor/nach der Kontextvorbereitung und bei der
Wertübernahme unverändert übereinstimmen.

Beide Inventare verwenden denselben erweiterten Namen (XTM-Namespace plus
`resourceData`) und vollständige Präorder im Originaldokument. **Alle**
`resourceData`-Elemente zählen, auch andere Datentypen; fremde lokale Namen
zählen nicht. Fremde Unterbäume werden bei der Inventur nicht übersprungen.
Die Inventarlängen müssen identisch sein. Jeder tatsächliche Source-Node
gehört per `EQ` genau einem dokumentlokalen Ordinalplatz; Tabellen-Lookup und
Node-Vektor werden gegengeprüft. Document IRI und diagnostischer Source Key
müssen zum aktuellen Rahmen passen. Der Source Key erzeugt keine Modellidentität.

Die definierten Namespace-/Präorder-Verträge beider vorhandener APIs werden
verwendet; der Reader liest weder private DOM-Felder noch konstruiert er XML neu.
Der opake Kontext bleibt während der gesamten Kanonisierung erhalten. Alle
anyType-Werte werden vor den weiteren Modelloperationen vorbereitet und danach über die
geprüften Source-Node-Bindungen übernommen. Der Kontext wird nicht in TMDM-Items
abgelegt. Separate `mergeMap`-Deserialisierungen besitzen eigene Rahmen und
Child-Document-IRIs; dynamische Bindung stellt den Parent-Rahmen anschließend wieder her.

Die Runtime-Gegenproben beschädigen Index, Ownership, Frame, Document IRI,
Octets oder Inventaranzahl. Sämtliche sechs Abweichungen werden sicher
zurückgewiesen. Der Fremdrahmentest benutzt sogar dieselben Bytes und denselben
Dokumentkontext, aber andere Source-Node-Objekte; gleiche Anzahl ist kein Ersatz
für `EQ`-Ownership.

## Produktiver Datenfluss und Grenzen

[Reader](../src/xtm/reader.lisp):

1. `deserialize-document` erhält Originalbytes, Doc IRI, Source Key und einen lokalen Snapshot.
2. Die vorhandene XML-Bytegrenze baut den bisherigen SAX-Source-Tree; `validate-source` prüft die XTM-Struktur.
3. `prepare-xml-resources` erzeugt nur bei anyType den privaten XML-Kontext, inventarisiert und kanonisiert.
4. `read-resource-value` übernimmt für anyType den geprüften String und unveränderten Datentyp.
5. `read-occurrence`/`read-variant` verwenden weiterhin die bestehenden Konstruktoren, Identifier-, Reifier- und Normalisierungsoperationen.
6. CXTM serialisiert das unveränderte native Modell deterministisch.

Keine zweite Modell- oder Kanonisierungsimplementierung. `xsd:string`,
`xsd:anyURI`, andere absolute Datentypen und `resourceRef` behalten ihre bisherigen
Pfade. Gewöhnliche Dokumente ohne anyType benötigen keinen zusätzlichen DOM-Parse.
Die bisherigen Bytegrenzen-Prüfungen (ein Aufruf und Originaloctets per `EQ`)
bleiben erhalten. DOCTYPE-Verbot, verweigerte externe Ressourcen und der
qualifizierte XML-Parser bleiben verbindlich.

Neue Diagnosen: `XTM-REJECTION/:embedded-xtm-element` für XTM-Elemente im
Markup; `XTM-XML-ERROR/:relative-namespace-uri` mit originaler
`CANONICALIZATION-ERROR`-Cause; `XTM-XML-ERROR/:resource-data-association` für
beschädigte interne Zuordnung. Die beiden letzten Diagnosen haben keine erfundenen
nativen Zeilen-/Spaltenpositionen. Sonstige XML-, Syntax- und native TMDM-Conditions
behalten ihre bisherigen Wege. Eine Zuordnungsstörung wird nicht als normative
Ungültigkeit des Originaldokuments behauptet.

## Dauerhafte Reader- und Modellbelege

[ASDF-Tests](../tests/xtm-anytype.lisp), registriert im vorhandenen
[System](../topic-maps.asd) und aufgerufen durch
[run-tests](../tests/xtm-identity.lisp).

23 positive vollständige XTM-Dokumente verwenden tatsächliche Original-Octets
und feste, von der neuen Reader-Ausgabe unabhängige Sollwerte:
16 unveränderte 22Q-Inhalte über den produktiven Reader; Unicode in drei
Encodings; gemischte Ressourcen/Datentypen inklusive `resourceRef`, leere Werte
und reiner Text; Occurrence-/Variant-Identifier und Reification; native
Duplikatnormalisierung lexikalisch verschiedener XML-Schreibweisen; Parent und
UTF-16-Kindressource mit verschiedenen Namespace-Bindungen und gleichem Source Key.

Jede Probe prüft erwartete native Werte/Datentypen, Parent/Type/Scope/Reifier,
kanonische EQ-Referenzen, unveränderte Originalbytes, Source-Key-Unabhängigkeit
und wiederholte modellunverändernde CXTM-Ausgabe. Der vorhandene vollständige
`occurrence-model`-Bericht enthält auch die vorhandenen Name-/Variant-/Reifier-
Beziehungen. Native Referenznummern bezeichnen die dortige Topic-Reihenfolge,
keine neu eingeführte Objektidentität oder CXTM-Nummerierung.

Bei XML-gleichen Occurrences vereinigt die bestehende TMDM-Normalisierung die
Identifier `urn:first` und `urn:second`. Die Metadatenprobe prüft getrennt
Occurrence `urn:o` und Variant `urn:v`, ihre Eltern, Typen, Scopes und inversen
Reifier-Beziehungen. Die Child-Probe prüft die exakten Resolverargumente und
Child-Document-IRI, nicht nur gleiche Werte.

17 negative Proben prüfen malformed XML, nicht gebundene Prefixe, relative
Namespace-URIs, DOCTYPE/externe Entity, fremdes XML außerhalb des Markups,
XTM-Elemente tief im Markup, verbotene Kindelemente bei vier anderen Datentypen
und die sechs beschädigten Zuordnungen.

[Vollständige Probe-Octets, Soll-/Istwerte, native Modellzustände, Conditions und CXTM-Hex](../reports/slice-22s/after/xtm.json),
Feld `anyTypeReader`. Die 44 Byteprüfungen und 41 nativen Werte aus 22R sind
unverändert enthalten. `resourceDataC14N` und `c14nPreflight` behalten ihre
komponentenbezogenen Herkunftsfelder; die aktuelle Reader-Unterstützung ist
separat in `anyTypeReader.XTMReaderAnyTypeIntegration` belegt. Die acht Fehler
des alten CXML-Kandidaten bleiben historische Charakterisierung.

## Unsupported-Kontrollen: ausdrückliche Retargetings

Die alten Quellen dürfen nicht weiter fälschlich als fehlende anyType-Fähigkeit
gelten. Die bestehenden Kontrollhelfer ergänzen bei den ausdrücklich umgestellten
Erwartungen ein gültiges `mergeMap` vor den lokalen Inhalten:
fehlender expliziter Resolver bzw. bei zwei bereits mit Resolver gelesenen
Kindressourcen ein unmittelbarer Selbstverweis unter der bestehenden Zyklusschutz-Policy.
Dies ist keine neue Zyklussemantik. Die ursprüngliche Aufgabe der Kontrollen —
reale Unsupported-Ausgänge, Diagnostik und Nicht-PASS-Klassifikation — bleibt erhalten.

36 ursprüngliche vollständige anyType-Quellen werden zusätzlich **ohne** diese
Policy-Auslöser über den produktiven Reader erneut ausgeführt. Alle werden
jetzt erfolgreich gelesen; native Werte und vollständiges CXTM sind gespeichert.
Historische Labels wie `anyType-still-Unsupported` bleiben zur Nachverfolgung
erhalten und beschreiben ausdrücklich keine aktuelle Fähigkeitsgrenze.

[Alle Vorher-/Nachher-Quellen, Conditions, Positionsänderungen und Replays](../reports/slice-22s/after/retargetings.json).
Die geänderten regulären Berichtszeilen verteilen sich wie folgt:

| Vorhandenes Berichtsfeld | Geänderte Kontrollzeilen |
| --- | ---: |
| negativeControls | 1 |
| nameControls | 2 |
| scopeControls | 3 |
| nameItemIdentityControls | 2 |
| variantControls | 5 |
| variantResourceDataURIControls | 2 |
| variantItemIdentityControls | 2 |
| mapReifierControls | 3 |
| nameReifierControls | 1 |
| variantReifierControls | 1 |
| datatypeControls | 3 |
| mergemapControls | 2 |
| occurrenceControls | 4 |
| roleReifierControls | 1 |
| occurrenceReifierControls | 1 |
| itemIdentityControls | 1 |

Die zwei CTM/XTM-Mergemap-Kindressourcen wurden ebenfalls ausdrücklich retargetet.
Deren gespeicherter Integrationsbericht ändert genau zwei Code-Felder:
`RESOURCE-DATA-DATATYPE` → `RESOURCE-RESOLVER-REQUIRED`; äußere Conditions,
Prüfzwecke und übrige Belege bleiben erhalten. Keine CTM-Produktionsänderung.

Die historische [22D-Fehlersteuerung](../reports/slice-22d/failure-controls.lisp)
bleibt unverändert. Die [22S-Kopie](../reports/slice-22s/failure-controls.lisp)
ändert ausschließlich den Kommentar und die reale Unsupported-Fixture zu einem
unaufgelösten `mergeMap`. Alle 113 Ziel-/Moduskombinationen und ihre erwarteten
Fehlerausgänge bleiben erhalten. Falsche Originalausgaben, XML-/XTM-/TMDM-Fehler,
Unsupported und falsche negative Ursachen werden weiterhin auseinandergehalten.

## Vollständige Offline-Abnahme und Integrität

[Ausführung](../reports/slice-22s/after/execution.json),
[Kommandos/Zeiten/Loghashes](../reports/slice-22s/after/runs.json),
[113 Fehlerkontrollen](../reports/slice-22s/after/failure-controls-audit.json).
Frische Prozesse in SBCL 2.5.4 ohne Benutzer-/Systeminitialisierung;
`sandbox-exec` verbietet Netzwerk und Repository-Schreibzugriffe einschließlich HyperDoc.
Sieben vorhandene lokale Pins und bestehende Encoding-Patches, keine Downloads
oder neuen Abhängigkeiten. Der vorhandene Collector und ASDF-Executor werden wiederverwendet.

Der endgültige reguläre XTM-Lauf besteht mit **4.327 Checks**:
4.123 erhaltene Check-Labels und 204 neue. Alle 119 erwarteten Prozessausgänge,
darunter 113 erwartete Executor-Fehler, sind eingetreten. Diese Fehlerkontrollen
werden nicht als erfolgreiche Originalverträge gezählt. Erhalten: 12.100
Kernchecks, 146 XML-Checks, sämtliche Slice-20-/22-Prüfungen, CTM/XTM- und
XTM-Mergemap, 30 Äquivalenzpaare mit 529 Checks und drei Kontrasten, zwei Python-
Tests und 16.294 NFC-Oracle-Vergleiche. Keine neue Äquivalenzprobe wird abgeleitet.

Die 124 Originaldiagnosen und alle 121 bisherigen XTM-PASS bleiben unverändert.
Die drei offenen XTM-Dispositionen aus [22O](slice-22o-qualified-xtm-corpus-disposition.md)
und die vier bekannten CTM-FAILs werden nicht umregistriert.

| Korpus | PASS | FAIL | NOT-RUN |
| --- | ---: | ---: | ---: |
| XTM 2.0 | 121 | 0 | 3 |
| CTM | 262 | 4 | 7 |

[Integritätsaudit](../reports/slice-22s/after/integrity.json): **11.245** geschützte
Basisdateien, darunter 2006 Korpusdateien und 8947 historische
Reportdateien. 45 erneut erzeugte Teilberichte sind byteidentisch; ausschließlich
der oben erläuterte CTM/XTM-Kontrollbericht besitzt zwei retargetete Codes.
C14N-, XML-, TMDM-, CTM- und CXTM-Quellen, Originale und Baselines bleiben unverändert.

```sh
python3 reports/slice-22s/reproduce.py --output /private/tmp/topic-maps-22s-new
python3 reports/slice-22s/reproduce.py --output /private/tmp/topic-maps-22s-new --audit-only
```

`--audit-only` prüft gespeicherte Ausführung und zählt nicht als neuer Testlauf.
Die beiden fehlgeschlagenen Entwicklungsanläufe (Testklammer und zunächst
unvollständiges Kindressourcen-Retargeting) sowie der korrigierte Audit-Formatfehler
sind getrennt unter `reports/slice-22s/attempts/` belegt. Ein erster Gesamtlauf war
erfolgreich, wurde aber nach der zusätzlichen Präzisierung der nativen Parent-/
Type-/Scope-/Reifier-Belege vollständig mit den endgültigen Quellen wiederholt.
Der Abschlussaudit bezieht sich ausschließlich auf diesen letzten Lauf.

Keine Erweiterung des XML-Profils oder der Zyklussemantik, keine Änderung
langlebiger Images, kein Push/Deployment und keine HyperDoc-Arbeit. Nach dem
lokalen Commit endet Slice 22S; kein automatischer Folgeauftrag.
