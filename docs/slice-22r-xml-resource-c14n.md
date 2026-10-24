# Slice 22R — geschlossene XML-/C14N-Infrastruktur

## Auftrag und Ausgangszustand

Basis `0cb182ebab1b90dd871048c031612acd9d302678` (22Q), Parent
`1418be83ad013fe6d69e6036e6786be8100b9355`; Arbeitsbaum und Index waren sauber.
Arbeitsbranch: `codex/xtm-slice-22r`.
[Anfangszustand mit Quellenhashes](../reports/slice-22r/initial-state.json).

Implementiert wird ausschließlich die zusätzliche XML-Infrastruktur für XTM
§4.16.3. Der XTM-Reader bleibt unverändert; insbesondere wird `xsd:anyType`
weiterhin nicht vom Reader verarbeitet. Kein neuer Originalvertrag wird registriert.
Die drei XTM-Dispositionen aus [22O](slice-22o-qualified-xtm-corpus-disposition.md)
und die offenen Abnahmetore A/B/C werden dadurch nicht abgeschlossen.

## Quellen und abgegrenzter Normvertrag

Referenzen: [XTM §4.16.3](https://www.isotopicmaps.org/sam/sam-xtm/)
und [W3C Canonical XML 1.0, 15.03.2001](https://www.w3.org/TR/2001/REC-xml-c14n-20010315),
§§2.1–2.4, 3.2, 3.3, 3.6 und 4.2.
Die öffentliche XTM-Referenz bezeichnet die offizielle ISO-Ausgabe als maßgeblich.
Eine unabhängige Gegenprüfung an den offiziellen ISO-Ausgaben bleibt ausstehend.

**Aus den Referenzen abgeleitet:** XTM wählt die Elemente, Attribute und Zeichen
unterhalb von `resourceData`, ohne den Container. Namespace-Paare werden nach
Verwendung von URI **und** Prefix im gesamten ausgewählten Knotensatz gefiltert;
QName-artige Attributwerte zählen nicht. PI und Kommentare werden ausgelassen.
C14N 1.0 erhält ursprüngliche QNames, ordnet Namespaces nach Prefix und Attribute
nach Namespace-URI/Lokalname, expandiert leere Elemente und unterscheidet Text-
von Attribut-Escapes. Am ausgewählten Apex werden die nächsten geerbten
`xml:*`-Attribute ergänzt. Relative Namespace-URIs sind ein Fehler. Ausgabe ist
UTF-8 ohne BOM und der entsprechende Unicode-String. Es erfolgt keine
Normalisierung UCS-basierter Zeichenfolgen. Die Sonderregeln von C14N 1.1
für `xml:id`/`xml:base` gelten hier nicht.

Dies ist eine begrenzte Implementierung des XTM-Knotensatzes im bestehenden
**DOCTYPE-freien XML-Profil**, keine allgemeine XPath-C14N-Bibliothek.
DTD-Defaultattribute und externe Entities werden nicht nachgeladen. Exclusive
C14N und C14N 1.1 werden weder verwendet noch als austauschbar behandelt.
Die optionalen Parser-Encodings außerhalb des unten geprüften Eingabeprofils
werden durch diese Qualifikation nicht zusätzlich zugesichert.

## Implementierung und öffentliche Schnittstelle

Die vorhandenen gepinnten Komponenten wurden in 22Q geprüft: Der CXML-Sink
implementiert eine ältere CanonXML-Form und ist kein W3C-C14N-1.0-Ersatz.
Der DOM-Builder kann den nötigen Kontext dagegen erhalten. Deshalb wird die
im Auftrag ausdrücklich erlaubte eigene, begrenzte Implementierung verwendet.
Es gibt keine neue externe Abhängigkeit.

- [resource-c14n.lisp](../src/xml/resource-c14n.lisp): zusätzliche Parseranbindung,
  Namespace-Achsen, Knotenauswahl und Kanonisierung.
- [package.lisp](../src/xml/package.lisp): zusätzliche öffentliche Symbole.
- [topic-maps.asd](../topic-maps.asd): bestehendes XML-System und regulärer
  XTM-ASDF-Testlauf laden die Komponenten.
- [Dauerhafte Tests](../tests/xml-resource-c14n.lisp), Aufruf und Berichtsfeld in
  [xtm-identity.lisp](../tests/xtm-identity.lisp).

```lisp
(let ((context (topic-maps.xml:parse-canonical-context original-octets)))
  (topic-maps.xml:resource-data-count context)
  (multiple-value-bind (value utf8-octets)
      (topic-maps.xml:canonicalize-resource-data context :index 0)
    (values value utf8-octets)))
```

Der opake Kontext hält ein privates DOM des **gesamten Originaldokuments**.
`index` ist nullbasiert; Auswahl erfolgt nach erweitertem Namen und Dokumentreihenfolge.
Der Einstieg validiert keine XTM-Grammatik, entscheidet keinen Datentyp und
führt keine TMDM-Operation aus. Ein fehlender Index signalisiert
`CANONICALIZATION-ERROR/:resource-data-index`; relative Namespace-URIs
`CANONICALIZATION-ERROR/:relative-namespace-uri`.
Die Ausgabe darf leer, reiner Text oder ein Fragment mit mehreren Apex-Elementen sein.

`parse-octets` in [parser.lisp](../src/xml/parser.lisp) bleibt byteidentisch.
Die zusätzlichen SAX-Einstellungen sind dynamisch gebunden; Namespace-Deklarationen
und Original-Prefixe werden nur im neuen Einstieg erhalten. Qualification-Marker,
`closed-handler`, frischer DTD-Cache, abgeschalteter Katalog und der niemals
normal zurückkehrende Ressourcenverweigerer bleiben wirksam. Globale Parser-
Einstellungen und übergebene Eingabebytes bleiben unverändert.

## Tatsächliche Byteergebnisse

Die vollständigen Eingabe-, Soll- und Ist-Bytes stehen als Hex sowie als String
im Feld `resourceDataC14N` von [xtm.json](../reports/slice-22r/after/xtm.json).
[Vergleichsübersicht](../reports/slice-22r/after/comparison-summary.json).
Jede der 18 22Q-Eingaben **und** Soll-Bytefolgen wird unverändert wiederverwendet:

| Gegenprobe aus 22Q | Ist / Soll (Bytes) | Ergebnis |
| --- | ---: | --- |
| simple | 12 / 12 | identisch |
| attributes-ba | 19 / 19 | identisch |
| attributes-ab | 19 / 19 | identisch |
| inherited-prefix | 28 / 28 | identisch |
| unused-local-namespace | 28 / 28 | identisch |
| inherited-default | 28 / 28 | identisch |
| nested | 42 / 42 | identisch |
| escaping | 66 / 66 | identisch |
| whitespace-line-endings | 17 / 17 | identisch |
| comments | 9 / 9 | identisch |
| lexical-cdata | 27 / 27 | identisch |
| lexical-escaped | 27 / 27 | identisch |
| unicode | 23 / 23 | identisch |
| processing-instruction | 9 / 9 | identisch |
| namespace-attribute-order | 65 / 65 | identisch |
| redundant-binding | 38 / 38 | identisch |
| unicode/UTF-16LE | 23 / 23 | identisch |
| unicode/UTF-16BE | 23 / 23 | identisch |

Zusätzlich bestehen Prefix-Shadowing, Default-Namespace-Wechsel, globale
Namespace-Verwendung, gleiche URI mit verschiedenen Prefixen, gefilterte
Namespace-Lücken, geerbtes/überschriebenes `xml:lang`/`xml:space`, C14N-1.0-
Behandlung von `xml:base`/`xml:id`, leere Inhalte/CDATA, reiner Text, mehrere
Apex-Elemente, Attributordnung und Zeichenreferenzen, dekomponierter UTF-8-Text
sowie U+FEFF im Inhalt. Keine Sollwerte wurden aus Ist-Ausgaben übernommen.

**Unabhängige normative Vektoren:** W3C §3.2 (169/169 Bytes), §3.3 ausschließlich
sein eigenständiges `e5`-Element samt veröffentlichter Ausgabe (146/146), §3.6
(ISO-8859-1-Deklaration, Zeichenreferenz und veröffentlichte UTF-8-Ausgabe,
13/13). Zwei vollständige Beispiele und ein ausdrücklich benannter Teilvektor.
Sie laufen zunächst ohne XTM-Hülle durch dieselbe interne Engine und zusätzlich
mit eingefügter `resourceData`-Hülle durch die **öffentliche** API; dabei bleibt
die unabhängige Soll-Ausgabe unverändert. Die Hülle und das Entfernen von
Prolog-Leerraum außerhalb des Dokumentelements sind in jeder Zeile ausgewiesen.
Die Vektoren sind aus den veröffentlichten XML-Beispielen transkribiert,
keine zusätzlich heruntergeladenen Testdateien. Darstellungsabstände in §3.2
werden als U+0020 wiedergegeben. Diese Vektoren benutzen alle ihre Namespace-Bindungen; XTM-Filterung verändert
deren normative Auswahl deshalb nicht.

Die DTD-enthaltenden vollständigen Beispiele §§3.1, 3.3, 3.4, 3.5 und 3.7 wurden
nicht als durchlaufen ausgegeben. Insbesondere wird weder beliebige XPath-Auswahl
noch DTD-/Entity-Unterstützung behauptet.

Qualifizierte Byte-Gegenproben decken UTF-8 mit/ohne BOM, UTF-16LE/BE mit BOM,
deklariertes UTF-16LE/BE ohne BOM und ISO-8859-1 ab. Wiederholte Ausgabe ist
identisch und verändert weder Eingabebytes noch DOM. Die alte Charakterisierung
`c14nPreflight` bleibt exakt wie 22Q: zehn passende und acht abweichende Zeilen.
Sie wird nicht nachträglich zum positiven C14N-Nachweis umgedeutet.

## Sicherheits- und Modellnachweise

Gespeicherte konkrete Conditions: fünfmal `DOCTYPE-FORBIDDEN` (inklusive interner
und externer Deklarationen), XML-Struktur-/Namespacefehler und ungültiges UTF-8
als `WELL-FORMEDNESS-VIOLATION`, fehlende Qualification-Marker beider Komponenten
als `UNQUALIFIED-PARSER`, verweigerte File-/HTTP-Ressourcen als
`EXTERNAL-RESOURCE-FORBIDDEN`, relative Namespaces als `CANONICALIZATION-ERROR`.
Die tatsächlichen Parserargumente werden geprüft; ein NIL-Rückfall auf implizites
OPEN ist ausgeschlossen. Tests prüfen außerdem unveränderte globale Einstellungen,
explizite Übersteuerung ungeeigneter Ambient-Einstellungen, Auswahl nach Namespace
und Dokumentreihenfolge sowie die unveränderte alte XML-Bytegrenze.

Alle 41 durch die öffentliche API erzeugten Werte werden über `add-occurrence`
und `add-variant` gespeichert und verlustfrei gelesen: Wert und `xsd:anyType`,
kanonische Parent-/Type-/Scope-EQ-Referenzen, genau fünf bewusst erzeugte Topics,
wiederholte identische CXTM-Ausgabe und unveränderter Modellzustand.
Keine Topics entstehen aus XML-Namen oder Datentyp-IRIs. Diese nativen Prüfungen
sind Infrastruktur-/Modelltests, keine Ausführung eines XTM-anyType-Originalvertrags.

## Offline-Regression, Integrität und Reproduktion

[Reproduktion](../reports/slice-22r/reproduce.py) verwendet den bestehenden
unveränderten `validate-slice-22d.py::collect`; Abhängigkeiten stammen aus lokalen
Pins mit den vorhandenen 19D0B-Patches. Jeder Lisp-Prozess startet SBCL 2.5.4
ohne Benutzer-/Systeminitialisierung. `sandbox-exec` sperrt Netzwerk und Schreibzugriff
auf Topic-Maps- und HyperDoc-Repository. Logs, Kommandos, Laufzeiten und Hashes
stehen in [runs.json](../reports/slice-22r/after/runs.json).

Der vollständige Abschlussaudit steht in
[execution.json](../reports/slice-22r/after/execution.json), die 113 erwarteten
Fehlerausgänge in [failure-controls-audit.json](../reports/slice-22r/after/failure-controls-audit.json).
Diese Kontrollausgänge werden nicht als erfolgreiche Originalverträge gezählt;
alle bisherigen Felder und Conditions bleiben identisch. Kein Retargeting.

Der reguläre XTM-Lauf führt 4.123 Checks aus: 3.844 erhaltene und 279 neue.
44 positive Bytevergleichszeilen, darunter 18 unveränderte 22Q-Zeilen und die
sechs unabhängigen W3C-/Hüllen-Zeilen; 41 native Wertprüfungen.
Erhalten bleiben 12.100 Kernchecks, 146 XML-Qualifikationschecks, sämtliche
Slice-20-Prüfungen, CTM/XTM-Mergemap und Äquivalenz (30 tatsächliche Reader-Paare,
529 Checks, drei Kontraste), Python (zwei Tests) und NFC-Oracle (16.294 Vergleiche).
Alle 124 XTM-Originaldiagnosen und sämtliche bisherigen Case Records bleiben unverändert.
46 erneut erzeugte Berichte sind byteidentisch zum gespeicherten 22Q-Stand.

| Registrierter Korpus | PASS | FAIL | NOT-RUN |
| --- | ---: | ---: | ---: |
| XTM 2.0 | 121 | 0 | 3 |
| CTM | 262 | 4 | 7 |

[Integritätsnachweis](../reports/slice-22r/after/integrity.json) prüft alle
unveränderten Basisdateien einschließlich gepinnter Originale/Baselines und aller
historischen Berichte: 10.957 geschützte Basisdateien, darunter 2.006 gepinnte
Korpusdateien und 8.645 historische Reportdateien. TMDM-, CTM-, XTM-Reader- und CXTM-Quellen bleiben unverändert.
Die vier bekannten CTM-FAILs und die offenen Fragen aus 22O bleiben sichtbar.

```sh
python3 reports/slice-22r/reproduce.py --output /private/tmp/topic-maps-22r-new
python3 reports/slice-22r/reproduce.py --output /private/tmp/topic-maps-22r-new --audit-only
```

Die zweite Zeile auditiert gespeicherte Ausführung und wird nicht als neuer
Testlauf ausgegeben. Frühere fehlgeschlagene Entwicklungsanläufe sind unter
[attempts/index.json](../reports/slice-22r/attempts/index.json) erhalten.
Die ersten drei scheiterten an Entwicklungsfehlern (String-Konstanten,
Testquellklammer, doppelte Check-Bezeichnung). Ein erster Gesamtlauf hatte alle
119 erwarteten Exit-Codes, scheiterte aber am irrtümlich angenommenen
Gesamtsummen-Logmarker im neuen Auditor. Dieser wurde durch die 24 tatsächlichen
Kernmarker ersetzt. Der abschließende Gesamtlauf verwendet die korrigierten
Quellen und eine zusätzlich präzisierte UTF-8-Condition-Prüfung. Kein Eingriff in `~/.nix-profile` oder
Sandbox-Konfiguration, keine neue Abhängigkeit, Reader-Integration oder Arbeit
an HyperDoc/langlebigen Images. Nach dem lokalen Commit endet Slice 22R.
