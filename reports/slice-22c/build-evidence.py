#!/usr/bin/env python3
"""Assemble documentary evidence from fresh observations, never register results.
The XML comparison view below is report-only: it does not construct native maps,
feed the reader, or participate in the conformance executor.
"""
import argparse, difflib, hashlib, json, re
from pathlib import Path
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
ROOT=Path(__file__).resolve().parents[2]
HYPERDOC=Path('/Users/rgb/workspace/hyperdoc-dreyeck-ch')
def read(p):return json.loads(p.read_text())
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(b):return hashlib.sha256(b).hexdigest()
def file_data(p):
    b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b),hex=b.hex(),text=b.decode('utf-8'))
def tree(e):return dict(element=e.tag,attributes=dict(e.attrib),text=e.text or '',children=[tree(c) for c in e])
def identifiers(e):return {(k,x.text) for k in ['itemIdentifiers','subjectIdentifiers','subjectLocators'] for x in e.findall(k+'/locator')}
def compare_models(actual,expected,native,doc):
    # Match by shared identifiers; canonical topic ordinals are not identities.
    a,b=ET.fromstring(actual),ET.fromstring(expected)
    at,bt=a.findall('topic'),b.findall('topic');assert len(at)==len(bt)==native['topicCount']
    keys_a={};keys_b={};alignment=[]
    for t in at:
        candidates=[u for u in bt if identifiers(t)&identifiers(u)]
        assert len(candidates)==1
        u=candidates[0];anchor=sorted(identifiers(t)&identifiers(u))[0];key=':'.join(anchor)
        keys_a[t.get('number')]=key;keys_b[u.get('number')]=key
        alignment.append(dict(anchor=list(anchor),actualTopicNumber=t.get('number'),expectedTopicNumber=u.get('number')))
    assert len(keys_b)==len(bt)
    def normalized(e,keys):
        attrs={k:(keys[v] if k in ['topicref','reifier'] else v) for k,v in e.attrib.items() if k!='number'}
        kids=[normalized(c,keys) for c in e]
        if e.tag=='topicMap':kids=sorted(kids,key=lambda x:json.dumps(x.get('identity','')))
        result=dict(element=e.tag,attributes=attrs,text=e.text if not len(e) else '',children=kids)
        if e.tag=='topic':result['identity']=keys[e.get('number')]
        return result
    aa,bb=normalized(a,keys_a),normalized(b,keys_b)
    # Independently reconcile every observed native topic/name/occurrence with
    # its actual CXTM element, resolving only the relative locator forms here.
    native_keys={}
    for t in native['topics']:
        ids={(k,v) for k in ['itemIdentifiers','subjectIdentifiers','subjectLocators'] for v in t[k]}
        matches=[e for e in at if ids=={(k,urljoin(doc,v)) for k,v in identifiers(e)}]
        assert len(matches)==1
        native_keys[t['ordinal']]=keys_a[matches[0].get('number')]
    for t in native['topics']:
        e=next(e for e in at if keys_a[e.get('number')]==native_keys[t['ordinal']])
        for kind,field in [('name','names'),('occurrence','occurrences')]:
            xs=e.findall(kind);assert len(xs)==len(t[field])
            for record,x in zip(t[field],xs):
                assert record['parent']==t['ordinal'] and record['value']==x.findtext('value')
                assert keys_a[x.find('type').get('topicref')]==native_keys[record['type']]
                assert sorted(native_keys[n] for n in record['scope'])==sorted(keys_a[s.get('topicref')] for s in x.findall('scope/scopingTopic'))
                if kind=='occurrence':assert record['datatype']==x.findtext('datatype')
                else:assert record['variantCount']==len(x.findall('variant'))==0
    assert len(a.findall('association'))==native['associationCount']==0
    def walk(x,y,path=''):
        if x==y:return []
        if isinstance(x,dict) and isinstance(y,dict):return sum((walk(x.get(k),y.get(k),path+'/'+k) for k in sorted(x.keys()|y.keys())),[])
        if isinstance(x,list) and isinstance(y,list) and len(x)==len(y):return sum((walk(v,w,path+'/'+str(i)) for i,(v,w) in enumerate(zip(x,y))),[])
        return [dict(path=path,actual=x,expected=y)]
    return dict(kind='report-only-XML-view-not-a-replacement-TMDM',topicAlignment=alignment,
        nativePropertiesMatchActualCXTM=True,actual=aa,expected=bb,differences=walk(aa,bb))
