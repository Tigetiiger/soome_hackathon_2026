V=1064.0
print("Sensitivity: value multiple = V*r/(12p)")
for p in [5,10,15,25,40]:
    print(p,[round(V*r/(12*p),1) for r in (0.25,0.5,0.75)])
# mix
mix={'ins':(0.70,12),'int':(0.27,25),'prem':(0.03,25+39)}  # prem = integrated + platform lease
arpu=sum(s*p for s,p in mix.values()); print('blended ARPU/mo',arpu)
cogs_dev_mo=1.0+0.2+1.5   # cloud+LLM+support
prem_hw_cost_mo=(1450/72)+3  # BOM mid / 72m + install amortised? install 4h*2*60=480 ->6.7/mo
prem_install_mo=480/72
onb=50+0.3*175
fixed={1:350e3,2:450e3,3:500e3}
sc={'low':[250,700,1500],'base':[400,1500,3000],'high':[700,2800,6000]}
for k,ends in sc.items():
    start=0;cum=0;out=[]
    for y,e in enumerate(ends,1):
        avg=(start+e)/2; new=e-start
        rev=avg*arpu*12
        cogs=avg*12*(cogs_dev_mo+mix['prem'][0]*(prem_hw_cost_mo+prem_install_mo))+new*onb
        gm=rev-cogs; ebit=gm-fixed[y]; cum+=ebit
        arr=e*arpu*12
        out.append((y,e,round(arr/1e3),round(rev/1e3),round(100*gm/rev),round(ebit/1e3),round(cum/1e3)))
        start=e
    print(k,out)
# breakeven devices on fixed Y3
contrib=arpu-cogs_dev_mo-mix['prem'][0]*(prem_hw_cost_mo+prem_install_mo)
print('contrib/dev/mo',contrib,'breakeven devices Y3',fixed[3]/(contrib*12),'Y1',fixed[1]/(contrib*12))
