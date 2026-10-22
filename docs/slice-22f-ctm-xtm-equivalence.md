# Slice 22F — CTM/XTM-Semantik über TMDM und CXTM

27 unmittelbar durch beide produktiven Reader eingelesene Quellpaare bestehen mit gleichen nativen TMDM-Eigenschaften und vollständig byteidentischen CXTM-Ausgaben. Die neue ASDF-Prüfung umfasst 487 Checks. Drei absichtlich verschiedene Maps behalten ihre Unterschiede; drei Fähigkeitsproben dokumentieren fehlende XTM-Unterstützung. Es gibt keine Änderung am Produktionscode und keine neue Originalkorpusregistrierung.

Ausgangscommit: `aeebbc7c6fdbf26642db0b7b5a358a3d04d62cca`; zu Beginn sauberer Index und Arbeitsbaum auf `codex/xtm-slice-22e`. Arbeitsbranch: `codex/ctm-xtm-slice-22f`. Das [Ausgangsaudit](../reports/slice-22f/initial-state.json) enthält die SHA-256 aller 8.110 damals versionierten Dateien. Der lokale Abschlusscommit enthält diesen Bericht zusammen mit Tests und Ausführungsevidenz; seine Identität wird im Abschluss geliefert.

## Normative Grundlage und Evidenzgrenzen

Die Äquivalenzerwartungen beziehen sich auf dieselben TMDM-Eigenschaften, nicht auf gleiche Syntax oder objektübergreifendes `EQ`. Fundstellen und Editionsgrenzen stehen auch in [normative-review.json](../reports/slice-22f/normative-review.json).

