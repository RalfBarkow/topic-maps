# Slice 21C: sieben negative XTM-Originalverträge

Nach tatsächlicher erneuter Ausführung: **XTM 33 PASS, 0 FAIL, 91 NOT-RUN**. CTM unverändert: **262 PASS, 4 FAIL, 7 NOT-RUN**. Produktionscode unverändert.

Ausgangscommit und Parent dieses Slices: `d498716b1e30ca1ef2b5c124038b372851ccb731`. Ausgangsbranch `codex/xtm-slice-21b`; Index und Arbeitsbaum waren sauber. Lieferbranch: `codex/xtm-slice-21c`. Testregistrierung und überprüfte Evidenz werden gemeinsam lokal committet; der Commit-Hash wird nach dem Commit ausgegeben.

## Normative Ursachen und tatsächlich beobachtete Conditions

Grundlagen sind die im Auftrag benannten Primärquellen [XTM 2.0](https://www.isotopicmaps.org/sam/sam-xtm/) und [TMDM](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/). Die Fundstellen je Original sind unten angegeben. XTM §5 trennt XML-Wohlgeformtheit, Schema-Konformität und fehlerfreie Deserialisierung ohne Modellverletzung. Die verwendete XML-Grenze ist nicht validierend: Wohlgeformtheit wird hier tatsächlich geprüft; daraus folgt keine vollständige Schema-Validierung.

Alle Dateien liegen unverändert unter `vendor/cxtm/xtm2/invalid/`. Jede Zeile ist nach spezifischer Ursachenprüfung **PASS**. Positionsangaben sind die vom vorhandenen Reader gelieferten ungefähren SAX-Zeilen/Spalten am Ende des Start-Tags, keine Byteoffsets.

| Originaldatei | Tatsächliche Quellstruktur | Normativer Ablehnungsgrund | Fundstelle | Tatsächliche Condition / Fehlercode | Position | Cause |
|---|---|---|---|---|---|---|
| `id-invalid.xtm` | `id="2topic"` | Die mit einer Ziffer beginnende ID verletzt den für topic/@id verlangten xsd:ID-/NCName-Vertrag. | XTM §4.5, Annex A | `XTM-REJECTION` / `invalid-id` | 2:22 | NIL / nicht exponiert |
| `itemid-collision.xtm` | `Map und Topic: http://example.org/#crash` | Zwei verschiedene Information Items dürfen keinen gleichen Item Identifier besitzen. Die Topic-Merge-Ausnahme gilt nicht für Map und Topic. | XTM §4.6; TMDM §5.1 | `OCCURRENCE-IDENTIFIER-ERROR` / `duplicate-item-identifier` | nicht exponiert | NIL / nicht exponiert |
| `no-version.xtm` | `topicMap ohne version` | Das erforderliche Versionsattribut fehlt. | XTM §4.4, Annex A | `XTM-REJECTION` / `missing-attribute` | 1:49 | NIL / nicht exponiert |
| `reifier-elem-in-2.0.xtm` | `topicMap/reifier/topicRef` | Ein reifier-Kindelement ist im XTM-2.0-Inhaltsmodell nicht vorgesehen; Reification verwendet dort ein Attribut. | XTM §§4.3.2,4.4, Annex A | `XTM-REJECTION` / `unexpected-element` | 2:12 | NIL / nicht exponiert |
| `subjid-ref-in-2.0.xtm` | `topic/instanceOf/subjectIdentifierRef` | instanceOf erlaubt topicRef-Kinder, keine subjectIdentifierRef-Kinder. | XTM §4.9, Annex A | `XTM-REJECTION` / `unexpected-element` | 4:65 | NIL / nicht exponiert |
| `subjloc-ref-in-2.0.xtm` | `topic/instanceOf/subjectLocatorRef` | instanceOf erlaubt topicRef-Kinder, keine subjectLocatorRef-Kinder. | XTM §4.9, Annex A | `XTM-REJECTION` / `unexpected-element` | 4:58 | NIL / nicht exponiert |
| `topic-no-id.xtm` | `topic ohne id, mit subjectIdentifier` | Ein Subject Identifier ersetzt das erforderliche XML-ID-Attribut nicht. | XTM §4.5, Annex A | `XTM-REJECTION` / `missing-id` | 2:10 | NIL / nicht exponiert |

Für alle sieben Originale ist `xmlWellFormed=true` und `intendedCauseReached=true`. Keine dieser Conditions ist `XTM-UNSUPPORTED` oder `XTM-XML-ERROR`. Die XTM-Conditions enthalten die korrekte Document IRI und den Source-Key. Die native TMDM-Condition enthält weder diese Felder noch eine Quellposition. Keine der sieben Original-Conditions besitzt einen Cause-Slot; `cause: null` dokumentiert dieses fehlende exponierte Feld und erfindet keine Kausalkette.

## Der Map-/Topic-Identifierkonflikt

Die Originalquelle enthält genau einen Item Identifier auf der Map und denselben auf dem einzigen Topic; keine Occurrence. Der vorhandene TMDM-Kompatibilitätspfad reicht die Verletzung als `OCCURRENCE-IDENTIFIER-ERROR` weiter. Der Klassenname ist unverändert. Der Code lautet `duplicate-item-identifier`, die tatsächliche Detaildiagnose `Locator already identifies a different information item.`. Das ist keine Meldung über eine Occurrence aus der Quelle.

Zwei tatsächlich deserialisierte Gegenproben ändern ausschließlich eine der beiden Identifier-Zeichenfolgen: einmal die der Map, einmal die des Topics. Beide werden akzeptiert. Die Tests prüfen per `EQ`, dass Map und Topic verschiedene Objekte sind, dass das Topic den richtigen Map-Parent hat und beide ihre exakten Identifier behalten. Names und Occurrences bleiben leer. Diese Gegenproben zählen nicht als Original-PASS. Die native Fehlerposition bleibt ausdrücklich NIL; es wird keine Position aus dem XML-Baum als Condition-Position ausgegeben.

## Originalbytes und Provenienz

| Originaldatei | Bytes | SHA-256 |
|---|---:|---|
| `id-invalid.xtm` | 108 | `13946473b901713300567dd3962474aaf72ac4f87b482ad7da1f92254bc89104` |
| `itemid-collision.xtm` | 211 | `b6ac27e6ba2699fd9904b9b6e66ffd9a7d390b9aa4bc80595ad9b8b64365f8f4` |
| `no-version.xtm` | 61 | `8eb0f23b5a3d2d035de5c34c46526a2b0c10a714c46b9853c9fc4496c648367f` |
| `reifier-elem-in-2.0.xtm` | 220 | `4603510ceeb992ea0b2ea4e57804aeca81a8efbe933efd0bb4c663109814bf5e` |
| `subjid-ref-in-2.0.xtm` | 207 | `046563a64f72b16842d3bd4d6c91e64802f898f353fd4936ea9bf8cf8e0bb033` |
| `subjloc-ref-in-2.0.xtm` | 200 | `f91ec8888adeb1f80bc06203f9f750202233e8a6c919d559741ed2793b4e382e` |
| `topic-no-id.xtm` | 155 | `7321a5abd569a87a4fb2e38d697e7ef044fdd90f3f41e23cd8a8ba4ab4aa9691` |

Die [maschinelle Originalevidenz](../reports/slice-21c/negative-originals.json) enthält den vollständigen Quelltext, die Originalbytes als Hex, Document IRI, Source-Key, Diagnose, Code, Position, Cause und Ergebnis je Fall. [candidate-inventory.json](../reports/slice-21c/candidate-inventory.json) und [observed-before-registration.json](../reports/slice-21c/observed-before-registration.json) halten die erneute Beobachtung vor jeder Registrierungsänderung fest. Der gespeicherte damalige Driver `before-registration.lisp` gehört zum damaligen Ausgangsstand; die aktuelle reproduzierbare Abnahme verwendet den unten genannten Validator.

## Bestehende Registrierung und gezielte Kontrollen

Das vorhandene ASDF-System `topic-maps/xtm/tests` lädt zusätzlich `tests/xtm-negative-originals.lisp`. Der vorhandene `run-tests`-Einstieg ruft die Gegenproben und die sieben Originale tatsächlich auf. Alle 33 Case IDs sind eindeutig. Die 26 positiven Case Records und ihre vollständigen Ist-/Baseline-Ausgaben sind identisch zu Slice 21B; alle 640 bisherigen benannten XTM-Prüfungen sind enthalten.

Der vorhandene Foundation-Harness besitzt den historischen Outcome-Token `ctm-rejection` für negative Verträge. Er wird wiederverwendet; in diesem Bericht bezeichnet er eine nachgewiesene XTM-/TMDM-Ablehnung. Es findet kein CTM-Parsing statt und keine zweite Ergebnisarchitektur wird eingeführt. Der eigenständige XTM-Prozess bestätigt weiterhin das Fehlen des CTM-Pakets.

Die Registrierung setzt PASS nur bei exakter nativer Condition-Klasse sowie passendem Code und konkreter Detaildiagnose. Für XTM werden zusätzlich Position und Kontext geprüft. Damit reicht insbesondere ein gleicher `unexpected-element`-Code an einem anderen Element nicht aus. Fehlende Ablehnung ergibt FAIL; eine beliebige oder XML-Condition ergibt FAIL; Unsupported bleibt Unsupported und lässt den ASDF-Test scheitern.

Sieben gültige Gegenproben prüfen gültige ID, vorhandene Version, vorhandene ID trotz SI, die beiden getrennten Map-/Topic-Identifier, zulässige Topic-Map-Kinder und ein zulässiges instanceOf/topicRef. Sechs Klassifizierungskontrollen prüfen Akzeptanz, beliebigen Fehler, XML-Fehler, Unsupported, falsche XTM-Ursache und denselben Code an einem anderen Element. Die ausführlichen Kontrollresultate und tatsächlichen Modelle stehen im [Harness-Bericht](../reports/slice-21c/xtm.json).

Vier zusätzliche frische Prozesse provozieren gezielt bei der ersten neuen Negativquelle Akzeptanz, XML-Fehler, Unsupported und eine falsche XTM-Ursache. Jeder ASDF-Lauf bricht mit dem erwarteten Exitcode 1 ab, sichert zuvor den richtigen Bericht und erhält die 26 positiven PASS. Die fünf bisherigen positiven Fehlerpfadkontrollen aus Slice 21B werden ebenfalls erneut ausgeführt. Diese neun erwarteten Abbrüche sind Kontrollergebnisse, keine gescheiterten Originalverträge. Siehe [failure-controls.json](../reports/slice-21c/failure-controls.json) und die einzelnen Kontrolllogs.

## Vollständige Offline-Regression

Alle Testprozesse laufen frisch mit SBCL 2.5.4, ohne Benutzer- oder Systeminitialisierung. Eine explizite macOS-Sandbox verweigert Netzwerk und Schreibzugriffe auf das Repository. Gepinnte lokale Store-Abhängigkeiten werden durch den bestehenden Verifier geprüft und mit den vorhandenen qualifizierten XML-Patches ausschließlich temporär vorbereitet. Es wurden keine Abhängigkeiten heruntergeladen und keine langlebigen Lisp-Images verändert.

| Prüfung | Tatsächliches Ergebnis |
|---|---:|
| Bestehende TMDM-/CTM-/CXTM-Suiten | 12.100 Prüfungen bestanden |
| XML-Qualifikation | 146 bestanden |
| XTM: alle bisherigen Tests, 26 positive und sieben negative Originale | 692 bestanden |
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
| Externe ASDF-Fehlerpfadkontrollen | neun erwartete Abbrüche; keine falsche PASS-Wertung |

Die vier CTM-FAILs bleiben unverändert:

- `ctm/in/include-template.ctm`
- `ctm/in/include-wildcard2.ctm`
- `ctm/in/occurrence-datetime-timezone2.ctm`
- `ctm/in/occurrence-datetime2.ctm`

## Vier ausgeschlossene negative Originale

Diese vier Originale werden in diesem Slice nicht ausgeführt oder registriert. Sie bleiben NOT-RUN:

- `xtm2/invalid/reifier-collision.xtm`
- `xtm2/invalid/role-duplicate-reified.xtm`
- `xtm2/invalid/topicref-no-fragment-id.xtm`
- `xtm2/invalid/variant-missing-scope-duplicate.xtm`

Die Korpusrechnung ist damit: 26 positive plus sieben spezifisch negative Original-PASS, 87 unregistrierte positive plus vier unregistrierte negative Originale. XTM ergibt **33 PASS, 0 FAIL, 91 NOT-RUN**. CTM bleibt **262 PASS, 4 FAIL, 7 NOT-RUN**.

Alle 2006 gepinnten Korpusdateien sind in Größe und SHA-256 gegen den Lock geprüft. Alle 1462 historischen Reportdateien bleiben byteidentisch. Alle 3694 geschützten Ausgangsdateien bleiben unverändert; sämtliche Produktionsdateien, Originalquellen und Baselines gehören dazu. Die 48 erneut erzeugten Nicht-XTM-Stufenberichte sind inhaltlich gleich zu Slice 21B. Historische Berichte und Validatoren behalten ihre bisherige Bedeutung.

## Reproduktion

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate-slice-21c.py \
  --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  --output /private/tmp/topic-maps-21c-new-output
```

Der Outputpfad muss unbenutzt und außerhalb des Repositorys liegen. [execution.json](../reports/slice-21c/execution.json) enthält tatsächliche Aufrufe, Zeitpunkte und Exitcodes; [integrity.json](../reports/slice-21c/integrity.json) enthält die geschützten Hashes. Die Shell-Aufrufe verwenden den regulär genehmigten Freigabeweg; für die Tests gilt zusätzlich die explizite Netzwerk- und Repository-Schreibsperre. Keine Änderung an Symlinks oder Sandbox-Konfiguration.

Nur Testregistrierung, Kontrollen, Dokumentation und Ausführungsevidenz werden geändert. Keine Produktions-, HyperDoc- oder anderen Repository-Änderungen, keine Pushes oder Deployments. Nach Slice 21C wird gestoppt.
