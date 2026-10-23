# Slice 22O — Qualifizierte XTM-Korpus-Disposition

Stand: 23. Oktober 2026. Ausgangscommit und vorgesehener Commit-Parent:
`2b6d6f4c7ccc351871a33beeba4bc9f34971617e` (abgeschlossener Slice 22N).
Ausgangsbranch `codex/xtm-slice-22n`, Dokumentationsbranch
`codex/xtm-slice-22o`. Index und Arbeitsbaum waren vor Beginn sauber.

Dieser Slice entscheidet die fachliche Behandlung der drei offenen XTM-Originale
innerhalb der unten ausgewiesenen Quellenbasis. Er ändert ausschließlich diesen
Bericht. Produktionscode, Tests, Case Records, Statusdefinitionen, Originale,
Baselines und historische Berichte bleiben unverändert. Kein neuer PASS,
kein neuer Reader-Lauf und keine neue Regression werden behauptet.

## Beurteilungsmaßstäbe und Herkunft

| Begriff | Bedeutung in diesem Bericht |
|---|---|
| Normative Konformität | Erfüllung einer konkret belegten Anforderung der vereinbarten Normedition; Umfang und Editionsgrenze werden genannt. |
| Historischer Originalvertrag | Unveränderte Eingabe und verlangte Ausgabe beziehungsweise Ablehnung des gepinnten Korpus. |
| Beobachtete Implementierung | Tatsächliches Ergebnis einer identifizierten gespeicherten Ausführung und zugehöriger aktueller Quellstand. |
| Disposition | Fachliche Entscheidung über Übereinstimmung, Korpuskonflikt oder fehlende Entscheidungsgrundlage; kein neuer Harness-Status. |
| Offene Frage | Noch fehlender Beleg, Editionsabgleich oder ausdrücklich erforderliche Abnahmeentscheidung. |

**Jetzt gelesen/geprüft:** Git-Zustand, Quellen, Originalbytes, Baselines und
Hashes der bestehenden Evidenz. **Gespeichert beobachtet:** Reader-, Modell-
und CXTM-Ergebnisse aus Slice 22N. **Normativ abgeleitet:** Folgerungen aus den
benannten Klauseln innerhalb ihrer Editionsgrenzen, übernommen aus der
vorangegangenen Untersuchung und den vorhandenen Berichten. **Bedingte
Modellfolgerung:** ein denkbarer endlicher Zyklusabschluss. Dieser ist weder
beobachtetes Reader-Ergebnis noch nachgewiesene Normpflicht.

Dispositionen benennen keine zusätzlichen PASS/FAIL/NOT-RUN/UNSUPPORTED-Werte.
Insbesondere sind die Abnahmetore A/B/C aus 22A und die historischen
Entscheidungskategorien A/B/C aus 22C unterschiedliche Bezeichnungen.
Dieser Bericht schreibt keine dieser historischen Entscheidungen rückwirkend um.

## Quellenbasis und Editionsgrenzen

