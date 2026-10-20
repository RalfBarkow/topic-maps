# Slice 22C — Originale, Baselines und tatsächliche Beobachtungen

Generiert aus der erneut geprüften fallbezogenen Evidenz. [Entscheidungen und Editionsgrenzen](slice-22c-normative-decisions.md); [vollständige JSON-Evidenz](../reports/slice-22c/case-evidence.json).

Quellbytes, Hashes und Prozessresultate sind `observed`; grammatische Rollen sind `derived`, historische Argumentabsichten `inferred`. Zeichenpositionen sind nullbasiert, Zeile/Spalte einsbasiert. XTM-Positionen bleiben die ungefähr gemeldeten SAX-Positionen. Die Lesefassung blendet Leerraum am Zeilenende aus; Text und Hexwerte im JSON erhalten sämtliche Originalbytes einschließlich BOM und fehlendem Schluss-LF.

## ctm/in/include-template.ctm

Vorher: unresolved-requirement / C. Neue Entscheidung: **C**. Registrierung unverändert: `fail`.

Document IRI: `https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/include-template.ctm`.

Original: `vendor/cxtm/ctm/in/include-template.ctm`, 48 Bytes; SHA-256 `345ee0e00a096195979bdc64cc8aad272e5c60ebeee185c69c4223b5c911f674`.

```text
%include <include-template.sub>

template(topic)
```

Quellabschluss: kein abschließendes LF. UTF-8-BOM: nein.

Unveränderte Baseline: `vendor/cxtm/ctm/baseline/include-template.ctm.cxtm`, 401 Bytes; SHA-256 `ebf9e7acc9dd9487ebf19c9f2dc1c8af3933e0371d9a506eee307923c5d65d0c`.

```xml
<topicMap>
<topic number="1">
<itemIdentifiers>
<locator>#topic</locator>
</itemIdentifiers>
<occurrence number="1">
<value>Test</value>
<datatype>http://www.w3.org/2001/XMLSchema#string</datatype>
<type topicref="2"></type>
</occurrence>
</topic>
<topic number="2">
<itemIdentifiers>
<locator>#occtype</locator>
<locator>include-template.sub#occtype</locator>
</itemIdentifiers>
</topic>
</topicMap>
```

Tatsächliche Condition (einschließlich Code, Position und Cause):

```json
null
```

Ist-CXTM: 353 Bytes, SHA-256 `15326a49da9e44f4a3f886414aa2134cf3ba0f7682bb52259e3b64138ac5e864`. Vollständiger Bytevergleich: **nicht identisch**. Erste Differenz: 58.

```xml
<topicMap>
<topic number="1">
<itemIdentifiers>
<locator>#occtype</locator>
</itemIdentifiers>
</topic>
<topic number="2">
<itemIdentifiers>
<locator>#topic</locator>
</itemIdentifiers>
<occurrence number="1">
<value>Test</value>
<datatype>http://www.w3.org/2001/XMLSchema#string</datatype>
<type topicref="1"></type>
</occurrence>
</topic>
</topicMap>
```

Verbleibende Modelldifferenzen nach Identitätszuordnung:

```json
[
  {
    "path": "/children/0/children/0/children",
    "actual": [
      {
        "element": "locator",
        "attributes": {},
        "text": "#occtype",
        "children": []
      }
    ],
    "expected": [
      {
        "element": "locator",
        "attributes": {},
        "text": "#occtype",
        "children": []
      },
      {
        "element": "locator",
        "attributes": {},
        "text": "include-template.sub#occtype",
        "children": []
      }
    ]
  }
]
```

Unveränderte Hilfsquelle: `vendor/cxtm/ctm/in/include-template.sub`, 52 Bytes; SHA-256 `d40daa6f573eac03e72c45ee8d018a23bffa97f0dcc28d4bcd481a7e5d11205f`.

```text

def template($topic)
  $topic occtype: "Test".
end
```

Neue normative Entscheidung und offene Primärquellen:

```json
{
  "classification": "C",
  "scope": "Definition/import/invocation environment and extra definition-source II",
  "claim": "The current model contains only caller-document identifiers. Whether the published later clauses require the baseline extra II is not established.",
  "conditionalConclusion": "B is supported by the inspected HTML interpretation; no eager Topic exists in the observed child.",
  "references": [
    "CTM-HTML:3.2,3.14–3.16.2",
    "CTM-PREVIEW",
    "TMDM-HTML:5.1,5.2,6.2"
  ],
  "openQuestions": [
    "Q-CTM",
    "Q-ERRATA"
  ],
  "nextAction": "Verify declaration vs invocation environment before proposing any identifier change.",
  "epistemicStatus": "derived",
  "evidenceStrength": "explicit missing primary clause or interpretation; bounded conclusion from available sources"
}
```

## ctm/in/include-wildcard2.ctm

Vorher: unresolved-requirement / C. Neue Entscheidung: **C**. Registrierung unverändert: `fail`.

Document IRI: `https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/include-wildcard2.ctm`.

Original: `vendor/cxtm/ctm/in/include-wildcard2.ctm`, 50 Bytes; SHA-256 `1e55e65bad772df558b27e9566b06e3529392983a18f9d9fc1d73518d85597c9`.

```text
%include <include-wildcard2.sub>

?foo - "Master".
```

Quellabschluss: kein abschließendes LF. UTF-8-BOM: nein.

Unveränderte Baseline: `vendor/cxtm/ctm/baseline/include-wildcard2.ctm.cxtm`, 669 Bytes; SHA-256 `cd55c6eb2fe686d73209d074ee42b576d0fdeab5efcc62f3beff24ced69ba327`.

```xml
<topicMap>
<topic number="1">
<itemIdentifiers>
<locator>#$__1.foo</locator>
</itemIdentifiers>
<name number="1">
<value>Sub Sub</value>
<type topicref="4"></type>
</name>
</topic>
<topic number="2">
<itemIdentifiers>
<locator>#$__2.foo</locator>
</itemIdentifiers>
<name number="1">
<value>Sub</value>
<type topicref="4"></type>
</name>
</topic>
<topic number="3">
<itemIdentifiers>
<locator>#$__3.foo</locator>
</itemIdentifiers>
<name number="1">
<value>Master</value>
<type topicref="4"></type>
</name>
</topic>
<topic number="4">
<subjectIdentifiers>
<locator>http://psi.topicmaps.org/iso13250/model/topic-name</locator>
</subjectIdentifiers>
</topic>
</topicMap>
```

Tatsächliche Condition (einschließlich Code, Position und Cause):

```json
null
```

Ist-CXTM: 719 Bytes, SHA-256 `be6e7114120452715b740956b25d8c1ec263814d2210e6ea323976055ecc082e`. Vollständiger Bytevergleich: **nicht identisch**. Erste Differenz: 61.

```xml
<topicMap>
<topic number="1">
<itemIdentifiers>
<locator>#$__2.foo</locator>
</itemIdentifiers>
<name number="1">
<value>Sub</value>
<type topicref="4"></type>
</name>
</topic>
<topic number="2">
<itemIdentifiers>
<locator>#$__3.foo</locator>
</itemIdentifiers>
<name number="1">
<value>Master</value>
<type topicref="4"></type>
</name>
</topic>
<topic number="3">
<itemIdentifiers>
<locator>#$__1.foo</locator>
<locator>include-wildcard2.sub#$__1.foo</locator>
</itemIdentifiers>
<name number="1">
<value>Sub Sub</value>
<type topicref="4"></type>
</name>
</topic>
<topic number="4">
<subjectIdentifiers>
<locator>http://psi.topicmaps.org/iso13250/model/topic-name</locator>
</subjectIdentifiers>
</topic>
</topicMap>
```

