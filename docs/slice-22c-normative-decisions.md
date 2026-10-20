# Slice 22C — Normative Entscheidungen mit ausgewiesenen Editionsgrenzen

Stand: 20. Oktober 2026. Basis/Parent: `bc9dcfb02f945422970d65266dc66b991806777d`. Branch: `codex/conformance-slice-22c`.

Die 13 beauftragten Originale wurden erneut untersucht. **Eine A-Entscheidung betrifft die fehlende nichtzyklische XTM-mergeMap-Verarbeitung; zwölf Fälle bleiben formal C. Keine unbedingte B-Entscheidung.** Für die DateTime-Fälle bleibt B durch die geprüfte öffentliche CXTM-Fassung und XSD gestützt, wird aber bis zum Publikationsabgleich ausdrücklich als bedingte Schlussfolgerung geführt. Das präzisiert die frühere editionsqualifizierte B-Einstufung; es ändert weder alte Berichte noch Teststatus.

Die vollständige vorhandene Regression ist erfolgreich reproduziert. Nach tatsächlicher Ausführung:

| Korpus | PASS | FAIL | NOT-RUN |
|---|---:|---:|---:|
| CTM | 262 | 4 | 7 |
| XTM 2.0 | 71 | 0 | 53 |
| Gesamt | 333 | 4 | 60 |

[Fallbezogene Evidenz](../reports/slice-22c/case-evidence.json) enthält alle Original- und Baselinebytes als Hex/Text/SHA-256, frische Conditions, Modelle, vollständige CXTM-Differenzen, vorherige und neue Entscheidungen. [Lesbarer Originalanhang](slice-22c-original-evidence.md) zeigt alle Quellen und Variablenpositionen. [Quellenprüfung](../reports/slice-22c/source-review.json) hält Editionsqualität und konkrete Beschaffungsfragen fest. Kein neuer Originalvertrag wurde registriert.

## Herkunft der Aussagen und verfügbare Quellen

`observed` bezeichnet gelesene lokale Bytes oder frische Prozessresultate; `derived` eine Schlussfolgerung aus benannten Quellen innerhalb ihrer Editionsgrenzen; `inferred` eine Implementierungs-/Planungsfolgerung; `hypothesized` eine unbelegte Möglichkeit. Diese Labels stehen auch in den JSON-Berichten. Vorschläge werden als solche bezeichnet; ihre Umsetzung ist nicht Teil dieses Slice.

**Lokales Inventar, observed:** Im Repository einschließlich `references/`, `docs/`, den bisherigen 22A-/22B-Berichten und den erhaltenen temporären 22A-/22B-Verzeichnissen wurde keine vollständige veröffentlichte Normdatei oder gespeicherte Normvorschau gefunden. Vorhanden sind Quellenverweise, frühere Interpretationen und ausführbare Korpusevidenz. Das ist keine Behauptung über sämtliche privaten Verzeichnisse des Auftraggebers. Die Normprüfung erfolgte anschließend lesend online; keine Normkopie wurde heruntergeladen oder eingecheckt.

