# Slice 22U — Die eigene Projektarbeit als Topicmap lesen und bearbeiten

## Ergebnis und Reichweite

Die kleine [CTM-Quelle](../examples/project-work.ctm) wird vom produktiven
`topic-maps.ctm:deserialize-string` gelesen. Das optionale
[Common-Lisp-Beispiel](../examples/project-work.lisp) arbeitet ausschließlich
mit öffentlichen TMDM-Operationen und CXTM. Die **27 dauerhaften Prüfungen**
in [tests/project-work.lisp](../tests/project-work.lisp) werden über die
[ASDF-Anbindung](../topic-maps.asd) im normalen
[Offline-Lauf](../scripts/fresh-sbcl.lisp) tatsächlich ausgeführt.

Beobachtet sind **21 native Topics** einschließlich des lokalen Vokabulars
und des impliziten Name-Type-Topics, **sechs Associations mit zwölf Roles**.
Sechs fachliche Gegenstände bilden den Ausschnitt: Projekt, Slice 22T, sein
Commit, seine Ausführungsevidenz, Q-XTM-LOOP und die dokumentierte Disposition
aus 22O. Hinzu kommt ein als Übung gekennzeichneter Scope-Topic. Lokale Type-
und Role-Topics dienen nur diesem Beispiel; es wird keine allgemeine
Projektmanagement-Ontologie oder standardisierte PSI-Sammlung eingeführt.

Das gehaltene Topic-Objekt zu Q-XTM-LOOP bleibt über die Übungsänderung hinweg
`EQ`. Die vorhandenen historischen Occurrence-Objekte bleiben erhalten.
Eine neue Occurrence ergänzt eine ausdrücklich gescopte Übungsnotiz. Ihr
Value lautet: „Uebung: Frage fuer die Lektuere markiert; kein historischer
Statuswechsel.“ Der Datentyp ist `xsd:string`, ihr Scope enthält ausschließlich
den Topic „Uebung; keine historische Aussage“. Der ursprüngliche ungescopte
Status „offene normative Frage“ wird weder ersetzt noch umgedeutet.

| Beobachtete Eigenschaft | Vorher | Nachher |
| --- | --- | --- |
| Gehaltener Q-XTM-LOOP-Topic | derselbe native Handle | `EQ` zum erneut gefundenen Topic |
| Topic-Identifikatoren | lokaler II und eigener SI | unverändert |
| Associations und Roles | sechs / zwölf | unverändert |
| Historische Aussagen und Quellen | aus CTM gelesen | unverändert |
| Übungsnotiz | nicht vorhanden | eine gescopte Occurrence |
| Vollständige CXTM-Ausgabe | 7.914 Bytes | 8.191 Bytes |
| Erste CXTM-Abweichung | — | Byte 5.141, nullbasiert |
| Erneutes Lesen derselben CTM-Datei | ursprüngliche Map | wieder ursprünglicher Zustand |

[Vollständiger nativer Zustand vorher](../reports/slice-22u/after/project-before-native.sexp),
[nachher](../reports/slice-22u/after/project-after-native.sexp),
[CXTM vorher](../reports/slice-22u/after/project-before.cxtm),
[nachher](../reports/slice-22u/after/project-after.cxtm),
[tatsächliche Ausgabe der Demonstration](../reports/slice-22u/after/project-repl.txt).
Die Zustandsansichten werden bei jedem Aufruf aus den nativen Items gelesen;
sie sind keine unabhängig gepflegte Projektdarstellung und kein zweites Modell.

## Sofort im frischen Lisp ausführen

Eine frische SBCL-Sitzung ohne Benutzer-/Systeminitialisierung starten,
z. B. mit `sbcl --no-sysinit --no-userinit`. Für die vollständige Abnahme wurde
SBCL 2.5.4 verwendet. Das Beispiel selbst benötigt keine XML-/CXML-Laufzeit;
es lädt nur die bestehenden CTM-, TMDM- und CXTM-Systeme über ASDF.
Die Beispielquelle ist absichtlich ASCII, damit ihre Leselogik ANSI-Common-Lisp-
Dateioperationen ohne implementierungsspezifisches External Format verwendet.
Die ASDF-Ladeschritte sind die vorhandene Projektinfrastruktur.

