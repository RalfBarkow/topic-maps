# Slice 21H — XTM Variant-Merge-Originalvertrag

## Ausgeführter Auftrag und Ausgangszustand

Branch: `codex/xtm-slice-21h`. Ausgangscommit und vorgesehener Parent:
`39c125bf9d462f538403aa633c56054511c210da`.
Vor Beginn waren Index und Arbeitsbaum sauber; der vorgefundene Branch war
`codex/xtm-slice-21g`. Der neue Branch setzt denselben Commit fort.
[initial-state.json](../reports/slice-21h/initial-state.json) enthält den
Ausgangszustand und die SHA-256-Werte aller damals versionierten Dateien.

Ein neuer Prozess ohne System-/Benutzerinitialisierung reproduzierte zunächst
1397 XTM-Prüfungen und den gespeicherten Stand **56 PASS, 0 FAIL, 68 NOT-RUN**.
Sein Report ist strukturell identisch mit dem Abschlussreport aus Slice 21G.
CTM startete unverändert bei **262 PASS, 4 FAIL, 7 NOT-RUN**.
Siehe [baseline.log](../reports/slice-21h/baseline.log) und
[baseline-xtm.json](../reports/slice-21h/baseline-xtm.json).

Die frühere Beobachtung aus
[Slice 21G](../reports/slice-21g/diagnostic-changes.json) ist historische Evidenz.
Sie wurde anhand der Originalbytes erneut reproduziert, bevor und nachdem die
Registrierung ergänzt wurde. Sie ersetzt keinen der neuen Ausführungsschritte.

## Unveränderter Originalvertrag

Einziger neu registrierter Case Record:
`xtm2/in/merge-itemid-with-variants.xtm`.

- [Originalquelle](../vendor/cxtm/xtm2/in/merge-itemid-with-variants.xtm): **641 Bytes**,
  SHA-256 `1712d72a0f3d908a259c539c13197af5e0d405a1572bbfd865aed8603b1edb45`.
- [Originalbaseline](../vendor/cxtm/xtm2/baseline/merge-itemid-with-variants.xtm.cxtm):
  **919 Bytes**, SHA-256
  `f157b2f40fa516c51dcc99cc7e151ed709d9ae3e29ba5c5c2bb5d9e9ef8a016a`.
- Document IRI:
  `https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/merge-itemid-with-variants.xtm`.
- Source Key: `xtm2/in/merge-itemid-with-variants.xtm`.

Die vollständigen Originalbytes als Hex und UTF-8-Text sowie das tatsächliche
Modell, beide Original-Reader-Zwischenstände und die vollständigen tatsächlichen
und erwarteten CXTM-Texte stehen in
[variant-merge-original.json](../reports/slice-21h/variant-merge-original.json).
Die Inventur mit historischer Ausgangsbeobachtung steht in
[candidate-inventory.json](../reports/slice-21h/candidate-inventory.json).

Beobachtet am tatsächlichen XML: Die zwei Topic-Elemente mit `id="topic"` und
`id="topic2"` besitzen beide den Item Identifier `http://example.org/#topic`.
Der erste Topic enthält den Name `Topic` mit Variant `TOPIC!`, der zweite den
Name `Topic 2` mit Variant `TOPIC2!`. Beide Name-Scopes sind leer. Beide expliziten
Variant-Scopes referenzieren `#theme`. Beide Werte sind textuelle `resourceData`
ohne ausdrücklichen Datentyp. Andere Sprachfähigkeiten werden nicht benötigt.

## Native Modell- und Identitätsnachweise

Die primäre Prüfung verarbeitet die unveränderten 641 Originalbytes über
`topic-maps.xtm:deserialize-octets` und den vorhandenen qualifizierten XML-Parser.
Sie erzeugt drei Topics, zwei verschiedene Names, zwei verschiedene Variants und
keine Associations. Die folgenden Aussagen sind ausgeführte Lisp-Assertions;
Objektgleichheit bedeutet dabei natives `EQ`, keine Gleichheit einer
nachgebildeten Identitätsstruktur.

1. `by-id("topic")`, `by-id("topic2")` und der kanonische Owner sind `EQ`.
   Seine Item-Identifier-Menge besteht genau aus `DocumentIRI#topic`,
   `DocumentIRI#topic2` und `http://example.org/#topic`. Er hat keine Subject
   Identifiers oder Subject Locators.
2. Der kanonische Theme-Topic besitzt genau `DocumentIRI#theme` als Item
   Identifier. Der Default-Name-Type besitzt genau den Subject Identifier
   `http://psi.topicmaps.org/iso13250/model/topic-name`. Weitere Identifier
   dieser Topics sowie Map-Item-Identifier fehlen. Die vorhandene globale
   Item-Identifier-Validierung besteht.
3. Beide Names bleiben verschieden. Ihre Parent-Topics sind `EQ` mit dem
   gemeinsamen kanonischen Owner, ihre Types mit dem Default-Name-Type.
   Beide haben leeren Scope und keine Item Identifier oder Reifier.
