"""Exact standalone proof checker. Standard library only."""
from fractions import Fraction as F
from math import lcm


def model(s):
 n,m=len(s['D']),len(s['Y']); size=n*m; S=2**s['b']
 def rat(v):return F(v['numerator'],v['denominator']) if isinstance(v,dict) else F(v)
 costs=[rat(v) for row in s['loss'] for v in row]; scale=lcm(*(v.denominator for v in costs)); c=[int(v*scale) for v in costs]
 rows=[]
 def add(a,b):rows.append((a,F(b)))
 for d in range(n):
  a={d*m+y:1 for y in range(m)};add(a,S);add({i:-v for i,v in a.items()},-S)
 r=rat(s['r'])
 for d,e in s['edges']:
  if d==e:continue
  for left,right in [(d,e),(e,d)]:
   for y in range(m):add({right*m+y:r.numerator,left*m+y:-r.denominator},0)
 q=s.get('output_constraints',{})
 for d,y in q.get('forbidden',[]):add({d*m+y:-1},0)
 for name,sign in [('min_counts',1),('max_counts',-1)]:
  for d,row in enumerate(q.get(name,[])):
   for y,v in enumerate(row):add({d*m+y:sign},sign*v)
 return c,rows,scale


def verify(spec,cert,table=None):
 c,rows,scale=model(spec)
 assert cert['version']==1
 target=None if table is None else sum(a*b for a,b in zip(c,sum(table,[])))
 def walk(node,rows):
  kind=node['kind']
  if kind=='branch':
   i,t=node['variable'],node['split'];assert type(i) is int and 0<=i<len(c) and type(t) is int
   return 1+walk(node['left'],rows+[({i:-1},F(-t))])+walk(node['right'],rows+[({i:1},F(t+1))])
  assert kind in ['bound','infeasible']
  lambdas={int(i):F(v) for i,v in node['dual'].items()}
  assert all(0<=i<len(rows) and v>=0 for i,v in lambdas.items())
  sums=[F(0)]*len(c);bound=F(0)
  for i,v in lambdas.items():
   a,b=rows[i];bound+=v*b
   for j,coef in a.items():sums[j]+=v*coef
  if kind=='infeasible':assert bound>0 and all(v<=0 for v in sums)
  else:
   assert target is not None and all(a<=b for a,b in zip(sums,c))
   assert -(-bound.numerator//bound.denominator)>=target
  return 1
 return {'nodes':walk(cert['tree'],rows),'integer_cost_scale':scale,'exact':'PASS'}
