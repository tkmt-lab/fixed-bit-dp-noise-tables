"""Bounded LP branch proof producer. Floating solver output is checked exactly."""
import time,math
from fractions import Fraction as F
import highspy
import numpy as np
import certcheck


def produce(spec,table=None,max_nodes=127,seconds=3):
 # Canonical rows belong to the trusted checker; every produced leaf is rechecked.
 c,base,scale=certcheck.model(spec); start=time.monotonic();count=0;better=None
 target=None if table is None else sum(a*b for a,b in zip(c,sum(table,[])))
 def lp(rows,farkas=False):
  h=highspy.Highs()
  for k,v in {'output_flag':False,'threads':1,'parallel':'off','time_limit':max(.01,seconds-(time.monotonic()-start))}.items():h.setOptionValue(k,v)
  if not farkas:
   for cost in c:h.addVar(0,highspy.kHighsInf);h.changeColCost(h.getNumCol()-1,cost)
   for a,b in rows:
    h.addRow(float(b),highspy.kHighsInf,len(a),np.array(list(a),dtype=np.int32),np.array(list(a.values()),dtype=float))
  else:
   for a,b in rows:h.addVar(0,highspy.kHighsInf);h.changeColCost(h.getNumCol()-1,-float(b))
   for j in range(len(c)):
    terms={i:a[j] for i,(a,b) in enumerate(rows) if j in a}
    h.addRow(-highspy.kHighsInf,0,len(terms),np.array(list(terms),dtype=np.int32),np.array(list(terms.values()),dtype=float))
   h.addRow(-highspy.kHighsInf,1,len(rows),np.arange(len(rows),dtype=np.int32),np.ones(len(rows)))
  h.run();return h
 def sparse(v):return {str(i):str(F(x).limit_denominator(10**7)) for i,x in enumerate(v) if abs(x)>1e-10}
 def leaf_ok(node,rows):
  # Reuse exact leaf equations with the current node's extra branch inequalities.
  dual={int(i):F(v) for i,v in node['dual'].items()};lhs=[F(0)]*len(c);bound=F(0)
  for i,v in dual.items():
   if v<0:return False
   a,b=rows[i];bound+=b*v
   for j,x in a.items():lhs[j]+=x*v
  if node['kind']=='infeasible':return bound>0 and all(x<=0 for x in lhs)
  return target is not None and all(x<=y for x,y in zip(lhs,c)) and -(-bound.numerator//bound.denominator)>=target
 def visit(rows):
  nonlocal count,better
  if count>=max_nodes or time.monotonic()-start>=seconds:raise RuntimeError('node/time limit')
  count+=1;h=lp(rows)
  if h.getModelStatus()==highspy.HighsModelStatus.kInfeasible:
   aux=lp(rows,True);sol=aux.getSolution();node={'kind':'infeasible','dual':sparse(sol.col_value)}
   if not sol.value_valid or not leaf_ok(node,rows):raise RuntimeError('no exact Farkas certificate')
   return node
  sol=h.getSolution()
  if not sol.value_valid or not sol.dual_valid:raise RuntimeError('LP unknown')
  node={'kind':'bound','dual':sparse(sol.row_dual)}
  if leaf_ok(node,rows):return node
  candidates=[(abs(x-round(x)),i,x) for i,x in enumerate(sol.col_value) if abs(x-round(x))>1e-7]
  if not candidates:
   v=[round(x) for x in sol.col_value];valid=all(sum(a.get(j,0)*v[j] for j in a)>=b for a,b in rows);cost=sum(a*b for a,b in zip(c,v))
   if valid and target is not None and cost<target:better=[v[i:i+len(spec['Y'])] for i in range(0,len(v),len(spec['Y']))]
   raise RuntimeError(f'unclosed integral point or dual reconstruction; exact_candidate_valid={valid}; cost={cost}; incumbent={target}')
  _,i,x=max(candidates);t=math.floor(x)
  return {'kind':'branch','variable':i,'split':t,'left':visit(rows+[({i:-1},F(-t))]),'right':visit(rows+[({i:1},F(t+1))])}
 try:
  if max(map(abs,c),default=0)>2**50:raise RuntimeError('integer objective scale too large')
  cert={'version':1,'tree':visit(base)};checked=certcheck.verify(spec,cert,table)
  return cert,{'complete':True,**checked,'seconds':time.monotonic()-start,'visited':count}
 except (RuntimeError,AssertionError,OverflowError,ValueError) as e:
  return None,{'complete':False,'reason':str(e),'seconds':time.monotonic()-start,'visited':count,'node_limit':max_nodes,'time_limit':seconds,'better_candidate':better}