Verbleibende Modelldifferenzen nach Identitätszuordnung:

```json
[
  {
    "path": "/children/0/children/0/children",
    "actual": [
      {
        "element": "locator",
        "attributes": {},
        "text": "#$__1.foo",
        "children": []
      },
      {
        "element": "locator",
        "attributes": {},
        "text": "include-wildcard2.sub#$__1.foo",
        "children": []
      }
    ],
    "expected": [
      {
        "element": "locator",
        "attributes": {},
        "text": "#$__1.foo",
        "children": []
      }
    ]
  }
]
```

Unveränderte Hilfsquelle: `vendor/cxtm/ctm/in/include-wildcard2.sub`, 49 Bytes; SHA-256 `d715a10dfd9fc01f0d37397d0ecf36ca169902144f6091d5e7ca036598d63efd`.

```text
%include <include-wildcard2.sub2>

?foo - "Sub".
```

Unveränderte Hilfsquelle: `vendor/cxtm/ctm/in/include-wildcard2.sub2`, 19 Bytes; SHA-256 `c78cc6ff88b6b04cddc5703f502783f3c739d082b744db21f10d2393c36a2a3d`.

```text

?foo - "Sub Sub".
```

Neue normative Entscheidung und offene Primärquellen:

```json
{
  "classification": "C",
  "scope": "Retention of nested include wildcard item identifier",
  "claim": "The child-origin II remains in the observed map, whereas the baseline omits it. Its removal is not justified by the inspected text.",
  "conditionalConclusion": "B under inspected HTML; publication-equivalent include text still needed.",
  "references": [
    "CTM-HTML:3.2,3.3.8,3.16.2",
    "CTM-PREVIEW",
    "TMDM-HTML:5.1,6.1–6.2"
  ],
  "openQuestions": [
    "Q-CTM",
    "Q-ERRATA"
  ],
  "nextAction": "Verify the exact published include identifier operation; preserve both observed identifiers meanwhile.",
  "epistemicStatus": "derived",
  "evidenceStrength": "explicit missing primary clause or interpretation; bounded conclusion from available sources"
}
```

## ctm/in/occurrence-datetime-timezone2.ctm

Vorher: normative-conflict / B. Neue Entscheidung: **C**. Registrierung unverändert: `fail`.

Document IRI: `https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/occurrence-datetime-timezone2.ctm`.

Original: `vendor/cxtm/ctm/in/occurrence-datetime-timezone2.ctm`, 92 Bytes; SHA-256 `4240411defe0618e6a6431d624cfbe480607e4d15c83c10d0c6a5a85c2fafa7c`.

```text
datetime - "datetime" .

some-topic - "some topic" ;
  datetime: 2011-01-01T00:00:00+02:00
.
```

Quellabschluss: kein abschließendes LF. UTF-8-BOM: nein.

Unveränderte Baseline: `vendor/cxtm/ctm/baseline/occurrence-datetime-timezone2.ctm.cxtm`, 679 Bytes; SHA-256 `fe840f8b3a6a7b068d08592373ab71ebe757f6d3e03c0bee792deab74b6b6080`.

```xml
<topicMap>
<topic number="1">
<itemIdentifiers>
<locator>#datetime</locator>
</itemIdentifiers>
<name number="1">
<value>datetime</value>
<type topicref="3"></type>
</name>
</topic>
<topic number="2">
<itemIdentifiers>
<locator>#some-topic</locator>
</itemIdentifiers>
<name number="1">
<value>some topic</value>
<type topicref="3"></type>
</name>
<occurrence number="1">
<value>2011-01-01T00:00:00+02:00</value>
<datatype>http://www.w3.org/2001/XMLSchema#dateTime</datatype>
<type topicref="1"></type>
</occurrence>
</topic>
<topic number="3">
<subjectIdentifiers>
<locator>http://psi.topicmaps.org/iso13250/model/topic-name</locator>
</subjectIdentifiers>
</topic>
</topicMap>
```

Tatsächliche Condition (einschließlich Code, Position und Cause):

```json
null
```

Ist-CXTM: 674 Bytes, SHA-256 `b15755d77327c002ae1e3c75c0fa8ac2de7f50f6175153012e0e88d8ba86dcff`. Vollständiger Bytevergleich: **nicht identisch**. Erste Differenz: 382.

```xml
<topicMap>
<topic number="1">
<itemIdentifiers>
<locator>#datetime</locator>
</itemIdentifiers>
<name number="1">
<value>datetime</value>
<type topicref="3"></type>
</name>
</topic>
<topic number="2">
<itemIdentifiers>
<locator>#some-topic</locator>
</itemIdentifiers>
<name number="1">
<value>some topic</value>
<type topicref="3"></type>
</name>
<occurrence number="1">
<value>2010-12-31T22:00:00Z</value>
<datatype>http://www.w3.org/2001/XMLSchema#dateTime</datatype>
<type topicref="1"></type>
</occurrence>
</topic>
<topic number="3">
<subjectIdentifiers>
<locator>http://psi.topicmaps.org/iso13250/model/topic-name</locator>
</subjectIdentifiers>
</topic>
</topicMap>
```

Verbleibende Modelldifferenzen nach Identitätszuordnung:

```json
[
  {
    "path": "/children/1/children/2/children/0/text",
    "actual": "2010-12-31T22:00:00Z",
    "expected": "2011-01-01T00:00:00+02:00"
  }
]
```

Neue normative Entscheidung und offene Primärquellen:

```json
{
  "classification": "C",
  "scope": "Final ISO CXTM edition decision; XSD-level conclusion separately supported",
  "claim": "Current value/canonical bytes have direct XSD support and contradict the public-CXTM reading of the historical baseline. Final B requires the unavailable published CXTM clause.",
  "conditionalConclusion": "B under CXTM-HTML plus XSD-2004; this is not an unconditional ISO-edition B.",
  "references": [
    "CTM-PREVIEW:3.4.1 printed p.5",
    "CXTM-HTML:2,3.16",
    "XSD-2004:3.2.7.1–3.2.7.3,D.1,E.1",
    "XSD-ERRATA"
  ],
  "openQuestions": [
    "Q-CXTM",
    "Q-ERRATA"
  ],
  "nextAction": "Retain FAIL; verify published CXTM 3.16, then separately approve a documented baseline exception, never rewrite the original baseline.",
  "changeFrom22A": "Tightens earlier edition-qualified B to formal C; observations and XSD reasoning are unchanged, but missing final CXTM clause is now a decision gate.",
  "epistemicStatus": "derived",
  "evidenceStrength": "explicit missing primary clause or interpretation; bounded conclusion from available sources"
}
```

## ctm/in/occurrence-datetime2.ctm

Vorher: normative-conflict / B. Neue Entscheidung: **C**. Registrierung unverändert: `fail`.

Document IRI: `https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/occurrence-datetime2.ctm`.

Original: `vendor/cxtm/ctm/in/occurrence-datetime2.ctm`, 122 Bytes; SHA-256 `75f6b381203abd7ffb0d0a398abb4ad2aea10b676772d54e8086adf52df88ab1`.

```text
﻿#
# Test for leap seconds,
# c.f. <http://projects.topicmapslab.de/issues/2563>
#
topic
occtype: 1976-09-19T12:01:60 .
```

Quellabschluss: kein abschließendes LF. UTF-8-BOM: ja.