| Kürzel | Geprüfte Quelle / maßgebliche Ausgabe | Qualität und konkrete Grenze |
|---|---|---|
| CTM-H | [öffentliche CTM-HTML-Fassung](https://www.isotopicmaps.org/ctm/ctm.html), Ziel ISO/IEC 13250-6:2010 | Die [Projektseite](https://www.isotopicmaps.org/ctm/) bezeichnet genau diesen Link als Entwurf vom 2010-03-31. Das ist zugleich der Korpusstand laut `vendor/cxtm/ctm/STATUS.txt`. |
| CTM-P | [veröffentlichte Teilvorschau](https://cdn.standards.iteh.ai/samples/43940/6663ee28c1604551ac6adc02e22c6bb6/ISO-IEC-13250-6-2010.pdf), erste Ausgabe 2010-11-15 | Extrahierter Text: gedruckte S.1–5 bis §3.4.2. Inhaltsverzeichnis ist kein Nachweis späterer Klauseln. Screenshotabrufe scheiterten mit Cache miss; keine visuelle Prüfung behauptet. |
| XTM-H | [XTM 2.0, öffentliche Fassung 2006-06-19](https://www.isotopicmaps.org/sam/sam-xtm/), Ziel ISO/IEC 13250-3:2007 | Kopf nennt FDIS, Einleitung erklärt ausdrücklich Identität mit der ISO-Veröffentlichung. Diese editorische Erklärung trägt die begrenzte A-Entscheidung; kein eigener PDF-Abgleich. |
| TMDM-H | [öffentliche Fassung 2006-06-18](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/), ISO/IEC 13250-2:2006 | Ebenfalls ausdrückliche Publikationsidentitätserklärung; keine separate Processor-Conformance-Klausel (§1). |
| CXTM-H | [öffentliche Fassung 2009-01-27](https://www.isotopicmaps.org/cxtm/cxtm.html), Ziel ISO/IEC 13250-4:2009 | Keine entsprechende Publikationsidentitätserklärung gefunden. Endgültiger §3.16 nicht unabhängig verfügbar verifiziert. |
| XSD | [W3C Recommendation 2004-10-28, zweite Ausgabe](https://www.w3.org/TR/2004/REC-xmlschema-2-20041028/) | Datierte Primärquelle; keine Übernahme von XSD 1.1. [Errataseite](https://www.w3.org/2004/03/xmlschema-errata): Part 2 ohne Einträge im gelesenen Stand. |

**Neue Editionsbeobachtung:** CTM-P §3.2 enthält eine zusätzliche Gültigkeitsforderung an das erzeugte TMDM-Modell; §3.4.1 verlangt ausdrücklich XSDT-gültige direkte DateTime-Werte; §3.4.2 verwendet verbindliches `shall`, wo CTM-H `should` verwendet. Damit ist eine pauschale Wortlautgleichheit bereits im verfügbaren Ausschnitt widerlegt. Ob gerade Include oder Template Tail geändert wurden, folgt daraus nicht.

Die offiziellen Katalogseiten bestätigen die Ausgaben [CTM 2010](https://www.iso.org/standard/43940.html), [XTM 2007](https://www.iso.org/standard/40018.html), [TMDM 2006](https://www.iso.org/standard/40017.html) und [CXTM 2009](https://www.iso.org/standard/52120.html). XTM 2007 ist inzwischen durch 2013 ersetzt; hier bleibt die ausdrücklich beauftragte Ausgabe 2007 maßgeblich. Im geprüften [SC-34-Katalog](https://www.iso.org/committee/45374/x/catalogue/) wurde keine separate einschlägige Berichtigung aufgefunden. Diese begrenzte Suche beweist keine Errata-Freiheit.

## Übersicht der 13 Entscheidungen

A = belegte Implementierungsabweichung; B = belegtes korrektes Ist-Modell gegenüber abweichender Baseline; C = abschließende Entscheidung mit konkreter Evidenzlücke. Die Spalte „Vorher“ gibt die historische 22A-Einstufung wieder, nicht deren Autorität für diese Entscheidung.

| Exakte Case-ID | Vorher 22A | 22C | Evidenz / offene Frage | Konsequenz |
|---|---|---|---|---|
| `ctm/in/include-template.ctm` | ungeklärte Anforderung / C | C | CTM-H §§3.2,3.14–3.16.2; Kindmodell leer, spätere Caller-II; veröffentlichte Include-/Template-Klauseln fehlen | FAIL erhalten; Q-CTM |
| `ctm/in/include-wildcard2.ctm` | ungeklärte Anforderung / C | C | CTM-H §§3.3.8,3.16.2; ein zusätzlicher erhaltener Kind-II; endgültige Regel fehlt | FAIL erhalten; Q-CTM |
| `ctm/in/occurrence-datetime-timezone2.ctm` | Norm-/Baselinekonflikt / B, editionsqualifiziert | C | XSD §§3.2.7.2–3; B unter CXTM-H §3.16 gestützt; endgültiger CXTM-Zweig fehlt | FAIL erhalten; Q-CXTM |
| `ctm/in/occurrence-datetime2.ctm` | Norm-/Baselinekonflikt / B, editionsqualifiziert | C | XSD §§3.2.7.1–2,D.1; B unter CXTM-H gestützt; endgültiger CXTM-Zweig fehlt | FAIL erhalten; Q-CXTM |
| `ctm/in/template-ambiguous-parameter5.ctm` | Normkonflikt / C | C | CTM-H Tail-SI-Grammatik, Condition bei 79; veröffentlichte spätere Grammatik fehlt | NOT-RUN; Q-CTM |
| `ctm/in/template-ambiguous-parameter6.ctm` | Normkonflikt / C | C | dieselbe Grammatikposition, Condition bei 114 | NOT-RUN; Q-CTM |
| `ctm/in/template-subject-identifier2.ctm` | Normkonflikt / C | C | dieselbe Grammatikposition, Condition bei 34 | NOT-RUN; Q-CTM |
| `ctm/invalid/template-item-identifier-2nd-arg.ctm` | Normkonflikt / C | C | Body-Ablehnung bei 44 statt Prüfung des zweiten `^`-Arguments | NOT-RUN; separater negativer Abnahmevertrag nötig |
| `ctm/invalid/template-item-identifier3.ctm` | Normkonflikt / C | C | Body-Ablehnung bei 34 statt Prüfung des `^`-Arguments | NOT-RUN; separater negativer Abnahmevertrag nötig |
| `ctm/invalid/template-subject-locator-2nd-arg.ctm` | Normkonflikt / C | C | Body-Ablehnung bei 44 statt Prüfung des zweiten `=`-Arguments | NOT-RUN; separater negativer Abnahmevertrag nötig |
| `ctm/invalid/template-subject-locator3.ctm` | Normkonflikt / C | C | Body-Ablehnung bei 34 statt Prüfung des `=`-Arguments | NOT-RUN; separater negativer Abnahmevertrag nötig |
| `xtm2/in/mergemap-itemid.xtm` | vorläufiger Normkonflikt / C | A | XTM-H §§4.21,5; nichtzyklischer Import wird als Unsupported abgebrochen. Baseline-Map-II separat widersprüchlich | minimale Importfähigkeit in gesondertem 22H; kein unbedingter PASS prognostiziert |
| `xtm2/in/mergemap-loop.xtm` | ungeklärte Anforderung / C | C | XTM-H §4.21, TMDM-H §§5.3.5,6; Zyklusmodell/Cache nicht explizit geregelt | Q-XTM-LOOP; endliche Strategie erst gesondert vereinbaren |

**Warum DateTime jetzt formal C:** Die verfügbare XSD-Evidenz hat sich nicht verschlechtert. Der Bericht unterscheidet jetzt konsequent zwischen einer gestützten B-Schlussfolgerung für den geprüften öffentlichen Text und einer abgeschlossenen Entscheidung über die verlangte ISO-Ausgabe. Q-CXTM ist dafür eine echte noch offene Voraussetzung. Frühere B-Berichte bleiben unverändert erhalten.

## Vier CTM-FAILs: vollständige Modell- und Byteprüfung

Für alle vier ist die tatsächliche Condition **null**. Die aktuellen Topic-/Type-/Parent-/Scope-Referenzen sind nativ geprüft; wiederholte Kanonisierung erhält die Map. Die Vergleichsansicht ordnet Topics anhand gemeinsamer Identifier zu, damit bloße kanonische Neunummerierung nicht als Identitätsänderung erscheint. Sie ist ein Bericht über die echten Modelle und XML-Bäume, keine zweite Modellimplementierung oder Ersatzmap.

| Original | Ist / Soll Bytes | Erste Differenz, nullbasiert | Vollständige verbleibende Modelldifferenz nach Topic-Zuordnung |
|---|---:|---:|---|
| include-template | 353 / 401 | 58 | Baseline hat am Occurrence-Type zusätzlich `include-template.sub#occtype` |
| include-wildcard2 | 719 / 669 | 61 | Ist hat beim Topic mit Name `Sub Sub` zusätzlich `include-wildcard2.sub#$__1.foo` |
| occurrence-datetime-timezone2 | 674 / 679 | 382 | ausschließlich Occurrence-Wert: UTC gegenüber Offset |
| occurrence-datetime2 | 370 / 370 | 232 | ausschließlich Occurrence-Wert: `12:02:00` gegenüber `12:01:60` |

Die vier vollständigen Istdateien und Zeilendiffs liegen in [comparisons](../reports/slice-22c/comparisons/). Alle weiteren Namen, Identifier, Datentypen, Type-/Parent-/Scope-Beziehungen und Objektanzahlen stimmen überein. Die nativen Identifier-Mengen sind mit den tatsächlichen CXTM-Elementen abgeglichen; beide vollständigen XML-Bäume und die verbleibenden Differenzpfade stehen in `completeModelComparison`.

**include-template, observed:** Original 48 Bytes, kein abschließendes LF. Nach `%include` besitzt das Kind eine Template-Definition, null Topics und null Associations. Der Aliastransfer bekommt folglich keine Topics. Erst `template(topic)` im Elternstream erzeugt `#topic`, `#occtype` und eine Occurrence `Test`/`xsd:string` mit Parent `#topic`, Type `#occtype`, leerem Scope. Counter 0. Keine Names/Associations. Die tatsächliche spätere Document IRI ist die Eltern-IRI; die Kindquellposition bleibt Diagnoseprovenienz.

**include-wildcard2, observed:** A=`include-wildcard2.ctm` inkludiert B=`include-wildcard2.sub`; B inkludiert C=`include-wildcard2.sub2`. Die dokumentierten Umgebungen ergeben:

| Quelle | Document IRI | Wildcard-IRI | Counter hinein → hinaus |
|---|---|---|---|
| C | C | B | 0 → 1 |
| B | B | A | 0 → 2 |
| A | A | A | 0 → 3 |

Die Map enthält vier Topics, drei Names, keine Occurrences/Associations. `Sub Sub` besitzt sowohl `B#$__1.foo` als auch `A#$__1.foo`; `Sub` besitzt `A#$__2.foo`, `Master` besitzt `A#$__3.foo`. Der vierte Topic ist der Standard-Name-Type mit SI `http://psi.topicmaps.org/iso13250/model/topic-name`. Alle Names haben diesen Type und leeren Scope. Es wurde weder ein Identifier hinzugefügt noch entfernt, um die Untersuchung passend zu machen.

**Include-Deutung, derived:** CTM-H §3.16.2 ergänzt Identifier, übernimmt den Kind-Counter und macht importierte Templates am Include-Ort nutzbar. Für das beobachtete leere Definitionsmodell fehlt ein Aliasoperand; im verschachtelten Fall ist die zusätzliche Kindidentität bereits vorhanden. Das stützt die bisherige B-Lesart, ersetzt aber nicht Q-CTM. Eine fortwirkende Bindung an die Definitions-IRI wäre eine zu belegende andere Regel, keine aus der Baseline automatisch ableitbare Pflicht.

**DateTime-Zeitzone, observed/derived:** Drei Topics, zwei Names, eine Occurrence vom Type `#datetime` am Parent `#some-topic`, Datentyp `xsd:dateTime`, leerer Scope. `2011-01-01T00:00:00+02:00` minus zwei Stunden ist `2010-12-31T22:00:00Z`. XSD §§3.2.7.2–3 stützen Wertgleichheit und UTC-Kanonik. Der Reader speichert bei diesem nackten Literal bereits die kanonische Form; die unveränderte CXTM-Kanonisierung erhält sie. Daraus folgt keine allgemeine Forderung, jede TMDM-Lexikalform schon beim Import umzuschreiben.

**DateTime-Sekunden 60, observed/derived:** Original 122 Bytes einschließlich UTF-8-BOM, zwei Topics, eine Occurrence am Parent `#topic`, Type `#occtype`, `xsd:dateTime`, leerer Scope. Die Grammatikform allein entscheidet die Wertgültigkeit nicht. XSD D.1 lässt Sekunden 60 in Schaltsekundenkontexten zu und behandelt ungeeignete Tageslagen als Minutenübertrag; der 19. September ist kein dort genannter Kandidat. Der beobachtete Wert ist `1976-09-19T12:02:00`, ohne erfundene Zeitzone. E.1 bestätigt den Überlauf für Arithmetik, wird hier aber nicht als eigenständige Importvorschrift ausgegeben. Weder Quellkommentar noch Baseline belegen eine tatsächliche Schaltsekunde. Der endgültige CXTM-Publikationsabgleich bleibt offen.

## Template-Grammatik und tatsächlich erreichte Fehler

**Derived aus CTM-H:** Die Herleitung für den unmarkierten zusätzlichen SI lautet `[50] → [51] → [52] → [17] → [12]`. Sie erreicht keine Variable. Die folgenden Positionen sind dagegen getrennt zu behandeln:

| Position | Herleitung / Bedingung im geprüften Text |
|---|---|
| Topic-Kopf | §3.8 `[49] → [13]`; variable vorgesehen |
| Topic Reference, einschließlich Type/Player | §3.3.7 `[20] → [13]`; variable vorgesehen |
| nach `=` / `^` | §3.3.6 `[18]` / `[19]`; variable ausdrücklich vorgesehen |
| Literal | §3.4 `[28]`; variable vorgesehen |
| zusätzlicher unmarkierter SI im Tail | §3.9 `[50–52] → [17] → [12]`; keine variable |

§§3.14–3.15 erlauben Template-Variablen im vorgesehenen Kontext, binden Argumente nach Position und erfordern eine dort zulässige Substitution. Diese Semantik erweitert nicht automatisch jeden Identifier-Slot. Die sieben Body-Eingaben sind daher **nach CTM-H** ungültig; die endgültige Editionsentscheidung bleibt wegen Q-CTM C. Eine historische Absicht, gerade diesen Slot zu erweitern, bleibt `hypothesized`; kein entsprechender Beschluss wurde gefunden.

**Observed:** Alle sieben Originale signalisieren `INVALID-TEMPLATE-BODY`, Code `template-identity-tail`, Cause und Context null. Zeichenpositionen sind nullbasiert, Zeile/Spalte einsbasiert:

| Datei | Zeichen | Zeile:Spalte | Original-CXTM |
|---|---:|---|---|
| template-ambiguous-parameter5.ctm | 79 | 5:13 | nicht erzeugt |
| template-ambiguous-parameter6.ctm | 114 | 7:11 | nicht erzeugt |
| template-subject-identifier2.ctm | 34 | 3:15 | nicht erzeugt |
| template-item-identifier-2nd-arg.ctm | 44 | 3:17 | keine positive Baseline |
| template-item-identifier3.ctm | 34 | 3:15 | keine positive Baseline |
| template-subject-locator-2nd-arg.ctm | 44 | 3:17 | keine positive Baseline |
| template-subject-locator3.ctm | 34 | 3:15 | keine positive Baseline |

Die Conditionposition liegt nach dem vom Syntaxprüfer konsumierten Variablentoken; sie ist nicht mit dem im Anhang separat angegebenen Variablenbeginn zu verwechseln. Die drei ausgeschriebenen positiven Gegenproben stimmen erneut **353/353, 613/613 und 204/204 Bytes** mit ihren Baselines überein. Sie bestätigen die erwarteten ausgeschriebenen Modelle, keinen Original-Template-PASS.

Bei den vier negativen Originalen sollte historisch ein markiertes `^`- beziehungsweise `=`-Argument im unmarkierten SI-Verwendungskontext scheitern. Tatsächlich wird bereits der Body abgelehnt, in den Zweiargumentfällen sogar beim ersten Body-Statement. Falls die veröffentlichte Grammatik dies bestätigt, wäre ein neuer Body-Syntax-Abnahmevertrag separat zu vereinbaren; der bisher beabsichtigte Argumenttest ist damit weiterhin nicht erreicht. Zwölf vorhandene Kontextkontrollen wurden unverändert erneut ausgeführt, einschließlich gültiger Kopf-/Referenz-/markierter Identitäts-/Literalverwendungen und gezielter ungültiger Argumente.

## XTM-mergeMap: Modellregel und Verfahrenswahl

**mergemap-itemid, observed:** Root 148 Bytes; Kind 151 Bytes. Die Rootquelle hat keinen Map-II, einen `mergeMap` und einen Topic `id="topic"`. Das Kind hat einen Map-II `#the-topic-map` und einen eigenen Topic `id="topic"`. Der frische öffentliche Reader lehnt das Rootoriginal mit `XTM-UNSUPPORTED/:unsupported-construct` bei ungefähr 2:41 ab; Cause null. Kein originales Ergebnis-Modell und keine Ist-CXTM-Bytes wurden erzeugt. Die Baseline hat 314 Bytes.

Die unveränderte Kindquelle wurde zusätzlich separat gelesen: ein Topic mit II `Kind-IRI#topic`, Map-II `Kind-IRI#the-topic-map`, keine Associations; Condition null, 185 CXTM-Bytes, aktuelle native Referenzen und reine wiederholte Kanonisierung. Dies ist eine Hilfsquellenbeobachtung, kein zusätzlicher Originalvertrag.

**Derived, A im bezeichneten Umfang:** XTM-H §4.21 verlangt bei diesem nichtzyklischen Fall Inhaltsimport; §5 verlangt das zugehörige isomorphe Modell. Die Unsupported-Ablehnung ist die fehlende Implementierung dieser Pflicht. Der minimale Korrekturbedarf für einen gesonderten Slice ist eine kontrollierte Ressourcenauflösung plus bestehender nativer Inhaltsimport mit korrekter Kind-IRI. Die beiden `#topic`-Identifier gehören zu verschiedenen Dokumenten und rechtfertigen kein gegenseitiges Merging.

**Separater Baselinebefund:** §4.21 nennt Topics und Associations als Operanden, nicht das Quell-Map-Item. TMDM-H §§5.1–5.2 und 6.1–6.2 erzeugen keinen zusätzlichen Auftrag, dessen II auf die Zielmap zu übertragen. Die Baseline erwartet genau diese zusätzliche Map-Eigenschaft. Das ist ein abgeleiteter Konflikt mit der geprüften Importregel. Der ganze Originalvertrag wird dennoch nicht B genannt: Eine Unsupported-Ablehnung ist kein normativ korrektes erfolgreiches Ist-Modell. Auch nach normgerechter Implementierung ist hier kein bedingungsloser historischer CXTM-PASS zu versprechen.

**mergemap-loop, observed:** Root und Sub haben jeweils 150 Bytes; beide enthalten vor dem lokalen Topic einen Verweis auf das andere Dokument. Der exakte Graph ist Root → Sub → Root. Root und separat gelesenes Sub signalisieren jeweils `XTM-UNSUPPORTED/:unsupported-construct` bei ungefähr 2:39, Cause null. Der Reader hat weder eine Schleife ausgeführt noch eine qualifizierte Zykluscondition erzeugt. Die Baseline mit 222 Bytes enthält zwei dokumentqualifizierte Topics und keine Map-Identifier.

**Derived / offen:** XTM-H §4.21 beschreibt erneute Deserialisierung; TMDM-H §5.3.5 und §6 führen gleiche Topic-Identitäten zusammen. In diesen Klauseln ist keine bestimmte Wiederholungs-/Cache-Strategie angegeben. Für genau diese Quellen ist ein endlicher Abschluss mit beiden dokumentqualifizierten Topics nachvollziehbar; das ist eine bedingte Modellfolgerung, kein schon ausgeführtes Ergebnis. Ob die rekursive Verfahrensbeschreibung diesen Abschluss verlangt oder welche Ergänzung dafür nötig ist, bleibt Q-XTM-LOOP.

**Inferred, vorgeschlagenes Verfahren für später:** Ein pro Import endlicher, gepinnter Ressourcengraph könnte jede IRI einem stabilen Dokumentknoten zuordnen, lokale Inhalte vollständig erfassen und die Abhängigkeiten über eine Worklist beziehungsweise stark zusammenhängende Komponenten bis zum stabilen Inhalt abschließen. Gleiche Identitäten werden dabei nur mit nativen TMDM-Operationen vereinigt. Ein bloßes „visited, daher leer zurückgeben“ wäre hier nicht ausreichend begründet: Die lokalen Topics stehen nach dem Rückverweis und dürfen nicht verloren gehen. Die Norm schreibt diese Datenstrukturen nicht vor. Auch Fehlerpolitik, Ressourcenlimits und Cache-Lebensdauer sind gesonderte Betriebsentscheidungen. Kein Netzwerkfallback und kein rekursives Warten auf sich selbst.

## Konkrete offene Primärquellen und Konsequenzen für 22D–22J

- **Q-CTM:** Rechtmäßig zugängliche Auszüge von ISO/IEC 13250-6:2010, §§3.8–3.9 (gedruckte S.6–7), §§3.14–3.15 (S.8–9), §3.16.2 (S.10) und zugehörige EBNF/Anhang B (S.13–14), einschließlich relevanter Berichtigungen. Prüfen: Tail-SI-Variable, Deklarations-/Aufrufumgebung und Identifieroperation bei Include.
- **Q-CXTM:** ISO/IEC 13250-4:2009 §§2 und 3.16, insbesondere der dateTime-Zweig und einschlägige Berichtigungen. Ergänzend §§3.13,3.17–3.18 für Identifierdarstellung. Bei bestätigtem Wortlaut können die beiden bedingten B-Schlussfolgerungen abschließend bewertet werden; der unveränderte Bytevergleich bleibt trotzdem FAIL.
- **Q-XTM-LOOP:** Veröffentlichung/Interpretation zu ISO/IEC 13250-3:2007 §§4.2,4.21,5 und wiederholter Dokument-IRI, gegebenenfalls einschlägige SC-34-Klarstellung. Fehlt eine eindeutige Vorgabe, muss der Auftraggeber eine explizite Modell- und Verfahrensabnahme vereinbaren.
- **Q-ERRATA:** Vor uneingeschränkter Gesamtkonformität die einschlägigen Berichtigungen und Publikationsgleichheit bestätigen. Ein aktueller Katalogeintrag ersetzt keinen Klauselabgleich. Keine automatische Beschaffung in diesem Slice.

Der historische [22A-Abschlussplan](slice-22a-conformance-closure.md) bleibt unverändert. Folgende Auswirkungen sind Vorschläge, keine freigegebenen Implementierungsaufträge:

| Geplanter Slice | Auswirkung von 22C |
|---|---|
| 22D — weitere textuelle Datentypen | Unabhängiger Umfang kann separat beauftragt werden; löst keine der hiesigen Editionsfragen. |
| 22E — Occurrences | Eigenständige native/API-Abnahme bleibt erforderlich; keine Anpassung der CTM-DateTime-FAILs einschleusen. |
| 22F — Associations/Roles | Unabhängige Original- und Modellabnahme wie geplant. |
| 22G — Association-/Role-Reification | Weiter abhängig von 22F; keine Änderung aus diesem Slice. |
| 22H — XTM mergeMap | Nichtzyklischen Inhaltsimport getrennt von Root-Metadaten und Zyklen abnehmen. Map-II-Original nicht als sicheren zusätzlichen PASS planen; Loop erst nach Q-XTM-LOOP. |
| 22I — übrige Profil-Lücken | Q-CTM/Q-CXTM und explizite Editionswahl berücksichtigen. Keine stillschweigende Kompatibilitätsgrammatik oder XSD-1.1-Umstellung. |
| 22J — Abschlussaudit | Alle 397 Originalstatus unverändert nachvollziehen; bedingte B/C-Fälle und vereinbarte Ausnahmen separat abschließen. Keine PASS-Zahl aus Norminterpretation. |

22D–22G müssen nicht pauschal auf jede Editionsfrage warten, sofern ihr eigener Auftrag und Normbezug geklärt sind. Die Tore normative Gesamtkonformität, Testsuite-Abschluss und HyperDoc-Integration bleiben offen. Dieser Slice beendet nur die beauftragte Untersuchung einschließlich konkret benannter Lücken.

## Vollständige Offline-Regression und Reproduktion

Die frische volle Regression lief vom **2026-10-20 13:53:55 UTC bis 13:57:21 UTC** über den unveränderten `scripts/validate-slice-22b.py`. Alle Lisp-Prozesse verwenden SBCL 2.5.4 mit `--no-sysinit --no-userinit`. Testkindprozesse sperren Netzwerk sowie Schreibzugriffe auf Topic Maps und HyperDoc. Builds/Ergebnisse liegen während der Ausführung außerhalb beider Repositories. Vorhandene gepinnte Abhängigkeiten, keine Downloads oder langlebigen Images.

| Bereich | Tatsächliches Ergebnis |
|---|---:|
| TMDM/CTM/CXTM einschließlich Include/Mergemap | 12.100 Checks |
| XTM einschließlich aller bisherigen Originale | 2.396 Checks; 63 positive + 8 negative Originale |
| XML-Qualifikation | 146 Checks |
| CTM/XTM-Mergemap | 217 Checks |
| Registrierte CTM positive / negative Originale | 286 / 25 Checks |
| Prolog / empty2 / CTM-Integer / Triple / Encoding | 171 / 13 / 112 / 226 / 722 Checks |
| Python / NFC-Oracle | 2 Tests / 16.294 Vergleiche |
| Executor-Fehlerkontrollen | 108, alle erwarteter Exit 1 |
| Volle Regression | 114 Prozesse, davon 6 regulär Exit 0 |
| Reader-Diagnosen | alle 124 vollständig bytegleich zu 22B |
| Verhaltensevidenz gegenüber 22B | 159 JSON-Berichte byteidentisch |
| Zusätzliche Beobachtung | 11 CTM-Originale, 12 vorhandene Kontextproben, 2 Hilfsquellen; keine Registrierung |

[Regression mit allen Kommandos/Exitcodes](../reports/slice-22c/regression/execution.json), [22C-Ausführung](../reports/slice-22c/execution.json), [159 Vergleiche](../reports/slice-22c/regression-comparison.json), [CTM-/Kontextvergleich](../reports/slice-22c/observation-comparison.json). Historische Felder des unveränderten 22B-Validators, beispielsweise „newPositiveOriginals: 1“, beschreiben dessen ursprüngliche Registrierung. Der übergeordnete 22C-Bericht weist **newOriginalPASS: 0** und gleiche Vorher-/Nachherzahlen aus.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 reports/slice-22c/reproduce.py \
  --output /private/tmp/topic-maps-22c-reproduction
PYTHONDONTWRITEBYTECODE=1 python3 reports/slice-22c/build-evidence.py \
  --execution /private/tmp/topic-maps-22c-reproduction \
  --regression /private/tmp/topic-maps-22c-reproduction/regression \
  --output /private/tmp/topic-maps-22c-case-evidence
```

Der Default startet die vollständige aktuelle Regression. Der hier tatsächlich verwendete `--reuse-regression`-Pfad verweist auf die unmittelbar zuvor frisch ausgeführte 114-Prozess-Regression; er spart keine erforderliche Prüfung aus. Der Builder verbindet die erneuten Beobachtungen mit den dokumentierten Entscheidungen und prüft originale Bytes/Variablenpositionen; er führt keine automatische Online-Normprüfung durch. Ausführungslogs und Quellhashes sind erhalten. `reports/slice-22c/audit-evidence.py --output /private/tmp/topic-maps-22c-audit` prüft anschließend die gelieferte Evidenz lesend; auch dieses Werkzeug schreibt ausschließlich außerhalb beider Repositories.

Alle **6.891** Ausgangsdateien, darunter **4.615 historische Reportdateien**, bleiben bytegleich. Alle **2.006** gepinnten Korpusdateien wurden nach Größe und SHA-256 geprüft. [Integrität](../reports/slice-22c/integrity.json), [Abschlussaudit](../reports/slice-22c/precommit-audit.json) und [Liefermanifest](../reports/slice-22c/artifacts.json) dokumentieren den Nachweis. Beim ursprünglichen erfolgreichen Audit stand HyperDoc sauber auf `306b7fd99fc2611a248e0927ce52a808abb7cc76`, mit denselben 14 früher inspizierten Quellhashes; dieses Audit ist unverändert als [audit-before-resume.json](../reports/slice-22c/audit-before-resume.json) erhalten. Bei der vom Nutzer angeforderten Fortsetzung wurde ein zwischenzeitlicher, außerhalb dieses Slice entstandener HyperDoc-Commit `0cc5ce5aeb20e683c886c0e30b2d305be92e2136` (20.10.2026, 19:25:40 +02:00) beobachtet: Arbeitsbaum sauber, sechs Pfade verändert, darunter einer der 14 inspizierten Pfade. Das Abschlussaudit dokumentiert diese Abweichung ausdrücklich. Die abgeschlossene Regression lag zeitlich davor und sperrte HyperDoc-Schreibzugriffe; Slice 22C hat dort ausschließlich gelesen und nichts zurückgesetzt oder übernommen.

Der normale Sandboxstart scheiterte am vorhandenen symlinkten Schreibroot `~/.nix-profile`; der genaue Fehler steht im Audit. Danach wurden regulär freigeprüfte Aufrufe mit kanonischem SBCL-Pfad und expliziter Kindprozess-Sandbox verwendet. Keine Änderung an Symlink oder Sandboxkonfiguration, keine Umgehung einer Freigabeprüfung.

Der Commit enthält ausschließlich neue Dokumentation, Untersuchungswerkzeuge und Ausführungsevidenz. Keine Produktions-, Test-, Registrierungs-, Korpus-, Baseline-, historische Report- oder HyperDoc-Änderung; kein Push/Deployment. Ende Slice 22C.
