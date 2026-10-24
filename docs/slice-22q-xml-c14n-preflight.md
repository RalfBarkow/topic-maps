# Slice 22Q — XML/C14N-Vorabnachweis für XTM §4.16.3

Stand: 24. Oktober 2026 (Europe/Zurich). Ausgangscommit und Commit-Parent:
`1418be83ad013fe6d69e6036e6786be8100b9355`.
Arbeitsbranch `codex/xtm-slice-22q`; zu Beginn sauberer Index/Arbeitsbaum.

**Entscheidung: Der vorhandene Pfad reicht für eine normgerechte
XTM-anyType-Reader-Integration ohne weitere Infrastrukturarbeit nicht aus.** Der
produktive XML-Wrapper ist mit dem vorhandenen DOM-Builder inkompatibel.
Darüber hinaus ist der untersuchte CXML-Canonical-Sink kein geeigneter
W3C-C14N-1.0-Kanonisierer: Acht konkrete Bytegegenproben widersprechen dem
benötigten Ergebnis. Es wurde weder ein eigener C14N-Algorithmus begonnen
noch eine Produktionskomponente oder Abhängigkeit geändert.

Native TMDM-Werte sind dagegen in dem unten abgegrenzten Umfang möglich:
Für zehn bytegleiche Einzelproben wurden tatsächliche Kandidatenbytes als
String in Occurrence und Variant gespeichert und über die öffentlichen Reader
geprüft. Das ist kein Nachweis allgemeiner XML-Kanonisierung oder einer
XTM-Reader-Fähigkeit. Der öffentliche XTM-Reader lehnt anyType weiterhin als
`XTM-UNSUPPORTED/resource-data-datatype` ab. Konformitätsregistrierungen bleiben
unverändert.

## Normativer Vertrag und Editionsgrenze

