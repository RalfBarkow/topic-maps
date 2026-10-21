# Slice 22D — Textuelles XTM resourceData mit absoluten Datentyp-IRIs

Stand: 21. Oktober 2026. Basis/Parent: `b5c5ea5cc84dd31104045d032c25880b8bd62839`. Branch: `codex/conformance-slice-22d`.

Der vorhandene XTM-Reader erhält bei textuellem `resourceData` jetzt jede validierte absolute Datentyp-IRI und den davon unabhängigen Ressourcenwert. Genau ein zusätzlicher positiver Originalvertrag wurde nativ geprüft, bytegenau bestanden und im bestehenden ASDF-/Konformitäts-Harness registriert: `xtm2/in/variant-datatype-unknown.xtm`.

**`xsd:anyType` ist ein gültiger normativer Datentyp. Seine besondere XTM-Verarbeitung ist noch nicht implementiert und bleibt ausdrücklich Slice 22I.** Der Reader meldet deshalb `XTM-UNSUPPORTED/:resource-data-datatype`, keinen Fehler einer ungültigen Datentyp-IRI. Das gilt derzeit sowohl für reine Textinhalte als auch für eingebettetes XML. Diese Fähigkeit wird weder als implementiert noch als neuer Original-PASS gezählt. [Maschinenlesbare Fähigkeitslücke](../reports/slice-22d/anytype-capability-gap.json).

## Tatsächlicher Konformitätsstand

| Korpus | Vorher PASS / FAIL / NOT-RUN | Nach vollständiger Ausführung PASS / FAIL / NOT-RUN |
|---|---|---|
| XTM 2.0 | 71 / 0 / 53 | 72 / 0 / 52 |
| CTM | 262 / 4 / 7 | 262 / 4 / 7 |
| Gesamt | 333 / 4 / 60 | 334 / 4 / 59 |

Die bisherigen 71 XTM-Case-Records und sämtliche bisherigen Originalmodelle/-ausgaben sind unverändert. Die vier CTM-FAILs bleiben `include-template.ctm`, `include-wildcard2.ctm`, `occurrence-datetime-timezone2.ctm`, `occurrence-datetime2.ctm`. Synthetische Gegenproben und Executor-Fehlerkontrollen erhöhen keine Korpus-PASS-Zahl.

## Normative Herleitung und Evidenzgrenzen

`observed` bezeichnet lokale Originalbytes und wirkliche Prozessresultate; `derived` bezeichnet die begrenzte Herleitung aus den folgenden Quellen; `inferred` bezeichnet die spätere Wiederverwendbarkeit der gemeinsamen Operation. Keine Hypothese wird als beobachtetes Ergebnis geführt.

