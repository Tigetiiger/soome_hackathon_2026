import copy
B=dict(base=[12000,12500,13000,13500,14000,14600], pl=[0,0,1500,1800,2100,2400],
 adopt=[0.03,0.10,0.18,0.24,0.28,0.30], price=15, prem_share=0.08, prem_price=49,
 cts=3.5, onb=60, churn=0.08, hw=1900, fixed=[380,200,230,180,180,180], prem_ret=0.0,
 renew_uplift=60, wacc=0.10)
def run(p, years=6):
    rows=[];act=0
    for y in range(years):
        elig=p['base'][y]+p['pl'][y]
        target=elig*p['adopt'][y]
        prev=act*(1-p['churn']); new=max(0,target-prev); act=prev+new
        avg=(prev+act)/2 if y else act/2
        prem=avg*p['prem_share']; std=avg-prem
        rev=(std*p['price']+prem*p['prem_price'])*12
        ret=avg*p['renew_uplift']
        cogs=avg*p['cts']*12
        onb=new*p['onb']
        hwcap=new*p['prem_share']*p['hw']
        fixed=p['fixed'][y]*1000
        ebitda=rev+ret-cogs-onb-fixed
        cf=ebitda-hwcap
        rows.append(dict(y=y+1,elig=elig,act=round(act),rev=rev,cogs=cogs,onb=onb,fixed=fixed,ebitda=ebitda,hw=hwcap,cf=cf))
    npv=sum(r['cf']/(1+p['wacc'])**(r['y']) for r in rows)
    cum=0;pb=None
    for r in rows:
        cum+=r['cf']
        if pb is None and cum>0: pb=r['y']
    return rows,npv,pb
def sc(**kw):
    p=copy.deepcopy(B);p.update(kw);return p
low=sc(adopt=[0.02,0.05,0.09,0.12,0.14,0.15],price=12,churn=0.12,cts=4.5,pl=[0,0,0,1000,1500,2000],renew_uplift=25)
high=sc(adopt=[0.05,0.15,0.28,0.35,0.40,0.42],price=19,churn=0.05,cts=3.0,renew_uplift=110)
for n,p in [('low',low),('base',B),('high',high)]:
    rows,npv,pb=run(p)
    print(n,'NPV6y kEUR',round(npv/1e3),'payback yr',pb)
    for r in rows[:3]: print('  ',{k:(round(v/1e3) if k in('rev','cogs','onb','fixed','ebitda','hw','cf') else v) for k,v in r.items()})
    print('   6y cum cf k', round(sum(r['cf'] for r in rows)/1e3))
_,b,_=run(B)
print('tornado base',round(b/1e3))
for name,lo,hi in [('price',sc(price=10),sc(price=20)),
 ('adoption',sc(adopt=[x*0.5 for x in B['adopt']]),sc(adopt=[x*1.5 for x in B['adopt']])),
 ('churn',sc(churn=0.15),sc(churn=0.04)),
 ('cost_to_serve',sc(cts=6),sc(cts=2)),
 ('fixed_dev',sc(fixed=[x*1.5 for x in B['fixed']]),sc(fixed=[x*0.75 for x in B['fixed']])),
 ('renewal_uplift',sc(renew_uplift=0),sc(renew_uplift=120)),
 ('wacc',sc(wacc=0.14),sc(wacc=0.07)),
 ('poland',sc(pl=[0]*6),sc(pl=[0,0,2500,3000,3500,4000]))]:
    print(name, round(run(lo)[1]/1e3), round(run(hi)[1]/1e3))
# break-even adoption multiplier
for m in [0.3,0.4,0.5,0.6,0.7]:
    print('adopt x',m, round(run(sc(adopt=[x*m for x in B['adopt']]))[1]/1e3))
# unit economics std device
print('std unit margin/mo',15-3.5,'onb payback months',60/(15-3.5))
print('prem unit: margin/mo',49-3.5,'capex',1900+60,'payback mo',(1960)/(45.5))

print('sub-only base',round(run(sc(renew_uplift=0))[1]/1e3))
for m in [0.4,0.5,0.6,0.7,0.8]: print('adopt',m,round(run(sc(adopt=[x*m for x in B['adopt']]))[1]/1e3))
print('fixed total',sum(B['fixed']))