[Die folgenden Schritte als ausführbare Lisp-Datei](../reports/slice-22u/repl-steps.lisp)
lassen sich in der frischen Sitzung mit `LOAD` ausführen oder einzeln am REPL
untersuchen. Sie berühren keine SLY-Konfiguration oder laufende Lisp-Images.

```lisp
(require :asdf)
(asdf:initialize-source-registry '(:source-registry :ignore-inherited-configuration))
(asdf:load-asd #p"/Users/rgb/workspace/topic-maps/topic-maps.asd")
(asdf:load-system "topic-maps/project-work-example")
(use-package '(:topic-maps.tmdm :topic-maps.project-work.example))

(defparameter *example-source* #p"/Users/rgb/workspace/topic-maps/examples/project-work.ctm")
(defparameter *example-map* (load-map *example-source*))
(defparameter *held-question*
  (find-topic *example-map* "urn:topic-maps:question:Q-XTM-LOOP"))
(describe *held-question*)
(show-topic *held-question*)
;; Native Associations and their actual Role Items are navigable:
(dolist (association (relations *held-question*))
  (describe association)
  (dolist (role (association-roles association)) (describe role)))

(defparameter *before-edit*
  (topic-maps.cxtm:canonicalize-octets *example-map* :base-locator *document-iri*))
(defparameter *exercise-occurrence* (add-exercise-note *example-map*))
(assert (eq *held-question*
  (find-topic *example-map* "urn:topic-maps:question:Q-XTM-LOOP")))
(show-topic *held-question*)
(defparameter *after-edit*
  (topic-maps.cxtm:canonicalize-octets *example-map* :base-locator *document-iri*))
(list (length *before-edit*) (length *after-edit*) (mismatch *before-edit* *after-edit*))
;; => (7914 8191 5141); mismatch uses a zero-based byte position.

(defparameter *same-note-again* (add-exercise-note *example-map*))
(assert (eq (canonical-occurrence *exercise-occurrence*) *same-note-again*))
(assert (equalp *after-edit*
  (topic-maps.cxtm:canonicalize-octets *example-map* :base-locator *document-iri*)))
;; The original CTM is untouched; a fresh read contains no exercise annotation:
(defparameter *fresh-original* (load-map *example-source* :source-key "re-read original"))
(assert (equalp *before-edit*
  (topic-maps.cxtm:canonicalize-octets *fresh-original* :base-locator *document-iri*)))
```

Für eine kompakte Vorher-/Nachher-Lektüre auf einer jeweils frischen Map genügt:

```lisp
(topic-maps.project-work.example:demo
  #p"/Users/rgb/workspace/topic-maps/examples/project-work.ctm")
```

`demo` gibt als ersten Wert die tatsächlich veränderte native Map zurück.
Weitere Werte sind Vorher-/Nachher-Ansichten, die beiden vollständigen
CXTM-Octet-Vektoren, der Notiz-Handle, der ursprüngliche CTM-String, der vor der
Änderung gehaltene Frage-Topic und die vor der Änderung gehaltenen historischen
Occurrences. Damit lassen sich die gleichen Objekte weiter mit `DESCRIBE`
oder den öffentlichen Property-Lesern untersuchen.

## Gegenstände, Identität, Beziehungen und Belege

Die Document IRI und CXTM-Basis sind ausdrücklich
`https://topic-maps.example.invalid/examples/project-work.ctm`. Diese IRI
ist ein projektlokaler Identitätskontext; es wird nichts darüber abgerufen.
CTM-Identifier wie `question` ergeben Item Identifier unter dieser IRI mit
`#question`. Diagnostische Source Keys werden getrennt vergeben und sind keine
Topic-Identitäten.