Unveränderte Baseline: `vendor/cxtm/ctm/baseline/occurrence-datetime2.ctm.cxtm`, 370 Bytes; SHA-256 `90bd6e740db72cb46a9fcee9329b70d0963bc6317300e498c941e00d9ff5c55f`.

```xml
<topicMap>
<topic number="1">
<itemIdentifiers>
<locator>#occtype</locator>
</itemIdentifiers>
</topic>
<topic number="2">
<itemIdentifiers>
<locator>#topic</locator>
</itemIdentifiers>
<occurrence number="1">
<value>1976-09-19T12:01:60</value>
<datatype>http://www.w3.org/2001/XMLSchema#dateTime</datatype>
<type topicref="1"></type>
</occurrence>
</topic>
</topicMap>
```

Tatsächliche Condition (einschließlich Code, Position und Cause):

```json
null
```

Ist-CXTM: 370 Bytes, SHA-256 `2cdbdd98349a1f830ec2f49c2331d2c5220492c1d8b75563db8623ecb38e76fd`. Vollständiger Bytevergleich: **nicht identisch**. Erste Differenz: 232.

```xml
<topicMap>
<topic number="1">
<itemIdentifiers>
<locator>#occtype</locator>
</itemIdentifiers>
</topic>
<topic number="2">
<itemIdentifiers>
<locator>#topic</locator>
</itemIdentifiers>
<occurrence number="1">
<value>1976-09-19T12:02:00</value>
<datatype>http://www.w3.org/2001/XMLSchema#dateTime</datatype>
<type topicref="1"></type>
</occurrence>
</topic>
</topicMap>
```

Verbleibende Modelldifferenzen nach Identitätszuordnung:

```json
[
  {
    "path": "/children/1/children/1/children/0/text",
    "actual": "1976-09-19T12:02:00",
    "expected": "1976-09-19T12:01:60"
  }
]
```

Neue normative Entscheidung und offene Primärquellen:

```json
{
  "classification": "C",
  "scope": "Final ISO CXTM edition decision; XSD-level conclusion separately supported",
  "claim": "Current value/canonical bytes have direct XSD support and contradict the public-CXTM reading of the historical baseline. Final B requires the unavailable published CXTM clause.",
  "conditionalConclusion": "B under CXTM-HTML plus XSD-2004; this is not an unconditional ISO-edition B.",
  "references": [
    "CTM-PREVIEW:3.4.1 printed p.5",
    "CXTM-HTML:2,3.16",
    "XSD-2004:3.2.7.1–3.2.7.3,D.1,E.1",
    "XSD-ERRATA"
  ],
  "openQuestions": [
    "Q-CXTM",
    "Q-ERRATA"
  ],
  "nextAction": "Retain FAIL; verify published CXTM 3.16, then separately approve a documented baseline exception, never rewrite the original baseline.",
  "changeFrom22A": "Tightens earlier edition-qualified B to formal C; observations and XSD reasoning are unchanged, but missing final CXTM clause is now a decision gate.",
  "epistemicStatus": "derived",
  "evidenceStrength": "explicit missing primary clause or interpretation; bounded conclusion from available sources"
}
```

## ctm/in/template-ambiguous-parameter5.ctm

Vorher: normative-conflict / C. Neue Entscheidung: **C**. Registrierung unverändert: `not-run`.

Document IRI: `https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/template-ambiguous-parameter5.ctm`.

Original: `vendor/cxtm/ctm/in/template-ambiguous-parameter5.ctm`, 146 Bytes; SHA-256 `5a4310d6f077776996700a77cd037ca30b1b616f7235128f9500ef16c5cd78a8`.

```text

# Using an IRI argument in different contexts

def template($iri)
  topic $iri; =$iri; ^$iri.
end

template(<http://www.example.org/something/>)
```

Quellabschluss: LF vorhanden. UTF-8-BOM: nein.

Unveränderte Baseline: `vendor/cxtm/ctm/baseline/template-ambiguous-parameter5.ctm.cxtm`, 353 Bytes; SHA-256 `a90bb867d36b9d99061d3815c6ce41a1cd4d8909c49adc7ce9cc1c9bfe06303f`.

```xml
<topicMap>
<topic number="1">
<subjectIdentifiers>
<locator>http://www.example.org/something/</locator>
</subjectIdentifiers>
<subjectLocators>
<locator>http://www.example.org/something/</locator>
</subjectLocators>
<itemIdentifiers>
<locator>#topic</locator>
<locator>http://www.example.org/something/</locator>
</itemIdentifiers>
</topic>
</topicMap>
```

Tatsächliche Condition (einschließlich Code, Position und Cause):

```json
{
  "condition": "INVALID-TEMPLATE-BODY",
  "message": "TEMPLATE-IDENTITY-TAIL in ctm/in/template-ambiguous-parameter5.ctm at CHARACTER 79 (line 5, column 13): Unmarked variable identities in Topic Tails remain outside the supported grammar.",
  "code": "template-identity-tail",
  "position": 79,
  "line": 5,
  "column": 13,
  "positionUnit": "character",
  "source": "ctm/in/template-ambiguous-parameter5.ctm",
  "cause": null,
  "context": null
}
```

Kein natives Original-Ergebnismodell und keine Original-Ist-CXTM-Ausgabe; keine Ersatzmap konstruiert.

Erneut geprüfte Variablenpositionen, Deklaration, Aufrufe und Bindungen:

```json
{
  "variables": [
    {
      "variable": "$iri",
      "position": 61,
      "line": 4,
      "column": 14,
      "role": "Parameterdeklaration"
    },
    {
      "variable": "$iri",
      "position": 75,
      "line": 5,
      "column": 9,
      "role": "Subject Identifier im Topic Tail (unmarkiert)"
    },
    {
      "variable": "$iri",
      "position": 82,
      "line": 5,
      "column": 16,
      "role": "Subject Locator nach ="
    },
    {
      "variable": "$iri",
      "position": 89,
      "line": 5,
      "column": 23,
      "role": "Item Identifier nach ^"
    }
  ],
  "declaration": "def template($iri)",
  "bindings": [
    [
      "$iri",
      "<http://www.example.org/something/>"
    ]
  ],
  "invocations": [
    {
      "text": "template(<http://www.example.org/something/>)",
      "position": 100,
      "line": 8
    }
  ]
}
```

Ausgeschriebene Gegenprobe (kein Original-PASS): 353/353 Bytes identisch; Condition null.

Neue normative Entscheidung und offene Primärquellen:

```json
{
  "classification": "C",
  "scope": "Published-edition legality of unmarked additional SI variable in Topic Tail",
  "claim": "The inspected HTML excludes this body position. The current condition occurs there before argument qualification; later published grammar has not been verified.",
  "conditionalConclusion": "Body invalid under inspected HTML. The expanded control reproduces baseline bytes but does not validate the original template.",
  "references": [
    "CTM-HTML:3.3.5–3.3.7,3.4,3.8–3.9,3.14–3.15",
    "CTM-LANDING",
    "CTM-PREVIEW"
  ],
  "openQuestions": [
    "Q-CTM",
    "Q-ERRATA"
  ],
  "nextAction": "Keep NOT-RUN. Decide any documented corpus exception only after edition check; compatibility grammar would need separate authorization.",
  "historicalIntent": {
    "epistemicStatus": "hypothesized",
    "claim": "The corpus may have assumed variable substitution in an additional SI tail position; no editor decision/erratum proving that intention was found."
  },
  "epistemicStatus": "derived",
  "evidenceStrength": "explicit missing primary clause or interpretation; bounded conclusion from available sources"
}
```

## ctm/in/template-ambiguous-parameter6.ctm

