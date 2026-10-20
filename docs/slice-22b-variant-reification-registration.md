# Slice 22B — Letzten beobachteten Variant-Reification-Vertrag registrieren

Stand: 20. Oktober 2026. Basis/Parent: `b12ece02faa039e816fca3750acd9eceb6be1513`; Branch `codex/conformance-slice-22b`.

Genau ein zusätzlicher positiver Originalvertrag ist dauerhaft registriert und im regulären ASDF-Testlauf ausgeführt: `xtm2/in/variant-duplicate-reifier2.xtm`. Keine neue Sprachfähigkeit und keine neue normative Entscheidung. XTM-Reader, TMDM, CTM, CXTM, XML, Originalquellen, Baselines, historische Berichte und HyperDoc blieben unverändert.

| Korpus | Vorher PASS / FAIL / NOT-RUN | Tatsächlich nachher PASS / FAIL / NOT-RUN |
|---|---|---|
| XTM 2.0 | 70 / 0 / 54 | 71 / 0 / 53 |
| CTM | 262 / 4 / 7 | 262 / 4 / 7 |
| Gesamt | 332 / 4 / 61 | 333 / 4 / 60 |

## Originalquelle und vollständiger Vergleich

[Original](../vendor/cxtm/xtm2/in/variant-duplicate-reifier2.xtm), [gepinntes CXTM](../vendor/cxtm/xtm2/baseline/variant-duplicate-reifier2.xtm.cxtm), Korpuscommit `cd165b150176c1d6842b37be9cc9051b40d4996b`.

| Größe / Hash | Tatsächlicher Befund |
|---|---|
| Originalgröße | 543 Bytes |
| Original-SHA-256 | `87b740c6ec7d11b485b223cb5c28807bce9259d04c2d586ea557e6cd10c3faf4` |
| CXTM Ist / Soll | 702 / 702 Bytes |
| Ist-SHA-256 | `014773fca95a2b7bb70038f8e118d402d311a2804f54f105ff05ee53c7eb0a60` |
| Soll-SHA-256 | `014773fca95a2b7bb70038f8e118d402d311a2804f54f105ff05ee53c7eb0a60` |
| Vollständige Bytegleichheit | true |
| Erste abweichende Byteposition | null, keine Abweichung |
| Tatsächliche Condition | null |

Lesbare Darstellung des vollständigen Quelltexts; die bytegenauen Whitespace-Daten stehen im verlinkten Original und im JSON-Bericht:

```xml
<topicMap xmlns="http://www.topicmaps.org/xtm/" version="2.0">
  <topic id="topic">
    <name>
      <value>Topic</value>
      <variant reifier="#reifier">
        <scope>
          <topicRef href="#command"/>
        </scope>
        <resourceData>TOPIC!</resourceData>
      </variant>
    </name>
    <name>
      <value>Topic</value>
      <variant reifier="#reifier">
        <scope>
          <topicRef href="#command"/>
        </scope>
        <resourceData>TOPIC!</resourceData>
      </variant>
    </name>
  </topic>
</topicMap>
```

Die Quelle enthält einen Topic `id="topic"` und zwei `name`-Elemente. Jedes hat den Wert `Topic` und genau einen `variant reifier="#reifier"`, dessen Scope auf `#command` und dessen textuelles `resourceData` auf `TOPIC!` lautet. Keine eigenen Item-Identifier am Name oder Variant, keine Reification des Name oder der Map.

Document IRI: `https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/variant-duplicate-reifier2.xtm`. Source Key des Primärimports: `xtm2/in/variant-duplicate-reifier2.xtm`. Die vollständigen Original-/Soll-/Istbytes, das native Modell und der Handle-Nachweis stehen in [original-contract.json](../reports/slice-22b/after/original-contract.json); die erzeugte Ausgabe in [actual CXTM](../reports/slice-22b/after/actual/variant-duplicate-reifier2.xtm.cxtm).

## Native Modell- und Identitätsprüfung

Der Vertrag verarbeitet die unveränderten Originaloctets über `topic-maps.xtm:deserialize-octets`. Ein passiver Beobachter am bestehenden qualifizierten XML-Parser weist genau einen Primärparseraufruf und `EQ` mit dem Original-Octet-Vektor nach. Er verwendet den wirklichen resultierenden XML-Quellbaum für die Prüfung beider Name-/Variant-Elemente; eine manuell konstruierte Ersatzmap wird nicht als Originalvertrag gezählt.

Das tatsächliche Modell hat vier Topics, keine Associations, einen Name und einen Variant:

