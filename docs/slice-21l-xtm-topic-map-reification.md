# Slice 21L — XTM 2.0 Topic Map Reification

## Ausgangszustand und normative Herleitung

Branch: `codex/xtm-slice-21l`. Ausgangscommit und Parent:
`da36095dddc1354ee8558dc9d729f5cb2fe53ff5`.
Der vorgefundene Branch war `codex/xtm-slice-21k`; Index und Arbeitsbaum waren sauber.
[initial-state.json](../reports/slice-21l/initial-state.json) enthält alle ursprünglichen Dateihashes.
Vor jeder Reader-Änderung reproduzierte ein frischer SBCL 2.5.4 ohne Benutzerinitialisierung
alle 1860 bisherigen XTM-Prüfungen und alle 124 Diagnosen identisch zu Slice 21K.
Siehe [baseline.log](../reports/slice-21l/baseline.log),
[baseline-xtm.json](../reports/slice-21l/baseline-xtm.json),
[before-diagnostics.json](../reports/slice-21l/before-diagnostics.json) und
[initial-source-preparation.json](../reports/slice-21l/initial-source-preparation.json).
Gespeicherter Ausgangsstand: XTM **62 PASS / 0 FAIL / 62 NOT-RUN**;
CTM **262 PASS / 4 FAIL / 7 NOT-RUN**, im vollständigen Lauf erneut bestätigt.

