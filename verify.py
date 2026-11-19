"""Verify included exact certificates and all supplied sample mappings; no solver."""
import copy,hashlib,importlib.util,json,shutil,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import checker

def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
independent=module('independent_certificate_checker',ROOT/'independent/certificate_checker.py')
mapping=module('mapping_checker',ROOT/'independent/mapping_checker.py')

def main():
 assert not sys.flags.optimize, 'Assertions must be enabled'
 lines=(ROOT/'MANIFEST.sha256').read_text().splitlines()
 expected={}
 for line in lines:
  digest,name=line.split('  ',1);assert name not in expected and not name.startswith('/') and '..' not in Path(name).parts
  expected[name]=digest
 actual={str(f.relative_to(ROOT)) for f in ROOT.rglob('*') if f.is_file() and '.git' not in f.relative_to(ROOT).parts and f.name!='MANIFEST.sha256'}
 assert actual==set(expected), 'manifest file set mismatch'
 for name,digest in expected.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest, name
 proof_files=sorted((ROOT/'data/proofs').glob('*.json'))+[ROOT/'data/improved-output/result.json']+sorted((ROOT/'data/examples-output').glob('*/result.json'))
 assert len(proof_files)==60
 counts={}
 for path in proof_files:
  obj=json.loads(path.read_text());checker.verify(path,False,True);independent.verify(obj)
  counts[obj['status']]=counts.get(obj['status'],0)+1
 assert counts=={'OPTIMAL':56,'FEASIBLE':3,'UNSAT':1},counts
 old=json.loads((ROOT/'data/proofs/k5_b11.json').read_text());new=json.loads((ROOT/'data/improved-output/result.json').read_text())
 assert independent.primal(old['spec'],old['table'])[0]==16093
 assert independent.primal(new['spec'],new['table'])[0]==16092
 broken=copy.deepcopy(json.loads((ROOT/'data/examples-output/unsat/result.json').read_text()))
 broken['certificate']['tree']['dual']={}
 try:independent.verify(broken)
 except AssertionError:pass
 else:raise AssertionError('forged UNSAT certificate accepted')
 with tempfile.TemporaryDirectory(prefix='dp-verify-') as tmp:
  runs=Path(tmp)/'runs';shutil.copytree(ROOT/'data/runs',runs)
  paths=sorted(runs.glob('*/*/result.json'));assert len(paths)==108
  words=0
  for path in paths:
   r=mapping.verify(path,True);assert r['status']=='PASS';words+=r['words']
  for sub in ['improved-output','examples-output']:
   shutil.copytree(ROOT/'data'/sub,Path(tmp)/sub)
  for path in [Path(tmp)/'improved-output/result.json']+sorted((Path(tmp)/'examples-output').glob('*/result.json')):
   result=json.loads(path.read_text())
   if result['status'] in ('OPTIMAL','FEASIBLE'):checker.verify(path,True,False)
 assert 'highspy' not in sys.modules and 'numpy' not in sys.modules
 print(json.dumps(dict(status='PASS',certificate_records=counts,proof_records=len(proof_files),historical_mappings=108,mapping_word_calls=words,forged_unsat='rejected',solver_imported=False,platform_scope=f"clang {' '.join(checker.shared_library_settings()[1])}, {sys.platform}"),indent=2))
if __name__=='__main__':main()
