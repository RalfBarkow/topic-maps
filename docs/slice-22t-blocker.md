# Slice 22T — begonnen, wegen fehlender lokaler Pins nicht abgenommen

Arbeitsbranch: `codex/ctm-xtm-slice-22t`.
HEAD bleibt `513de98e5f9dfb62ba3c6310a150bb43c5a4c151`.
Zu Beginn waren Index und Arbeitsbaum sauber. Kein Commit wurde erstellt.

## Tatsächlich beobachteter Blocker

Die unveränderte Offline-Vorbereitung `scripts/validate-slice-22d.py --prepare`
scheiterte vor jedem Reader-Aufruf mit:

```
AssertionError: Missing local source: cxml
```

Die Prüfung aller sieben bisherigen Pins ergibt zwei fehlende Quellverzeichnisse:

| Paket | Version | Bisheriger lokaler Pfad |
| --- | --- | --- |
| cxml | 20200610-git | `/nix/store/5075y4alv1is8n78bcsfcaj0mfpqz195-source` |
| closure-common | 20181018-git | `/nix/store/yw7j44h85ilvrg9jsnwcyz048nbl3cl9-source` |

Die fünf anderen Quellverzeichnisse existieren; ihre Hashes wurden hier nicht
als Ersatz für die fehlende vollständige Vorbereitung qualifiziert.
SBCL 2.5.4 selbst ist vorhanden. Die früheren vorbereiteten Kopien aus 22R/22S
existieren nicht mehr. In den untersuchten lokalen Quellverzeichnissen,
Quicklisp-Archiven und Nix-Fetcher-Metadaten wurde kein Ersatz für die beiden
fehlenden Pins gefunden. Die Ursache ihres Fehlens wurde nicht festgestellt.
Keine Downloads, Substitutionen, Nix-Profiländerungen oder Dependency-Upgrades.

[Blocker-/Umgebungsnachweis samt Pins](../reports/slice-22t/blocked-state.json).

## Erhaltener Arbeitsstand, ausdrücklich unvalidiert

- [Begonnene zusätzliche Quellpaare](../tests/ctm-xtm-anytype-equivalence.lisp):
  Occurrence mit SI/SL/II und Reifier; typisierte/scoped Name-Variant mit
  Namespace-Kontext und Reifiern; Normalisierung zweier Occurrences und zweier
  Variants; Namespace-Bedeutung als absichtlich ungleiche Gegenprobe.
- [Bisherige Suite](../tests/ctm-xtm-equivalence.lisp): Aufrufe der neuen Proben
  ergänzt; die bisherigen 30 Paare und drei Kontraste nicht ersetzt.
- [ASDF-Anbindung](../topic-maps.asd): zusätzliche Testdatei vorgesehen.

Die kanonischen Sollwerte sind in der Testdatei als feste Literale vorgegeben,
nicht aus einer neuen XTM-Ausgabe erzeugt. Es liegt aber noch **kein** tatsächlicher
CTM-/XTM-Vergleich, kein natives Modellergebnis und kein CXTM-Bytevergleich
für diese neuen Fälle vor. Die erweiterte Suite wurde weder kompiliert noch ausgeführt.
Daraus folgt keine Aussage über eine CTM-Fähigkeitslücke oder Reader-Abweichung.

Eine ergänzende reine Lisp-Leseprüfung hat nach Korrektur einer überzähligen
Klammer 13 Formen gelesen. Sie lädt weder ASDF noch CXML, CTM-/XTM-Reader oder
TMDM und wertet die gelesenen Testformen nicht aus. Nur leere Package-Namensräume
ermöglichen das Lesen qualifizierter Symbole; es gibt keine Ersatz-Reader oder
Ersatzmaps. [Prüfquelle](../reports/slice-22t/syntax-only.lisp) und
[Log](../reports/slice-22t/syntax-only.log). Das ist keine fachliche Testabnahme.

## Integrität und ausstehende Abnahme

[Integritätsaudit](../reports/slice-22t/integrity.json): alle 11.574 geschützten
Basisdateien stimmen mit dem Ausgangszustand überein, darunter 2.006 Korpusdateien
und 9.256 historische Reportdateien. Sämtliche Produktionsquellen und vorhandenen
Case Records bleiben unverändert. Nur die beiden begonnenen versionierten
Test-/ASDF-Dateien sind von diesem Schutzvergleich ausgenommen; die neue Testdatei
und diese neuen Berichte sind noch uncommittiert.

Der zuletzt gespeicherte Stand bleibt XTM **121/0/3**, CTM **262/4/7**.
Diese Zahlen wurden in 22T **nicht erneut durch Testausführung bestätigt**.
Es gibt keine neuen Originalregistrierungen, keine Vollregression und keine
neu ausgeführten Executor-Fehlerkontrollen. Kein PASS wird aus der Syntaxprüfung
oder den erwarteten Quellpaaren abgeleitet.

Zur Fortsetzung müssen zuerst genau die beiden bisherigen gepinnten Quellen
lokal wieder verfügbar sein. Anschließend stehen die produktiven Reader-Aufrufe,
nativen Prüfungen, vollständigen CXTM-Vergleiche, der Erhalt aller bisherigen
Äquivalenzen, die vollständige Offline-Regression einschließlich aller 113
Executor-Kontrollen und erst nach erfolgreicher Abnahme der lokale Commit aus.
Der vorliegende Arbeitsstand wird erhalten; keine Produktionsänderung, kein
Push, Deployment, HyperDoc-Eingriff oder automatischer Folgeauftrag.
