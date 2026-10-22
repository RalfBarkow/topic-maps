# Slice 22E — Nichtzyklisches XTM mergeMap

Stand: 22. Oktober 2026. Basis/Parent: `791969ca59922d61e967198eaee4c1fe172b5a0d`; Branch `codex/xtm-slice-22e`.

Nichtzyklisches `<mergeMap>` wird jetzt mit expliziter Ressourcenauflösung, eigener Kind-Document-IRI, qualifiziertem XML-Byteparser und vorhandener TMDM-Inhaltsimportoperation verarbeitet. Source Keys bleiben diagnostisch. Die Topics und Associations der Kindmap werden kopiert und mit den Zielidentitäten normalisiert; ihre Map-Item-Identifier und ihr Map-Reifier werden nicht auf die Zielmap übertragen.

**Der Originalvertrag `mergemap-itemid.xtm` bleibt NOT-RUN.** Der Inhaltsimport gelingt, aber seine historische Baseline erwartet zusätzlich den Map-Item-Identifier des Kindes auf der Zielmap. Das tatsächliche Ergebnis hat 224 statt 314 Bytes; die erste Abweichung liegt bei Byteindex 12. Keine Map-Identitätsregel wurde an diese Baseline angepasst. Auch `mergemap-loop.xtm` bleibt NOT-RUN; seine vorsorgliche Zykluszurückweisung ist keine normative Zyklusentscheidung.

| Korpus | Vorher PASS / FAIL / NOT-RUN | Tatsächlich nach Regression PASS / FAIL / NOT-RUN |
|---|---|---|
| XTM 2.0 | 72 / 0 / 52 | 72 / 0 / 52 |
| CTM | 262 / 4 / 7 | 262 / 4 / 7 |
| Gesamt | 334 / 4 / 59 | 334 / 4 / 59 |

## Normative Grundlage und Grenze

