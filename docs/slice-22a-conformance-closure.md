# Slice 22A — Abschlussplanung für Profil 1 und HyperDoc

Stand: 20. Oktober 2026. Ausgangscommit: `1c0b92c68fe1114b926d4405b553dfb096d2f425`; Untersuchungsbranch: `codex/conformance-slice-22a`.

Die Ausgangsregression wurde vollständig reproduziert. Dieser Slice registriert keinen zusätzlichen PASS und ändert weder Produktionscode noch Tests, Korpus oder historische Berichte. Die drei Abnahmetore A, B und C bleiben offen. Der Plan beschreibt weitere, jeweils gesondert zu beauftragende Arbeit; er behauptet keinen Konformitätsabschluss nach Zettel 11326.

| Korpus | PASS | FAIL | NOT-RUN | Gesamt |
|---|---:|---:|---:|---:|
| CTM | 262 | 4 | 7 | 273 |
| XTM 2.0 | 70 | 0 | 54 | 124 |
| Zusammen | 332 | 4 | 61 | 397 |

Die [vollständige lesbare Matrix](slice-22a-conformance-matrix.md) enthält genau 65 eindeutige offene Originale. [matrix.json](../reports/slice-22a/matrix.json) bewahrt pro Fall Originaltext und Hexbytes, SHA-256, Document IRI, Baselinebytes und -baum, registrierten Status, aktuelle Condition einschließlich Cause und Position, Modellbeobachtung, Normversion/Fundstellen, Begründungsstand, Abhängigkeiten und nächsten Slice. Der [maschinenlesbare Abschlussplan](../reports/slice-22a/closure-plan.json) enthält zusätzlich alle vorgeschlagenen Slices und Integrationskriterien.

## Evidenz und Normeditionen

**Beobachtet** bezeichnet eine frische Ausführung oder gelesene lokale Quelle. **Abgeleitet** bezeichnet eine Schlussfolgerung aus den angegebenen Normstellen innerhalb ihrer Editionsgrenzen. **Inferiert** bezeichnet den aus Implementierung und Ergebnissen erschlossenen Arbeitsumfang. **Hypothese** bezeichnet eine unbelegte historische Absicht. **Vorgeschlagen** bezeichnet künftige Arbeit oder Abnahme, keine bereits erreichte Eigenschaft. Diese Unterscheidungen gelten auch für die maschinenlesbare Matrix; deren Klassifikation ist eine überprüfbare fachliche Beurteilung, kein neuer Harness-Status.

