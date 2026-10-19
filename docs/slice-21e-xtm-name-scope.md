# Slice 21E — XTM 2.0 Topic Name Scope

## Ausgeführter Umfang und Ausgangszustand

Basis und Commit-Parent: `d034a8deafa7cf74b2264ea8a7bd5cc0950806bf`; Branch `codex/xtm-slice-21e`. Der Ausgangsbranch `codex/xtm-slice-21d`, HEAD, Index und Arbeitsbaum wurden geprüft; der Ausgangszustand war sauber. Ein frischer SBCL-2.5.4-Prozess ohne Benutzer-/Systeminitialisierung reproduzierte alle 935 bisherigen XTM-Prüfungen und einen strukturell identischen Report zu Slice 21D. Siehe [Ausgangszustand](../reports/slice-21e/initial-state.json), [Baseline](../reports/slice-21e/baseline-xtm.json) und [Ausgangslauf](../reports/slice-21e/baseline.log).

Beobachteter registrierter Ausgangsstand: **XTM 43 PASS, 0 FAIL, 81 NOT-RUN; CTM 262 PASS, 4 FAIL, 7 NOT-RUN.** Die fünf Scope-Originale wurden erst nach tatsächlicher Deserialisierung, nativen Modellprüfungen und vollständigem CXTM-Bytevergleich als PASS registriert.

## Normative Grundlage und Anbindung

Die folgenden Anforderungen sind aus der Norm abgeleitet, die nachfolgenden Ergebnisse sind beobachtet:

- [XTM 2.0 §4.10](https://www.isotopicmaps.org/sam/sam-xtm/) ordnet den optionalen Scope zwischen Type und Value ein; höchstens ein Name-Scope ist erlaubt.
- [XTM 2.0 §4.13](https://www.isotopicmaps.org/sam/sam-xtm/) verlangt mindestens ein `topicRef`; deren Topics bilden eine Menge.
- [XTM 2.0 §4.20 und §4.3.4](https://www.isotopicmaps.org/sam/sam-xtm/) bestimmen Referenzauflösung, SI-/II-Treffer und neue II-Platzhalter. Ein Treffer erfordert keinen zusätzlichen II.
- [TMDM §§5.3.3 und 5.4](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/) definieren Scope als Topic-Menge und Name-Gleichheit anhand von Parent, Type, Value und Scope.
- [TMDM §§6.1–6.3](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/) verlangen nach identitätsbedingten Topic-Merges aktualisierte Referenzen und gegebenenfalls Name-Merging.

`src/xtm/reader.lisp:validate-source` akzeptiert Scope ausschließlich im bisher unterstützten Name-Kontext. Die vorhandene Reihenfolgeprüfung bleibt erhalten; neu sind `:duplicate-name-scope` und `:empty-scope`. Die Scope-Prüfung erlaubt keine Attribute und ruft für jedes Kind die vorhandene TopicRef-/IRI-Prüfung auf. Andere Eltern wie Occurrence und Association bleiben vor ihren Untergrammatiken Unsupported.

`read-name` verarbeitet den Type vor den Scope-Referenzen und reicht die Topics als `:scope` an `topic-maps.tmdm:add-name` beziehungsweise `add-default-name` weiter. `reference-iri` und `find-reference-topic` bleiben unverändert. Die bestehenden TMDM-Operationen `canonical-scope`, `same-scope-p`, Topic-Merging und `normalize-names` übernehmen Set-Bildung, kanonische Referenzen und Name-Normalisierung. Keine parallele Modellrepräsentation; keine Änderung an TMDM, CTM, CXTM oder XML.

## Fünf ausgeführte Originalverträge

Für jedes Original gilt: unveränderte gepinnte Rohbytes → `deserialize-octets` → qualifizierter XML-Parser → native Parent-/Type-/Value-/Scope-Prüfungen → CXTM → bestehender Case Record. Document IRI ist jeweils `https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/` plus Case-ID `xtm2/in/<Dateiname>`; Source-Key ist exakt diese Case-ID. Ein anderer Source-Key erzeugt dieselben Identitäten und Bytes.

| Original | Quelle Bytes | CXTM tatsächlich / Baseline | Value | Type | Scope nach Normalisierung | Status |
|---|---:|---:|---|---|---|---|
| `name-scope.xtm` | 227 | **483 / 483** | `Emne` | Default-Name-Type | `#norwegian` | PASS |
| `name-scope-multiple.xtm` | 262 | **618 / 618** | `Emne` | Default-Name-Type | `#norwegian`, `#danish` | PASS |
| `name-scope-duplicate.xtm` | 265 | **483 / 483** | `Emne` | Default-Name-Type | `#norwegian` (einmal) | PASS |
| `name-scope-duplicate-merged.xtm` | 325 | **506 / 506** | `Emne` | Default-Name-Type | `#no` EQ `#norwegian` (ein Theme) | PASS |
| `name-type-scope.xtm` | 310 | **471 / 471** | `Emner` | `http://psi.ontopia.net/xtm/basename/#plural` (II) | `#norwegian` | PASS |

Alle fünf Maps haben genau ein Name-Item am kanonischen Parent `#topic`, keine Associations und keine ausgeschlossenen Name-Eigenschaften. Die vier Default-Names verwenden den Topic mit SI `http://psi.topicmaps.org/iso13250/model/topic-name`. `name-type-scope` verwendet einen separaten expliziten Type-Topic. Die Modellprüfungen vergleichen die tatsächlichen Objekte mit `EQ`, prüfen vollständige Topic-Identifier-Mengen und kanonische Name-Handles. Die Kanonisierung ist wiederholbar und verändert weder Modell noch Handles oder Originalbytes. Jeder Vergleich hat `firstDifferentByte: null` und keine Condition.

Exakte Rohbytes (Hex und lesbarer Quelltext), Document IRI, Source-Key, native Modellreferenzen sowie vollständige tatsächliche und erwartete CXTM-Ausgabe stehen in [scope-originals.json](../reports/slice-21e/scope-originals.json); die tatsächlichen Byteausgaben liegen unter [actual/](../reports/slice-21e/actual/). Es wurden keine handgebauten Modelle als Originalverträge gezählt.

| Original | SHA-256 Quelle | SHA-256 Baseline = tatsächliches CXTM |
|---|---|---|
| `name-scope.xtm` | `44b14ba5da4048c383a337ef1f15d18cf5d5d718ffe848bf3811eefac4090224` | `9a1258dbc6c26b835717205c081ad4db72d347c9b4a13bcf9e80adbecbca4584` |
| `name-scope-multiple.xtm` | `fefe14d0d9689dfcb25d1a660a16ed0b950105cb8a71863a071ffc813cf7aaee` | `de65aae448329c7ed5281b3f9c6783915fcf92c4bf756512875a64fd52393686` |
| `name-scope-duplicate.xtm` | `4bfc5ce2e6c9addc5aa4c384728542dc50111911d34a923732746c2764df8d51` | `9a1258dbc6c26b835717205c081ad4db72d347c9b4a13bcf9e80adbecbca4584` |
| `name-scope-duplicate-merged.xtm` | `043e54de5da62a74cb132d6a022593612461faa6fcee55e552703a239672e0c7` | `9764166e65434b0f20aad62bc2b133d00a37d2be31ebcf1a8090e5c3299e89fa` |
| `name-type-scope.xtm` | `4ba8f4cdcf1e40e8ac76b5c3bec6883faa18bd1fb955e94450bf3cee1060fb72` | `ccb9fde3906f36fe58218488149465325043295d705c399ade1cfb2c4c3da469` |

## Mengen, Referenzen, Handles und Merging

Die 38 dauerhaften Gegenproben sind im bestehenden `topic-maps/xtm/tests`-System registriert. `run-tests` führt Scope-Originale und Scope-Gegenproben tatsächlich aus. Die bestehenden Case Records und Klassifizierungsfunktionen werden weiterverwendet. Der erfolgreiche Lauf enthält **1082 eindeutig benannte Prüfungen**: 929 bisherige Namen unverändert, vier bewusste Umbenennungen der Unsupported-Fixture, zwei entfernte Scope-Unsupported-Prüfungen mit neuer positiver Abdeckung und 149 neue Prüfungen. Die bisherigen 43 Original-Case-Records und deren positive/negative Ergebnisdaten sind unverändert.

Elf positive XML-Gegenproben beobachten: einzelnes Theme und Forward Reference; mehrere Themes mit umgekehrter Reihenfolge und Wiederholungen; Name-Kollaps bei gleicher Scope-Menge; getrennte Names bei verschiedenen oder unbeschränkten Scopes; separaten Type und Scope trotz identischem Topic; SI-/II-Referenztreffer ohne zusätzlichen II; einen SL-only-Nichttreffer als separaten II-Platzhalter; UTF-8-Prozentreferenzen ohne Abruf; Parent als Theme; Default-Type als Theme; sowie Parent-Merging mit mengenidentischen Scopes.

Drei gestufte Gegenproben führen die echten Reader-Operationen in Dokumentreihenfolge aus und behalten die ursprünglichen Topic- und Name-Handles: je ein SI-, SL- und II-Bridge-Merge. Vor dem Merge existieren zwei verschiedene Themes und drei Names (zwei mit Value `N`, einer mit `D`). Nach dem Merge zeigen beide alten Theme-Handles auf denselben kanonischen Topic. Die beiden alten `N`-Handles zeigen auf denselben kanonischen Name; die Name-Scope enthält genau ein Theme. Beim `D`-Name kollabiert die zuvor aus zwei Themes bestehende Scope auf ein Theme. Die zwei unterschiedlichen Values bleiben als zwei Names bestehen. CXTM-Erzeugung erhält alle geprüften Handles und Zustände. Diese gestuften Gegenproben sind keine Korpusregistrierungen.

## Syntax und Conditions

Die 24 Fehler-/Unsupported-Gegenproben enthalten 19 ungültige und fünf gültige ausgeschlossene Konstrukte. Jede prüft konkrete native Condition-Klasse, Fehlercode, Document IRI, Source-Key und positive SAX-Zeile/-Spalte. Die Positionen sind approximative SAX-Positionen am Starttag-Ende, keine Bytepositionen. Alle tatsächlich beobachteten Signaturen einschließlich Detail, Message und Cause stehen in `scopeControls` des [XTM-Reports](../reports/slice-21e/xtm.json).

| Gegenprobe | Native Condition | Code | Zeile:Spalte |
|---|---|---|---|
| `scope:empty` | `XTM-REJECTION` | `empty-scope` | 1:91 |
| `scope:whitespace-only` | `XTM-REJECTION` | `empty-scope` | 1:90 |
| `scope:text-without-topicRef` | `XTM-REJECTION` | `unexpected-text` | 1:90 |
| `scope:wrong-child` | `XTM-REJECTION` | `unexpected-element` | 1:123 |
| `scope:attribute` | `XTM-REJECTION` | `unexpected-attribute` | 1:100 |
| `scope:multiple` | `XTM-REJECTION` | `duplicate-name-scope` | 1:126 |
| `scope:before-later-type` | `XTM-REJECTION` | `element-order` | 1:125 |
| `scope:missing-href` | `XTM-REJECTION` | `missing-attribute` | 1:101 |
| `scope:empty-href` | `XTM-REJECTION` | `invalid-topic-ref` | 1:109 |
| `scope:no-fragment` | `XTM-REJECTION` | `invalid-topic-ref` | 1:114 |
| `scope:invalid-fragment` | `XTM-REJECTION` | `invalid-topic-ref` | 1:114 |
| `scope:bad-percent` | `XTM-REJECTION` | `invalid-percent-escape` | 1:114 |
| `scope:bad-utf8` | `XTM-REJECTION` | `invalid-percent-utf8` | 1:114 |
| `scope:bad-IRI` | `XTM-REJECTION` | `invalid-iri` | 1:113 |
| `scope:ref-attribute` | `XTM-REJECTION` | `unexpected-attribute` | 1:121 |
| `scope:nested-ref` | `XTM-REJECTION` | `unexpected-child` | 1:110 |
| `scope:namespace` | `XTM-REJECTION` | `invalid-namespace` | 1:110 |
| `scope:ref-namespace` | `XTM-REJECTION` | `invalid-namespace` | 1:131 |
| `scope:after-value` | `XTM-REJECTION` | `element-order` | 1:106 |
| `scope:variant-stays-unsupported` | `XTM-UNSUPPORTED` | `unsupported-construct` | 1:144 |
| `scope:name-II-stays-unsupported` | `XTM-UNSUPPORTED` | `unsupported-construct` | 1:108 |
| `scope:name-reifier-stays-unsupported` | `XTM-UNSUPPORTED` | `reification` | 1:96 |
| `scope:occurrence-stays-unsupported` | `XTM-UNSUPPORTED` | `unsupported-construct` | 1:89 |
| `scope:association-stays-unsupported` | `XTM-UNSUPPORTED` | `unsupported-construct` | 1:76 |

Variants, Name-Item-Identifier und Reification bleiben Unsupported. Dasselbe gilt für Occurrence und Association einschließlich ihrer Scopes. Die alte gültige Name-Scope-Unsupported-Fixture wurde in Klassifizierungs- und CTM/XTM-Mergemap-Kontrollen durch gültige Name-Item-Identity ersetzt. Der Fehler bleibt `XTM-UNSUPPORTED/:unsupported-construct`; für `unsupported-is-not-pass` wechselt die Detailursache von Scope zu ItemIdentity, die Quellposition wegen der anderen Fixture von 1:90 zu 1:108. Die übrigen 49 bisherigen Name-Gegenproben bleiben in ihren Ergebnisdaten exakt gleich.

## Diagnosedifferenzen des gesamten XTM-Korpus

Alle 124 Originalquellen wurden vor und nach der Änderung read-only beobachtet; diese Diagnoseprobe registriert keine weiteren Verträge. 117 Beobachtungen sind strukturell exakt identisch. Genau sieben ändern sich nach vormals Unsupported Name-Scope:

| Original | Zuvor | Jetzt | Registrierungsänderung |
|---|---|---|---|
| `xtm2/in/name-scope-duplicate-merged.xtm` | `XTM-UNSUPPORTED/unsupported-construct`, 4:14, Scope | CXTM bytegenau | NOT-RUN → PASS |
| `xtm2/in/name-scope-duplicate.xtm` | `XTM-UNSUPPORTED/unsupported-construct`, 4:14, Scope | CXTM bytegenau | NOT-RUN → PASS |
| `xtm2/in/name-scope-multiple.xtm` | `XTM-UNSUPPORTED/unsupported-construct`, 4:14, Scope | CXTM bytegenau | NOT-RUN → PASS |
| `xtm2/in/name-scope.xtm` | `XTM-UNSUPPORTED/unsupported-construct`, 4:14, Scope | CXTM bytegenau | NOT-RUN → PASS |
| `xtm2/in/name-type-scope.xtm` | `XTM-UNSUPPORTED/unsupported-construct`, 5:14, Scope | CXTM bytegenau | NOT-RUN → PASS |
| `xtm2/in/variant-inherit.xtm` | `XTM-UNSUPPORTED/unsupported-construct`, 4:14, Scope | `XTM-UNSUPPORTED/unsupported-construct`, 8:16, Variant | bleibt NOT-RUN |
| `xtm2/invalid/variant-missing-scope-duplicate.xtm` | `XTM-UNSUPPORTED/unsupported-construct`, 4:14, Scope | `XTM-UNSUPPORTED/unsupported-construct`, 8:16, Variant | bleibt NOT-RUN |

Vollständige Signaturen und ursprüngliche Kontext-/Cause-Felder sind in [before-diagnostics.json](../reports/slice-21e/before-diagnostics.json), [after-diagnostics.json](../reports/slice-21e/after-diagnostics.json) und [diagnostic-changes.json](../reports/slice-21e/diagnostic-changes.json) erhalten. Die vier noch nicht registrierten negativen XTM-Originale bleiben NOT-RUN.

17 zusätzliche Executor-Fehlerkontrollen starten jeweils einen frischen ASDF-Prozess: fünf positive, vier negative, vier Name- und vier Scope-Kontrollen. Gezielt herbeigeführte CXTM-Abweichung, XML-/XTM-/TMDM-Fehler, Unsupported sowie falsche negative Ursache oder Annahme führen zum erwarteten ASDF-Abbruch und niemals zu einem zusätzlichen PASS. Diese Kontrollen verwenden den vorhandenen Executor und dessen Reports; sie sind keine weiteren Korpusfälle. Siehe [failure-controls.json](../reports/slice-21e/failure-controls.json) und die jeweiligen vollständigen Logs/Fehlerreports.

## Vollständige Offline-Regression

Alle Läufe verwenden frische SBCL-2.5.4-Prozesse mit `--no-sysinit --no-userinit`. Die zusätzliche Betriebssystem-Sandbox verbietet Netzwerkzugriffe und Schreibzugriff auf das Repository. ASDF nutzt ausschließlich verifizierte lokale gepinnte Abhängigkeiten; die vorhandenen XML-Patches werden auf temporäre Kopien angewendet. Keine Downloads, kein langlebiges Lisp-Image, kein vollständiger Nix-Neubau. Die Kommandos, Zeitstempel, erwarteten und tatsächlichen Exitcodes sowie Sandbox-Regeln stehen in [execution.json](../reports/slice-21e/execution.json).

| Prüfung | Tatsächliches Ergebnis |
|---|---:|
| Bestehende Lisp-Regression (TMDM, CTM/CXTM, Identität, Merging, Literale, Scopes, Templates, Include/Mergemap) | 12100 PASS |
| XML-Qualifikation | 146 PASS |
| XTM einschließlich 43 bisherigen und fünf neuen Originalen | 1082 PASS |
| XTM-MERGEMAP | 217 PASS |
| REGISTERED-ORIGINALS | 286 PASS |
| REGISTERED-NEGATIVES | 25 PASS |
| PROLOG | 171 PASS |
| EMPTY2 | 13 PASS |
| CTM-INTEGER | 112 PASS |
| TRIPLE | 226 PASS |
| ENCODING | 722 PASS |
| Python-Unittests | 2 PASS |
| Unabhängige NFC-Oracle-Vergleiche | 16294 PASS |
| Executor-Fehlerkontrollen | 17 erwartete ASDF-Abbrüche |

Die 48 behaltenen Nicht-XTM-JSON-Reports sind gegenüber Slice 21D qualifiziert identisch; nur die ausdrücklich dokumentierten Unsupported-Fixture-/Prüfnamen ändern sich. Die vier bekannten CTM-FAILs bleiben unverändert:

- `ctm/in/include-template.ctm`
- `ctm/in/include-wildcard2.ctm`
- `ctm/in/occurrence-datetime-timezone2.ctm`
- `ctm/in/occurrence-datetime2.ctm`

Nach tatsächlicher Ausführung: **XTM 48 PASS, 0 FAIL, 76 NOT-RUN; CTM 262 PASS, 4 FAIL, 7 NOT-RUN.** XTM umfasst 41 positive Originalvergleiche und sieben qualifizierte negative Originale; 72 positive und vier negative Originale bleiben unregistriert. Keine weiteren Korpusverträge wurden als PASS gezählt.

## Integrität, Abgrenzung und Reproduktion

Alle **2006** gepinnten Korpusdateien wurden nach Größe und SHA-256 geprüft. Alle **1651** historischen Reportdateien und **3885** geschützten Basisdateien bleiben bytegleich. Quellen, Baselines, historische Evidenz sowie die ausgeführten Test-/Reader-Dateien wurden über den Lauf hinweg mit SHA-256-Snapshots geprüft. Siehe [integrity.json](../reports/slice-21e/integrity.json) und [source-preparation.json](../reports/slice-21e/source-preparation.json).

Produktiv geändert wurde ausschließlich der XTM-Reader. Teständerungen betreffen Name-Scope, dessen ASDF-Ausführung und die nach der Scope-Unterstützung erforderlichen Unsupported-Fixtures. Keine TMDM-/CTM-/CXTM-/XML-Änderungen; keine Variant-, Occurrence- oder Association-Unterstützung, keine Name-Item-Identifier, Reification, XTM-mergeMap oder XTM-2.1-Erweiterungen. Keine HyperDoc-Änderungen, Pushes oder Deployments. Die reguläre Freigabe wurde verwendet; keine Änderung an `~/.nix-profile` oder der Sandbox-Konfiguration.

Wiederholung aus dem Repository mit einem neuen temporären Ausgabeverzeichnis:

```sh
python3 scripts/validate-slice-21e.py \
  --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  --output /private/tmp/topic-maps-21e-review
```

Der Validator benötigt die bereits lokal vorhandenen gepinnten Store-Pfade. Er schreibt Testergebnisse ausschließlich in das neue temporäre Verzeichnis; die versionierte Evidenz wird dadurch nicht überschrieben. Die hier gespeicherten Abnahmeberichte wurden nach erfolgreicher Abnahme bytegleich aus dem endgültigen temporären Lauf übernommen. Slice 21E endet mit gemeinsamem lokalem Commit von Reader, Tests und dieser Evidenz.
