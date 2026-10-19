# Slice 20J — Template-Tail-Grammatik und überprüfte Evidenz

Ausgangscommit: `bc04a1657f0b548ec5cdf2862aeed6a1ad0630b8`.
Der registrierte Stand bleibt CTM **262 PASS, 4 FAIL, 7 NOT-RUN** und XTM **6 PASS, 0 FAIL, 118 NOT-RUN**.
Dieser Slice dokumentiert sieben offene Verträge. Er ändert weder Sprache noch Reader, Binding, Modell, Baselines oder Registrierung.

## Herkunft der Aussagen

| Kennzeichnung | Bedeutung | Evidenz |
| --- | --- | --- |
| Beobachtet | Originalbytes, Quellpositionen, aktuelle Conditions, tatsächliche Gegenproben und Regression | Originaldateien; observed-originals.json; observed-controls.json; execution.json |
| Aus der Norm abgeleitet | Ableitbarkeit in der gedruckten Grammatik | Die unten genannten Abschnitte und Produktionsnummern |
| Inferiert | Deutung der Korpusabsicht und des Verwendungskontexts | Quelltext, invalid-Kommentare, Baselines und deren getrennte Gegenproben |
| Hypothesiert | Mögliche Erweiterungsabsicht und zusätzliche Regel eines späteren Modus | Keine historische Bestätigung und keine Implementierung |

Die temporären Slice-20I-Dateien unter reports/slice-20j/slice20i/ sind unveränderte Archive. import.json verzeichnet ihre SHA-256-Werte.
Der Validator prüft sämtliche ursprünglichen 3.519 Datei-Hashes, Quellen, Variablenpositionen und Baselines vor der Übernahme.
Er reproduziert sieben Originalbeobachtungen und zwölf Gegenproben mit dem unveränderten Reader und vergleicht beide Ergebnisse vollständig mit 20I.
Die aktuellen Herkunftskennzeichnungen stehen in current.investigation.json; archivierte Rollennamen beschreiben beabsichtigte Kontexte, keine bereits ausgeführten Identitätsoperationen.

## Normative Fundstellen