| Objekt | Native Eigenschaften und Referenzen |
|---|---|
| Owner-Topic | II `Document IRI#topic`; Parent ist die aktuelle Map |
| Standard-Name-Type | SI `http://psi.topicmaps.org/iso13250/model/topic-name`; kein II |
| Name | Value `Topic`; Parent `EQ` Owner; Type `EQ` Standard-Type; leerer Scope; kein II/Reifier |
| Scope-Topic | II `Document IRI#command`; kein SI/SL; einziges Variant-Theme |
| Reifier-Topic | II `Document IRI#reifier`; kein SI/SL; kein Identifier wird auf Name/Variant übertragen |
| Variant | Value `TOPIC!`; Datatype `http://www.w3.org/2001/XMLSchema#string`; Parent `EQ` kanonischer Name; einziges Scope-Theme `EQ` zum `#command`-Topic |
| Reifier-Inverse | `(item-reifier variant)` ist `EQ` zum kanonischen Reifier-Topic; `(topic-reified reifier)` ist invers `EQ` zum kanonischen Variant |

Alle übrigen Topic-Reified-Werte sind null; Map, Name und Variant haben keine Item-Identifier. Alle Topic-Parents und Name-/Variant-/Scope-/Type-Referenzen verweisen auf aktuelle native Objekte. Keine Occurrences oder Roles wurden unbeabsichtigt erzeugt.

**Tatsächlich beobachtete alte Handles:** Während dieses öffentlichen Imports werden die Ergebnisse der beiden `read-name`-Aufrufe und die beiden verschiedenen Variant-Handles unmittelbar vor ihrer gemeinsamen Normalisierung festgehalten. Der zweite Name-Aufruf verwendet bereits denselben nativen Name (`sameRawNameHandleEQ = true`); der Test erfindet deshalb keinen zweiten veralteten Name. Beim Variant wird eine reale Ersetzung beobachtet: die beiden verschiedenen festgehaltenen Handles führen über `canonical-variant` zum selben aktuellen Variant, und mindestens einer ist roh nicht `EQ` zu diesem Repräsentanten. Beide Name-Handles führen über `canonical-topic-name` zum aktuellen Parent. Reifier und inverse Referenz entsprechen auch beim Zugriff über die alten Variant-Handles dem aktuellen Objekt.

Die Beobachter an Parser, `read-name` und `normalize-variants` verändern weder Rückgaben noch Normalisierungsregeln. `unwind-protect` stellt alle ursprünglichen Funktionsdefinitionen auch bei Fehlern wieder her; nur die Wegwerf-Testprozesse werden instrumentiert. Es gibt keine dauerhafte Reader-/TMDM-Änderung und keinen langlebigen Image-Load.

**Zusätzliche Abnahme:** Ein zweiter Import mit anderem Source Key und derselben Document IRI erzeugt dieselben modellierten Werte/Identifikatoren und CXTM-Bytes. `EQ` wird innerhalb der jeweiligen Map geprüft, nicht zwischen unabhängig erzeugten Maps. Wiederholte CXTM-Kanonisierung ist deterministisch und erhält den vollständigen vorhandenen Snapshot einschließlich aktueller und festgehaltener alter Handles/Forwarding- und Reifier-Beziehungen.

## Registrierung und ASDF-Ausführung

Die Ergänzung steht in `tests/xtm-variant-reification.lisp` als `variant-reifier-followup-original-contract`. Sie verwendet die vorhandenen `make-test-case`, `record-original-result`, Case Records, Modellserializer, Snapshot- und CXTM-Funktionen. Der tatsächliche Aufruf ist in `topic-maps.xtm.tests:run-tests` ergänzt; `topic-maps/xtm` ruft diesen bestehenden Testpfad über `topic-maps/xtm/tests` auf. Die ASDF-Beschreibung und der Reportumfang wurden von 62 auf 63 positive Originale aktualisiert. Keine neue Testarchitektur oder neues ASDF-System.

Der reguläre Lauf weist 71 eindeutige IDs nach: 63 positive und acht unverändert qualifizierte negative Originale. Die ersten 70 Case Records und sämtliche bisherigen Originalausgaben/negativen Ursachen sind mit Slice 22A unverändert gleich. Alle 2.384 bisherigen XTM-Checks bleiben in derselben relativen Reihenfolge erhalten; zwölf neue Prüfungen ergeben tatsächlich 2.396 erfolgreiche Checks. Der neue Vertrag wird vor der Registrierung von PASS deserialisiert, nativ geprüft und vollständig verglichen. Jede vorher ausgelöste Condition wird im bestehenden Executor als Fehler/Unsupported registriert und anschließend durch ASDF propagiert.

## Executor-Fehlerkontrollen