Vorher: normative-conflict / C. Neue Entscheidung: **C**. Registrierung unverändert: `not-run`.

Document IRI: `https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/template-ambiguous-parameter6.ctm`.

Original: `vendor/cxtm/ctm/in/template-ambiguous-parameter6.ctm`, 163 Bytes; SHA-256 `d2fd507bbbd544b6eae6caf4497c18e746165a5868a1d8e644eb18815db44d50`.

```text

%prefix ex <http://www.example.org/>

# Using a QName argument in different contexts

def template($q)
  topic $q; =$q; ^$q; occ: $q.
end

template(ex:something)
```

Quellabschluss: LF vorhanden. UTF-8-BOM: nein.

Unveränderte Baseline: `vendor/cxtm/ctm/baseline/template-ambiguous-parameter6.ctm.cxtm`, 613 Bytes; SHA-256 `3b20e3168ad1260c2a4fcb2b5b4b0026324a78263f2431d6637473087eecd672`.

```xml
<topicMap>
<topic number="1">
<itemIdentifiers>
<locator>#occ</locator>
</itemIdentifiers>
</topic>
<topic number="2">
<subjectIdentifiers>
<locator>http://www.example.org/something</locator>
</subjectIdentifiers>
<subjectLocators>
<locator>http://www.example.org/something</locator>
</subjectLocators>
<itemIdentifiers>
<locator>#topic</locator>
<locator>http://www.example.org/something</locator>
</itemIdentifiers>
<occurrence number="1">
<value>http://www.example.org/something</value>
<datatype>http://www.w3.org/2001/XMLSchema#anyURI</datatype>
<type topicref="1"></type>
</occurrence>
</topic>
</topicMap>
```

Tatsächliche Condition (einschließlich Code, Position und Cause):

```json
{
  "condition": "INVALID-TEMPLATE-BODY",
  "message": "TEMPLATE-IDENTITY-TAIL in ctm/in/template-ambiguous-parameter6.ctm at CHARACTER 114 (line 7, column 11): Unmarked variable identities in Topic Tails remain outside the supported grammar.",
  "code": "template-identity-tail",
  "position": 114,
  "line": 7,
  "column": 11,
  "positionUnit": "character",
  "source": "ctm/in/template-ambiguous-parameter6.ctm",
  "cause": null,
  "context": null
}
```

Kein natives Original-Ergebnismodell und keine Original-Ist-CXTM-Ausgabe; keine Ersatzmap konstruiert.

Erneut geprüfte Variablenpositionen, Deklaration, Aufrufe und Bindungen:

```json
{
  "variables": [
    {
      "variable": "$q",
      "position": 100,
      "line": 6,
      "column": 14,
      "role": "Parameterdeklaration"
    },
    {
      "variable": "$q",
      "position": 112,
      "line": 7,
      "column": 9,
      "role": "Subject Identifier im Topic Tail (unmarkiert)"
    },
    {
      "variable": "$q",
      "position": 117,
      "line": 7,
      "column": 14,
      "role": "Subject Locator nach ="
    },
    {
      "variable": "$q",
      "position": 122,
      "line": 7,
      "column": 19,
      "role": "Item Identifier nach ^"
    },
    {
      "variable": "$q",
      "position": 131,
      "line": 7,
      "column": 28,
      "role": "Occurrence-Literal; Datentyp xsd:anyURI"
    }
  ],
  "declaration": "def template($q)",
  "bindings": [
    [
      "$q",
      "ex:something → http://www.example.org/something"
    ]
  ],
  "invocations": [
    {
      "text": "template(ex:something)",
      "position": 140,
      "line": 10
    }
  ]
}
```

Ausgeschriebene Gegenprobe (kein Original-PASS): 613/613 Bytes identisch; Condition null.

Neue normative Entscheidung und offene Primärquellen:

```json
{
  "classification": "C",
  "scope": "Published-edition legality of unmarked additional SI variable in Topic Tail",
  "claim": "The inspected HTML excludes this body position. The current condition occurs there before argument qualification; later published grammar has not been verified.",
  "conditionalConclusion": "Body invalid under inspected HTML. The expanded control reproduces baseline bytes but does not validate the original template.",
  "references": [
    "CTM-HTML:3.3.5–3.3.7,3.4,3.8–3.9,3.14–3.15",
    "CTM-LANDING",
    "CTM-PREVIEW"
  ],
  "openQuestions": [
    "Q-CTM",
    "Q-ERRATA"
  ],
  "nextAction": "Keep NOT-RUN. Decide any documented corpus exception only after edition check; compatibility grammar would need separate authorization.",
  "historicalIntent": {
    "epistemicStatus": "hypothesized",
    "claim": "The corpus may have assumed variable substitution in an additional SI tail position; no editor decision/erratum proving that intention was found."
  },
  "epistemicStatus": "derived",
  "evidenceStrength": "explicit missing primary clause or interpretation; bounded conclusion from available sources"
}
```

## ctm/in/template-subject-identifier2.ctm

Vorher: normative-conflict / C. Neue Entscheidung: **C**. Registrierung unverändert: `not-run`.

Document IRI: `https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/in/template-subject-identifier2.ctm`.

Original: `vendor/cxtm/ctm/in/template-subject-identifier2.ctm`, 81 Bytes; SHA-256 `ffc9a5554b9c908386f6888ef29ccda5cc433e5519924db52f9441769e1df014`.

```text

def template($iri)
    topic $iri.
end

template(<http://psi.example.org/fake>)
```

Quellabschluss: LF vorhanden. UTF-8-BOM: nein.

Unveränderte Baseline: `vendor/cxtm/ctm/baseline/template-subject-identifier2.ctm.cxtm`, 204 Bytes; SHA-256 `e138a02738dc4a2526c465b11fa6915bed84724a31748eb3578ddf0f8ab16253`.

```xml
<topicMap>
<topic number="1">
<subjectIdentifiers>
<locator>http://psi.example.org/fake</locator>
</subjectIdentifiers>
<itemIdentifiers>
<locator>#topic</locator>
</itemIdentifiers>
</topic>
</topicMap>
```

Tatsächliche Condition (einschließlich Code, Position und Cause):

```json
{
  "condition": "INVALID-TEMPLATE-BODY",
  "message": "TEMPLATE-IDENTITY-TAIL in ctm/in/template-subject-identifier2.ctm at CHARACTER 34 (line 3, column 15): Unmarked variable identities in Topic Tails remain outside the supported grammar.",
  "code": "template-identity-tail",
  "position": 34,
  "line": 3,
  "column": 15,
  "positionUnit": "character",
  "source": "ctm/in/template-subject-identifier2.ctm",
  "cause": null,
  "context": null
}
```

Kein natives Original-Ergebnismodell und keine Original-Ist-CXTM-Ausgabe; keine Ersatzmap konstruiert.

Erneut geprüfte Variablenpositionen, Deklaration, Aufrufe und Bindungen:

```json
{
  "variables": [
    {
      "variable": "$iri",
      "position": 14,
      "line": 2,
      "column": 14,
      "role": "Parameterdeklaration"
    },
    {
      "variable": "$iri",
      "position": 30,
      "line": 3,
      "column": 11,
      "role": "Subject Identifier im Topic Tail (unmarkiert)"
    }
  ],
  "declaration": "def template($iri)",
  "bindings": [
    [
      "$iri",
      "<http://psi.example.org/fake>"
    ]
  ],
  "invocations": [
    {
      "text": "template(<http://psi.example.org/fake>)",
      "position": 41,
      "line": 6
    }
  ]
}
```

