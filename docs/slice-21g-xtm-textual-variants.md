# Slice 21G — XTM 2.0 Name Variants mit textuellem resourceData

## Ausgangszustand und Wiederaufnahme

Basis und Commit-Parent: `a8d514d5a3a6026bc5440c67ab666630783398b3`; Branch `codex/xtm-slice-21g`. Der anfängliche Branch `codex/xtm-slice-21f`, HEAD, Index und Arbeitsbaum wurden geprüft; vor Slice 21G waren Index und Arbeitsbaum sauber. Der frische Ausgangslauf in SBCL 2.5.4 reproduzierte den Slice-21F-Report mit 1215 XTM-Prüfungen exakt. Beobachteter registrierter Ausgangsstand: **XTM 50 PASS, 0 FAIL, 74 NOT-RUN; CTM 262 PASS, 4 FAIL, 7 NOT-RUN.**

Die Implementierung wurde nach einer Unterbrechung durch das Nutzungslimit auf demselben Branch mit unverändertem HEAD fortgesetzt. Bei der Wiederaufnahme war der Index weiterhin leer. Alle begonnenen Reader-/Testdateien und die vorhandene Evidenz wurden gelesen und per SHA-256 gesichert; diese Inhalte wurden bei der Fortsetzung vollständig erhalten. Ergänzt wurden Abnahmetreiber, dauerhafte Berichte und Dokumentation. Siehe [initial-state.json](../reports/slice-21g/initial-state.json), [resumption-state.json](../reports/slice-21g/resumption-state.json), [baseline-xtm.json](../reports/slice-21g/baseline-xtm.json) und [baseline.log](../reports/slice-21g/baseline.log).

## Normative Herleitung und Reader-Operationen