Die bisherigen 103 Kontrollen werden erneut über ihren unveränderten historischen Treiber ausgeführt. Alle Verhaltensfelder ihrer JSON-Ergebnisse sind gleich; allein der feste beschreibende `/scope`-Text nennt nun 63 statt 62 positive Verträge. Das ist keine Erhöhung der in einem abgebrochenen Kontrolllauf tatsächlich ausgeführten PASS-Zahl. Vorher-/Nachherhashes und die exakt zugelassene Metadatenabweichung stehen in [retained-fault-reports.json](../reports/slice-22b/after/retained-fault-reports.json).

Fünf neue Kontrollen richten sich ausdrücklich gegen den neuen positiven Case Record. Byteabweichung ändert ein Ausgabebyte nach der echten Kanonisierung. Die übrigen Kontrollen leiten ausschließlich beim Ziel-Source-Key andere Testbytes durch den echten öffentlichen Reader: fehlverschachteltes XML, ungültige Topic-ID, ausgeschlossener Datentyp und zwei verschiedene Variant-Werte mit demselben Reifier. Keine manuell signalisierte Ersatzcondition; insbesondere entsteht der Reification-Konflikt wirklich durch die TMDM-Operationen.

| Modus | Tatsächliche Condition / Code | Zeile:Spalte | Executor-Outcome | Zielstatus | Erhaltene Original-PASS |
|---|---|---|---|---|---:|
| mismatch | keine | – | `cxtm-mismatch` | fail | 70 |
| xml | `XTM-XML-ERROR/:xml-not-well-formed` | 1:11 | `execution-error` | fail | 70 |
| xtm | `XTM-REJECTION/:invalid-id` | 1:81 | `execution-error` | fail | 70 |
| unsupported | `XTM-UNSUPPORTED/:resource-data-datatype` | 1:210 | `unsupported` | unsupported | 70 |
| tmdm | `REIFICATION-ERROR/:reifier-conflict` | – | `execution-error` | fail | 70 |

Alle fünf neuen und 103 bisherigen Kontrollprozesse enden wie verlangt mit Exit 1. Der neue Zielvertrag zählt in keinem Fehlerlauf als PASS. Native Conditions ohne Quellpositionsfelder werden mit null dokumentiert, nicht mit erfundenen XML-Positionen. [failure-controls.json](../reports/slice-22b/after/failure-controls.json) und die einzelnen Kontrollreports/Logs bewahren die konkreten Conditions einschließlich Causes. Der reguläre Originallauf hat weiterhin Condition null und Exit 0.

## Ausgangsbaseline, Diagnosevergleich und vollständige Regression

Vor den Teständerungen lief der vorhandene `validate-slice-21o.py` unverändert auf dem sauberen Ausgangscommit mit frischem SBCL 2.5.4. Alle 154 vergleichbaren Verhaltensberichte stimmen SHA-256- und bytegenau mit Slice 22A überein. Das umfasst bestehende XTM-Originalergebnisse und alle 124 Reader-Diagnosen. [Baselinekommandos](../reports/slice-22b/baseline/execution.json), [Vergleich](../reports/slice-22b/baseline-comparison.json) und [Anfangszustand](../reports/slice-22b/initial-state.json) sind neu gesichert. Historische „new“-Felder und Basisangaben des unveränderten alten Validators bleiben dessen Slice-21O-Provenienz; sie bezeichnen keine zusätzlichen 22B-Registrierungen.

Nach der Ergänzung lief die vollständige Regression erneut. Alle Lisp-Prozesse verwenden SBCL 2.5.4 ohne System-/Benutzerinitialisierung; Lisp startet mit `--no-sysinit --no-userinit`. Kindprozesse laufen mit Netzwerksperre und Dateischreibsperre für Topic Maps und HyperDoc. Vorhandene gepinnte Abhängigkeiten werden über den bisherigen Vorbereitungspfad verwendet. Buildkopien/FASLs und Ergebnisse liegen außerhalb der Repositories. Keine Downloads, kein vollständiger neuer Nix-Build, kein langlebiges Lisp-Image.

| Teil | Ergebnis nach der Registrierung |
|---|---:|
| TMDM/CTM/CXTM einschließlich Include/Mergemap | 12.100 Checks |
| Eigenständige XTM-Prüfungen | 2.396 Checks, 63 positive + 8 negative Originale |
| XML-Qualifikation | 146 Checks |
| CTM/XTM-Mergemap | 217 Checks |
| CTM registrierte positive / negative Originale | 286 / 25 Checks |
| Prolog / empty2 / CTM-Integer / Triple / Encoding | 171 / 13 / 112 / 226 / 722 Checks |
| Python-Unittests | 2 |
| NFC-Oracle | 16.294 Vergleiche |
| Executor-Fehlerkontrollen | 108, davon 5 neu; erwarteter Exit 1 |
| Reader-Diagnosen | 124 von 124 unverändert, vollständige JSON-Bytes identisch |
| Unveränderte Nicht-XTM-Berichte | 48 byteidentisch |