4. Die Variants bleiben verschieden und sind jeweils `EQ` mit ihrem aktuellen
   kanonischen Handle. `TOPIC!` gehört zu `Topic`, `TOPIC2!` zu `Topic 2`.
   Beide behalten den Datentyp
   `http://www.w3.org/2001/XMLSchema#string` und genau den kanonischen
   Theme-Topic im Scope. Variant-Parent und zugehöriger Name sind `EQ`.
   Es entstehen keine Variant-Item-Identifier oder Reifier.
5. Eine zusätzliche Handle-Spur liest denselben vollständigen qualifizierten
   Originalbaum mit den bestehenden Reader-Operationen Topic für Topic.
   Nach Topic 1 werden Owner-, Name-, Variant- und Theme-Handles festgehalten.
   Nach Topic 2 ist der alte rohe Owner-Handle vom neuen Owner verschieden;
   `canonical-topic(old-owner)` ist aber `EQ` mit dem gemeinsamen Owner.
   Der festgehaltene Name und Variant bleiben unmittelbar `EQ` mit den
   aktuellen Objekten, der Name-Parent wird auf den gemeinsamen Owner
   aktualisiert, Variant-Parent und Theme-Referenz bleiben kanonisch.
   Die beiden Zwischenstände sind im Originalreport enthalten. Das endgültige
   Modell und die CXTM-Bytes entsprechen denen der öffentlichen API.
6. Wiederholte CXTM-Kanonisierung ist deterministisch und verändert keinen
   nativen Modellzustand. Die Originaloctets bleiben erhalten. Derselbe
   Document IRI mit Source Key `independent:variant-merge-provenance` ergibt
   dasselbe vollständige Modell und dieselben CXTM-Bytes. Die aufgelösten
   Identitäten hängen damit vom Document IRI, nicht vom Source Key ab.

Die Handle-Spur ist eine zusätzliche Prüfung desselben Originals. Sie wird
nicht als weiterer Originalvertrag gezählt. Es wird keine Ersatzmap als
Originalvergleich registriert.

## Bytevergleich, Registrierung und Fehlerklassifikation

Tatsächlich erzeugte Ausgabe: **919 Bytes**. Originalbaseline: **919 Bytes**.
Der Vergleich sämtlicher Bytes ist erfolgreich, `firstDifferentByte` ist `null`.
Die [tatsächliche Ausgabe](../reports/slice-21h/actual/merge-itemid-with-variants.xtm.cxtm)
hat denselben oben angegebenen SHA-256-Wert wie die Baseline.
Die tatsächliche Condition ist `null`; entsprechend gibt es für diesen
positiven Vertrag keinen Fehlercode und keine Fehlerposition.

Der bestehende ASDF-Testlauf ruft `variant-merge-original-contract` aus
`run-tests` tatsächlich auf. Originalvergleich und native Modellprüfungen
verwenden den vorhandenen Case Record und dieselbe Ergebnisklassifikation wie
die bisherigen Verträge. Es gibt insgesamt genau 57 eindeutige Case Records:
49 positive CXTM-Verträge und acht nach Ursache qualifizierte negative
Verträge. Alle bisherigen 56 Case Records bleiben unverändert.

Der XTM-Lauf besteht mit **1414 eindeutigen Prüfungen**, davon **17 neue**.
Alle bisherigen 1397 Prüfungsnamen bleiben in ihrer bisherigen relativen
Reihenfolge erhalten. Neue Prüfungen sind in
[xtm.json](../reports/slice-21h/xtm.json) und
[xtm.log](../reports/slice-21h/xtm.log) nachvollziehbar.

35 isolierte Fehlerkontrollen prüfen die unveränderte Ergebnisklassifikation.
Die fünf Kontrollen des neuen Originals erzwingen Byteabweichung, XML-Fehler,
Unsupported, TMDM-Fehler und XTM-Syntaxfehler. Der ASDF-Test scheitert jeweils
wie erwartet mit Exit 1; keiner dieser Fälle zählt als positiver PASS und die
vorherigen 56 PASS bleiben erhalten. Die erwarteten Outcomes sind
`cxtm-mismatch`, `execution-error`, `unsupported`, `execution-error` und
`execution-error`. Die übrigen 30 Kontrollen bleiben erhalten. Einzelreports,
Logs und [failure-controls.json](../reports/slice-21h/failure-controls.json)
dokumentieren die tatsächlichen Klassifikationen. Dies sind Testinjektionen,
keine zusätzlichen ausgeführten Korpusverträge.

## Vollständige Offline-Abnahme

Die Abnahme lief in frischen **SBCL-2.5.4-Prozessen**, jeweils mit
`--no-sysinit --no-userinit`. Für Quellvorbereitung, Tests und Diagnose galt
zusätzlich die macOS-Sandboxregel:

```text
(version 1)(allow default)(deny network*)(deny file-write* (subpath "/Users/rgb/workspace/topic-maps"))
```

Die vorhandenen gepinnten lokalen Abhängigkeiten und vorhandenen XML-Patches
wurden geprüft und in temporären Verzeichnissen verwendet. Es gab keinen
Download, keinen Nix-Daemon-Aufruf, keinen vollständigen Nix-Neubau und keinen
Zugriff auf langlebige Lisp-Images. Der vollständige Nix-Neubau ist ausdrücklich
`NOT-RUN`; ausgeführt wurde die geforderte frische Offline-SBCL-Regression.

Die reguläre Freigabe über `require_escalated` war erfolgreich. Damit wurde
die nicht startfähige Standard-Sandbox wegen ihres symlinkbehafteten Writable
Root nicht verändert. Der zuvor beobachtete Startfehler lautet:
`writable root /Users/rgb/.nix-profile contains symlink component /Users/rgb/.nix-profile; symlinked writable roots are not supported.`
Weder `~/.nix-profile` noch die Sandbox-Konfiguration wurden geändert.

| Ausgeführter Bereich | Bestandene Prüfungen |
| --- | ---: |
| Bisherige Lisp-Regression einschließlich TMDM, CTM/CXTM, Include und Mergemap | 12100 |
| XTM-Originale, Identität, Names, Scopes, Item Identity, Variants und neuer Originalvertrag | 1414 |
| XML-Qualifikation | 146 |
| CTM/XTM-Mergemap | 217 |
| Slice 20A: registrierte Originale | 286 |
| Slice 20B: negative Originale | 25 |
| Slice 20C: Prolog | 171 |
| Slice 20E: empty2 | 13 |
| Slice 20F: CTM-Integer | 112 |
| Slice 20G: Triple Strings | 226 |
| Slice 20H: Encoding | 722 |
| Python-Unit-Tests | 2 |
| NFC-Oracle-Vergleiche | 16294 |
| Erwartet scheiternde Fehlerkontrollen | 35 |

Alle 48 übernommenen Nicht-XTM-JSON-Reports sind strukturell identisch mit
Slice 21G. Sämtliche 124 separaten Originaldiagnosen bleiben identisch;
[diagnostics.json](../reports/slice-21h/diagnostics.json) hält die leere
Änderungsliste fest. Diese Diagnoseaufrufe bewirken keine zusätzliche
Konformitätsregistrierung.

Tatsächlich registrierter Abschlussstand nach der Ausführung:

| Korpus | PASS | FAIL | NOT-RUN |
| --- | ---: | ---: | ---: |
| XTM | 57 | 0 | 67 |
| CTM | 262 | 4 | 7 |

Die vier bekannten CTM-Abweichungen bleiben unverändert:
`include-template.ctm`, `include-wildcard2.ctm`,
`occurrence-datetime-timezone2.ctm`, `occurrence-datetime2.ctm`.
Die XTM-NOT-RUN-Zahl setzt sich aus 64 positiven und drei negativen
unregistrierten Originalverträgen zusammen.

## Integrität, Umfang und Reproduktion

Die Größe und SHA-256 sämtlicher **2006 gepinnter Korpusdateien** entsprechen
`references/corpus-lock.json`. Alle **2013 historischen Reportdateien** sowie
alle **4259 geschützten Dateien** des Ausgangscommits bleiben unverändert.
Die Hashlisten stehen in [integrity.json](../reports/slice-21h/integrity.json).
Es gibt keine Produktionscodeänderung. Insbesondere bleiben TMDM, CTM, CXTM,
XML und der XTM-Reader byteidentisch zum Ausgangscommit.

Geändert wurden nur die vorhandenen XTM-Testdateien und die beschreibende
ASDF-Testsystem-Zeile. Hinzu kommen dieser Bericht, ein Abnahmeskript und neue
Slice-21H-Evidenz. Historische Reports werden ausschließlich gelesen.
Das Skript orchestriert die vorhandenen Tests, Case Records und Reports und
führt keine zweite Konformitätsprüfung ein.

Die vollständigen Befehle, Zeitpunkte, erwarteten und tatsächlichen Exitcodes
sowie die Abnahmeprüfungen stehen in
[execution.json](../reports/slice-21h/execution.json).
[precommit-audit.json](../reports/slice-21h/precommit-audit.json) und
[artifacts.json](../reports/slice-21h/artifacts.json) sichern den finalen
Änderungsumfang und die neuen Artefakte.

Reproduktion mit einem noch unbenutzten Ausgabeverzeichnis außerhalb des
Repositorys:

```sh
python3 scripts/validate-slice-21h.py   --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl   --output /private/tmp/topic-maps-21h-recheck
```

Nach erfolgreicher Abnahme werden Registrierung, Dokumentation und Evidenz
zusammen lokal committet. Slice 21H endet damit.