Ausgeschriebene Gegenprobe (kein Original-PASS): 204/204 Bytes identisch; Condition null.

Neue normative Entscheidung und offene Primärquellen:

```json
{
  "classification": "C",
  "scope": "Published-edition legality of unmarked additional SI variable in Topic Tail",
  "claim": "The inspected HTML excludes this body position. The current condition occurs there before argument qualification; later published grammar has not been verified.",
  "conditionalConclusion": "Body invalid under inspected HTML. The expanded control reproduces baseline bytes but does not validate the original template.",
  "references": [
    "CTM-HTML:3.3.5–3.3.7,3.4,3.8–3.9,3.14–3.15",
    "CTM-LANDING",
    "CTM-PREVIEW"
  ],
  "openQuestions": [
    "Q-CTM",
    "Q-ERRATA"
  ],
  "nextAction": "Keep NOT-RUN. Decide any documented corpus exception only after edition check; compatibility grammar would need separate authorization.",
  "historicalIntent": {
    "epistemicStatus": "hypothesized",
    "claim": "The corpus may have assumed variable substitution in an additional SI tail position; no editor decision/erratum proving that intention was found."
  },
  "epistemicStatus": "derived",
  "evidenceStrength": "explicit missing primary clause or interpretation; bounded conclusion from available sources"
}
```

## ctm/invalid/template-item-identifier-2nd-arg.ctm

Vorher: normative-conflict / C. Neue Entscheidung: **C**. Registrierung unverändert: `not-run`.

Document IRI: `https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/invalid/template-item-identifier-2nd-arg.ctm`.

Original: `vendor/cxtm/ctm/invalid/template-item-identifier-2nd-arg.ctm`, 167 Bytes; SHA-256 `ceb46d4457532cc5b432d5e601275cc6950bb105088e2b2ccfa4ffa5fbe82266`.

```text

def template($iri1, $iri2)
    topic1 $iri1.
    topic2 $iri2.
end

template(<http://www.example.org/>,     # valid
        ^<http://www.example.org/>)     # invalid
```

Quellabschluss: LF vorhanden. UTF-8-BOM: nein.

Keine positive CXTM-Baseline für diesen negativen Syntaxvertrag.

Tatsächliche Condition (einschließlich Code, Position und Cause):

```json
{
  "condition": "INVALID-TEMPLATE-BODY",
  "message": "TEMPLATE-IDENTITY-TAIL in ctm/invalid/template-item-identifier-2nd-arg.ctm at CHARACTER 44 (line 3, column 17): Unmarked variable identities in Topic Tails remain outside the supported grammar.",
  "code": "template-identity-tail",
  "position": 44,
  "line": 3,
  "column": 17,
  "positionUnit": "character",
  "source": "ctm/invalid/template-item-identifier-2nd-arg.ctm",
  "cause": null,
  "context": null
}
```

Kein natives Original-Ergebnismodell und keine Original-Ist-CXTM-Ausgabe; keine Ersatzmap konstruiert.

Erneut geprüfte Variablenpositionen, Deklaration, Aufrufe und Bindungen:

```json
{
  "variables": [
    {
      "variable": "$iri1",
      "position": 14,
      "line": 2,
      "column": 14,
      "role": "Parameterdeklaration"
    },
    {
      "variable": "$iri2",
      "position": 21,
      "line": 2,
      "column": 21,
      "role": "Parameterdeklaration"
    },
    {
      "variable": "$iri1",
      "position": 39,
      "line": 3,
      "column": 12,
      "role": "Subject Identifier von topic1 (unmarkiert)"
    },
    {
      "variable": "$iri2",
      "position": 57,
      "line": 4,
      "column": 12,
      "role": "Subject Identifier von topic2 (unmarkiert)"
    }
  ],
  "declaration": "def template($iri1, $iri2)",
  "bindings": [
    [
      "$iri1",
      "<http://www.example.org/>"
    ],
    [
      "$iri2",
      "^<http://www.example.org/>"
    ]
  ],
  "invocations": [
    {
      "text": "template(<http://www.example.org/>,     # valid\n        ^<http://www.example.org/>)",
      "position": 69,
      "line": 7
    }
  ]
}
```

Historisch beabsichtigte, tatsächlich nicht erreichte Argumentprüfung:

```json
{
  "argumentPosition": 2,
  "marker": "^",
  "cause": "Argument 2 mit ^ ist für den beabsichtigten unmarkierten SI-Verwendungskontext ungeeignet.",
  "currentlyReached": false,
  "actualBlockingCause": "INVALID-TEMPLATE-BODY/:template-identity-tail",
  "evidence": "Originalkörper und markiertes Argument; bei 2nd-arg Originalkommentar valid/invalid."
}
```

Neue normative Entscheidung und offene Primärquellen:

```json
{
  "classification": "C",
  "scope": "Published-edition legality of unmarked additional SI variable in Topic Tail",
  "claim": "The inspected HTML excludes this body position. The current condition occurs there before argument qualification; later published grammar has not been verified.",
  "conditionalConclusion": "Body invalid under inspected HTML. This does not qualify the historical argument-rejection contract.",
  "references": [
    "CTM-HTML:3.3.5–3.3.7,3.4,3.8–3.9,3.14–3.15",
    "CTM-LANDING",
    "CTM-PREVIEW"
  ],
  "openQuestions": [
    "Q-CTM",
    "Q-ERRATA"
  ],
  "nextAction": "Keep NOT-RUN. A body-syntax negative acceptance contract would require a separate agreement even if final grammar confirms exclusion.",
  "historicalIntent": {
    "epistemicStatus": "hypothesized",
    "claim": "The corpus may have assumed variable substitution in an additional SI tail position; no editor decision/erratum proving that intention was found."
  },
  "epistemicStatus": "derived",
  "evidenceStrength": "explicit missing primary clause or interpretation; bounded conclusion from available sources"
}
```

## ctm/invalid/template-item-identifier3.ctm

Vorher: normative-conflict / C. Neue Entscheidung: **C**. Registrierung unverändert: `not-run`.

Document IRI: `https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/invalid/template-item-identifier3.ctm`.

Original: `vendor/cxtm/ctm/invalid/template-item-identifier3.ctm`, 78 Bytes; SHA-256 `4c7ed0ab1574462b8939379f745a28942aa380fc6cc7fabae597fdc7bb21225f`.

```text

def template($iri)
    topic $iri.
end

template(^<http://www.example.org/>)
```

Quellabschluss: LF vorhanden. UTF-8-BOM: nein.

Keine positive CXTM-Baseline für diesen negativen Syntaxvertrag.

Tatsächliche Condition (einschließlich Code, Position und Cause):

```json
{
  "condition": "INVALID-TEMPLATE-BODY",
  "message": "TEMPLATE-IDENTITY-TAIL in ctm/invalid/template-item-identifier3.ctm at CHARACTER 34 (line 3, column 15): Unmarked variable identities in Topic Tails remain outside the supported grammar.",
  "code": "template-identity-tail",
  "position": 34,
  "line": 3,
  "column": 15,
  "positionUnit": "character",
  "source": "ctm/invalid/template-item-identifier3.ctm",
  "cause": null,
  "context": null
}
```

Kein natives Original-Ergebnismodell und keine Original-Ist-CXTM-Ausgabe; keine Ersatzmap konstruiert.

Erneut geprüfte Variablenpositionen, Deklaration, Aufrufe und Bindungen:

```json
{
  "variables": [
    {
      "variable": "$iri",
      "position": 14,
      "line": 2,
      "column": 14,
      "role": "Parameterdeklaration"
    },
    {
      "variable": "$iri",
      "position": 30,
      "line": 3,
      "column": 11,
      "role": "Subject Identifier von topic (unmarkiert)"
    }
  ],
  "declaration": "def template($iri)",
  "bindings": [
    [
      "$iri",
      "^<http://www.example.org/>"
    ]
  ],
  "invocations": [
    {
      "text": "template(^<http://www.example.org/>)",
      "position": 41,
      "line": 6
    }
  ]
}
```

Historisch beabsichtigte, tatsächlich nicht erreichte Argumentprüfung:

```json
{
  "argumentPosition": 1,
  "marker": "^",
  "cause": "Argument 1 mit ^ ist für den beabsichtigten unmarkierten SI-Verwendungskontext ungeeignet.",
  "currentlyReached": false,
  "actualBlockingCause": "INVALID-TEMPLATE-BODY/:template-identity-tail",
  "evidence": "Originalkörper und markiertes Argument; bei 2nd-arg Originalkommentar valid/invalid."
}
```

Neue normative Entscheidung und offene Primärquellen:

```json
{
  "classification": "C",
  "scope": "Published-edition legality of unmarked additional SI variable in Topic Tail",
  "claim": "The inspected HTML excludes this body position. The current condition occurs there before argument qualification; later published grammar has not been verified.",
  "conditionalConclusion": "Body invalid under inspected HTML. This does not qualify the historical argument-rejection contract.",
  "references": [
    "CTM-HTML:3.3.5–3.3.7,3.4,3.8–3.9,3.14–3.15",
    "CTM-LANDING",
    "CTM-PREVIEW"
  ],
  "openQuestions": [
    "Q-CTM",
    "Q-ERRATA"
  ],
  "nextAction": "Keep NOT-RUN. A body-syntax negative acceptance contract would require a separate agreement even if final grammar confirms exclusion.",
  "historicalIntent": {
    "epistemicStatus": "hypothesized",
    "claim": "The corpus may have assumed variable substitution in an additional SI tail position; no editor decision/erratum proving that intention was found."
  },
  "epistemicStatus": "derived",
  "evidenceStrength": "explicit missing primary clause or interpretation; bounded conclusion from available sources"
}
```

## ctm/invalid/template-subject-locator-2nd-arg.ctm

Vorher: normative-conflict / C. Neue Entscheidung: **C**. Registrierung unverändert: `not-run`.

Document IRI: `https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/invalid/template-subject-locator-2nd-arg.ctm`.

Original: `vendor/cxtm/ctm/invalid/template-subject-locator-2nd-arg.ctm`, 167 Bytes; SHA-256 `e7e8ca08ad1dec89549afbe2d3cf90098269031f239ddae37258bf87ba4c018f`.

```text

def template($iri1, $iri2)
    topic1 $iri1.
    topic2 $iri2.
end

template(<http://www.example.org/>,     # valid
         =<http://www.example.org/>)    # invalid
```

Quellabschluss: LF vorhanden. UTF-8-BOM: nein.

Keine positive CXTM-Baseline für diesen negativen Syntaxvertrag.

Tatsächliche Condition (einschließlich Code, Position und Cause):

```json
{
  "condition": "INVALID-TEMPLATE-BODY",
  "message": "TEMPLATE-IDENTITY-TAIL in ctm/invalid/template-subject-locator-2nd-arg.ctm at CHARACTER 44 (line 3, column 17): Unmarked variable identities in Topic Tails remain outside the supported grammar.",
  "code": "template-identity-tail",
  "position": 44,
  "line": 3,
  "column": 17,
  "positionUnit": "character",
  "source": "ctm/invalid/template-subject-locator-2nd-arg.ctm",
  "cause": null,
  "context": null
}
```

Kein natives Original-Ergebnismodell und keine Original-Ist-CXTM-Ausgabe; keine Ersatzmap konstruiert.

Erneut geprüfte Variablenpositionen, Deklaration, Aufrufe und Bindungen:

```json
{
  "variables": [
    {
      "variable": "$iri1",
      "position": 14,
      "line": 2,
      "column": 14,
      "role": "Parameterdeklaration"
    },
    {
      "variable": "$iri2",
      "position": 21,
      "line": 2,
      "column": 21,
      "role": "Parameterdeklaration"
    },
    {
      "variable": "$iri1",
      "position": 39,
      "line": 3,
      "column": 12,
      "role": "Subject Identifier von topic1 (unmarkiert)"
    },
    {
      "variable": "$iri2",
      "position": 57,
      "line": 4,
      "column": 12,
      "role": "Subject Identifier von topic2 (unmarkiert)"
    }
  ],
  "declaration": "def template($iri1, $iri2)",
  "bindings": [
    [
      "$iri1",
      "<http://www.example.org/>"
    ],
    [
      "$iri2",
      "=<http://www.example.org/>"
    ]
  ],
  "invocations": [
    {
      "text": "template(<http://www.example.org/>,     # valid\n         =<http://www.example.org/>)",
      "position": 69,
      "line": 7
    }
  ]
}
```

Historisch beabsichtigte, tatsächlich nicht erreichte Argumentprüfung:

```json
{
  "argumentPosition": 2,
  "marker": "=",
  "cause": "Argument 2 mit = ist für den beabsichtigten unmarkierten SI-Verwendungskontext ungeeignet.",
  "currentlyReached": false,
  "actualBlockingCause": "INVALID-TEMPLATE-BODY/:template-identity-tail",
  "evidence": "Originalkörper und markiertes Argument; bei 2nd-arg Originalkommentar valid/invalid."
}
```

Neue normative Entscheidung und offene Primärquellen:

```json
{
  "classification": "C",
  "scope": "Published-edition legality of unmarked additional SI variable in Topic Tail",
  "claim": "The inspected HTML excludes this body position. The current condition occurs there before argument qualification; later published grammar has not been verified.",
  "conditionalConclusion": "Body invalid under inspected HTML. This does not qualify the historical argument-rejection contract.",
  "references": [
    "CTM-HTML:3.3.5–3.3.7,3.4,3.8–3.9,3.14–3.15",
    "CTM-LANDING",
    "CTM-PREVIEW"
  ],
  "openQuestions": [
    "Q-CTM",
    "Q-ERRATA"
  ],
  "nextAction": "Keep NOT-RUN. A body-syntax negative acceptance contract would require a separate agreement even if final grammar confirms exclusion.",
  "historicalIntent": {
    "epistemicStatus": "hypothesized",
    "claim": "The corpus may have assumed variable substitution in an additional SI tail position; no editor decision/erratum proving that intention was found."
  },
  "epistemicStatus": "derived",
  "evidenceStrength": "explicit missing primary clause or interpretation; bounded conclusion from available sources"
}
```

## ctm/invalid/template-subject-locator3.ctm

Vorher: normative-conflict / C. Neue Entscheidung: **C**. Registrierung unverändert: `not-run`.

Document IRI: `https://ctm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/ctm/invalid/template-subject-locator3.ctm`.

Original: `vendor/cxtm/ctm/invalid/template-subject-locator3.ctm`, 78 Bytes; SHA-256 `d53c835df922469d65e5103f48b38faa94be56c06a4cb1da356a8ad6b277496d`.

```text

def template($iri)
    topic $iri.
end

template(=<http://www.example.org/>)
```

Quellabschluss: LF vorhanden. UTF-8-BOM: nein.

Keine positive CXTM-Baseline für diesen negativen Syntaxvertrag.

Tatsächliche Condition (einschließlich Code, Position und Cause):

