#!/usr/bin/env python3
"""Join reviewed capability annotations with existing reports and original bytes.
Documentary analysis only: no reader implementation, test system or registration.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
PIN = 'cd165b150176c1d6842b37be9cc9051b40d4996b'
NORMS = {
    'CTM': {'edition': 'ISO/IEC 13250-6:2010', 'url': 'https://www.isotopicmaps.org/ctm/ctm.html',
            'evidenceLimit': 'Public HTML mirror; published 2010 preview confirms through 3.4.2, not full 3.9/3.14-3.16. Corpus targets draft 2010-03-31.'},
    'XTM': {'edition': 'ISO/IEC 13250-3:2007 / XTM 2.0', 'url': 'https://www.isotopicmaps.org/sam/sam-xtm/',
            'evidenceLimit': '2006-06-19 public mirror explicitly states identity with published standard; ISO publication remains authoritative.'},
    'TMDM': {'edition': 'ISO/IEC 13250-2:2006', 'url': 'https://www.isotopicmaps.org/sam/sam-model/2006-06-18/',
             'evidenceLimit': 'Mirror states identity with publication; model has no standalone processor conformance section (1).'},
    'CXTM': {'edition': 'ISO/IEC 13250-4:2009', 'url': 'https://www.isotopicmaps.org/cxtm/cxtm.html',
             'evidenceLimit': 'Public 2009-01-27 mirror; final edition/errata equivalence is a closure review obligation.'},
    'XSD': {'edition': 'XML Schema 1.0 Part 2, Second Edition, 2004-10-28',
            'url': 'https://www.w3.org/TR/2004/REC-xmlschema-2-20041028/', 'evidenceLimit': 'Dated primary W3C Recommendation; no substitution of XSD 1.1.'},
    'CTM-published-preview': {'edition': 'ISO/IEC 13250-6:2010(E), first edition 2010-11-15, 11-page preview',
            'url': 'https://cdn.standards.iteh.ai/samples/43940/6663ee28c1604551ac6adc02e22c6bb6/ISO-IEC-13250-6-2010.pdf',
            'evidenceLimit': 'Public published sample inspected online only; later clauses/complete grammar unavailable in preview. No local download.'}}

FAMILIES = {
 'registration': ('Bereits bytegenau beobachtet; Registrierung fehlt', '22B'),
 'text-datatype': ('Textuelles resourceData mit beliebiger absoluter Datentyp-IRI', '22D'),
 'occurrence': ('Occurrences: Parent, Type, Scope, Resource, II, Reification, Merging', '22E'),
 'association-role': ('Explizite Associations/Roles: Type, Player, Scope, II, Merging', '22F'),
 'association-reification': ('Reification kanonischer Associations/Roles', '22G'),
 'mergemap': ('XTM mergeMap: endlicher Resolver, Dokumentidentität, Import, Zyklen', '22H'),
 'ctm-tail-grammar': ('Norm-/Qualifikationsentscheidung zum unmarkierten SI-Template-Tail', '22C'),
 'ctm-include': ('Normentscheidung zu Include-Umgebung und erhaltenen Identifiern', '22C'),
 'ctm-datetime': ('Normativ begründete DateTime-Baseline-Abweichung abschließen', '22C')}


def load(path): return json.loads(path.read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path, value): path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
def local(tag): return tag.rsplit('}', 1)[-1]
def tree(node):
    return {'element': local(node.tag), 'attributes': dict(node.attrib), 'text': node.text or '',
            'children': [tree(c) for c in node]}
def original(path):
    raw = path.read_bytes()
    return {'path': str(path.relative_to(ROOT)), 'bytes': len(raw), 'sha256': sha(path),
            'hex': raw.hex(), 'text': raw.decode('utf-8')}
def reference(key, clauses): return dict(standard=key, clauses=clauses, **NORMS[key])
def expected_model(path):
    node = ET.fromstring(path.read_bytes())
    return {'evidence': 'unchanged legacy CXTM baseline, not independent normative authority',
            'elementCounts': dict(Counter(local(n.tag) for n in node.iter())), 'xmlTree': tree(node)}


def xtm_features(source):
    node = ET.fromstring(source.read_bytes())
    elements = list(node.iter())
    names = [local(n.tag) for n in elements]
    reifiers = [{'element': local(n.tag), 'iri': n.get('reifier')} for n in elements if n.get('reifier') is not None]
    required = []
    for tag, capability in [('occurrence', 'occurrence'), ('association', 'association-role'), ('role', 'association-role')]:
        if tag in names and capability not in required: required.append(capability)
    for name in sorted({r['element'] for r in reifiers}): required.append(name + '-reification')
    if 'itemIdentity' in names: required.append('native-item-identifiers-and-normalization')
    if 'scope' in names: required.append('canonical-scope-set-and-reference-merging')
    if 'resourceRef' in names: required.append('resource-IRI-resolution')
    datatypes = [n.get('datatype', 'http://www.w3.org/2001/XMLSchema#string') for n in elements if local(n.tag) == 'resourceData']
    if 'http://example.com/bogus' in datatypes: required.append('text-datatype')
    if 'mergeMap' in names: required.append('mergemap')
    return {'elementCounts': dict(Counter(names)), 'reifiers': reifiers, 'datatypes': datatypes,
            'resourceReferences': [n.get('href') for n in elements if local(n.tag) == 'resourceRef'],
            'topicReferences': [n.get('href') for n in elements if local(n.tag) == 'topicRef'],
            'sourceTree': tree(node), 'requiredCapabilities': required}


def xtm_annotation(id, f):
    names = f['elementCounts']; rs = {r['element'] for r in f['reifiers']}
    negative = '/invalid/' in id
    if id == 'xtm2/in/variant-duplicate-reifier2.xtm': group = 'registration'
    elif 'mergeMap' in names: group = 'mergemap'
    elif 'occurrence' in names: group = 'occurrence'
    elif 'association' in rs or 'role' in rs: group = 'association-reification'
    elif 'association' in names: group = 'association-role'
    else:
        assert id == 'xtm2/in/variant-datatype-unknown.xtm'
        group = 'text-datatype'
    clauses = ['4.2', '4.3.1-4.3.4']
    model_clauses = ['5.1', '5.2', '5.3', '6.2']
    if 'topicRef' in names: clauses.append('4.20')
    if 'scope' in names: clauses.append('4.13')
    if 'type' in names: clauses.append('4.14')
    if 'occurrence' in names: clauses.append('4.15'); model_clauses += ['5.6', '6.5']
    if 'variant' in names: clauses.append('4.12'); model_clauses += ['5.5', '6.4']
    if 'resourceData' in names: clauses.append('4.16.1-4.16.2')
    if 'resourceRef' in names: clauses.append('4.17')
    if 'association' in names: clauses += ['4.18', '4.19']; model_clauses += ['5.7', '5.8', '6.6', '6.7']
    if 'itemIdentity' in names: clauses.append('4.6')
    if group == 'mergemap': clauses.append('4.21')
    deps = {
      'registration': ['existing-qualified-variant-reification'],
      'text-datatype': ['existing-qualified-XML-and-resourceData-string-path'],
      'occurrence': ['existing-native-add-occurrence-canonical-occurrence-II-reifier-APIs'],
      'association-role': ['existing-native-make-association-and-canonical-association-role-APIs'],
      'association-reification': ['22F', 'existing-native-II-only-reifier-resolution'],
      'mergemap': ['22C:map-metadata-and-cycle-decisions', 'existing-qualified-XML-and-native-import-map-content']
    }[group]
    if group == 'occurrence' and 'text-datatype' in f['requiredCapabilities']: deps += ['22D']
    classification = 'already-observed-unregistered' if group == 'registration' else 'missing-language-capability'
    decision = None
    issue = 'Normstellen geprüft; Originalmodell und Originalvergleich erst nach Implementierung zu qualifizieren.'
    if id == 'xtm2/in/mergemap-itemid.xtm':
        classification = 'normative-conflict'; decision = 'C'
        issue = 'Vorläufiger Konflikt: Baseline überträgt Quell-Map-II, 4.21 nennt nur Topics/Associations; endgültige Norm-/Errataentscheidung offen. Keine Zusage eines PASS.'
    elif id == 'xtm2/in/mergemap-loop.xtm':
        classification = 'unresolved-requirement'; decision = 'C'
        issue = 'Positive Baseline fordert Terminierung mit beiden Dokumenten. Explizite Zyklus-/Cache-Semantik im geprüften Text nicht angegeben; Profilentscheidung/Primärbeleg erforderlich.'
    elif group == 'registration': issue = 'Erneut ausgeführt und 702/702 Bytes gleich; native Beziehungen geprüft; Case Record bleibt NOT-RUN.'
    intended = None
    if id == 'xtm2/invalid/reifier-collision.xtm':
        intended = {'cause': 'Dasselbe #reifier-Topic reifiziert Map und Occurrence, also verschiedene Items.',
                    'requiredCondition': 'REIFICATION-ERROR', 'requiredCode': 'reifier-conflict',
                    'currentlyReached': False, 'evidence': 'Original-Attributwerte und Kommentar; TMDM 5.3.5 / 6.2.'}
    elif id == 'xtm2/invalid/role-duplicate-reified.xtm':
        intended = {'cause': 'Gleicher Role-Type/Player und Reifier bei ungleichen Association-Parents (#assoctype vs #assoctype2). Rollen sind nicht gleich.',
                    'requiredCondition': 'REIFICATION-ERROR', 'requiredCode': 'reifier-conflict',
                    'currentlyReached': False, 'evidence': 'Originalkommentar sowie TMDM 5.8 (Parent in Gleichheit), 5.3.5 / 6.2.'}
    elif id == 'xtm2/invalid/topicref-no-fragment-id.xtm':
        intended = {'cause': 'Association-Scope topicRef href="scopingtopic" hat keinen Shorthand-Fragment-Identifier.',
                    'requiredCondition': 'XTM-REJECTION', 'requiredCode': 'invalid-topic-ref',
                    'currentlyReached': False, 'evidence': 'Originalkommentar, XTM 4.13 / 4.20.'}
    return {'family': group, 'familyDescription': FAMILIES[group][0], 'primaryClassification': classification,
      'normativeDecisionABC': decision, 'normativeJustificationStatus': issue,
      'normativeReferences': [reference('XTM', clauses), reference('TMDM', model_clauses), reference('CXTM', ['3-4'])],
      'missingCapability': FAMILIES[group][0] if group != 'registration' else 'Nur dauerhafte Originalregistrierung; keine Produktionsänderung.',
      'dependencies': deps, 'proposedSlice': FAMILIES[group][1], 'intendedNegativeCause': intended,
      'forecastIsNotExecutedPASS': True, 'expectedOutcome': 'qualified-rejection' if negative else 'byte-exact-CXTM'}


def ctm_annotation(case, obs, detailed):
    id = case['id']; negative = case['category'] == 'invalid'
    if '/template-' in id:
        group = 'ctm-tail-grammar'; decision = 'C'; category = 'normative-conflict'
        refs = [reference('CTM', ['3.3.5 [12]', '3.3.6 [13],[17]-[19]', '3.3.7 [20]-[21]', '3.4 [28]', '3.8 [49]', '3.9 [50]-[52]', '3.14 [63]-[67]', '3.15 [68]-[70]'])]
        missing = 'Keine belegte fehlende Normfähigkeit: Variable im unmarkierten zusätzlichen SI-Slot ist in der geprüften Ableitung nicht vorgesehen.'
        status = 'HTML-Ableitung [50]→[51]→[52]→[17]→[12] geprüft; vollständigen veröffentlichten Grammatiktext abgleichen, keine stillschweigende Erweiterung.'
        proposed = '22C: Striktes Profil bestätigen; positive Korpusabweichung begründet ausweisen. Negativen Originalen keinen argumentbezogenen PASS geben, solange die vorgesehene Substitutionsprüfung nicht erreicht ist.'
        if negative:
            status += ' Die frühe Body-Syntaxablehnung ist keine erreichte Prüfung des markierten Arguments.'
            proposed += ' Alternative normative Grammatik-Ablehnung nur nach ausdrücklich geänderter Qualifikationsentscheidung; gültige Kontextgegenprobe separat, kein Ersatzoriginal.'
    elif '/include-' in id:
        group = 'ctm-include'; decision = 'C'; category = 'unresolved-requirement'
        refs = [reference('CTM', ['3.2', '3.3.6', '3.3.8', '3.14-3.15', '3.16.2']), reference('TMDM', ['5-6']), reference('CXTM', ['3.13', '3.17-3.18'])]
        missing = 'Keine nachgewiesene fehlende Fähigkeit; bestehende Umgebung-/Alias-Auslegung gegen maßgeblichen vollständigen Normtext entscheiden.'
        status = 'B nach bisheriger Mirror-Auslegung plausibel; formaler Abschluss C, weil veröffentlichte spätere CTM-Klauseln hier nicht vollständig primär verifiziert sind.'
        proposed = '22C: unverändert FAIL; vollständige Primärfassung/Errata beschaffen lassen und A/B entscheiden. Nur bei nachgewiesenem A eine gesondert freigegebene minimale Korrektur planen.'
    else:
        assert '/occurrence-datetime' in id
        group = 'ctm-datetime'; decision = 'B'; category = 'normative-conflict'
        refs = [reference('CTM-published-preview', ['3.4.1 (printed p.5)']), reference('XSD', ['3.2.7.1-3.2.7.3', 'D.1']), reference('CXTM', ['3.16', '4.9']), reference('TMDM', ['4.3-4.4', '5.6', '6.5'])]
        missing = 'Keine Reader-Erweiterung zur Nachbildung der Baseline; qualifizierten Baseline-Konflikt abschließen.'
        status = 'B durch untersuchte XSD-1.0-/CXTM-Regeln gestützt; öffentliche CXTM-Fassung/Errata im abschließenden Editionsreview bestätigen.'
        proposed = '22C: aktuellen Wert erhalten, FAIL und Normabweichung ausweisen; niemals Originalbaseline oder fallabhängige Ausgabe anpassen.'
    negative_intent = None
    if negative:
        marker = '^' if 'item-identifier' in id else '='
        number = 2 if '2nd-arg' in id else 1
        negative_intent = {'argumentPosition': number, 'marker': marker,
          'cause': f'Argument {number} mit {marker} ist für den beabsichtigten unmarkierten SI-Verwendungskontext ungeeignet.',
          'currentlyReached': False, 'actualBlockingCause': 'INVALID-TEMPLATE-BODY/:template-identity-tail',
          'evidence': 'Originalkörper und markiertes Argument; bei 2nd-arg Originalkommentar valid/invalid.'}
    return {'family': group, 'familyDescription': FAMILIES[group][0], 'primaryClassification': category,
       'normativeDecisionABC': decision, 'normativeJustificationStatus': status, 'normativeReferences': refs,
       'missingCapability': missing, 'dependencies': ['22C:authoritative-edition-and-qualification-decision'],
       'proposedSlice': '22C', 'proposedDecision': proposed, 'intendedNegativeCause': negative_intent,
       'templateAnalysis': ({k: detailed[k] for k in ['variables', 'declaration', 'bindings', 'invocations'] if k in detailed} if detailed else None),
       'forecastIsNotExecutedPASS': True}


def make_matrix(baseline, observations):
    ctm = load(baseline / 'ctm.validation.json'); xtm = load(baseline / 'xtm.json')
    assert ctm == load(ROOT / 'reports/slice-21o/ctm.validation.json')
    assert xtm == load(ROOT / 'reports/slice-21o/xtm.json')
    registered = {c['id']: c for c in xtm['cases']}
    diagnostics = {c['id']: c for c in load(baseline / 'after-diagnostics.json')}
    actual_ctm = {c['id']: c for c in load(observations / 'ctm-observations.json')['cases']}
    old_templates = {c['id']: c for c in load(ROOT / 'reports/slice-20j/slice20i/detailed-inventory.json')['cases']}
    controls = load(observations / 'controls.json')
    rows = []
    for c in ctm['cases']:
        if c['status'] == 'pass': continue
        id = c['id']; obs = actual_ctm[id]; source = ROOT / 'vendor/cxtm' / id
        assert bytes.fromhex(obs['sourceHex']) == source.read_bytes()
        d = old_templates.get(id)
        if d:
            assert sha(source) == d['sourceSHA256'] and obs['condition'] == d['condition']
        baseline_path = ROOT / 'vendor/cxtm' / c['expectedCXTM'] if c['expectedCXTM'] else None
        ann = ctm_annotation(c, obs, d)
        row = {'id': id, 'corpus': 'CTM', 'normVersion': NORMS['CTM']['edition'],
          'corpusVersion': 'CTM draft 2010-03-31, pin ' + PIN,
          'category': c['category'], 'registeredStatus': c['status'], 'caseRecord': c,
          'source': original(source), 'documentIRI': c['documentIRI'], 'condition': obs['condition'],
          'expected': {'outcome': c['expectedOutcome'], 'baseline': original(baseline_path) if baseline_path else None,
                       'baselineModel': expected_model(baseline_path) if baseline_path else None},
          'observation': obs, **ann}
        if d and d.get('expandedControl'):
            expanded = next(x for x in controls if x['originalControlOnly'] == id)
            assert expanded == d['expandedControl']
            row['expandedControl'] = expanded
        rows.append(row)
    xtm_catalog = sorted([* (ROOT/'vendor/cxtm/xtm2/in').glob('*.xtm'), * (ROOT/'vendor/cxtm/xtm2/invalid').glob('*.xtm')])
    assert len(xtm_catalog) == 124
    for source in xtm_catalog:
        id = str(source.relative_to(ROOT/'vendor/cxtm'))
        if id in registered: continue
        negative = '/invalid/' in id
        baseline_path = None if negative else ROOT/'vendor/cxtm/xtm2/baseline'/(source.name+'.cxtm')
        f = xtm_features(source); obs = diagnostics[id]; ann = xtm_annotation(id, f)
        row = {'id': id, 'corpus': 'XTM 2.0', 'normVersion': NORMS['XTM']['edition'],
          'corpusVersion': PIN, 'category': 'invalid' if negative else 'valid', 'registeredStatus': 'not-run',
          'caseRecord': None, 'caseRecordProvenance': 'Current registered IDs subtracted from exact 124-file original inventory; not a newly registered Case Record.',
          'source': original(source), 'documentIRI': obs['documentIRI'], 'condition': obs['condition'],
          'expected': {'outcome': 'xtm-rejection' if negative else 'cxtm-equal',
                       'baseline': original(baseline_path) if baseline_path else None,
                       'baselineModel': expected_model(baseline_path) if baseline_path else None},
          'sourceFeatures': f, 'observation': obs, **ann}
        if ann['family'] == 'registration':
            further = load(baseline/'further-variant-reification.json')
            assert further['id'] == id and not further['registered'] and further['byteExact']
            row['nativeModelObservation'] = further
        if ann['family'] == 'mergemap':
            child = source.parent / next(n.get('href') for n in ET.fromstring(source.read_bytes()).iter() if local(n.tag) == 'mergeMap')
            row['auxiliarySource'] = original(child)
            refs = [n.get('href') for n in ET.fromstring(child.read_bytes()).iter() if local(n.tag) == 'mergeMap']
            row['auxiliaryMergeMapReferences'] = refs
            row['referencesRootAgain'] = source.name in refs
        rows.append(row)
    rows.sort(key=lambda c: c['id'])
    assert len(rows) == len({c['id'] for c in rows}) == 65
    assert Counter(c['corpus'] for c in rows) == {'CTM': 11, 'XTM 2.0': 54}
    assert Counter(c['registeredStatus'] for c in rows) == {'fail':4, 'not-run':61}
    assert Counter(c['category'] for c in rows) == {'valid':58, 'invalid':7}
    assert sum(c['expected']['baseline'] is not None for c in rows) == 58
    groups = {g: {'description': d[0], 'proposedSlice': d[1], 'caseIDs': [c['id'] for c in rows if c['family'] == g]} for g,d in FAMILIES.items()}
    return {'schemaVersion':1, 'kind':'documentary-conformance-closure-matrix-no-registration',
       'baseCommit':'1c0b92c68fe1114b926d4405b553dfb096d2f425', 'corpusPin':PIN,
       'norms':NORMS, 'registeredStatusesUnchanged':True,
       'registeredTotals':{'CTM':{'pass':262,'fail':4,'not-run':7,'total':273}, 'XTM':{'pass':70,'fail':0,'not-run':54,'total':124},
                           'combined':{'pass':332,'fail':4,'not-run':61,'total':397}},
       'openCounts': {'total':65, 'ctm':11, 'xtm':54, 'positive':58, 'negative':7,
                      'byClassification': dict(Counter(c['primaryClassification'] for c in rows))},
       'families':groups, 'cases':rows}


def markdown_matrix(matrix):
    lines = ['# Slice 22A — Vollständige Konformitätsmatrix der 65 offenen Originale', '',
      'Alle Statuswerte stammen aus der frisch reproduzierten Slice-21O-Registrierung. Beobachtungen ersetzen keine Registrierung. Vollständige Bytes, SHA-256, Quellen, Baselines, Modelle, Causes und pro Fall Normedition/Fundstellen stehen in [matrix.json](../reports/slice-22a/matrix.json).', '',
      'Normeditionen: CTM = ISO/IEC 13250-6:2010 (Korpusentwurf 2010-03-31); XTM = ISO/IEC 13250-3:2007 / XTM 2.0; TMDM = 13250-2:2006; CXTM = 13250-4:2009. Grenzen der Primärevidenz und A/B/C-Entscheidungen: [Abschlussplan](slice-22a-conformance-closure.md).', '',
      'Kategorien: **F** fehlende Sprachfähigkeit; **N** Norm-/Baseline-Konflikt (gegebenenfalls vorläufig); **U** ungeklärte Anforderung; **R** bereits erfolgreich beobachtet, unregistriert. Prognosen sind keine neu ausgeführten PASS.', '']
    kinds={'valid':'positiv (Korpus)', 'invalid':'negativ (Korpus)'}
    cats={'missing-language-capability':'F','normative-conflict':'N','unresolved-requirement':'U','already-observed-unregistered':'R'}
    for corpus in ['CTM','XTM 2.0']:
        lines += ['## '+corpus, '', '| Case-ID / Originalquelle | Art / Status | Kategorie | Tatsächliche Condition / Position | Erwartung | Fehlende Fähigkeit / Abhängigkeiten | Normstellen / Begründungsstand | Nächster Slice |', '|---|---|---|---|---|---|---|---|']
        for row in matrix['cases']:
            if row['corpus'] != corpus: continue
            c=row['condition']; cond='keine; ' + ('702/702 Bytes gleich (nur Diagnose)' if row['family']=='registration' else 'CXTM-Abweichung')
            if c:
                cond=f"`{c.get('class',c.get('condition'))}/:{c['code']}`; "
                if c.get('position') is not None:cond+=f"Zeichen {c['position']}, "
                cond+=f"{c['line']}:{c['column']}" if c.get('line') is not None else 'Position null'
            b=row['expected']['baseline'];expected=f"[{b['bytes']} CXTM-Bytes](../{b['path']})" if b else 'qualifizierte Ablehnung; keine Baseline'
            refs='; '.join(x['standard']+' '+', '.join(x['clauses']) for x in row['normativeReferences'])
            deps=', '.join(row['dependencies']);proof=row['normativeDecisionABC'] or 'Klauseln geprüft; Ausführung offen'
            lines.append(f"| [`{row['id']}`](../{row['source']['path']}) | {kinds[row['category']]} / **{row['registeredStatus'].upper()}** | {cats[row['primaryClassification']]} | {cond} | {expected} | {row['familyDescription']}; {deps} | {refs}; {proof} | {row['proposedSlice']} |")
        lines.append('')
    lines += ['Alle 65 Zeilen sind eindeutige Original-Case-IDs. `.sub`-Ressourcen und synthetische Gegenproben werden nicht mitgezählt. Registrierung und historische Reports bleiben unverändert.', '']
    return '\n'.join(lines)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--observations',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--markdown',type=Path)
    a=p.parse_args();matrix=make_matrix(a.baseline,a.observations);save(a.output,matrix)
    if a.markdown:a.markdown.write_text(markdown_matrix(matrix))
    print(json.dumps(matrix['openCounts']))

if __name__=='__main__':main()
