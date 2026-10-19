# Slice 21B: zwanzig positive XTM-Originalverträge

Beobachtete Abnahme: **XTM 26 PASS, 0 FAIL, 98 NOT-RUN**. CTM bleibt bei **262 PASS, 4 FAIL, 7 NOT-RUN**. Alle Zahlen stammen aus der erneuten tatsächlichen Ausführung; die Kandidatenevidenz aus Slice 21A dient ausschließlich der Auswahl.

Ausgangspunkt und Commit-Parent: `1a2808b2d123184b2494f93b19738a31fc27fd52`. Branch: `codex/xtm-slice-21b`. Ausgangsindex und Arbeitsbaum waren sauber. Dieser Bericht ist Teil des gemeinsamen lokalen Commits von Testregistrierung und Evidenz; sein Hash wird nach dem Commit geliefert.

## Ausführung im vorhandenen Harness

Unveränderte Original-Rohbytes werden durch `topic-maps.xtm:deserialize-octets` deserialisiert. Die Document IRI folgt unverändert der Konvention `https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/<Dateiname>`. Der Source-Key ist die relative Original-ID und beeinflusst nur die Provenienz. Für jeden neuen Originalvertrag bestätigt ein zweiter Reader-Aufruf mit anderem Source-Key identische Modellwerte und CXTM-Bytes.

Das vorhandene ASDF-System `topic-maps/xtm` führt über `topic-maps/xtm/tests` dieselbe erweiterte Funktion `original-contracts` in `tests/xtm-identity.lisp` aus. Die explizite Liste enthält genau zwanzig neue Kandidaten. Die sechs bisherigen Case Records und alle 327 bisherigen benannten Prüfungen sind erhalten. Jeder der 26 Originalverträge ist genau einmal registriert und liefert `cxtm-match`. Die vorhandene ASDF-Verdrahtung genügt; nur ihre Beschreibung wurde aktualisiert.

## Zwanzig erneut verglichene Originale

Alle Dateien liegen unter `vendor/cxtm/xtm2/in/`. Baseline ist jeweils `vendor/cxtm/xtm2/baseline/<Dateiname>.cxtm`. Beide Bytezahlen umfassen die vollständige Datei einschließlich vorhandener Zeilenenden. Kein erster abweichender Byteoffset, keine ausgelöste Condition. Jede Zeile ist PASS.

| Originaldatei | SHA-256 der Originalquelle | Quelle Bytes | CXTM Ist / Baseline Bytes | Vergleich |
|---|---|---:|---:|---|
| `itemid-duplicate.xtm` | `de03c886bc3559bfbbbba3efd99f737d21dd98274337a6e6d20249bd2be15ab4` | 141 | 114 / 114 | bytegleich, PASS |
| `itemid-fragment.xtm` | `8d91a15a7c8a5c409ef64ac089f9b713812e80f1899c0750aff8bb22cd16c183` | 142 | 141 / 141 | bytegleich, PASS |
| `itemid-relative.xtm` | `eb184bf6d43b30c4948c83939f712a6533ebf66e9051810eb1022de53ce917e9` | 160 | 159 / 159 | bytegleich, PASS |
| `itemid.xtm` | `aeb88fc3bb3f40f2621e330b114d81520160e8245018357d08956e3f3090f80b` | 160 | 159 / 159 | bytegleich, PASS |
| `merge-itemid-with-types.xtm` | `59e09290227949b321090efb2e18d51d4c3989ffbfef043183ffe3eb3a7c1ffc` | 394 | 1478 / 1478 | bytegleich, PASS |
| `merge-itemid.xtm` | `365c9ef953b195cdc54cef6e5ce75959530212f7e3f458c2b3597c951e232937` | 246 | 186 / 186 | bytegleich, PASS |
| `merge-subjid.xtm` | `c5626addd6c81aef44b1ac30d4dafa4bbe7402d36020ace2b6c770c403b3f41a` | 256 | 229 / 229 | bytegleich, PASS |
| `merge-subjloc.xtm` | `e7d9f6f200c3f8dfff1e7b0b62a26ed2d51f53c99925a774f684ff1e7056f7d8` | 250 | 223 / 223 | bytegleich, PASS |
| `subjid-duplicate.xtm` | `ede80c9c329997c17c4422bdd02cd60a2c9bae6ebc88905d47e18f8f40df5272` | 191 | 186 / 186 | bytegleich, PASS |
| `subjid-escaping.xtm` | `88d6dd1eb9853a8dd64f471fa73d8cb83ea93e9f23ac204b0afce009c7924cde` | 177 | 214 / 214 | bytegleich, PASS |
| `subjid-escaping2.xtm` | `c1501dfceb8bc8b3f5bced3a8014e2ad0fb07a24b2481d97bacbb5c87305f52c` | 179 | 214 / 214 | bytegleich, PASS |
| `subjid-fragment.xtm` | `0494cfd57abc7c74b0540f16126f7e3f263bfc02c633071aa715dadd317cd455` | 184 | 183 / 183 | bytegleich, PASS |
| `subjid-relative.xtm` | `a4382629022bb3622bf8de49aebf4f8cc2b1322a407e60ec5941eecd95a7f670` | 149 | 186 / 186 | bytegleich, PASS |
| `subjid-sameas-itemid.xtm` | `906f9b41356fb1f836ad4b357383b9831cc0ac79c5cae2c65b8c1f8d1b4b8cd7` | 222 | 251 / 251 | bytegleich, PASS |
| `subjid.xtm` | `eb5180db0f6e4b6607cb77c8bdd07008f4ff623a397f05a9ed68089232ea5c05` | 165 | 202 / 202 | bytegleich, PASS |
| `subjloc-duplicate.xtm` | `b29fb45c977c6fdb5cb5a74d4551c2ba19537d837aee57f28fb7e75319eaf19c` | 185 | 180 / 180 | bytegleich, PASS |
| `subjloc-fragment.xtm` | `dfdd314cf01305e089d28952256319752224a65f80a50dc3805241e8766ec3fc` | 143 | 177 / 177 | bytegleich, PASS |
| `subjloc-multiple.xtm` | `590e9c591f1ad7d076fd165a00ee7123911026794a014df3bc1538e3502b4aea` | 219 | 243 / 243 | bytegleich, PASS |
| `subjloc-relative.xtm` | `431f4fbba958ef4d94b7ff6e0caea6dae25b4c029c47eda3e0e5cbc5166c00be` | 146 | 180 / 180 | bytegleich, PASS |
| `subjloc.xtm` | `c6b8ce542fbe8b3250780c5100f56c439dc64b276de257694f1e0a7a05d88786` | 162 | 196 / 196 | bytegleich, PASS |