**Derived, XTM:** [XTM 2.0 §§4.16.1–4.16.3](https://www.isotopicmaps.org/sam/sam-xtm/) verlangt für ein vorhandenes `datatype` eine absolute IRI. §4.16.2 verwendet bei fehlendem Attribut `xsd:string`, ansonsten den Attributwert als Datentyp. `xsd:anyURI` hat die besondere IRI-Verarbeitung nach §4.3.4. `xsd:anyType` führt zum besonderen XML-Kanonisierungsverfahren aus §4.16.3. Für andere Datentypen werden Unicode-Zeichen zum Ressourcenwert verbunden; Elementkinder sind dort unzulässig. Eine unbekannte Datentyp-IRI allein begründet keine Ablehnung. §4.12 ordnet den Variant dem Parent Name zu und vereinigt dessen Scope mit dem expliziten Scope.

**Derived, TMDM:** [TMDM §§4.4, 5.5 und 6.4](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/) trennt textuellen Ressourcenwert und Datentyp. Ein Datentyp benötigt keinen zusätzlichen Topic. Variant-Gleichheit berücksichtigt Parent, Wert, Datentyp und Scope; bei Normalisierung bleiben die vereinigten Item-Identifier und die zusammengeführten Reifier erhalten. Der Variant-Scope muss den Name-Scope echt enthalten.

**Derived, CXTM:** Die geprüfte [öffentliche CXTM-Fassung §§3.14, 3.16 „Other“ und 3.20](https://www.isotopicmaps.org/cxtm/cxtm.html) beschreibt Datentypausgabe, Werterhaltung für andere Datentypen und NFC bei der Serialisierung. Bestehende besondere Kanonisierungen bekannter Datentypen bleiben unverändert; etwa wird der native Integer-Text `+00042` nicht beim XTM-Import umgeschrieben. Der Originalfall `BOGUS` wird unabhängig davon vollständig mit seiner gepinnten Baseline verglichen.

Die Editionsgrenzen aus [Slice 22C](slice-22c-normative-decisions.md) gelten weiter: XTM-H (2006-06-19) und TMDM-H (2006-06-18) enthalten redaktionelle Erklärungen ihrer Identität mit der veröffentlichten Ausgabe; ein eigener PDF-Abgleich erfolgte nicht. Für CXTM-H (2009-01-27) ist die endgültige Publikationsidentität weiterhin nicht unabhängig belegt. Slice 22D entscheidet keinen der zwölf offenen C-Fälle aus 22C und ändert keine historischen Einstufungen. Normtexte wurden lesend geprüft; keine neue Normkopie oder Abhängigkeit wurde heruntergeladen.

## Native Vorprüfung vor jeder Reader-Änderung

**Observed:** Die native Vorprüfung lief am 20. Oktober um 21:53:30–21:53:31 UTC in frischem SBCL 2.5.4 mit Netzwerk-/Repository-Schreibsperre. Der Reader-SHA-256 entsprach dabei unverändert dem Ausgangscommit: `c4aada0e70b2904fce3931884a24fb9d7dcfa8f1d10b724a82f23f302adf9143`.

Elf Checks verwenden ausschließlich vorhandene TMDM-/CXTM-APIs: `intern-topic`, `add-default-name`, `add-variant`, `add-item-identifier`, `set-item-reifier`, `merge-topics`, die nativen `canonical-*`-Operationen und `canonicalize-octets`. Der Wert ` 42 & 馬🦊 ` bleibt unter `https://types.example.invalid/custom` erhalten; derselbe Wert mit `urn:types:other` bleibt ein anderer Variant. Datentyp und Wert erzeugen keinen Topic.

Das Zusammenführen der Scope-Topics normalisiert zwei gleiche Variants, vereinigt beide Item-Identifier und Reifier und erhält die inverse Reifier-Beziehung. Tatsächlich verschiedene alte Variant-Handles führen über `canonical-variant` zum aktuellen Objekt (`EQ`); eine weitere identische Erzeugung liefert wieder dessen kanonischen Handle. Wiederholte CXTM-Ausgabe erhält das native Modell und den benutzerdefinierten lexikalischen Wert.

[Vorprüfungsmodell und elf Checks](../reports/slice-22d/native-preflight.json), [Provenienz mit unverändertem Readerhash](../reports/slice-22d/native-preflight-provenance.json), [Log](../reports/slice-22d/native-preflight.log). Zwei vorausgehende Testkorrekturen betrafen die Reihenfolge der Handle-Auflösung nach einer Mutation und den bereits erforderlichen CXTM-Parameter `base-locator`; sie änderten keine Produktionssemantik. Dieselben elf Checks laufen zusätzlich im regulären ASDF-Testlauf.

## Begrenzte Reader-Änderung

Nur `src/xtm/reader.lisp` enthält Produktionsänderungen:

- `validate-source` behält die vorhandene absolute IRI-, Prozent-/UTF-8- und Referenzvalidierung bei. Die frühere Beschränkung auf String/URI entfällt. `anyType` bleibt eine spezifische Unsupported-Fähigkeit. Elementkinder anderer Ressourcenwerte ergeben `XTM-REJECTION/:unexpected-child`.
- `read-resource-value` extrahiert die vorhandene gemeinsame Wertoperation: `resourceRef` und `anyURI` verwenden die bisherige IRI-Auflösung; andere textuelle Werte und ihre Datentyp-Attribute bleiben exakt erhalten. Es erfolgen weder Topic-Lookup noch Ressourcenabruf anhand von Wert oder Datentyp.
- `read-variant` übergibt diese beiden Werte an das bestehende `add-variant`. Scope-Vereinigung, Identifikatoren, Reification, Normalisierung und kanonischer Rückgabehandle bleiben Aufgaben der vorhandenen TMDM-Operationen.

Kein Sonderfall für Dateiname, `BOGUS` oder `http://example.com/bogus`. Keine Änderung an TMDM, CTM, CXTM, XML oder der CTM/XTM-Mergemap-Implementierung.

**Observed/inferred, gemeinsamer Kontext:** Vier synthetische qualifizierte XML-Quellen (benutzerdefinierter Datentyp, Standardstring, `anyURI`, `resourceRef`) durchlaufen dieselbe validierte Ressourcenwertoperation. Ihre Ergebnisse werden an die bestehenden nativen `add-variant`- und `add-occurrence`-APIs gegeben und auf gleiche Werte/Datentypen, richtige Parents und ausbleibende Topic-Erzeugung geprüft. Dies ist ein Wiederverwendungsnachweis, keine XTM-Occurrence-Deserialisierung. Der öffentliche Reader weist ein XTM-`occurrence` weiterhin als Unsupported zurück; seine Implementierung bleibt Slice 22E.

## Originalquelle und vollständiger CXTM-Vergleich

[Originalquelle](../vendor/cxtm/xtm2/in/variant-datatype-unknown.xtm), [unveränderte Baseline](../vendor/cxtm/xtm2/baseline/variant-datatype-unknown.xtm.cxtm), Korpuscommit `cd165b150176c1d6842b37be9cc9051b40d4996b`.

```xml
<topicMap xmlns="http://www.topicmaps.org/xtm/" version="2.0">
  <topic id="topic">
    <name>
      <value>Topic</value>
      <variant>
        <scope>
          <topicRef href="#scope"/>
        </scope>
        <resourceData datatype="http://example.com/bogus">BOGUS</resourceData>
      </variant>
    </name>
  </topic>
</topicMap>
```

Diese lesbare Darstellung entfernt allein die abschließenden Leerzeichen der ersten Zeile; der JSON-Bericht enthält die vollständigen Originalbytes als Hex und Text.

| Merkmal | Tatsächlicher Befund |
|---|---|
| Originalgröße | 340 Bytes |
| Quell-SHA-256 | `180e23d77c902891c85ff58e3d88a7759dfb6ec59d5788c9bc115f438b515566` |
| CXTM Ist / Soll | 579 / 579 Bytes |
| Ist- und Soll-SHA-256 | `67c9e04883d378bb0fe3ea77f5bc6b7ca7b464a7debd68cf293c9fba6380c289` |
| Erste abweichende Byteposition | null, keine Abweichung |
| Condition / Code / Position / Cause | null / null / null / null |
| Qualified-Parser-Aufrufe im Primärimport | genau 1, Octet-Vektor `EQ` mit Originalbytes |

Document IRI: `https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/variant-datatype-unknown.xtm`. Ein zweiter Import mit anderem Source Key und gleicher Document IRI ergibt dieselben Modellwerte und CXTM-Bytes. Kein synthetisches Ersatzmodell wird als Originalvertrag gezählt.

Das wirkliche Modell enthält drei Topics, einen Name, einen Variant und keine Associations/Occurrences:

| Objekt | Identität und native Beziehungen |
|---|---|
| Owner | II `Document IRI#topic`; keine SI/SL |
| Standard-Name-Type | SI `http://psi.topicmaps.org/iso13250/model/topic-name`; kein II/SL |
| Name | Value `Topic`; Parent `EQ` Owner; Type `EQ` Standard-Type; leerer Scope |
| Theme | II `Document IRI#scope`; keine SI/SL |
| Variant | Value `BOGUS`; Datatype `http://example.com/bogus`; Parent `EQ` kanonischer Name; einziges Theme `EQ` zum kanonischen `#scope`-Topic |

Map, Name und Variant haben keine Item-Identifier oder Reifier; inverse Reifier-Beziehungen sind leer. Die Datentyp-IRI erzeugt keinen vierten Topic. Wiederholte Kanonisierung bleibt deterministisch und erhält Modell, Referenzen und gehaltene Handles. [Vollständiger Original-/Modellbericht](../reports/slice-22d/after/original-contract.json), [tatsächlich erzeugte CXTM-Datei](../reports/slice-22d/after/actual/variant-datatype-unknown.xtm.cxtm).

## Dauerhafte Tests und Retargetings

`tests/xtm-resource-datatypes.lisp` ergänzt die bestehenden Testfunktionen und Case Records. `topic-maps/xtm/tests` lädt die Datei; `topic-maps.xtm.tests:run-tests` ruft Originalvertrag und Gegenproben tatsächlich auf. Insgesamt 72 eindeutige registrierte IDs: 64 positive und acht bereits qualifizierte negative Originale. Die bisherigen 2.396 Checks bleiben in relativer Reihenfolge erhalten; zwei Namen werden passend zum Retargeting umbenannt. 126 zusätzliche Checks ergeben tatsächlich 2.522 erfolgreiche XTM-Checks.

Positive Gegenproben umfassen HTTP-/URN-/Unicode-Datentypen, unveränderte Prozentnotation des Datentyps, Unicode-/Whitespace-/XML-Escaping, leere Werte, Standard-/explizite Strings, Integer-Lexikalform, erhaltene `anyURI`-Auflösung sowie Gleichheitsunterscheidung nach Wert und Datentyp. Drei SI-/SL-/II-Merging-Gegenproben beobachten echte alte Variant-Handles, Parent-/Theme-Identität, Identifier-Vereinigung, Reifier-Merging und inverse Referenzen.

23 negative Gegenproben unterscheiden acht ungültige Datentyp-IRIs, acht verbotene Elementkind-Kombinationen, zwei gültige aber unimplementierte `anyType`-Quellen, unbekannte XTM-Struktur, weiterhin unimplementierte Occurrences, wirkliche native Reifier-/Scope-Konflikte und fehlerhaftes Roh-UTF-8. Conditions bleiben nach XML, XTM-Syntax, Unsupported und TMDM-Konflikten getrennt. [Alle Modelle, Checks und Conditions](../reports/slice-22d/after/xtm.json).

**Retargeting bestehender Prüfziele:** 21 Quellzeilen in elf Testdateien werden auf gültiges, aber weiterhin unimplementiertes `xsd:anyType` umgestellt. Die bisherigen Prüfziele bleiben die Unterscheidung von Unsupported und Syntaxfehlern sowie die korrekte Cause-/Identitäts-/Atomizitätsbehandlung. Eine frühere Default-String-Quelle mit fremdem XML war normativ nicht gültig; ihr Unsupported-Prüfziel verwendet jetzt explizites `anyType`. Die tatsächliche Syntaxablehnung von Elementkindern unter Standardstring wird durch neue Gegenproben geprüft.

[retargetings.json](../reports/slice-22d/retargetings.json) enthält jede alte/neue Quellzeile, Ausgangshash, Hash direkt nach Retargeting und endgültigen Dateihash. Bei `xtm-identity.lisp` umfasst der endgültige Hash zusätzlich die Registrierung. [retargeted-control-observations.json](../reports/slice-22d/after/retargeted-control-observations.json) erhält alle 22 geänderten bisherigen Kontrollbeobachtungen einschließlich genauer Conditions und Positionen. Nicht jede geänderte Beobachtung ist ein Retargeting: vorhandene Elementkind-Rejections erhalten teilweise den präzisierten gemeinsamen Meldungstext.

**CTM/XTM-Mergemap:** Ausschließlich die eine synthetische Prüfquelle in `tests/ctm-xtm-mergemap.lisp` wechselt von Integer zu `anyType`. Unverändert geprüft werden `MERGEMAP-SOURCE-UNSUPPORTED`, die wirkliche `XTM-UNSUPPORTED`-Cause mit Code `resource-data-datatype`, Kind-Document-IRI und XML-Position sowie die Erhaltung des vorherigen Modells. Alle 217 Adapterchecks bestehen. Die drei serialisierten Adapterberichte sind byteidentisch; sie enthalten diese einzelne synthetische Quelltextänderung nicht. Deshalb liefern Quell-Diff, Retargeting-Bericht und Regressionslog gemeinsam die Evidenz.

## 124 Originaldiagnosen und 113 Executor-Fehlerkontrollen

Der unveränderte historische Reader-Diagnosetreiber wurde vor und nach der Änderung gegen alle 124 Originale ausgeführt. **Genau ein Unterschied:** `variant-datatype-unknown.xtm` wechselt von `XTM-UNSUPPORTED/:resource-data-datatype`, ungefähr 9:59, Cause null, zu erfolgreicher Deserialisierung mit bytegleicher Baseline und Condition null. Die übrigen 123 vollständigen Diagnosen sind gleich. [Diagnosedelta](../reports/slice-22d/after/diagnostic-changes.json).

Die bisherigen 108 Executor-Fehlerkontrollen bleiben aktiv. Der neue Treiber ist eine dokumentierte Fortführung des bisherigen Executors, keine zweite Testarchitektur. Seine Unsupported-Quelle verwendet nun `anyType`; bestimmte Variant-Reifier-Konfliktquellen verwenden zwei verschiedene Werte desselben benutzerdefinierten Datentyps. Die tatsächliche Ablehnungsursache und die bisherigen Case-Status/Outcomes bleiben erhalten. [Executor-Retargetings](../reports/slice-22d/executor-retargetings.json).

Fünf neue isolierte Kontrollen richten sich gegen den neuen Original-Case-Record. XML-/XTM-/Unsupported-/TMDM-Kontrollen verarbeiten wirkliche Ersatzbytes durch den öffentlichen Reader. Der native Reifier-Konflikt wird nicht künstlich signalisiert. Die Byteabweichung verändert ein Byte nach echter Kanonisierung.

| Modus | Condition / Code | Zeile:Spalte | Zielstatus / Outcome | Erhaltene frühere PASS |
|---|---|---|---|---:|
| Byteabweichung | keine; erste Abweichung 0 | – | fail / cxtm-mismatch | 71 |
| XML | XTM-XML-ERROR / xml-not-well-formed; Cause WELL-FORMEDNESS-VIOLATION | 1:11 | fail / execution-error | 71 |
| XTM | XTM-REJECTION / invalid-id | 1:81 | fail / execution-error | 71 |
| Unsupported | XTM-UNSUPPORTED / resource-data-datatype | 1:210 | unsupported / unsupported | 71 |
| TMDM | REIFICATION-ERROR / reifier-conflict | null | fail / execution-error | 71 |

Alle 113 Fehlerprozesse liefern den geforderten Exit 1; kein beschädigter Zielvertrag zählt als PASS. Die fünf neuen Kontrollen erhalten jeweils alle 71 vorausgehenden Original-PASS. Historische Kontrollen brechen beim bisherigen Ziel ab und erhalten denselben erfolgreichen Präfix; spätere Verträge werden dort nicht fälschlich als ausgeführt dargestellt. Der reguläre Lauf weist separat alle 72 PASS nach. [Kontrollauswertung](../reports/slice-22d/after/failure-controls.json) und die einzelnen JSON-/Logdateien enthalten die vollständigen Ergebnisse.

## Vollständige Offline-Regression und Integrität

Die Ausgangsregression auf dem sauberen Ausgangscommit reproduzierte 2.396 XTM-Checks, 12.100 TMDM-/CTM-/CXTM-Checks, 124 Originaldiagnosen und 108 Fehlerkontrollen. Der unveränderte 22B-Validator bleibt als Werkzeugprovenienz erkennbar: seine historischen Basis-/„new“-Felder beziehen sich auf dessen ursprünglichen Slice, nicht auf zusätzliche 22D-Registrierungen. Der tatsächliche 22D-Ausgangszustand steht separat in [initial-state.json](../reports/slice-22d/initial-state.json).

Der erfolgreiche Endlauf vom 20. Oktober 22:05:28–22:08:44 UTC (21. Oktober 00:05:28–00:08:44 Europe/Zurich) umfasst 119 isolierte Prozesse: sechs reguläre mit Exit 0 und 113 Kontrollen mit erwartetem Exit 1. SBCL 2.5.4 startet jeweils ohne System-/Benutzerinitialisierung. Netzwerk und Schreibzugriff auf beide Repositories sind für die Testprozesse gesperrt; lokale gepinnte Abhängigkeiten und temporäre Buildkopien werden weiterverwendet.

| Teil | Tatsächliches Ergebnis |
|---|---:|
| TMDM / CTM / CXTM einschließlich Include / Mergemap | 12.100 Checks |
| XTM einschließlich Names / Variants / Ressourcen / Identifier / Reification | 2.522 Checks |
| XML-Qualifikation | 146 Checks |
| CTM/XTM-Mergemap | 217 Checks |
| registrierte CTM-Originale positiv / negativ | 286 / 25 Checks |
| Prolog / empty2 / CTM-Integer / Triple / Encoding | 171 / 13 / 112 / 226 / 722 Checks |
| Python-Unittests | 2 |
| NFC-Oracle | 16.294 Vergleiche |
| Originaldiagnosen | 124, genau eine erwartete Änderung |
| Executor-Fehlerkontrollen | 113 = 108 erhalten + 5 neu |
| bisherige Nicht-XTM-Berichte | 48 byteidentisch |
| gepinnte Korpusdateien | 2.006 Größen-/SHA-256-Prüfungen bestanden |
| historische Berichtsdateien | 4.929 SHA-256-Prüfungen bestanden |

[execution.json](../reports/slice-22d/after/execution.json) enthält Kommandos, Zeitstempel, Exitcodes und Abnahme; [integrity.json](../reports/slice-22d/after/integrity.json) enthält die vollständigen geschützten Ausgangshashes. [final-audit.json](../reports/slice-22d/final-audit.json) prüft zusätzlich Quellen, Index-/Änderungsumfang, gesicherte Evidenz und unveränderten HyperDoc-Zustand.

Ein erster Gesamtversuch scheiterte korrekt an der noch nicht retargetierten Mergemap-Gegenprobe; er wird [separat als Entwicklungsfehler](../reports/slice-22d/development-regression-failure.json) aufbewahrt und nicht als erfolgreiche Regression gezählt. Ein während des Nutzungslimits von der automatischen Freigabeprüfung abgelehnter Leseaufruf wurde nicht ausgeführt. Keine Umgehung der Freigabeprüfung und keine Änderung an `~/.nix-profile`; nach ausdrücklicher Fortsetzung funktionierte die reguläre Freigabe. [Freigabeereignis](../reports/slice-22d/approval-events.json).

Reproduktion mit neuen Ergebnissen außerhalb des Repositories:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate-slice-22d.py --output /private/tmp/topic-maps-22d-new-run
```

`--audit-only` prüft gespeicherte Ausführungen anhand ihrer Logs, Quell- und Berichthashes; es behauptet keinen neuen Testlauf. Eine spätere Änderung von Reader oder Tests erfordert eine neue vollständige Ausführung.

## Delta zur Abschlussmatrix und verbleibende Arbeit

Gegenüber der unveränderten 22A-Matrix sind genau zwei Registrierungen hinzugekommen: der bereits in 22B registrierte `variant-duplicate-reifier2.xtm` und jetzt `variant-datatype-unknown.xtm`. Gegenüber dem unmittelbaren Ausgangscommit 22C gibt es genau einen zusätzlichen PASS und eine allgemeine neue textuelle Datentypfähigkeit. 63 Korpusfälle bleiben offen (vier FAIL, 59 NOT-RUN). [Vollständiges Delta](../reports/slice-22d/after/closure-delta.json).

Die 13 Entscheidungen aus 22C einschließlich der zwölf offenen C-Fälle bleiben bytegenau unverändert. Occurrence-Deserialisierung (22E) und die normative `anyType`-Verarbeitung (22I) bleiben künftige Arbeit; weitere offene Features werden nicht implementiert. Originalquellen, Baselines, Corpus-Lock, historische Berichte und HyperDoc sind unverändert. Kein Push, Deployment, Download oder langlebiger Image-Load. Slice 22D endet mit dem lokalen Commit dieser Reader-Erweiterung, Tests, Dokumentation und neuen Evidenz.
