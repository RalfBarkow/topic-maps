# Nicht abgenommene Entwicklungsversuche

- `native-test-api-misuse.log`: falsche Test-Arity für `intern-topic`, vor jeder Reader-Änderung. Korrigiert auf den vorhandenen `add-topic-identifier`-Vertrag; danach erfolgreiches natives Gate mit 12 Checks. Kein Modellfehler und keine TMDM-Änderung.
- `test-helper-compile-error.log`: überzählige Klammer im neuen Testhelfer. Korrigiert; der anschließende isolierte XTM-Lauf besteht mit 3587 Checks.

Diese Versuche zählen nicht als erfolgreiche Abnahme. Maßgeblich sind das gesicherte Native-Gate und die vollständig neue Offline-Regression unter `../after/`.
