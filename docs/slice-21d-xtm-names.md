# Slice 21D: XTM Topic Names, Value, Parent und Type

Nach tatsächlicher Ausführung: **XTM 43 PASS, 0 FAIL, 81 NOT-RUN**. CTM bleibt **262 PASS, 4 FAIL, 7 NOT-RUN**. Alle zehn neuen Originalverträge sind bytegleich; alle 33 bisherigen Originalergebnisse bleiben unverändert.

Ausgangspunkt und Parent: `0eed7189a0cdd535c980c2160ae2065de21f5d93`. Ausgangsbranch: `codex/xtm-slice-21c`. Index und Arbeitsbaum waren sauber. Lieferbranch: `codex/xtm-slice-21d`. Reader-Erweiterung, Tests und überprüfte Evidenz werden gemeinsam lokal committet; der Commit-Hash wird nach dem Commit geliefert.

## Normative Grundlage und begrenzte Implementierung

[XTM 2.0 §§4.10, 4.11 und 4.14](https://www.isotopicmaps.org/sam/sam-xtm/) ordnet den Name seinem Parent-Topic zu, verwendet bei fehlendem Type den Topic mit dem Subject Identifier `http://psi.topicmaps.org/iso13250/model/topic-name` und löst explizite Types als Topic-Referenzen auf. Der Value stammt aus den XML-Zeicheninformationen. [TMDM §5.4 und §6.3](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/) bestimmt Name-Gleichheit und Zusammenführung anhand von Value, Type, Scope und Parent.

Die Produktionsänderung beschränkt sich auf `src/xtm/reader.lisp`:

- `validate-source` prüft die unterstützte Name-Untergrammatik: optional genau ein Type vor genau einem Value, ein TopicRef im Type, erlaubte Attribute/Namespaces, ausschließlich Zeicheninhalt im Value sowie Reihenfolge und Kardinalitäten.
- `read-name` fügt die vorhandenen SAX-Zeichenstücke zusammen und ruft `add-name` beziehungsweise `add-default-name` auf. Keine zweite Escape-Interpretation, kein Trimmen und keine zusätzliche Unicode-Normalisierung. Die XML-Zeilenendenverarbeitung bleibt Aufgabe des qualifizierten Parsers.
- `read-topic` dispatcht Name-Kinder auf diese Operation. Topic-Elemente werden weiterhin in Dokumentreihenfolge verarbeitet. Explizite Types verwenden unverändert `find-reference-topic`.

TMDM, CTM, CXTM, XML-Grenze und Name-Normalisierung bleiben byteidentisch. Scope, Variants, Name-Item-Identifier und Name-Reification bleiben in syntaktisch zulässiger Stellung spezifisch Unsupported. Ungültige Stellung oder Syntax wird als XTM-Rejection zurückgewiesen. Die vollständigen Untergrammatiken ausgeschlossener Konstrukte werden hier nicht implementiert.

## Zehn tatsächlich ausgeführte Originalverträge

Originalquelle: `vendor/cxtm/xtm2/in/<Datei>`. Baseline: `vendor/cxtm/xtm2/baseline/<Datei>.cxtm`. Document IRI folgt der unveränderten Korpuskonvention `https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/<Datei>`. Source-Key ist die relative Original-ID; ein zweiter Reader-Aufruf mit anderem Source-Key bestätigt unveränderte Modelle und CXTM-Bytes.

Alle folgenden Ergebnisse sind nach dem realen Reader-Aufruf und den Modellprüfungen registriert. Jede Zeile ist PASS; Condition und erster abweichender Byteoffset sind jeweils NIL. D bezeichnet den oben genannten Default-Type-SI. Fragmente sind relativ zur jeweiligen Document IRI dargestellt.

| Originaldatei | Tatsächlicher Name-Wert | Parent-Identifier | Tatsächlicher Type | CXTM Ist / Baseline Bytes |
|---|---|---|---|---:|
| `name.xtm` | `Topic` | `#topic` | `D` | 329 / 329 |
| `name-unicode.xtm` | `馬籠` | `#topic` | `D` | 330 / 330 |
| `name-escaping.xtm` | `<AT&T>` | `#att` | `D` | 338 / 338 |
| `name-duplicate.xtm` | `Topic` | `#topic` | `D` | 329 / 329 |
| `name-duplicate-merge.xtm` | `Topics` | `#topic` | `#flertall, #plural` | 310 / 310 |
| `merge-itemid-with-names.xtm` | `Topics`; `Topics 2` | `http://example.org/#topic, #topic, #topic2` | `D` | 479 / 479 |
| `name-type.xtm` | `Topics` | `#topic` | `http://psi.ontopia.net/xtm/basename/#plural` | 317 / 317 |
| `name-type-before.xtm` | `Topics` | `#topic` | `D (#nametype)` | 396 / 396 |
| `name-type-after.xtm` | `Topics` | `#topic` | `D (#nametype)` | 396 / 396 |
| `name-type-after-bad.xtm` | `Topics`; `Other` | `#topic; #other` | `D (#nametype)` | 561 / 561 |

Die tatsächlichen TMDM-Objekte werden zusätzlich per `EQ` geprüft: gespeicherte Names sind kanonisch; Parent ist das betreffende kanonische Topic; Type ist ein lebendes kanonisches Topic derselben Map. Die unveränderten Originale werden ausschließlich über `topic-maps.xtm:deserialize-octets` aus Rohbytes gelesen. Keine manuelle Ersatzmap zählt als Originalvertrag.

`name-type-after-bad.xtm` bleibt ein positiver Vertrag: der zuerst erzeugte Default-Type wird mit der späteren `nametype`-Definition zusammengeführt; auch der nachfolgende Name von `other` verwendet dasselbe kanonische Type-Objekt. `name-duplicate-merge.xtm` führt die vorher verschiedenen Type-Referenzen `#plural` und `#flertall` zusammen und normalisiert dadurch die beiden gleichwertigen Names zu einem. `merge-itemid-with-names.xtm` erhält beide Name-Werte am zusammengeführten Parent und alle ursprünglichen Topic-Identifier.

## Originalquellen und Hashes

| Originaldatei | Quellbytes | SHA-256 der unveränderten Quelle |
|---|---:|---|
| `name.xtm` | 161 | `9371957f79b2feccabdba82ddff327bd3e951a46ae99853a98de068922c8261e` |
| `name-unicode.xtm` | 172 | `f273f3ce56b952d8914596eb1ca18861759ee8b7d0c4d13194f8838d9b6d752a` |
| `name-escaping.xtm` | 170 | `6b7af035336ada40cb47b8ddde06cac44a77f9410568ff5b49cdc61325b794a5` |
| `name-duplicate.xtm` | 211 | `5024f457e912925ded85d02149fb5d80da53f1d2588add3170c25601de1c5289` |
| `name-duplicate-merge.xtm` | 417 | `4a3693ba31c308a40491cb292bb3ed8d49366d178c40e9b608d6691acecf68f8` |
| `merge-itemid-with-names.xtm` | 350 | `adc98c4380106b6b42f19142845044075f0dcb5d7c69e5fca0bcd8b754e7c6ba` |
| `name-type.xtm` | 244 | `220887ad8ae950560f5860056e034f019c5b057b1fd52e78fdca5892550f94a0` |
| `name-type-before.xtm` | 280 | `f638ad087c106a303ccc353716b7a4d0c43624386add15ff8060ca0d9f0c615b` |
| `name-type-after.xtm` | 280 | `d150a73d82add96a8c5e273596565470ee717fcbd6c34403af5a19f9cfb9d6ce` |
| `name-type-after-bad.xtm` | 366 | `d12d013cee9199e41a8fa1f7a6e142856863879aade95ab4bd31c6ae5e5cfcaa` |

[name-originals.json](../reports/slice-21d/name-originals.json) enthält Originalbytes als Hex, Quelltext, Document IRI, Source-Key, vollständige Ist-/Baseline-Texte, Quell-/Baseline-/Ist-SHA-256, Bytezahlen und tatsächliche Modelle. Die erzeugten Bytes liegen unverändert unter [actual](../reports/slice-21d/actual/). [candidate-inventory.json](../reports/slice-21d/candidate-inventory.json) trennt die vor der Implementierung festgestellten Baseline-Eigenschaften von der neuen Ausführungsevidenz.

## Identitäts- und Syntaxgegenproben

Im selben vorhandenen ASDF-System `topic-maps/xtm/tests` werden `name-original-contracts` und `name-tests` tatsächlich aufgerufen. Die vorhandenen Case Records und Ergebnisfunktionen werden wiederverwendet. Alle 43 Case IDs sind eindeutig.

Der [Harness-Bericht](../reports/slice-21d/xtm.json) protokolliert 50 zusätzliche Gegenproben:

- `TMDM-only-control-no-XTM-Scope`: 1.
- `negative-or-unsupported-XTM`: 27.
- `positive-XTM`: 17.
- `staged-native-reader-control`: 5.

Die positiven XTM-Gegenproben umfassen leeren und selbstschließenden Value, Unicode einschließlich Astralzeichen und unnormalisierter Zeichenfolge, Escaping genau einmal, Whitespace, XML-Zeilenenden, CDATA/Kommentare/PI und SAX-Zeichenstücke. Default-Type vor/nach Definition, SI-Treffer ohne zusätzlichen II, explizite/Forward-/externe Types, identische Names sowie unterschiedliche Parents und Types werden an tatsächlichen Maps geprüft. Eine externe Topic-Referenz erzeugt unter Netzwerksperre den vorgesehenen Placeholder.

Die fünf gestuften Kontrollen verwenden die vorhandenen nativen Reader-Operationen an tatsächlichen XML-Knoten in Dokumentreihenfolge. Sie behalten Name-, Parent- und Type-Handles über spätere SI-, SL-, II- und Type-Merges hinweg. Vor dem Merge verschiedene Name-Objekte zeigen danach per `canonical-topic-name` auf denselben Name mit korrektem kanonischem Parent/Type. Wiederholte CXTM-Kanonisierung erhält die Handles. Diese Kontrollen sind keine zusätzlichen Originalverträge.

Die eine ausdrücklich als TMDM-Kontrolle markierte Scope-Gegenprobe zeigt die vorhandene Modellgleichheit: identische Werte mit unterschiedlichem Scope bleiben verschiedene Names. Dafür wird kein XTM-Scope eingelesen. Weitere Prüfungen sichern Namespaces und die tatsächliche mehrzeilige Fehlerposition.

Die 23 ungültigen Name-Untergrammatiken werden als `XTM-REJECTION` zurückgewiesen: fehlender/mehrfacher Value, fehlender/mehrfacher Type-TopicRef, mehrfacher Type, falsche Reihenfolge, unbekannte Elemente/Attribute, Text an unzulässiger Stelle, verschachtelter Value, fremdes Markup, Namespace- und Referenzfehler. Vier gültig platzierte ausgeschlossene Konstrukte ergeben `XTM-UNSUPPORTED`: Scope, Variant, Item Identity und Reifier. Jeder protokollierte Fehler enthält tatsächliche Klasse, Code, Detail, Quellkontext und SAX-Position.

## Erhaltene und bewusst veränderte Diagnosen

Von den 692 bisherigen benannten XTM-Prüfungen bleiben 688 Namen unverändert; vier `unsupported-name:*`-Prüfungen heißen jetzt `unsupported-name-scope:*`. Der frühere einfache Name ist unterstützt. Die Unsupported-Fixtures verwenden nun gültigen Name-Scope. Auch die entsprechende CTM/XTM-Mergemap-Fixture wird gezielt umgestellt. Die alten versionierten Berichte und ihre historischen Fehlerkontroll-Driver bleiben unverändert.

Die Diagnose der umgestellten Fixture bleibt `XTM-UNSUPPORTED / unsupported-construct`, benennt aber jetzt `scope` und dessen tatsächliche Position. Die verbleibenden ursprünglichen Original-Conditions, einschließlich aller sieben registrierten negativen Originalverträge, bleiben exakt erhalten.

Der separate read-only Diagnosevergleich führt alle 124 Originale vor und nach der Erweiterung aus: 86 Beobachtungen bleiben exakt gleich. 38 Änderungen betreffen ausschließlich den früheren Unsupported-Punkt am `name`-Element: zehn neue bytegleiche Ergebnisse und 28 weiterhin ausgeschlossene Name-Konstrukte. Es wird dadurch kein weiterer Originalvertrag registriert. [diagnostic-changes.json](../reports/slice-21d/diagnostic-changes.json) enthält jede alte und neue Condition samt Begründung; `before-diagnostics.json` und `after-diagnostics.json` enthalten das vollständige Inventar.

13 frische Fehlerkontrollprozesse sichern weiterhin die tatsächliche ASDF-Abbruch-/Berichtskette: fünf bisherige positive, vier bisherige negative und vier neue Name-Kontrollen. Mismatch, XML-/TMDM-Fehler, Unsupported, Akzeptanz eines Negativfalls oder falsche Fehlerursache erfüllen den jeweiligen Originalvertrag nicht. Die erwarteten Exitcodes 1 sind Kontrollergebnisse. Siehe [failure-controls.json](../reports/slice-21d/failure-controls.json).

## Vollständige Offline-Regression

Alle Testprozesse laufen frisch in SBCL 2.5.4 mit `--no-sysinit --no-userinit`. Die explizite Sandbox sperrt Netzwerk und Schreibzugriffe auf das Repository. Gepinnte lokale Store-Abhängigkeiten werden mit dem bestehenden Verifier geprüft und mit den unveränderten qualifizierten XML-Patches ausschließlich temporär vorbereitet. Keine zusätzlichen Downloads oder langlebigen Lisp-Images.

| Prüfung | Tatsächliches Ergebnis |
|---|---:|
| Bestehende TMDM-/CTM-/CXTM-Suiten | 12.100 Prüfungen bestanden |
| XML-Qualifikation | 146 bestanden |
| XTM einschließlich aller 43 Originalverträge | 935 bestanden |
| XTM-MERGEMAP | 217 bestanden |
| REGISTERED-ORIGINALS | 286 bestanden |
| REGISTERED-NEGATIVES | 25 bestanden |
| PROLOG | 171 bestanden |
| EMPTY2 | 13 bestanden |
| CTM-INTEGER | 112 bestanden |
| TRIPLE | 226 bestanden |
| ENCODING | 722 bestanden |
| Python | 2 Tests bestanden |
| NFC-Oracle | 16.294 Vergleiche bestanden |
| Diagnoseinventar | 124 Originale geprüft; ausschließlich begründete Name-Änderungen |
| Fehlerpfadkontrollen | 13 erwartete ASDF-Abbrüche korrekt berichtet |

Alle 33 bisherigen Originalergebnisse bleiben identisch. Die vier bekannten CTM-FAILs bleiben unverändert:

- `ctm/in/include-template.ctm`
- `ctm/in/include-wildcard2.ctm`
- `ctm/in/occurrence-datetime-timezone2.ctm`
- `ctm/in/occurrence-datetime2.ctm`

Die 48 reproduzierten Nicht-XTM-Stufenberichte sind nach ausschließlich der dokumentierten Name-Scope-Prüfnamensumstellung gleich zu Slice 21C. Alle 1546 historischen Reportdateien bleiben byteidentisch. Sämtliche 2006 gepinnten Korpusdateien sind in Größe und SHA-256 gegen den Lock geprüft; Quellen und Baselines sind unverändert. Alle 3778 geschützten Ausgangsdateien bleiben unverändert. Die einzige Produktionsänderung liegt im XTM-Reader.

Der registrierte Stand ist **XTM 43 PASS, 0 FAIL, 81 NOT-RUN**, entsprechend 36 positiven und sieben negativen PASS sowie 77 offenen positiven und vier offenen negativen Verträgen. Die vier negativen bleiben `reifier-collision.xtm`, `role-duplicate-reified.xtm`, `topicref-no-fragment-id.xtm` und `variant-missing-scope-duplicate.xtm`. NOT-RUN bezeichnet den registrierten Harness-Vertrag; diagnostische Leseproben erhöhen die PASS-Zahl nicht. CTM bleibt **262 PASS, 4 FAIL, 7 NOT-RUN**.

## Reproduktion und Abgrenzung

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate-slice-21d.py \
  --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  --output /private/tmp/topic-maps-21d-new-output
```

Der Outputpfad muss unbenutzt und außerhalb des Repositorys liegen. [execution.json](../reports/slice-21d/execution.json) hält tatsächliche Befehle, Zeitpunkte, Exitcodes und Prüfzahlen fest. [integrity.json](../reports/slice-21d/integrity.json) enthält die verifizierten Hashes. Die Shell-Aufrufe verwenden den regulär genehmigten Freigabeweg; für sämtliche Testprozesse gilt zusätzlich die explizite Netzwerk- und Repository-Schreibsperre. Keine Symlink- oder Sandbox-Konfigurationsänderung.

Keine Implementierung von XTM-Name-Scope, Variants, Name-Identifiern, Reification, Occurrences, expliziten Associations/Roles, XTM-mergeMap oder XTM 2.1. Keine Änderung an CTM-Grammatik, TMDM-Semantik oder CXTM-Normalisierung. Keine HyperDoc-/anderen Repository-Änderungen, Pushes oder Deployments. Nach Slice 21D wird gestoppt.
