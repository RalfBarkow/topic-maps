# Slice 21M — XTM 2.0 Topic Name Reification

## Ausgangszustand, Norm und Vorprüfung

Branch: `codex/xtm-slice-21m`. Ausgangscommit und Parent:
`6e7c8fc9f247a3e4419299caa7836366573c8c63`.
Der vorgefundene Branch war `codex/xtm-slice-21l`; Index und Arbeitsbaum waren sauber.
[initial-state.json](../reports/slice-21m/initial-state.json) erhält den Zustand
und SHA-256 aller ursprünglich versionierten Dateien. Vor der Reader-Änderung
reproduzierte ein frischer Offline-SBCL 2.5.4 alle **1972 bisherigen XTM-Prüfungen**
und alle **124 Diagnosen** identisch zu Slice 21L. Siehe
[baseline.log](../reports/slice-21m/baseline.log),
[baseline-xtm.json](../reports/slice-21m/baseline-xtm.json),
[before-diagnostics.json](../reports/slice-21m/before-diagnostics.json) und
[initial-source-preparation.json](../reports/slice-21m/initial-source-preparation.json).
Ausgangsstand: XTM **63 PASS / 0 FAIL / 61 NOT-RUN**;
gespeicherter CTM-Stand **262 PASS / 4 FAIL / 7 NOT-RUN**, im vollständigen Lauf erneut bestätigt.