Referenz ist die im Auftrag vorgegebene [CTM-Fassung ISO/IEC 13250-6:2010](https://www.isotopicmaps.org/ctm/ctm.html).

| Befund — aus der Norm abgeleitet | Konkrete Fundstelle |
| --- | --- |
| Unmarkierter SI im Tail: [50] → [51] → [52] → [17] → [12]; keine Variable | §3.9 [50]–[52]; §3.3.6 [17]; §3.3.5 [12] |
| Topic-Identität enthält ausdrücklich eine Variable | §3.3.6 [13] |
| Markierte SL- und II-Stellen erlauben Variablen | §3.3.6 [18], [19] |
| Topic-Referenz umfasst Topic-Identität | §3.3.7 [20]; Type §3.3.11 [27]; Player §3.13 [62] |
| Literal enthält eine Variable | §3.4.1 [28] |
| Variablen nur in Templates; Körper aus Topics, Associations und Aufrufen | §3.3.6 und §3.4.1, jeweiliger Variablenabsatz; §3.14 [63]–[67] |
| Positionsbindung und kontextabhängige Substitution | §3.15 [68]–[70], Verarbeitungsschritte und wiki-entry-Beispiel |

Der Topic-Kopf benutzt §3.8 [49] → [13]. Er ist vom zusätzlichen SI im Tail zu unterscheiden. Die Template-Regeln ergänzen dessen fehlende Variablenalternative nicht ausdrücklich.

## Beobachtungen der sieben Originalverträge

Alle Originale enthalten ausschließlich ASCII, führendes und abschließendes LF, keine BOM und keine CR. Offsets sind nullbasiert; Zeile und Spalte einsbasiert.
Die numerische Gleichheit von Byte- und Zeichenoffsets ist hier eine Eigenschaft dieser konkreten Quellen.
Alle sieben tatsächlichen Conditions sind **INVALID-TEMPLATE-BODY**, Code **template-identity-tail**, Einheit **character**, Cause **NIL**, Context **NIL**.
Kein Original liefert eine Map oder CXTM-Ausgabe. Kein Originalvergleich wird als bestanden bezeichnet. Sämtliche Case Records bleiben NOT-RUN.

### 1. ctm/in/template-ambiguous-parameter5.ctm

[Originalquelle](../vendor/cxtm/ctm/in/template-ambiguous-parameter5.ctm) — 146 Bytes.
SHA-256: `5a4310d6f077776996700a77cd037ca30b1b616f7235128f9500ef16c5cd78a8`.

Beobachtete Originalquelle (einschließlich der führenden Leerzeile):
```ctm

# Using an IRI argument in different contexts

def template($iri)
  topic $iri; =$iri; ^$iri.
end

template(<http://www.example.org/something/>)

```

Beobachtete Variablenpositionen; Rollen außerhalb der Parameterdeklaration sind aus dem Quellkontext inferiert:

| Variable | Offset | Zeile:Spalte | Rolle |
| --- | ---: | --- | --- |
| `$iri` | 61 | 4:14 | Parameterdeklaration |
| `$iri` | 75 | 5:9 | Subject Identifier im Topic Tail (unmarkiert) |
| `$iri` | 82 | 5:16 | Subject Locator nach = |
| `$iri` | 89 | 5:23 | Item Identifier nach ^ |

Positionsbindung: `$iri` ← `<http://www.example.org/something/>`.
Beobachtete Zurückweisung: Zeichen **79**, **5:13**.
Sie erfolgt während der Definitionsprüfung nach der ersten unmarkierten Tail-Variablen, am folgenden Punkt beziehungsweise Semikolon. Der Aufruf wird nicht erreicht.

[Unveränderte Baseline](../vendor/cxtm/ctm/baseline/template-ambiguous-parameter5.ctm.cxtm) — 353 Bytes.
SHA-256: `a90bb867d36b9d99061d3815c6ce41a1cd4d8909c49adc7ce9cc1c9bfe06303f`.

Ausgeschriebene Gegenprobe — keine Ausführung des Originaltemplates:
```ctm
topic <http://www.example.org/something/>; =<http://www.example.org/something/>; ^<http://www.example.org/something/>.
```

Beobachtet: **353/353 Bytes identisch**.
Die Gegenprobe benutzt die ursprüngliche Document IRI. Referenzen bleiben aktuell und die Kanonisierung verändert die gehaltenen Objekte nicht.
Baseline und Gegenprobe stehen vollständig im maschinenlesbaren Fallbericht; die Original-CXTM-Ausgabe bleibt nicht vorhanden.
Beobachteter Baseline-Graph: ein Topic mit SI, SL und II http://www.example.org/something/ sowie lokalem II #topic; keine Associations.
Inferiert: Die positive Korpuserwartung benötigt die zusätzliche Zulässigkeit dieses SI-Slots. Der bereits reproduzierbare Ergebnisgraph belegt diese Zulässigkeit nicht.

### 2. ctm/in/template-ambiguous-parameter6.ctm

[Originalquelle](../vendor/cxtm/ctm/in/template-ambiguous-parameter6.ctm) — 163 Bytes.
SHA-256: `d2fd507bbbd544b6eae6caf4497c18e746165a5868a1d8e644eb18815db44d50`.

Beobachtete Originalquelle (einschließlich der führenden Leerzeile):
```ctm

%prefix ex <http://www.example.org/>

# Using a QName argument in different contexts

def template($q)
  topic $q; =$q; ^$q; occ: $q.
end

template(ex:something)

```

Beobachtete Variablenpositionen; Rollen außerhalb der Parameterdeklaration sind aus dem Quellkontext inferiert:

| Variable | Offset | Zeile:Spalte | Rolle |
| --- | ---: | --- | --- |
| `$q` | 100 | 6:14 | Parameterdeklaration |
| `$q` | 112 | 7:9 | Subject Identifier im Topic Tail (unmarkiert) |
| `$q` | 117 | 7:14 | Subject Locator nach = |
| `$q` | 122 | 7:19 | Item Identifier nach ^ |
| `$q` | 131 | 7:28 | Occurrence-Literal; Datentyp xsd:anyURI |

Positionsbindung: `$q` ← `ex:something → http://www.example.org/something`.
Beobachtete Zurückweisung: Zeichen **114**, **7:11**.
Sie erfolgt während der Definitionsprüfung nach der ersten unmarkierten Tail-Variablen, am folgenden Punkt beziehungsweise Semikolon. Der Aufruf wird nicht erreicht.

[Unveränderte Baseline](../vendor/cxtm/ctm/baseline/template-ambiguous-parameter6.ctm.cxtm) — 613 Bytes.
SHA-256: `3b20e3168ad1260c2a4fcb2b5b4b0026324a78263f2431d6637473087eecd672`.

Ausgeschriebene Gegenprobe — keine Ausführung des Originaltemplates:
```ctm
%prefix ex <http://www.example.org/> topic ex:something; =ex:something; ^ex:something; occ: ex:something.
```

Beobachtet: **613/613 Bytes identisch**.
Die Gegenprobe benutzt die ursprüngliche Document IRI. Referenzen bleiben aktuell und die Kanonisierung verändert die gehaltenen Objekte nicht.
Baseline und Gegenprobe stehen vollständig im maschinenlesbaren Fallbericht; die Original-CXTM-Ausgabe bleibt nicht vorhanden.
Beobachteter Baseline-Graph: zwei Topics; SI/SL/II http://www.example.org/something und lokaler II #topic; Occurrence mit diesem Wert, Datentyp xsd:anyURI und Type #occ. Das QName wird über den ursprünglichen ex-Präfix aufgelöst.
Inferiert: Die positive Korpuserwartung benötigt die zusätzliche Zulässigkeit dieses SI-Slots. Der bereits reproduzierbare Ergebnisgraph belegt diese Zulässigkeit nicht.

### 3. ctm/in/template-subject-identifier2.ctm

[Originalquelle](../vendor/cxtm/ctm/in/template-subject-identifier2.ctm) — 81 Bytes.
SHA-256: `ffc9a5554b9c908386f6888ef29ccda5cc433e5519924db52f9441769e1df014`.

Beobachtete Originalquelle (einschließlich der führenden Leerzeile):
```ctm

def template($iri)
    topic $iri.
end

template(<http://psi.example.org/fake>)

```

Beobachtete Variablenpositionen; Rollen außerhalb der Parameterdeklaration sind aus dem Quellkontext inferiert:

| Variable | Offset | Zeile:Spalte | Rolle |
| --- | ---: | --- | --- |
| `$iri` | 14 | 2:14 | Parameterdeklaration |
| `$iri` | 30 | 3:11 | Subject Identifier im Topic Tail (unmarkiert) |

Positionsbindung: `$iri` ← `<http://psi.example.org/fake>`.
Beobachtete Zurückweisung: Zeichen **34**, **3:15**.
Sie erfolgt während der Definitionsprüfung nach der ersten unmarkierten Tail-Variablen, am folgenden Punkt beziehungsweise Semikolon. Der Aufruf wird nicht erreicht.

[Unveränderte Baseline](../vendor/cxtm/ctm/baseline/template-subject-identifier2.ctm.cxtm) — 204 Bytes.
SHA-256: `e138a02738dc4a2526c465b11fa6915bed84724a31748eb3578ddf0f8ab16253`.

Ausgeschriebene Gegenprobe — keine Ausführung des Originaltemplates:
```ctm
topic <http://psi.example.org/fake>.
```

Beobachtet: **204/204 Bytes identisch**.
Die Gegenprobe benutzt die ursprüngliche Document IRI. Referenzen bleiben aktuell und die Kanonisierung verändert die gehaltenen Objekte nicht.
Baseline und Gegenprobe stehen vollständig im maschinenlesbaren Fallbericht; die Original-CXTM-Ausgabe bleibt nicht vorhanden.
Beobachteter Baseline-Graph: ein Topic mit SI http://psi.example.org/fake und lokalem II #topic; keine Associations.
Inferiert: Die positive Korpuserwartung benötigt die zusätzliche Zulässigkeit dieses SI-Slots. Der bereits reproduzierbare Ergebnisgraph belegt diese Zulässigkeit nicht.

### 4. ctm/invalid/template-item-identifier-2nd-arg.ctm

[Originalquelle](../vendor/cxtm/ctm/invalid/template-item-identifier-2nd-arg.ctm) — 167 Bytes.
SHA-256: `ceb46d4457532cc5b432d5e601275cc6950bb105088e2b2ccfa4ffa5fbe82266`.

Beobachtete Originalquelle (einschließlich der führenden Leerzeile):
```ctm

def template($iri1, $iri2)
    topic1 $iri1.
    topic2 $iri2.
end

template(<http://www.example.org/>,     # valid
        ^<http://www.example.org/>)     # invalid

```

Beobachtete Variablenpositionen; Rollen außerhalb der Parameterdeklaration sind aus dem Quellkontext inferiert:

| Variable | Offset | Zeile:Spalte | Rolle |
| --- | ---: | --- | --- |
| `$iri1` | 14 | 2:14 | Parameterdeklaration |
| `$iri2` | 21 | 2:21 | Parameterdeklaration |
| `$iri1` | 39 | 3:12 | Subject Identifier von topic1 (unmarkiert) |
| `$iri2` | 57 | 4:12 | Subject Identifier von topic2 (unmarkiert) |

Positionsbindung: `$iri1` ← `<http://www.example.org/>`; `$iri2` ← `^<http://www.example.org/>`.
Beobachtete Zurückweisung: Zeichen **44**, **3:17**.
Sie erfolgt während der Definitionsprüfung nach der ersten unmarkierten Tail-Variablen, am folgenden Punkt beziehungsweise Semikolon. Der Aufruf wird nicht erreicht.

Keine CXTM-Baseline: negativer Originalvertrag.
Inferierte beabsichtigte Prüfung: Argument 2 / $iri2 trägt `^` und soll im unmarkierten SI-Verwendungskontext zurückgewiesen werden.
Beide Originalkommentare kennzeichnen Argument 1 als valid und Argument 2 als invalid. Die Definitionssperre tritt bereits beim ersten Body-Statement ein.
Beobachtet: Dieser Argumentfehler wird nicht geprüft. Die frühe Zurückweisung allein ist kein Nachweis der vorgesehenen kontextabhängigen Ablehnung.

### 5. ctm/invalid/template-item-identifier3.ctm

[Originalquelle](../vendor/cxtm/ctm/invalid/template-item-identifier3.ctm) — 78 Bytes.
SHA-256: `4c7ed0ab1574462b8939379f745a28942aa380fc6cc7fabae597fdc7bb21225f`.

Beobachtete Originalquelle (einschließlich der führenden Leerzeile):
```ctm

def template($iri)
    topic $iri.
end

template(^<http://www.example.org/>)

```

Beobachtete Variablenpositionen; Rollen außerhalb der Parameterdeklaration sind aus dem Quellkontext inferiert:

| Variable | Offset | Zeile:Spalte | Rolle |
| --- | ---: | --- | --- |
| `$iri` | 14 | 2:14 | Parameterdeklaration |
| `$iri` | 30 | 3:11 | Subject Identifier von topic (unmarkiert) |

Positionsbindung: `$iri` ← `^<http://www.example.org/>`.
Beobachtete Zurückweisung: Zeichen **34**, **3:15**.
Sie erfolgt während der Definitionsprüfung nach der ersten unmarkierten Tail-Variablen, am folgenden Punkt beziehungsweise Semikolon. Der Aufruf wird nicht erreicht.

Keine CXTM-Baseline: negativer Originalvertrag.
Inferierte beabsichtigte Prüfung: Argument 1 / $iri trägt `^` und soll im unmarkierten SI-Verwendungskontext zurückgewiesen werden.
Die Absicht wird aus invalid-Kategorie, Argumentmarker und dem ansonsten gleichen Template-Körper inferiert.
Beobachtet: Dieser Argumentfehler wird nicht geprüft. Die frühe Zurückweisung allein ist kein Nachweis der vorgesehenen kontextabhängigen Ablehnung.

### 6. ctm/invalid/template-subject-locator-2nd-arg.ctm

[Originalquelle](../vendor/cxtm/ctm/invalid/template-subject-locator-2nd-arg.ctm) — 167 Bytes.
SHA-256: `e7e8ca08ad1dec89549afbe2d3cf90098269031f239ddae37258bf87ba4c018f`.

Beobachtete Originalquelle (einschließlich der führenden Leerzeile):
```ctm

def template($iri1, $iri2)
    topic1 $iri1.
    topic2 $iri2.
end

template(<http://www.example.org/>,     # valid
         =<http://www.example.org/>)    # invalid

```

Beobachtete Variablenpositionen; Rollen außerhalb der Parameterdeklaration sind aus dem Quellkontext inferiert:

| Variable | Offset | Zeile:Spalte | Rolle |
| --- | ---: | --- | --- |
| `$iri1` | 14 | 2:14 | Parameterdeklaration |
| `$iri2` | 21 | 2:21 | Parameterdeklaration |
| `$iri1` | 39 | 3:12 | Subject Identifier von topic1 (unmarkiert) |
| `$iri2` | 57 | 4:12 | Subject Identifier von topic2 (unmarkiert) |

Positionsbindung: `$iri1` ← `<http://www.example.org/>`; `$iri2` ← `=<http://www.example.org/>`.
Beobachtete Zurückweisung: Zeichen **44**, **3:17**.
Sie erfolgt während der Definitionsprüfung nach der ersten unmarkierten Tail-Variablen, am folgenden Punkt beziehungsweise Semikolon. Der Aufruf wird nicht erreicht.

Keine CXTM-Baseline: negativer Originalvertrag.
Inferierte beabsichtigte Prüfung: Argument 2 / $iri2 trägt `=` und soll im unmarkierten SI-Verwendungskontext zurückgewiesen werden.
Beide Originalkommentare kennzeichnen Argument 1 als valid und Argument 2 als invalid. Die Definitionssperre tritt bereits beim ersten Body-Statement ein.
Beobachtet: Dieser Argumentfehler wird nicht geprüft. Die frühe Zurückweisung allein ist kein Nachweis der vorgesehenen kontextabhängigen Ablehnung.

### 7. ctm/invalid/template-subject-locator3.ctm

[Originalquelle](../vendor/cxtm/ctm/invalid/template-subject-locator3.ctm) — 78 Bytes.
SHA-256: `d53c835df922469d65e5103f48b38faa94be56c06a4cb1da356a8ad6b277496d`.

Beobachtete Originalquelle (einschließlich der führenden Leerzeile):
```ctm

def template($iri)
    topic $iri.
end

template(=<http://www.example.org/>)

```

Beobachtete Variablenpositionen; Rollen außerhalb der Parameterdeklaration sind aus dem Quellkontext inferiert:

| Variable | Offset | Zeile:Spalte | Rolle |
| --- | ---: | --- | --- |
| `$iri` | 14 | 2:14 | Parameterdeklaration |
| `$iri` | 30 | 3:11 | Subject Identifier von topic (unmarkiert) |

Positionsbindung: `$iri` ← `=<http://www.example.org/>`.
Beobachtete Zurückweisung: Zeichen **34**, **3:15**.
Sie erfolgt während der Definitionsprüfung nach der ersten unmarkierten Tail-Variablen, am folgenden Punkt beziehungsweise Semikolon. Der Aufruf wird nicht erreicht.

Keine CXTM-Baseline: negativer Originalvertrag.
Inferierte beabsichtigte Prüfung: Argument 1 / $iri trägt `=` und soll im unmarkierten SI-Verwendungskontext zurückgewiesen werden.
Die Absicht wird aus invalid-Kategorie, Argumentmarker und dem ansonsten gleichen Template-Körper inferiert.
Beobachtet: Dieser Argumentfehler wird nicht geprüft. Die frühe Zurückweisung allein ist kein Nachweis der vorgesehenen kontextabhängigen Ablehnung.

## Einordnung ohne pauschales Korpusurteil

**A/B/C/D sind aspektbezogen:** A kennzeichnet ausdrücklich zugelassene Teilformen. B betrifft die fehlende Ableitung des unmarkierten Tail-Slots. C lässt eine unbelegte Auslassung oder Erweiterung offen. D betrifft bei den drei positiven Fällen nur die zusätzliche Zulässigkeitserwartung, nicht einen nachgewiesenen Fehler der Baseline-Werte.

Beobachtete Gegenproben zeigen schon vorhandene Unterstützung für Topic-Kopf-Variablen mit IRI, II und SL sowie Variablen als Association-/Role-Type, Player und Literal.
II-/SL-Argumente scheitern in Literal- oder expliziten IRI-Slots mit INVALID-TEMPLATE-ARGUMENT und vorhandenem Aufrufkontext.
Der gleiche unmarkierte Tail wird auch ganz ohne Aufruf zurückgewiesen. Diese Gegenproben sind keine neuen Konformitätsverträge.

## Zusätzliche Regel eines möglichen späteren Modus — Hypothese

Ein gesondert beauftragter Modus müsste innerhalb des Subject-Identifier-Zweigs von [52] im Template-Tail eine zusätzliche Regel festlegen:

```text
template-tail-subject-identifier ::= iri-ref | variable
```

Dies ist ein hypothetischer Entwurf für die beobachtete Korpuserwartung, keine Aussage über eine historisch nachgewiesene Absicht.
Die Variable müsste ein IRI-Referenzargument tragen: eine IRI oder ein im Aufrufkontext aufgelöstes QName.
Der Locator würde als zusätzlicher SI des bestehenden Owner-Topics benutzt.
Markierte II-/SL-Argumente, bloße Topic-Argumente und Literalargumente würden diesen Slot nicht erfüllen; Marker dürften nicht entfernt und Topic-Identifier nicht ersatzweise als IRI ausgewählt werden.
Die normale Verwendung einer Variable als Topic-Kopf, Type, Player oder Literal bliebe davon getrennt.
Das ist insbesondere keine beliebige textuelle Substitution, die einen SI-Slot durch Einsetzen von ^ oder = in einen anderen Identitätstyp verwandelt.

Inferiert aus dem aktuellen Code: Eine spätere Umsetzung müsste sowohl die Definitionsprüfung als auch den Ausführungskontext unterscheiden.
Beobachtete Quellstellen: [syntax-tail, templates.lisp:240](../src/ctm/templates.lisp), [read-identity-tail, reader.lisp:242](../src/ctm/reader.lisp), [bound-identity, templates.lisp:68](../src/ctm/templates.lisp), [read-template-invocation, templates.lisp:107](../src/ctm/templates.lisp).
Dieser Slice ändert keine dieser Operationen.

## Historische Aussagegrenze

Beobachtet: [STATUS.txt](../vendor/cxtm/ctm/STATUS.txt) nennt den Entwurf 2010-03-31.
[Der Projektindex](https://www.isotopicmaps.org/ctm/) verlinkt dieselbe Referenz-URL als Entwurf dieses Datums.
Ein separater datierter Normvergleich ist nicht vorhanden. Eine spätere Normänderung oder eine bewusste Erweiterungsabsicht ist deshalb **Hypothese, nicht Befund**.

## Regression und Reproduktion

Die neue Datei reports/slice-20j/reproduce.py ist ein Evidenztreiber; sie fügt weder ein ASDF-Testsystem noch Case-Registrierungen hinzu.

```sh
python3 reports/slice-20j/reproduce.py \
  --sbcl /nix/store/hlsiblxpxr1hax3dw9x8znd6zy097ddj-sbcl-2.5.4/bin/sbcl \
  --output reports/slice-20j-rerun
```

Der bestehende Offline-Testlauf bleibt unverändert: TMDM, CTM/CXTM, Include/Mergemap, XML, XTM, XTM-Mergemap, alle bisherigen Slice-20-Tests, Python-Tests und NFC-Oracle.
Die lokalen gepinnten Store-Quellen werden mit dem bestehenden XML-Verifizierer geprüft und dessen unveränderte Patches ausschließlich temporär angewandt. Es gibt keine Downloads.
Jeder Prozess hat eine Netzwerksperre; die zusätzliche Beobachtungsphase hat außerdem eine Repository-Schreibsperre und schreibt nur temporär.

Die Abnahme verlangt 12.100 bisherige Lisp-Prüfungen; XML 146; XTM 327; XTM-Mergemap 217; Slice 20A 286, 20B 25, Prolog 171, empty2 13, CTM-Integer 112, Triple Strings 226 und Encoding 722; Python 2 und NFC 16.294.
Alle erneut erzeugten Stufenberichte einschließlich finalem CTM/CXTM/Encoding-Bericht müssen JSON-inhaltlich exakt mit Slice 20H übereinstimmen.
Sämtliche 273 CTM-Case-Records und die vier bekannten FAIL-Ausgaben bleiben dadurch erhalten.
Die Abnahme prüft zusätzlich alle 2.006 gepinnten Dateigrößen und SHA-256-Werte, sämtliche bisherigen getrackten Dateien und historischen Berichte.

Die Ergebnisse stehen unter [reports/slice-20j](../reports/slice-20j): current.investigation.json trennt Herkunft und Beobachtung, execution.json enthält Befehle und Rückgabecodes, integrity.json die Hashnachweise. Es erfolgt kein vollständiger Nix-Neubau und kein Laden langlebiger Lisp-Images.