Maßgeblich sind XTM 2.0, ISO/IEC 13250-3:2007 §§4.16.1–4.16.3, und die dort
referenzierte [W3C Canonical XML 1.0 Recommendation vom 15. März 2001](https://www.w3.org/TR/2001/REC-xml-c14n-20010315),
insbesondere §§2.1–2.4. Der [öffentliche XTM-Text](https://www.isotopicmaps.org/sam/sam-xtm/)
erklärt Publikationsgleichheit; die unabhängige Prüfung gegen die offizielle
ISO-Ausgabe und anwendbare Berichtigungen bleibt ausstehend.
Exclusive C14N, C14N 1.1 und W3C C14N 2.0 werden nicht substituiert.

**Normativ abgeleitet:** Der XTM-Knotensatz umfasst die nachgeordneten
Element-, Attribut- und Zeichenknoten von `resourceData`. Unbenutzte
Namespace-Knoten werden nach der in §4.16.3 bezeichneten URI-/Prefix-Bedingung
entfernt; benötigte geerbte Bindungen bleiben relevant. PI werden nicht
selektiert, Kommentare nicht ausgegeben. Das kanonische UTF-8-Ergebnis wird
als entsprechender Unicode-String zum TMDM-Wert. Bei anyType gilt das auch
für reinen Text, nicht bloß für Inhalte mit Elementen.

**C14N-Vertrag:** QName-/Namespacekontext und Teilbaumkontext sind zu erhalten;
Attributordnung und Text-/Attribut-Escaping sind getrennte Regeln. XML-
Zeilenendennormalisierung ist nicht mit Entitätenausgabe für jeden LF
identisch. Die erwarteten Ergebnisse stehen fest in den Testdaten, einschließlich
Tabs, LF, CR-Zeichenreferenzen und leeren Elementen. Ihre lokalen Herleitungen
stehen pro Probe unter `normativeReason`; sie werden nicht aus dem Kandidaten
oder einem zweiten Prozessor berechnet.

Die [22P-Matrix](slice-22p-xtm-norm-coverage.md),
[22A-XML-Vorprüfung](slice-22a-conformance-closure.md) und
[22O-Disposition](slice-22o-qualified-xtm-corpus-disposition.md) bleiben
unverändert. Dieser Slice ersetzt weder die offene Editionsprüfung noch
entscheidet er Q-XTM-LOOP oder die DOCTYPE-Profilfrage.

## Tatsächlich vorhandene Komponenten

[component-sources.json](../reports/slice-22q/component-sources.json) bindet die
untersuchten CXML-Dateien per SHA-256 an die lokal gepinnte Source
`/nix/store/5075y4alv1is8n78bcsfcaj0mfpqz195-source`, CXML `20200610-git`.
Die [Offline-Vorbereitung](../reports/slice-22q/source-preparation.json) weist
sämtliche sieben vorhandenen Abhängigkeiten und die unveränderten 19D0B-
Patches aus. Es wurde keine Bibliothek installiert oder heruntergeladen.

| Komponente | Beobachtete reale API / Grenze |
|---|---|
| XML-Bytegrenze | `topic-maps.xml:parse-octets(bytes, handler)` aus [src/xml/parser.lisp](../src/xml/parser.lisp): Raw Octets, qualifizierte 19D0B-Marker, Namespaces aktiv, `xmlns`-Attribute aus, alle DOCTYPEs und externe Ressourcen gesperrt. |
| SAX | CXML/SAX-Ereignisse mit QName und Namespace-URI sind grundsätzlich vorhanden. Der produktive XTM-Sourcebaum verwirft QName/Namespace-Mapping-Kontext; er wurde nicht erweitert. |
| DOM | Bereits durch `cxml` geladenes `cxml/dom`, öffentlich `cxml-dom:make-dom-builder`, DOM-Zugriffe und `dom:map-document`. Kein neuer DOM- oder Topic-Maps-Modelltyp eingeführt. |
| DOM-Konfiguration | Der Builder verlangt bei Namespace-Verarbeitung zugleich `sax:*include-xmlns-attributes*` und `sax:*use-xmlns-namespace*`. Der öffentliche Wrapper setzt Ersteres auf NIL; direkter Aufbau scheitert. |
| Ausgabe-Sink | `cxml:make-octet-vector-sink :canonical t` und dokumentierte Option `2`; beide liefern über `sax:end-document` UTF-8-Octets. T wird intern zu 1. Option 2 heißt „Second Canonical Form“, nicht W3C C14N 2.0. |
| DOM-Walker | `dom:map-document(handler, document, &key include-xmlns-attributes include-doctype include-default-values recode)`. Kein beobachteter Knotensatz-/Filterparameter. |
| XPath | `cxml-xmls:make-xpath-navigator` und ein Hilfscontainer sind in `xml/xmls-compat.lisp:247` vorhanden. Daraus ergibt sich keine nachgewiesene XPath-/C14N-Knotensatz-API. Sie wurde nicht vorausgesetzt. |

CXML `xml/unparse.lisp:166–200` beschreibt die Canonical-Modi als Formen zum
Parsergebnisvergleich. `sax:start-element` sortiert bei Canonical-Ausgabe
nach `attribute-qname` (Zeilen 508–511), nicht nach dem verlangten
Namespace-URI-/Local-Name-Schlüssel. Dieselbe Escapefunktion wird für Attribute
und Text verwendet (Zeilen 517/578/672ff). `dom/dom-sax.lisp:11–94` traversiert
Kinder und deren tatsächlich vorhandene Attribute; es implementiert dabei
keinen beliebigen XPath-Knotensatz und keine XTM-Namespace-Selektion.
Ein Funktionsname „canonical“ war somit kein Beleg für die benötigte Normfassung.

## Externe Exploration und produktive Wrapper-Grenze

Zuerst wurden die Programme außerhalb des Repositorys im temporären Verzeichnis
`tm-slice-22q-*` angelegt und mit frischem SBCL 2.5.4 ausgeführt, ohne
Benutzer-/Systeminitialisierung, mit gesperrtem Netzwerk und gesperrten
Schreibzugriffen auf Topic-Maps und HyperDoc. Erst nach den tatsächlichen
Beobachtungen wurden die Charakterisierungen dauerhaft registriert.

**Erster Lauf:** `topic-maps.xml:parse-octets` mit
`cxml-dom:make-dom-builder` signalisiert `SIMPLE-ERROR`:
`SAX configuration is incompatible with DOM: *namespace-processing* is activated, but *include-xmlns-attributes* or *use-xmlns-namespace* are not`.
Exitcode 1. [Originalprogramm und Fehlerlog](../reports/slice-22q/attempts/),
[Ausführung](../reports/slice-22q/attempts/initial-boundary-exploration-execution.json).
Dieser Lauf ist kein erfolgreicher C14N-/Modellnachweis; er belegt eine reale
API-Inkompatibilität und wird nicht nachträglich als PASS umgedeutet.

**Zweiter Lauf:** Eine ausschließlich diagnostische CXML-Konfiguration aktiviert
die beiden vom vorhandenen DOM-Builder benötigten Flags. Sie benutzt den
vorhandenen `closed-handler`, verbietet DOCTYPE und internen Subset-Zugriff,
setzt einen verweigernden Entity-Resolver, deaktiviert Catalog/DTD-Caches und
prüft dieselben beiden Patchmarker. Der produktive Wrapper bleibt unverändert.
Das ist eine Testkonfiguration derselben gepinnten Parserkomponenten, keine
bereits qualifizierte alternative Produktions-Bytegrenze. Zwei ausgeführte
DOCTYPE-Proben bestätigen die Absperrung, ersetzen aber keine allgemeine
Qualifikation dieser Konfiguration.

Danach wird der vorhandene DOM-Kinderwalker experimentell auf das
`resourceData`-Element angewandt; sein Parameter heißt `document`. Dass die
vorhandene Implementierung dessen Kinder traversiert, ist beobachtet, aber
kein zugesagter beliebiger Subset-Vertrag. Es gibt keinen selbst geschriebenen
Serializer, Namespace-Reparaturcode, XML-Sortierer oder C14N-Nachbau. Genau
deshalb bleiben Namespaceverluste und falsche Ausgaben in den Ergebnissen
sichtbar. Die vollständige Dokumentausgabe des unveränderten Walkers ist pro
Probe zusätzlich unter `wholeDocumentCanonicalXML` erhalten.

Die Dokumente sind kleine XML-Komponenteneingaben mit einem `resourceData`-
Container; sie werden nicht als vollständige erfolgreich deserialisierte
XTM-Maps gezählt. Der produktive XTM-Deserializer wird für diese Komponenten-
und nativen Wertproben nicht aufgerufen.

## Festgelegte Gegenproben und tatsächliche Bytes

Die vollständigen XML-Eingaben, Eingabe-Hexbytes/Encoding, tatsächlichen
Parser-/Sink-Aufrufe, unabhängig erwarteten Strings/UTF-8-Hexbytes,
Ist-Strings/Hexbytes, erste Differenz und native Wertresultate stehen in
[exploration.json](../reports/slice-22q/exploration.json) und im dauerhaften
ASDF-Report unter `c14nPreflight.probes`.
Die [ausführbaren Testdaten](../tests/xml-c14n-preflight.lisp) enthalten
`cq-specs` als festen Erwartungskatalog.

| Probe | Soll/Ist UTF-8-Bytes | Erste Differenz, nullbasiert | Vergleich |
|---|---:|---:|---|
| `simple` | 12/12 | — | Bytegleich nur für diese Probe |
| `attributes-ba` | 19/19 | — | Bytegleich nur für diese Probe |
| `attributes-ab` | 19/19 | — | Bytegleich nur für diese Probe |
| `inherited-prefix` | 28/12 | 4 | Abweichung |
| `unused-local-namespace` | 28/49 | 20 | Abweichung |
| `inherited-default` | 28/8 | 2 | Abweichung |
| `nested` | 42/42 | — | Bytegleich nur für diese Probe |
| `escaping` | 66/77 | 23 | Abweichung |
| `whitespace-line-endings` | 17/32 | 5 | Abweichung |
| `comments` | 9/9 | — | Bytegleich nur für diese Probe |
| `lexical-cdata` | 27/27 | — | Bytegleich nur für diese Probe |
| `lexical-escaped` | 27/27 | — | Bytegleich nur für diese Probe |
| `unicode` | 23/23 | — | Bytegleich nur für diese Probe |
| `processing-instruction` | 9/23 | 4 | Abweichung |
| `namespace-attribute-order` | 65/65 | 3 | Abweichung |
| `redundant-binding` | 38/54 | 25 | Abweichung |
| `unicode/UTF-16LE` | 23/23 | — | Bytegleich nur für diese Probe |
| `unicode/UTF-16BE` | 23/23 | — | Bytegleich nur für diese Probe |

Das sind **18 tatsächlich ausgeführte Byteproben**, davon **10 exakt gleich**
und **8 abweichend**. Die zehn Gleichheiten beweisen nur die jeweiligen
Einzelfälle. Der globale Wert `W3CC14NQualified` bleibt **false**.

Die beiden Attributreihenfolgen liefern dieselben tatsächlichen Bytes.
Ebenso stimmen die ausgewählten Werte der CDATA-/Referenz- und ausgeschriebenen
Variante überein. Die beiden UTF-16-BOM-Eingaben liefern denselben Unicode-Wert
und dieselben UTF-8-Ausgabebytes wie die UTF-8-Probe. Ein Prefixwechsel wird
nicht als automatische C14N-Gleichheit behauptet: Prefixe gehören zum hier
relevanten lexikalischen Kontext.

### Konkrete Unterschiede statt bloßer Fehlermeldungen

- **Geerbter Prefix:** Soll `<p:x xmlns:p="urn:p">A</p:x>`, Ist
  `<p:x>A</p:x>`. Die benötigte Bindung des ausgelassenen Containers fehlt.
- **Unbenutzte lokale Bindung:** Ist enthält zusätzlich
  `xmlns:u="urn:unused"`; Soll entfernt sie nach XTM-Selektion.
- **Geerbter Default-Namespace:** Soll `<x xmlns="urn:default">A</x>`,
  Ist `<x>A</x>`; die Zeichenform bezeichnet eine andere Namespace-Zuordnung.
- **Escaping:** Ist schreibt unter anderem `&#9;`, `&#10;`, `&#13;` und
  `&quot;` in Text; Soll unterscheidet Attribut- und Textregeln und verwendet
  die festgelegten hexadezimalen Zeichenreferenzen an den erforderlichen Stellen.
- **Whitespace:** Soll erhält Tabs/LF im Text nach XML-Zeilenendennormalisierung;
  Ist wandelt sie in dezimale Zeichenreferenzen um.
- **PI:** Ist enthält `<?p excluded?>`, obwohl dieser Knoten nicht zum
  XTM-Knotensatz gehört. Kommentare fehlen dagegen in der einfachen Probe.
- **Attributordnung:** Ist beginnt mit `a:a="2" plain="0" ...`; Soll mit den
  Namespace-Deklarationen und danach den nach URI/Local Name geordneten Attributen.
- **Redundante Bindung:** Ist wiederholt `xmlns:p="urn:p"` auf dem Kind;
  Soll gibt die bereits wirksame identische Bindung nicht erneut aus.

Die vorhandene Option `:canonical 2` wurde für dieselben 18 Fälle tatsächlich
mit ausgeführt. Sie behebt keine der acht abweichenden Proben. Keine Option
wurde aufgrund ihres Namens als W3C-C14N-Version bezeichnet. Allgemeine
DOM-Serialisierung ist kein erfolgreicher Canonical-XML-Nachweis.

### Konkrete API-Grenzen

Die nicht vorhandenen Selektorargumente wurden ebenfalls ausgeführt:

| API-Probe | Tatsächliche Condition |
|---|---|
| Sink mit `:node-set` | `INITARG-ERROR`, ungültiger Initialisierungsparameter |
| `dom:map-document` mit `:node-set` | `UNKNOWN-KEYWORD-ARGUMENT` |
| Produktiver Bytewrapper mit DOM-Builder | `SIMPLE-ERROR`, inkompatible Namespace-Flags |
| Diagnostischer DOM-Pfad mit leerem/externalem DOCTYPE | jeweils `DOCTYPE-FORBIDDEN` |

Die beiden Keyword-Proben sind ein negativer Nachweis für diese konkreten
APIs. Zusammen mit der gelesenen Source begründen sie die fehlende direkte
Knotensatzeignung; sie behaupten keine Vollinventur aller Programme des Hosts.

## Native TMDM-Wertprüfung: möglich im ausdrücklich begrenzten Umfang

Für **jede der zehn bytegleichen Einzelproben** wurde die tatsächliche
Kandidatenausgabe streng als UTF-8 dekodiert und die Rückkodierung bytegenau
geprüft. Anschließend wurden ausschließlich öffentliche TMDM-Konstruktoren
verwendet: `make-topic-map`, `intern-topic`, `add-name`, `add-occurrence`,
`add-variant`. Beide Werte tragen den Datentyp
`http://www.w3.org/2001/XMLSchema#anyType`.

Die Occurrence hat kanonischen Parent, Type und einen Scope-Theme. Die Variant
gehört zum kanonischen Name und hat Parent-Scope plus zusätzlichem Theme.
`occurrence-value`/`occurrence-datatype` und `variant-value`/`variant-datatype`
erhalten jeweils den vollständigen tatsächlichen String und die Datentyp-IRI.
Parent-/Type-/Scope-/Handle-Beziehungen werden per EQ beziehungsweise
Topic-Mengengleichheit geprüft. Die Anzahl der Topics bleibt **5 vor/nach**
der Anlage der XML-Werte; aus XML-Tags oder Attributen entstehen keine Topics.

Zwei tatsächliche CXTM-Kanonisierungen sind bytegleich. Der vollständige
vorhandene native Zustandsbeobachter `ik-state` prüft gleichzeitig, dass Werte,
Identifikatoren, Referenzen und Handles unverändert bleiben. CXTM enthält
die üblich XML-escaped eingebettete Wertzeichenfolge; das ist weder ein weiterer
C14N-Schritt noch eine nachträgliche Reparatur der Werte.

Die zehn strukturierten Ergebniszeilen stehen unter `nativeValues`.
Für die acht abweichenden Kandidatenwerte wird bewusst **kein positiver
normativer XML-Wertnachweis** ausgegeben. Die Modellfähigkeit ist damit lokal
belegt; eine allgemeine normgerechte Eingabe→C14N→TMDM-Verarbeitung bleibt
wegen der vorgeschalteten technischen Grenzen unbewiesen. Es wird keine
Reader-Unterstützung simuliert.

## Dauerhafte Tests und unveränderte Registrierung

Neue serielle Testkomponente:
[tests/xml-c14n-preflight.lisp](../tests/xml-c14n-preflight.lisp),
angebunden in [topic-maps.asd](../topic-maps.asd) an das vorhandene
`topic-maps/xtm/tests`. Der bestehende `run-tests` in
[xtm-identity.lisp](../tests/xtm-identity.lisp) ruft `cq-tests` wirklich auf und
sichert `c14nPreflight` im vorhandenen Reportformat. Es entsteht keine zweite
Konformitäts- oder Modellarchitektur.

Die neuen **101 Charakterisierungschecks** prüfen Eingabeerhaltung,
UTF-8-String-Rückkodierung, die beobachtete Gleichheit beziehungsweise Grenze
des unveränderten Kandidaten, die beiden lexikalischen Paarvergleiche,
API-Grenzen und die nativen Werte. Die festgehaltene Liste übereinstimmender
Kandidatenfälle wurde erst **nach** dem externen Lauf eingetragen. Sie verändert
keinen normativen Erwartungsstring. Eine Regression im Charakterisierungstest
wäre kein Ersatz für die erfolgreiche Qualifikation eines späteren anderen
Kanonisierers.

**Wichtige Abnahmeunterscheidung:** Ein erfolgreicher ASDF-Lauf bedeutet, dass
die tatsächlich beobachteten Fähigkeiten **und Grenzen** reproduziert wurden.
Er bedeutet nicht, dass alle acht normativen Bytegegenproben bestanden hätten.
Im Report bleiben diese `BYTE-DIFFERENCE`; `W3CC14NQualified=false` und
`XTMReaderIntegration=false` sind ausdrücklich erhalten. Keine gewöhnliche
Serialisierung wird als vollständiger C14N-PASS gewertet.

Der fokussierte frische ASDF-Lauf erreichte **3844 Checks**, darunter die
101 neuen gegenüber **3743 historisch gespeicherten 22N-Checks**. Die vorherigen
121 Case Records und alle bisherigen fachlichen Reportfelder bleiben identisch.
Der frühere Stand wurde per Hash geprüft, nicht als erneut ausgeführte
unveränderte Vorher-Regression ausgegeben.

## Stopppunkt und genau ein begründeter Folgeauftrag

**Der Infrastruktur-Stopppunkt ist erreicht.** Eine Reader-Integration kann
nicht schlicht durch Entfernen der Unsupported-Prüfung erfolgen. Es fehlen
mindestens ein tatsächlich qualifizierter W3C-C14N-1.0-Knotensatzpfad sowie eine
ausdrücklich freigegebene Namespace-/QName-fähige XML-Anbindung. Die vorhandene
Speicherung nativer Stringwerte ist nicht der Blocker.

Als **ein** gesonderter Folgeauftrag ist die Bereitstellung und Qualifikation
eines W3C-C14N-1.0-Infrastrukturpfads mit dem von XTM bestimmten Knotensatz
zu begründen. Erst dessen bewiesene Eignung und eine ausdrücklich genehmigte
XML-Anbindung würden eine spätere Reader-Integration tragen. Eine eventuelle
Abhängigkeit oder Änderung des XML-Wrappers bedarf des konkreten gesonderten
Auftrags; dieser Bericht wählt keine neue Bibliothek aus und implementiert
keinen eigenen Kanonisierer. Zyklen, Map-II, XTM-2.1-Fähigkeiten und HyperDoc
gehören nicht dazu. Die unabhängige ISO-Ausgabenprüfung bleibt ausstehend.

## Vollständige Offline-Regression und Integrität

Der unveränderte Collector aus `scripts/validate-slice-22d.py` wurde durch den
neuen [Untersuchungswrapper](../reports/slice-22q/reproduce.py) aufgerufen.
Alle **119 Prozesse** erreichten ihre vorgesehenen Exitcodes; darunter sind
**113 Executor-Fehlerkontrollen mit erwartetem Exit 1**. Ein erwarteter
Fehlerlauf zählt nicht als positiver Originalvertrag. Die neuen Komponenten-
proben werden in früh abgebrochenen Fault-Läufen ausdrücklich als nicht ausgeführt
berichtet (`c14nPreflight.executed=false`).

Die Lisp-Prozesse starten frisch mit SBCL 2.5.4,
`--no-sysinit --no-userinit`, vorhandenen gepinnten Abhängigkeiten, gesperrtem
Netzwerk und gesperrten Schreibzugriffen auf beide Repositories. Ein früher
fehlgeschlagener Explorationsprozess wird separat erhalten, nicht zu diesen
119 angenommenen Prozessresultaten gezählt. Die externe erfolgreiche Exploration
und der fokussierte Lauf sind ebenfalls separat dokumentiert.

| Prüfung | Vorherige gespeicherte Evidenz / tatsächlicher neuer Lauf |
|---|---|
| Standalone-XTM | 3743 → **3844 Checks**, alle bisherigen Checklabels erhalten; 101 neue Charakterisierungen |
| TMDM-/CTM-/CXTM-Kern | **12100 Checks**, unverändert |
| XML-Qualifikation | **146 Checks**, unverändert; kein Ersatz für die fehlende C14N-Qualifikation |
| CTM/XTM-Äquivalenz | **30 Paare, 529 Checks, 3 Kontraste**, Report byteidentisch |
| CTM/XTM-Mergemap | **217 Checks**, unverändert |
| Slice 20A/20B/20C/20E/20F/20G/20H | **286/25/171/13/112/226/722 Checks**, erhalten |
| Executor-Fehlerkontrollen | **113**, alte Reportfelder/Case Records/Outcomes vollständig identisch |
| Python / NFC-Oracle | **2 Tests / 16294 Vergleiche**, erhalten |
| Alle 124 XTM-Originaldiagnosen | **vollständig unverändert** |
| Zusätzliche Originalregistrierungen | **0** |

[execution.json](../reports/slice-22q/after/execution.json),
[runs.json](../reports/slice-22q/after/runs.json),
[Bytevergleichszusammenfassung](../reports/slice-22q/after/comparison-summary.json),
[Fault-Audit](../reports/slice-22q/after/failure-controls-audit.json) und
[erhaltene Reports](../reports/slice-22q/after/retained-reports.json) binden
Kommandos, Zeiten, erwartete Exitcodes, Source-/Loghashes und Vergleiche.
`acceptancePassed=true` bedeutet hier erfolgreiche Durchführung und Prüfung
des Vorabnachweises samt Regression, **nicht** erfolgreiche allgemeine
C14N-Kanonisierung. Der Bericht führt `W3CC14NQualified=false` und
`XTMReaderIntegration=false` separat.

| Registrierter Korpus | PASS | FAIL | NOT-RUN |
|---|---:|---:|---:|
| XTM 2.0 | **121** | **0** | **3** |
| CTM | **262** | **4** | **7** |

Die [22O-Dispositionen](slice-22o-qualified-xtm-corpus-disposition.md) gelten
fort. Die drei XTM-NOT-RUN und die vier bekannten CTM-FAILs werden nicht verändert.
Die Abnahmetore A (Normkonformität), B (qualifizierter Abschluss aller Originale)
und C (HyperDoc-Integration) bleiben offen beziehungsweise separat unabgenommen.
Dieser Vorabnachweis schließt keines der Tore pauschal ab.

Alle **10648 geschützten Ausgangsdateien** bleiben
SHA-256-identisch; darin **2006 gepinnte Korpusdateien** und
**8337 historische Reportdateien**.
Alle produktiven TMDM-/CTM-/XTM-/CXTM-/XML-Komponenten und Patchdateien sind
unverändert. Geändert sind allein die zwei vorhandenen Testanbindungsdateien,
die neue Testkomponente, diese Dokumentation und neue Evidenz.
Die **46 erzeugten retained-Reports** sind mit 22N byteidentisch.
[initial-state.json](../reports/slice-22q/initial-state.json) und
[integrity.json](../reports/slice-22q/after/integrity.json) sichern die Vergleichsbasis.

Der neue vollständige Lauf lief von **2026-10-24T06:21:43.997840+00:00** bis
**2026-10-24T06:25:27.926162+00:00**. Diese maschinell erfassten UTC-Zeiten werden nicht mit
der lokalen Datumsangabe des Berichts verwechselt.

Reproduktion in ein neues Verzeichnis außerhalb des Repositorys:

```sh
python3 reports/slice-22q/reproduce.py --output /private/tmp/topic-maps-22q-new
python3 reports/slice-22q/reproduce.py --audit-only --output /private/tmp/topic-maps-22q-new
```

Das [Abschlussmanifest](../reports/slice-22q/completion-audit.json) bindet alle
neuen und geänderten Slice-Artefakte an ihre SHA-256. Der lokale Commit enthält
nur Tests/Testanbindung, Dokumentation und Evidenz. Parent ist der oben genannte
22P-Commit; die finale Commit-ID und der saubere Git-Zustand werden nach dem
Commit separat ausgegeben. Keine Produktionserweiterung, neue Abhängigkeit,
HyperDoc-Änderung, Downloads, Pushes, Deployments oder langlebigen Images.
Ende Slice 22Q; keine automatische Fortsetzung mit 22R.