```json
{
  "condition": "INVALID-TEMPLATE-BODY",
  "message": "TEMPLATE-IDENTITY-TAIL in ctm/invalid/template-subject-locator3.ctm at CHARACTER 34 (line 3, column 15): Unmarked variable identities in Topic Tails remain outside the supported grammar.",
  "code": "template-identity-tail",
  "position": 34,
  "line": 3,
  "column": 15,
  "positionUnit": "character",
  "source": "ctm/invalid/template-subject-locator3.ctm",
  "cause": null,
  "context": null
}
```

Kein natives Original-Ergebnismodell und keine Original-Ist-CXTM-Ausgabe; keine Ersatzmap konstruiert.

Erneut geprüfte Variablenpositionen, Deklaration, Aufrufe und Bindungen:

```json
{
  "variables": [
    {
      "variable": "$iri",
      "position": 14,
      "line": 2,
      "column": 14,
      "role": "Parameterdeklaration"
    },
    {
      "variable": "$iri",
      "position": 30,
      "line": 3,
      "column": 11,
      "role": "Subject Identifier von topic (unmarkiert)"
    }
  ],
  "declaration": "def template($iri)",
  "bindings": [
    [
      "$iri",
      "=<http://www.example.org/>"
    ]
  ],
  "invocations": [
    {
      "text": "template(=<http://www.example.org/>)",
      "position": 41,
      "line": 6
    }
  ]
}
```

Historisch beabsichtigte, tatsächlich nicht erreichte Argumentprüfung:

```json
{
  "argumentPosition": 1,
  "marker": "=",
  "cause": "Argument 1 mit = ist für den beabsichtigten unmarkierten SI-Verwendungskontext ungeeignet.",
  "currentlyReached": false,
  "actualBlockingCause": "INVALID-TEMPLATE-BODY/:template-identity-tail",
  "evidence": "Originalkörper und markiertes Argument; bei 2nd-arg Originalkommentar valid/invalid."
}
```

Neue normative Entscheidung und offene Primärquellen:

```json
{
  "classification": "C",
  "scope": "Published-edition legality of unmarked additional SI variable in Topic Tail",
  "claim": "The inspected HTML excludes this body position. The current condition occurs there before argument qualification; later published grammar has not been verified.",
  "conditionalConclusion": "Body invalid under inspected HTML. This does not qualify the historical argument-rejection contract.",
  "references": [
    "CTM-HTML:3.3.5–3.3.7,3.4,3.8–3.9,3.14–3.15",
    "CTM-LANDING",
    "CTM-PREVIEW"
  ],
  "openQuestions": [
    "Q-CTM",
    "Q-ERRATA"
  ],
  "nextAction": "Keep NOT-RUN. A body-syntax negative acceptance contract would require a separate agreement even if final grammar confirms exclusion.",
  "historicalIntent": {
    "epistemicStatus": "hypothesized",
    "claim": "The corpus may have assumed variable substitution in an additional SI tail position; no editor decision/erratum proving that intention was found."
  },
  "epistemicStatus": "derived",
  "evidenceStrength": "explicit missing primary clause or interpretation; bounded conclusion from available sources"
}
```

## xtm2/in/mergemap-itemid.xtm

Vorher: normative-conflict / C. Neue Entscheidung: **A**. Registrierung unverändert: `not-run`.

Document IRI: `https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/mergemap-itemid.xtm`.

Original: `vendor/cxtm/xtm2/in/mergemap-itemid.xtm`, 148 Bytes; SHA-256 `23de617d6e201374ec3f9c12e02be88bc555dd7dbcd262e854c8e9a3f96966d1`.

```xml
<topicMap xmlns="http://www.topicmaps.org/xtm/" version="2.0">
  <mergeMap href="mergemap-itemid.sub"/>
  <topic id="topic">
  </topic>
</topicMap>
```

Quellabschluss: LF vorhanden. UTF-8-BOM: nein.

Unveränderte Baseline: `vendor/cxtm/xtm2/baseline/mergemap-itemid.xtm.cxtm`, 314 Bytes; SHA-256 `03c5c1694e572674c0982f3b01d8c2fb323159ba6436857924814ea1e7a2d5d7`.

```xml
<topicMap>
<itemIdentifiers>
<locator>mergemap-itemid.sub#the-topic-map</locator>
</itemIdentifiers>
<topic number="1">
<itemIdentifiers>
<locator>#topic</locator>
</itemIdentifiers>
</topic>
<topic number="2">
<itemIdentifiers>
<locator>mergemap-itemid.sub#topic</locator>
</itemIdentifiers>
</topic>
</topicMap>
```

Tatsächliche Condition (einschließlich Code, Position und Cause):

```json
{
  "class": "XTM-UNSUPPORTED",
  "code": "unsupported-construct",
  "detail": "XTM mergeMap is not implemented in this subset.",
  "message": "XTM UNSUPPORTED-CONSTRUCT at xtm2/in/mergemap-itemid.xtm (https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/mergemap-itemid.xtm), approximately 2:41: XTM mergeMap is not implemented in this subset.",
  "line": 2,
  "column": 41,
  "positionUnit": "approximate-SAX-line-column",
  "documentIRI": "https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/mergemap-itemid.xtm",
  "sourceKey": "xtm2/in/mergemap-itemid.xtm",
  "cause": null
}
```

Kein natives Original-Ergebnismodell und keine Original-Ist-CXTM-Ausgabe; keine Ersatzmap konstruiert.

Unveränderte Hilfsquelle: `vendor/cxtm/xtm2/in/mergemap-itemid.sub`, 151 Bytes; SHA-256 `20cfc5dafa42543648b9f3ee4f41434f56f7fe7679afb0f4a1c870bde2415c01`.

```xml
<topicMap xmlns="http://www.topicmaps.org/xtm/" version="2.0">
  <itemIdentity href="#the-topic-map"/>
  <topic id="topic">
  </topic>
</topicMap>
```

Tatsächlicher Ressourcen-Referenzgraph:

```json
[
  {
    "fromDocumentIRI": "https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/mergemap-itemid.xtm",
    "href": "mergemap-itemid.sub",
    "toDocumentIRI": "https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/mergemap-itemid.sub"
  }
]
```

Separate Hilfsquellenbeobachtung, keine Originalregistrierung:

```json
[
  {
    "id": "xtm2/in/mergemap-itemid.sub",
    "kind": "auxiliary-source-only-not-an-original-contract",
    "documentIRI": "https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/mergemap-itemid.sub",
    "sourceHex": "3C746F7069634D617020786D6C6E733D22687474703A2F2F7777772E746F7069636D6170732E6F72672F78746D2F222076657273696F6E3D22322E30223E0A20203C6974656D4964656E7469747920687265663D22237468652D746F7069632D6D6170222F3E0A20203C746F7069632069643D22746F706963223E202020200A20203C2F746F7069633E0A3C2F746F7069634D61703E0A",
    "sourceBytes": 151,
    "condition": null,
    "nativeModel": {
      "topicCount": 1,
      "associationCount": 0,
      "canonicalParentsAndInverseReferences": true,
      "topics": [
        {
          "ordinal": 1,
          "itemIdentifiers": [
            "https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/mergemap-itemid.sub#topic"
          ],
          "subjectIdentifiers": [],
          "subjectLocators": []
        }
      ],
      "associations": []
    },
    "mapItemIdentifiers": [
      "https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/mergemap-itemid.sub#the-topic-map"
    ],
    "actualCXTM": "<topicMap>\n<itemIdentifiers>\n<locator>#the-topic-map</locator>\n</itemIdentifiers>\n<topic number=\"1\">\n<itemIdentifiers>\n<locator>#topic</locator>\n</itemIdentifiers>\n</topic>\n</topicMap>\n",
    "actualBytes": 185,
    "canonicalizationPreservesMap": true,
    "referencesCurrent": true
  }
]
```