Eigene `urn:topic-maps:*`-Subject-Identifier benennen Projekt, Slice, Commit,
Frage und Übung. Sie sind bewusste Identifier dieses Beispiels, keine neuen
historischen Tatsachen und keine veröffentlichten Standard-PSIs.
Die Dokument-Topics für Evidenz und Disposition tragen Subject Locators auf
konkrete Dateien. `file:`-IRIs sind in dieser Demonstration Daten; weder Reader
noch Query-Helfer laden ihre Ziele. Die absoluten Quellenpfade sind auf das
beauftragte Repository zugeschnitten und müssen bei einem Repository-Umzug
bewusst angepasst werden. Es gibt keinen versteckten Netzwerk- oder Dateiresolver.

| Modellierter Zusammenhang | Native Association und Roles |
| --- | --- |
| Slice gehört zum Projekt | `part-of(part: slice, whole: project)` |
| Commit ist ein Ergebnis des Slices | `result-of(result: commit, work: slice)` |
| Testevidenz ist ein Ergebnis des Slices | `result-of(result: evidence, work: slice)` |
| Projektarbeit betrifft die offene Frage | `concerns(work: project, subject: question)` |
| Quelle für den Umgang mit der Frage | `documented-by(subject: question, source: disposition)` |
| Quelle für die dokumentierte Slice-Abnahme | `documented-by(subject: slice, source: evidence)` |

Die Tabelle erläutert die CTM-Deklarationen. Die ausgeführten Abfragen nehmen
ihre Antworten aus den tatsächlichen `topic-roles-played`,
`association-role-parent`, `association-role-type` und `association-role-player`.
Alle Parent-, Type-, Player- und Scope-Referenzen werden auf kanonische `EQ`-
Objekte derselben Map geprüft, einschließlich inverser `rolesPlayed`-Beziehungen.
Die Namen erleichtern das Lesen; identifiziert wird nicht allein durch Namen.
`find-topic` ist lediglich eine lineare Suche in den öffentlichen Topic-Mengen.
Es gibt keinen zusätzlichen Identitätsindex oder unabhängigen Beziehungsgraphen.

**Geprüfte historische Quellen:**

- [22T-Abschlussbericht](slice-22t-ctm-xtm-anytype-equivalence.md): dokumentierter
  Abschluss des Slices, zugehöriger Commit und die Grenzen des Austauschnachweises.
- [22T-Ausführungsevidenz](../reports/slice-22t/after/execution.json):
  `acceptancePassed=true`, 34 Reader-Paare, vier Kontraste, 728 Äquivalenzchecks.
- [22O-Disposition zu Q-XTM-LOOP](slice-22o-qualified-xtm-corpus-disposition.md),
  Abschnitt „Normative Konformität / offene Frage Q-XTM-LOOP“ und „Disposition“:
  ungeklärter normativer Zyklusabschluss, bestehende Unsupported-Grenze und
  unveränderter Originalstatus NOT-RUN.

Die Daten in der kleinen CTM-Map sind eine quellengebundene manuelle Auswahl,
kein automatischer Import aller Projektdokumente. Die tatsächlichen aus den
nativen Items gelesenen Fakten und ihre überprüften Dateihashes stehen im
[Quellenaudit](../reports/slice-22u/after/source-grounding.json).
Damit wird keine neue Normentscheidung getroffen. Insbesondere wird aus der
Übungsnotiz weder eine Priorisierung noch eine Freigabe der Zyklusimplementierung
abgeleitet.

## Was die Bearbeitung tatsächlich tut