Die maschinenlesbare [Vergleichsevidenz](../reports/slice-21b/comparisons.json) dokumentiert alle 26 tatsächlichen Vergleiche, ihre Längen/Hashes und das beobachtete TMDM-Modell; der [Harness-Bericht](../reports/slice-21b/xtm.json) enthält vollständige Ist-/Baseline-Texte sowie Checknamen und Case Records. Die tatsächlichen Bytes liegen unter [actual](../reports/slice-21b/actual/). Die [Kandidatenprovenienz](../reports/slice-21b/candidate-inventory.json) wird bewusst getrennt von den neuen Ergebnissen geführt.

## Tatsächlich geprüfte Identitätsbeziehungen

- Alle zwanzig neuen Maps: exakte Mengen von Topic Item Identifiers, Subject Identifiers und Subject Locators; Auflösung relativer und fragmentärer Locators; Deduplikation ohne zusätzliche Identifikatoren. Prozentkodierung eines Leerzeichens und ein unverändertes Pluszeichen werden getrennt geprüft.
- Die vier Merge-Originale: `by-id(topic) EQ by-id(topic2)`; Erhaltung beider ursprünglicher Dokument-Item-Identifier und des gemeinsamen II, SI oder SL. Das ist eine Prüfung an den vom Reader erzeugten Maps.
- `merge-itemid-with-types.xtm`: sechs Topics, zwei Type-Instance-Associations und vier Rollen. Beide Forward-Reference-Topics sind kanonisch; die beiden Associations behalten den zusammengeführten Player, die richtigen Core Subjects sowie kanonische Parent- und inverse RolesPlayed-Referenzen. Core Subjects erhalten keine zusätzlichen Item Identifier.
- Alle 26 Maps: kanonische Topics/Associations/Rollen per `EQ`, korrekte Map-/Association-Parents, lebende Type-/Player-Referenzen und übereinstimmende inverse Rollenverweise. CXTM verändert den Mapzustand weder beim ersten noch beim wiederholten Aufruf; beide Ausgaben sind identisch. Die Quelloktette bleiben unverändert.
- Die bestehenden zusätzlichen Semantiktests prüfen beibehaltene Forward Handles vor/nach dem Merge, SI-/II-Auflösung ohne unberechtigtes II-Hinzufügen und Kaskaden mit umgeleiteten Rollen. Diese lokalen Gegenproben zählen nicht als zusätzliche Originalverträge.

## Fehlende Vergleiche ergeben kein PASS

