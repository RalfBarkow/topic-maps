# Slice 21O — XTM 2.0 Variant Reification

Ausgangspunkt: `6f6170b7e9b76ab6b8c117b90e3781b6b8ffe6a3`, sauberer Index/Arbeitsbaum auf `codex/xtm-slice-21n`. Arbeitsbranch: `codex/xtm-slice-21o`.

## Norm und implementierte Operationen

**Normativ:** [XTM 2.0 §§4.3.1–4.3.4](https://www.isotopicmaps.org/sam/sam-xtm/) definiert `reifiable` als optionales Reifier-Attribut mit nachfolgenden Item Identities. Die aufgelöste Reifier-IRI wird ausschließlich in Topic-Item-Identifiern gesucht. Ein fehlendes Topic wird mit diesem II erzeugt. §§4.12–4.13 ordnen den Variant dem Parent-Name zu und vereinigen dessen Scope mit den expliziten Themes. Die bereits vorhandene IRI-Auflösung bleibt zuständig.

**Normativ:** [TMDM §§5.3.4–5.3.5, 5.5, 6.2 und 6.4](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/) unterscheidet Variant-Gleichheit (Parent, Wert, Datentyp, Scope), Variant-II und Reifier-Topic-II. Gleiche Variants vereinigen Metadaten; zwei vorhandene Reifier werden dabei zusammengeführt. Die Scope muss eine echte Obermenge der Name-Scope bleiben. Topic-Merging mit unterschiedlichen nichtleeren reifizierten Gegenständen ist ein Fehler.

**Implementiert:** [Reader](../src/xtm/reader.lisp) validiert nun die Reifier-IRI des Variant statt sie als Unsupported abzuweisen. `read-variant` verwendet die vorhandene Reihenfolge: Parent-/Scope-Verarbeitung, Ressourcenwert/Datentyp, `add-variant`, `add-item-identifier`, gemeinsame II-Auflösung `read-item-reifier`, `set-item-reifier`, `canonical-variant`. Der unbenutzte Unsupported-Helfer entfällt. Keine neue Auflösung oder Registry. TMDM, CTM, CXTM und XML sind unverändert.

## Vorprüfung vor der Reader-Änderung

**Beobachtet:** Die vier frischen Prozesse in [baseline-execution.json](../reports/slice-21o/baseline-execution.json) reproduzieren die Ausgangsstände XTM **68 PASS / 0 FAIL / 56 NOT-RUN** und CTM **262 / 4 / 7**, alle 124 Originaldiagnosen sowie die bisherige vollständige Regression. Alle damaligen getrackten Dateien waren vor der Reader-Änderung unverändert.

Die [native Vorprüfung](../reports/slice-21o/api-preflight.lisp) / [Ausgabe](../reports/slice-21o/baseline-variant-reifier-api-preflight.log) belegt an tatsächlichen TMDM-Objekten: Zuweisung und inverse `EQ`-Referenz; Normalisierung gleicher Variants; Identifier-Vereinigung; Erhaltung eines einzelnen Reifiers; Zusammenführung zweier zulässiger Reifier; kanonische Auflösung alter Variant-, Name- und Topic-Handles. Reifier-Konflikte und Identifier-Kollisionen sind atomar zurückgewiesen.

Die anfängliche Prüf-Assertion verlangte fälschlich rohe `EQ`-Identität eines alten Variant nach Normalisierung. Sie wurde auf `canonical-variant` korrigiert. [Anfängliches Skript](../reports/slice-21o/development-preflight-original.lisp) und [Fehlerausgabe](../reports/slice-21o/development-preflight-original.log) bleiben erhalten. Das war ein Fehler der Vorprobe; die Produktions-API wurde nicht verändert. Die [Entwicklungsläufe](../reports/slice-21o/development/attempts.json) sind getrennt von den abschließend akzeptierten Ergebnissen archiviert.

## Unveränderte Originale und Baselines

Vollständige Originalbytes als Hex und UTF-8-Text, Document IRIs, Baselines und SHA-256: [Inventar vor Implementierung](../reports/slice-21o/candidate-inventory.json).

| Original | Quellbytes | Name-/Variant-Elemente | Baseline | Registrierung |
|---|---:|---:|---:|---|
| [variant-reifier.xtm](../vendor/cxtm/xtm2/in/variant-reifier.xtm) | 326 | 1 / 1 | 702 Bytes | PASS |
| [variant-duplicate-reifier.xtm](../vendor/cxtm/xtm2/in/variant-duplicate-reifier.xtm) | 493 | 1 / 2 | 702 Bytes | PASS |
| [variant-duplicate-reifier2.xtm](../vendor/cxtm/xtm2/in/variant-duplicate-reifier2.xtm) | 543 | 2 / 2 | 702 Bytes | NOT-RUN; nur beobachtet |

| Original | SHA-256 der Quelle |
|---|---|
| `variant-reifier.xtm` | `59fc86dbefd9b8c647baff6d88bbc0768bb0a4abfc510f5eef4d391ee312d87f` |
| `variant-duplicate-reifier.xtm` | `62d364191cf06854be9a683956c30f5bf5282d7c89f604ccc2923bf8b4738653` |
| `variant-duplicate-reifier2.xtm` | `87b740c6ec7d11b485b223cb5c28807bce9259d04c2d586ea557e6cd10c3faf4` |

Alle drei unveränderten Baselines haben SHA-256 `014773fca95a2b7bb70038f8e118d402d311a2804f54f105ff05ee53c7eb0a60` und genau 702 Bytes.

**Beobachtete Quellstruktur:** Die beiden beauftragten Originale enthalten jeweils ein Topic `topic` und einen Name ohne eigene Scope/Identifier/Reifier. Der Name-Wert ist `Topic`. Ein beziehungsweise zwei Variant-Elemente enthalten `reifier="#reifier"`, explizit genau das Theme `#command`, und textuelles `resourceData` mit `TOPIC!`, ohne Datentyp-Attribut. Kein Variant hat Item Identity. Reifier und Theme sind nicht explizit als Topic definiert. Alle benötigten Konstrukte lagen im beauftragten Umfang.

**Beobachtetes natives Ergebnis beider registrierter Originale:** Vier Topics (Owner `#topic`, Standard-Name-Type-SI, Theme `#command`, Reifier `#reifier`), ein Name, ein Variant, keine Association/Occurrence/Role. Name-Scope leer; Variant-Scope genau Theme `#command`; Wert `TOPIC!`; Datentyp `http://www.w3.org/2001/XMLSchema#string`. Map, Name und Variant haben keine eigenen IIs. Owner, Theme und Reifier tragen jeweils ihren Document-IRI-plus-Fragment-II, ohne SI/SL; nur das Standard-Type-Topic hat die vorgeschriebene SI. Der Reifier reifiziert ausschließlich den Variant.

Nachgewiesen mit `EQ`: Variant ist `canonical-variant`, sein Parent der kanonische Name, dessen Parent der Owner; Theme und Reifier sind kanonische Topics; `item-reifier(v) = r` und `topic-reified(r) = v`. Zweimalige Kanonisierung erhält diese realen Referenzen und alle alten Forward-Handles. Die nativen Topic-Ordnungsnummern im JSON (Reifier 4) sind von den sortierten CXTM-Nummern (Reifier 2) zu unterscheiden.

Die [beiden ausgeführten Originalverträge](../reports/slice-21o/variant-reifier-originals.json) verwenden die tatsächlichen Rohbytes über `deserialize-octets` und genau einen qualifizierten XML-Parser-Aufruf für die primäre Deserialisierung. Separate Source-Key-Gegenproben liefern dasselbe Modell und CXTM. Beide vollständigen Originalvergleiche: **702/702 Bytes, keine abweichende Byteposition, Condition null**. Jeweils genau ein neuer Case Record; synthetische Gegenproben zählen nicht als Original.

Der gesondert beobachtete dritte Vertrag enthält zwei gleichwertige Name-Elemente mit jeweils einem solchen Variant. Name- und Variant-Normalisierung ergeben ebenfalls einen Name und einen reifizierten Variant; die Baseline stimmt mit **702/702 Bytes** überein. [Natives Modell und CXTM](../reports/slice-21o/further-variant-reification.json). Er ist ausdrücklich **nicht registriert**.

## Dauerhafte Gegenproben

[ASDF-Testdatei](../tests/xtm-variant-reification.lisp), aufgerufen durch das bestehende `run-tests`, mit zusätzlichen Feldern im bisherigen [XTM-Report](../reports/slice-21o/xtm.json):

- Reifier als absolute/relative/Fragment-/leere IRI; Unicode und UTF-8-Prozentsequenzen; Ressourcenwert mit XML-Escaping, Unicode und erhaltenem Whitespace.
- II-Treffer, SI-Miss mit anschließender nativer SI/II-Identitätsvereinigung und obligatorischem neuem II sowie getrennt bleibender SL-Fall.
- Gleiche Variants mit gleichem/verschiedenen Reifiern; Vereinigung ihrer IIs; unterschiedliche Varianten bleiben getrennt. Bereits unterstütztes `resourceRef` und `xsd:anyURI`-`resourceData` normalisieren nach ihren tatsächlichen Werten/Datentypen; spätere Reifier-Topic-Definition erhält die II-Menge.
- Neun gestufte Reader-Prüfungen: SI-/SL-/II-Merging von Parent-Topics, Name-Scope-Themes und Variant-Scope-Themes. Alte Variant-, Name-, Theme- und Reifier-Handles werden gehalten und nach Normalisierung mit den neuen kanonischen Objekten per `EQ` verglichen. Öffentliche Deserialisierung ergibt das gleiche Modell. Wiederholtes CXTM verändert weder aktuelle noch alte Handles.
- Scope-Vererbung, mehrfache/doppelte Themes, echte Obermenge, atomare native Scope-Kollapse, auch wenn Reifier-Merging den Kollaps auslösen würde.
- Native Reifier-Wiederverwendung, unzulässige Reifier-/Parent-Topic-Merges und Identifier-Kollisionen; getrennte XML-, XTM-, Unsupported- und TMDM-Diagnosen.

### Tatsächliche Conditions

Alle Details, Quellen, Document IRIs, Source Keys und Causes stehen unter `variantReifierControls` im XTM-Report. Native Conditions haben keine XML-Quellposition; es wird keine erfunden. XML-/XTM-Positionen sind ungefähre SAX-Zeile/Spalte. `—` bedeutet null.

| Gegenprobe | Condition | Code | Zeile:Spalte | Cause / atomare native Ablehnung |
|---|---|---|---|---|
| `variant:space` | `XTM-REJECTION` | `invalid-iri` | 1:126 | — |
| `variant:percent` | `XTM-REJECTION` | `invalid-percent-escape` | 1:126 | — |
| `variant:UTF8` | `XTM-REJECTION` | `invalid-percent-utf8` | 1:129 | — |
| `variant:surrogate` | `XTM-REJECTION` | `invalid-percent-utf8` | 1:132 | — |
| `variant:control` | `XTM-REJECTION` | `invalid-iri` | 1:126 | — |
| `variant:attribute` | `XTM-REJECTION` | `unexpected-attribute` | 1:131 | — |
| `variant:qualified-attribute` | `XTM-REJECTION` | `unexpected-attribute` | 1:139 | — |
| `variant:reifier-child` | `XTM-REJECTION` | `unexpected-element` | 1:128 | — |
| `variant:II-order` | `XTM-REJECTION` | `element-order` | 1:185 | — |
| `variant:scope-after-resource` | `XTM-REJECTION` | `missing-variant-scope` | 1:135 | — |
| `variant:two-scopes` | `XTM-REJECTION` | `duplicate-variant-scope` | 1:164 | — |
| `variant:two-resources` | `XTM-REJECTION` | `variant-resource-cardinality` | 1:214 | — |
| `variant:XML` | `XTM-XML-ERROR` | `xml-not-well-formed` | 1:128 | WELL-FORMEDNESS-VIOLATION |
| `variant:occurrence-reification-excluded` | `XTM-UNSUPPORTED` | `unsupported-construct` | 1:102 | — |
| `variant:variant-II-reifier-II` | `OCCURRENCE-IDENTIFIER-ERROR` | `duplicate-item-identifier` | — | — |
| `variant:name-II-reifier-II` | `OCCURRENCE-IDENTIFIER-ERROR` | `duplicate-item-identifier` | — | — |
| `variant:map-II-reifier-II` | `OCCURRENCE-IDENTIFIER-ERROR` | `duplicate-item-identifier` | — | — |
| `variant:reuse-reifier` | `REIFICATION-ERROR` | `reifier-conflict` | — | — |
| `variant:scope-equal-1` | `VARIANT-ERROR` | `invalid-variant-scope` | — | — |
| `variant:scope-equal-2` | `VARIANT-ERROR` | `invalid-variant-scope` | — | — |
| `variant:native-reuse-reifier` | `REIFICATION-ERROR` | `reifier-conflict` | — | atomar geprüft |
| `variant:native-distinct-reified-merge` | `REIFICATION-ERROR` | `reifier-conflict` | — | atomar geprüft |
| `variant:native-scope-collapse` | `VARIANT-ERROR` | `variant-scope-collapse` | — | atomar geprüft |
| `variant:reifier-merge-collapses-scope` | `VARIANT-ERROR` | `variant-scope-collapse` | — | — |
| `variant:native-reifier-merge-collapses-scope` | `VARIANT-ERROR` | `variant-scope-collapse` | — | atomar geprüft |
| `variant:native-parent-reifier-conflict` | `REIFICATION-ERROR` | `reifier-conflict` | — | atomar geprüft |

Der historische Klassenname `OCCURRENCE-IDENTIFIER-ERROR` stammt aus der vorhandenen nativen Topic-Erzeugung bei belegtem Item Identifier. Er wird nicht in einen XTM-Fehler übersetzt.

## Vergleich aller 124 Originaldiagnosen

[Vorher](../reports/slice-21o/before-diagnostics.json), [nachher](../reports/slice-21o/after-diagnostics.json), [vollständige Änderungen](../reports/slice-21o/diagnostic-changes.json).

Genau drei Änderungen: `variant-reifier.xtm`, `variant-duplicate-reifier.xtm`, `variant-duplicate-reifier2.xtm`. Vorher jeweils `XTM-UNSUPPORTED/:reification`, ungefähr **5:35**, Cause null. Nachher erfolgreiche Deserialisierung ohne Condition und bytegenaues Original-CXTM. **Alle übrigen 121 Diagnoseobjekte sind vollständig identisch**, einschließlich Codes, Positionen, Causes und gegebenenfalls vollständiger CXTM-Ausgabe.

Die weiterhin offenen negativen Originale `reifier-collision.xtm`, `role-duplicate-reified.xtm` und `topicref-no-fragment-id.xtm` bleiben NOT-RUN. Keine zusätzliche negative Ursache wird durch diese Implementierung neu als PASS qualifiziert.

Neun bisherige lokale Variant-Reification-Unsupported-Proben prüfen jetzt gültige Variants mit weiterhin ausgeschlossenem Integer-`resourceData`; Klassen bleiben `XTM-UNSUPPORTED`, Codes wechseln spezifisch auf `resource-data-datatype`. [Exakte Vorher-/Nachher-Zeilen](../reports/slice-21o/retargeted-controls.json), [22 umbenannte Check-Labels](../reports/slice-21o/retargeted-checks.json). Zwei weitere Fixtures im allgemeinen XTM-/CTM-XTM-Fehlerpfad prüfen nun gültige ausgeschlossene Occurrence-Reification, Code `unsupported-construct`. Die zwei erzeugten CTM/XTM-Integrationsreport-Kopien unterscheiden sich ausschließlich in den [ausdrücklich aufgeführten JSON-Pfaden](../reports/slice-21o/retargeted-integration.json). Historische Dateien bleiben bytegleich.

## Abschließende Offline-Abnahme

[Vollständiger Ausführungsbericht](../reports/slice-21o/execution.json), [Rohlog](../reports/slice-21o/regression.log), [isolierte Fehlerkontrollen](../reports/slice-21o/failure-controls.json).

- 109 Abnahme-Prozesse: sechs reguläre Prozesse mit Exit 0 und 103 isolierte Executor-Fehlerkontrollen mit erwartetem Exit 1. Jedes tatsächliche Exit-Ergebnis entspricht dem erwarteten.
- 2384 eindeutige XTM-Checks: 2204 bisherige (mit den 22 ausdrücklich dokumentierten Umbenennungen) und 180 zusätzliche. **62 positive und acht negative Originalverträge**, insgesamt **70 PASS / 0 FAIL / 54 NOT-RUN**.
- **CTM 262 PASS / 4 FAIL / 7 NOT-RUN**; die vier bisherigen FAILs bleiben unverändert.
- 12100 bisherige Lisp-Kernprüfungen, 146 XML-Qualifikationsprüfungen, 2 Python-Unittests, 16294 NFC-Oracle-Vergleiche.
- Stufenprüfungen: XTM-MERGEMAP 217, REGISTERED-ORIGINALS 286, REGISTERED-NEGATIVES 25, PROLOG 171, EMPTY2 13, CTM-INTEGER 112, TRIPLE 226, ENCODING 722. Include, sämtliche Slice-20-Stufen und CTM/XTM-Mergemap sind im vollständigen Lauf enthalten.
- CXTM-Mismatch, XML-Fehler, XTM-Ablehnung, Unsupported und echte native TMDM-Reifier-Konflikte führen bei positiven Originalverträgen niemals zu PASS. Die neue falsche Condition `REIFICATION-ERROR/:foreign-reifier` wird als falsche Erwartungsursache statt `:reifier-conflict` zurückgewiesen. Beide neuen Original-Executors werden in allen fünf positiven Fehlermodi geprüft. Alle bisherigen Executor-Kontrollen bleiben aktiv.
- 48 bisherige Nicht-XTM-Ergebnisberichte geprüft; ausschließlich zwei erzeugte Integrationskopien enthalten die oben explizit begrenzten Fixture-Änderungen. 2006 Korpusdateien, 3453 historische Reportdateien und 5711 geschützte Basisdateien per SHA-256 verifiziert.

Unveränderte CTM-FAILs: `ctm/in/include-template.ctm`, `ctm/in/include-wildcard2.ctm`, `ctm/in/occurrence-datetime-timezone2.ctm`, `ctm/in/occurrence-datetime2.ctm`.


Die Tests laufen jeweils in frischen Prozessen ohne SBCL-Benutzer-/Systeminitialisierung mit den überprüften lokalen gepinnten Abhängigkeiten und vorhandenen XML-Patches. Jeder Testprozess steht unter `sandbox-exec` mit Netzwerk- und Repository-Schreibsperre. Ausgaben entstehen außerhalb des Repository und werden erst nach erfolgreicher Abnahme übernommen. Kein vollständiger Nix-Neubau; keine neuen Abhängigkeiten oder Downloads und keine langlebigen Lisp-Images.

Reproduktion: `python3 scripts/validate-slice-21o.py --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl --output /private/tmp/<neues-verzeichnis>`.

[Integrität](../reports/slice-21o/integrity.json) schützt Originale, Baselines, historische Reports und sämtliche unveränderten Basisdateien. [Artefaktmanifest](../reports/slice-21o/artifacts.json) enthält die SHA-256 der gemeinsam committeten neuen Dateien; [Abnahmeprüfung vor Commit](../reports/slice-21o/precommit-audit.json) belegt den zulässigen Umfang. Keine HyperDoc-Änderung, kein Push oder Deployment. Slice 21O endet mit dem lokalen Commit.
