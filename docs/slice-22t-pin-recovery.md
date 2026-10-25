# Slice 22T — Wiederbeschaffungsbedarf für zwei unveränderte Nix-Pins

Ergebnis **B**: Der bestehende Slice bleibt blockiert und uncommittiert.
Arbeitsbranch `codex/ctm-xtm-slice-22t`, HEAD
`513de98e5f9dfb62ba3c6310a150bb43c5a4c151`, Parent
`c1fa847c85017d4edf5c2439c772d903261e5a12`. Der Index ist leer.
Die begonnenen Tests, ASDF-Anbindung und bisherigen 22T-Berichte wurden erhalten.

## Rekonstruierte Herkunft und Identität

[flake.nix](../flake.nix) verwendet `pkgs.sbclPackages.cxml` aus der in
[flake.lock](../flake.lock) gebundenen Nixpkgs-Revision
`50ab793786d9de88ee30ec4e4c24fb4236fc2674`, NAR-Hash
`sha256-/bVBlRpECLVzjV19t5KMdMFWSwKLtb5RyXdjz3LJT+g=`.
Deren Git-Baum `297fd1a23ea526b5bb33ddad9c385d4cee7baeb3` ist im lokalen
Nix-Tarball-Cache noch lesbar. Daraus wurden die ursprünglichen Definitionen
`pkgs/development/lisp-modules/imported.nix:41169` (closure-common) und
`:45322` (cxml) gelesen. Beide rufen `createAsd` mit `asd == system` auf.
Die dortige Funktion, Zeilen 23–38, liefert deshalb unverändert
`fetchzip { inherit url sha256; }`; es gibt keine zusätzliche ASD-Umbenennung.
Die Versionsbezeichnung `-git` benennt in dieser Fetch-Definition **keinen**
zusätzlich belegten Upstream-Git-Commit. Die konkrete Quellenbindung erfolgt
über Archiv-URL und rekursiven SHA-256-Hash.

### cxml 20200610-git

- Archiv: `http://beta.quicklisp.org/archive/cxml/2020-06-10/cxml-20200610-git.tgz`
- Nix32-NAR-SHA-256: `18fls3bx7vmnxfa6qara8fxp316d8kb3izar0kysvqg6l0a45a51`
- SRI desselben Hashes: `sha256-oahCFKDm4a39BFn9ONZEzYRxu0MqK2yU67bu09fQ1KE=`
- Erwarteter Store-Pfad: `/nix/store/5075y4alv1is8n78bcsfcaj0mfpqz195-source`

### closure-common 20181018-git

- Archiv: `http://beta.quicklisp.org/archive/closure-common/2018-10-18/closure-common-20181018-git.tgz`
- Nix32-NAR-SHA-256: `0k5r2qxn122pxi301ijir3nayi9sg4d7yiy276l36qmzwhp4mg5n`
- SRI desselben Hashes: `sha256-trxKLuS/YjOoOcJHfxp5OkWv7MhRxgBG7FeIYDsWuUw=`
- Erwarteter Store-Pfad: `/nix/store/yw7j44h85ilvrg9jsnwcyz048nbl3cl9-source`

Die Hashes betreffen den entpackten NAR-Baum, nicht die komprimierte Datei.
`nix-store --print-fixed-path --recursive sha256 HASH source` berechnet für
beide Pins exakt die historischen Store-Pfade. Das realisiert keine Quelle.
Die gespeicherten Quellen- und Patchdatensätze aus
[20H](../reports/slice-20h/source-preparation.json),
[22R](../reports/slice-22r/after/source-preparation.json) und
[22S](../reports/slice-22s/after/source-preparation.json) sind identisch.

## Offline-Prüfung und ihre Grenzen

**Beobachtet:** Beide Store-Verzeichnisse fehlen. Für sie existieren weder
`ValidPaths`- noch `DerivationOutputs`-Einträge in der lokalen Nix-Datenbank.
28.700 vorhandene `.drv`-Dateien enthalten keinen Bezug auf diese Ausgaben oder
Archivnamen. Temporäre, nur gelesene Kopien der Fetcher- und Binary-Cache-Datenbanken
liefern ebenfalls keinen passenden Eintrag. Konfiguriert sind HTTPS-Substituter;
ein lokaler Dateisubstituter ist nicht konfiguriert. Die Git-Objekte belegen die
Fetch-Definitionen, nicht die Verfügbarkeit der Quellarchive.