- XTM: ISO/IEC 13250-3:2007, insbesondere §§4.2, 4.5, 4.6, 4.21 und 5,
  [öffentlicher Referenztext vom 2006-06-19](https://www.isotopicmaps.org/sam/sam-xtm/).
- TMDM: ISO/IEC 13250-2:2006, §§5.1, 5.2, 5.3.5, 5.6 und 6.1–6.5,
  [Referenztext vom 2006-06-18](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/).
- XML: [XML 1.0 Third Edition, §3.3.1](https://www.w3.org/TR/2004/REC-xml-20040204/#sec-attribute-types).
  Keine stillschweigende Umstellung auf eine spätere XML-Ausgabe.
- CXTM: ISO/IEC 13250-4:2009, bestehende Kanonisierung; dieser Slice ändert
  weder das Verfahren noch den historischen Vergleichsvertrag.
- [22A-Abschlussplan](slice-22a-conformance-closure.md), insbesondere
  „Evidenz und Normeditionen“, „Profil 1“ und „Drei getrennte Abnahmetore“;
  [22C-Entscheidungen](slice-22c-normative-decisions.md), insbesondere
  „XTM-mergeMap: Modellregel und Verfahrenswahl“ und Q-XTM-LOOP;
  [22E-Importbefund](slice-22e-xtm-mergemap.md) sowie
  [22N-Abschlussbericht](slice-22n-xtm-role-reification.md).

XTM- und TMDM-Referenztexte erklären ihre Publikationsgleichheit. Ein davon
unabhängiger Klauselabgleich gegen die offiziellen ISO-Ausgaben und relevante
Berichtigungen steht weiterhin aus. Die korrigierte TMDM-Fassung von 2008
ersetzt die vereinbarte Ausgabe 2006 nicht automatisch. Die in 22C benannten
CTM-/CXTM-Editionslücken und Q-ERRATA bleiben offen. Es wurden in 22O keine
Normdateien beschafft oder heruntergeladen und keine neue Primärquellenprüfung
als unabhängig abgeschlossene ISO-Verifikation ausgegeben.

Der Korpus ist auf `cd165b150176c1d6842b37be9cc9051b40d4996b` gepinnt.
Die [Korpus-README](../vendor/cxtm/README) fordert für positive Originale
vollständige Bytegleichheit und für negative Originale Ablehnung. Ihre Aussage
über die Richtigkeit der Sammlung und ein möglicher Ontopia-Vergleich sind
kein unabhängiger Normnachweis.

Für die gespeicherten Originaldiagnosen gilt die Document-IRI-Konvention:
`https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/`
plus vollständiger Case-ID. Root-IRI bezeichnet die so gebildete IRI der
jeweiligen `.xtm`-Datei, Kind-IRI die gegen diese aufgelöste `.sub`-Ressource.
Die Case-ID als Source Key bleibt davon unabhängig.

## Entscheidungsdatensatz 22O-XML-ID

**Original / historischer Vertrag:**
[`xtm2/in/occurrence-duplicate-iid2.xtm`](../vendor/cxtm/xtm2/in/occurrence-duplicate-iid2.xtm)
(543 Bytes) ist historisch positiv. Die
[443-Byte-Baseline](../vendor/cxtm/xtm2/baseline/occurrence-duplicate-iid2.xtm.cxtm)
enthält zwei Topics, eine Occurrence, deren Type `#occtype`, leeren Scope,
Value `Testing resource data.`, Datatype `xsd:string` und II `#the-occurrence`.

**Tatsächliche Quelle:** Zwei `topic`-Elemente tragen jeweils `id="topic"`
(Zeilen 2 und 11). Ihre Occurrences tragen beide
`itemIdentity href="#the-occurrence"` (Zeilen 4 und 13). Die wiederholten
`topicRef href="#occtype"` sind Referenzen, keine weiteren XML-ID-Deklarationen.

**Normative Konformität:** XTM §4.5 verlangt einen dokumentweit eindeutigen
Topic-Identifier und deklariert ihn als `xsd:ID`; §5 verlangt die Ablehnung
nichtkonformer XTM-Eingaben. Die Datei kann trotzdem XML-wohlgeformt sein:
Ohne DTD ist `id` für den XML-Parser nicht bereits allein wegen seines Namens
ein deklariertes ID-Attribut. XML-Wohlgeformtheit und XTM-/Schema-Gültigkeit
sind getrennte Anforderungen.

**TMDM-Abgrenzung:** Dokumentlokale ID-Deklarationen sind keine allgemeine
TMDM-Identifier-Regel. Gemeinsame Topic-II begründen gemäß TMDM §§5.3.5 und
6.2 Topic-Merging; gleiche Occurrences werden nach §§5.6 und 6.5 anhand
Parent, Type, Scope, Value und Datatype normalisiert und ihre II vereinigt.
Gleiche Occurrence-II allein erlauben kein Merging fachlich verschiedener
Occurrences (§5.1). Das erwartete Modell wäre nach Übergehen der doppelten
Dokument-ID nachvollziehbar; die Modellregel legitimiert dieses Übergehen nicht.

**Beobachtete Implementierung:** Der gespeicherte 22N-Originaldiagnoselauf
liefert `XTM-REJECTION`, Code `duplicate-id`, Detail
`Duplicate XML ID in this document.`, ungefähr SAX-Zeile/Spalte **11:21**,
Cause `null`. Document IRI ist die oben erklärte Original-IRI, Source Key die
Case-ID. [Diagnose](../reports/slice-22n/after/all-124-original-statuses.json),
[Quellprüfung](../src/xtm/reader.lisp),
[vorhandene Kontrolle](../tests/xtm-item-identities.lisp).
Die zusätzliche gespeicherte Hilfskontrolle verwendet `example.xtm` als Document
IRI; das wird nicht mit dem Originaldiagnoselauf verwechselt. `validate-source`
prüft Dokument-ID-Eindeutigkeit vor der Befüllung der Map.

**Disposition:** Beabsichtigte, fachlich korrekte Zurückweisung innerhalb der
geprüften Normbasis; der historische positive Vertrag ist normativ widersprüchlich.
Keine Reader-/XML-/TMDM-Änderung und keine Lockerung der Dokument-ID-Prüfung.
**Registrierter Status bleibt NOT-RUN**, obwohl die Ablehnung bereits beobachtet
ist: Der bestehende positive Originalvertrag wurde nicht erfüllt und wird nicht
still in einen negativen PASS umgedeutet.

**Offene Frage / Konsequenz:** Der unabhängige ISO-Abgleich bleibt bestehen.
Ein späterer qualifizierter Testsuite-Abschluss muss den Korpuskonflikt ausdrücklich
als Ausnahme behandeln oder einen gesonderten negativen Abnahmevertrag vereinbaren.
Das ist kein Auftrag, Case Records oder Originale zu verändern.

## Entscheidungsdatensatz 22O-MAP-II

**Original / historischer Vertrag:**
[`mergemap-itemid.xtm`](../vendor/cxtm/xtm2/in/mergemap-itemid.xtm)
(148 Bytes) importiert
[`mergemap-itemid.sub`](../vendor/cxtm/xtm2/in/mergemap-itemid.sub)
(151 Bytes). Die Rootmap hat keine Map-II, die Kindmap
`itemIdentity href="#the-topic-map"`. Beide Dokumente definieren einen Topic
`id="topic"`. Die [314-Byte-Baseline](../vendor/cxtm/xtm2/baseline/mergemap-itemid.xtm.cxtm)
erwartet zusätzlich den Kind-Map-II auf der Zielmap.

**Normative Konformität:** XTM §4.21 benennt Topics und Associations der Kindmap
als Importinhalt. TMDM §5.2 unterscheidet diese Mengen von Map-II und Map-Reifier;
§6.2 beschreibt Topic-Merging und begründet keine Vereinigung der Map-Items.
Eine zusätzliche Übertragung des Kind-Map-II folgt aus diesen Klauseln nicht.

**Beobachtete Implementierung mit explizitem Resolver:** Zwei unterschiedliche
Topics mit II `Root-IRI#topic` und `Kind-IRI#topic`, keine SI/SL, Names, Variants,
Occurrences oder Associations. Die Zielmap hat keine Map-II und keinen Reifier;
die Quellmap behält `Kind-IRI#the-topic-map` und bleibt unverändert. Die
kanonischen nativen Referenzen sind im gespeicherten Modell geprüft.
Der [bestehende Importvertrag](../src/tmdm/import.lisp) kopiert Inhalte,
vereinigt dabei nach TMDM und überträgt keine Root-Metadaten.

Die Resolverargumente der vorhandenen Originalkontrolle sind:
`(Kind-IRI :purpose :mergemap :from-document-iri Root-IRI
:notation "http://psi.topicmaps.org/iso13250/xtm")`.
Kind-IRI entsteht aus `mergemap-itemid.sub` relativ zur Root-Document-IRI;
Source Key ist ausschließlich diagnostisch. Die Kindbytes gehen durch einen
eigenen qualifizierten XML-/XTM-Kontext.

**Vollständige Byteabweichung:** Die gespeicherte tatsächliche CXTM-Ausgabe hat
**224 Bytes**, die unveränderte Baseline **314 Bytes**. Condition ist `null`;
erste Differenz ist der **nullbasierte Byteindex 12**. Nur die Baseline enthält
diesen exakt 90 Byte langen UTF-8-/LF-Block unmittelbar nach `<topicMap>`:

```xml
<itemIdentifiers>
<locator>mergemap-itemid.sub#the-topic-map</locator>
</itemIdentifiers>
```

Der abschließende LF gehört zu den 90 Bytes. In 22O wurde anhand der gespeicherten
vollständigen Ist-Ausgabe erneut lesend geprüft: Baseline enthält diesen Block
genau einmal; ausschließlich dessen Entfernung aus einer temporären
Vergleichszeichenfolge ergibt bytegenau die 224 Ist-Bytes. Keine Datei und keine
Map wurde dafür verändert. Ist-SHA-256:
`ddbdfd9384267ec8d71fc5e56218c3b3b6680efdc232830c904c9aa3f52ec62a`.

[Gespeicherte Modelle, Resolverbeobachtungen und vollständige Ausgaben](../reports/slice-22n/after/xtm.json),
Feld `mergemapOriginalObservations`;
[vorhandene Originalkontrolle](../tests/xtm-mergemap.lisp).
Die getrennte generische Diagnose ohne Resolver erreicht
`XTM-UNSUPPORTED/resource-resolver-required` bei ungefähr **2:41**. Sie ist
kein Nachweis eines fehlgeschlagenen Inhaltsimports mit Resolver und ersetzt
dessen erfolgreiche gespeicherte Ausführung nicht.

**Disposition:** Normgerecht begründeter Inhaltsimport bei abweichender
historischer Map-II-Erwartung, innerhalb der benannten Editionsgrenze.
Keine zusätzliche Map-Metadatenübertragung und keine Baselineanpassung.
**Registrierter Status bleibt NOT-RUN**; weder der erfolgreiche Inhaltsimport
noch die dokumentierte Korpusabweichung erzeugt einen Original-PASS.
Die historische 22C-A-Entscheidung beschrieb den damals fehlenden Inhaltsimport;
diese Fähigkeit wurde in 22E umgesetzt. Der alte Bericht bleibt unverändert.

**Offene Frage / Konsequenz:** Publikations-/Errata-Abgleich und ausdrücklicher
qualifizierter Ausnahmeentscheid für die historische Baseline bleiben Teil der
Gesamtabnahme. Es folgt keine gerechtfertigte Produktionsänderung allein aus
Wünschen nach 314 statt 224 Bytes.

## Entscheidungsdatensatz 22O-LOOP

**Original / historischer Vertrag:**
[`mergemap-loop.xtm`](../vendor/cxtm/xtm2/in/mergemap-loop.xtm) und
[`mergemap-loop.sub`](../vendor/cxtm/xtm2/in/mergemap-loop.sub)
(jeweils 150 Bytes) importieren einander:

```text
mergemap-loop.xtm → mergemap-loop.sub → mergemap-loop.xtm
```

In beiden Dateien folgt der lokale Topic `id="topic"` erst nach `mergeMap`.
Die [222-Byte-Baseline](../vendor/cxtm/xtm2/baseline/mergemap-loop.xtm.cxtm)
enthält zwei dokumentqualifizierte Topics und keine Map-II. Das sind verschiedene
Dokumentidentitäten, kein doppeltes XML-ID innerhalb eines Dokuments.

**Beobachtete Implementierung mit explizitem Resolver:** Ein Abruf der
Kindressource. Vor einem erneuten Abruf der Root-IRI erkennt der Reader die
bereits aktive IRI und signalisiert `XTM-UNSUPPORTED`, Code `cyclic-mergemap`,
Detail `Active recursive XTM resource dependency; cycle processing is not implemented.`.
Kontext ist das Kinddokument mit dessen Source Key, ungefähre SAX-Position
**2:39**, Cause `null`. Kein vollständiges Ergebnis-Modell oder Ist-CXTM wird
zurückgegeben. [Aktiver Pfad und Resolver](../src/xtm/reader.lisp),
[gespeicherte Originalbeobachtung](../reports/slice-22n/after/xtm.json),
Feld `mergemapOriginalObservations`.
Ohne Resolver endet die generische Diagnose bereits im Root mit
`resource-resolver-required` bei ungefähr **2:39**; die beiden Ursachen sind
nicht austauschbar.

**Normative Konformität / offene Frage Q-XTM-LOOP:** XTM §§4.2 und 4.21
beschreiben dokumentgeordnete rekursive Deserialisierung, aber keinen
festgelegten Zyklusabschluss. §5 liefert ebenfalls keine ausdrückliche
Zyklusregel. Weder eine konkrete endliche Strategie noch die normative
Ungültigkeit zyklischer Ressourcen wird hier als bewiesen ausgegeben.
Ein endlicher minimaler Inhaltsabschluss mit beiden Topics ist eine bedingte
Modellfolgerung; er ist keine ausreichend belegte Auslegung der rekursiven
Verfahrensvorschrift. TMDM-Merging beendet nicht selbst die Reader-Rekursion.
Die Aussage, allein ein Cache müsse implementiert werden, wäre deshalb zu stark.

**Disposition:** Offene normative Frage und ehrlich ausgewiesene
Implementierungsgrenze. Die Schutzprüfung verhindert unkontrollierte Rekursion;
sie ist keine normative Ablehnung als ungültig, kein negativer Original-PASS und
keine bereits abgenommene Zyklussemantik. **Registrierter Status bleibt NOT-RUN.**

**Fehlender Beleg / Konsequenz:** Maßgebliche ISO-Klauseln und gegebenenfalls
anwendbare autoritative Klarstellung zu wiederholter Dokument-IRI prüfen.
Falls diese keinen eindeutigen Abschluss bestimmen, ist vor einer Implementierung
eine ausdrückliche Modell-/Verfahrensabnahme notwendig. Insbesondere müssen
lokale Inhalte nach Rückkanten vollständig erfasst werden; ein übersprungener
aktiver Import allein belegt das nicht. Keine Strategie, Cache-Verwaltung,
zusätzliche Ressourcengrenze oder Implementation wird mit diesem Slice beauftragt.

## Originalintegrität und gespeicherte Ausführungsevidenz

Alle Pfade der Tabelle sind relativ zu `vendor/cxtm/`.

| Datei | Bytes | SHA-256 |
|---|---:|---|
| `xtm2/in/occurrence-duplicate-iid2.xtm` | 543 | `6745fa2eaaf2e1ecca9e13ecee53af7774b26c96d9cfb41ca820a5cbc03a79e1` |
| `xtm2/baseline/occurrence-duplicate-iid2.xtm.cxtm` | 443 | `9ec57587c2cdc00eff715ad80b3a8be1313c1778d152d29834f02b7270741479` |
| `xtm2/in/mergemap-itemid.xtm` | 148 | `23de617d6e201374ec3f9c12e02be88bc555dd7dbcd262e854c8e9a3f96966d1` |
| `xtm2/in/mergemap-itemid.sub` | 151 | `20cfc5dafa42543648b9f3ee4f41434f56f7fe7679afb0f4a1c870bde2415c01` |
| `xtm2/baseline/mergemap-itemid.xtm.cxtm` | 314 | `03c5c1694e572674c0982f3b01d8c2fb323159ba6436857924814ea1e7a2d5d7` |
| `xtm2/in/mergemap-loop.xtm` | 150 | `033f5191ccfa3af9382a9cc6c47720f9b63b990f9485f10c3d2ac8d113b1cedb` |
| `xtm2/in/mergemap-loop.sub` | 150 | `94e4a9ac5ea85c2f5025cf8feff5e8eb62f5981795b0d19a8a64af1b2f69835c` |
| `xtm2/baseline/mergemap-loop.xtm.cxtm` | 222 | `f0f56a0e2cf22ba274b6f10ef20cd128841908ed0f3e10de3b67b218c394fc6f` |

Die gespeicherte vollständige 22N-Ausführung lief vom
**2026-10-23T19:16:53.046559+00:00** bis
**2026-10-23T19:20:33.892127+00:00** mit SBCL 2.5.4 und Netzwerksperre.
[execution.json](../reports/slice-22n/after/execution.json),
[runs.json](../reports/slice-22n/after/runs.json),
[124 Originaldiagnosen und registrierte Status](../reports/slice-22n/after/all-124-original-statuses.json),
[Integrität](../reports/slice-22n/after/integrity.json) und
[22N-Inhaltsmanifest](../reports/slice-22n/completion-audit.json)
bleiben unverändert.

In 22O wurden die SHA-256 von **323 im 22N-Inhaltsmanifest erfassten Artefakten**
und **10324 geschützten Ausgangsdateien** erneut mit deren aktuellen Bytes
verglichen. Darin bleiben alle **2006 gepinnten Korpusdateien** und **8026 vor
22N vorhandenen historischen Reportdateien** unverändert; die neuen 22N-Reports
sind separat über die 323 Artefakte gebunden. Die gespeicherte Ist-CXTM wurde
mit der Originalbaseline wie oben beschrieben verglichen. Das sind neue
Lese-/Integritätsprüfungen bestehender Evidenz, keine neue Lisp-, ASDF-,
Python-Test- oder NFC-Ausführung. Die damaligen Testzahlen bleiben historische
Ausführungsergebnisse. Für 22O wird keine Regression als neu ausgeführt ausgegeben.

## Registrierter Stand und Abnahmetore

| Korpus | PASS | FAIL | NOT-RUN | Originale |
|---|---:|---:|---:|---:|
| XTM 2.0 | **121** | **0** | **3** | 124 |
| CTM | **262** | **4** | **7** | 273 |
| Zusammen | **383** | **4** | **10** | 397 |

Alle 121 registrierten XTM-Case-Records sind eindeutig und PASS. Die drei
verbleibenden positiven Originale werden weiterhin als unregistriert geführt;
die Disposition verändert weder deren Status noch die Definition von NOT-RUN.
Die vier bekannten CTM-FAILs und sieben CTM-NOT-RUN bleiben unverändert.

| Abnahmetor aus 22A | Bedeutung und Stand nach 22O |
|---|---|
| **A — Normative Konformität** | Weiterhin offen: unabhängiger ISO-/Errata-Abgleich, Q-XTM-LOOP und die vorhandenen Editions-/Klausel-/Profilgrenzen sind nicht abgeschlossen. Eine Fall-Disposition ist keine Gesamtkonformität. |
| **B — Qualifizierter Testsuite-Abschluss** | Weiterhin offen: 397 Originale sind nicht sämtlich erfüllt; CTM 4 FAIL/7 NOT-RUN und XTM 3 NOT-RUN bleiben sichtbar. Die beiden dokumentierten XTM-Korpuskonflikte erzeugen keinen PASS. Eine spätere Ausnahmeabnahme muss sie ausdrücklich benennen; die ungelöste Zyklusfrage bleibt offen. |
| **C — HyperDoc-Integration** | In 22O weder bearbeitet noch abgenommen. Die Dokumentation beweist keine Integration und erteilt keinen Integrationsauftrag. |

Die historische 22A-Formulierung „FAIL/Testabweichung“ bei Baselinekonflikten ist
hier eine fachliche Abweichungsbeurteilung. Sie bewirkt ausdrücklich **keine**
Umklassifizierung der beiden noch nicht registrierten XTM-Originale zu FAIL.
Die über diesen Slice hinausreichenden Q-CTM-, Q-CXTM- und Q-ERRATA-Fragen aus
22C bleiben bestehen. Bereits implementierte Fähigkeiten werden dadurch nicht
zurückgenommen, und historische Slice-Vorschläge werden nicht zu neuen Aufträgen.

## Abschluss und verbleibender Entscheidungsbedarf

Die Disposition der drei Fälle ist dokumentiert: korrekte Dokument-ID-Ablehnung
bei positivem Korpuskonflikt; normativer Inhaltsimport bei zusätzlicher
historischer Map-II-Erwartung; offene Zyklusfrage Q-XTM-LOOP. Ein unabhängiger
Abgleich mit den offiziellen ISO-Ausgaben bleibt ausstehend. Ein späterer
qualifizierter Ausnahmeabschluss der ersten beiden Verträge muss die Abweichung
und deren Editionsbasis nennen; für den dritten Vertrag fehlt weiterhin die
normative beziehungsweise ausdrücklich abgenommene Verfahrensgrundlage.

Der lokale Slice-22O-Commit soll ausschließlich diesen neuen Bericht enthalten.
Sein Parent ist der oben genannte unveränderte 22N-Commit; die Commit-ID und der
abschließende saubere Git-Zustand werden nach dem Commit separat ausgegeben,
um keine selbstreferenzielle Commit-ID in das Dokument einzuschreiben.
Keine Produktions-/Test-/Registrierungsänderung, kein Download, Push,
Deployment, HyperDoc-Eingriff oder Folgeauftrag. Ende Slice 22O.