| Gegenstand | Zielausgabe / verfügbare Primärevidenz | Grenze |
|---|---|---|
| CTM | ISO/IEC 13250-6:2010; [öffentliche HTML-Fassung](https://www.isotopicmaps.org/ctm/ctm.html); [veröffentlichte Vorschau](https://cdn.standards.iteh.ai/samples/43940/6663ee28c1604551ac6adc02e22c6bb6/ISO-IEC-13250-6-2010.pdf), erste Ausgabe 2010-11-15 | Die Vorschau enthält den Text nur bis §3.4.2. Spätere Template-/Include-Klauseln sind hier nur in der HTML-Fassung geprüft. Deren vollständige Identität mit der veröffentlichten Ausgabe ist nicht nachgewiesen. |
| XTM 2.0 | ISO/IEC 13250-3:2007; [öffentliche Fassung vom 2006-06-19](https://www.isotopicmaps.org/sam/sam-xtm/) | Die Seite erklärt ihre Identität mit der Veröffentlichung. Publikation/Errata bleiben maßgeblich. |
| TMDM | ISO/IEC 13250-2:2006; [öffentliche Fassung vom 2006-06-18](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/) | Erklärt Identität mit Veröffentlichung; §1 enthält ausdrücklich keine eigene Processor-Conformance-Klausel. Modellinvarianten sind separat zu prüfen. |
| CXTM | ISO/IEC 13250-4:2009; [öffentliche Fassung vom 2009-01-27](https://www.isotopicmaps.org/cxtm/cxtm.html) | Abschließender Abgleich mit veröffentlichter Ausgabe und Errata steht aus. |
| XSD-Datentypen | [XML Schema 1.0 Part 2, zweite Ausgabe 2004-10-28](https://www.w3.org/TR/2004/REC-xmlschema-2-20041028/) | Keine stillschweigende Anwendung von XSD 1.1. |
| XML-Inhalte | [Canonical XML 1.0, 2001-03-15](https://www.w3.org/TR/2001/REC-xml-c14n-20010315), §§2.1–2.4; XTM §4.16.3 | Der von XTM bestimmte Teilbaum und der Ausschluss von Kommentaren sind zu qualifizieren; kein Austausch gegen C14N 1.1/2.0. |

Der gepinnte Korpus `cd165b150176c1d6842b37be9cc9051b40d4996b` benennt in `vendor/cxtm/ctm/STATUS.txt` den Entwurf vom 31. März 2010. Die README-Aussage über richtige Tests ist keine unabhängige Normevidenz. `ctm/MISSING.txt` und `xtm2/MISSING` benennen Abdeckungslücken. Es wurde kein vollständiger Normtext heruntergeladen oder als neue lokale Normkopie abgelegt. [normative-review.json](../reports/slice-22a/normative-review.json) hält Fundstellen und Grenzen fest.

## Tatsächlich reproduzierte Regression

Das bestehende `scripts/validate-slice-21o.py` lief unverändert mit gepinnten, bereits vorhandenen Abhängigkeiten. Jeder Lisp-Prozess startete mit SBCL 2.5.4, `--no-sysinit --no-userinit` und frischem Prozess. Die Kindprozesse hatten durch `sandbox-exec` gesperrtes Netzwerk und keinen Schreibzugriff auf das Topic-Maps-Repository. Neue Beobachtungsprozesse sperrten zusätzlich Schreibzugriff auf HyperDoc. Ergebnisse und FASLs entstanden außerhalb der Repositories; kein langlebiges Image wurde geladen.

| Nachweis | Tatsächliches Ergebnis |
|---|---:|
| Bestehende Validator-Prozesse | 109, davon 6 regulär mit Exit 0 und 103 erwartete Fault-Kontrollen mit Exit 1 |
| TMDM/CTM/CXTM-Grundregression einschließlich Include/Mergemap | 12.100 Checks |
| Eigenständige XTM-Regression einschließlich Names, Scopes, II und Reification | 2.384 Checks |
| XML-Qualifikation | 146 Checks |
| CTM/XTM-Mergemap | 217 Checks |
| CTM registrierte positive / negative Originale | 286 / 25 Checks |
| Prolog / empty2 / CTM-Integer / Triple-Strings / Encoding | 171 / 13 / 112 / 226 / 722 Checks |
| Python / NFC-Oracle | 2 Tests / 16.294 Vergleiche |
| Erneut erzeugte, mit Slice 21O byteidentische Verhaltensberichte | 154 |
| Zusätzliche frische Untersuchungsprozesse | 2, beide Exit 0 |
| CTM offene Originale / bestehende Template-Kontextgegenproben | 11 / 12 |
| Zusätzliche diagnostische Profilgegenproben | 8, keine Originalverträge oder Registrierung |

Die 124 aktuellen XTM-Originalbeobachtungen einschließlich aller offenen Fälle stammen ebenfalls aus dem frisch ausgeführten bestehenden Diagnoselauf. Die zwölf Template-Kontrollen stimmen exakt mit der historischen Slice-20J-Evidenz überein. Registrierte Case Records wurden in der Untersuchung vor/nach verglichen und blieben unverändert.

Die [Ausführungsevidenz](../reports/slice-22a/execution.json), [109 Prozesskommandos und Ergebnisse](../reports/slice-22a/baseline/execution.json), [zusätzlichen Kommandos](../reports/slice-22a/investigation/execution.json) und [154 SHA-256-Vergleiche](../reports/slice-22a/baseline-comparison.json) sind neu gesichert. Der unveränderte alte Validator nennt in seinem Report weiterhin seine historische Slice-21O-Basis und damalige „new“-Checks; diese Felder sind **keine** neuen Slice-22A-Registrierungen. Tatsächliche 22A-Basis, Branch und Nullgewinn stehen im übergeordneten Bericht und im Anfangssnapshot.

## Klassifikation aller offenen Verträge

| Primäre Beurteilung | Anzahl | Bedeutung |
|---|---:|---|
| Fehlende Sprachfähigkeit | 51 | 51 XTM-Originale mit noch fehlender Unterstützung; Fähigkeitserweiterung muss erst tatsächlich qualifiziert werden. |
| Norm-/Baseline-Konflikt | 10 | Sieben CTM-Template-Fälle, zwei DateTime-Abweichungen und vorläufig XTM-Map-Item-Identity. Editionsgrenzen bleiben ausdrücklich sichtbar. |
| Ungeklärte Anforderung | 3 | Zwei CTM-Include-Fälle und XTM-mergeMap-Zyklus. |
| Beobachtet erfolgreich, unregistriert | 1 | `xtm2/in/variant-duplicate-reifier2.xtm`; erneuter Originalvergleich 702/702 Bytes. |

Dies ist eine primäre Zuordnung: Ein Konfliktfall kann zusätzlich eine noch fehlende Reader-Fähigkeit haben. Die Inventarisierung ist aus den aktuellen Case Records und dem aktuellen XTM-Inventar abzüglich registrierter Originale abgeleitet. Keine Kandidatenliste aus alten Berichten ersetzt das Inventar. `.sub`-Dateien, synthetische Kontrollen und Baselines zählen nicht als zusätzliche Verträge.

## Vier CTM-FAILs: Modelle, Abweichungen und Entscheidung

Für diese vier Quellen war die tatsächliche Condition jeweils **null**: Deserialisierung gelang, der vollständige CXTM-Vergleich scheiterte. Die zusätzliche Beobachtung prüft aktuelle Referenzen und modellunverändernde Kanonisierung. Vollständige Originalbytes, Modelle, Include-Umgebungen und CXTM stehen in [ctm-observations.json](../reports/slice-22a/investigation/ctm-observations.json) und der Matrix. Bytepositionen der ersten Differenz sind nullbasiert.

### `ctm/in/include-template.ctm` — Entscheidung C

**Beobachtet:** 48 Quellbytes, kein abschließendes LF. `%include <include-template.sub>` lädt eine Definition `def template($topic)` mit `$topic occtype: "Test".`; danach ruft die Elternquelle `template(topic)` auf. Das Kind enthält nach bloßer Definition null Topics. Der spätere Aufruf erzeugt zwei Topics: `#topic` und `#occtype` im Eltern-Dokument, eine Occurrence mit Wert `Test`, Datentyp `xsd:string`, Parent `#topic`, Type `#occtype`, leerem Scope; keine Names oder Associations. Der Wildcard-Zähler bleibt 0.

**Baseline:** 401 Bytes statt tatsächlich 353; erste Differenz Byte 58. Die Baseline erwartet am Type-Topic zusätzlich `include-template.sub#occtype` als Item Identifier und entsprechend andere kanonische Topicnummern. Im beobachteten definitionsleeren Kind hat die Include-Aliasphase noch kein solches Topic als Operand.

**Abgeleitet / offen:** CTM §§3.2, 3.14–3.16.2 verbinden Umgebungen, Template-Übernahme und Include-Identifier. Frühere Berichte deuten dies als B, weil eine Definition keine eager Topic-Erzeugung verlangt und der Aufruf am Aufrufort verarbeitet wird. Die konkrete Behandlung später instanziierter Template-Identifier durch die Include-Umgebung ist jedoch anhand des vollständigen veröffentlichten Normtexts noch nicht primär verifiziert. Die HTML-Fassung allein schließt die Editionsfrage nicht. **Formale Entscheidung C**, B unter bisheriger HTML-Auslegung plausibel. Nächster Schritt: Quell-/Aufrufumgebung und Zeitpunkt der Aliasbildung aus der maßgeblichen Ausgabe belegen; keine zusätzliche II allein zur Baselineanpassung erzeugen. [CTM §§3.14–3.16](https://www.isotopicmaps.org/ctm/ctm.html).

### `ctm/in/include-wildcard2.ctm` — Entscheidung C

**Beobachtet:** Wurzel A inkludiert B (`include-wildcard2.sub`), B inkludiert C (`include-wildcard2.sub2`); jede Quelle verwendet `?foo` mit Name `Master`, `Sub` beziehungsweise `Sub Sub`. Der gemeinsame Zähler endet bei 3. Vier Topics entstehen: drei benannte Wildcard-Topics und der Standard-Name-Type. C erhält die Dokument-IRI von B als Wildcard-IRI und erzeugt dort `$__1.foo`; B erzeugt unter A `$__2.foo`, A unter A `$__3.foo`. Die Übertragung fügt für `Sub Sub` den Alias unter A hinzu und bewahrt den II unter B. Alle Names und Referenzen bleiben erhalten.

**Baseline:** tatsächlich 719 gegenüber 669 Bytes; erste Differenz Byte 61. Die Baseline lässt den bestehenden Identifier `include-wildcard2.sub#$__1.foo` weg und behält den Wurzelalias. Es geht um Identifiererhaltung, nicht um Zählerwert oder Name-Verlust.

**Abgeleitet / offen:** Die untersuchte HTML-Regel §3.16.2 setzt die unmittelbare Eltern-Dokument-IRI als Wildcard-IRI und beschreibt zusätzliche Identifier; TMDM §§5.1 und 6 begründen keine beiläufige Löschung eines bestehenden II. Frühere B-Begründung ist unter dieser Lesart plausibel. Wegen des noch fehlenden Abgleichs der vollständigen veröffentlichten Include-Regel bleibt die formale Entscheidung **C**. Keine Identifier für den erwarteten Bytevergleich löschen. [CTM §3.16.2](https://www.isotopicmaps.org/ctm/ctm.html), [TMDM §§5–6](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/).

### `ctm/in/occurrence-datetime-timezone2.ctm` — Entscheidung B, editionsqualifiziert

**Beobachtet:** Die unveränderte Quelle benennt `datetime` und `some-topic` und verwendet das nackte Literal `2011-01-01T00:00:00+02:00`. Es entstehen drei Topics, zwei Names und eine Occurrence. Ihr gespeicherter Wert und die CXTM-Ausgabe lauten `2010-12-31T22:00:00Z`, Datentyp `xsd:dateTime`; Parent und Type verweisen auf die aktuellen Topics. Die Baseline behält die Offset-Schreibweise. Tatsächlich 674 gegenüber 679 Bytes; erste Differenz Byte 382.

**Abgeleitet:** CTM §3.4.1 bezieht seine DateTime-Literale auf XSD; die veröffentlichte Vorschau enthält diese Klausel. XSD 1.0 §3.2.7.2 verlangt in kanonischer Darstellung für zeitbezogene Werte UTC mit `Z`; CXTM §3.16 verwendet die kanonische Datentypdarstellung. Das gezeigte Ergebnis erhält den Zeitpunkt. **B** ist damit gestützt; der abschließende CXTM-Ausgaben-/Errata-Abgleich bleibt Teil des Normreviews. FAIL erhalten, keine Ausgabe mit historischem Offset erzwingen. [XSD §3.2.7.2](https://www.w3.org/TR/2004/REC-xmlschema-2-20041028/#dateTime-canonical-representation), [CXTM §3.16](https://www.isotopicmaps.org/cxtm/cxtm.html).

### `ctm/in/occurrence-datetime2.ctm` — Entscheidung B, editionsqualifiziert

**Beobachtet:** Original mit UTF-8-BOM und Leap-Second-Kommentar; Literal `1976-09-19T12:01:60`. Zwei Topics, eine Occurrence mit Type `occtype`, Parent `topic`, `xsd:dateTime`. Gespeicherter und kanonisierter Wert `1976-09-19T12:02:00`; die Baseline erwartet unverändert `12:01:60`. Beide Ausgaben haben 370 Bytes, erste Differenz Byte 232. Die Ablehnung einer Eingabe ist hier nicht das Ergebnis.

**Abgeleitet:** XSD 1.0 §3.2.7 und Anhang D.1 unterscheiden Leap-Second-Kandidaten und die Behandlung einer ungeeigneten Sekunden-60-Position als folgende Minute. Die gegebene Minute ist kein solcher Kandidat. CXTM §3.16 verlangt kanonischen Wert. Die Befunde stützen **B**; kein nach Dateiname oder Kommentar erzwungener Sonderwert, kein neues historisches Leap-Second-Datenarchiv. CXTM-Editionsreview bleibt offen. [XSD D.1](https://www.w3.org/TR/2004/REC-xmlschema-2-20041028/), [CXTM §3.16](https://www.isotopicmaps.org/cxtm/cxtm.html).

Bei keinem der vier Fälle wurde in dieser Untersuchung ein normativ nachgewiesener **A-Implementierungsfehler** festgestellt. Das ist keine Behauptung, alle künftigen Auslegungen seien entschieden. B und C bleiben sichtbar unterschiedliche Entscheidungen.

## Sieben CTM-Template-Fälle

**Abgeleitet aus der geprüften HTML-Grammatik:** Im unmarkierten zusätzlichen Subject-Identifier des Topic Tail führt `[50] → [51] → [52] → [17] → [12]` zur IRI-Produktion ohne Variable. Dagegen erlauben Topic Identity `[13]`, markierte Subject Locator / Item Identifier `[18]`/`[19]`, Topic Reference `[20]` und Literal `[28]` ausdrücklich Variablen. §§3.14–3.15 beschränken deren Ort auf Templates, binden Argumente positionsabhängig und prüfen den Verwendungskontext nach Substitution. Eine Variable am Topic-Kopf, nach `=`/`^` oder als Literal ist daher nicht dieselbe Grammatikposition wie die unmarkierte zusätzliche SI-Variable im Tail. [CTM §§3.3.5–3.4, 3.8–3.9 und 3.14–3.15](https://www.isotopicmaps.org/ctm/ctm.html).

Alle sieben Originale werden aktuell schon beim Template-Body mit `INVALID-TEMPLATE-BODY/:template-identity-tail` zurückgewiesen. Ursache/Context sind jeweils null, es gibt kein erzeugtes Originalmodell und keinen positiven Original-CXTM-Vergleich. Die Fehlerposition ist die tatsächliche Readerposition am erkannten Token, nicht eine nachträglich behauptete Startposition jeder Variable. Die folgenden Quellen und Variablenpositionen stammen aus den unveränderten Originalen; SHA-256/Hex und Bindungen stehen vollständig in der Matrix.

### `ctm/in/template-ambiguous-parameter5.ctm`

```ctm

# Using an IRI argument in different contexts

def template($iri)
  topic $iri; =$iri; ^$iri.
end

template(<http://www.example.org/something/>)
```

**Beobachtet:** $iri ← `<http://www.example.org/something/>`. Fehler an Zeichen 79 (nullbasiert), 5:13 (Zeile/Spalte einsbasiert), `INVALID-TEMPLATE-BODY/:template-identity-tail`.

**Erwartung / Gegenprobe:** Die historische positive Baseline umfasst 353 Bytes. Die ausgeschriebene Kontrollquelle ohne problematische Tail-Variable deserialisiert erneut und stimmt vollständig 353/353 Bytes überein. Das zählt als Kontextgegenprobe, nicht als Ausführungserfolg des Originals.

**Variablenverwendungen:** $iri 4:14 — Parameterdeklaration; $iri 5:9 — Subject Identifier im Topic Tail (unmarkiert); $iri 5:16 — Subject Locator nach =; $iri 5:23 — Item Identifier nach ^.

### `ctm/in/template-ambiguous-parameter6.ctm`

```ctm

%prefix ex <http://www.example.org/>

# Using a QName argument in different contexts

def template($q)
  topic $q; =$q; ^$q; occ: $q.
end

template(ex:something)
```

**Beobachtet:** $q ← `ex:something → http://www.example.org/something`. Fehler an Zeichen 114 (nullbasiert), 7:11 (Zeile/Spalte einsbasiert), `INVALID-TEMPLATE-BODY/:template-identity-tail`.

**Erwartung / Gegenprobe:** Die historische positive Baseline umfasst 613 Bytes. Die ausgeschriebene Kontrollquelle ohne problematische Tail-Variable deserialisiert erneut und stimmt vollständig 613/613 Bytes überein. Das zählt als Kontextgegenprobe, nicht als Ausführungserfolg des Originals.

**Variablenverwendungen:** $q 6:14 — Parameterdeklaration; $q 7:9 — Subject Identifier im Topic Tail (unmarkiert); $q 7:14 — Subject Locator nach =; $q 7:19 — Item Identifier nach ^; $q 7:28 — Occurrence-Literal; Datentyp xsd:anyURI.

### `ctm/in/template-subject-identifier2.ctm`

```ctm

def template($iri)
    topic $iri.
end

template(<http://psi.example.org/fake>)
```

**Beobachtet:** $iri ← `<http://psi.example.org/fake>`. Fehler an Zeichen 34 (nullbasiert), 3:15 (Zeile/Spalte einsbasiert), `INVALID-TEMPLATE-BODY/:template-identity-tail`.

**Erwartung / Gegenprobe:** Die historische positive Baseline umfasst 204 Bytes. Die ausgeschriebene Kontrollquelle ohne problematische Tail-Variable deserialisiert erneut und stimmt vollständig 204/204 Bytes überein. Das zählt als Kontextgegenprobe, nicht als Ausführungserfolg des Originals.

**Variablenverwendungen:** $iri 2:14 — Parameterdeklaration; $iri 3:11 — Subject Identifier im Topic Tail (unmarkiert).

### `ctm/invalid/template-item-identifier-2nd-arg.ctm`

```ctm

def template($iri1, $iri2)
    topic1 $iri1.
    topic2 $iri2.
end

template(<http://www.example.org/>,     # valid
        ^<http://www.example.org/>)     # invalid
```

**Beobachtet:** $iri1 ← `<http://www.example.org/>`; $iri2 ← `^<http://www.example.org/>`. Fehler an Zeichen 44 (nullbasiert), 3:17 (Zeile/Spalte einsbasiert), `INVALID-TEMPLATE-BODY/:template-identity-tail`.

**Beabsichtigte negative Prüfung:** Das zweite Argument ist mit `^` markiert und passt nicht als Subject Identifier in den unmarkierten Verwendungskontext. Tatsächlich blockiert bereits die erste zusätzliche SI-Variable im Body. Die Argumentprüfung wird nicht erreicht.

**Variablenverwendungen:** $iri1 2:14 — Parameterdeklaration; $iri2 2:21 — Parameterdeklaration; $iri1 3:12 — Subject Identifier von topic1 (unmarkiert); $iri2 4:12 — Subject Identifier von topic2 (unmarkiert).

### `ctm/invalid/template-item-identifier3.ctm`

```ctm

def template($iri)
    topic $iri.
end

template(^<http://www.example.org/>)
```

**Beobachtet:** $iri ← `^<http://www.example.org/>`. Fehler an Zeichen 34 (nullbasiert), 3:15 (Zeile/Spalte einsbasiert), `INVALID-TEMPLATE-BODY/:template-identity-tail`.

**Beabsichtigte negative Prüfung:** Das erste Argument ist mit `^` markiert und passt nicht als Subject Identifier in den unmarkierten Verwendungskontext. Tatsächlich blockiert bereits die erste zusätzliche SI-Variable im Body. Die Argumentprüfung wird nicht erreicht.

**Variablenverwendungen:** $iri 2:14 — Parameterdeklaration; $iri 3:11 — Subject Identifier von topic (unmarkiert).

### `ctm/invalid/template-subject-locator-2nd-arg.ctm`

```ctm

def template($iri1, $iri2)
    topic1 $iri1.
    topic2 $iri2.
end

template(<http://www.example.org/>,     # valid
         =<http://www.example.org/>)    # invalid
```

**Beobachtet:** $iri1 ← `<http://www.example.org/>`; $iri2 ← `=<http://www.example.org/>`. Fehler an Zeichen 44 (nullbasiert), 3:17 (Zeile/Spalte einsbasiert), `INVALID-TEMPLATE-BODY/:template-identity-tail`.

**Beabsichtigte negative Prüfung:** Das zweite Argument ist mit `=` markiert und passt nicht als Subject Identifier in den unmarkierten Verwendungskontext. Tatsächlich blockiert bereits die erste zusätzliche SI-Variable im Body. Die Argumentprüfung wird nicht erreicht.

**Variablenverwendungen:** $iri1 2:14 — Parameterdeklaration; $iri2 2:21 — Parameterdeklaration; $iri1 3:12 — Subject Identifier von topic1 (unmarkiert); $iri2 4:12 — Subject Identifier von topic2 (unmarkiert).

### `ctm/invalid/template-subject-locator3.ctm`

```ctm

def template($iri)
    topic $iri.
end

template(=<http://www.example.org/>)
```

**Beobachtet:** $iri ← `=<http://www.example.org/>`. Fehler an Zeichen 34 (nullbasiert), 3:15 (Zeile/Spalte einsbasiert), `INVALID-TEMPLATE-BODY/:template-identity-tail`.

**Beabsichtigte negative Prüfung:** Das erste Argument ist mit `=` markiert und passt nicht als Subject Identifier in den unmarkierten Verwendungskontext. Tatsächlich blockiert bereits die erste zusätzliche SI-Variable im Body. Die Argumentprüfung wird nicht erreicht.

**Variablenverwendungen:** $iri 2:14 — Parameterdeklaration; $iri 3:11 — Subject Identifier von topic (unmarkiert).

**Entscheidung:** Unter der geprüften HTML-Fassung ist die jeweilige unmarkierte Tail-Variable ausgeschlossen. Die drei positiven Baselines setzen dagegen eine zusätzliche Sprachregel voraus. Ein späterer Kompatibilitätsmodus müsste ausdrücklich eine Variable als zusätzlichen unmarkierten Subject Identifier zulassen und nach Substitution IRI-/QName-/Referenzqualifikation, markierte Argumente und Positionsdiagnosen definieren. Eine historische Erweiterungsabsicht ist **Hypothese**, kein belegter Normtext.

Der vollständige veröffentlichte Grammatik-/Errata-Abgleich fehlt; formaler Editionsentscheid deshalb C. Alle sieben bleiben NOT-RUN. Die vier negativen Dateien sind bereits wegen des Body-Kontexts syntaktisch problematisch, ihre historische intendierte Argumentprüfung ist gleichwohl nicht erreicht. Nur ein gesondert freigegebener Qualifikationsentscheid könnte diese echte Body-Syntaxablehnung als Abschluss eines generischen negativen Originalvertrags akzeptieren; dabei wären weiterhin gesonderte gültige Kontextgegenproben nötig. Das ist höchstens eine bedingte spätere Registrierung von vier Fällen, kein jetziger Gewinn und keine Einladung zur Grammatikänderung. Die bestehende Slice-20J-Provenienz bleibt unverändert.

## 54 offene XTM-Originale nach Fähigkeiten

Alle exakten Dateinamen mit tatsächlicher XML-Struktur, erwarteten CXTM-Bäumen, Baselines und aktuellen Fehlerpositionen stehen in der Matrix. Die folgenden Gruppen partitionieren die 54 Originale; Datentyp-, Identitäts- und Reification-Fähigkeiten überschneiden sich fachlich.

| Familie | Originale | Beobachtung / notwendige Fähigkeit | Prognose zusätzlicher PASS |
|---|---:|---|---:|
| Bereits beobachteter Variant-Vertrag | 1 | `variant-duplicate-reifier2.xtm`: 543 Originalbytes; zwei gleiche Names mit gleichen reifizierten Variants normalisieren zu einem Name/Variant; Name `Topic`, Variant `TOPIC!`, `xsd:string`, Scope `#command`, Reifier `#reifier`, kein eigener Variant-II. 702/702 CXTM-Bytes erneut gleich. Keine Condition. | 1 nach eigenständiger Registrierung |
| Unbekannter textueller Datentyp | 1 | `variant-datatype-unknown.xtm`: `BOGUS` und `http://example.com/bogus` erhalten; aktuell `XTM-UNSUPPORTED/:resource-data-datatype`. Keine neue Datentypkonvertierung. | 1 |
| Occurrences | 17 | 16 positive mit Parent, Type, Scope, Text/resourceRef/anyURI/unbekanntem Datentyp, II, Reification und Merging; dazu negativer Map-/Occurrence-Reifier-Konflikt. Aktuell vorgelagertes Unsupported. | 17 |
| Associations und Roles | 17 | 16 positive mit Type, Player, Scope, II, Role-/Association-Normalisierung und Merging; dazu negative fragmentlose Topic Reference. | 17 |
| Association-/Role-Reification | 11 | Je fünf positive für Association und Role; ein negativer Role-Reifier-Konflikt. Native normalisierte Objekte und II-only Reifier-Auflösung verwenden. | 11 |
| XTM mergeMap | 7 | Endlicher Ressourcenresolver, Dokumentidentität, Inhaltimport, Root-Metadaten und Zyklen. Alle aktuell Unsupported. | 5 regulär erwartet, 2 normativ bedingt |
| **Gesamt** | **54** | Unveränderte NOT-RUN-Registrierung in 22A | **52 erwartet + 2 bedingt, noch nicht erreicht** |

Die XML-/Datentypverarbeitung folgt XTM §§4.15–4.16; Association und Role folgen §§4.18–4.19 sowie TMDM §§5.7–5.8 und 6.6–6.7. Bei doppelten Role-Elementen müssen Metadaten dem passenden normalisierten nativen Role-Objekt zugeordnet werden. Role-Parent gehört zur Gleichheit; ein gleicher Player/Type allein rechtfertigt keinen Merge über verschiedene Associations. Gleich aussehende Originalquellen bleiben getrennt auszuführende Verträge. [XTM §§4.15–4.20](https://www.isotopicmaps.org/sam/sam-xtm/), [TMDM §§5–6](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/).

### Drei negative XTM-Originale

| Case-ID | Tatsächliche frühe Ursache | Beabsichtigte zu erreichende Ursache |
|---|---|---|
| `xtm2/invalid/reifier-collision.xtm` | Unsupported beim Occurrence-Konstrukt | Derselbe Reifier `#reifier` wird für Map und Occurrence verwendet. Native `REIFICATION-ERROR/:reifier-conflict`, keine teilweise bestätigte Mutation. |
| `xtm2/invalid/role-duplicate-reified.xtm` | Unsupported beim Association-Konstrukt | Zwei Roles mit gleichem Type/Player liegen in unterschiedlichen Parent-Associations (`assoctype` / `assoctype2`). Ihr gemeinsamer Reifier darf sie nicht gleichsetzen; native Reifier-Kollision. |
| `xtm2/invalid/topicref-no-fragment-id.xtm` | Unsupported beim Association-Konstrukt | Die Scope-Referenz `href="scopingtopic"` hat kein Fragment, die übrigen Type-/Role-/Player-Referenzen sind markiert. XTM §4.20: qualifizierte `XTM-REJECTION/:invalid-topic-ref` an dieser Referenz. |

Die aktuellen konkreten Conditions, SAX-Zeilen/Spalten und Causes sind pro Original in der Matrix erhalten. Kein Unsupported wird als negativer PASS gewertet. XTM §4.3 und TMDM §5.1 begründen die Reifier-Eindeutigkeit. [XTM §§4.3, 4.20](https://www.isotopicmaps.org/sam/sam-xtm/).

### Zwei zusätzliche mergeMap-Entscheidungen

**`mergemap-itemid.xtm`:** Die Original-Submap setzt einen Map-II `mergemap-itemid.sub#the-topic-map`; die 314-Byte-Baseline erwartet diesen an der Zielmap. XTM §4.21 beschreibt dagegen den Import von Topics und Associations. Das vorhandene native `import-map-content` übernimmt bewusst nicht Root-II/Reifier. Der Baselinewunsch ist deshalb ein **vorläufiger Norm-/Baseline-Konflikt, Entscheidung C**, keine zugesagte Funktion. TMDM-Map-Metadaten, übergebene Zielmap und Notationsimport sind auseinanderzuhalten. Kein bloßes Kopieren für diesen Dateinamen. [XTM §4.21](https://www.isotopicmaps.org/sam/sam-xtm/), [TMDM §5.2](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/).

**`mergemap-loop.xtm`:** Originalressourcen referenzieren sich Root→Sub→Root; die unveränderte 222-Byte-Baseline enthält die beiden dokumentbezogenen Topics. §4.21 legt im untersuchten Text keinen expliziten Wiederholungs-/Cachealgorithmus fest. Ein endlicher, dokument-IRI-basierter Cache einschließlich Root ist ein zu qualifizierender Vorschlag; ein Cycle-Error wäre kein positiver Originalvergleich. Entscheidung **C**. Netzwerkfallback oder unendliche Rekursion sind keine Abnahme.

Die weiteren fünf Fälle heißen `mergemap-merge.xtm`, `mergemap-ontopia-issue-28-2.xtm`, `mergemap-ontopia-issue-28.xtm`, `mergemap-tm-reifier.xtm`, `mergemap.xtm`. `.sub`-Quellen und deren Graphen sind vollständig erfasst. Insbesondere erwartet `mergemap-tm-reifier` das importierte Reifier-Topic, aber keinen übernommenen Root-Reifier. Source Key und Document IRI dürfen nicht verwechselt werden.

## Profil 1: Umfang und zusätzliche Normpflichten

Profil 1 zielt auf die oben genannten CTM-/XTM-/TMDM-/CXTM-Ausgaben und 397 gepinnte Originalverträge. Das Foundation-System `topic-maps` ist allein kein Reader. Der Build muss ausdrücklich `topic-maps/tmdm`, `topic-maps/ctm`, `topic-maps/xtm`, `topic-maps/cxtm` und den bestehenden `topic-maps/ctm/xtm`-Adapter qualifizieren. TMDM-Invarianten, CXTM-Ordnung/Kanonisierung und Unicode/NFC sind neben Originalvergleichen nachzuweisen.

Ausgeschlossen vom zunächst vereinbarten Austauschformat-Korpus sind `xtm1`, `xtm21`, `ltm`, `tmxml`, `jtm`, `jtm11`, `rdf`, `tmcl`, `snello` sowie Web-/Release-Infrastruktur der Sammlung. `.sub`-Ressourcen sind notwendige Eingaben, keine eigenen Originalfälle. TMCL, TMQL und sämtliche Topic-Maps-Normen werden nicht allein durch dieses Profil abgedeckt.

**Beobachtete Abdeckungslücken jenseits der 65 Originale:** [profile-probes.json](../reports/slice-22a/investigation/profile-probes.json) enthält acht tatsächlich ausgeführte, unregistrierte Gegenproben. Der aktuelle Teilkorpus hat keinen `xsd:anyType`-/eingebetteten-XML-Originalvertrag; die Normpflicht verschwindet deshalb nicht.

| Gegenprobe | Tatsächliches Ergebnis | Abschlussbedarf |
|---|---|---|
| Unbekannter textueller Datentyp | `XTM-UNSUPPORTED/:resource-data-datatype`, 1:194 | §4.16.2: Datentyp-IRI/Wert erhalten, nicht in Datentyp-Topics umformen. |
| `xsd:anyType` mit XML | `XTM-UNSUPPORTED/:resource-data-datatype`, 1:210 | §4.16.3 und W3C C14N 1.0 qualifizieren. |
| Elementinhalt bei gewöhnlichem String | `XTM-UNSUPPORTED/:resource-data-markup`, 1:182 | Eingabe wird schon zurückgewiesen. Erreichte normative Fehlerursache/Diagnose qualifizieren; Lisp-Conditionname allein beweist keine Verletzung der Ablehnungspflicht. |
| Elementinhalt bei anyURI | `XTM-REJECTION/:unexpected-child`, 1:233 | Spezifische Zurückweisung erhalten. |
| Leeres DOCTYPE vor leerer Map | `XTM-XML-ERROR/:doctype-forbidden`, 1:20; Cause `DOCTYPE-FORBIDDEN` | Bewusste Betriebsgrenze für XML-Bytes, keine normative XTM-Syntaxungültigkeit behaupten. Infoset-/Parserprofil ausdrücklich entscheiden. |
| Deklariertes Shift-JIS bei ASCII-Inhalt | `CTM-UNSUPPORTED/:unsupported-encoding`, Zeichen 11, 1:12 | UTF-8/ISO-8859-5-Grenze offen nennen; normativ verpflichtenden Zeichensatzumfang aus maßgeblicher Edition bestimmen. |
| Qualifiziertes XSD-Date mit Zeitzone | Deserialisiert; CXTM `:date-timezone-canonicalization`, keine Quellposition | Datentyp-/Kanonisierungspflicht implementieren oder explizite Profileinschränkung. |
| BCE-DateTime mit Zeitzonen-Jahreswechsel | Deserialisiert; CXTM `:datetime-bce-timezone-rollover`, keine Quellposition | Kalender-/Zeitzonengrenze qualifizieren oder explizite Einschränkung. |

Weitere im Code sichtbare DateTime-Leap-Second-/Offsetgrenzen sind ebenfalls in die Klauselabdeckung aufzunehmen. Es ist keine Implementierung beliebiger IANA-Encodings allein aus der Existenz einer Deklaration abzuleiten. XTM §2 benennt XML 1.0 Third Edition (2004-02-04), Namespaces (1999-01-14), Infoset Second Edition (2004-02-04), XPointer (2003-03-25) und RFC 3986/3987. Die tatsächliche Implementierungsabdeckung sowie die CTM-/CXTM-Unicode-Bezüge bleiben klauselspezifisch zu prüfen; der NFC-Oracle-Lauf ersetzt das nicht.

**XML-Vorprüfung:** Der aktuelle XTM-SAX-Quellbaum speichert expandierte Namen, Attribute, Kinder, Text und Positionen; er bewahrt nicht den gesamten QName-/Namespace-Kontext für beliebige kanonische XML-Teilbäume. Die gepinnte CXML-Quelle bietet `make-octet-vector-sink :canonical`; das ist noch kein Nachweis des von XTM geforderten W3C-C14N-1.0-Verfahrens für den festgelegten Node-Set. XTM wählt Element-, Attribut- und Zeichen-Nachfahren aus und filtert Namespace-Knoten; PI gehören nicht zu diesem Node-Set, Kommentare werden ausgeschlossen. Zuerst vorhandene Fähigkeiten qualifizieren, dann gegebenenfalls einen gesondert freigegebenen XML-Adapter erweitern. Kein zweites TMDM-Modell und kein ungezielter XML-Umbau. [XTM §4.16.3](https://www.isotopicmaps.org/sam/sam-xtm/), [W3C C14N §§2.1–2.4](https://www.w3.org/TR/2001/REC-xml-c14n-20010315).

Aktuell zulässige Aussage: **qualifizierter Funktionsumfang mit ausgewiesenen Betriebsgrenzen und offenen Normentscheidungen**. Auch 397 PASS würden weder vollständige Klauselabdeckung noch uneingeschränkte ISO-Konformität beweisen.

## Priorisierte weitere Slices

Die folgenden Namen sind Vorschläge. Sie erteilen keine Implementierungsfreigabe in Slice 22A. Die exakten Original-IDs je Schritt stehen in `closure-plan.json` und der Matrix; bei 22C werden zusätzlich die zwei später 22H zugeordneten Auslegungsfälle geprüft. Alle Implementierungsschritte müssen unveränderte Originalbytes/IRIs, native Modell-/EQ-Prüfungen, vollständige CXTM-Vergleiche beziehungsweise qualifizierte negative Ursachen, tatsächliche ASDF-Ausführung, komplette frische Offline-Regression und Integrität nachweisen.

### 22B — Bereits bestandenen Variant-Reification-Originalvertrag registrieren

**Normative Funktion:** XTM 4.3,4.12-4.13; TMDM 5.5,6.3-6.4. **Abhängigkeiten:** existing-Slice-21O.

**Originalverträge:** `xtm2/in/variant-duplicate-reifier2.xtm`.

**Codebereiche:** `tests/xtm-variant-reification.lisp`; `tests/xtm-identity.lisp`; `topic-maps.asd`; `new evidence only`. **Modell-/Identitätsabnahme:** Parent-Name, kanonischer Variant, item-reifier/topic-reified EQ; Identifiertrennung; reine Kanonisierung; Source-Key-Unabhängigkeit; genau ein neuer Case Record.

**Erwarteter zusätzlicher Original-PASS-Gewinn:** 1; ausschließlich Prognose. **Stop:** Sobald aktuelle Originalbytes, native Prüfung oder 702-Byte-Vergleich abweichen; keine Produktionskorrektur in dieser Registrierungsaufgabe.

### 22C — Normedition, CTM-Auslegungen und XTM-mergeMap-Metadaten/Zyklen entscheiden

**Normative Funktion:** CTM 3.9,3.14-3.16; XTM 4.21; TMDM 5.1-5.3; CXTM 3.16; XSD 1.0 3.2.7,D.1. **Abhängigkeiten:** keine; frühzeitig unabhängig möglich.

**Originalverträge:** `ctm/in/include-template.ctm`, `ctm/in/include-wildcard2.ctm`, `ctm/in/occurrence-datetime-timezone2.ctm`, `ctm/in/occurrence-datetime2.ctm`, `ctm/in/template-ambiguous-parameter5.ctm`, `ctm/in/template-ambiguous-parameter6.ctm`, `ctm/in/template-subject-identifier2.ctm`, `ctm/invalid/template-item-identifier-2nd-arg.ctm`, `ctm/invalid/template-item-identifier3.ctm`, `ctm/invalid/template-subject-locator-2nd-arg.ctm`, `ctm/invalid/template-subject-locator3.ctm`, `xtm2/in/mergemap-itemid.xtm`, `xtm2/in/mergemap-loop.xtm`.

**Codebereiche:** `docs/`; `reports/`; `references only after approved normative review`. **Modell-/Identitätsabnahme:** Vollständigen veröffentlichten CTM-Text/Errata mit Mirror vergleichen; vier FAILs A/B/C entscheiden; sieben Tail-Fälle und intendierte negative Argumentprüfung getrennt behandeln; Map-II-Übertragung und Loop-Semantik belegen.

**Erwarteter zusätzlicher Original-PASS-Gewinn:** 0; ausschließlich Prognose. Bedingung: Nur falls eine ausdrücklich freigegebene Qualifikationsentscheidung die echte Body-Syntaxablehnung als Abschluss der generischen negativen Originalverträge akzeptiert; kein beobachteter zusätzlicher PASS und kein Ersatz für Kontextgegenproben. **Stop:** Keine Grammatik-, Umgebungs- oder Map-Metadatenregel ohne Normbeleg implementieren. Bei fehlendem Volltext bleibt Entscheidung offen und Zähler unverändert.

### 22D — Gemeinsames textuelles resourceData für unbekannte absolute Datentypen vervollständigen

**Normative Funktion:** XTM 4.16.1-4.16.2; TMDM 4.3-4.4,5.5-5.6. **Abhängigkeiten:** existing-qualified-XML/resourceData.

**Originalverträge:** `xtm2/in/variant-datatype-unknown.xtm`.

**Codebereiche:** `src/xtm/reader.lisp: validate-source/shared resource value path`; `existing XTM tests`. **Modell-/Identitätsabnahme:** BOGUS und Datentyp http://example.com/bogus exakt erhalten; keine Datentyp-Topics; kein URI-Resolving des Werts; Child-Elemente außerhalb anyType spezifisch ablehnen; xsd:string/anyURI erhalten.

**Erwarteter zusätzlicher Original-PASS-Gewinn:** 1; ausschließlich Prognose. **Stop:** Stop bei notwendiger Änderung von TMDM/CXTM oder unklarer Datentypkonvertierung; XML-anyType gehört in 22I.

### 22E — Occurrences über vorhandene native Operationen einschließlich Scope, II und Reification einlesen

**Normative Funktion:** XTM 4.3,4.6,4.13-4.17; TMDM 5.6,6.5. **Abhängigkeiten:** 22D for occurrence-datatype-unknown; existing TMDM occurrence/II/reifier APIs.

**Originalverträge:** `xtm2/in/itemid-occurrence.xtm`, `xtm2/in/merge-itemid-with-occurrences.xtm`, `xtm2/in/occurrence-datatype-unknown.xtm`, `xtm2/in/occurrence-duplicate-iid.xtm`, `xtm2/in/occurrence-duplicate-iid2.xtm`, `xtm2/in/occurrence-duplicate-reifier.xtm`, `xtm2/in/occurrence-duplicate.xtm`, `xtm2/in/occurrence-reifier.xtm`, `xtm2/in/occurrence-resourcedata-uri-relative.xtm`, `xtm2/in/occurrence-resourcedata-uri.xtm`, `xtm2/in/occurrence-resourceref-relative.xtm`, `xtm2/in/occurrence-resourceref.xtm`, `xtm2/in/occurrence-scope-duplicate-merged.xtm`, `xtm2/in/occurrence-scope-duplicate.xtm`, `xtm2/in/occurrence-scope.xtm`, `xtm2/in/occurrence.xtm`, `xtm2/invalid/reifier-collision.xtm`.

**Codebereiche:** `src/xtm/reader.lisp: occurrence validation/deserialization`; `existing XTM ASDF harness`. **Modell-/Identitätsabnahme:** add-occurrence/canonical-occurrence native Vorprüfung; Parent/Type/Scope EQ; text/ref/anyURI-Werte; Scope-Themes nach Merging; II vor Reification am normalisierten Item; gleiche Occurrences vereinigen Metadaten; Map-/Occurrence-Reifier-Konflikt vorgesehen und atomar.

**Erwarteter zusätzlicher Original-PASS-Gewinn:** 17; ausschließlich Prognose. **Stop:** Stop vor TMDM-Änderung bei nativer API-Lücke oder vor fremder Fehlerursache; reifier-collision erst bei nativer reifier-conflict zählen.

### 22F — Explizite Associations und Roles gemeinsam mit Scope und Item Identity

**Normative Funktion:** XTM 4.6,4.13-4.14,4.18-4.20; TMDM 5.7-5.8,6.6-6.7,7.2. **Abhängigkeiten:** existing native association/role API.

**Originalverträge:** `xtm2/in/association-binary-duplicate.xtm`, `xtm2/in/association-binary.xtm`, `xtm2/in/association-duplicate-iid.xtm`, `xtm2/in/association-duplicate-iid2.xtm`, `xtm2/in/association-duplicate-iid3.xtm`, `xtm2/in/association-duplicate-role.xtm`, `xtm2/in/association-instanceof-duplicate.xtm`, `xtm2/in/association-instanceof-scope.xtm`, `xtm2/in/association-scope.xtm`, `xtm2/in/association-ternary.xtm`, `xtm2/in/association.xtm`, `xtm2/in/itemid-association.xtm`, `xtm2/in/itemid-role.xtm`, `xtm2/in/merge-itemid-with-association.xtm`, `xtm2/in/role-duplicate-iid.xtm`, `xtm2/in/role-duplicate-iid2.xtm`, `xtm2/invalid/topicref-no-fragment-id.xtm`.

**Codebereiche:** `src/xtm/reader.lisp: association/role validation and readers`; `existing XTM ASDF harness`. **Modell-/Identitätsabnahme:** Unary/binary/ternary; Role-Type/Player/Parent EQ; Native make-association und kanonische Role-Handles; doppelte Roles/Associations; II-Vereinigung; Forward-/SI-/SL-/II-Merges; instanceOf-Synthese vs explizite Association, scoped Unterschied erhalten; negative Scope-Referenz ohne Fragment erreichen.

**Erwarteter zusätzlicher Original-PASS-Gewinn:** 17; ausschließlich Prognose. **Stop:** Stop bei unklarer Role-Zuordnung nach Normalisierung oder Modellfehler; keine zweite Identitätsrepräsentation oder Behandlung nach Dateinamen.

### 22G — Reification kanonischer Associations und Roles

**Normative Funktion:** XTM 4.3,4.18-4.19; TMDM 5.3.5,5.7-5.8,6.2,6.6-6.7. **Abhängigkeiten:** 22F; existing shared read-item-reifier.

**Originalverträge:** `xtm2/in/association-duplicate-reified.xtm`, `xtm2/in/association-duplicate-reified2.xtm`, `xtm2/in/association-duplicate-reified3.xtm`, `xtm2/in/association-duplicate-reified4.xtm`, `xtm2/in/association-reifier.xtm`, `xtm2/in/role-duplicate-reified.xtm`, `xtm2/in/role-duplicate-reified2.xtm`, `xtm2/in/role-duplicate-reified3.xtm`, `xtm2/in/role-duplicate-reified4.xtm`, `xtm2/in/role-reifier.xtm`, `xtm2/invalid/role-duplicate-reified.xtm`.

**Codebereiche:** `src/xtm/reader.lisp: normalized association/role attachment points`; `existing XTM ASDF harness`. **Modell-/Identitätsabnahme:** Native Vorprüfung vor Reader-Änderung; Normalisierung vor II/R-Zuweisung; alte Association-/Role-/Reifier-Handles kanonisch; Parent gehört zur Role-Gleichheit; Metadaten bleiben beim Association-Merge erhalten; verschiedene Parent-Associations dürfen nicht durch gemeinsamen Role-Reifier gleichgesetzt werden.

**Erwarteter zusätzlicher Original-PASS-Gewinn:** 11; ausschließlich Prognose. **Stop:** Stop vor TMDM-Änderung; negative Role erst bei beabsichtigtem reifier-conflict registrieren; gleichartige Quellfälle trotzdem jeweils tatsächlich vergleichen.

### 22H — XTM mergeMap über kontrollierte gepinnte Ressourcen

**Normative Funktion:** XTM 4.2,4.21; TMDM 5.1-5.3,6. **Abhängigkeiten:** 22C:map-metadata/cycles; existing qualified XML/IRI/import-map-content.

**Originalverträge:** `xtm2/in/mergemap-itemid.xtm`, `xtm2/in/mergemap-loop.xtm`, `xtm2/in/mergemap-merge.xtm`, `xtm2/in/mergemap-ontopia-issue-28-2.xtm`, `xtm2/in/mergemap-ontopia-issue-28.xtm`, `xtm2/in/mergemap-tm-reifier.xtm`, `xtm2/in/mergemap.xtm`.

**Codebereiche:** `src/xtm/reader.lisp`; `XTM resource boundary, reusing existing CTM resource/import principles`; `tests and pinned .sub sources`. **Modell-/Identitätsabnahme:** Child Document IRI, getrennte Source Keys; Fragmentverbot; finite Resolver-Tabelle inklusive Root; rekursive Ressourcen; SI/II-Cross-Merging; reine Quellen; root metadata getrennt von importiertem Inhalt; keine Netzwerkfallbacks.

**Erwarteter zusätzlicher Original-PASS-Gewinn:** 5 regulär erwartet, 2 bedingt, maximal 7; ausschließlich Prognose. Bedingung: Abnahme nur nach Klärung 22C und tatsächlichem Originalvergleich. **Stop:** Map-II darf nicht allein für Baselinekopie übertragen werden. Loop-Policy muss normativ/profilbezogen geklärt sein; ungeklärte Fälle bleiben offen, unabhängige Fälle dürfen qualifiziert werden.

### 22I — anyType/XML und übrige explizite Profil-Lücken schließen oder einschränken

**Normative Funktion:** XTM 4.16.2-4.16.3,5; Canonical XML 1.0 2.1-2.4; CTM 3.2,3.4,3.6; CXTM 3.16. **Abhängigkeiten:** 22C:explicit conformance profile; 22D; qualified XML event/canonicalization review.

**Originalverträge:** keine zusätzlichen Originale; gesonderte Profil-/Integrationsprüfungen.

**Codebereiche:** `src/xtm/reader.lisp: source-handler/resourceData`; `qualified XML adapter only if separately authorized`; `CTM/CXTM limits only after scoped normative approval`; `supplemental tests`. **Modell-/Identitätsabnahme:** W3C Canonical XML 1.0 für XTM-Subset ohne Kommentare qualifizieren; QName/Namespace-Kontext für ausgewählte Elemente/Attribute erhalten; XTM-Node-Set aus Elementen/Attributen/Zeichen bilden, unbenutzte Namespace-Knoten entfernen, PI und Kommentare nicht aufnehmen; vorhandenes CXML :canonical nicht ungeprüft als Beleg ansehen; nicht-anyType-Elementdiagnose unterscheiden; DOCTYPE/Entity-Policy als Betriebsprofil; Date/DateTime/BCE/Encoding-Normpflichten und Grenzen ausdrücklich entscheiden.

**Erwarteter zusätzlicher Original-PASS-Gewinn:** 0; ausschließlich Prognose. **Stop:** Keine Vollkonformitätsbehauptung aus 397 Tests; bei neuer XML/TMDM/CXTM-Architektur oder ungeklärter Normpflicht vor Änderung stoppen und gesonderten Umfang entscheiden.

### 22J — Profil-1-Abschlussaudit: normative Klauselabdeckung, 397 Originale und Ausnahmen

**Normative Funktion:** Profile 1 target editions and their actual reviewed clauses. **Abhängigkeiten:** 22B-22I normative/implementation decisions.

**Originalverträge:** `ctm/in/include-template.ctm`, `ctm/in/include-wildcard2.ctm`, `ctm/in/occurrence-datetime-timezone2.ctm`, `ctm/in/occurrence-datetime2.ctm`, `ctm/in/template-ambiguous-parameter5.ctm`, `ctm/in/template-ambiguous-parameter6.ctm`, `ctm/in/template-subject-identifier2.ctm`, `ctm/invalid/template-item-identifier-2nd-arg.ctm`, `ctm/invalid/template-item-identifier3.ctm`, `ctm/invalid/template-subject-locator-2nd-arg.ctm`, `ctm/invalid/template-subject-locator3.ctm`, `xtm2/in/association-binary-duplicate.xtm`, `xtm2/in/association-binary.xtm`, `xtm2/in/association-duplicate-iid.xtm`, `xtm2/in/association-duplicate-iid2.xtm`, `xtm2/in/association-duplicate-iid3.xtm`, `xtm2/in/association-duplicate-reified.xtm`, `xtm2/in/association-duplicate-reified2.xtm`, `xtm2/in/association-duplicate-reified3.xtm`, `xtm2/in/association-duplicate-reified4.xtm`, `xtm2/in/association-duplicate-role.xtm`, `xtm2/in/association-instanceof-duplicate.xtm`, `xtm2/in/association-instanceof-scope.xtm`, `xtm2/in/association-reifier.xtm`, `xtm2/in/association-scope.xtm`, `xtm2/in/association-ternary.xtm`, `xtm2/in/association.xtm`, `xtm2/in/itemid-association.xtm`, `xtm2/in/itemid-occurrence.xtm`, `xtm2/in/itemid-role.xtm`, `xtm2/in/merge-itemid-with-association.xtm`, `xtm2/in/merge-itemid-with-occurrences.xtm`, `xtm2/in/mergemap-itemid.xtm`, `xtm2/in/mergemap-loop.xtm`, `xtm2/in/mergemap-merge.xtm`, `xtm2/in/mergemap-ontopia-issue-28-2.xtm`, `xtm2/in/mergemap-ontopia-issue-28.xtm`, `xtm2/in/mergemap-tm-reifier.xtm`, `xtm2/in/mergemap.xtm`, `xtm2/in/occurrence-datatype-unknown.xtm`, `xtm2/in/occurrence-duplicate-iid.xtm`, `xtm2/in/occurrence-duplicate-iid2.xtm`, `xtm2/in/occurrence-duplicate-reifier.xtm`, `xtm2/in/occurrence-duplicate.xtm`, `xtm2/in/occurrence-reifier.xtm`, `xtm2/in/occurrence-resourcedata-uri-relative.xtm`, `xtm2/in/occurrence-resourcedata-uri.xtm`, `xtm2/in/occurrence-resourceref-relative.xtm`, `xtm2/in/occurrence-resourceref.xtm`, `xtm2/in/occurrence-scope-duplicate-merged.xtm`, `xtm2/in/occurrence-scope-duplicate.xtm`, `xtm2/in/occurrence-scope.xtm`, `xtm2/in/occurrence.xtm`, `xtm2/in/role-duplicate-iid.xtm`, `xtm2/in/role-duplicate-iid2.xtm`, `xtm2/in/role-duplicate-reified.xtm`, `xtm2/in/role-duplicate-reified2.xtm`, `xtm2/in/role-duplicate-reified3.xtm`, `xtm2/in/role-duplicate-reified4.xtm`, `xtm2/in/role-reifier.xtm`, `xtm2/in/variant-datatype-unknown.xtm`, `xtm2/in/variant-duplicate-reifier2.xtm`, `xtm2/invalid/reifier-collision.xtm`, `xtm2/invalid/role-duplicate-reified.xtm`, `xtm2/invalid/topicref-no-fragment-id.xtm`.

**Codebereiche:** `docs/`; `reports/`; `existing harness execution`. **Modell-/Identitätsabnahme:** 397 eindeutige Originale, keine Hilfsressourcen mitzählen; native TMDM-Eigenschaften separat; CXTM-Byte-/Sortier-/NFC-/Reinheitsnachweise; dokumentierte genehmigte Abweichungen statt falscher PASS; Offline-Build/Run-Manifest und Paketversionen.

**Erwarteter zusätzlicher Original-PASS-Gewinn:** 0; ausschließlich Prognose. **Stop:** Tor A/B bleiben offen bei ungeklärter Klausel, unregistriertem unqualifiziertem Fall, künstlicher PASS-Zahl oder unerklärter Regression.

### 22K — HyperDoc-Abhängigkeit und bestehende native Inspector-Anbindung qualifizieren

**Normative Funktion:** Integration gate C; conformance gates remain separate. **Abhängigkeiten:** 22J:approved profile / explicit remaining exceptions; separate HyperDoc change authorization.

**Originalverträge:** keine zusätzlichen Originale; gesonderte Profil-/Integrationsprüfungen.

**Codebereiche:** `HyperDoc dreyeck.asd / flake.nix / lock configuration`; `existing dreyeck/inspector/tmdm and TMDM reading adapters`; `packaging tests`. **Modell-/Identitätsabnahme:** Einen reproduzierbaren Topic-Maps-Commit wählen; 5a4a668-Performance-Abzweig ausdrücklich qualifizieren statt still übernehmen; frische ASDF-Ladung CTM+XTM+Adapter; alle Modellobjekte EQ; Scoped Views und Reifier-/Parent-Navigation aller Item-Arten; keine zweite TMDM-Implementierung.

**Erwarteter zusätzlicher Original-PASS-Gewinn:** 0; ausschließlich Prognose. **Stop:** Stop bei ungeklärter Versions-/Performanceentscheidung, inkompatiblen Strukturen/alten FASLs oder erforderlicher TMDM-Semantikänderung.

### 22L — Lernpfad in realem Workspace und Browser-Integration abnehmen

**Normative Funktion:** Integration/application contract, not a replacement for ISO conformance. **Abhängigkeiten:** 22K; separate HyperDoc application/test authorization.

**Originalverträge:** keine zusätzlichen Originale; gesonderte Profil-/Integrationsprüfungen.

**Codebereiche:** `HyperDoc existing topicmap projection/workspace`; `inspector views and Lisp/browser integration tests`; `versioned application CTM/XTM fixture`. **Modell-/Identitätsabnahme:** Geplantes Lernpfad-Fixture real importieren, native Objekte navigieren, Point/History verfolgen, SI-Alias-Merge mit alten Handles nachweisen, wiederholtes Rendering modellunverändernd, Start aus sauberem gepinntem Build, CTM/XTM Importparität bei bewusst gleichen Identitäten.

**Erwarteter zusätzlicher Original-PASS-Gewinn:** 0; ausschließlich Prognose. **Stop:** Keine Zettel-11326-Abschlussbehauptung ohne A+B+C; UI-Projektion darf kanonische Identität nicht neu erfinden; keine Abnahme allein aus Screenshot oder Testzahl.

Die reguläre XTM-Prognose beträgt damit +52, weitere +2 sind normativ bedingt; maximal +54 würde 124 PASS ergeben. CTM hat keinen zugesagten Implementierungsgewinn; vier negative Qualifikationen wären nur nach ausdrücklichem Entscheid möglich. Die drei positiven Template-Tail-Konflikte und vier bestehenden FAILs lassen sich nicht als reine Restimplementierung behandeln. **397 PASS sind kein garantiert erreichbares Ergebnis ohne Norm-/Profilentscheidungen.** Die Reihenfolge bündelt zusammengehörige Fähigkeiten; XML-anyType und Profilgrenzen sind ein eigener fachlicher Abschlussbedarf mit null Korpusgewinn, keine künstliche Zählstufe.

## HyperDoc: vorhandene Architektur und konkrete Integrationsabnahme

**Nur Quellinspektion:** HyperDoc-HEAD `306b7fd99fc2611a248e0927ce52a808abb7cc76`, Branch `dreyeck.ch`, sauber. Vierzehn gelesene Dateien und SHA-256 stehen in [hyperdoc-source-inspection.json](../reports/slice-22a/hyperdoc-source-inspection.json). Kein HyperDoc-System wurde in 22A geladen, kein UI bedient, kein Integrationstest ausgeführt und keine HyperDoc-Datei geändert. Historische Browser-/Performanceberichte sind Herkunftsevidenz, keine neu reproduzierten Ergebnisse.

Vorhanden sind `dreyeck/inspector/tmdm`, `dreyeck/work/tmdm-reading`, `dreyeck/topic-maps-reading` und `dreyeck/work/project` in `dreyeck.asd` (Zeilen 3167, 3172, 1648, 3188). `dreyeck/src/tmdm-model-navigation.lisp` besitzt spezialisierte Map-/Topic-/Name-Views und echte `object-ref`-Navigation. Die UI-Projektion in `dreyeck/work/topic-maps-reading.lisp` und im Project Workspace bewahrt native TMDM-Ursprungsobjekte. Sie ersetzt kein Identitätsmodell. Zusätzliche spezialisierte Role-/Scope-/Variant-/Occurrence-/Reifier-Views und Provenienzzuordnung für alle Item-Arten sind noch abzusichern; `model-map-of` behandelt derzeit nur Map/Topic/Name.

**Versionsentscheidung:** `dreyeck/work/tmdm-model-reading.lisp:14` nennt `788899aea1a20b9cd8237c6106e6613e180d7362` und akzeptiert geprüfte saubere Nachfolger. `dreyeck/work/project/project-workspace.lisp:12` verlangt dagegen den Performance-Pin `5a4a66850403cdfe2755c6c88083a8e31af89628`. Dessen ein zusätzlicher Commit liegt nicht im aktuellen Konformitätsbranch; gemeinsame Basis `963f2a09444100d37e49cccbd6634879bd6742b5`. Die Abzweigung verändert native TMDM-Merging-/Association-Pfade und Tests. Keine stillschweigende Zusammenführung oder Übernahme eines bewegten Checkouts. Die ASDF-Kommentare nennen Packaging E1 ausdrücklich offen; die Flake pinnt dieses Topic-Maps-Paket noch nicht. Historische Hinweise auf unzureichende CTM-Performance sind kein aktuelles Benchmarkresultat. 22K muss gemeinsame Version, Performance und vollständige Konformitätsregression ausdrücklich qualifizieren.

| Nr. | Vorhanden / noch offen | Konkrete künftige Abnahme |
|---|---|---|
| 1 | Eigenständige native ASDF-Systeme und Adapter existieren; aktuelle Abschlussrevision in HyperDoc ungeprüft | Gepinnte Registry lädt TMDM, CTM, XTM, CXTM und CTM/XTM-Adapter in frischem HyperDoc-Prozess. Packages, Klassen und Symbole sind dieselben; kein zweites Modell. Foundation allein genügt nicht. |
| 2 | Vorhandene CTM-Importpfade; XTM-Anwendungsanbindung offen | Reale CTM- und XTM-Dateien über öffentliche Byte-APIs mit festem Document IRI, Source Key, Encoding und endlichem Resolver importieren; Fehlerklassen und Positionsprovenienz erhalten. |
| 3 | Native Topics/Names/Variants/Occurrences/Associations/Roles/Scope-Referenzen modellseitig vorhanden | Über Integrationsgrenze identische Common-Lisp-Objekte und `canonical-*`/`EQ` nachweisen, keine Label-/JSON-Ersatzidentität. |
| 4 | CLOG Moldable Inspector für Map/Topic/Name vorhanden | Map→Association→Role→Player/Type und Topic→Name→Variant und Topic→Occurrence sowie Scope/Parent/Reifier und inverse Links mit echten `object-ref`-Zielen navigieren; Rendering ändert Modell nicht. |
| 5 | Lernpfad-Anwendung vorgeschlagen, nicht erstellt | Vier Lernschritte: TMDM-Grundlagen, CTM-Import, XTM-Import, Identität/Merging. Vier prerequisite-Associations: Grundlagen→CTM/XTM und CTM/XTM→Merging; Role-Types und Scope-Themes Anfänger/Sprache. Type-/Theme-Topics separat zählen. |
| 6 | Native kanonische Identität modellseitig geprüft; Grenztest offen | Zweiten Import über absichtlich gemeinsame SI/II durchführen. Alte UI-Ursprungsobjekte und native Handles müssen nach `canonical-*` `EQ` zur aktuellen Map sein; normalisierte Names/Variants/Roles und reine CXTM-Kanonisierung erhalten. |
| 7 | Ältere Lisp-/Browsertests vorhanden; Abschlussfall offen | Frische Load-/Import-/Referenztests sowie reale CLOG-Klicks: Lernschritt auswählen, Association/Role inspizieren, Player/Scope/Parent/Reifier erreichen, Workspace Point/History und Rückwege prüfen. Kein Screenshot allein als Nachweis. |
| 8 | Gepinnte Abhängigkeiten teilweise vorhanden; Topic-Maps-Packaging offen | Gemeinsamen Commit und Abhängigkeiten locken, sauberen Build dokumentieren, FASLs bei Layoutänderung neu kompilieren. Performanceabzweig separat qualifizieren oder gemessene Alternative wählen; offline ausführbare Lisp-/Browser-Kommandos und Exitcodes sichern. |

Vorhandene Ansatzpunkte für Tests: `dreyeck/tests/tmdm-model-reading.lisp`, `dreyeck/tests/topic-maps-reading.lisp`, `dreyeck/tests/project-ctm.lisp`, `scripts/test-project-workspace.mjs`. Die Anwendung soll bestehende Workspace-/Topicmap-Projektion und Inspector-Mechanismen erweitern. CTM-/XTM-Anwendungsfixtures verwenden bewusst dieselben absoluten Identitäten und dokumentierte Document-IRI-Verträge; Parität von Modell und CXTM darf erst nach wirklichem Import behauptet werden. Die vier Lernschritte sind keine neuen Korpus-Case-IDs. Dieser Anwendungstest ersetzt keine normative Prüfung.

## Drei getrennte Abnahmetore

**A — Normative Konformität: OFFEN.** Abnahmekriterium: Maßgebliche veröffentlichte Editionen und Errata sind belegt; jede vereinbarte Klausel ist implementiert/geprüft oder eine Ausnahme normativ begründet und ausdrücklich als Profileinschränkung genehmigt. Native TMDM-Invarianten und CXTM-Kanonisierung/Ordnung/NFC/Reinheit sind separat belegt. Offene Editions-, Auslegungs-, Parser-/Encoding- oder XML-Anforderungen schließen eine uneingeschränkte Aussage aus.

**B — Testsuite: OFFEN.** Abnahmekriterium: Alle 397 eindeutigen unveränderten Originale haben einen überprüfbaren, qualifizierten Abschluss. Ziel ohne Ausnahmen: CTM 273/0/0 und XTM 124/0/0. Positive erfordern wirklichen Originalimport, native Prüfung und vollständige CXTM-Byteidentität; negative ihre qualifizierte konkrete Ablehnungsursache. Begründete Baselinekonflikte bleiben FAIL/Testabweichung mit gesondertem ausdrücklichem Abschlussentscheid, niemals künstlicher PASS. Ungeklärte NOT-RUN verhindern pauschale Vollabnahme. Historische Provenienz, Integrität und vollständige Offline-Regression sind erhalten.

**C — HyperDoc-Integration: IN 22A NICHT AUSGEFÜHRT.** Abnahmekriterium: Die geprüfte gepinnte Implementierung besteht die acht obigen Integrationskriterien einschließlich realem Lernpfad-Workspace, nativer Identitätsnavigation und reproduzierbaren Lisp-/Browser-Anwendungstests. Vorhandene ältere Views beweisen noch nicht diese Abnahme.

Erst wenn A, B und C jeweils ausdrücklich abgenommen sind, ist der Gesamtauftrag nach Zettel 11326 abgeschlossen. Ein bewilligtes eingeschränktes Profil muss seine Ausnahmen auch in der abschließenden Aussage nennen.

## Reproduktion und Integrität

Ein einziger neuer Untersuchungswrapper verwendet den bestehenden Harness und dessen Case Records/Serializer, ohne ASDF-/Registrierungsänderung oder zweite Testarchitektur:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 reports/slice-22a/reproduce.py \
  --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  --output /private/tmp/topic-maps-22a-reproduction
```

Ausgabe muss außerhalb des Repositories liegen; der Validator verwendet vorhandene gepinnte Nix-Store-Quellen und kopiert nur bereits qualifizierte Dependency-Patches in temporäre Buildquellen. Er baut keine neuen Downloads oder langlebigen Images ein. Der Default führt alle 109 bestehenden Prozesse und zwei neuen Lisp-Beobachtungsprozesse aus. `--reuse-baseline`/`--reuse-observations` dienen ausschließlich der erneuten Matrix-/Integritätsprüfung einer bereits frisch ausgeführten Evidenz; der neue Wrapperlauf ist nicht mit einem zweiten vollständigen Regressionstest gleichzusetzen. Die tatsächlich verwendeten temporären Pfade, Zeiten, Kommandos und Logs sind im Bericht erhalten; deren Löschung verhindert keine neue Ausführung über den Default.

Auf diesem Host wurden Aufrufe wegen der bekannten Sandbox-Pfadkonfiguration über regulär automatisch freigegebene Ausführung gestartet. Die Testkindprozesse selbst blieben im beschriebenen Netzwerk-/Dateischreibsandbox. Keine Änderung an `~/.nix-profile`, keine Umgehung einer abgelehnten Freigabe und kein verschachtelter Sandboxstart.

Alle 6.024 bei Untersuchungsbeginn verfolgten Dateien blieben bytegleich; darin 3.752 historische Reportdateien. Alle 2.006 Korpus-Lockeinträge wurden einschließlich Größe und SHA-256 geprüft. Originalquellen, CXTM-Baselines, Testregistrierung und Produktionscode blieben unverändert. [initial-state.json](../reports/slice-22a/initial-state.json) und [integrity.json](../reports/slice-22a/integrity.json) bewahren Anfangszustand und vollständige Hashes; [precommit-audit.json](../reports/slice-22a/precommit-audit.json) prüft zusätzlich neue Artefakte, Matrix/Plan und unveränderten HyperDoc-Zustand. [artifacts.json](../reports/slice-22a/artifacts.json) listet SHA-256 der neuen Lieferdateien (Manifest selbst ausgenommen).

Der lokale Commit enthält ausschließlich diesen Plan, die vollständige Matrix, neue Untersuchungswerkzeuge und neue Ausführungsevidenz. Keine Registrierung, kein neuer PASS, keine Produktions-/HyperDoc-/Korpus-/Baseline-/historische Reportänderung; kein Push oder Deployment. Ende Slice 22A.
