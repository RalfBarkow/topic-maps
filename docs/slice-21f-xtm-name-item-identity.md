# Slice 21F — XTM 2.0 Item Identity of Topic Names

## Ausgangszustand und Norm

Basis und Commit-Parent: `5d3ed0455de32b9d19ac791b9e4c4882a03c79b8`; neuer Branch `codex/xtm-slice-21f`. Der Ausgangsbranch `codex/xtm-slice-21e`, HEAD, Index und Arbeitsbaum wurden geprüft; der Ausgangszustand war sauber. Ein frischer SBCL-2.5.4-Prozess ohne Benutzer-/Systeminitialisierung reproduzierte die 1082 bisherigen XTM-Prüfungen und den exakt gleichen Report wie Slice 21E. Siehe [initial-state.json](../reports/slice-21f/initial-state.json), [baseline-xtm.json](../reports/slice-21f/baseline-xtm.json) und [baseline.log](../reports/slice-21f/baseline.log).

Beobachteter Ausgangsstand: **XTM 48 PASS, 0 FAIL, 76 NOT-RUN; CTM 262 PASS, 4 FAIL, 7 NOT-RUN.**

Die folgenden Anforderungen sind normativ hergeleitet; die übrigen Ergebnisangaben wurden ausgeführt und beobachtet:

- [XTM 2.0 §§4.3.1 und 4.10](https://www.isotopicmaps.org/sam/sam-xtm/) gestatten null oder mehrere Name-Item-Identity-Elemente vor Type, Scope und Value.
- [XTM 2.0 §§4.3.3–4.3.4 und 4.6](https://www.isotopicmaps.org/sam/sam-xtm/) bestimmen Locator-Auflösung gegen die Document IRI und Zuweisung an das Information Item des Eltern-Elements: hier den Name.
- [TMDM §§4.3 und 5.1](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/) bestimmen Mengen-/Locator-Gleichheit und die globale Eindeutigkeit von Item Identifiern unterschiedlicher Information Items.
- [TMDM §§5.4 und 6.1–6.3](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/) bestimmen Name-Gleichheit über Parent, Type, Value und Scope sowie Identifier-Vereinigung und Referenzersetzung beim Merging.

## Vorprüfung und minimale Reader-Änderung

Vor der Implementierung wurden die vorhandenen TMDM-Operationen tatsächlich geprüft: sechs gestufte Parent-/Theme-Merges über SI, SL und II erhielten Identifier und kanonische Name-Handles. Diese Vorprüfung verwendet den bestehenden Reader für die bisher unterstützte XML-Syntax und weist Identifier über die vorhandene TMDM-API zu. Sie wurde mit dem endgültigen Quellstand identisch reproduziert. Siehe [model-preflight.json](../reports/slice-21f/model-preflight.json), [Treiber](../reports/slice-21f/model-preflight.lisp) und [Log](../reports/slice-21f/model-preflight.log). Eine Modelländerung war nicht erforderlich.

Produktiv geändert wurde ausschließlich `src/xtm/reader.lisp`: `validate-source` lässt Name-`itemIdentity*` im bestehenden Reihenfolgeautomaten zu und prüft jedes Element über die vorhandene Locator-Validierung. `read-name` übernimmt den kanonischen Name von `add-name`/`add-default-name` und fügt dessen aufgelöste Item-Identifier über `add-item-identifier` hinzu. Parent-/Type-Topics werden dabei nicht als Identifier-Owner verwendet. Keine neue Identifier-Registry; keine Änderung an IRI-Auflösung, TMDM, CTM, CXTM oder XML-Parser.

## Tatsächliche Originalquellen und Bytevergleiche

Vor der Implementierung gelesen: `itemid-name.xtm` enthält ein Name-Element mit `itemIdentity href="#the-name"` und Value `Topic`. `name-duplicate-iid.xtm` enthält zwei solcher Name-Elemente am selben Parent mit identischen Properties und demselben Locator. Die Baseline erwartet jeweils einen Name. Die Deutung wurde aus diesen Quellen und den tatsächlichen Ergebnissen bestimmt.

| Original | Quellbytes | Name-Elemente → native Names | CXTM tatsächlich / Baseline | Status |
|---|---:|---:|---:|---|
| `itemid-name.xtm` | 196 | 1 → 1 | **395 / 395 Bytes** | PASS |
| `name-duplicate-iid.xtm` | 285 | 2 → 1 | **395 / 395 Bytes** | PASS |

Document IRI ist für jedes Original `https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/` plus Case-ID `xtm2/in/<Dateiname>`. Der Source-Key ist die Case-ID; ein zweiter unabhängiger Source-Key erzeugt dieselben Identitäten und CXTM-Bytes. Die Originalbytes werden unverändert über `topic-maps.xtm:deserialize-octets` und den qualifizierten XML-Parser verarbeitet.

Beobachtete native Objekte beider Originale: zwei Topics, keine Association, genau ein Name am Topic `DocumentIRI#topic`; Value `Topic`, Default-Type mit SI `http://psi.topicmaps.org/iso13250/model/topic-name`, leere Scope. Der Name enthält genau den Item Identifier **`DocumentIRI#the-name`**. Der Parent enthält ausschließlich `DocumentIRI#topic`; Type und Topic Map haben keine Item Identifier. Kein Reifier und keine Variants. Parent-/Type-/Name-Handles sind kanonisch und per `EQ` geprüft. Eine Suche über alle tatsächlichen Information Items findet den Locator ausschließlich am Name-Item.

Beide vollständigen Bytevergleiche haben `firstDifferentByte: null` und keine Condition. Originalbytes, rohe Hexdarstellung, lesbarer Quelltext, Document IRI, Source-Key, native Modellreferenzen und vollständige CXTM-Ausgaben stehen in [name-item-identity-originals.json](../reports/slice-21f/name-item-identity-originals.json). Die tatsächlichen Bytes liegen unter [actual/](../reports/slice-21f/actual/). Kanonisierung wurde auf Determinismus und unveränderte Modelle/Handles geprüft. Erst native Modellprüfung und tatsächlicher Bytevergleich qualifizieren das PASS im bestehenden Case Record.

| Original | SHA-256 Quelle | SHA-256 Baseline = tatsächliches CXTM |
|---|---|---|
| `itemid-name.xtm` | `95d64ef5047e6b8e21ac956abc44a8d02d18163b1fe50980d4e382fa67f73776` | `5fc741733b889754c7d7f0fffc2bb4ee266ef46cad694630a0b92e93f1a17cd3` |
| `name-duplicate-iid.xtm` | `b878a68cb4c2eaaae70cb8c587fc5110392dece181e064b523831e685654cfdf` | `5fc741733b889754c7d7f0fffc2bb4ee266ef46cad694630a0b92e93f1a17cd3` |

## Dauerhafte Gegenproben und Normalisierung

ASDF `topic-maps/xtm/tests` lädt `tests/xtm-name-item-identities.lisp`; `run-tests` führt beide Originale und alle 46 Gegenproben tatsächlich aus. Der bestehende Harness, Case Records, Klassifizierungsfunktionen, Name-/Scope-Modellprüfungen und Reportformat werden weiterverwendet. Der erfolgreiche Lauf enthält **1215 eindeutig benannte Prüfungen**: 1074 bisherige Prüfnamen unverändert, vier bewusst umbenannte Unsupported-Fixture-Prüfungen, vier durch positive Abdeckung ersetzte Item-Identity-Unsupported-Prüfungen sowie 137 neue Prüfungen. Die bisherigen 48 Original-Case-Records und ihre Ergebnis-/Modelldaten bleiben exakt identisch.

| Gegenproben-Gruppe | Anzahl | Beobachtung |
|---|---:|---|
| Positive XTM-Gegenproben | 12 | Identifier-Owner, leere/einfache/mehrfache Mengen, relative/absolute IRIs, Dubletten, Name-Gleichheit und unterschiedliche Properties |
| Gestufte native Reader-Merges | 6 | Parent und Theme jeweils über SI, SL und II; Identifier-Vereinigung und erhaltene kanonische Handles |
| Reader mit nativen TMDM-Konflikten | 9 | Eindeutigkeitskonflikte getrennt von XTM-Syntax und Unsupported |
| Native atomare Konfliktprüfungen | 5 | Abgewiesene Zuweisungen verändern Identifier, Modell und Handles nicht |
| Syntax/Unsupported | 14 | 12 Syntaxfehler und zwei gültige ausgeschlossene Konstrukte |

Gleiche Names vereinigen `urn:first` und `urn:second` auch bei umgekehrter Scope-Reihenfolge. Abweichende Values (einschließlich nachfolgendem Leerzeichen), Types, Scopes oder Parents bleiben verschiedene Name-Objekte. Die kombinierte Gegenprobe mit Item Identifier, Type und Scope prüft alle kanonischen Eigenschaften und ihre getrennten Owner. Ein Name-II und ein Topic-SI mit gleichem String erzeugen keine implizite Reification oder gemeinsame Item-Identität.

Eine leere `href`-Referenz ist hier eine gültige relative anyURI und wird zur Document IRI aufgelöst. Ein Item Identifier benötigt im Unterschied zu `topicRef` keinen XPointer-Shorthand-Fragment-Identifier. Fehlendes `href`, ungültige Prozentkodierung, ungültiges UTF-8 und unerlaubte IRI-Zeichen werden spezifisch abgewiesen. Der bestehende IRI-Pfad wird auch mit einer abweichenden Document IRI und einem Unicode-Locator geprüft.

Bei jedem der sechs gestuften Merges werden zwei zunächst verschiedene native Name-Objekte mit den Identifiern `urn:name:1` und `urn:name:2` behalten. Nach dem Bridge-Merge enthalten beide alten Handles dieselbe vereinigte Identifier-Menge und zeigen per `canonical-topic-name`/`EQ` auf den einen Name des kanonischen Parents. Bei Theme-Merges zeigen auch die alten Theme-Handles auf denselben Topic; die Scope enthält diesen einmal. CXTM-Erzeugung verändert diese Zustände und Handles nicht. Die Tests führen tatsächliche Reader-Operationen auf XML in Dokumentreihenfolge aus und zählen als Gegenproben, nicht als zusätzliche Korpusfälle.

## Konflikte und konkrete Conditions

Alle folgenden Konflikte führen zu `:duplicate-item-identifier`; Name-Identifier werden nicht auf Topics umgedeutet oder still überschrieben. Die bestehenden nativen TMDM-Conditions bleiben unverpackt. Die historische Topic-Mutationsroute verwendet `OCCURRENCE-IDENTIFIER-ERROR`, eine Unterklasse von `ITEM-IDENTIFIER-ERROR`; daraus folgt keine XTM-Occurrence-Unterstützung. Diese Conditions besitzen keine Quellpositions- oder Cause-Slots: der Report enthält dort ausdrücklich `null`, keine erfundenen Positionen. Document IRI und Source-Key des Reader-Aufrufs stehen separat im Konfliktdatensatz.

| Reader-Konflikt | Tatsächliche Condition |
|---|---|
| `different-parent-same-II` | `ITEM-IDENTIFIER-ERROR` |
| `different-scope-same-II` | `ITEM-IDENTIFIER-ERROR` |
| `different-type-same-II` | `ITEM-IDENTIFIER-ERROR` |
| `different-value-same-II` | `ITEM-IDENTIFIER-ERROR` |
| `topic-II-after-name` | `OCCURRENCE-IDENTIFIER-ERROR` |
| `topic-after-name` | `OCCURRENCE-IDENTIFIER-ERROR` |
| `map-before-name` | `ITEM-IDENTIFIER-ERROR` |
| `name-type` | `ITEM-IDENTIFIER-ERROR` |
| `name-parent` | `ITEM-IDENTIFIER-ERROR` |

Die fünf atomaren Prüfungen verwenden eine tatsächlich deserialisierte Map und rufen die vorhandene Modelloperation auf: Name → Map-Identifier, Map → Name-Identifier, Name → Topic-Identifier, Topic → Name-Identifier und Name → anderer Name-Identifier. Jede konkrete Condition wird geprüft; das Modell einschließlich Identifier-Mengen und kanonischer Handles bleibt vor/nach dem abgewiesenen Aufruf gleich.

## Syntax und bewusste Diagnosedifferenzen

| Gegenprobe | Condition | Code | Approximative SAX-Zeile:Spalte |
|---|---|---|---|
| `iid:missing-href` | `XTM-REJECTION` | `missing-attribute` | 1:98 |
| `iid:bad-percent` | `XTM-REJECTION` | `invalid-percent-escape` | 1:109 |
| `iid:bad-percent-utf8` | `XTM-REJECTION` | `invalid-percent-utf8` | 1:109 |
| `iid:illegal-IRI-character` | `XTM-REJECTION` | `invalid-iri` | 1:113 |
| `iid:unexpected-attribute` | `XTM-REJECTION` | `unexpected-attribute` | 1:121 |
| `iid:namespaced-attribute` | `XTM-REJECTION` | `unexpected-attribute` | 1:129 |
| `iid:nested-element` | `XTM-REJECTION` | `unexpected-child` | 1:110 |
| `iid:non-whitespace-text` | `XTM-REJECTION` | `unexpected-text` | 1:110 |
| `iid:wrong-namespace` | `XTM-REJECTION` | `invalid-namespace` | 1:131 |
| `iid:after-type` | `XTM-REJECTION` | `element-order` | 1:145 |
| `iid:after-scope` | `XTM-REJECTION` | `element-order` | 1:147 |
| `iid:after-value` | `XTM-REJECTION` | `element-order` | 1:127 |
| `iid:reifier-stays-unsupported` | `XTM-UNSUPPORTED` | `reification` | 1:96 |
| `iid:variant-stays-unsupported` | `XTM-UNSUPPORTED` | `unsupported-construct` | 1:172 |

Alle XTM-Syntaxgegenproben prüfen zusätzlich Document IRI und Source-Key. Gültige Name-Reification und Variants bleiben Unsupported; Name-Scope bleibt unterstützt. Die alten Name-Item-Identity-Unsupported-Fixtures in Klassifizierungs- und Mergemap-Prüfungen wurden durch gültige Name-Variants ersetzt. Für `unsupported-is-not-pass` bleiben Klasse, Code, Kontext, Cause und Position 1:108 identisch; nur Detail/Message nennen jetzt Variant. Die bisherigen 48 übrigen Name- und 37 übrigen Scope-Gegenprobendatensätze bleiben exakt unverändert.

Alle 124 Originalquellen wurden vor und nach der Änderung read-only beobachtet. **122 Beobachtungen sind exakt identisch.** Nur die beiden beauftragten Originale ändern sich von `XTM-UNSUPPORTED/:unsupported-construct` für `itemIdentity` bei **4:39** zu erfolgreicher Deserialisierung mit exaktem CXTM. Keine anderen Originaldiagnosen ändern sich; die vier unregistrierten negativen XTM-Originale bleiben NOT-RUN. Vollständige Signaturen einschließlich Cause: [diagnostic-changes.json](../reports/slice-21f/diagnostic-changes.json), [before-diagnostics.json](../reports/slice-21f/before-diagnostics.json), [after-diagnostics.json](../reports/slice-21f/after-diagnostics.json).

21 separate Executor-Fehlerkontrollen starten frische ASDF-Prozesse: fünf positive sowie jeweils vier negative, Name-, Scope- und Item-Identity-Kontrollen. CXTM-Byteabweichung, XML-/XTM-/TMDM-Fehler, Unsupported und falsche negative Ursache/Annahme lösen den erwarteten ASDF-Abbruch aus und ergeben niemals einen zusätzlichen PASS. Der neue Item-Identity-Pfad erhält bei solchen Fehlern genau die bisherigen 48 PASS und einen fehlerhaften beziehungsweise Unsupported-Case. Siehe [failure-controls.json](../reports/slice-21f/failure-controls.json) sowie die konkreten gespeicherten Fehlerreports und Logs.

## Vollständige Offline-Regression

Frische SBCL-2.5.4-Prozesse mit `--no-sysinit --no-userinit`; Betriebssystem-Sandbox mit Netzwerk- und Repository-Schreibsperre. Der Build verwendet ausschließlich verifizierte lokale gepinnte Quellen und die bestehenden XML-Patches in temporären Dependency-Kopien. Kein zusätzlicher Download oder langlebiges Lisp-Image. Alle Kommandos, Zeitstempel und tatsächlichen/erwarteten Exitcodes stehen in [execution.json](../reports/slice-21f/execution.json).

| Prüfung | Tatsächliches Ergebnis |
|---|---:|
| Bestehende Lisp-Regression (TMDM, CTM/CXTM, Identität, Merging, Literale, Scopes, Templates, Include/Mergemap) | 12100 PASS |
| XML-Qualifikation | 146 PASS |
| XTM einschließlich 48 bisheriger und zwei neuer Originale | 1215 PASS |
| XTM-MERGEMAP | 217 PASS |
| REGISTERED-ORIGINALS | 286 PASS |
| REGISTERED-NEGATIVES | 25 PASS |
| PROLOG | 171 PASS |
| EMPTY2 | 13 PASS |
| CTM-INTEGER | 112 PASS |
| TRIPLE | 226 PASS |
| ENCODING | 722 PASS |
| Vorprüfung vorhandener TMDM-Identifier-Erhaltung | 12 Prüfungen / sechs Merges PASS |
| Python-Unittests | 2 PASS |
| NFC-Oracle | 16294 Vergleiche PASS |
| Executor-Fehlerkontrollen | 21 erwartete ASDF-Abbrüche |

48 behaltene Nicht-XTM-JSON-Reports sind gegenüber Slice 21E qualifiziert identisch; nur die dokumentierten Unsupported-Fixture-/Prüfnamen ändern sich. Die vier bekannten CTM-FAILs bleiben mit ihren bisherigen Ergebnissen unverändert:

- `ctm/in/include-template.ctm`
- `ctm/in/include-wildcard2.ctm`
- `ctm/in/occurrence-datetime-timezone2.ctm`
- `ctm/in/occurrence-datetime2.ctm`

Nach tatsächlicher Ausführung: **XTM 50 PASS, 0 FAIL, 74 NOT-RUN; CTM 262 PASS, 4 FAIL, 7 NOT-RUN.** XTM enthält 43 positive Original-CXTM-Vergleiche und sieben qualifizierte negative Originale; 70 positive und vier negative Originale bleiben unregistriert. Weder Modell-/Syntaxgegenproben noch diagnostische Korpusbeobachtungen erhöhen die Original-PASS-Zahl.

## Integrität, Abgrenzung und Reproduktion

**2006 gepinnte Korpusdateien** wurden anhand von Größe und SHA-256 verifiziert; **1760 historische Reportdateien** und **3996 geschützte Basisdateien** bleiben bytegleich. Alle Originalquellen, Baselines und historischen Reports sind unverändert. Die ausgeführten Reader-/Testquellen sind ebenfalls über SHA-256-Snapshots gesichert. Siehe [integrity.json](../reports/slice-21f/integrity.json) und [source-preparation.json](../reports/slice-21f/source-preparation.json).

Produktiver Umfang: Name-Item-Identifier im XTM-Reader. Keine neue TMDM-Gleichheit oder Modelländerung, keine CTM-Grammatikänderung. Variants, Name-Reification, Occurrences, explizite Associations/Roles, XTM-mergeMap und XTM-2.1 bleiben außerhalb dieses Slices. Keine HyperDoc- oder anderen Repository-Änderungen, keine Pushes oder Deployments. Die reguläre Freigabe wurde verwendet; keine Änderung an `~/.nix-profile` oder der Sandbox-Konfiguration.

Reproduktion mit vorhandenem lokalem Store und einem neuen temporären Ausgabeverzeichnis:

```sh
python3 scripts/validate-slice-21f.py \
  --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  --output /private/tmp/topic-maps-21f-review
```

Der Validator schreibt Ergebnisse ausschließlich in das neue temporäre Verzeichnis. Die hier versionierten Abnahmeberichte wurden nach erfolgreicher Abnahme bytegleich aus dem temporären Lauf übernommen. Ein vollständiger Nix-Neubau wurde nicht ausgeführt. Reader-Erweiterung, Tests und diese Evidenz werden gemeinsam lokal committet; danach endet Slice 21F.
