import json,sys,re
D=json.load(open(sys.argv[1]))
# shorten numbers to 1 decimal
def sh(d): return re.sub(r'(\d+\.\d)\d+', r'\1', d)
D['sym']['comps'][0]['d']=sh(D['sym']['comps'][0]['d'])
for c in D['wm']['comps']: c['d']=sh(c['d']); c['bbox']=[round(float(v),1) for v in c['bbox']]
for h in D['holes']: h['d']=sh(h['d']); h['bbox']=[round(float(v),1) for v in h['bbox']]
D['sym']['comps'][0]['bbox']=[float(v) for v in D['sym']['comps'][0]['bbox']]
t=open('src/template.html').read().replace('__DATA__',json.dumps(D,separators=(',',':')))
open('soolow-motion.html','w').write(t); print(len(t))