- [TMDM](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/), §§4.4, 5.2–5.8, 6.2–6.7, 7.2, 7.5: Eigenschaften der Information Items, Identitätskategorien, Gleichheit/Zusammenführung, Core Subjects und Reification.
- [XTM 2.0](https://www.isotopicmaps.org/sam/sam-xtm/), §§4.3.2, 4.4–4.17 und 4.21: Abbildung der XML-Konstrukte auf dieses Modell. §§4.15 und 4.18–4.19 begründen die separat dokumentierten Fähigkeitslücken.
- [CTM](https://www.isotopicmaps.org/ctm/ctm.html), §§3.3.6, 3.3.9–3.3.10, 3.4, 3.5, 3.9–3.13 und 3.16.3: Identitäten, Typisierung, Charakteristika, Literale, Reification und Inhaltsimport.
- [CXTM](https://www.isotopicmaps.org/cxtm/cxtm.html), insbesondere §3.1: Kanonisierung erhält die Map und einen expliziten Basis-Locator. Alle positiven Vergleiche verwenden dieselbe Basis auf beiden Seiten.

Die öffentlichen Texte sind datiert: TMDM 18.06.2006, XTM 19.06.2006, CTM Entwurf 31.03.2010, CXTM 27.01.2009. Eine unabhängige Prüfung gegen separat beschaffte veröffentlichte ISO-Ausgaben fand nicht statt. Der Slice beschafft keine Dateien und entscheidet die offenen Editions-/Template-Fragen aus Slice 22C nicht neu. Die nachstehenden Konstrukte verwenden die dokumentierten gemeinsamen Abbildungen. **Beobachtet** sind die Reader-Ergebnisse und Bytes; **aus den Referenztexten abgeleitet** ist die Erwartung gleicher Eigenschaften. Ein endlicher Testumfang beweist keine vollständige Sprachkonformität.

## Ausführungs- und Identitätskonvention

[tests/ctm-xtm-equivalence.lisp](../tests/ctm-xtm-equivalence.lisp) ergänzt das bestehende ASDF-System `topic-maps/ctm/xtm-tests`. Dessen Test-Operation führt zuerst die bestehenden 217 Adapterchecks und dann die neue Suite aus. Es gibt kein zweites Modell und keine konkurrierende Konformitätsregistrierung. Die vorhandene Check-Funktion wird mit dynamisch getrenntem Check-Speicher wiederverwendet; der bisherige Adapterbericht bleibt unverändert.

Jedes positive Paar verwendet die Document IRI `https://equivalence.example.invalid/<id>/map` für beide Reader und dieselbe CXTM-Basis. CTM-Identifier `a` und XTM `id='a'` behalten damit denselben Item Identifier `<Document IRI>#a`. SI, SL und zusätzliche II bleiben vollständig erhalten. Die Diagnose-Source-Keys `ctm:<id>` und `xtm:<id>` unterscheiden sich; wiederholtes tatsächliches Einlesen mit anderen Keys muss dieselben Eigenschaften und Bytes ergeben. Es gibt keine impliziten Ressourcenabrufe.

Die beiden Einstiege sind `topic-maps.ctm:deserialize-string` und `topic-maps.xtm:deserialize-octets`. XTM-Rohbytes gehen unverändert durch den qualifizierten XML-Parser. Passive, nach jeder Prüfung wiederhergestellte Beobachter protokollieren Parser- und Importaufrufe. Keine Vergleichsmap wird manuell als Ersatz aufgebaut.

Verglichen werden alle nativen Eigenschaftstupel: II/SI/SL, Name-/Variant-/Occurrence-Werte und Datentypen, Type, Scope, Parent, Rollen und Player sowie Reifier und inverse Referenzen. Mengen werden ausschließlich in temporären Testlisten sortiert. Modell und CXTM-Ausgabe werden nicht nachbearbeitet. Die vorhandenen Referenz- und Importvalidatoren prüfen kanonische `EQ`-Referenzen innerhalb jeder Map. Die unabhängigen Maps teilen keine Information Items. Wiederholte Kanonisierung muss identische Bytes liefern und sämtliche gehaltenen Handles sowie Modellzustände unverändert lassen.

## Tatsächliche positive Vergleiche

Alle folgenden Vergleiche bestehen: gleiche native Eigenschaften, kanonisches `EQ` innerhalb beider Maps, keine Condition, vollständige Bytegleichheit und keine erste Abweichung. Zählreihenfolge: Topics / Names / Variants / Occurrences / Associations / Roles / reifizierte Items. Die [Zusammenfassung](../reports/slice-22f/after/equivalence-summary.json) enthält Quell- und Ausgabe-SHA-256; die [vollständige Reader-Evidenz](../reports/slice-22f/after/retained/xtm-mergemap.equivalence.json) enthält beide vollständigen Modellzustände und sämtliche Quellen/Ausgaben.

| Paar | Native Struktur, beide Maps | CXTM CTM/XTM in Bytes |
|---|---|---:|
| `local-II` | 1 / 0 / 0 / 0 / 0 / 0 / 0 | 110/110 |
| `identity-SI` | 1 / 0 / 0 / 0 / 0 / 0 / 0 | 184/184 |
| `merge-SI` | 1 / 0 / 0 / 0 / 0 / 0 / 0 | 206/206 |
| `identity-SL` | 1 / 0 / 0 / 0 / 0 / 0 / 0 | 178/178 |
| `merge-SL` | 1 / 0 / 0 / 0 / 0 / 0 / 0 | 200/200 |
| `identity-II` | 1 / 0 / 0 / 0 / 0 / 0 / 0 | 138/138 |
| `merge-II` | 1 / 0 / 0 / 0 / 0 / 0 / 0 | 160/160 |
| `isa-instanceOf` | 5 / 0 / 0 / 0 / 1 / 2 / 0 | 956/956 |
| `isa-multiple-normalized` | 6 / 0 / 0 / 0 / 2 / 4 / 0 | 1384/1384 |
| `default-name` | 2 / 1 / 0 / 0 / 0 / 0 / 0 | 324/324 |
| `typed-scoped-name` | 4 / 1 / 0 / 0 / 0 / 0 / 0 | 549/549 |
| `unicode-whitespace-escaping` | 2 / 1 / 0 / 0 / 0 / 0 / 0 | 353/353 |
| `empty-name` | 2 / 1 / 0 / 0 / 0 / 0 / 0 | 320/320 |
| `duplicate-names` | 2 / 1 / 0 / 0 / 0 / 0 / 0 | 321/321 |
| `variant-inherited-scope` | 4 / 1 / 1 / 0 / 0 / 0 / 0 | 775/775 |
| `variant-datatype-integer` | 3 / 1 / 1 / 0 / 0 / 0 / 0 | 580/580 |
| `variant-datatype-decimal` | 3 / 1 / 1 / 0 / 0 / 0 / 0 | 581/581 |
| `variant-datatype-date` | 3 / 1 / 1 / 0 / 0 / 0 / 0 | 585/585 |
| `variant-datatype-datetime` | 3 / 1 / 1 / 0 / 0 / 0 / 0 | 599/599 |
| `variant-datatype-unknown-http` | 3 / 1 / 1 / 0 / 0 / 0 / 0 | 584/584 |
| `variant-datatype-unknown-urn` | 3 / 1 / 1 / 0 / 0 / 0 / 0 | 561/561 |
| `variant-resourceRef` | 3 / 1 / 1 / 0 / 0 / 0 / 0 | 582/582 |
| `variant-anyURI-data` | 3 / 1 / 1 / 0 / 0 / 0 / 0 | 582/582 |
| `variant-ctm-integer-star` | 3 / 1 / 1 / 0 / 0 / 0 / 0 | 584/584 |
| `name-variant-reification` | 5 / 1 / 1 / 0 / 0 / 0 / 2 | 778/778 |
| `map-reification` | 2 / 0 / 0 / 0 / 0 / 0 / 1 | 209/209 |
| `content-import` | 9 / 1 / 1 / 0 / 1 / 2 / 0 | 1626/1626 |

Die Type–Instance-Paare prüfen die tatsächlichen Associations mit den Core-Subject-SIs `type-instance`, `type` und `instance`, einschließlich Player-Referenzen. Zweifache identische Beziehungen normalisieren zu einer Association; zwei verschiedene Typen bleiben zwei Associations. SI-, SL- und II-Merging erhalten beide dokumentlokalen II. Namen behalten Typ und Scope; Variant-Scope ist die Vereinigung aus Name-Scope und explizitem Scope mit echter Obermengenbedingung.

Bei den Datentyp-Paaren bleiben die nativen lexikalischen Werte exakt erhalten, etwa `+00042` und `01.50`; die bestehende CXTM-Kanonisierung darf ihre definierten Datentypregeln anwenden. Unbekannte absolute Datentyp-IRIs und `ctm-integer` werden nicht in Topics oder neue Arithmetik umgedeutet. Name-, Variant- und Map-Reifier zeigen innerhalb jeder Map auf die kanonischen Objekte zurück.

### Import und Map-Item-Identität

Beide Parent-Dokumente erhalten denselben unveränderten XTM-Kindinhalt über den expliziten Resolver. Dessen exakte Argumente sind Ressourcen-IRI `https://equivalence.example.invalid/content-import/child.xtm`, `:purpose :mergemap`, Parent-Document-IRI und Notation `http://psi.topicmaps.org/iso13250/xtm`. Die Kindressource hat ihre eigene Document IRI. Beide Pfade verwenden den qualifizierten XML-Parser mit denselben ursprünglichen 343 Rohbytes sowie die vorhandene TMDM-Importoperation.

Das Kind enthält Typisierung, Name, Variant mit Scope und benutzerdefiniertem Datentyp sowie eine Map-II `urn:child-map` und Map-Reifier `#child-r`. Der Inhalt erzeugt gemeinsam mit dem lokalen Parent-Topic 9 Topics, 1 Name, 1 Variant, 1 Type–Instance-Association und 2 Roles. Quellmap, deren Handles und CXTM bleiben unverändert. Die Ziel-Map-Items haben weder Item Identifier noch Reifier. Das Topic `child-r` bleibt als gewöhnliches importiertes Topic erhalten; seine Quell-Map-Reification wird nicht übernommen. Map-Metadaten werden nicht zum Erreichen einer historischen Baseline übertragen. Der Originalvertrag aus Slice 22E bleibt unverändert offen.

## Absichtlich unterschiedliche Semantik

Die Quellen werden auch hier tatsächlich gelesen. Beide vollständigen Modellzustände und Ausgaben stehen im maschinenlesbaren Bericht. Bytepositionen sind **nullbasiert**. Die Unterschiede sind Erwartungen dieser Gegenproben, keine Reader-Fehler.

| Gegenprobe | CTM/XTM Bytes | Erste Abweichung | Verursachende Eigenschaft |
|---|---:|---:|---|
| `different-document-IRIs` | 115/115 | 57 | Unterschiedliche Document IRIs ergeben unterschiedliche dokumentlokale Topic-II; eine gemeinsame dritte CXTM-Basis erhält den Unterschied. |
| `SI-versus-SL` | 185/179 | 38 | Gleiche Locator-Schreibweise in SI beziehungsweise SL ergibt verschiedene native Identitätseigenschaften. |
| `non-topic-item-Identifier` | 321/391 | 152 | XTM Name trägt zusätzlich `urn:name-item`; dieser Nicht-Topic-II kann hier in CTM nicht ausgedrückt werden und bleibt erhalten. |

## Konkrete Fähigkeitslücken

Occurrences und explizite Associations sind vom Modell und von CTM unterstützt, aber im aktuellen XTM-Reader noch nicht implementiert. Diese drei Proben zählen **nicht** als erfolgreiche Reader-Äquivalenz und nicht als Original-PASS. Die CTM-Seite erzeugt tatsächliche kanonische Maps; die XTM-Seite liefert jeweils `XTM-UNSUPPORTED`, Code `:unsupported-construct`. Die Zurückweisung beweist keine semantische Gleichheit der noch nicht gelesenen XTM-Seite.

| Probe | Tatsächliche CTM-Struktur | XTM Position (Zeile:Spalte) | Grenze |
|---|---|---|---|
| `occurrence-scope-reifier` | 4 / 0 / 0 / 1 / 0 / 0 / 1 | 1:102 | XTM occurrence deserialization |
| `explicit-association` | 3 / 0 / 0 / 0 / 1 / 1 / 0 | 1:76 | XTM association deserialization |
| `association-role-scope-reifiers` | 6 / 0 / 0 / 0 / 1 / 1 / 2 | 1:90 | XTM association deserialization |

Die Association-Gegenproben decken erwartete Types, Player, Scope und Association-/Role-Reifier ab, können aber ohne XTM-Unterstützung noch keinen sprachübergreifenden Gleichheitsnachweis liefern. Kein Produktionsfehler oder Modellkonflikt wurde in diesen Proben nachgewiesen. Es gibt daher keine Reader-Erweiterung. `xsd:anyType`, Zyklussemantik, zusätzliche XTM-2.1-Fähigkeiten und offene CTM-Template-Fragen bleiben außerhalb dieses Slices.

Während der Testerstellung wurden zunächst `role:a`-Token als QName gelesen. Der fehlerhafte Testinput wurde zu `role: a` berichtigt, damit er die beabsichtigte XTM-Fähigkeitslücke erreicht. [development-input-fix.json](../reports/slice-22f/development-input-fix.json) hält den ursprünglichen Diagnosebefund fest. Dieser Entwicklungsfehler wurde nicht als erfolgreicher Vergleich gewertet.

## Vollständige Offline-Regression

Der tatsächlich abgenommene Lauf fand am 22.10.2026 von 11:48:49 bis 11:52:16 UTC statt. [execution.json](../reports/slice-22f/after/execution.json) und [runs.json](../reports/slice-22f/after/runs.json) dokumentieren alle 119 Prozesse, Befehle, Zeitpunkte, Exitcodes und Log-Hashes. Frisches SBCL 2.5.4 startet ohne Benutzer-/Systeminitialisierung. Alle Kindprozesse liefen mit Netzwerksperre und Schreibsperre für Topic Maps und HyperDoc; gepinnte lokale Abhängigkeiten wurden verwendet. Die reguläre Sandbox hatte zuvor den bekannten Startfehler am Symlink `~/.nix-profile`; die regulär freigegebenen Werkzeugaufrufe änderten weder diesen Symlink noch die Sandbox-Konfiguration.

- Neue direkte Äquivalenzsuite: 487 Checks, 27 Paare, 3 Unterschiedsproben, 3 Fähigkeitslücken.
- Bestehende TMDM/CTM/CXTM-Semantik: 12.100 Checks; separater XTM-Testlauf: 2.704 Checks.
- CTM/XTM-Mergemap: 217; registrierte Originale: 286; negative Originale: 25; Prolog: 171; empty2: 13; CTM-Integer: 112; Triple-Strings: 226; Encoding: 722.
- XML-Qualifikation: 146 PASS; Python: 2 Tests; NFC-Oracle: 16.294 Vergleiche.
- Alle 113 bisherigen Executor-Fehlerkontrollen lieferten den erwarteten ASDF-Fehlerexit 1; ihre Verhaltensberichte sind byteidentisch zu Slice 22E. Keine neue Originalregistrierung oder Fehlerkontrolle wurde erfunden.
- Alle 124 Originaldiagnosen, der gesamte separate XTM-Bericht und 48 bisherige weitere Ergebnisberichte sind byteidentisch zu Slice 22E. Die neue Suite wird im regulären ASDF-Testlauf tatsächlich ausgeführt.

| Registrierter Korpus | PASS | FAIL | NOT-RUN |
|---|---:|---:|---:|
| CTM | 262 | 4 | 7 |
| XTM | 72 | 0 | 52 |

Die bekannten CTM-FAILs bleiben `include-template.ctm`, `include-wildcard2.ctm`, `occurrence-datetime-timezone2.ctm` und `occurrence-datetime2.ctm`. Die neuen konstruierten Paare werden nicht in diese Korpuszahlen eingerechnet.

## Reproduktion und Integrität

Vollständige Reproduktion aus dem Repository mit lokal vorhandenen gepinnten Abhängigkeiten:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate-slice-22f.py --output /private/tmp/topic-maps-22f-reproduction
```

`--audit-only` prüft eine bereits gespeicherte Ausführung, ohne Tests erneut auszuführen. Der zusätzliche [Fresh-SBCL-Treiber](../reports/slice-22f/fresh-equivalence.lisp) erlaubt den gezielten ASDF-Testlauf; die Abnahme beruht auf der vollständigen Regression. Der vorhandene Collector und die bisherigen Fehlerkontrolltreiber bleiben unverändert.

Das [Integritätsaudit](../reports/slice-22f/after/integrity.json) bestätigt sämtliche 2.006 gepinnten Korpusdateien nach Größe und SHA-256, alle 5.826 historischen Berichtdateien und insgesamt 8.109 geschützte Ausgangsdateien. Originalquellen, Baselines, Corpus Lock, bestehende Reports und sämtliche Produktionsdateien bleiben unverändert. Die einzige Änderung einer bereits versionierten Datei ist die ASDF-Testintegration. Neue Dateien sind Tests, Untersuchungswerkzeug, Dokumentation und Evidenz. HyperDoc HEAD und Arbeitsbaumzustand entsprechen dem Ausgangsaudit. Keine Downloads, Änderungen langlebiger Images, Pushes oder Deployments.

Die [Whitespace-Prüfung](../reports/slice-22f/whitespace-check.json) meldet genau vier Stellen in den beiden tatsächlichen Unicode-CXTM-Dateien: Leerzeichen vor einem LF und Leerzeichen vor einem Tab im Name-Wert. Diese Bytes sind gewollte Literal-Evidenz und bleiben unverändert. Alle übrigen indexierten Dateien bestehen `git diff --cached --check`.

Das [Abschlussaudit](../reports/slice-22f/final-audit.json) enthält die SHA-256 aller neuen Artefakte einschließlich der 54 unveränderten tatsächlichen CXTM-Dateien unter `reports/slice-22f/after/actual/`. Sein Prüfskript startet keine Tests neu. Commit und sauberer Arbeitsbaum werden anschließend separat geprüft.

## Vollständige tatsächlich verwendete Quellpaare

Die folgenden Quellen stammen direkt aus dem erfolgreichen maschinenlesbaren Ergebnisbericht. CTM wird als String gelesen; XTM wird UTF-8-kodiert an `deserialize-octets` übergeben. Die JSON-Evidenz bewahrt Zeilenumbrüche/Whitespace exakt. XML-Dokumente sind jeweils vollständig; keine manuelle Ersatzmap ist beteiligt.

### `local-II`

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/local-II/map`.

Begründung: CTM local identifier and XTM id both assign the common Document IRI followed by #a. Fundstellen: CTM 3.3.6, XTM 4.5, TMDM 5.3.5.

CTM:

```text
a.
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'/></topicMap>
```

### `identity-SI`

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/identity-SI/map`.

Begründung: Both sources preserve the local II and add the same locator in the same identity category. Fundstellen: CTM 3.3.6,3.9, XTM 4.5-4.8, TMDM 5.3.5.

CTM:

```text
a <urn:subject>.
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><subjectIdentifier href='urn:subject'/></topic></topicMap>
```

### `merge-SI`

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/merge-SI/map`.

Begründung: The shared locator merges two Topics; both document-local IIs must survive. Creation order differs. Fundstellen: CTM 3.3.6,3.9, XTM 4.5-4.8, TMDM 5.3.5,6.2.

CTM:

```text
a <urn:subject>. b <urn:subject>.
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='b'><subjectIdentifier href='urn:subject'/></topic><topic id='a'><subjectIdentifier href='urn:subject'/></topic></topicMap>
```

### `identity-SL`

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/identity-SL/map`.

Begründung: Both sources preserve the local II and add the same locator in the same identity category. Fundstellen: CTM 3.3.6,3.9, XTM 4.5-4.8, TMDM 5.3.5.

CTM:

```text
a =<urn:subject>.
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><subjectLocator href='urn:subject'/></topic></topicMap>
```

### `merge-SL`

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/merge-SL/map`.

Begründung: The shared locator merges two Topics; both document-local IIs must survive. Creation order differs. Fundstellen: CTM 3.3.6,3.9, XTM 4.5-4.8, TMDM 5.3.5,6.2.

CTM:

```text
a =<urn:subject>. b =<urn:subject>.
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='b'><subjectLocator href='urn:subject'/></topic><topic id='a'><subjectLocator href='urn:subject'/></topic></topicMap>
```

### `identity-II`

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/identity-II/map`.

Begründung: Both sources preserve the local II and add the same locator in the same identity category. Fundstellen: CTM 3.3.6,3.9, XTM 4.5-4.8, TMDM 5.3.5.

CTM:

```text
a ^<urn:item>.
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><itemIdentity href='urn:item'/></topic></topicMap>
```

### `merge-II`

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/merge-II/map`.

Begründung: The shared locator merges two Topics; both document-local IIs must survive. Creation order differs. Fundstellen: CTM 3.3.6,3.9, XTM 4.5-4.8, TMDM 5.3.5,6.2.

CTM:

```text
a ^<urn:item>. b ^<urn:item>.
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='b'><itemIdentity href='urn:item'/></topic><topic id='a'><itemIdentity href='urn:item'/></topic></topicMap>
```

### `isa-instanceOf`

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/isa-instanceOf/map`.

Begründung: Both create the same type-instance Association with instance/type Roles and identical Core Subject SIs. Fundstellen: CTM 3.9, XTM 4.9, TMDM 7.2.

CTM:

```text
a isa t.
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><instanceOf><topicRef href='#t'/></instanceOf></topic></topicMap>
```

### `isa-multiple-normalized`

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/isa-multiple-normalized/map`.

Begründung: Two distinct type-instance Associations remain; repeating one relation is normalized. Fundstellen: CTM 3.9, XTM 4.9, TMDM 6.6,7.2.

CTM:

```text
a isa t; isa u; isa t.
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='u'/><topic id='a'><instanceOf><topicRef href='#t'/><topicRef href='#u'/><topicRef href='#t'/></instanceOf></topic></topicMap>
```

### `default-name`

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/default-name/map`.

Begründung: Both create one Name of the same implicit topic-name Core Subject type. Fundstellen: CTM 3.11, XTM 4.10-4.11, TMDM 5.4,7.5.

CTM:

```text
a - "Name".
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><name><value>Name</value></name></topic></topicMap>
```

### `typed-scoped-name`

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/typed-scoped-name/map`.

Begründung: Name Type and Scope are identical native references; Scope is a set. Fundstellen: CTM 3.3.9,3.11, XTM 4.10,4.13-4.14, TMDM 5.4.

CTM:

```text
a - t:"Name"@s2,s1,s1.
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><name><type><topicRef href='#t'/></type><scope><topicRef href='#s1'/><topicRef href='#s2'/></scope><value>Name</value></name></topic></topicMap>
```

### `unicode-whitespace-escaping`

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/unicode-whitespace-escaping/map`.

Begründung: CTM escapes and XML references encode the same Unicode characters and whitespace. Fundstellen: CTM 3.4.2,3.11, XTM 4.11, TMDM 5.4.

CTM:

```text
a - " 馬🦊 & < > \n \t \" \\ ".
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><name><value> 馬🦊 &amp; &lt; &gt; &#xA; &#x9; &quot; \ </value></name></topic></topicMap>
```

### `empty-name`

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/empty-name/map`.

Begründung: Both Name values are the empty string. Fundstellen: CTM 3.11, XTM 4.11, TMDM 5.4.

CTM:

```text
a - "".
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><name><value/></name></topic></topicMap>
```

### `duplicate-names`

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/duplicate-names/map`.

Begründung: Equal Names normalize to one native Name in both maps. Fundstellen: CTM 3.11, XTM 4.10, TMDM 5.4,6.3.

CTM:

```text
a - "N"; - "N".
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><name><value>N</value></name><name><value>N</value></name></topic></topicMap>
```

### `variant-inherited-scope`

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/variant-inherited-scope/map`.

Begründung: Variant Scope is Name Scope union explicit Scope, a proper superset. Fundstellen: CTM 3.12, XTM 4.12, TMDM 5.5.

CTM:

```text
a - "N"@base ("V"@extra).
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><name><scope><topicRef href='#base'/></scope><value>N</value><variant><scope><topicRef href='#extra'/></scope><resourceData>V</resourceData></variant></name></topic></topicMap>
```

### `variant-datatype-integer`

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/variant-datatype-integer/map`.

Begründung: Both quoted resource forms retain the same lexical value and exact datatype IRI; datatype is not a Topic. Fundstellen: CTM 3.4.1,3.12, XTM 4.12,4.16, TMDM 4.4,5.5.

CTM:

```text
a - "N" ("+00042"^^<http://www.w3.org/2001/XMLSchema#integer>@s).
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><name><value>N</value><variant><scope><topicRef href='#s'/></scope><resourceData datatype='http://www.w3.org/2001/XMLSchema#integer'>+00042</resourceData></variant></name></topic></topicMap>
```

### `variant-datatype-decimal`

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/variant-datatype-decimal/map`.

Begründung: Both quoted resource forms retain the same lexical value and exact datatype IRI; datatype is not a Topic. Fundstellen: CTM 3.4.1,3.12, XTM 4.12,4.16, TMDM 4.4,5.5.

CTM:

```text
a - "N" ("01.50"^^<http://www.w3.org/2001/XMLSchema#decimal>@s).
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><name><value>N</value><variant><scope><topicRef href='#s'/></scope><resourceData datatype='http://www.w3.org/2001/XMLSchema#decimal'>01.50</resourceData></variant></name></topic></topicMap>
```

### `variant-datatype-date`

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/variant-datatype-date/map`.

Begründung: Both quoted resource forms retain the same lexical value and exact datatype IRI; datatype is not a Topic. Fundstellen: CTM 3.4.1,3.12, XTM 4.12,4.16, TMDM 4.4,5.5.

CTM:

```text
a - "N" ("2000-02-29"^^<http://www.w3.org/2001/XMLSchema#date>@s).
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><name><value>N</value><variant><scope><topicRef href='#s'/></scope><resourceData datatype='http://www.w3.org/2001/XMLSchema#date'>2000-02-29</resourceData></variant></name></topic></topicMap>
```

### `variant-datatype-datetime`

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/variant-datatype-datetime/map`.

Begründung: Both quoted resource forms retain the same lexical value and exact datatype IRI; datatype is not a Topic. Fundstellen: CTM 3.4.1,3.12, XTM 4.12,4.16, TMDM 4.4,5.5.

CTM:

```text
a - "N" ("2000-02-29T01:02:03Z"^^<http://www.w3.org/2001/XMLSchema#dateTime>@s).
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><name><value>N</value><variant><scope><topicRef href='#s'/></scope><resourceData datatype='http://www.w3.org/2001/XMLSchema#dateTime'>2000-02-29T01:02:03Z</resourceData></variant></name></topic></topicMap>
```

### `variant-datatype-unknown-http`

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/variant-datatype-unknown-http/map`.

Begründung: Both quoted resource forms retain the same lexical value and exact datatype IRI; datatype is not a Topic. Fundstellen: CTM 3.4.1,3.12, XTM 4.12,4.16, TMDM 4.4,5.5.

CTM:

```text
a - "N" ("literal%GG"^^<https://types.example.invalid/custom>@s).
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><name><value>N</value><variant><scope><topicRef href='#s'/></scope><resourceData datatype='https://types.example.invalid/custom'>literal%GG</resourceData></variant></name></topic></topicMap>
```

### `variant-datatype-unknown-urn`

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/variant-datatype-unknown-urn/map`.

Begründung: Both quoted resource forms retain the same lexical value and exact datatype IRI; datatype is not a Topic. Fundstellen: CTM 3.4.1,3.12, XTM 4.12,4.16, TMDM 4.4,5.5.

CTM:

```text
a - "N" (" urn:literal "^^<urn:custom>@s).
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><name><value>N</value><variant><scope><topicRef href='#s'/></scope><resourceData datatype='urn:custom'> urn:literal </resourceData></variant></name></topic></topicMap>
```

### `variant-resourceRef`

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/variant-resourceRef/map`.

Begründung: IRI-valued literals resolve against the same explicit Document IRI without Topic creation. Fundstellen: CTM 3.4.1, XTM 4.16-4.17, TMDM 4.4,5.5.

CTM:

```text
a - "N" (<../sound>@s).
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><name><value>N</value><variant><scope><topicRef href='#s'/></scope><resourceRef href='../sound'/></variant></name></topic></topicMap>
```

### `variant-anyURI-data`

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/variant-anyURI-data/map`.

Begründung: IRI-valued literals resolve against the same explicit Document IRI without Topic creation. Fundstellen: CTM 3.4.1, XTM 4.16-4.17, TMDM 4.4,5.5.

CTM:

```text
a - "N" (<../sound>@s).
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><name><value>N</value><variant><scope><topicRef href='#s'/></scope><resourceData datatype='http://www.w3.org/2001/XMLSchema#anyURI'>../sound</resourceData></variant></name></topic></topicMap>
```

### `variant-ctm-integer-star`

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/variant-ctm-integer-star/map`.

Begründung: The literal * is an opaque lexical value with ctm-integer datatype in both maps. Fundstellen: CTM 3.4.1,Annex A, XTM 4.16, TMDM 4.4.

CTM:

```text
a - "N" (*@s).
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><name><value>N</value><variant><scope><topicRef href='#s'/></scope><resourceData datatype='http://psi.topicmaps.org/iso13250/ctm-integer'>*</resourceData></variant></name></topic></topicMap>
```

### `name-variant-reification`

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/name-variant-reification/map`.

Begründung: The same local-II Topics reify the Name and Variant, with inverse references within each map. Fundstellen: CTM 3.3.10,3.11-3.12, XTM 4.3.2,4.10,4.12, TMDM 5.3.4.

CTM:

```text
a - "N"~nr ("V"@s ~vr).
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><name reifier='#nr'><value>N</value><variant reifier='#vr'><scope><topicRef href='#s'/></scope><resourceData>V</resourceData></variant></name></topic></topicMap>
```

### `map-reification`

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/map-reification/map`.

Begründung: The same local-II Topic reifies the fresh Map item; neither Map has explicit item identifiers. Fundstellen: CTM 3.5, XTM 4.3.2,4.4, TMDM 5.2,5.3.4.

CTM:

```text
~r a.
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0' reifier='#r'><topic id='a'/></topicMap>
```

### `content-import`

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/content-import/map`.

Begründung: Both readers import the same supported XTM child using its resource IRI; child Map metadata is excluded. Fundstellen: CTM 3.16.3, XTM 4.21, TMDM 5.2,6.2.

CTM:

```text
%mergemap <child.xtm> <http://psi.topicmaps.org/iso13250/xtm>
local.
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><mergeMap href='child.xtm'/><topic id='local'/></topicMap>
```

Explizite Kindressource `https://equivalence.example.invalid/content-import/child.xtm`:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0' reifier='#child-r'><itemIdentity href='urn:child-map'/><topic id='owner'><instanceOf><topicRef href='#t'/></instanceOf><name><value>Imported</value><variant><scope><topicRef href='#s'/></scope><resourceData datatype='urn:custom'>V</resourceData></variant></name></topic></topicMap>
```

## Tatsächliche Quellen der Unterschieds- und Fähigkeitsproben

### `different-document-IRIs`

CTM:

```text
a.
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'/></topicMap>
```

### `SI-versus-SL`

CTM:

```text
a <urn:identity>.
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><subjectLocator href='urn:identity'/></topic></topicMap>
```

### `non-topic-item-Identifier`

CTM:

```text
a - "N".
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><name><itemIdentity href='urn:name-item'/><value>N</value></name></topic></topicMap>
```

### `occurrence-scope-reifier`

CTM:

```text
a t:"42"^^<http://www.w3.org/2001/XMLSchema#integer>@s ~r.
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><occurrence reifier='#r'><type><topicRef href='#t'/></type><scope><topicRef href='#s'/></scope><resourceData datatype='http://www.w3.org/2001/XMLSchema#integer'>42</resourceData></occurrence></topic></topicMap>
```

Tatsächliche XTM-Condition:

```json
{
  "class": "XTM-UNSUPPORTED",
  "code": "unsupported-construct",
  "line": 1,
  "column": 102,
  "sourceKey": "gap:XTM:occurrence-scope-reifier",
  "documentIRI": "https://equivalence.example.invalid/gap-occurrence-scope-reifier/map",
  "position": null,
  "message": "XTM UNSUPPORTED-CONSTRUCT at gap:XTM:occurrence-scope-reifier (https://equivalence.example.invalid/gap-occurrence-scope-reifier/map), approximately 1:102: XTM occurrence is not implemented in this subset."
}
```

### `explicit-association`

CTM:

```text
rel(role: a)
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><association><type><topicRef href='#rel'/></type><role><type><topicRef href='#role'/></type><topicRef href='#a'/></role></association></topicMap>
```

Tatsächliche XTM-Condition:

```json
{
  "class": "XTM-UNSUPPORTED",
  "code": "unsupported-construct",
  "line": 1,
  "column": 76,
  "sourceKey": "gap:XTM:explicit-association",
  "documentIRI": "https://equivalence.example.invalid/gap-explicit-association/map",
  "position": null,
  "message": "XTM UNSUPPORTED-CONSTRUCT at gap:XTM:explicit-association (https://equivalence.example.invalid/gap-explicit-association/map), approximately 1:76: XTM association is not implemented in this subset."
}
```

### `association-role-scope-reifiers`

CTM:

```text
rel(role: a ~rr)@s ~ar
```

XTM:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><association reifier='#ar'><type><topicRef href='#rel'/></type><scope><topicRef href='#s'/></scope><role reifier='#rr'><type><topicRef href='#role'/></type><topicRef href='#a'/></role></association></topicMap>
```

Tatsächliche XTM-Condition:

```json
{
  "class": "XTM-UNSUPPORTED",
  "code": "unsupported-construct",
  "line": 1,
  "column": 90,
  "sourceKey": "gap:XTM:association-role-scope-reifiers",
  "documentIRI": "https://equivalence.example.invalid/gap-association-role-scope-reifiers/map",
  "position": null,
  "message": "XTM UNSUPPORTED-CONSTRUCT at gap:XTM:association-role-scope-reifiers (https://equivalence.example.invalid/gap-association-role-scope-reifiers/map), approximately 1:90: XTM association is not implemented in this subset."
}
```
