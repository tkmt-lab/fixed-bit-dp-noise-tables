"""Independent standard-form and certificate verifier from the public specification."""
from fractions import Fraction as F
import math

def rat(r):return F(r['numerator'],r['denominator']) if isinstance(r,dict) else F(r)
def build(spec):
 nd,ny=len(spec['D']),len(spec['Y']);N=nd*ny;S=1<<spec['b'];r=rat(spec['r']);rows=[]
 def add(co,b):rows.append((co,F(b)))
 for d in range(nd):
  add({d*ny+y:F(1) for y in range(ny)},S);add({d*ny+y:F(-1) for y in range(ny)},-S)
 for u,v in spec['edges']:
  for a,b in [(u,v),(v,u)]:
   for y in range(ny):add({b*ny+y:F(r.numerator),a*ny+y:F(-r.denominator)},0)
 cons=spec.get('output_constraints',{})
 for d,y in cons.get('forbidden',[]):add({d*ny+y:F(-1)},0)
 for key,sg in [('min_counts',1),('max_counts',-1)]:
  if key in cons:
   for d in range(nd):
    for y in range(ny):add({d*ny+y:F(sg)},sg*cons[key][d][y])
 losses=[F(x) for row in spec['loss'] for x in row];scale=math.lcm(*(x.denominator for x in losses));c=[int(x*scale) for x in losses]
 return rows,c,scale

def primal(spec,table):
 nd,ny=len(spec['D']),len(spec['Y']);assert len(table)==nd and all(len(row)==ny for row in table)
 x=[n for row in table for n in row];assert all(type(n)==int and n>=0 for n in x)
 rows,c,scale=build(spec)
 assert all(sum(a*x[j] for j,a in co.items())>=b for co,b in rows)
 cost=sum(a*n for a,n in zip(c,x));loss=F(cost,scale*nd*(1<<spec['b']))
 return cost,loss

def verify(obj):
 spec=obj['spec'];rows,c,scale=build(spec);status=obj['status'];N=len(c);leaves=[];branches=0
 if obj.get('table') is not None:
  target,loss=primal(spec,obj['table'])
  if 'loss' in obj:assert loss==F(obj['loss'])
 else:target=None;loss=None
 if status not in ('OPTIMAL','UNSAT'):return dict(status=status,cost=target,loss=str(loss),certificate='NOT CLAIMED')
 cert=obj['certificate'];assert set(cert)=={'version','tree'} and cert['version']==1
 def walk(node,path):
  nonlocal branches
  assert type(node)==dict
  if node['kind']=='branch':
   assert set(node)=={'kind','variable','split','left','right'}
   j,z=node['variable'],node['split'];assert type(j)==int and 0<=j<N and type(z)==int
   branches+=1
   walk(node['left'],path+[({j:F(-1)},F(-z))]);walk(node['right'],path+[({j:F(1)},F(z+1))]);return
  assert set(node)=={'kind','dual'} and node['kind'] in ('bound','infeasible')
  allrows=rows+path;coeff=[F(0)]*N;bound=F(0)
  for key,value in node['dual'].items():
   assert str(int(key))==key
   i=int(key);assert 0<=i<len(allrows)
   lam=F(value);assert lam>=0
   co,b=allrows[i];bound+=lam*b
   for j,a in co.items():coeff[j]+=lam*a
  if node['kind']=='infeasible':assert all(a<=0 for a in coeff) and bound>0
  else:
   assert status=='OPTIMAL' and target is not None
   assert all(a<=b for a,b in zip(coeff,c))
   ceil=-(-bound.numerator//bound.denominator)
   assert ceil>=target
  leaves.append(dict(kind=node['kind'],bound=str(bound),depth=len(path)))
 walk(cert['tree'],[])
 if status=='UNSAT':assert all(x['kind']=='infeasible' for x in leaves)
 return dict(status=status,cost=target,loss=str(loss),integer_cost_scale=scale,branches=branches,leaves=leaves,verdict='PASS')