`add-exercise-note` ruft die bestehende öffentliche Operation
`topic-maps.tmdm:add-occurrence` auf dem kanonischen Frage-Topic auf. Es werden
keine privaten Slots beschrieben. Der Topic erhält eine zusätzliche Characteristic;
seine Identität und die Projektbeziehungen bleiben erhalten. Der Scope trennt
bewusst die Übungsannotation von ungescopten historischen Aussagen; er ist
keine Zugriffskontrolle und kein automatisches Wahrheits-/Provenienzsystem.

Die zweimalige Eingabe derselben Notiz demonstriert die bestehende
Occurrence-Gleichheit anhand von Parent, Type, Scope, Value und Datatype.
Die beiden Notizen fallen auf ein kanonisches Item zusammen. Der zuerst
gehaltene Occurrence-Handle ist danach in der beobachteten Implementierung
nicht mehr selbst `EQ` zum lebenden Item; `canonical-occurrence` löst ihn
weiterhin auf dasselbe Item wie den Rückgabewert des zweiten Aufrufs auf.
Die zweite Annotation verändert die CXTM-Bytes nicht nochmals. Das ist von der
unveränderten `EQ`-Identität des Frage-Topics zu unterscheiden.

`intern-topic` mit einem schon vorhandenen Subject Identifier bzw. Subject
Locator liefert denselben nativen Topic, ohne eine zweite Darstellung zu
bauen. SI, SL und II bleiben getrennte Kategorien. `normalize-topic-map` ist
nach der Änderung idempotent. Ein Versuch mit einem Type aus einer fremden
Map erreicht die native `occurrence-error` mit Code `:foreign-type`; Modell
und CXTM bleiben dabei unverändert.

Es gelten drei unterschiedliche Bearbeitungsebenen:

1. **Native Map im Arbeitsspeicher:** `add-occurrence` verändert die Map dieser
   Lisp-Sitzung. Die Property-Leser geben schützende Kopien ihrer Mengen zurück;
   private Setter sind kein Bearbeitungspfad.
2. **CTM-Quelle:** Die ursprüngliche Datei wird durch diese Operation nicht
   geändert. Erneutes Deserialisieren liefert den ursprünglichen Zustand.
   Das Beispiel entwickelt keinen CTM-Writer und keinen Source-Patch-/Roundtrip-Pfad.
3. **Dauerhafte Speicherung:** Die Beispielquelle und Programme sind versionierte
   Dateien; die native Übungsänderung wird nicht automatisch gespeichert.
   Die vorhandene CXTM-Ausgabe kann explizit als Datei geschrieben werden,
   ist hier jedoch Ausführungsevidenz und kein nachgewiesener wieder einlesbarer
   Workspace-/Bearbeitungszustand. Transaktionen, Undo, eine Map-Datenbank und
   Sitzungswiederaufnahme werden nicht behauptet.

## Abnahme und erhaltene Verträge

[27 ausgeführte Beispielprüfungen und vollständige native Beobachtung](../reports/slice-22u/after/retained/core.json.project-work.json),
[Vollregression](../reports/slice-22u/after/execution.json),
[Kommandos, Zeiten und Loghashes](../reports/slice-22u/after/runs.json).
Die Quelle wurde mit beiden diagnostischen Source Keys produktiv gelesen;
ihre Datei bleibt unverändert. Wiederholte Kanonisierung erhält alle geprüften
Eigenschaften und gehaltenen kanonischen Referenzen.

Der bereits gestartete Lauf endete vollständig mit **119 erwarteten Prozessausgängen**,
inklusive aller **113 unveränderten Executor-Fehlerkontrollen**. Bei der Fortsetzung
wurde dieser gespeicherte Lauf mit `--audit-only` und den aktuellen Quellhashes
nochmals überprüft; er wird nicht als neu durchgeführter Testlauf ausgegeben.
Die isolierten Vorläufe sind in `reports/slice-22u/` getrennt erhalten. Die
nachträgliche Lektüreprüfung wird gesondert protokolliert.