Die vorhandene Ergebnisregistrierung klassifiziert einen tatsächlich abweichenden CXTM-Vektor als `cxtm-mismatch / FAIL`. XML-, XTM- und TMDM-Conditions ergeben `execution-error / FAIL`; fehlende Sprachunterstützung bleibt `unsupported`. Der ASDF-Test schlägt jeweils fehl und sichert zuvor den Harness-Bericht. Fünf gesonderte frische Prozesse belegen diesen gesamten Fehlerpfad durch gezielte Fault Injection. Ihre erwarteten Exitcodes 1 sind Abnahmeergebnisse der Kontrollen, keine Fehlschläge von Originalvergleichen und keine neu registrierten negativen Originalverträge. Siehe [Kontrollen](../reports/slice-21b/failure-controls.json) und `control-*.json/log`.

## Vollständige Offline-Regression

Alle Testprozesse laufen frisch in SBCL 2.5.4 mit `--no-sysinit --no-userinit`. Die explizite macOS-Sandbox sperrt Netzwerk und Schreibzugriff auf das Repository. Gepinnte lokale Nix-Store-Abhängigkeiten werden geprüft und mit den vorhandenen qualifizierten XML-Patches ausschließlich temporär vorbereitet. Keine Downloads und kein langlebiges Lisp-Image. Die eigenständige XTM-Ausführung bestätigt weiterhin, dass kein CTM-Paket geladen wurde.

| Prüfung | Beobachtetes Ergebnis |
|---|---:|
| Bestehende TMDM-/CTM-/CXTM-Suiten | 12.100 Prüfungen bestanden |
| XML-Qualifikation | 146 bestanden |
| XTM einschließlich 26 Originalen | 640 bestanden; alle 327 bisherigen Prüfungen enthalten |
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
| Fehlerpfadkontrollen | fünf erwartete ASDF-Abbrüche samt korrekter Berichtsklassifikation |

Die vier historischen CTM-Abweichungen sind unverändert:

- `ctm/in/include-template.ctm`
- `ctm/in/include-wildcard2.ctm`
- `ctm/in/occurrence-datetime-timezone2.ctm`
- `ctm/in/occurrence-datetime2.ctm`

Alle 48 reproduzierten Nicht-XTM-Stufenberichte sind inhaltlich gleich zu Slice 20J. Alle 1361 bisherigen Reportdateien bleiben byteidentisch. Geprüft wurden sämtliche 2006 gepinnten Korpusdateien und 3591 geschützten Ausgangsdateien. Änderungen an bisherigen Dateien beschränken sich auf den XTM-Testharness und eine ASDF-Beschreibung. Sämtliche Produktionsdateien, Originalquellen und Baselines sind unverändert.

## Reproduktion und Grenzen

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate-slice-21b.py \
  --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  --output /private/tmp/topic-maps-21b-new-output
```

Der Outputpfad muss unbenutzt und außerhalb des Repositorys liegen. [execution.json](../reports/slice-21b/execution.json) dokumentiert Zeitpunkte, tatsächliche Aufrufe und Exitcodes; [integrity.json](../reports/slice-21b/integrity.json) dokumentiert SHA-256-Werte. Die sechs ursprünglichen Case Records bleiben in [baseline-xtm.json](../reports/slice-21b/baseline-xtm.json) nachvollziehbar. Historische Validatoren behalten ihre historischen Abnahmeannahmen; die neue Gesamtabnahme erfolgt über `validate-slice-21b.py`.

Der verwaltete Sandbox-Start scheiterte vor der Ausführung am konfigurierten Symlink: `writable root /Users/rgb/.nix-profile contains symlink component /Users/rgb/.nix-profile; symlinked writable roots are not supported.` Der reguläre Freigabeweg wurde genehmigt; die Testprozesse erhielten anschließend die oben genannte explizite Sandbox mit kanonischem SBCL-Pfad. Kein automatischer Freigabeentscheid wurde umgangen, kein Symlink und keine Sandbox-Konfiguration geändert. [initial-state.json](../reports/slice-21b/initial-state.json) hält den Fehler und den Ausgangszustand fest.

Keine neue XTM-Sprachoperation, kein Name-/Variant-/Occurrence-/Association-/Reification-/mergeMap-Ausbau, keine Änderung an CTM/TMDM/CXTM/XML. Alle elf negativen XTM-Originalverträge bleiben unregistriert. Die verbleibenden 87 positiven und elf negativen Originale ergeben 98 NOT-RUN. Der direkte Helper-Test zählt weiterhin gesondert. Keine HyperDoc-Änderungen, Pushes oder Deployments. Slice 21B endet hier.
