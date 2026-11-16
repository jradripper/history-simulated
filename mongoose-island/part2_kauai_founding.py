"""Founding-stage model for Kauai: can a handful of arrivals start a breeding population,
and how hard must trapping work to stop it? Stochastic, individual-count, monthly steps.
Illustrative assumptions throughout; not fitted to field data."""
import numpy as np, json
rng = np.random.default_rng(11)
RECRUITS = 3.0     # surviving young per female per year (both sexes), assumed
DEATH = 0.5        # natural death hazard per year, assumed
ESTABLISHED = 200  # population size we call "established"

def trial(founders=0, pregnant_female=False, arrivals_per_year=0.0, trap=0.0, years=30, p=None):
    """Monthly steps so that young animals face death and trapping from birth."""
    rec = RECRUITS if p is None else p[0]; death = DEATH if p is None else p[1]
    f = rng.binomial(founders, 0.5); m = founders - f
    if pregnant_female:                      # she arrives carrying one litter
        k = rng.poisson(rec/2); kf = rng.binomial(k, 0.5); f += 1 + kf; m += k - kf
    surv = np.exp(-(death + trap)/12)
    for t in range(years*12):
        births = rng.poisson(rec/12 * f) if (f > 0 and m > 0) else 0
        f = rng.binomial(f, surv); m = rng.binomial(m, surv)
        nf = rng.binomial(births, 0.5); f += nf; m += births - nf
        if arrivals_per_year > 0:
            a = rng.poisson(arrivals_per_year/12); af = rng.binomial(a, 0.5); f += af; m += a - af
        if f + m >= ESTABLISHED: return (t + 1)/12
        if f + m == 0 and arrivals_per_year == 0: return 0
    return 0

def prob(n=1500, **kw):
    r = np.array([trial(**kw) for _ in range(n)])
    est = r > 0
    return round(100*est.mean(), 1), (round(float(np.median(r[est])), 1) if est.any() else None)

if __name__ == '__main__':
    out = {}
    traps = {'no trapping': 0.0, 'catch 39%/yr': 0.5, 'catch 63%/yr': 1.0, 'catch 86%/yr': 2.0}
    for label, kw in [('1 stowaway, not pregnant', dict(founders=1)),
                      ('1 pregnant female', dict(pregnant_female=True)),
                      ('2 animals', dict(founders=2)), ('5 animals', dict(founders=5)),
                      ('10 animals', dict(founders=10)), ('72 animals', dict(founders=72))]:
        out[label] = {t: prob(trap=v, **kw) for t, v in traps.items()}
    out['steady trickle: 1 stowaway every 2.5 yrs, 50 years'] = {t: prob(arrivals_per_year=0.4, years=50, trap=v) for t, v in traps.items()}
    # robustness: vary recruits and death +-50%, 2 animals and trickle, no trapping and 63% trapping
    rob = {}
    for name, kw in [('2 animals, no trapping', dict(founders=2, trap=0.0)), ('2 animals, catch 63%/yr', dict(founders=2, trap=1.0)),
                     ('trickle, catch 63%/yr', dict(arrivals_per_year=0.4, years=50, trap=1.0))]:
        ps = []
        for _ in range(120):
            p = (RECRUITS*rng.uniform(.5, 1.5), DEATH*rng.uniform(.5, 1.5))
            ps.append(np.mean([trial(p=p, **kw) > 0 for _ in range(120)]) * 100)
        ps = np.array(ps); rob[name] = dict(median=round(float(np.median(ps)), 1), p10=round(float(np.percentile(ps, 10)), 1), p90=round(float(np.percentile(ps, 90)), 1))
    out['robustness (% established; recruits and death varied +-50%)'] = rob
    print(json.dumps(out, indent=1))