Normativ hergeleitet aus [XTM 2.0 §§4.3.1–4.3.4 und 4.4](https://www.isotopicmaps.org/sam/sam-xtm/):
`reifier` ist ein optionales Attribut des `topicMap`-Elements, vor dessen
`itemIdentity*`-Kindern. Der aufgelöste absolute Locator wird in der
Item-Identifier-Menge der vorhandenen Topics gesucht. Ein Treffer wird
zugewiesen; andernfalls wird ein Topic mit diesem II erzeugt. SI sind kein
Trefferkriterium dieser Auflösung. Prozentdekodierung, UTF-8 und relative
IRI-Auflösung folgen §4.3.4. Das Attribut erzeugt keinen Map-II.
[TMDM §§5.2, 5.3.4–5.3.5 und 6.2](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/)
geben die Topic-Map-Reifier-Eigenschaft, die berechnete Topic-Rückreferenz und
die Umschreibung auf kanonische Reifier nach Topic-Merging vor. Ein Topic
kann keine verschiedenen Information Items reifizieren. Die folgenden
Aussagen sind beobachtete Ausführungsbefunde, getrennt von dieser Herleitung.

## Native API und begrenzte Reader-Änderung

[api-preflight.lisp](../reports/slice-21l/api-preflight.lisp) prüfte bereits vor
Änderung des Readers `set-item-reifier`, `item-reifier`, `topic-reified`,
`intern-topic`, Identifier-Zuweisung und kanonisches Merging.
Zuweisung und inverse Referenz funktionieren ohne Modelländerung.
Wiederverwendung des Reifiers wird als `REIFICATION-ERROR/:reifier-conflict`
abgewiesen; die Kollision eines neu zu erzeugenden Topic-II mit einem Name-II
als `OCCURRENCE-IDENTIFIER-ERROR/:duplicate-item-identifier`.
Beide Operationen erhalten die gespeicherten Identitäten und Handles atomar.
Siehe [Vorablog](../reports/slice-21l/api-preflight-before-reader.log) und
[wiederholte Abnahme](../reports/slice-21l/map-reifier-api-preflight.log).

Ausschließlich `src/xtm/reader.lisp` enthält Produktionsänderungen:

1. `validate-source` validiert das Map-Attribut mit dem vorhandenen IRI-Resolver.
   Die bisherigen Attribut-, Versions-, Namespace- und Kindreihenfolgeprüfungen bleiben erhalten.
2. `read-map-reifier` sucht direkt über die II-Mengen der aktuellen nativen Topics.
   Der Suchpfad verwendet **nicht** `find-reference-topic`, dessen SI-/II-Trefferregel
   unverändert bleibt. Auf einem Miss erzeugt `intern-topic` die erforderliche
   II-Identität; `set-item-reifier` setzt die native Beziehung.
3. `deserialize-octets` führt diese Operation nach Quellvalidierung und vor den
   Map-Item-Identities sowie späteren Topic-Elementen aus. Vorhandene Map-II bleiben getrennt.

Keine neue Registry, keine neue Objektart und keine Transaktion für den gesamten Reader.
Die Erzeugung eines Topics mit II kann durch die bestehende TMDM-SI-/II-Regel
mit einem SI-Topic zusammenfallen. Das ist von einem anfänglichen SI-Treffer
zu unterscheiden: Die neue II-Zuweisung ist trotzdem erforderlich und geprüft.
Ein ausschließlich gleichlautender SL bewirkt keine solche Zusammenführung.
Die bestehende `intern-topic`-Implementierung realisiert diesen TMDM-Schritt;
es wird keine sichtbare Zwischenrepräsentation erfunden.

## Unveränderter Originalvertrag

`vendor/cxtm/xtm2/in/tm-reifier.xtm` enthält **94 Originalbytes**:

```xml
<topicMap xmlns="http://www.topicmaps.org/xtm/" version="2.0" reifier="#reifier">
</topicMap>
```

Es gibt kein Topic-Element und keine andere neue Sprachfähigkeit.
Die Document IRI ist:

```text
https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/tm-reifier.xtm
```

Das Attribut erzeugt genau ein Topic mit diesem absoluten II:

```text
https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/tm-reifier.xtm#reifier
```

Der Source Key ist `xtm2/in/tm-reifier.xtm` und hat keine Identitätswirkung.
Das tatsächliche Modell enthält eine Map, ein Topic und keine Associations,
Names, Variants, Occurrences oder Rollen. Die Map hat keine Item Identifier;
das Topic hat ausschließlich den genannten II, keine SI und keine SL.
`item-reifier(map)`, das einzige Live-Topic, `by-id("reifier")` und
`canonical-topic(reifier)` sind **EQ**. `topic-parent(reifier)` und
`topic-reified(reifier)` sind **EQ** zur Map.

Die öffentliche API `topic-maps.xtm:deserialize-octets` erhält die unveränderten
Originalbytes. Eine instrumentierte Gegenprobe belegt genau einen Aufruf des
qualifizierten XML-Parsers mit demselben Bytevektor per EQ.
Kanonisierung ist wiederholbar und verändert weder Rohquelle, Modell noch
kanonische Handles oder inverse Reification. Ein anderer Source Key bei
gleicher Document IRI liefert dasselbe Modell und dieselben CXTM-Bytes.

Vollständige tatsächliche Ausgabe und unveränderte Baseline:

```xml
<topicMap reifier="1">
<topic number="1">
<itemIdentifiers>
<locator>#reifier</locator>
</itemIdentifiers>
</topic>
</topicMap>
```

**128/128 Bytes identisch**, einschließlich abschließendem LF;
`firstDifferentByte = null`, tatsächliche Condition `null`.

| Artefakt | SHA-256 |
| --- | --- |
| Originalquelle | `092abcbbaef0cdbd0e3629708b25c5a5b07a8bf47d94cccb56f116fdd7585c9e` |
| Originalbaseline | `53c9dc74e32578ef85c0c88ddf0eb52e265102d5fcc4a63b0f99b7e6d7c24e08` |
| Tatsächliche CXTM-Ausgabe | `53c9dc74e32578ef85c0c88ddf0eb52e265102d5fcc4a63b0f99b7e6d7c24e08` |

[map-reifier-originals.json](../reports/slice-21l/map-reifier-originals.json)
enthält Quellhex, Quelltext, IRI, tatsächliches Modell, Condition und alle CXTM-Bytes;
[actual/tm-reifier.xtm.cxtm](../reports/slice-21l/actual/tm-reifier.xtm.cxtm) erhält die Ausgabe.
Der vorhandene Case-Record-Executor registriert genau einen neuen positiven
Vertrag nach Deserialisierung, Modellprüfung und vollständigem Originalvergleich.
Der reguläre ASDF-Testlauf führt ihn tatsächlich aus: insgesamt 63 eindeutige
Case Records, 55 positive und acht ursachenqualifizierte negative Originale.
Die bisherigen 62 Ergebnisse und ihre Reihenfolge sind identisch zu Slice 21K.

## Modell-, Konflikt- und Syntaxgegenproben

[tests/xtm-map-reification.lisp](../tests/xtm-map-reification.lisp) ist ein
weiterer Bestandteil des vorhandenen ASDF-Testsystems. Es gibt keine zweite
Testarchitektur. Der Lauf enthält **1972 eindeutige XTM-Prüfungen**:
1860 erhaltene und **112 neue**.
Alle bisherigen Checknamen und deren relative Reihenfolge bleiben erhalten.
[xtm.json](../reports/slice-21l/xtm.json) protokolliert 38 zusätzliche
Kontrollzeilen mit tatsächlichen Modellen oder Conditions; weitere präzise
EQ-, Lookup- und Classifier-Prüfungen stehen in dessen `checks` und im [XTM-Log](../reports/slice-21l/xtm.log).

Geprüft sind absolute, relative, Fragment-, Nicht-Shorthand-Fragment- und leere
Referenzen, Unicode, XML-Escaping und Prozent-/UTF-8-Dekodierung. Map-II und
Reifier-II bleiben getrennt, doppelte Map-II normalisieren. Die spätere
Definition des Reifier-Topics erhält dessen Name und Variant einschließlich
Whitespace, Parent, Datentyp und Scope. SI-, SL- und II-Merge-Routen werden
zusätzlich mit den tatsächlichen Reader-Operationen schrittweise beobachtet:
Die Attributoperation erzeugt den Reifier vor den Topic-Definitionen.
Alle festgehaltenen alten Reifier-Handles liefern nach Merging denselben
kanonischen Topic wie Map-Reifier und beide definierten Topic-IDs. Vollständige
Identifier-Mengen bleiben erhalten. Wiederholte CXTM-Kanonisierung verändert
auch die festgehaltenen Forward-Handles und deren Rückreferenz nicht.
Die gleiche Quelle über die öffentliche API erzeugt das gleiche Modell.

Eine native Map mit bereits vorhandenem passenden Topic-II prüft den
Produktions-Lookup ohne erneuten `intern-topic`-Aufruf. Separate SI-/SL-Maps
prüfen ausdrücklich den fehlenden II-Treffer und die anschließenden
Modellregeln. Diese isolierten Prüfungen erweitern die öffentliche API nicht
um die Deserialisierung in eine bestehende Map und zählen nicht als Originale.

Die native Wiederverwendung eines Reifier-Topics für einen Name sowie das
Merging zweier Topics, die verschiedene Items reifizieren, scheitern als
`REIFICATION-ERROR/:reifier-conflict`. Die Kollision mit einem vorhandenen
Name-II scheitert als `OCCURRENCE-IDENTIFIER-ERROR/:duplicate-item-identifier`.
Jeweils bleiben vollständiger Modellzustand, Identitäten, Reifier, Inversen und
Handles erhalten. Diese Atomarität betrifft die bestehenden nativen Operationen.
Ein Map-II, der dem bereits erzeugten Reifier-II entspricht, wird als
`ITEM-IDENTIFIER-ERROR/:duplicate-item-identifier` zurückgewiesen.

Alle tatsächlichen Fehlerbeobachtungen:

| Gegenprobe | Condition | Code | Zeile:Spalte |
| --- | --- | --- | --- |
| `bad-percent` | `XTM-REJECTION` | `invalid-percent-escape` | 1:81 |
| `truncated-percent` | `XTM-REJECTION` | `invalid-percent-escape` | 1:80 |
| `bad-percent-utf8` | `XTM-REJECTION` | `invalid-percent-utf8` | 1:84 |
| `surrogate-percent-utf8` | `XTM-REJECTION` | `invalid-percent-utf8` | 1:87 |
| `space` | `XTM-REJECTION` | `invalid-iri` | 1:81 |
| `decoded-control` | `XTM-REJECTION` | `invalid-iri` | 1:81 |
| `relative-colon` | `XTM-REJECTION` | `invalid-iri` | 1:86 |
| `two-fragments` | `XTM-REJECTION` | `invalid-iri` | 1:78 |
| `extra-attribute` | `XTM-REJECTION` | `unexpected-attribute` | 1:87 |
| `qualified-reifier` | `XTM-REJECTION` | `unexpected-attribute` | 1:95 |
| `missing-version` | `XTM-REJECTION` | `missing-attribute` | 1:63 |
| `invalid-version` | `XTM-REJECTION` | `invalid-version` | 1:77 |
| `wrong-namespace` | `XTM-REJECTION` | `invalid-namespace` | 1:57 |
| `identity-after-topic` | `XTM-REJECTION` | `element-order` | 1:121 |
| `reifier-child` | `XTM-REJECTION` | `unexpected-element` | 1:83 |
| `name-reification` | `XTM-UNSUPPORTED` | `reification` | 1:113 |
| `variant-reification` | `XTM-UNSUPPORTED` | `reification` | 1:138 |
| `occurrence-reification` | `XTM-UNSUPPORTED` | `unsupported-construct` | 1:119 |
| `association-role-reification` | `XTM-UNSUPPORTED` | `unsupported-construct` | 1:106 |
| `mergeMap` | `XTM-UNSUPPORTED` | `unsupported-construct` | 1:108 |
| `map-ii-reifier-ii-collision` | `ITEM-IDENTIFIER-ERROR` | `duplicate-item-identifier` | keine native Quellposition |
| `reuse-reifier` | `REIFICATION-ERROR` | `reifier-conflict` | keine native Quellposition |
| `existing-name-ii-collision` | `OCCURRENCE-IDENTIFIER-ERROR` | `duplicate-item-identifier` | keine native Quellposition |
| `merge-two-different-reified-items` | `REIFICATION-ERROR` | `reifier-conflict` | keine native Quellposition |

Die Positionen sind ungefähre SAX-Zeile/Spalte, keine Byteoffsets. Native
TMDM-Conditions werden unverändert ohne erfundene Position oder Cause erhalten.
Die drei atomaren Konfliktkontrollen enthalten den vollständigen beobachteten
Condition-Text. Name-/Variant-Reification bleibt `:reification`/Unsupported;
Occurrence und explizite Association/Role-Verarbeitung bleiben am jeweiligen
nicht unterstützten Konstrukt stehen. Ein `reifier`-Kindelement wird spezifisch
als XTM-Syntaxfehler abgewiesen. Die beiden bisherigen allgemeinen
Unsupported-Fixtures (direkt und im CTM/XTM-Mergemap-Test) verwenden jetzt
Name-Reification statt der nun gültigen Map-Reification. Labels, Conditions
und Codes bleiben erhalten; es sind keine neuen Originalverträge.

## Alle 124 Diagnosen und verbleibende negative Originale

[diagnostic-changes.json](../reports/slice-21l/diagnostic-changes.json) und
[diagnostics.json](../reports/slice-21l/diagnostics.json) belegen genau zwei Änderungen:

- `xtm2/in/tm-reifier.xtm`: bisher `XTM-UNSUPPORTED/:reification` bei 1:82;
  jetzt erfolgreiche Deserialisierung, Condition null, vollständiger Originalvergleich PASS.
- `xtm2/invalid/reifier-collision.xtm`: bisher `XTM-UNSUPPORTED/:reification`
  am Root-Attribut; jetzt `XTM-UNSUPPORTED/:unsupported-construct`,
  `XTM occurrence is not implemented in this subset.`, bei 3:36.
  Bereits die vorangestellte Quellvalidierung erreicht hier den noch
  ausgeschlossenen Occurrence-Knoten; die beabsichtigte native Reifier-Kollision
  wird nicht erreicht. Es gibt keinen negativen PASS.

Die übrigen **122 Beobachtungen sind vollständig identisch**, einschließlich
ihrer Conditions, Codes, Positionen, Messages und gegebenenfalls CXTM-Bytes.
Alle drei folgenden Dateien bleiben unregistriert und **NOT-RUN**:

| Negatives Original | Tatsächlicher diagnostischer Zustand nach Slice 21L |
| --- | --- |
| `reifier-collision.xtm` | `XTM-UNSUPPORTED/:unsupported-construct`, 3:36; XTM occurrence is not implemented in this subset. |
| `role-duplicate-reified.xtm` | `XTM-UNSUPPORTED/:unsupported-construct`, 5:16; XTM association is not implemented in this subset. |
| `topicref-no-fragment-id.xtm` | `XTM-UNSUPPORTED/:unsupported-construct`, 2:16; XTM association is not implemented in this subset. |

## Vollständige Offline-Abnahme und Integrität

[execution.json](../reports/slice-21l/execution.json) enthält alle **72**
frischen Prozessaufrufe einschließlich Kommando, UTC-Zeiten, tatsächlichem und
erwartetem Exitcode. Jeder Ausführungsprozess verwendet `sandbox-exec` mit
Netzwerksperre und Schreibsperre für dieses Repository. SBCL ist exakt 2.5.4,
mit `--no-sysinit --no-userinit`; die Lisp-Tests laufen in frischen Prozessen.
Vorhandene gepinnte lokale Abhängigkeiten und bestehende XML-Patches werden
geprüft und temporär vorbereitet. Kein Download, kein Nix-Rebuild und kein
langlebiges Lisp-Image. Das Skript [validate-slice-21l.py](../scripts/validate-slice-21l.py)
ist der vorhandenen Validierungskette nachgeführt.

| Abnahmebereich | Tatsächliches Ergebnis |
| --- | ---: |
| Erhaltene TMDM-/CTM-/CXTM-Prüfungen | 12100 PASS |
| XML-Qualifikation | 146 PASS |
| XTM | 1972 PASS |
| CTM/XTM-Mergemap | 217 PASS |
| Slice 20A / 20B / 20C | 286 / 25 / 171 PASS |
| Slice 20E / 20F / 20G / 20H | 13 / 112 / 226 / 722 PASS |
| Python-Unittests | 2 PASS |
| NFC-Oracle | 16294 Vergleiche PASS |
| Executor-Fehlerkontrollen | 66 erwartete ASDF-Fehlschläge nachgewiesen |

Die Fehlerkontrollen bewahren alle 60 bisherigen Kontrollpfade und ergänzen
fünf Faults im neuen Originalvertrag: vollständige CXTM-Byteabweichung,
XML-Fehler, XTM-Fehler, Unsupported und eine **tatsächlich über die TMDM-API
ausgelöste Reification-Kollision**. Alle bewahren die 62 vorherigen Original-PASS
und klassifizieren den beschädigten neuen Vertrag niemals als PASS.
Eine weitere Kontrolle ersetzt die erwartete native `:reifier-conflict`-Ursache
durch einen tatsächlich ausgelösten `:foreign-reifier`. Der ASDF-Lauf scheitert
an der spezifischen Condition-Prüfung; die bereits korrekt bestandenen 63
Originale bleiben getrennt davon erhalten. Classifier-Gegenproben weisen auch
eine falsche Condition bei einem negativen Vertrag als Ausführungsfehler zurück.
Siehe [failure-controls.json](../reports/slice-21l/failure-controls.json),
[failure-controls.lisp](../reports/slice-21l/failure-controls.lisp) und die Einzel-JSON/Logs.

Die vollständige Regression ist in [regression.log](../reports/slice-21l/regression.log)
und den [erhaltenen Teilberichten](../reports/slice-21l/retained/) dokumentiert.
Alle 48 bisherigen Nicht-XTM-Berichte sind strukturell identisch zu Slice 21K.
Die vier bekannten CTM-Abweichungen bleiben unverändert:
`include-template.ctm`, `include-wildcard2.ctm`,
`occurrence-datetime-timezone2.ctm`, `occurrence-datetime2.ctm`.

Erst nach tatsächlicher Ausführung ermittelter registrierter Stand:
**XTM 63 PASS / 0 FAIL / 61 NOT-RUN**;
**CTM 262 PASS / 4 FAIL / 7 NOT-RUN**.
Diagnostische Beobachtungen sind keine zusätzlichen Registrierungen.

[integrity.json](../reports/slice-21l/integrity.json) prüft
**2006 gepinnte Korpusdateien** nach Größe und SHA-256,
**2687 historische Berichte** und
**4943 geschützte Dateien des Ausgangscommits**,
einschließlich TMDM, CTM, CXTM und XML. Originalquellen, Baselines,
Korpus-Lock und historische Reports bleiben unverändert. Die während der
Abnahme ausgeführten Reader-, Test- und Treiberquellen werden zusätzlich
vor und nach allen Prozessen auf identische SHA-256 geprüft.
[precommit-audit.json](../reports/slice-21l/precommit-audit.json) dokumentiert
die abschließende Pfad-/Hashprüfung;
[artifacts.json](../reports/slice-21l/artifacts.json) sichert die neuen Artefakte
mit SHA-256 (Manifest selbst ausgenommen).

[development-attempts.json](../reports/slice-21l/development-attempts.json)
erhält zwei nicht abgenommene Entwicklungsstarts: macOS verweigerte eine
verschachtelte `sandbox_apply`; danach stoppte ein Syntaxfehler im neu
ergänzten Faultdriver vor dessen erster Kontrollausführung. Die Ursachen und
vollständigen Fehlerlogs sind bewahrt. Der Orchestrator erhielt reguläre
Tool-Freigabe; alle Ausführungsprozesse behalten dieselben Netz-/Schreibsperren.
Die Symlink-Konfiguration und Freigabeprüfung wurden nicht verändert. Der
abschließende vollständige Lauf ist davon getrennt und erfolgreich.

Keine Erweiterung auf andere Reification-Konstrukte, Occurrences, explizite
Associations/Roles, XTM-`mergeMap`, zusätzliche Datentypen, XML-Kanonisierung
oder XTM 2.1. Keine HyperDoc-Änderung, kein Push und kein Deployment.
Slice 21L endet mit dem gemeinsamen lokalen Commit.
