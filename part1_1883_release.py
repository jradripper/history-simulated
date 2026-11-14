"""Toy three-species model: rats, ground-nesting birds, mongooses on one island region.
Illustrative only: parameters are plausible assumptions, not fitted to field data.
Densities are animals (or active nests) per square km. Time in years."""
import numpy as np, json

BASE = dict(
    rR=3.0,   KR=5000.0,   # rats: fast breeders, high ceiling (assumed 50 per hectare)
    rB=0.25,  KB=50.0,     # ground-nesting birds: slow breeders
    a=0.05,                # mongoose search rate
    h=1/1500,              # handling time: caps intake near 1,500 food items a year
    aB=1.0,                # nests sit on the ground day and night: fully available
    F=200000.0,            # other food (insects, fruit, frogs), held constant
    eR=0.00115, eB=0.00115, eF=0.00115,  # mongoose births per item eaten
    m=0.5,                 # mongoose death rate per year
    d=1/300,               # crowding limit: settles near 300 per km^2 on other food alone
    M0=0.072,              # 72 animals spread over ~1000 km^2
)

def run(overlap, years=140, mongoose=True, p=BASE, dt=0.01):
    R, B = p['KR'], p['KB']
    M = p['M0'] if mongoose else 0.0
    n = int(years/dt); out = np.zeros((n//100+1, 4)); k = 0
    for i in range(n+1):
        if i % 100 == 0:
            out[k] = (i*dt, R, B, M); k += 1
        avail = overlap*R + p['aB']*B + p['F']
        D = 1 + p['a']*p['h']*avail
        killR = p['a']*overlap*R/D
        killB = p['a']*p['aB']*B/D
        eatF  = p['a']*p['F']/D
        dR = p['rR']*R*(1-R/p['KR']) - killR*M
        dB = p['rB']*B*(1-B/p['KB']) - killB*M
        dM = M*(p['eR']*killR + p['eB']*killB + p['eF']*eatF - p['m'] - p['d']*M)
        R = max(R+dR*dt, 0.0); B = max(B+dB*dt, 0.0); M = max(M+dM*dt, 0.0)
    return out[:k]

if __name__ == '__main__':
    res = {}
    for name, ov, mg in [('kauai_no_mongoose',0,False),('real_day_hunter',0.15,True),('whatif_night_hunter',0.9,True)]:
        o = run(ov, mongoose=mg)
        res[name] = dict(rats_end=round(o[-1,1]), birds_end=round(o[-1,2],2), mongoose_end=round(o[-1,3]),
                         rats_pct_of_start=round(100*o[-1,1]/BASE['KR'],1), birds_pct_of_start=round(100*o[-1,2]/BASE['KB'],1))
        # year birds fall below 10% and mongoose passes 50% of final
        b = o[:,2]/BASE['KB']; idx = np.argmax(b<0.1) if (b<0.1).any() else -1
        res[name]['year_birds_below_10pct'] = float(o[idx,0]) if idx>=0 else None
    # sweep overlap
    sweep = []
    for ov in np.linspace(0,1,11):
        o = run(float(ov)); sweep.append((round(float(ov),1), round(100*o[-1,1]/BASE['KR'],1), round(100*o[-1,2]/BASE['KB'],1), round(o[-1,3])))
    res['sweep_overlap_rats%_birds%_mongoose'] = sweep
    # robustness: vary every parameter +-50%, 500 draws, real scenario
    rng = np.random.default_rng(7); rats=[]; birds=[]
    for _ in range(500):
        p = {k:(v*rng.uniform(0.5,1.5) if k!='M0' else v) for k,v in BASE.items()}
        o = run(0.15, p=p, dt=0.02)
        rats.append(100*o[-1,1]/p['KR']); birds.append(100*o[-1,2]/p['KB'])
    rats=np.array(rats); birds=np.array(birds)
    res['robustness_real'] = dict(rats_pct_median=round(float(np.median(rats)),1), rats_pct_p10=round(float(np.percentile(rats,10)),1), rats_pct_p90=round(float(np.percentile(rats,90)),1),
        rats_eliminated_share=round(float((rats<1).mean()),3), birds_below_10pct_share=round(float((birds<10).mean()),3), birds_pct_median=round(float(np.median(birds)),1))
    print(json.dumps(res, indent=1))