**Derived:** [XTM 2.0 §§4.2–4.4 und 4.21](https://www.isotopicmaps.org/sam/sam-xtm/) ordnet `mergeMap` vor die lokalen Topic-/Association-Elemente ein. Seine fragmentfreie `href`-IRI wird relativ zur referenzierenden Document IRI aufgelöst. Die Ressourcenbytes werden als XML verarbeitet und mit ihrer eigenen IRI in eine eigenständige TMDM-Map deserialisiert. Anschließend werden deren Topics und Associations in die aktuelle Map übernommen. Dabei können weitere TMDM-Merges entstehen. Eine Übertragung des Quell-Map-Items oder seiner Metadaten wird dort nicht angeordnet.

**Derived:** [TMDM §§5.1–5.2 und 6.1–6.2](https://www.isotopicmaps.org/sam/sam-model/2006-06-18/) trennt Map, Topics und Associations sowie deren Item-Identifier und Reification. Gleiche Topic-Identitäten führen nach dem Inhaltsimport zu nativen Merges. Die beiden dokumentqualifizierten `#topic`-Identifier des Originals sind dagegen verschieden.

Die bereits in [22C](slice-22c-normative-decisions.md) belegte fehlende nichtzyklische Importfähigkeit ist in diesem begrenzten Umfang umgesetzt. Der gesonderte Baselinekonflikt und die offene Zyklusfrage werden davon getrennt. Die öffentlichen XTM-/TMDM-Fassungen erklären redaktionell Identität mit der veröffentlichten Norm; ein unabhängiger PDF-Abgleich erfolgte weiterhin nicht. Die zwölf offenen C-Entscheidungen aus 22C werden nicht neu entschieden. Historische Dokumente bleiben unverändert. [Neue Quellen-/Ableitungsevidenz](../reports/slice-22e/normative-review.json).

`observed` bezeichnet hier wirklich gelesene Bytes und ausgeführte Prüfungen; `derived` die benannte Normherleitung; die Zyklus-/Tiefengrenze ist ausdrücklich Implementierungspolitik. Keine neue Normkopie oder Abhängigkeit wurde heruntergeladen.

## Resolver- und Deserialisierungsvertrag

Die vorhandene API bleibt kompatibel:

```lisp
(topic-maps.xtm:deserialize-octets raw-octets
  :document-iri "https://example.invalid/root.xtm"
  :source-key "diagnostic:root"
  :resource-resolver resolver
  :max-resource-depth 32)
```

Die beiden letzten Argumente sind optional. Der Resolver wird für jedes tatsächlich verarbeitete `mergeMap` so aufgerufen:

```lisp
(funcall resolver absolute-resource-iri
  :purpose :mergemap
  :from-document-iri referring-document-iri
  :notation "http://psi.topicmaps.org/iso13250/xtm")
;; => (values raw-octet-vector optional-diagnostic-source-key)
```

Dies entspricht der bereits vorhandenen CTM-Resolver-Konvention. Die XTM-Verarbeitung hängt trotzdem nicht vom CTM-Reader ab. Ein eigenständiger öffentlicher XTM-Aufruf startet einen eigenen Rekursionspfad; verschachtelte XTM-Aufrufe übernehmen ausdrücklich ihren XTM-Resolver und dessen Tiefenlimit. Es werden keine CTM-Parser-, Include-, Template- oder Wildcard-Kontexte übernommen.

Ein spezialisierter Bytevektor bleibt bis `topic-maps.xml:parse-octets` dasselbe Objekt (`EQ`). Wie beim bestehenden CTM-Resolver sind auch generische Vektoren mit Bytewerten zulässig; nur deren Speicherrepräsentation wird spezialisiert. XML wird dabei nicht vorab dekodiert und neu kodiert. Fehlender Source Key fällt auf die absolute Ressourcen-IRI zurück. Der Source Key bestimmt niemals Topic-Identität.

Es gibt keinen Netzwerk-/Dateisystemfallback und keinen impliziten Resolver. Kein öffentlich übergebenes Map-Objekt wird mutiert. Validierung geschieht vor Modellaufbau und Ressourcenauflösung; Syntaxfehler können deshalb ohne Resolveraufruf zurückgewiesen werden. Resolverfehler werden als neue öffentliche `XTM-RESOURCE-ERROR` mit `error-cause` gemeldet. Kind-XML-/XTM-Conditions behalten Kind-Document-IRI und Kind-Source-Key. Native Importkonflikte werden an der referenzierenden `mergeMap`-Position mit derselben ursprünglichen Condition als Cause dokumentiert.

**CTM/XTM-Adapter:** `src/ctm/xtm.lisp` bleibt unverändert und erhält keine neue implizite Resolverweitergabe. Der schon vorhandene CTM-Resolververtrag wird nur als API-Konvention wiederverwendet. Die bestehende CTM-Adapter-Gegenprobe für ein XTM-Kind mit `mergeMap` prüft daher jetzt die spezifisch fehlende XTM-Resolverfreigabe. CTM `%mergemap` und XTM `<mergeMap>` bleiben verschiedene Syntaxoperationen.

## TMDM-Import, Identität und Quellmap

`read-mergemap` lässt das Kind durch den privaten XTM-Dokumentlesepfad in eine neue Map deserialisieren. Anschließend verwendet es unverändert `topic-maps.tmdm:import-map-content`. Dessen vorhandener Copy-/Preflight-/Normalisierungspfad erhält die Quellmap und kopiert die Inhaltsobjekte mit umgeschriebenen Referenzen. Die zweite Rückgabe ist die bestehende native Zuordnungsfunktion für kanonische Zielrepräsentanten; Tests beobachten diese wirkliche Funktion auch nach späteren lokalen Topic-Merges.

**Observed:** Die Tests prüfen `EQ` für aktuelle Topic-/Name-/Variant-/Occurrence-/Association-/Role-Referenzen, Parents, Type, Player, Scope, Reifier und inverse Beziehungen. SI-, SL- und II-Merging werden getrennt geprüft. Identische lokale Fragmentnamen unter verschiedenen Document IRIs bleiben verschieden. Source-Key-Änderungen erzeugen identische Werte und CXTM-Bytes.

Quell-Map-Identifier und Quell-Map-Reifier werden nicht übernommen. Der Topic, der die Quellmap reifiziert, gehört zu deren Inhalt und kann als gewöhnlicher Topic importiert werden; seine Beziehung zur Quellmap wird nicht auf die Zielmap kopiert. Wenn seine Identität später mit dem vorhandenen Ziel-Map-Reifier zusammenfällt, erfolgt ein gewöhnlicher nativer Topic-Merge mit kanonischer Ziel-Reifier-Inverse. Das ist keine Übernahme der Quell-Map-Metadaten. Eigene Topic-/Name-/Variant-/Occurrence-/Association-/Role-Item-Identifier werden dagegen erhalten.

Die Quellmaps bleiben einschließlich gehaltenen Handles, Forwarding-Referenzen, Werten und CXTM unverändert. Wiederholte CXTM-Kanonisierung ist deterministisch und modellunverändernd. Importkonflikte werden durch die vorhandene TMDM-Vorprüfung atomar abgewiesen.

## Originalvertrag mit unveränderten Ressourcen

Root: [mergemap-itemid.xtm](../vendor/cxtm/xtm2/in/mergemap-itemid.xtm)

```xml
<topicMap xmlns="http://www.topicmaps.org/xtm/" version="2.0">
  <mergeMap href="mergemap-itemid.sub"/>
  <topic id="topic">
  </topic>
</topicMap>
```

Kind: [mergemap-itemid.sub](../vendor/cxtm/xtm2/in/mergemap-itemid.sub)

```xml
<topicMap xmlns="http://www.topicmaps.org/xtm/" version="2.0">
  <itemIdentity href="#the-topic-map"/>
  <topic id="topic">
  </topic>
</topicMap>
```

Die lesbare Kinddarstellung lässt die Leerzeichen hinter dem öffnenden Topic-Tag weg; die vollständigen Originalbytes werden als Hex und Text beziehungsweise Kind-Hex gesichert.

| Daten | Größe / SHA-256 |
|---|---|
| Rootquelle | 148 Bytes; `23de617d6e201374ec3f9c12e02be88bc555dd7dbcd262e854c8e9a3f96966d1` |
| Kindquelle | 151 Bytes; `20cfc5dafa42543648b9f3ee4f41434f56f7fe7679afb0f4a1c870bde2415c01` |
| unveränderte CXTM-Baseline | 314 Bytes; `03c5c1694e572674c0982f3b01d8c2fb323159ba6436857924814ea1e7a2d5d7` |
| tatsächliche CXTM-Ausgabe | 224 Bytes; `ddbdfd9384267ec8d71fc5e56218c3b3b6680efdc232830c904c9aa3f52ec62a` |
| erste abweichende Position | nullbasierter Byteindex 12; Ist `t`, Soll `i` |
| Condition / Code / Position / Cause beim Inhaltsimport | null / null / null / null |
| registrierter Status | NOT-RUN; kein neuer Case Record und kein PASS |

Root-Document-IRI: `https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/mergemap-itemid.xtm`. Die Kind-IRI entsteht daraus als `.../xtm2/in/mergemap-itemid.sub`, nicht aus dem Source Key.

Das tatsächliche Modell enthält genau zwei Topics mit II `Root-IRI#topic` beziehungsweise `Kind-IRI#topic`; beide sind verschieden und haben keine SI/SL oder Statements. Keine Associations, Map-Reifier oder weiteren Inhaltsidentifikatoren. Die Quellmap behält ihren Map-II `Kind-IRI#the-topic-map`, die Zielmap hat keine Map-II.

Die Baseline setzt zusätzlich genau diesen Quell-Map-II auf die Zielmap. Entfernt man allein den entsprechenden Root-XML-Block in einer temporären Vergleichszeichenfolge, sind alle verbleibenden Baselinebytes mit der tatsächlichen Ausgabe identisch. Das ist ein Nachweis der verursachenden Eigenschaft; weder Baseline noch tatsächliche Map werden dafür angepasst. [Vollständige Originalbeobachtungen](../reports/slice-22e/after/original-observations.json), [wirkliche Ist-CXTM-Datei](../reports/slice-22e/after/actual/mergemap-itemid.xtm.cxtm).

## Gegenproben und Implementierungsgrenzen

Der bestehende ASDF-Testpfad lädt `tests/xtm-mergemap.lisp` und ruft `mergemap-tests` tatsächlich auf. Es entstehen keine neuen ASDF-Systeme oder alternativen Modellrepräsentationen. 182 neue Checks ergänzen die bisherigen 2.522 zu insgesamt **2.704 erfolgreichen XTM-Checks**. Die 72 vorhandenen Original-Case-Records bleiben vollständig gleich.

Positive Gegenproben umfassen relative/absolute IRIs, Unicode-Prozentnotation, Query, exakte Resolverargumente, Source-Key-Unabhängigkeit, mehrere und wiederholte Imports, verschachtelte Imports, UTF-16-Kindbytes, Names/Variants mit allen bisher unterstützten Ressourcenwertpfaden, SI-/SL-/II-Merging, Map-Metadaten und Reifier-Identitätsmerges. Wiederholte Geschwisterimports werden wirklich ausgeführt; ein globales „visited, also überspringen“ wird nicht eingeführt.

**Native Inhaltstests:** Ein wirklicher XML-Import erzeugt Names, Variants und über `instanceOf` bereits unterstützte Associations/Roles. Für den zusätzlichen Importnachweis von Occurrences und expliziten Associations/Roles ergänzt der Test die echte deserialisierte Kindmap vor dem unveränderten TMDM-Import mit vorhandenen nativen APIs. Der Test kennzeichnet dies ausdrücklich als native Vorbereitung. Diese Gegenprobe implementiert keine neue XML-Sprache und zählt nicht als Originalvertrag. XTM-Occurrence-/explizite Association-Deserialisierung bleiben unverändert außerhalb dieses Slices.

Negative Gegenproben unterscheiden fehlenden Resolver, verweigerte oder nicht gelieferte Ressourcen, ungültige Rückgaben, fehlerhaftes XML/UTF-8, leere Bytes, DOCTYPE, ungültige XTM-Strukturen, fragmentbehaftete oder fehlerhaft escaped IRIs, Kindreihenfolge und native Importkonflikte. Bei einer leeren Ressource liegt vor dem ersten SAX-Ereignis keine bekannte Zeilen-/Spaltenposition vor; null wird erhalten statt erfunden.

| Situation | Tatsächliche Condition / Code | Kontext / Cause |
|---|---|---|
| Resolver fehlt | XTM-UNSUPPORTED / resource-resolver-required | referenzierende Map; z.B. 1:91 |
| Resolver liefert keine Ressource | XTM-RESOURCE-ERROR / resource-unavailable | referenzierende Map; Cause null |
| Resolver verweigert mit Fehler | XTM-RESOURCE-ERROR / resource-resolver-failure | Cause dasselbe Fehlerobjekt (`EQ`) |
| ungültige Resolverrückgabe | XTM-RESOURCE-ERROR / invalid-resource-result | referenzierende Map |
| fehlerhaftes Kind-XML | XTM-XML-ERROR / xml-not-well-formed | Kind-IRI/Source Key; originale XML-Cause |
| fragmentbehaftetes href | XTM-REJECTION / mergemap-fragment | kein Resolveraufruf |
| Item-Identifier-Importkonflikt | XTM-RESOURCE-ERROR / mergemap-import-failure | Cause ITEM-IDENTIFIER-ERROR / duplicate-item-identifier; beide Graphen unverändert |
| Reifier-Importkonflikt | XTM-RESOURCE-ERROR / mergemap-import-failure | Cause REIFICATION-ERROR / reifier-conflict; beide Graphen unverändert |

Die Tests enthalten 49 Kontrollbeobachtungen; vollständige positive Modelle, Parser-/Resolveraufrufe und Conditions stehen in [xtm.json](../reports/slice-22e/after/xtm.json).

**Zyklen und Tiefe:** Ein aktiver Pfad aufgelöster Document IRIs verhindert unmittelbare und mittelbare Rekursion. Zusätzlich begrenzt `max-resource-depth` standardmäßig auf 32 verschachtelte Ressourcen; null verbietet den ersten Import. Dies sind dokumentierte Betriebsgrenzen, keine normative Ungültigkeitserklärung. Öffentliche reentrante XTM-Aufrufe starten unabhängige Pfade.

Das unveränderte zyklische Original wird mit explizitem gepinntem Resolver nach genau einem Ressourcenabruf im Sub-Dokument bei ungefähr 2:39 als `XTM-UNSUPPORTED/:cyclic-mergemap` zurückgewiesen. Kein unvollständiges Modell wird als Ergebnis ausgegeben und kein PASS registriert. Die normative endliche Zyklusverarbeitung bleibt offen.

`xsd:anyType` bleibt ein gültiger, noch nicht implementierter normativer Datentyp mit seiner besonderen XML-Kanonisierung, geplant für **Slice 22I**. Keine XTM-2.1-Merkmale, CTM-Semantikänderungen oder historische Kompatibilitätsregeln wurden ergänzt.

## Diagnosedelta, Retargetings und vollständige Regression

Vor den Änderungen wurden 2.522 XTM-Checks, alle 72 Original-PASS und sämtliche 124 Reader-Diagnosen frisch offline reproduziert. Die vollständige vorherige 22D-Regression wurde anhand ihres vorhandenen Artefakt-/Quellhashmanifests verifiziert. Sie wird nicht als erneut ausgeführt dargestellt. [Frischer Ausgangslauf](../reports/slice-22e/baseline/execution.json), [gesicherter Ausgangszustand](../reports/slice-22e/initial-state.json).

Ohne optionalen Resolver ändern sich genau die sieben bisherigen MergeMap-Originaldiagnosen (`mergemap-itemid.xtm`, `mergemap-loop.xtm`, `mergemap-merge.xtm`, `mergemap-ontopia-issue-28-2.xtm`, `mergemap-ontopia-issue-28.xtm`, `mergemap-tm-reifier.xtm`, `mergemap.xtm`): statt pauschal `unsupported-construct` lautet die spezifische Ursache jetzt `resource-resolver-required`. Die übrigen **117 Diagnosen sind vollständig unverändert**. Die getrennten Beobachtungen mit explizitem Resolver dokumentieren erfolgreichen Inhaltsimport beziehungsweise die Zyklusschutzgrenze; sie verändern keine registrierten Status. [Diagnosedelta](../reports/slice-22e/after/diagnostic-changes.json).

Drei bestehende Unsupported-Erwartungen werden präzisiert: Standalone-XTM, Map-Reification und CTM/XTM-Adapter. Die unveränderte gültige MergeMap-Prüfquelle scheitert jetzt am fehlenden expliziten XTM-Resolver. Condition-Klasse, Quellkontext und die CTM-Adapter-Cause bleiben erhalten; Fehlercode und Meldung werden angepasst. [Exakte alte/neue Erwartungen](../reports/slice-22e/retargetings.json), [beobachtete XTM-Änderung](../reports/slice-22e/after/retargeted-observations.json), [einzelnes Adapter-Berichtsfeld](../reports/slice-22e/after/adapter-retargeting.json).

Die vollständige Regression verwendet den unveränderten vorhandenen Offline-Collector aus `scripts/validate-slice-22d.py` und dessen 113 Executor-Fehlerkontrollen. Alle Kontroll-Case-Records, Status und Outcomes bleiben gegenüber 22D gleich; bisherige korrekte PASS bleiben erhalten. Die neue fehlende-Resolver-Ursache der vorhandenen Map-Reification-Gegenprobe ist im Audit ausdrücklich dokumentiert. Kein Fehlerlauf zählt als positiver Originalvergleich.

| Regressionsteil | Tatsächliches Ergebnis |
|---|---:|
| TMDM / CTM / CXTM einschließlich Include / Mergemap | 12.100 Checks |
| Standalone-XTM | 2.704 Checks, 64 positive und acht negative Original-PASS |
| XML-Qualifikation | 146 Checks |
| CTM/XTM-Mergemap | 217 Checks |
| registrierte CTM-Originale positiv / negativ | 286 / 25 Checks |
| Prolog / empty2 / CTM-Integer / Triple / Encoding | 171 / 13 / 112 / 226 / 722 Checks |
| Python-Unittests | 2 |
| NFC-Oracle | 16.294 Vergleiche |
| Executor-Fehlerkontrollen | 113, alle erwarteten Exit 1 |
| unveränderte Nicht-XTM-Berichte | 47 byteidentisch; ein Adapter-Kontrollcode präzisiert |
| gepinnter Korpus | 2.006 Größen-/SHA-256-Prüfungen bestanden |
| historische Berichtsdateien | 5.520 SHA-256-Prüfungen bestanden |

Der Endlauf umfasst 119 isolierte Prozesse: sechs reguläre mit Exit 0 und 113 erwartete Fehlerkontrollen. SBCL 2.5.4 wird ohne System-/Benutzerinitialisierung gestartet. Netzwerk und Repository-Schreibzugriff sind für Testprozesse gesperrt; gepinnte lokale Abhängigkeiten und temporäre Buildkopien werden verwendet. Ein anfänglicher regulärer Sandbox-Start konnte wegen des unveränderten Symlinks `~/.nix-profile` nicht ausgeführt werden; die reguläre Freigabe funktionierte. Keine Änderung an Symlink/Konfiguration und keine Umgehung einer Freigabeprüfung. [Umgebungsereignis](../reports/slice-22e/environment-events.json).

Der Diagnoseaudit ermittelte alle sieben von der allgemeinen MergeMap-Fähigkeit betroffenen Quellen statt nur der zwei gesondert untersuchten Originale. Außerdem musste der Auswertungsschritt das zusätzliche `expectedCode`-Metadatenfeld der dokumentierten Gegenprobe berücksichtigen. Die bereits vollständig ausgeführten Tests wurden deswegen nicht wiederholt; `--audit-only` verifiziert ihre gespeicherten Logs, Sourcehashes, Berichte und Exitcodes. [Akzeptierte Ausführung](../reports/slice-22e/after/execution.json), [Integrität](../reports/slice-22e/after/integrity.json), [abschließender Artefakt-/Git-Audit](../reports/slice-22e/final-audit.json).

Reproduktion der vollständigen Regression mit neuem Ausgabeordner außerhalb des Repositories:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate-slice-22e.py \
  --output /private/tmp/topic-maps-22e-new-run
```

Ausschließlich `src/xtm/package.lisp` und `src/xtm/reader.lisp` enthalten Produktionsänderungen. TMDM, CTM, CXTM, XML, Originalquellen, Baselines, Corpus-Lock und historische Berichte bleiben unverändert. Die vier bekannten CTM-FAILs sowie sämtliche bisherigen Original-PASS bleiben erhalten. HyperDoc bleibt unverändert. Keine Downloads, langlebigen Lisp-Images, Pushes oder Deployments. Slice 22E endet mit dem lokalen Commit von Implementierung, dauerhaften Tests und neuer Ausführungsevidenz.
