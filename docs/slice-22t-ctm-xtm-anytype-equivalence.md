# Slice 22T — CTM/XTM-Äquivalenz für xsd:anyType

## Ergebnis und geprüfter Ausgangspunkt

Basis und Commit-Parent dieses Slices:
`513de98e5f9dfb62ba3c6310a150bb43c5a4c151` (22S).
Arbeitsbranch: `codex/ctm-xtm-slice-22t`.
[Ursprünglicher sauberer Ausgangszustand](../reports/slice-22t/initial-state.json).
Beim Fortsetzen waren die begonnenen Tests und die ASDF-Anbindung uncommittiert;
sie wurden erhalten und vervollständigt. Keine Produktionsdatei wurde geändert.

**Beobachtet:** Alle vier neuen positiven Quellenpaare erreichen über die beiden
produktiven Reader identische native TMDM-Eigenschaften und vollständige
byteidentische CXTM-Ausgaben. Der zusätzliche Namespace-Kontrast bleibt ungleich.
Die ASDF-Suite besteht nun mit **34 positiven Paaren, vier Kontrasten und 728 Checks**.
Alle bisherigen 30 Paare, drei Kontraste und 529 Check-Labels bleiben erhalten;
ihre 33 Berichtszeilen stimmen auch in ihrer individuellen JSON-Serialisierung überein.
Der isolierte und der vollständige Lauf erzeugten denselben Äquivalenzbericht.

[Ausführung und Vollabnahme](../reports/slice-22t/after/execution.json),
[Äquivalenz-Audit](../reports/slice-22t/after/equivalence-audit.json),
[vollständiger regulärer Reader-Bericht](../reports/slice-22t/after/retained/xtm-mergemap.equivalence.json),
[exakte Eingaben und Ausgabehashes](../reports/slice-22t/artifact-index.json).

## Normative Herleitung und Evidenzgrenze

Die bereits dokumentierten Grundlagen aus [22F](slice-22f-ctm-xtm-equivalence.md),
[22R](slice-22r-xml-resource-c14n.md) und
[22S](slice-22s-xtm-anytype-integration.md) werden weiterverwendet; nach den zwei
freigegebenen Archivabrufen fand keine weitere Netzrecherche statt.

**Aus den Referenztexten abgeleitet:**

