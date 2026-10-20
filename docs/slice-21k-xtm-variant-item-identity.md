# Slice 21K — Item Identity of Name Variants

## Ausgangszustand und normative Zuordnung

Branch: `codex/xtm-slice-21k`. Ausgangscommit und vorgesehener Parent:
`49e4f2efb3df426d8ce249bc9b714bbd81323525`.
Der vorgefundene Branch war `codex/xtm-slice-21j`; Index und Arbeitsbaum waren
sauber. [initial-state.json](../reports/slice-21k/initial-state.json) bewahrt den
Ausgangszustand und die SHA-256-Werte aller damals versionierten Dateien.

Ein frischer Offline-SBCL-Prozess reproduzierte vor der Reader-Änderung alle
1713 XTM-Prüfungen und sämtliche 124 Originaldiagnosen identisch zu Slice 21J.
Ausgangsstand: **XTM 60 PASS, 0 FAIL, 64 NOT-RUN** und
**CTM 262 PASS, 4 FAIL, 7 NOT-RUN**. Siehe
[baseline.log](../reports/slice-21k/baseline.log),
[baseline-xtm.json](../reports/slice-21k/baseline-xtm.json) und
[before-diagnostics.json](../reports/slice-21k/before-diagnostics.json).

Normativ hergeleitet aus
[XTM 2.0 §§4.3.1, 4.6 und 4.12](https://www.isotopicmaps.org/sam/sam-xtm/):
`itemIdentity*` steht im Variant vor Scope und Ressourcenwert. Sein Locator
gehört zum Information Item des Elternelements, hier dem Variant. Die
vorhandenen XTM-IRI-Regeln lösen `href` gegen die Document IRI auf.
[TMDM §§5.1, 5.5 und 6.4](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/)
bestimmen globale Item-Identifier-Eindeutigkeit, Variant-Gleichheit anhand von
Parent, Value, Datatype und Scope sowie Identifier-Erhaltung beim Merging.
Die folgenden Aussagen sind tatsächliche Ausführungsbefunde.

## Vorhandene TMDM-API und minimale Reader-Erweiterung

Vor der Reader-Änderung prüfte
[api-preflight.lisp](../reports/slice-21k/api-preflight.lisp) die unveränderte
native API in einem frischen Offline-Prozess. `add-variant` normalisiert und
liefert den kanonischen Variant. Bereits zugewiesene Identifier bleiben dabei
erhalten; derselbe Identifier ist am selben kanonischen Item idempotent.
`add-item-identifier` weist Identifier dem aktuellen Variant zu und lehnt
Kollisionen mit verschiedenen Items vor Mutation ab. Retained Handles und
Identifier-Mengen bleiben beim fehlgeschlagenen Zuweisungsversuch unverändert.
Der Test wurde in der vollständigen Abnahme erneut ausgeführt; beide Logs sind
erhalten. Es war keine TMDM-Änderung erforderlich.

Nur `src/xtm/reader.lisp` enthält Produktionsänderungen:

1. `validate-source` erlaubt null oder mehrere Variant-`itemIdentity`-Elemente
   in Phase 0 vor Scope und Ressourcenwert. Die bestehende allgemeine
   `itemIdentity`-/`leaf-href`-Validierung prüft Attribute, Inhalt und IRI.
2. `read-variant` erzeugt zunächst den vollständigen Variant mit Parent, Value,
   Datatype und Scope über `add-variant`. Erst an dessen kanonischem Ergebnis
   weist `add-item-identifier` die aufgelösten Identifier zu. Jeder Rückgabewert
   wird als aktuelles Variant-Handle weiterverwendet und zurückgegeben.

Diese Reihenfolge ist für das doppelte Original wesentlich: Der zweite
normativ gleiche Variant fällt bereits vor der erneuten Zuweisung von
`#the-variant` mit dem ersten zusammen. Unterschiedliche Variants werden durch
einen kollidierenden Identifier nicht gleichgesetzt.

Es gibt keine zweite Identifier-Registry oder Variant-Repräsentation.
Owner-Prüfungen durchsuchen ausschließlich die aktuellen nativen Information
Items mit `map-information-items` und vergleichen deren tatsächliche Handles.
TMDM, CTM, CXTM und XML bleiben unverändert. Reification, weitere Datentypen,
XML-Kanonisierung, Occurrences, explizite Associations/Roles, XTM-`mergeMap` und
XTM 2.1 wurden nicht implementiert. Die bisherigen Resource-Pfade bleiben
bestehen.

## Zwei unveränderte Originalverträge

| Original | Quellbytes | Variant-Elemente | kanonische Variants | CXTM Ist/Soll | Ergebnis |
| --- | ---: | ---: | ---: | ---: | --- |
| `itemid-variant.xtm` | 351 | 1 | 1 | 666/666 | PASS |
| `variant-duplicate-iid.xtm` | 543 | 2 | 1 | 666/666 | PASS |

Das tatsächliche XML enthält jeweils den Owner-Topic `id="topic"`, den Name
`Topic`, einen leeren Name-Scope und textuelles `resourceData` mit Value
`TOPIC!` und Standarddatentyp `xsd:string`. Jeder Variant enthält vor seinem
Scope ein `itemIdentity href="#the-variant"`. Der explizite Scope referenziert
`#command`. Das zweite Original enthält zwei solche vollständig gleichwertigen
Variant-Elemente. Weitere neue Sprachunterstützung ist für beide nicht nötig.

Document IRI ist jeweils
`https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/`
plus Case-ID `xtm2/in/<Dateiname>`. Der Source Key ist die Case-ID.
Beide unveränderten Rohquellen werden über
`topic-maps.xtm:deserialize-octets` und den qualifizierten XML-Parser verarbeitet.

Tatsächlich gespeicherte absolute Variant-Identifier:

```text
https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/itemid-variant.xtm#the-variant
https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/variant-duplicate-iid.xtm#the-variant
```

Native Modellprüfungen belegen für jedes Original:

- Drei Topics, keine Associations, ein Name und genau ein kanonischer Variant.
  `TOPIC!` und `http://www.w3.org/2001/XMLSchema#string` bleiben erhalten.
- Owner und Name-Parent sind `EQ`; Name und Variant-Parent sind `EQ`.
  Name-, Variant-, Type- und Theme-Handles sind kanonisch. Der Variant-Scope
  besteht genau aus dem kanonischen `DocumentIRI#command`-Topic.
- Ausschließlich der Variant hat den oben angegebenen Item Identifier.
  Die Suche über alle aktuellen Information Items liefert per `EQ` genau ihn.
  Der Owner hat nur `DocumentIRI#topic`, der Theme-Topic nur
  `DocumentIRI#command`. Der Default-Name-Type hat nur seinen vorgesehenen SI.
  Map und Name haben keine Item Identifier, es entstehen keine Subject
  Locators, zusätzlichen Subject Identifier oder Reifier.
- Die globale Identifier-Eindeutigkeit besteht. Die zwei Quellvarianten des
  zweiten Originals normalisieren zu einem Variant mit einem Identifier.

Alle vollständigen CXTM-Bytes entsprechen den unveränderten Originalbaselines,
jeweils **666/666 Bytes** einschließlich abschließendem LF.
`firstDifferentByte` und tatsächliche Condition sind jeweils `null`.
Die Kanonisierung ist deterministisch und verändert native Modellzustände und
Rohbytes nicht. Ein unabhängiger Source Key bei gleicher Document IRI erzeugt
dasselbe Modell und dieselben CXTM-Bytes.

| Original | SHA-256 Quelle | SHA-256 Baseline und tatsächliche Ausgabe |
| --- | --- | --- |
| `itemid-variant.xtm` | `73cd8cd0cea5d56f990f0653428b0cb954d730f2c2785f95cd5a0979d05dc9e3` | `e35c1eb8965421ab8c2125856623bb86079c59c07f094e0719735b3628f8382b` |
| `variant-duplicate-iid.xtm` | `33bad7a941744e476b2facc1a89ab8a7cea1efe063a5869c211cc9053ea6f879` | `e35c1eb8965421ab8c2125856623bb86079c59c07f094e0719735b3628f8382b` |

[variant-item-identity-originals.json](../reports/slice-21k/variant-item-identity-originals.json)
enthält vollständige Rohbytes als Hex und Text, Document IRI, Identifier,
tatsächliche Modelle, Conditions sowie alle tatsächlichen und erwarteten
CXTM-Texte. Die beiden tatsächlichen Ausgabedateien sind in
[actual/](../reports/slice-21k/actual/) erhalten.

Der bestehende Case-Record-Executor klassifiziert nur nach tatsächlicher
Deserialisierung, nativen Modellprüfungen und vollständigem Bytevergleich als
`cxtm-match`/PASS. Beide Originale werden genau einmal im regulären ASDF-Lauf
ausgeführt. Insgesamt bestehen 62 eindeutige Case Records: 54 positive und
acht ursachenqualifizierte negative Originale. Die bisherigen 60 Ergebnisse
bleiben unverändert. Synthetische Gegenproben zählen nicht als Originalverträge.

## Native Identifier-, Normalisierungs- und Handle-Prüfungen

Die **49 neuen protokollierten Kontrollen** umfassen zwölf positive XTM-
Eingaben, neun schrittweise Merge-Prüfungen, 22 Syntax-/Konflikt-/Unsupported-
Prüfungen, einen rohen UTF-8-Fehler und fünf native Atomaritätsprüfungen.

Geprüft werden absolute, relative, Fragment- und leere IRI-Referenzen, Unicode,
Prozent-/UTF-8-Dekodierung, eine andere Document IRI sowie mehrere und doppelte
Identifier am selben Variant. `itemIdentity` hat keine TopicRef-Shorthand-
Einschränkung. Gleichwertige Variants mit demselben Identifier normalisieren
idempotent; gleichwertige Variants mit verschiedenen Identifiern bewahren deren
Vereinigung. `resourceRef` und anyURI-`resourceData` behalten Value und Datatype
auch mit Variant-Identifiern. Ein gleichlautender Topic-SI und Variant-II
bewirken keine implizite Reification oder Topic-Vereinigung.

Alle neun Kombinationen aus SI-/SL-/II-Merging von Parent-Topics, Name-Scope-
Themes und Variant-Scope-Themes werden mit den bestehenden Reader-Operationen
schrittweise ausgeführt. Vor dem Merge sind zwei Variants und deren Identifier
verschieden. Nach dem Merge zeigen alle festgehaltenen Name-, Variant- und
Theme-Handles auf die korrekten kanonischen Objekte. Die Identifier
`urn:v1` und `urn:v2` gehören danach ausschließlich zum gemeinsamen kanonischen
Variant. Retained Variant-Handles liefern beide Identifier; Parent und Scope
bleiben per `EQ` korrekt. Die globale Identifierprüfung und reine CXTM-
Kanonisierung bestehen jeweils.

Fünf separate native `add-item-identifier`-Konfliktversuche betreffen Map,
Owner-Topic, Name, Theme-Topic und einen anderen Variant. Für jeden Versuch
bleiben der vollständige native Modellzustand, Identifier-Mengen und
kanonischen Handles unverändert. Diese Aussage betrifft die native Zuweisung;
es wird keine neue Transaktionssemantik für den gesamten Reader eingeführt.

Der reguläre Lauf besteht mit **1860 eindeutigen XTM-
Prüfungen**: 1713 bisherige Prüfungen, davon zwei sinnvoll umbenannte Labels,
und **147 neue**. Die relative Reihenfolge der bisherigen
Prüfungen bleibt erhalten.

## Konkrete Conditions und Syntaxgrenzen

Die folgende Tabelle stammt aus `variantItemIdentityControls` in
[xtm.json](../reports/slice-21k/xtm.json). Dort sind vollständige Quelltexte,
Kontexte, native Modelle und gegebenenfalls Causes erhalten. SAX-Positionen
sind ungefähre Zeichenpositionen; native TMDM-Conditions haben keine
Quellposition.

| Gegenprobe | Condition | Fehlercode | Zeile:Spalte |
| --- | --- | --- | --- |
| `after-scope` | `XTM-REJECTION` | `element-order` | 1:172 |
| `after-resource` | `XTM-REJECTION` | `element-order` | 1:202 |
| `missing-href` | `XTM-REJECTION` | `missing-attribute` | 1:123 |
| `attribute` | `XTM-REJECTION` | `unexpected-attribute` | 1:148 |
| `child` | `XTM-REJECTION` | `unexpected-child` | 1:135 |
| `text` | `XTM-REJECTION` | `unexpected-text` | 1:135 |
| `invalid-iri` | `XTM-REJECTION` | `invalid-iri` | 1:140 |
| `percent-short` | `XTM-REJECTION` | `invalid-percent-escape` | 1:138 |
| `percent-hex` | `XTM-REJECTION` | `invalid-percent-escape` | 1:139 |
| `percent-utf8` | `XTM-REJECTION` | `invalid-percent-utf8` | 1:139 |
| `percent-overlong` | `XTM-REJECTION` | `invalid-percent-utf8` | 1:142 |
| `collision-map` | `ITEM-IDENTIFIER-ERROR` | `duplicate-item-identifier` | nicht vorhanden (TMDM) |
| `collision-topic` | `ITEM-IDENTIFIER-ERROR` | `duplicate-item-identifier` | nicht vorhanden (TMDM) |
| `collision-name` | `ITEM-IDENTIFIER-ERROR` | `duplicate-item-identifier` | nicht vorhanden (TMDM) |
| `collision:different-value` | `ITEM-IDENTIFIER-ERROR` | `duplicate-item-identifier` | nicht vorhanden (TMDM) |
| `collision:different-datatype` | `ITEM-IDENTIFIER-ERROR` | `duplicate-item-identifier` | nicht vorhanden (TMDM) |
| `collision:different-scope` | `ITEM-IDENTIFIER-ERROR` | `duplicate-item-identifier` | nicht vorhanden (TMDM) |
| `collision-different-parent` | `ITEM-IDENTIFIER-ERROR` | `duplicate-item-identifier` | nicht vorhanden (TMDM) |
| `topicRef-does-not-reify-variant` | `OCCURRENCE-IDENTIFIER-ERROR` | `duplicate-item-identifier` | nicht vorhanden (TMDM) |
| `scope-not-proper-superset` | `VARIANT-ERROR` | `invalid-variant-scope` | nicht vorhanden (TMDM) |
| `reification-still-unsupported` | `XTM-UNSUPPORTED` | `reification` | 1:121 |
| `other-datatype-still-unsupported` | `XTM-UNSUPPORTED` | `resource-data-datatype` | 1:238 |
| `invalid-raw-UTF8` | `XTM-XML-ERROR` | `xml-not-well-formed` | 1:7 |
| `atomic-conflict:map` | `ITEM-IDENTIFIER-ERROR` | `duplicate-item-identifier` | nicht vorhanden (TMDM) |
| `atomic-conflict:topic` | `ITEM-IDENTIFIER-ERROR` | `duplicate-item-identifier` | nicht vorhanden (TMDM) |
| `atomic-conflict:name` | `ITEM-IDENTIFIER-ERROR` | `duplicate-item-identifier` | nicht vorhanden (TMDM) |
| `atomic-conflict:theme` | `ITEM-IDENTIFIER-ERROR` | `duplicate-item-identifier` | nicht vorhanden (TMDM) |
| `atomic-conflict:other-variant` | `ITEM-IDENTIFIER-ERROR` | `duplicate-item-identifier` | nicht vorhanden (TMDM) |

Kollisionen unterschiedlicher Variants bleiben auch bei unterschiedlichem
Value, Datatype, Scope oder Parent native `ITEM-IDENTIFIER-ERROR` mit
`:duplicate-item-identifier`. Ein `topicRef` auf einen Variant-II kann keinen
Topic aus diesem Variant machen; der bestehende Topic-Konstruktorpfad bewahrt
dafür seinen Kompatibilitätsnamen `OCCURRENCE-IDENTIFIER-ERROR`.
Die rohe UTF-8-Fehleingabe bewahrt die XML-Cause
`WELL-FORMEDNESS-VIOLATION` zum ungültigen Startbyte `11111111`.

Identifier nach Scope oder Ressourcenwert sind Syntaxfehler. Scope ohne echte
Erweiterung erreicht `VARIANT-ERROR/:invalid-variant-scope`. Gültige
Reification und gültiges, nicht implementiertes `xsd:integer` bleiben spezifisch
Unsupported. Keine beliebige Ablehnung zählt als bestandene negative Prüfung.
Die nativen Conditionklassen werden weder umbenannt noch generisch verpackt.

## Gezielte Aktualisierung einer Unsupported-Fixture

Die alte gültige, inzwischen unterstützte Item-Identity-Gegenprobe wird um
`reifier="#r"` ergänzt. Dieses vollständige Konstrukt bleibt gültig und liegt
wegen Reification außerhalb des Slices. Das Label `itemIdentity` wird zu
`reified-itemIdentity`, der erwartete Code von `:unsupported-construct` zu
`:reification`. Beide Prüfungsnamen ändern sich entsprechend.

Genau eine Zeile des alten `variantControls`-Reports ändert sich dadurch.
Alle anderen alten Kontrollzeilen und sämtliche bisherigen Original- und
Resource-Reports bleiben identisch. Es werden keine historischen Berichte
umgeschrieben. Sämtliche 48 übernommenen Nicht-XTM-Reports sind strukturell
identisch zu Slice 21J.

## Diagnosevergleich sämtlicher 124 Originale

Genau die beiden beauftragten Beobachtungen ändern sich:

| Original | Vorher | Tatsächliches Ergebnis danach |
| --- | --- | --- |
| `itemid-variant.xtm` | `XTM-UNSUPPORTED/:unsupported-construct`, 6:44 | keine Condition, 666/666 Bytes identisch |
| `variant-duplicate-iid.xtm` | `XTM-UNSUPPORTED/:unsupported-construct`, 6:44 | keine Condition, 666/666 Bytes identisch |

Ursache ist die nun unterstützte Identifier-Zuweisung an den zuvor erzeugten
kanonischen Variant. Die übrigen **122 vollständigen Beobachtungen bleiben
identisch**. [diagnostic-changes.json](../reports/slice-21k/diagnostic-changes.json)
erhält beide vollständigen Vorher-/Nachher-Beobachtungen mit konkretem Grund.
Es werden keine weiteren Originalverträge aus explorativen Befunden registriert.

## Vollständige Offline-Abnahme

Alle Testprozesse verwenden frisches **SBCL 2.5.4** ohne System-/Benutzerinit.
Die vorhandenen gepinnten lokalen Abhängigkeiten und XML-Patches werden geprüft
und in temporären Verzeichnissen verwendet. Quellvorbereitung, API-Vorprüfung,
Tests und Diagnose laufen zusätzlich mit Netzwerk- und Repository-Schreibsperre:

```text
(version 1)(allow default)(deny network*)(deny file-write* (subpath "/Users/rgb/workspace/topic-maps"))
```

Die reguläre `require_escalated`-Freigabe war erfolgreich. Die Sandbox-
Konfiguration und `~/.nix-profile` wurden nicht geändert. Es gab keine neuen
Downloads, keine langlebigen Lisp-Image-Loads und keinen vollständigen
Nix-Neubau. Letzterer ist ausdrücklich NOT-RUN; die frische Offline-SBCL-
Regression wurde vollständig ausgeführt.

| Bereich | Bestandene Prüfungen |
| --- | ---: |
| Bisherige Lisp-Regression einschließlich TMDM, CTM/CXTM, Include und Mergemap | 12100 |
| XTM einschließlich aller bisherigen und beider neuer Originale | 1860 |
| XML-Qualifikation | 146 |
| XTM-MERGEMAP | 217 |
| REGISTERED-ORIGINALS | 286 |
| REGISTERED-NEGATIVES | 25 |
| PROLOG | 171 |
| EMPTY2 | 13 |
| CTM-INTEGER | 112 |
| TRIPLE | 226 |
| ENCODING | 722 |
| Python-Unittests | 2 |
| NFC-Oracle-Vergleiche | 16294 |
| Isolierte, erwartet scheiternde Executor-Kontrollen | 60 |

Zusätzlich besteht die native Variant-Identifier-API-Vorprüfung erneut.
Die **60 Executor-Kontrollen** erhalten alle bisherigen 50 Fehlerpfade und
fügen je neuem Original Byteabweichung, XML-Fehler, Unsupported, einen echten
Konflikt zwischen verschiedenen Variants und eine falsche XTM-Condition hinzu.
Alle erzeugen den erwarteten ASDF-Exit 1 und zählen niemals als positiver PASS.
Die davor registrierten Original-PASS bleiben jeweils erhalten. Siehe
[failure-controls.json](../reports/slice-21k/failure-controls.json) und die
zugehörigen einzelnen Logs und Case-Record-Reports.

Tatsächlich registrierter Stand nach erfolgreicher Ausführung:

| Korpus | PASS | FAIL | NOT-RUN |
| --- | ---: | ---: | ---: |
| XTM | 62 | 0 | 62 |
| CTM | 262 | 4 | 7 |

Die offenen XTM-Verträge umfassen 59 positive und drei negative Originale.
Die vier bekannten CTM-FAILs bleiben unverändert: `include-template.ctm`,
`include-wildcard2.ctm`, `occurrence-datetime-timezone2.ctm` und
`occurrence-datetime2.ctm`.

## Integrität und Reproduktion

Alle **2006 gepinnten Korpusdateien** stimmen
weiterhin in Größe und SHA-256 mit `references/corpus-lock.json` überein.
Alle **2491 historischen Reportdateien** und
**4744 geschützten Dateien** des Ausgangscommits
bleiben byteidentisch. [integrity.json](../reports/slice-21k/integrity.json)
enthält vollständige Hashlisten und die geprüften Ausführungsquellen.

[execution.json](../reports/slice-21k/execution.json) protokolliert alle Befehle,
UTC-Zeitpunkte, Sandboxregeln, erwarteten und tatsächlichen Exitcodes und die
registrierten Stände. [precommit-audit.json](../reports/slice-21k/precommit-audit.json)
sichert den finalen Änderungsumfang;
[artifacts.json](../reports/slice-21k/artifacts.json) enthält Größen und
SHA-256-Werte aller neuen Artefakte.

Reproduktion mit unbenutztem Ausgabeverzeichnis außerhalb des Repositorys:

```sh
python3 scripts/validate-slice-21k.py --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl --output /private/tmp/topic-maps-21k-recheck
```

Reader-Erweiterung, Tests, Dokumentation und geprüfte Ausführungsevidenz werden
zusammen lokal committet. Slice 21K endet damit.