Die gezielte Suche nach den beiden ASD-Dateien, benannten TGZ- und NAR-Archiven
in Store, temporären Verzeichnissen, Benutzer-Caches und lokalen Share-Verzeichnissen
fand keine Quelle. `~/quicklisp` fehlt; einige geschützte macOS-TemporaryItems-
Verzeichnisse waren nicht lesbar (Suchprozess Exit 2). Das ist ein begrenzter
Negativbefund, kein Beweis, dass nirgends eine externe Sicherung existiert.

**Schlussfolgerung:** Es gibt in den geprüften lokalen Beständen keinen belegten
Offline-Wiederherstellungsweg. Deshalb wurde kein Fetch-/Build-/Realisierungsversuch
gestartet und die bereits am fehlenden Input gescheiterte Vorbereitung nicht
unverändert wiederholt. Die Ursache des Verschwindens bleibt unbekannt.

## 19D0B-Identitätsvertrag bleibt erhalten

Die aktuellen Patchdateien stimmen mit den historischen Hashes überein:

- `patches/cxml-19d0b.patch`:
  `86720fb7960057def9092e8e75332ce45348b9809766667b8e6b1901c7cf5f24`
- `patches/closure-common-19d0b.patch`:
  `bbe8e956a147f6f122025e3c355bb13cf0d55ad811d1d4003f9ab50976aed74a`

[scripts/prepare-cxml.py](../scripts/prepare-cxml.py) prüft zuerst alle sieben
pristinen NAR-Hashes, kopiert dann die zwei betroffenen Quellen und wendet die
versionierten Patches mit `--fuzz=0` ohne Offset an. Die gespeicherten Before-/After-
Hashes der drei geänderten Dateien sind im neuen JSON vollständig enthalten.
Die Patches gehören weiterhin in separate Vorbereitungskopien, nicht in den Store.
Eine erneute erfolgreiche Anwendung kann erst nach Wiederbeschaffung nachgewiesen
werden; in diesem Lauf wurde kein Patch angewendet.

## Minimal erforderliche Freigabe und vorgesehene Befehle

Erforderlich ist ausschließlich die ausdrückliche Erlaubnis, die beiden
ursprünglichen Archive einschließlich nötiger Weiterleitungen derselben Archive
über Netzwerk zu beziehen und unter den unveränderten erwarteten Hashes dem
Nix-Store hinzuzufügen. Keine neue Pin-Definition, Ersatzversion, weitere Abhängigkeit,
Flake-/Profil-/Nix-Konfigurationsänderung oder Dienständerung ist vorgesehen.
Die folgende Syntax wurde mit der lokalen Hilfe von Nix 2.31.1 geprüft;
**die Befehle wurden nicht ausgeführt**:

```sh
nix store prefetch-file --unpack --name source --expected-hash sha256-oahCFKDm4a39BFn9ONZEzYRxu0MqK2yU67bu09fQ1KE= --json http://beta.quicklisp.org/archive/cxml/2020-06-10/cxml-20200610-git.tgz
nix store prefetch-file --unpack --name source --expected-hash sha256-trxKLuS/YjOoOcJHfxp5OkWv7MhRxgBG7FeIYDsWuUw= --json http://beta.quicklisp.org/archive/closure-common/2018-10-18/closure-common-20181018-git.tgz
```

Erst bei exakt bestätigtem Store-Pfad und NAR-Hash darf die unveränderte
Offline-Vorbereitung folgen. Deren Quellen, Patchprofile und Before-/After-Hashes
müssen den bisherigen Nachweisen entsprechen. Danach können die bereits
autorisierten produktiven Reader-Vergleiche und die volle Offline-Regression
fortgesetzt werden. Eine abweichende Identität bleibt ein Stopppunkt.

## Keine neue fachliche Abnahme

Keine produktiven Reader-Aufrufe, CXTM-Vergleiche oder Executor-Kontrollen wurden
in diesem Fortsetzungsversuch ausgeführt. Kein Commit, Download, Push oder
Deployment. XTM **121/0/3**, CTM **262/4/7** sind weiterhin der zuletzt gespeicherte
Stand, keine neue Testbestätigung. Der Slice bleibt offen.

[Maschinenlesbarer Herkunfts- und Wiederbeschaffungsnachweis](../reports/slice-22t/pin-recovery.json).