- [CTM §3.4.1, Produktionen [28]–[29]](https://www.isotopicmaps.org/ctm/ctm.html):
  ein String mit `^^` und Datentyp-IRI stellt den angegebenen lexikalischen Wert
  mit diesem Datentyp dar. §§3.3.9–3.3.10 und 3.10–3.12 legen Scope, Reifier,
  Occurrence und Variant fest.
- [XTM §§4.12, 4.15, 4.16.2–4.16.3](https://www.isotopicmaps.org/sam/sam-xtm/):
  eingebettetes XML mit `xsd:anyType` erhält die in §4.16.3 definierte kanonische
  XML-Stringrepräsentation; Typ, Parent, Scope und Reifier bleiben eigene
  Modelleigenschaften. Namespace-Kontext wird dabei berücksichtigt.
- [TMDM §§4.4, 5.4–5.6, 6.4–6.5](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/):
  bei gleichen Parent-/Type-/Scope-/Value-/Datatype-Eigenschaften gelten die
  bestehenden Gleichheits- und Normalisierungsoperationen. Die Variant hat den
  Name-Scope vereinigt mit ihrem expliziten Scope, als echte Obermenge.
- [CXTM](https://www.isotopicmaps.org/cxtm/cxtm.html) liefert die vollständige
  kanonische Repräsentation der jeweiligen unveränderten nativen Map.

Die kanonischen Sollstrings stehen als feste Literale in
[den Tests](../tests/ctm-xtm-anytype-equivalence.lisp), bereits vor der ersten
produktiven Ausführung. Sie wurden nicht aus einer neuen XTM-Ausgabe erzeugt.
CTM kanonisiert in diesen Proben kein XML: Der Quelltext enthält bereits genau
diesen kanonischen String und die absolute Datentyp-IRI. Eine beliebige
nichtkanonische XML-Zeichenfolge in CTM wäre deshalb keine begründet äquivalente
Ersatzquelle. Die Testkonstanten und Erwartungen wurden nach dem erfolgreichen
Reader-Vergleich nicht an dessen Ausgaben angepasst.

**Evidenzgrenze:** Dies ist ein direkter Austausch-/Semantiknachweis für die
geprüften Quellen, kein Beweis vollständiger CTM-/XTM-Konformität. Die bisher
fehlende unabhängige Gegenprüfung gegen die offiziellen ISO-Ausgaben bleibt
ausstehend; Abnahmetore A, B und C werden nicht pauschal geschlossen.

## Produktive Pfade und native Invarianten

Die bestehende [ASDF-Suite](../topic-maps.asd) lädt die neue Testdatei nach
[der bisherigen Äquivalenzsuite](../tests/ctm-xtm-equivalence.lisp); deren reguläres
`run-tests` ruft alle neuen Paare und den Kontrast tatsächlich auf.

`topic-maps.ctm:deserialize-string` verwendet den bisherigen
[read-literal-Pfad](../src/ctm/reader.lisp),
`topic-maps.xtm:deserialize-octets` den qualifizierten XML-Parser und den in 22S
integrierten [read-resource-value-Pfad](../src/xtm/reader.lisp).
Die bestehenden [add-occurrence](../src/tmdm/occurrences.lisp)- und
[add-variant](../src/tmdm/variants.lisp)-Operationen erzeugen und normalisieren
sämtliche geprüften Items. Es gibt keine Ersatzmap und keine neue Identitätsverwaltung.

Jedes positive Paar wird mit gleicher expliziter Document IRI und CXTM-Basis
zweimal je Reader gelesen, beim zweiten Mal mit anderen diagnostischen Source Keys.
Der Kontrast wird einmal je Reader gelesen. Die fünf neuen Fälle ergeben im
regulären Lauf **18 tatsächliche Reader-Aufrufe und 26 native Constructor-Aufrufe**.
Die Testbeobachter rufen die ursprünglichen Funktionen auf und stellen sie mit
`unwind-protect` wieder her. Sie ändern weder Ergebnisse noch Modelloperationen.

Geprüft werden alle nativen Eigenschaftstupel einschließlich II/SI/SL, Werte,
Datentypen, Parent, Type, Scope und Reifier samt inversen Referenzen. Es gilt
kanonisches `EQ` innerhalb jeder Map; die unabhängig gelesenen Maps teilen keine
Information Items. Zusätzliche Topics für XML-Elemente, Namespace- oder Datentyp-IRIs
würden die exakten Topic-Identitäten und Itemzahlen verletzen und die Tests fehlschlagen
lassen. Wiederholte Kanonisierung muss Bytes, Eigenschaften und gehaltene Handles
unverändert lassen. Keine Ausgabe wird nachbearbeitet.

Zählreihenfolge: **Topics / Names / Variants / Occurrences / Associations / Roles /
reifizierte Items**. Alle geprüften Datentypen sind exakt
`http://www.w3.org/2001/XMLSchema#anyType`.

| Tatsächlicher Fall | Native Soll- und Istzahlen beider Maps | CTM/XTM-CXTM-Bytes | Vergleich |
| --- | --- | ---: | --- |
| `anytype-occurrence` | `4 / 0 / 0 / 1 / 0 / 0 / 1` | 855 / 855 | identisch; keine Abweichungsposition |
| `anytype-variant` | `6 / 1 / 1 / 0 / 0 / 0 / 2` | 1030 / 1030 | identisch; keine Abweichungsposition |
| `anytype-occurrence-normalization` | `4 / 0 / 0 / 1 / 0 / 0 / 1` | 647 / 647 | identisch; keine Abweichungsposition |
| `anytype-variant-normalization` | `6 / 1 / 1 / 0 / 0 / 0 / 2` | 993 / 993 | identisch; keine Abweichungsposition |
| `anytype-namespace-meaning` | `2 / 0 / 0 / 1 / 0 / 0 / 0` | 382 / 383 | absichtlich verschieden; erste Abweichung bei Byte 141 (nullbasiert) |

Occurrence: Owner `a` besitzt neben dem dokumentlokalen II auch
SI `urn:anytype:subject`, SL `urn:anytype:resource` und II `urn:anytype:item`.
Type `t`, Scope `{s}`, Reifier `r` und dessen Rückverweis sind kanonisch.
Die Normalisierungsprobe benutzt dieselben Parent-/Type-/Scope-/Reifier-Beziehungen
mit dokumentlokalen Topic-Identitäten.

Variant: Name `N` gehört zu `a`, hat Type `nt`, Scope `{base}` und Reifier `nr`.
Die Variant hat Scope `{base, extra}`, Reifier `vr` und den kanonischen Parent-Name.
Doppelte Themes werden als Menge behandelt. Die Normalisierungsprobe besitzt
dieselben Beziehungen. Alle nicht ausdrücklich genannten Nicht-Topic-Identifier
sind leer; Names, Variants und Occurrences erhalten keine künstlichen IIs.

In beiden Normalisierungsfällen führen zwei Quellkonstrukte pro Reader zu genau
einem Item. Die beobachteten Constructor-Zahlen sind vor den Aufrufen `[0, 1]`,
danach `[1, 1]`; beide zurückgegebenen Handles lösen auf dasselbe lebende kanonische
Item auf. Das wird vor und nach der übrigen Deserialisierung geprüft, nicht allein
aus einer kurzen CXTM-Ausgabe geschlossen.

Der Kontrast hält Parent, Type, Datentyp, Itemzahlen und Identifier gleich.
`urn:left` gegenüber `urn:right` verändert den kanonischen XML-Wert und damit
die native Occurrence und CXTM-Ausgabe. Dies ist **keine** Reader-/Modellabweichung.
Für die positiven Paare trat keine Condition und keine Fähigkeitslücke auf.

## Quellenpaare, unabhängige Sollwerte und vollständige Ausgaben

Die folgenden Quellen sind exakt die tatsächlich übergebenen Zeichenfolgen bzw.
UTF-8-Octets, ohne ergänztes abschließendes LF. Die exportierten Dateien stimmen
mit den protokollierten Input-Hexwerten überein. Vollständige native Eigenschaftstupel
und Constructor-/Reader-Traces stehen jeweils im Modellbericht.

### anytype-occurrence

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/anytype-occurrence/map`.

Unabhängig erwarteter CTM-Wert und zugleich erwarteter XTM-Wert:

```xml
<p:x xmlns:p="urn:payload" a="A">Grüße 水 &amp; B</p:x>
```

Tatsächliche CTM-Quelle:

```ctm
a <urn:anytype:subject>. a =<urn:anytype:resource>. a ^<urn:anytype:item>. a t:"<p:x xmlns:p=\"urn:payload\" a=\"A\">Grüße 水 &amp; B</p:x>"^^<http://www.w3.org/2001/XMLSchema#anyType>@s ~r.
```

Tatsächliche XTM-Quelle:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><subjectIdentifier href='urn:anytype:subject'/><subjectLocator href='urn:anytype:resource'/><itemIdentity href='urn:anytype:item'/><occurrence reifier='#r'><type><topicRef href='#t'/></type><scope><topicRef href='#s'/></scope><resourceData datatype='http://www.w3.org/2001/XMLSchema#anyType' xmlns:p='urn:payload' xmlns:u='urn:unused'><p:x a='&#65;'>Grüße 水 &amp; B</p:x></resourceData></occurrence></topic></topicMap>
```

[CTM-Eingabe](../reports/slice-22t/after/sources/anytype-occurrence.ctm), [XTM-Octets](../reports/slice-22t/after/sources/anytype-occurrence.xtm), [nativer Modellbericht](../reports/slice-22t/after/models/anytype-occurrence.json), [vollständiges CTM-CXTM](../reports/slice-22t/after/cxtm/anytype-occurrence.ctm.cxtm), [vollständiges XTM-CXTM](../reports/slice-22t/after/cxtm/anytype-occurrence.xtm.cxtm).

### anytype-variant

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/anytype-variant/map`.

Unabhängig erwarteter CTM-Wert und zugleich erwarteter XTM-Wert:

```xml
<p:outer xmlns:p="urn:variant"><p:leaf a="1" b="2">V&amp;🦊</p:leaf></p:outer>
```

Tatsächliche CTM-Quelle:

```ctm
a - nt:"N"@base ~nr ("<p:outer xmlns:p=\"urn:variant\"><p:leaf a=\"1\" b=\"2\">V&amp;🦊</p:leaf></p:outer>"^^<http://www.w3.org/2001/XMLSchema#anyType>@extra,extra ~vr).
```

Tatsächliche XTM-Quelle:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><name reifier='#nr'><type><topicRef href='#nt'/></type><scope><topicRef href='#base'/></scope><value>N</value><variant reifier='#vr'><scope><topicRef href='#extra'/><topicRef href='#extra'/></scope><resourceData datatype='http://www.w3.org/2001/XMLSchema#anyType' xmlns:p='urn:variant' xmlns:u='urn:unused'><p:outer><p:leaf b='2' a='1'>V&amp;🦊</p:leaf></p:outer></resourceData></variant></name></topic></topicMap>
```

[CTM-Eingabe](../reports/slice-22t/after/sources/anytype-variant.ctm), [XTM-Octets](../reports/slice-22t/after/sources/anytype-variant.xtm), [nativer Modellbericht](../reports/slice-22t/after/models/anytype-variant.json), [vollständiges CTM-CXTM](../reports/slice-22t/after/cxtm/anytype-variant.ctm.cxtm), [vollständiges XTM-CXTM](../reports/slice-22t/after/cxtm/anytype-variant.xtm.cxtm).

### anytype-occurrence-normalization

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/anytype-occurrence-normalization/map`.

Unabhängig erwarteter CTM-Wert und zugleich erwarteter XTM-Wert:

```xml
<x a="A" b="2"><y></y>a&amp;b</x>
```

Tatsächliche CTM-Quelle:

```ctm
a t:"<x a=\"A\" b=\"2\"><y></y>a&amp;b</x>"^^<http://www.w3.org/2001/XMLSchema#anyType>@s ~r; t:"<x a=\"A\" b=\"2\"><y></y>a&amp;b</x>"^^<http://www.w3.org/2001/XMLSchema#anyType>@s ~r.
```

Tatsächliche XTM-Quelle:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><occurrence reifier='#r'><type><topicRef href='#t'/></type><scope><topicRef href='#s'/></scope><resourceData datatype='http://www.w3.org/2001/XMLSchema#anyType'><x xmlns='' b='2' a='&#65;'><y/><![CDATA[a&b]]></x></resourceData></occurrence><occurrence reifier='#r'><type><topicRef href='#t'/></type><scope><topicRef href='#s'/></scope><resourceData datatype='http://www.w3.org/2001/XMLSchema#anyType'><x xmlns='' a='A' b='2'><y></y>a&amp;b</x></resourceData></occurrence></topic></topicMap>
```

[CTM-Eingabe](../reports/slice-22t/after/sources/anytype-occurrence-normalization.ctm), [XTM-Octets](../reports/slice-22t/after/sources/anytype-occurrence-normalization.xtm), [nativer Modellbericht](../reports/slice-22t/after/models/anytype-occurrence-normalization.json), [vollständiges CTM-CXTM](../reports/slice-22t/after/cxtm/anytype-occurrence-normalization.ctm.cxtm), [vollständiges XTM-CXTM](../reports/slice-22t/after/cxtm/anytype-occurrence-normalization.xtm.cxtm).

### anytype-variant-normalization

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/anytype-variant-normalization/map`.

Unabhängig erwarteter CTM-Wert und zugleich erwarteter XTM-Wert:

```xml
<p:x xmlns:p="urn:variant" a="A" b="2">V&amp;🦊</p:x>
```

Tatsächliche CTM-Quelle:

```ctm
a - nt:"N"@base ~nr ("<p:x xmlns:p=\"urn:variant\" a=\"A\" b=\"2\">V&amp;🦊</p:x>"^^<http://www.w3.org/2001/XMLSchema#anyType>@extra ~vr) ("<p:x xmlns:p=\"urn:variant\" a=\"A\" b=\"2\">V&amp;🦊</p:x>"^^<http://www.w3.org/2001/XMLSchema#anyType>@extra ~vr).
```

Tatsächliche XTM-Quelle:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><name reifier='#nr'><type><topicRef href='#nt'/></type><scope><topicRef href='#base'/></scope><value>N</value><variant reifier='#vr'><scope><topicRef href='#extra'/></scope><resourceData datatype='http://www.w3.org/2001/XMLSchema#anyType' xmlns:p='urn:variant'><p:x b='2' a='&#65;'><![CDATA[V&🦊]]></p:x></resourceData></variant><variant reifier='#vr'><scope><topicRef href='#extra'/></scope><resourceData datatype='http://www.w3.org/2001/XMLSchema#anyType' xmlns:p='urn:variant'><p:x a='A' b='2'>V&amp;🦊</p:x></resourceData></variant></name></topic></topicMap>
```

[CTM-Eingabe](../reports/slice-22t/after/sources/anytype-variant-normalization.ctm), [XTM-Octets](../reports/slice-22t/after/sources/anytype-variant-normalization.xtm), [nativer Modellbericht](../reports/slice-22t/after/models/anytype-variant-normalization.json), [vollständiges CTM-CXTM](../reports/slice-22t/after/cxtm/anytype-variant-normalization.ctm.cxtm), [vollständiges XTM-CXTM](../reports/slice-22t/after/cxtm/anytype-variant-normalization.xtm.cxtm).

### anytype-namespace-meaning

Document IRI und CXTM-Basis: `https://equivalence.example.invalid/anytype-namespace-meaning/map`.

Unabhängig erwarteter CTM-Wert:

```xml
<p:x xmlns:p="urn:left"></p:x>
```

Unabhängig erwarteter XTM-Wert:

```xml
<p:x xmlns:p="urn:right"></p:x>
```

Tatsächliche CTM-Quelle:

```ctm
a t:"<p:x xmlns:p=\"urn:left\"></p:x>"^^<http://www.w3.org/2001/XMLSchema#anyType>.
```

Tatsächliche XTM-Quelle:

```xml
<topicMap xmlns='http://www.topicmaps.org/xtm/' version='2.0'><topic id='a'><occurrence><type><topicRef href='#t'/></type><resourceData datatype='http://www.w3.org/2001/XMLSchema#anyType' xmlns:p='urn:right'><p:x/></resourceData></occurrence></topic></topicMap>
```

[CTM-Eingabe](../reports/slice-22t/after/sources/anytype-namespace-meaning.ctm), [XTM-Octets](../reports/slice-22t/after/sources/anytype-namespace-meaning.xtm), [nativer Modellbericht](../reports/slice-22t/after/models/anytype-namespace-meaning.json), [vollständiges CTM-CXTM](../reports/slice-22t/after/cxtm/anytype-namespace-meaning.ctm.cxtm), [vollständiges XTM-CXTM](../reports/slice-22t/after/cxtm/anytype-namespace-meaning.xtm.cxtm).

## Wiederherstellung und abgeschlossene Offline-Regression

Die früheren [Blocker](slice-22t-blocker.md)- und
[Wiederbeschaffungsberichte](slice-22t-pin-recovery.md) bleiben unveränderte
historische Momentaufnahmen. Nach ausdrücklicher Nutzerfreigabe wurden genau
zwei ursprüngliche Quicklisp-Archive durch die dokumentierten Nix-Befehle bezogen.
[Restoration mit Kommandos, Ergebnissen und Hashprüfungen](../reports/slice-22t/restoration.json).
NAR-Hashes und Store-Pfade stimmen exakt mit beiden ursprünglichen Pins überein.
Keine Ersatzversion, Lockfile-, Profil-, Konfigurations- oder Dienständerung.

Die unveränderte Offline-Vorbereitung prüfte alle sieben Pins und wendete die
19D0B-Patches auf getrennte Kopien an. Quellenmanifest, Patchhashes und sämtliche
Before-/After-Hashes stimmen mit 22S überein:
[erste Vorbereitung](../reports/slice-22t/restored-preparation.json) und
[Vorbereitung der Vollregression](../reports/slice-22t/after/source-preparation.json).
Bei der Fortsetzung betraf die vor der ersten fachlichen Ausführung nötige
Testkorrektur acht literale Reifier-Tilden in Lisp-FORMAT-Quelltextfabriken (`~~` erzeugt `~`);
[Nachweis](../reports/slice-22t/pre-execution-test-corrections.json).
Keine produktive Semantik wurde korrigiert oder erweitert.

[Isolierter Lauf](../reports/slice-22t/isolated-run.json),
[isoliertes Log](../reports/slice-22t/isolated.log),
[Vollregressions-Kommandos und Loghashes](../reports/slice-22t/after/runs.json),
[Regressionslog](../reports/slice-22t/after/regression.log).
Die bereits vorhandene 22D-Collect-Funktion und der unveränderte
22S-Fehlerkontrolltreiber werden über eine minimale
[Konfiguration](../reports/slice-22t/collect.py) wiederverwendet.
Der [Auditor](../reports/slice-22t/reproduce.py) prüft die Ergebnisse gegen die
historische 22S-Evidenz; `--audit-only` bezeichnet ausdrücklich keine neue Ausführung.

Alle 119 Prozessausgänge stimmen mit der Erwartung überein. Jeder Testprozess
läuft frisch, mit Netzwerk- und Repository-Schreibsperre einschließlich HyperDoc;
SBCL 2.5.4 ohne Benutzer-/Systeminitialisierung. Die 113 erwarteten Fehlerausgänge
sind Executor-Gegenproben, keine Original-PASS. Es gab kein Retargeting.

| Erhaltene Prüfung | Ergebnis |
| --- | ---: |
| Kernregression TMDM/CTM/CXTM | 12.100 Checks |
| Eigenständige XTM-Suite einschließlich bisheriger 22Q/R/S-Prüfungen | 4.327 Checks; Bericht unverändert |
| XML-Qualifikation | 146 PASS, 0 FAIL |
| CTM/XTM-Mergemap | 217 Checks |
| Slice 20A / 20B / 20C / 20E / 20F / 20G / 20H | 286 / 25 / 171 / 13 / 112 / 226 / 722 Checks |
| CTM/XTM-Äquivalenz | 728 Checks; 34 positive Paare; vier Kontraste |
| Executor-Fehlerkontrollen | 113 erwartete Fehlerausgänge; Berichte byteidentisch zu 22S |
| Python | zwei Tests |
| NFC-Oracle | 16.294 Vergleiche |

[Diagnosevergleich](../reports/slice-22t/after/diagnostic-changes.json): Alle 124
XTM-Originaldiagnosen sind unverändert, einschließlich aller bisherigen 121 PASS.
[Fehlerkontrollaudit](../reports/slice-22t/after/failure-controls-audit.json).
Alle bisherigen gespeicherten Regressionsberichte außer dem ausdrücklich um die
fünf neuen Fälle ergänzten Äquivalenzbericht bleiben byteidentisch:
[Vergleichsliste](../reports/slice-22t/after/retained-reports.json).

| Registrierter Originalkorpus | PASS | FAIL | NOT-RUN |
| --- | ---: | ---: | ---: |
| XTM 2.0 | 121 | 0 | 3 |
| CTM | 262 | 4 | 7 |
| Gesamt | 383 | 4 | 10 |

Die neuen synthetischen Reader-Paare erzeugen keine Originalregistrierungen.
Alle drei XTM-Dispositionen, vier bekannten CTM-FAILs und offenen CTM-Fälle
bleiben sichtbar. Keine Änderung an Case Records oder Statusdefinitionen.

## Integrität und Abschlussgrenze

[Integritätsaudit](../reports/slice-22t/after/integrity.json): **11.574** geschützte
Basisdateien sind unverändert, darunter **2.006** gepinnte Korpusdateien und
**9.256** historische Reportdateien. Sämtliche produktiven TMDM-, CTM-, XTM-,
CXTM- und XML-Quellen bleiben byteidentisch. Die einzigen Änderungen an bereits
versionierten Dateien sind Testaufrufe in `tests/ctm-xtm-equivalence.lisp` und
die ASDF-Anbindung in `topic-maps.asd`; hinzu kommen neue Tests, Dokumentation
und Ausführungsevidenz dieses Slices. Keine neue Abhängigkeit, kein Push,
Deployment, HyperDoc-Eingriff oder Load eines langlebigen Lisp-Images.

Für die geprüften Konstrukte besteht der beauftragte Austausch-Nachweis Z3.
Keine Produktionsabweichung wurde festgestellt; ein weiterer Implementierungsslice
wird aus diesem Ergebnis nicht abgeleitet. Slice 22T endet nach dem lokalen Commit.