Normativ hergeleitet: [XTM 2.0 §§4.12–4.13](https://www.isotopicmaps.org/sam/sam-xtm/) ordnen den Variant dem Parent-Name zu und vereinigen die expliziten Scope-Topics mit dessen Scope. [§4.16](https://www.isotopicmaps.org/sam/sam-xtm/) bestimmt den Textwert und den Standarddatentyp `xsd:string`. [TMDM §5.5](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/) verlangt eine echte Obermenge der Name-Scope und definiert Variant-Gleichheit anhand von Parent, Value, Datatype und Scope. Die folgenden Ergebnisse sind ausgeführt und beobachtet.

```text
S_variant = S_name ∪ S_explicit
S_name ⊂ S_variant
```

Produktiv geändert wurde ausschließlich `src/xtm/reader.lisp`: `validate-source` akzeptiert Variants nach dem Name-Value und prüft genau einen nichtleeren Scope sowie genau eine Resource in der richtigen Reihenfolge. Die unterstützte Resource ist textuelles `resourceData`; explizites `xsd:string` wird ebenso wie der Standarddatentyp verarbeitet. `read-variant` verwendet `reference-iri`/`find-reference-topic` für kanonische Theme-Topics und übergibt die Scope-Vereinigung an die vorhandene TMDM-Operation `add-variant`. Diese bildet die kanonische Menge und erzwingt die echte Obermengenbedingung. `read-name` verarbeitet seine Variants am tatsächlichen kanonischen Name-Handle. Keine Änderung an TMDM, CTM, CXTM, XML oder der IRI-Auflösung.

## Sechs Originalverträge

Alle Originalquellen wurden vor der Implementierung gelesen. Die fünf positiven Fälle verwenden textuelles `resourceData` ohne zusätzliche Datentypen, Variant-Item-Identifier oder Reifier. Im negativen Original sind Name-Scope und explizite Variant-Scope jeweils genau `#command`; die Vereinigung fügt deshalb kein Theme hinzu. Die Bearbeitung blieb vollständig im freigegebenen Umfang.

Für jedes positive Original: unveränderte Rohbytes → `deserialize-octets` → qualifizierter XML-Parser → native Modellprüfung → CXTM-Originalvergleich → bestehender Case Record. Source-Key ist die Case-ID `xtm2/in/<Dateiname>`; Document IRI ist `https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/` plus diese Case-ID. Ein unabhängiger anderer Source-Key erzeugt dasselbe Modell und dieselben CXTM-Bytes.

| Original | Quellbytes | CXTM tatsächlich / Baseline | Name-Scope | Variant-Scope | Status |
|---|---:|---:|---|---|---|
| `variant.xtm` | 307 | **597 / 597 Bytes** | ∅ | `#command` | PASS |
| `variant-duplicate.xtm` | 455 | **597 / 597 Bytes** | ∅ | `#command` | PASS |
| `variant-scope-duplicate.xtm` | 345 | **597 / 597 Bytes** | ∅ | `#command` | PASS |
| `variant-scope-multiple.xtm` | 343 | **731 / 731 Bytes** | ∅ | `#command`, `#silly` | PASS |
| `variant-inherit.xtm` | 372 | **793 / 793 Bytes** | `#english` | `#english`, `#command` | PASS |

Beobachtete native Modelle: jeweils ein Name mit Value `Topic` am kanonischen Parent-Topic `DocumentIRI#topic`, Default-Name-Type und genau ein Variant mit Value **`TOPIC!`** und Datatype **`http://www.w3.org/2001/XMLSchema#string`**. Der Variant-Parent ist per `EQ` genau der tatsächliche Name. Name-, Variant- und Theme-Handles sind kanonisch. Doppelte Variants und wiederholte Theme-Referenzen sind normalisiert. Es entstehen keine Variant-Item-Identifier oder Reifier. Kanonisierung ist deterministisch und erhält Modellzustände und Handles. Alle fünf Vergleiche haben `firstDifferentByte: null` und keine Condition.

Der negative Vertrag `xtm2/invalid/variant-missing-scope-duplicate.xtm` enthält **404 Bytes**. Er erreicht tatsächlich **`VARIANT-ERROR`, `:invalid-variant-scope`**, Detail: `Variant scope must properly contain its Parent Name scope.` Diese native TMDM-Condition besitzt keine Quellposition oder Cause; ihre Reportfelder sind ausdrücklich `null`. Die separat aus dem XML-Ereignisbaum beobachtete Variant-Elementposition ist **8:16** (approximative SAX-Position, keine Condition-Position). Der Vertrag wird nur bei dieser Klasse, diesem Code und diesem Detail als PASS registriert. Beliebige andere Fehler, Unsupported oder eine Annahme sind kein PASS.

Vollständige Rohbytes, lesbarer Quelltext, Document IRIs, Source-Keys, native Modelle, tatsächliche/erwartete CXTM-Ausgaben und die native Negativ-Condition: [variant-originals.json](../reports/slice-21g/variant-originals.json). Tatsächliche Byteausgaben: [actual/](../reports/slice-21g/actual/).

| Original | SHA-256 Quelle | SHA-256 Baseline = tatsächliche Ausgabe |
|---|---|---|
| `variant.xtm` | `b69e6c1143e087133a2c8016f1cd656e7a1e138dd5dc82bb55ca6e049203806a` | `7076e59abf281e3439045bdc3fde7887ff5772ccc532f77c68b177b3ea2ff68b` |
| `variant-duplicate.xtm` | `e256a746059346bf0779d42bbc9c72089edb44833507d5e5a7b21bae742dee06` | `7076e59abf281e3439045bdc3fde7887ff5772ccc532f77c68b177b3ea2ff68b` |
| `variant-scope-duplicate.xtm` | `949b3c8917bab79ad450567a011e78007bc36631d4d918c8ee70ce6a6ce653cf` | `7076e59abf281e3439045bdc3fde7887ff5772ccc532f77c68b177b3ea2ff68b` |
| `variant-scope-multiple.xtm` | `27bad5bbd96149964923ef11a9ff0b024461d9e13c6ba151e2f22dc78ab73fd5` | `1ffe1be12d2706189c2a1ebb0d3626c51cecc40c467ea51ef28834cbcad4526f` |
| `variant-inherit.xtm` | `ca041e98ef6f7ecde47a8ca6fcda2bc764cd01cd4d0f2c912ab73daf7892eeef` | `32b352e866673a8da7adc00db887a80d14eceea86dc09f260c05f30bdf38e450` |
| `variant-missing-scope-duplicate.xtm` | `91a6ec6e0d36c0b5e996969a3cebaef074417d44804de87487603aa80c6c922d` | negativer Vertrag, keine CXTM-Baseline |

## Native Gegenproben und Handles

`tests/xtm-variants.lisp` ist im vorhandenen ASDF-System `topic-maps/xtm/tests` registriert und wird von `run-tests` tatsächlich ausgeführt. Keine zweite Testarchitektur. Die bestehenden Case Records und Klassifizierungsfunktionen werden weiterverwendet; das bestehende Condition-Reportformat wurde um native Variant-Conditions ergänzt. Der erfolgreiche Lauf enthält **1397 eindeutig benannte XTM-Prüfungen**: 1205 bisherige Prüfnamen unverändert, zehn bewusst umbenannte Unsupported-Fixture-Prüfungen und 182 neue Prüfungen. Alle bisherigen 50 Original-Case-Records einschließlich Modell-/Byte-/Condition-Daten sind exakt unverändert.

| Gruppe | Anzahl | Tatsächliche Prüfung |
|---|---:|---|
| Positive XML-Gegenproben | 12 | Text, Unicode, Escaping, Whitespace, leere Werte, explizites xsd:string, Scope-Vererbung, Mengenbildung, Forward References und SI-/II-Treffer ohne zusätzliche II |
| Gestufte native Reader-Merges | 9 | Parent, Name-Theme und Variant-Theme jeweils über SI, SL und II; kanonische Name-/Variant-/Theme-Handles und Normalisierung |
| Fehler-/Unsupported-Gegenproben | 29 | 18 Syntaxfehler, fünf gültige ausgeschlossene Konstrukte und sechs native TMDM-Ablehnungen |
| Atomare Scope-Collapse-Prüfungen | 3 | SI-/SL-/II-Mutation wird mit :variant-scope-collapse ohne Modelländerung zurückgewiesen |

Bei den neun gestuften Gegenproben werden zunächst zwei verschiedene Variant-Objekte behalten. Nach dem Bridge-Merge zeigen beide alten Variant-Handles per `canonical-variant`/`EQ` auf dasselbe aktuelle Objekt; dessen Parent ist der kanonische Name. Die alten Name- und Theme-Handles lösen sich ebenfalls kanonisch auf. Name-Item-Identifier bleiben erhalten. Scope-Mengen sind korrekt und echt größer als die Name-Scope. CXTM-Erzeugung verändert weder diese Zustände noch Handles. Unterschiedliche Values (einschließlich Leerzeichen) oder unterschiedliche Scopes halten Variants getrennt.

Die drei atomaren Gegenproben verwenden tatsächlich deserialisierte Maps. Die vorhandene Modelloperation zur Topic-Identifier-Zuweisung würde Name- und zusätzliche Variant-Themes zusammenführen. `VARIANT-ERROR/:variant-scope-collapse` verhindert dies vor der Mutation. Vollständiger Zustand, Identifier und kanonische Handles bleiben gleich. Die bestehende TMDM-Vorprüfung wurde wiederverwendet und nicht geändert.

## Conditions, Syntax und ausgeschlossene Konstrukte

| Gegenprobe | Native Condition | Code | Condition-Position |
|---|---|---|---|
| `equal` | `VARIANT-ERROR` | `invalid-variant-scope` | null (native TMDM-Condition) |
| `explicit-subset` | `VARIANT-ERROR` | `invalid-variant-scope` | null (native TMDM-Condition) |
| `duplicate-adds-no-theme` | `VARIANT-ERROR` | `invalid-variant-scope` | null (native TMDM-Condition) |
| `SI-alias-adds-no-theme` | `VARIANT-ERROR` | `invalid-variant-scope` | null (native TMDM-Condition) |
| `forward-merge-collapses-proper-scope` | `VARIANT-ERROR` | `variant-scope-collapse` | null (native TMDM-Condition) |
| `topicRef-conflicts-with-name-II` | `OCCURRENCE-IDENTIFIER-ERROR` | `duplicate-item-identifier` | null (native TMDM-Condition) |
| `collapse-SUBJECT-IDENTIFIER` | `VARIANT-ERROR` | `variant-scope-collapse` | null (native TMDM-Condition) |
| `collapse-SUBJECT-LOCATOR` | `VARIANT-ERROR` | `variant-scope-collapse` | null (native TMDM-Condition) |
| `collapse-ITEM-IDENTIFIER` | `VARIANT-ERROR` | `variant-scope-collapse` | null (native TMDM-Condition) |
| `empty-variant` | `XTM-REJECTION` | `missing-variant-scope` | 1:109 |
| `missing-scope` | `XTM-REJECTION` | `missing-variant-scope` | 1:122 |
| `missing-resource` | `XTM-REJECTION` | `missing-variant-resource` | 1:108 |
| `empty-scope` | `XTM-REJECTION` | `empty-scope` | 1:116 |
| `scope-wrong-child` | `XTM-REJECTION` | `unexpected-element` | 1:122 |
| `scope-text` | `XTM-REJECTION` | `unexpected-text` | 1:115 |
| `multiple-scopes` | `XTM-REJECTION` | `duplicate-variant-scope` | 1:151 |
| `scope-after-resource` | `XTM-REJECTION` | `element-order` | 1:181 |
| `multiple-resources` | `XTM-REJECTION` | `variant-resource-cardinality` | 1:188 |
| `mixed-resources` | `XTM-REJECTION` | `variant-resource-cardinality` | 1:201 |
| `variant-attribute` | `XTM-REJECTION` | `unexpected-attribute` | 1:118 |
| `data-attribute` | `XTM-REJECTION` | `unexpected-attribute` | 1:168 |
| `XTM-markup-in-data` | `XTM-REJECTION` | `unexpected-child` | 1:165 |
| `unknown-child` | `XTM-REJECTION` | `unexpected-element` | 1:116 |
| `text-in-variant` | `XTM-REJECTION` | `unexpected-text` | 1:108 |
| `wrong-namespace` | `XTM-REJECTION` | `invalid-namespace` | 1:126 |
| `bad-href` | `XTM-REJECTION` | `invalid-topic-ref` | 1:139 |
| `resourceRef-missing-href` | `XTM-REJECTION` | `missing-attribute` | 1:158 |
| `resourceRef` | `XTM-UNSUPPORTED` | `unsupported-construct` | 1:171 |
| `itemIdentity` | `XTM-UNSUPPORTED` | `unsupported-construct` | 1:136 |
| `reifier` | `XTM-UNSUPPORTED` | `reification` | 1:121 |
| `datatype` | `XTM-UNSUPPORTED` | `resource-data-datatype` | 1:179 |
| `embedded-XML` | `XTM-UNSUPPORTED` | `resource-data-markup` | 1:179 |

Die native `:invalid-variant-scope`-Ablehnung wird ausdrücklich auch bei gleicher Scope, expliziter Teilmenge, bloßen Duplikaten und verschiedenen Referenzen auf dasselbe bereits identifizierte Theme geprüft. Ein späterer Merge kann mit `:variant-scope-collapse` scheitern; dies ist von der ursprünglichen Scope-Verletzung zu unterscheiden. Ein TopicRef-Konflikt mit einem Name-Item-Identifier bleibt die bestehende native `OCCURRENCE-IDENTIFIER-ERROR/:duplicate-item-identifier`-Condition. Die historische Klassenbezeichnung bedeutet keine XTM-Occurrence-Unterstützung.

Gültige `resourceRef`, weitere Datentypen, eingebettetes XML, Variant-Item-Identifier und Reification bleiben Unsupported. Die Untergrammatiken ausgeschlossener Sprachfähigkeiten werden nicht vollständig implementiert. Textuelles `resourceData` akzeptiert XML-Character-Data und das vorhandene XML-Decoding; XTM-Markup darin wird als Syntaxfehler zurückgewiesen. Unicode-Sequenzen werden als Text erhalten, XML-Escapes einmal aufgelöst und XML-Zeilenenden nach der vorhandenen Parserverarbeitung übernommen.

## Erhaltene und bewusst geänderte Diagnosen

Von 124 read-only Korpusbeobachtungen bleiben **108 exakt unverändert**. 16 Beobachtungen ändern sich nach zuvor Unsupported Variant. Die sechs beauftragten Fälle sind registriert; die übrigen Beobachtungen ändern keine Case Records.

| Original | Beobachtetes Ergebnis nach Änderung | Registrierung in 21G |
|---|---|---|
| `xtm2/in/itemid-variant.xtm` | `XTM-UNSUPPORTED/unsupported-construct` | bleibt NOT-RUN |
| `xtm2/in/merge-itemid-with-variants.xtm` | bytegenau deserialisiert | bleibt NOT-RUN |
| `xtm2/in/variant-datatype-unknown.xtm` | `XTM-UNSUPPORTED/resource-data-datatype` | bleibt NOT-RUN |
| `xtm2/in/variant-duplicate-iid.xtm` | `XTM-UNSUPPORTED/unsupported-construct` | bleibt NOT-RUN |
| `xtm2/in/variant-duplicate-reifier.xtm` | `XTM-UNSUPPORTED/reification` | bleibt NOT-RUN |
| `xtm2/in/variant-duplicate-reifier2.xtm` | `XTM-UNSUPPORTED/reification` | bleibt NOT-RUN |
| `xtm2/in/variant-duplicate.xtm` | bytegenau deserialisiert | NOT-RUN → PASS |
| `xtm2/in/variant-inherit.xtm` | bytegenau deserialisiert | NOT-RUN → PASS |
| `xtm2/in/variant-reifier.xtm` | `XTM-UNSUPPORTED/reification` | bleibt NOT-RUN |
| `xtm2/in/variant-resourcedata-uri.xtm` | `XTM-UNSUPPORTED/resource-data-datatype` | bleibt NOT-RUN |
| `xtm2/in/variant-resourceref-relative.xtm` | `XTM-UNSUPPORTED/unsupported-construct` | bleibt NOT-RUN |
| `xtm2/in/variant-resourceref.xtm` | `XTM-UNSUPPORTED/unsupported-construct` | bleibt NOT-RUN |
| `xtm2/in/variant-scope-duplicate.xtm` | bytegenau deserialisiert | NOT-RUN → PASS |
| `xtm2/in/variant-scope-multiple.xtm` | bytegenau deserialisiert | NOT-RUN → PASS |
| `xtm2/in/variant.xtm` | bytegenau deserialisiert | NOT-RUN → PASS |
| `xtm2/invalid/variant-missing-scope-duplicate.xtm` | `VARIANT-ERROR/invalid-variant-scope` | NOT-RUN → PASS |

Insbesondere wurde `merge-itemid-with-variants.xtm` nur in der Diagnoseprobe bytegenau beobachtet. Dieser zusätzliche Vergleich bleibt ausdrücklich **unregistriert / NOT-RUN** und erhöht die PASS-Zahl nicht. Die erste Berichtsauswertung wurde für diese tatsächliche zusätzliche Beobachtung korrigiert; anschließend wurde die vollständige Abnahme mit dem endgültigen Validator in frischen Prozessen wiederholt. Reader und vorhandene Tests blieben dabei unverändert.

Die vier bisherigen Unsupported-Fixtures verwenden jetzt gültiges ausgeschlossenes `resourceRef` statt textuellem `resourceData`. Klasse `XTM-UNSUPPORTED` und Code `unsupported-construct` bleiben erhalten; der Detailtext nennt `resourceRef`, die SAX-Spalte liegt wegen des später erreichten Elements jeweils 70 Zeichen weiter. Für `unsupported-is-not-pass`: **1:108 → 1:178**. Nur die entsprechend benannten Fixture-/Prüfnamen und zugehörigen Source-Keys ändern sich. Alle anderen bisherigen Gegenprobendatensätze bleiben exakt gleich. Vollständige Signaturen und Vorher-/Nachher-Daten: [diagnostic-changes.json](../reports/slice-21g/diagnostic-changes.json), [before-diagnostics.json](../reports/slice-21g/before-diagnostics.json), [after-diagnostics.json](../reports/slice-21g/after-diagnostics.json).

30 separate Executor-Fehlerkontrollen starten frische ASDF-Prozesse. Die bisherigen 21 Kontrollen bleiben erhalten; vier prüfen den neuen positiven Variant-Pfad und fünf den negativen Originalpfad. Byteabweichung, XML-/XTM-/TMDM-Fehler, Unsupported, Annahme und falsche negative Ursache führen zum erwarteten ASDF-Abbruch und niemals zu einem zusätzlichen PASS. Für die falsche negative Ursache wird sogar dieselbe native Klasse `VARIANT-ERROR` mit dem falschen Code `variant-scope-collapse` statt `invalid-variant-scope` erzeugt. Siehe [failure-controls.json](../reports/slice-21g/failure-controls.json) sowie die tatsächlichen Fehlerreports und Logs.

## Vollständige Offline-Regression und registrierter Stand

Frische SBCL-2.5.4-Prozesse mit `--no-sysinit --no-userinit`. Die zusätzliche Betriebssystem-Sandbox verbietet Netzwerk und Repository-Schreibzugriff während aller Tests. Abhängigkeiten stammen ausschließlich aus verifizierten gepinnten lokalen Quellen; bestehende XML-Patches werden auf temporäre Kopien angewandt. Alle Kommandos, Start-/Endzeiten und tatsächlichen/erwarteten Exitcodes: [execution.json](../reports/slice-21g/execution.json).

| Prüfung | Tatsächliches Ergebnis |
|---|---:|
| Bestehende Lisp-Regression (TMDM, CTM/CXTM, Identität, Literale, Merging, Templates, Include/Mergemap) | 12100 PASS |
| XML-Qualifikation | 146 PASS |
| XTM einschließlich 50 bisheriger und sechs neuer Originalverträge | 1397 PASS |
| XTM-MERGEMAP | 217 PASS |
| REGISTERED-ORIGINALS | 286 PASS |
| REGISTERED-NEGATIVES | 25 PASS |
| PROLOG | 171 PASS |
| EMPTY2 | 13 PASS |
| CTM-INTEGER | 112 PASS |
| TRIPLE | 226 PASS |
| ENCODING | 722 PASS |
| Python-Unittests | 2 PASS |
| NFC-Oracle | 16294 Vergleiche PASS |
| Executor-Fehlerkontrollen | 30 erwartete ASDF-Abbrüche |

48 behaltene Nicht-XTM-JSON-Reports sind gegenüber Slice 21F qualifiziert identisch; nur der dokumentierte Unsupported-Fixture-/Prüfname ändert sich. Die vier bekannten CTM-FAILs bleiben mit unveränderten Ergebnissen erhalten:

- `ctm/in/include-template.ctm`
- `ctm/in/include-wildcard2.ctm`
- `ctm/in/occurrence-datetime-timezone2.ctm`
- `ctm/in/occurrence-datetime2.ctm`

Nach tatsächlicher vollständiger Ausführung: **XTM 56 PASS, 0 FAIL, 68 NOT-RUN; CTM 262 PASS, 4 FAIL, 7 NOT-RUN.** Die XTM-Registrierung umfasst 48 positive und acht qualifizierte negative Originalverträge; 65 positive und drei negative Originale bleiben NOT-RUN. Gegenproben und zusätzliche Diagnosebeobachtungen erhöhen diese registrierten Zahlen nicht.

## Integrität, Abgrenzung und Reproduktion

Alle **2006 gepinnten Korpusdateien** wurden nach Größe und SHA-256 geprüft. **1877 historische Reportdateien** und **4115 geschützte Basisdateien** bleiben bytegleich. Originalquellen, Baselines und historische Berichte sind unverändert. Quellstand, Tests und Abnahmetreiber sind durch SHA-256-Snapshots über die Ausführung hinweg gesichert. Siehe [integrity.json](../reports/slice-21g/integrity.json) und [source-preparation.json](../reports/slice-21g/source-preparation.json).

Produktiv geändert wurde ausschließlich der XTM-Reader für textuelle Name-Variants. Keine Änderung an TMDM, CTM, CXTM oder XML. Keine resourceRef-Verarbeitung, weiteren Datentypen, Variant-Item-Identifier, Reification, Occurrences, expliziten Associations/Roles oder XTM-mergeMap. Keine Downloads, HyperDoc-/anderen Repository-Änderungen, langlebigen Image-Loads, Pushes oder Deployments. Die reguläre Freigabe wurde verwendet; keine Änderung an `~/.nix-profile` oder der Sandbox-Konfiguration.

Reproduktion mit dem vorhandenen lokalen Store und neuem temporären Ausgabeverzeichnis:

```sh
python3 scripts/validate-slice-21g.py \
  --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  --output /private/tmp/topic-maps-21g-review
```

Der Validator überschreibt keine historischen Ergebnisse. Die versionierte Abschlussevidenz wurde erst nach erfolgreicher Abnahme bytegleich aus dem endgültigen temporären Lauf übernommen. Ein vollständiger Nix-Neubau wurde nicht ausgeführt. Reader, Tests und überprüfte Evidenz werden gemeinsam lokal committet; danach endet Slice 21G.