Die Abschlussausführung hat 114 Prozesse: sechs reguläre mit Exit 0 und 108 Fehlerkontrollen mit erwartetem Exit 1. Ein vorausgehender erfolgreicher ASDF-Prüflauf ist separat als `smoke-xtm.json/log` gesichert und wird nicht als zweiter Originalvertrag gezählt. [execution.json](../reports/slice-22b/after/execution.json) enthält alle Kommandos, Zeitstempel und Exitcodes; [after-diagnostics.json](../reports/slice-22b/after/after-diagnostics.json) und [diagnostic-changes.json](../reports/slice-22b/after/diagnostic-changes.json) belegen null Reader-Änderungen.

Die vier CTM-FAILs bleiben unverändert: `include-template.ctm`, `include-wildcard2.ctm`, `occurrence-datetime-timezone2.ctm`, `occurrence-datetime2.ctm`. Auch die sieben CTM-NOT-RUN und drei offenen negativen XTM-Originale werden nicht neu qualifiziert.

Die automatische Freigabeprüfung fiel während eines Leseaufrufs mit `Automatic approval review failed: You’ve hit your usage limit` aus; der Aufruf wurde nicht ausgeführt. Nach dem erneut erteilten Auftrag funktionierte die reguläre Freigabe wieder. Laufende Baseline und begonnener Branch wurden erhalten. Keine Änderung an `~/.nix-profile`, keine Umgehung einer Freigabeprüfung.

## Delta zur historischen Slice-22A-Matrix

[closure-delta.json](../reports/slice-22b/after/closure-delta.json) referenziert SHA-256 der unveränderten [Slice-22A-Matrix](../reports/slice-22a/matrix.json) und enthält alle 65 früher offenen Case-IDs mit Vorher-/Nachherstatus. Genau `xtm2/in/variant-duplicate-reifier2.xtm` geht von beobachtet erfolgreich/unregistriert (NOT-RUN) zu PASS. Die übrigen 64 offenen Originale bleiben statusgleich: vier FAIL und 60 NOT-RUN. Keine neue Sprachfähigkeit, keine vorweggenommene Slice-22C-Auslegung, keine Änderung der CTM-Abweichungen.

Der Abschlussplan und sämtliche Slice-22A-Dateien bleiben historische Evidenz. Die dort vorgeschlagenen weiteren Fähigkeiten und Normentscheidungen werden in diesem Slice nicht implementiert. Die Gesamtabnahmetore A, B und C bleiben offen; die reine Registrierungsaufgabe 22B ist abgeschlossen.

## Reproduktion und Integrität

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate-slice-22b.py \
  --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  --output /private/tmp/topic-maps-22b-reproduction
```

Der Default prüft die archivierte tatsächliche Vorher-Baseline gegen Slice 22A und führt die vollständige aktuelle Regression mit allen 108 Fehlerkontrollen neu aus. `--baseline` kann auf eine andere vollständig verifizierte Vorher-Ausführung zeigen; es ersetzt keine Testausführung durch erwartete Zähler. Die historische Vorher-Regressionsausführung liegt unter `reports/slice-22b/baseline`; das Wiederholkommando schreibt ausschließlich außerhalb des Repositories.

Von 6.323 zu Beginn verfolgten Dateien wurden ausschließlich `tests/xtm-variant-reification.lisp`, `tests/xtm-identity.lisp` und die Testsystembeschreibung in `topic-maps.asd` geändert. Alle übrigen 6.320 Ausgangsdateien, darunter 4.049 historische Reportdateien, bleiben bytegleich. Alle 2.006 Korpus-Lockeinträge sind nach Größe und SHA-256 geprüft. [integrity.json](../reports/slice-22b/after/integrity.json) bewahrt die Schutz- und ausgeführten Werkzeughashes. [Abschlussaudit](../reports/slice-22b/precommit-audit.json) und [Liefermanifest](../reports/slice-22b/artifacts.json) ergänzen Index-/Artefaktprüfungen.

HyperDoc blieb auf `306b7fd99fc2611a248e0927ce52a808abb7cc76`, sauber und ohne Lade-/Schreiboperationen. Die 14 in Slice 22A inspizierten Quelldateien wurden nur nach HEAD/Status/Hash erneut geprüft. Keine Produktionscode-, Korpus-, Baseline-, historische Report- oder HyperDoc-Änderung; kein Push und kein Deployment. Ende Slice 22B.