Normativ hergeleitet aus [XTM 2.0 §§4.3.1–4.3.4 und 4.10](https://www.isotopicmaps.org/sam/sam-xtm/):
Das optionale `name/@reifier` bezeichnet das den Name reifizierende Topic.
Seine IRI wird prozent-/UTF-8-dekodiert und gegen die Document IRI aufgelöst.
Die Suche trifft ausschließlich Topic-II; auf einem Miss wird die II-Identität
erzeugt. Das Attribut erzeugt keinen Name-II. Parent, Type, Scope und Value
bestimmen den Name. Der Default-Type hat den SI
`http://psi.topicmaps.org/iso13250/model/topic-name`.
[TMDM §§5.3.4–5.4 und 6.2–6.3](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/)
unterscheiden Name-Gleichheit anhand von Parent, Type, Value und Scope von
Reifier-Identität. Name-Normalisierung erhält Identifier und Reification;
Reifier gleicher Information Items werden zusammengeführt. Topics mit
verschiedenen nichtleeren Reified-Beziehungen dürfen nicht zusammengeführt werden.
Diese Herleitung ist von den folgenden tatsächlichen Ausführungsbefunden getrennt.

[api-preflight.lisp](../reports/slice-21m/api-preflight.lisp) lief **vor jeder
Reader-Änderung** in frischem SBCL. `add-default-name`/`add-name` liefern bereits
den kanonischen Name; ein zweiter gleicher Aufruf kann dasselbe Objekt liefern.
`set-item-reifier` erhält diesen Name, liefert dessen aktuellen kanonischen
Handle zurück und setzt die native inverse Beziehung über `topic-reified`.
Die Vorprüfung belegt auch echte Normalisierung zweier zunächst verschiedener
Names nach Parent-Merging: Beide alten Handles führen zum neuen gemeinsamen
Name. Ein vorhandener Reifier bleibt erhalten; zwei zulässige Reifier werden
mitsamt ihren IIs vereinigt. Die beiden Name-II-Mengen bleiben ebenfalls erhalten.
Unzulässige Wiederverwendung und Merging verschiedener Reified-Beziehungen
liefern `REIFICATION-ERROR/:reifier-conflict`; die Kollision einer neuen Topic-II
mit einem fremden Name-II liefert `OCCURRENCE-IDENTIFIER-ERROR/:duplicate-item-identifier`.
Alle geprüften nativen Ablehnungen erhalten Identitäten und Handles atomar.
Siehe [Vorablog](../reports/slice-21m/api-preflight-before-reader.log) und
[wiederholte Abnahme](../reports/slice-21m/name-reifier-api-preflight.log).
Eine TMDM-Änderung war nicht erforderlich.

## Begrenzte Reader-Erweiterung und Reihenfolge

Produktionsänderungen betreffen ausschließlich `src/xtm/reader.lisp`:

1. `validate-source` akzeptiert Name-Reification und prüft deren Attribut mit
   dem vorhandenen Resolver; alle bisherigen Syntaxprüfungen bleiben bestehen.
2. Die II-Auflösung aus `read-map-reifier` ist in `read-item-reifier` gemeinsam
   nutzbar. Der Map-Wrapper ruft dieselbe Operation auf. `find-reference-topic`
   und dessen SI-/II-Suchregel bleiben unverändert.
3. `read-name` bestimmt Parent, Type, Scope und Value und erhält den kanonischen
   Rückgabewert der vorhandenen Name-Erzeugung. Danach werden Name-II am
   aktuellen Handle erhalten beziehungsweise ergänzt. `read-item-reifier`
   setzt die native Reification. Sein Rückgabewert wird als aktueller Name
   für die folgende Variant-Verarbeitung weiterverwendet. Zurückgegeben wird
   `canonical-topic-name`.

Die Reihenfolge gilt für alle Eingaben; es gibt keine Sonderbehandlung von
Originalfällen. Die IRI-Auflösung kann native SI-/II-Identität auslösen, und
`set-item-reifier` kann Reifier-Topics zusammenführen. Deshalb ist gerade dessen
kanonischer Rückgabewert vor weiteren Variant-Operationen erforderlich.
SI allein ist kein anfänglicher II-Treffer: Bei anschließender nativer
SI-/II-Zusammenführung muss der neue II dennoch vorhanden sein. Ein SL allein
bewirkt kein solches Merging. Keine zusätzliche Registry, Objektart oder
Transaktionssemantik für den vollständigen Reader wurde eingeführt.

## Zwei unveränderte Originalverträge

| Original | Quellbytes | Name-Elemente | normalisierte Names | Reifier | CXTM Ist/Soll |
| --- | ---: | ---: | ---: | --- | ---: |
| `name-reifier.xtm` | 180 | 1 | 1 | `#reifier` | **434/434** |
| `name-duplicate-reified.xtm` | 251 | 2 | 1 | `#reifier1` | **435/435** |

Beide XML-Quellen definieren den Parent `topic/@id="topic"`. Jeder Name hat
Value `Topic`, keinen expliziten Type, keinen Scope, keinen Item Identifier
und keinen Variant. Im zweiten Original stehen **zwei vollständig gleiche
Name-Elemente mit demselben Reifier `#reifier1`**. Das wurde aus dem tatsächlichen
XML geprüft; es wird keine zusätzliche Beziehung aus dem Dateinamen abgeleitet.

Die Document IRI ist jeweils dieser Präfix plus Case-ID `xtm2/in/<Dateiname>`:

```text
https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/
```

Der Source Key ist die Case-ID. Vollständige Document IRIs, Quellhex,
Quelltext und CXTM-Ausgaben sind in
[candidate-inventory.json](../reports/slice-21m/candidate-inventory.json) und
[name-reifier-originals.json](../reports/slice-21m/name-reifier-originals.json) erhalten.

Das tatsächliche native Modell enthält je drei Topics: Parent, Default-Name-Type
und Reifier. Es enthält genau einen kanonischen Name und keine Associations,
Variants, Occurrences oder Rollen. Der Parent hat ausschließlich `DocumentIRI#topic`
als II, der Reifier ausschließlich `DocumentIRI#reifier` beziehungsweise
`DocumentIRI#reifier1`. Nur der Default-Type hat seinen vorgesehenen SI.
Map und Name haben keine II; es gibt keine SL oder zusätzlichen SI.

`topic-name-parent(name)` ist **EQ** zum Parent; der Type ist **EQ** zum
Default-Type. `item-reifier(name)` ist **EQ** zum kanonischen Reifier-Topic;
`topic-reified(reifier)` ist **EQ** zum selben kanonischen Name. Parent, Type
und Map werden durch dieses Attribut nicht reifiziert. Der doppelte Name des
zweiten Originals wird über die bestehende native Name-Gleichheit wiederverwendet.

Beide Originale werden mit unveränderten Rohbytes über
`topic-maps.xtm:deserialize-octets` verarbeitet. Instrumentierte Prüfungen
belegen pro Aufruf genau einen Eintritt in den qualifizierten XML-Parser mit
dem originalen Bytevektor per EQ. Ein unabhängiger Source Key erzeugt dasselbe
Modell und dieselben CXTM-Bytes. Wiederholte Kanonisierung ist deterministisch
und erhält vollständigen Modellzustand sowie aktuelle und festgehaltene Handles.
Beide vollständigen Ausgaben entsprechen den unveränderten Baselines,
einschließlich abschließendem LF. Condition und `firstDifferentByte` sind jeweils null.
Die tatsächlichen Ausgaben stehen in [actual/](../reports/slice-21m/actual/).

| Original | SHA-256 Quelle | SHA-256 Baseline = tatsächliche Ausgabe |
| --- | --- | --- |
| `name-reifier.xtm` | `6c7bc5c3ed096994578b40f7cf42d0509a4e1c6f5655e7b59abedd3bd851a44c` | `ebe1d29a01d2a2693ec4154a03bbe65494745f421b013b45113ada095d4b2239` |
| `name-duplicate-reified.xtm` | `ca99c45dd6515c620038860ffb7977fef88170d7fce85cfe536c4162470d3edb` | `ecdd8cfed65c9536c4c8d91df4c92a94922ba0e67bb4d29c378617087ce0d1d7` |

Der vorhandene Case-Record-Executor zählt die zwei Originale erst nach
Deserialisierung, nativen Modellprüfungen und vollständigem Bytevergleich als
PASS. Die ASDF-Registrierung führt beide tatsächlich aus: **65 eindeutige
Case Records, 57 positive und acht ursachenqualifizierte negative Originale**.
Die bisherigen 63 Originalergebnisse bleiben vollständig identisch.
Synthetische und diagnostische Beobachtungen zählen nicht als neue Verträge.

## Native Handles, Name-Normalisierung und Grenzen

[tests/xtm-name-reification.lisp](../tests/xtm-name-reification.lisp) ergänzt
das bestehende ASDF-Testsystem. Der reguläre Lauf besteht mit
**2157 eindeutigen XTM-Prüfungen**: 1972 erhaltene,
davon acht präzise umbenannte Labels, und **185 neue**.
Die relative Reihenfolge der bisherigen Prüfungen bleibt erhalten.
[xtm.json](../reports/slice-21m/xtm.json) enthält 44 neue Kontrollzeilen mit
Quellen und tatsächlichen Modellen oder Conditions; weitere Native-/EQ-Prüfungen
stehen in dessen `checks` und im [XTM-Log](../reports/slice-21m/xtm.log).

Die Gegenproben prüfen absolute, relative, Fragment-, leere und Nicht-Shorthand-
Referenzen, Unicode, XML-Escaping, Whitespace und Prozent-/UTF-8-Dekodierung.
Ein bereits vorhandener II-Reifier wird wiederverwendet. Ein SI-Treffer allein
muss den erforderlichen II ergänzen; ein gleichlautender SL bleibt getrennt.
Name-II, Map-II, Parent-II und Reifier-II bleiben ihren tatsächlichen Items zugeordnet.
Expliziter Type und Scope, ein folgender Variant mit Value, Datatype und
Scope-Vereinigung sowie gleichzeitige Map-/Name-Reification bestehen.

Gleiche Names mit demselben Reifier normalisieren idempotent. Gleiche Names
mit verschiedenen zulässigen Reifiern bewahren beide Name-II und vereinigen
die Reifier-II. Verschiedene Names behalten ihre verschiedenen Reifier.
Eine zunächst implizite Reifier-Identität wird bei einer späteren Topic-Definition
mit zusätzlicher II korrekt zusammengeführt. Das alte Reifier-Handle, der
Name-Reifier und beide Topic-IDs zeigen per `canonical-topic`/EQ auf dasselbe
aktuelle Objekt; die inverse Beziehung und vollständige II-Vereinigung bleiben erhalten.

Alle **neun Kombinationen** aus Parent-, Type- oder Scope-Merging über SI, SL
oder II werden mit den tatsächlichen Reader-Operationen schrittweise ausgeführt.
Vorher bestehen zwei verschiedene Names und Reifier. Nachher führen beide
alten Name-Handles zum gemeinsamen Name, beide Reifier-Handles zum gemeinsamen
Reifier und dessen inverse Beziehung zum gemeinsamen Name. Die Name-II und
Reifier-II werden jeweils vollständig vereinigt. Type/Scope/Parent sind die
richtigen kanonischen Objekte. Der schrittweise Zustand entspricht dem Ergebnis
der gleichen Originalbytes über die öffentliche API. CXTM-Kanonisierung erhält
auch die privaten Forward-Referenzen der festgehaltenen alten Handles.

Zwei unterschiedliche Konflikte bleiben getrennt:

- Werden verschiedene **aktuell lebende Items** mit demselben Topic reifiziert,
  scheitert die native Zuweisung als `REIFICATION-ERROR/:reifier-conflict`.
  Auch die Zusammenführung zweier bereits verschiedene Items reifizierender
  Topics scheitert so. Das gilt selbst dann, wenn deren eigene Names nach einem
  hypothetischen Parent-Merge gleich wären: TMDM 6.2 verbietet diesen Topic-Merge
  bereits wegen der verschiedenen Reified-Beziehungen. Eine spätere mögliche
  Name-Normalisierung hebt diesen Konflikt nicht auf.
- Kollidiert ein erforderlicher Reifier-Topic-II mit einem fremden Information
  Item, bleibt die native `:duplicate-item-identifier`-Condition erhalten.
  Sie wird nicht in eine XTM-Rejection umgewandelt.

Die vier nativen Konfliktkontrollen prüfen die vorhandene atomare Operation
auf vollständige Zustands-/Identifier-/Handle-Erhaltung. Diese Aussage gilt
für die native Zuweisung, Erzeugung oder Zusammenführung; es gibt keine neue
Atomaritätszusage für den gesamten Reader.

## Tatsächliche Conditions und Syntaxgegenproben

| Gegenprobe | Condition | Code | Zeile:Spalte |
| --- | --- | --- | --- |
| `name:space` | `XTM-REJECTION` | `invalid-iri` | 1:101 |
| `name:bad-percent` | `XTM-REJECTION` | `invalid-percent-escape` | 1:101 |
| `name:bad-utf8` | `XTM-REJECTION` | `invalid-percent-utf8` | 1:104 |
| `name:surrogate-utf8` | `XTM-REJECTION` | `invalid-percent-utf8` | 1:107 |
| `name:decoded-control` | `XTM-REJECTION` | `invalid-iri` | 1:101 |
| `name:relative-colon` | `XTM-REJECTION` | `invalid-iri` | 1:102 |
| `name:extra-attribute` | `XTM-REJECTION` | `unexpected-attribute` | 1:106 |
| `name:qualified-reifier` | `XTM-REJECTION` | `unexpected-attribute` | 1:114 |
| `name:reifier-child` | `XTM-REJECTION` | `unexpected-element` | 1:103 |
| `name:wrong-namespace` | `XTM-REJECTION` | `invalid-namespace` | 1:114 |
| `name:identity-order` | `XTM-REJECTION` | `element-order` | 1:140 |
| `name:malformed-XML` | `XTM-XML-ERROR` | `xml-not-well-formed` | 1:111 |
| `name:variant-remains-unsupported` | `XTM-UNSUPPORTED` | `reification` | 1:134 |
| `name:name-own-II-collision` | `OCCURRENCE-IDENTIFIER-ERROR` | `duplicate-item-identifier` | keine native Quellposition |
| `name:map-II-collision` | `OCCURRENCE-IDENTIFIER-ERROR` | `duplicate-item-identifier` | keine native Quellposition |
| `name:reuse-reifier` | `REIFICATION-ERROR` | `reifier-conflict` | keine native Quellposition |
| `name:native-reuse-reifier` | `REIFICATION-ERROR` | `reifier-conflict` | keine native Quellposition |
| `name:native-distinct-reified-merge` | `REIFICATION-ERROR` | `reifier-conflict` | keine native Quellposition |
| `name:native-II-collision` | `OCCURRENCE-IDENTIFIER-ERROR` | `duplicate-item-identifier` | keine native Quellposition |
| `name:native-parent-merge-reifier-conflict` | `REIFICATION-ERROR` | `reifier-conflict` | keine native Quellposition |

Positionen sind ungefähre SAX-Zeile/Spalte. Native TMDM-Conditions behalten
fehlende Quellposition und Cause als null. Vollständige Messages, Details,
XML-Causes, Source Keys und Document IRIs sind im JSON protokolliert.
Ungültige Attribute, qualifiziertes `reifier`, falscher Namespace, ein
`reifier`-Kindelement und falsche II-Reihenfolge sind XTM-Syntaxfehler.
Variant-Reification bleibt trotz gültiger Name-Reification Unsupported.
Malformed XML bleibt `XTM-XML-ERROR` und ist kein Syntax-/TMDM-Konflikt.

Vier obsolete Unsupported-Kontrollzeilen verwenden nun gültige ausgeschlossene
Variant-Reification anstelle der nun unterstützten Name-Reification. Die
entsprechenden acht Labels sind gezielt umbenannt, Condition-Klasse und Code
bleiben gleich. [retargeted-controls.json](../reports/slice-21m/retargeted-controls.json)
erhält jeweils alte und neue Quelle und Condition; die Abnahme prüft diese
exakten Unterschiede und Identität aller anderen bisherigen XTM-Berichtsfelder.
Die allgemeinen direkten und CTM/XTM-Mergemap-Unsupported-Fixtures wurden ebenso
auf Variant-Reification verschoben, mit unveränderten Labels und Codes.
Historische Berichte bleiben unangetastet.

## Alle 124 Originaldiagnosen; drei weitere Erfolge ohne Registrierung

[diagnostic-changes.json](../reports/slice-21m/diagnostic-changes.json) erhält
sämtliche vorherigen und nachfolgenden Conditions, Codes, Positionen und
vollständigen CXTM-Texte. **Genau fünf Diagnosen ändern sich**; die übrigen
**119 Beobachtungen bleiben vollständig identisch**.
Die fünf bisherigen `XTM-UNSUPPORTED/:reification` werden jetzt erfolgreich
mit jeweils vollständig identischen Originalbaselines deserialisiert.

| Original | Vorher Zeile:Spalte | CXTM Ist/Soll | Registrierung in Slice 21M |
| --- | --- | ---: | --- |
| `name-duplicate-reified.xtm` | 3:31 | 435/435 | PASS |
| `name-duplicate-reified2.xtm` | 3:31 | 701/701 | **NOT-RUN**, nur Diagnose |
| `name-duplicate-reified3.xtm` | 3:31 | 497/497 | **NOT-RUN**, nur Diagnose |
| `name-duplicate-reified4.xtm` | 3:31 | 497/497 | **NOT-RUN**, nur Diagnose |
| `name-reifier.xtm` | 3:30 | 434/434 | PASS |

Die drei unregistrierten Quellen wurden einzeln gelesen:
`name-duplicate-reified2.xtm` ergänzt am ersten gleichen Name einen bereits
unterstützten textuellen Variant in Scope `#ahwell`.
`name-duplicate-reified3.xtm` weist dem ersten Name `itemIdentity="#name"` zu,
`name-duplicate-reified4.xtm` dem zweiten. Die übrigen Name-Eigenschaften und
der gemeinsame Reifier `#reifier1` sind gleich. Die vorhandene Name-/Variant-
und Identifier-Normalisierung verarbeitet diese Quellen nach der Erweiterung
bereits vollständig. Das sind tatsächliche zusätzliche diagnostische Erfolge,
keine neuen Registrierungen. Quellen als Hex/Text, SHA-256, Baselinegrößen und
vollständige Beobachtungen stehen in
[further-name-reification-observations.json](../reports/slice-21m/further-name-reification-observations.json).

`reifier-collision.xtm` bleibt wegen ausgeschlossener Occurrence-Verarbeitung
`XTM-UNSUPPORTED/:unsupported-construct` bei 3:36 und NOT-RUN.
`role-duplicate-reified.xtm` und `topicref-no-fragment-id.xtm` bleiben ebenfalls
unregistriert. Keine bloß verschobene Unsupported-Condition zählt als PASS.
Topic-Map-Reification einschließlich ihres bisherigen Originals bleibt unverändert.

## Vollständige Offline-Abnahme und Integrität

[execution.json](../reports/slice-21m/execution.json) protokolliert
**83 frische Prozessaufrufe**, ihre Kommandos, UTC-Zeiten sowie tatsächliche
und erwartete Exitcodes. Jeder Ausführungsprozess verwendet `sandbox-exec`
mit Netzwerk- und Repository-Schreibsperre. SBCL ist exakt **2.5.4** ohne
System-/Benutzerinitialisierung. Gepinnte lokale Abhängigkeiten und die
bestehenden XML-Patches werden offline geprüft und temporär vorbereitet.
Kein Download, kein Nix-Rebuild und kein langlebiges Lisp-Image.
[validate-slice-21m.py](../scripts/validate-slice-21m.py) folgt der vorhandenen
Validierungskette und führt keine zweite Konformitätsarchitektur ein.

| Bereich | Tatsächliches Ergebnis |
| --- | ---: |
| Erhaltene TMDM-/CTM-/CXTM-Prüfungen | 12100 PASS |
| XML-Qualifikation | 146 PASS |
| XTM | 2157 PASS |
| CTM/XTM-Mergemap | 217 PASS |
| Slice 20A / 20B / 20C | 286 / 25 / 171 PASS |
| Slice 20E / 20F / 20G / 20H | 13 / 112 / 226 / 722 PASS |
| Python-Unittests | 2 PASS |
| NFC-Oracle | 16294 Vergleiche PASS |
| Executor-Faults | 77 erwartete ASDF-Fehlschläge nachgewiesen |

Alle 66 bisherigen Fehlerkontrollen bleiben erhalten. Zwei neue Familien
prüfen für **jedes** neue Original CXTM-Byteabweichung, XML-Fehler, XTM-Fehler,
Unsupported und einen tatsächlich durch den Reader ausgelösten nativen
Reification-Konflikt. Der beschädigte Vertrag zählt nie als PASS; sämtliche
vorangehenden Original-PASS bleiben erhalten. Eine zusätzliche Kontrolle
ersetzt die erwartete native `:reifier-conflict`-Ursache durch den tatsächlich
ausgelösten `:foreign-reifier`. Der ASDF-Lauf scheitert spezifisch daran;
die 65 zuvor korrekt bestandenen Originalverträge bleiben davon getrennt.
Auch bei einem solchen Kontrollfehler wird die tatsächliche Condition mit
`unwind-protect` dauerhaft im Bericht gesichert. Siehe
[failure-controls.json](../reports/slice-21m/failure-controls.json),
[failure-controls.lisp](../reports/slice-21m/failure-controls.lisp) und die Einzelberichte/Logs.

[regression.log](../reports/slice-21m/regression.log) und
[retained/](../reports/slice-21m/retained/) belegen die vollständige Regression.
Alle **48 bisherigen Nicht-XTM-Berichte** sind strukturell identisch zu Slice 21L.
Die vier bekannten CTM-Abweichungen bleiben unverändert:
`include-template.ctm`, `include-wildcard2.ctm`,
`occurrence-datetime-timezone2.ctm`, `occurrence-datetime2.ctm`.

Erst nach tatsächlicher Ausführung ermittelter registrierter Stand:
**XTM 65 PASS / 0 FAIL / 59 NOT-RUN**;
**CTM 262 PASS / 4 FAIL / 7 NOT-RUN**.

[integrity.json](../reports/slice-21m/integrity.json) prüft
**2006 gepinnte Korpusdateien** nach Größe und SHA-256,
**2900 historische Berichte** und
**5155 geschützte Dateien des Ausgangscommits**, einschließlich
TMDM, CTM, CXTM und XML. Originalquellen, Baselines, Corpus-Lock und historische
Reports bleiben unverändert. Ausgeführte Reader-, Test- und Treiberquellen
werden vor und nach der gesamten Abnahme zusätzlich auf identische Hashes geprüft.
[precommit-audit.json](../reports/slice-21m/precommit-audit.json) erhält die
abschließende Pfad-/Hashprüfung;
[artifacts.json](../reports/slice-21m/artifacts.json) sichert alle neuen Artefakte
mit SHA-256 (Manifest selbst ausgenommen).

Nicht abgenommene Entwicklungsversuche sind separat in
[development-attempts.json](../reports/slice-21m/development-attempts.json) samt
vollständigen Logs erhalten: eine zusätzliche Klammer in der neuen Testdatei,
doppelte staged/public Prüflabel und ein Klammerfehler im ergänzten Faultdriver.
Beim ersten vollständigen Abnahmelauf wählte der Python-Treiber aus dem
Teilbericht eines absichtlich fehlgeschlagenen zweiten Originals den falschen
Listeneintrag. Die tatsächliche `REIFICATION-ERROR/:reifier-conflict` war am
richtigen Case bereits korrekt erhalten. Die Auswertung wählt jetzt über die
exakte Case-ID; anschließend wurde die gesamte Abnahme mit unverändertem Reader
und unveränderten Tests wiederholt. Diese Fehlstarts sind keine abgenommenen
Konformitätsläufe. Die fachliche TMDM-Vorprüfung bestand vor der
Reader-Implementierung; die finale vollständige Abnahme besteht danach.

Keine Variant-/Occurrence-/Association-/Role-Reification, keine Occurrences,
expliziten Associations/Roles, XTM-`mergeMap`, zusätzlichen Datentypen oder
XTM-2.1-Funktionen. Keine Änderungen an TMDM, CTM, CXTM oder XML.
Keine HyperDoc-Änderung, kein Push und kein Deployment. Slice 21M endet mit
dem gemeinsamen lokalen Commit von Reader, Tests, Dokumentation und Evidenz.