def render_appendix(rows):
    lines=['# Slice 22C — Originale, Baselines und tatsächliche Beobachtungen', '',
        'Generiert aus der erneut geprüften fallbezogenen Evidenz. [Entscheidungen und Editionsgrenzen](slice-22c-normative-decisions.md); [vollständige JSON-Evidenz](../reports/slice-22c/case-evidence.json).', '',
        'Quellbytes, Hashes und Prozessresultate sind `observed`; grammatische Rollen sind `derived`, historische Argumentabsichten `inferred`. Zeichenpositionen sind nullbasiert, Zeile/Spalte einsbasiert. XTM-Positionen bleiben die ungefähr gemeldeten SAX-Positionen. Die Lesefassung blendet Leerraum am Zeilenende aus; Text und Hexwerte im JSON erhalten sämtliche Originalbytes einschließlich BOM und fehlendem Schluss-LF.', '']
    def blob(label,b):
        lines.extend([label+': `'+b['path']+'`, '+str(b['bytes'])+' Bytes; SHA-256 `'+b['sha256']+'`.', '',
            '```'+('xml' if (b['path'].endswith(('.xtm','.cxtm')) or '/xtm2/' in b['path']) else 'text'),b['text'].rstrip('\n'),'```',''])
    def structured(label,obj):
        lines.extend([label,'','```json',json.dumps(obj,ensure_ascii=False,indent=2),'```',''])
    for c in rows:
        lines.extend(['## '+c['id'],'',
            'Vorher: '+c['priorClassification']+' / '+c['priorDecision']+'. Neue Entscheidung: **'+c['decision']['classification']+'**. Registrierung unverändert: `'+c['registeredAfter']+'`.', '',
            'Document IRI: `'+c['documentIRI']+'`.', ''])
        blob('Original',c['source'])
        lines.extend(['Quellabschluss: '+('LF vorhanden.' if c['source']['text'].endswith('\n') else 'kein abschließendes LF.')+' UTF-8-BOM: '+('ja.' if c['source']['hex'].startswith('efbbbf') else 'nein.'),''])
        if c['baseline']:blob('Unveränderte Baseline',c['baseline'])
        else:lines.extend(['Keine positive CXTM-Baseline für diesen negativen Syntaxvertrag.',''])
        structured('Tatsächliche Condition (einschließlich Code, Position und Cause):',c['actualCondition'])
        if c['actualCXTM']:
            lines.extend(['Ist-CXTM: '+str(c['actualCXTM']['bytes'])+' Bytes, SHA-256 `'+c['actualCXTM']['sha256']+'`. Vollständiger Bytevergleich: **nicht identisch**. Erste Differenz: '+str(c['comparison']['firstDifferentByte'])+'.','','```xml',c['actualCXTM']['text'].rstrip('\n'),'```',''])
            structured('Verbleibende Modelldifferenzen nach Identitätszuordnung:',c['completeModelComparison']['differences'])
        else:lines.extend(['Kein natives Original-Ergebnismodell und keine Original-Ist-CXTM-Ausgabe; keine Ersatzmap konstruiert.',''])
        if c.get('templateAnalysis'):
            structured('Erneut geprüfte Variablenpositionen, Deklaration, Aufrufe und Bindungen:',c['templateAnalysis'])
            for control in c['expandedControls']:
                lines.extend(['Ausgeschriebene Gegenprobe (kein Original-PASS): '+str(len(control['actualCXTM'].encode()))+'/'+str(c['baseline']['bytes'])+' Bytes identisch; Condition null.',''])
            if c.get('intendedNegativeCause'):structured('Historisch beabsichtigte, tatsächlich nicht erreichte Argumentprüfung:',c['intendedNegativeCause'])
        for a in c['auxiliarySources']:blob('Unveränderte Hilfsquelle',a)
        if c.get('sourceReferenceGraph'):structured('Tatsächlicher Ressourcen-Referenzgraph:',c['sourceReferenceGraph'])
        if c.get('auxiliaryObservations'):structured('Separate Hilfsquellenbeobachtung, keine Originalregistrierung:',c['auxiliaryObservations'])
        structured('Neue normative Entscheidung und offene Primärquellen:',c['decision'])
    return '\n'.join(line.rstrip() for line in '\n'.join(lines).splitlines()).rstrip()+'\n'
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--execution',type=Path,required=True);ap.add_argument('--regression',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();out=args.output.resolve();assert not out.is_relative_to(ROOT) and not out.is_relative_to(HYPERDOC);out.mkdir(parents=True,exist_ok=True)
    matrix=read(ROOT/'reports/slice-22a/matrix.json')
    old=[c for c in matrix['cases'] if c['id'].startswith('ctm/') or c['id'] in ['xtm2/in/mergemap-itemid.xtm','xtm2/in/mergemap-loop.xtm']]
    assert len(old)==13
    ctm={c['id']:c for c in read(args.execution/'investigation/ctm-observations.json')['cases']}
    xtm={c['id']:c for c in read(args.regression/'after-diagnostics.json')}
    states={c['id']:c['status'] for c in read(args.regression/'ctm.validation.json')['cases']}
    registered={c['id'] for c in read(args.regression/'xtm.json')['cases']}
    controls=read(args.execution/'investigation/controls.json');rows=[]
    decisions=read(Path(__file__).parent/'decisions.json')
    for prior in old:
        id=prior['id'];obs=ctm.get(id,xtm.get(id));assert obs==prior['observation'],id
        source=file_data(ROOT/prior['source']['path']);assert source==prior['source']
        baseline=prior['expected']['baseline']
        if baseline:assert file_data(ROOT/baseline['path'])==baseline
        status=states.get(id,'not-run');assert status==prior['registeredStatus']
        if id.startswith('xtm2/'):assert id not in registered
        actual=obs.get('actualCXTM');model=obs.get('model')
        condition=obs['condition']
        row=dict(id=id,epistemicStatus='observed',category=prior['category'],registeredBefore=status,registeredAfter=status,
            source=source,documentIRI=prior['documentIRI'],baseline=baseline,actualCondition=condition,nativeModel=model,
            observation=obs,priorClassification=prior['primaryClassification'],priorDecision=prior['normativeDecisionABC'],
            priorJustification=prior['normativeJustificationStatus'],decision=decisions[id],
            actualCXTM=None if actual is None else dict(bytes=len(actual.encode()),sha256=sha(actual.encode()),hex=actual.encode().hex(),text=actual),
            comparison=dict(executed=actual is not None and baseline is not None,byteExact=None if actual is None or baseline is None else actual==baseline['text'],
                firstDifferentByte=next((i for i,(a,b) in enumerate(zip(actual.encode(),bytes.fromhex(baseline['hex']))) if a!=b),min(len(actual.encode()),baseline['bytes']) if len(actual.encode())!=baseline['bytes'] else None) if actual is not None and baseline else None),
            nativeModelUnavailableReason=None if model else 'Reader rejected before returning an original map; no replacement map constructed.')
        if actual is not None and baseline:
            row['completeModelComparison']=compare_models(actual,baseline['text'],model,prior['documentIRI'])
            diff=''.join(difflib.unified_diff(baseline['text'].splitlines(True),actual.splitlines(True),fromfile='unchanged-original-baseline',tofile='fresh-actual'))
            (out/(Path(id).name+'.diff')).write_text(diff)
            (out/(Path(id).name+'.actual.cxtm')).write_bytes(actual.encode())
            row['completeCXTMUnifiedDiff']=diff
        if prior.get('templateAnalysis') is not None:
            row['templateAnalysis']=prior['templateAnalysis'];row['intendedNegativeCause']=prior['intendedNegativeCause']
            variables=prior['templateAnalysis']['variables']
            matches=list(re.finditer(r'\$[A-Za-z_][A-Za-z_0-9]*',source['text']))
            assert [(m.group(),m.start()) for m in matches]==[(v['variable'],v['position']) for v in variables]
            for v in variables:
                prefix=source['text'][:v['position']]
                assert v['line']==prefix.count('\n')+1 and v['column']==len(prefix.rsplit('\n',1)[-1])+1
            row['variablePositionsReverifiedFromOriginal']=True
            row['templateAnalysisProvenance']={'positions':'observed: reverified from unchanged original text','roles':'derived: manually reviewed against source syntax and cited grammar','historicalArgumentIntent':'inferred from original argument markers and comments; not an executed argument check'}
            matches=[c for c in controls if c.get('originalControlOnly')==id]
            row['expandedControls']=matches
            for c in matches:assert c['byteExact'] and c['condition'] is None and c['actualCXTM']==baseline['text']
        auxiliaries=[]
        if 'include-' in id:
            for request in obs['requests']:auxiliaries.append(file_data(ROOT/'vendor/cxtm'/request['sourceKey']))
        elif id.startswith('xtm2/'):
            auxiliaries.append(file_data(ROOT/prior['auxiliarySource']['path']))
            refs=[]
            for f in [source,*auxiliaries]:
                root=ET.fromstring(f['text']);doc=urljoin(prior['documentIRI'],Path(f['path']).name)
                for e in root.findall('{http://www.topicmaps.org/xtm/}mergeMap'):
                    refs.append(dict(fromDocumentIRI=doc,href=e.get('href'),toDocumentIRI=urljoin(doc,e.get('href'))))
            row['sourceReferenceGraph']=refs
            row['auxiliaryObservations']=[x for x in read(args.execution/'investigation/xtm-auxiliary.json') if x['id']==prior['auxiliarySource']['path'].removeprefix('vendor/cxtm/')]
        row['auxiliarySources']=auxiliaries
        rows.append(row)
    counts={k:sum(c['decision']['classification']==k for c in rows) for k in 'ABC'}
    save(out/'case-evidence.json',dict(kind='slice-22c-independent-normative-decisions-no-registration',baseCommit='bc9dcfb02f945422970d65266dc66b991806777d',
        matrixSHA256=sha((ROOT/'reports/slice-22a/matrix.json').read_bytes()),closureDeltaSHA256=sha((ROOT/'reports/slice-22b/after/closure-delta.json').read_bytes()),
        cases=rows,decisionCounts=counts,statusChanges=0,newPASS=0))
    (out/'slice-22c-original-evidence.md').write_text(render_appendix(rows))
    print(json.dumps(dict(cases=len(rows),decisions=counts,output=str(out))))
if __name__=='__main__':main()