Neue normative Entscheidung und offene Primärquellen:

```json
{
  "classification": "A",
  "scope": "Missing non-cyclic XTM mergeMap operation, not a claim that the baseline is fully normative",
  "claim": "The conforming non-cyclic source and available subresource require content import. The current reader rejects mergeMap before returning a model.",
  "references": [
    "XTM-HTML:4.2,4.4–4.6,4.21,5",
    "TMDM-HTML:5.1,5.2,5.3.5,6.1–6.2"
  ],
  "openQuestions": [
    "Q-ERRATA"
  ],
  "minimalCorrection": "In a separately authorized 22H, resolve pinned child bytes using the child Document IRI and native content import; preserve topic identifiers and target-map identity. No root-map II transfer solely for baseline matching.",
  "baselineAspect": {
    "epistemicStatus": "derived",
    "claim": "The expected child map II is outside the 4.21 import operands. Child model proves that this II belongs to the child Map, not its Topic. No current successful original model exists, so calling the whole case B would fail the requested B definition."
  },
  "nextAction": "Plan normative mergeMap support separately; its result may still disagree with this historical baseline. Do not forecast this original as an unconditional PASS.",
  "changeFrom22A": "Resolves the absent non-cyclic import as A using publication-identical declared XTM text; isolates the baseline root-II conflict rather than treating unsupported as an acceptable B result.",
  "epistemicStatus": "derived",
  "evidenceStrength": "publication-identical declared public XTM/TMDM plus fresh execution"
}
```

## xtm2/in/mergemap-loop.xtm

Vorher: unresolved-requirement / C. Neue Entscheidung: **C**. Registrierung unverändert: `not-run`.

Document IRI: `https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/mergemap-loop.xtm`.

Original: `vendor/cxtm/xtm2/in/mergemap-loop.xtm`, 150 Bytes; SHA-256 `033f5191ccfa3af9382a9cc6c47720f9b63b990f9485f10c3d2ac8d113b1cedb`.

```xml
<topicMap xmlns="http://www.topicmaps.org/xtm/" version="2.0">
  <mergeMap href="mergemap-loop.sub"/>
  <topic id="topic">
  </topic>
</topicMap>
```

Quellabschluss: LF vorhanden. UTF-8-BOM: nein.

Unveränderte Baseline: `vendor/cxtm/xtm2/baseline/mergemap-loop.xtm.cxtm`, 222 Bytes; SHA-256 `f0f56a0e2cf22ba274b6f10ef20cd128841908ed0f3e10de3b67b218c394fc6f`.

```xml
<topicMap>
<topic number="1">
<itemIdentifiers>
<locator>#topic</locator>
</itemIdentifiers>
</topic>
<topic number="2">
<itemIdentifiers>
<locator>mergemap-loop.sub#topic</locator>
</itemIdentifiers>
</topic>
</topicMap>
```

Tatsächliche Condition (einschließlich Code, Position und Cause):

```json
{
  "class": "XTM-UNSUPPORTED",
  "code": "unsupported-construct",
  "detail": "XTM mergeMap is not implemented in this subset.",
  "message": "XTM UNSUPPORTED-CONSTRUCT at xtm2/in/mergemap-loop.xtm (https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/mergemap-loop.xtm), approximately 2:39: XTM mergeMap is not implemented in this subset.",
  "line": 2,
  "column": 39,
  "positionUnit": "approximate-SAX-line-column",
  "documentIRI": "https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/mergemap-loop.xtm",
  "sourceKey": "xtm2/in/mergemap-loop.xtm",
  "cause": null
}
```

Kein natives Original-Ergebnismodell und keine Original-Ist-CXTM-Ausgabe; keine Ersatzmap konstruiert.

Unveränderte Hilfsquelle: `vendor/cxtm/xtm2/in/mergemap-loop.sub`, 150 Bytes; SHA-256 `94e4a9ac5ea85c2f5025cf8feff5e8eb62f5981795b0d19a8a64af1b2f69835c`.

```xml
<topicMap xmlns="http://www.topicmaps.org/xtm/" version="2.0">
  <mergeMap href="mergemap-loop.xtm"/>
  <topic id="topic">
  </topic>
</topicMap>
```

Tatsächlicher Ressourcen-Referenzgraph:

```json
[
  {
    "fromDocumentIRI": "https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/mergemap-loop.xtm",
    "href": "mergemap-loop.sub",
    "toDocumentIRI": "https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/mergemap-loop.sub"
  },
  {
    "fromDocumentIRI": "https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/mergemap-loop.sub",
    "href": "mergemap-loop.xtm",
    "toDocumentIRI": "https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/mergemap-loop.xtm"
  }
]
```

Separate Hilfsquellenbeobachtung, keine Originalregistrierung:

```json
[
  {
    "id": "xtm2/in/mergemap-loop.sub",
    "kind": "auxiliary-source-only-not-an-original-contract",
    "documentIRI": "https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/mergemap-loop.sub",
    "sourceHex": "3C746F7069634D617020786D6C6E733D22687474703A2F2F7777772E746F7069636D6170732E6F72672F78746D2F222076657273696F6E3D22322E30223E0A20203C6D657267654D617020687265663D226D657267656D61702D6C6F6F702E78746D222F3E0A20203C746F7069632069643D22746F706963223E202020200A20203C2F746F7069633E0A3C2F746F7069634D61703E0A",
    "sourceBytes": 150,
    "condition": {
      "class": "XTM-UNSUPPORTED",
      "code": "unsupported-construct",
      "detail": "XTM mergeMap is not implemented in this subset.",
      "message": "XTM UNSUPPORTED-CONSTRUCT at xtm2/in/mergemap-loop.sub (https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/mergemap-loop.sub), approximately 2:39: XTM mergeMap is not implemented in this subset.",
      "line": 2,
      "column": 39,
      "positionUnit": "approximate-SAX-line-column",
      "documentIRI": "https://xtm-tests.example.invalid/cd165b150176c1d6842b37be9cc9051b40d4996b/xtm2/in/mergemap-loop.sub",
      "sourceKey": "xtm2/in/mergemap-loop.sub",
      "cause": null
    },
    "nativeModel": null,
    "mapItemIdentifiers": null,
    "actualCXTM": null,
    "actualBytes": null,
    "canonicalizationPreservesMap": null,
    "referencesCurrent": null
  }
]
```

Neue normative Entscheidung und offene Primärquellen:

```json
{
  "classification": "C",
  "scope": "Cyclic deserialization semantics and finite model completion",
  "claim": "Root and subresource reference each other before their local Topic. The current rejection is unsupported, not cycle handling. The inspected rules do not prescribe a repeated-document cache or cycle error.",
  "references": [
    "XTM-HTML:4.2,4.21,5",
    "TMDM-HTML:5.3.5,6.1–6.2"
  ],
  "openQuestions": [
    "Q-XTM-LOOP",
    "Q-ERRATA"
  ],
  "conditionalConclusion": "A finite closure retaining both document-qualified topic identifiers is consistent with the baseline; its operational derivation needs explicit qualification.",
  "nextAction": "Separately approve a finite resolver/graph-completion acceptance contract before implementing or registering this cyclic original.",
  "epistemicStatus": "derived",
  "evidenceStrength": "explicit missing primary clause or interpretation; bounded conclusion from available sources"
}
```