Erhalten: 12.100 Kernchecks, 4.327 XTM-Checks, 146 XML-Prüfungen, alle bisherigen
Slice-20-/22-Stufen, CTM/XTM- und XTM-Mergemap, 34 Äquivalenzpaare und vier
Kontraste mit 728 Checks, zwei Python-Tests und 16.294 NFC-Vergleiche.
Sämtliche bisherigen gespeicherten Regressionsberichte sind byteidentisch;
neu hinzu kommt nur der gesonderte Projektbeispielbericht.
[Berichtsvergleich](../reports/slice-22u/after/retained-reports.json),
[Fehlerkontrollen](../reports/slice-22u/after/failure-controls-audit.json),
[124 unveränderte Originaldiagnosen](../reports/slice-22u/after/diagnostic-changes.json).

| Originalkorpus | PASS | FAIL | NOT-RUN |
| --- | ---: | ---: | ---: |
| XTM 2.0 | 121 | 0 | 3 |
| CTM | 262 | 4 | 7 |

Das Lernbeispiel ist kein neuer Originalkorpusvertrag und erzeugt keine
PASS-Registrierung. Sämtliche gepinnten Originale, Baselines, Case Records und
historischen Reports bleiben unverändert. [Integritätsnachweis](../reports/slice-22u/after/integrity.json): **11.912**
geschützte Basisdateien sind unverändert, darunter **2.006** Korpusdateien und
**9.590** historische Reportdateien. Alle Produktionsdateien unter `src/`
sowie `flake.nix` und `flake.lock` bleiben byteidentisch. Bestehende Dateien
ändern sich ausschließlich durch die zwei optionalen ASDF-Systeme und den
Aufruf ihrer Tests nach den bisherigen Stufen des frischen SBCL-Laufs.

## Befund zu Z1 und Z4–Z6; Anforderungen an Z2

**Vorhanden und ausgeführt:** Gegenstände über Identifier auffinden, verschiedene
Dokumente als Belege referenzieren, Beziehungen über native Roles navigieren,
Items inspizieren, eine gescopte Annotation hinzufügen, Gleichheit normalisieren
und den resultierenden Zustand kanonisch vergleichen. Damit ist ein kleiner
realer Projektausschnitt lesbar, untersuchbar und im Modell bearbeitbar.

**Aus der Benutzung abgeleitete Anforderungen, keine freigegebenen Arbeitspakete:**
Eine spätere Oberfläche müsste Gegenstandsidentität neben lesbaren Namen zeigen,
kanonische Handles nach Normalisierung auflösen, Scopes sichtbar machen,
Belegverweise bewusst öffnen und zwischen Speicherzustand und CTM-Datei
unterscheiden. Gerade die zwei nebeneinander bestehenden Aussagen — dokumentierter
Status und Übungsannotation — zeigen den Bedarf, Perspektive und Bearbeitungsart
sichtbar zu halten. Die aktuelle Demonstration bleibt eine REPL-Lektüre mit
linearen Abfragen, ohne UI, allgemeine Queries, automatische Quellensynchronisation
oder persistente Arbeitsumgebung. Kein Bedarf wird als automatisch beauftragte
Produktionsänderung behandelt.

Eine allgemeine Wertänderungs- oder Löschoperation für Occurrences wird nicht
vorgeführt: Die öffentlichen Value-Leser sind keine Setter, und die verwendete
API bietet keinen allgemeinen `set-occurrence-value`-/Löschpfad. Das Beispiel
bearbeitet den Gegenstand durch Ergänzen einer Characteristic. Eine darüber
hinausgehende Editierfähigkeit wird weder vorausgesetzt noch nachimplementiert.

Die bestehende CTM-/TMDM-/CXTM-Fähigkeit reicht für diese begrenzte Aufgabe aus.
Es wurde keine wesentliche Modelloperation als Voraussetzung nachimplementiert.
HyperDoc, SLY, externe Abhängigkeiten, Normentscheidungen und weitere Slices
bleiben außerhalb des Auftrags. Nach dem lokalen Commit endet Slice 22U.
