"""
What if America had stayed home one week earlier? (spring 2020)

A small spread model of the United States, January to 3 May 2020.
People move through four boxes: can catch it -> caught it, not yet
spreading -> spreading -> finished. On one date the country starts
staying home and the spread slows over a few weeks.

The one dial: how many days earlier that date is.

This is a toy model. The published study it is checked against is
Pei, Kandula and Shaman (Columbia University), Science Advances 2020,
doi 10.1126/sciadv.abd6370, which modelled 3,142 counties.

Run:  python3 covid_one_week_earlier.py
Plain Python + numpy. Seed fixed so results repeat.
"""
import numpy as np
from math import gamma as G

# ----------------------------------------------------------------------------
# PARAMETERS
# ----------------------------------------------------------------------------
POP = 330_000_000                 # SOURCED: US population, rounded
DAY0 = np.datetime64("2020-01-15")
REAL_START = np.datetime64("2020-03-15")   # SOURCED: Columbia study start of distancing
END = np.datetime64("2020-05-03")          # SOURCED: Columbia study end date

# SOURCED - Pei, Kandula, Shaman 2020
DEATH_DELAY_SHAPE, DEATH_DELAY_SCALE = 2.6, 8.6   # infection-to-death delay, mean 22.4 days
REAL_DEATHS = 65_455   # deaths to 3 May implied by the paper (32,335 averted = 49.4%)
COLUMBIA = {7: (32_335, 49.4), 14: (59_351, 90.8)}  # deaths averted, percent

# ASSUMED
A1_R_BEFORE = 2.8      # A1: each spreader infects 2.8 others before distancing
                       #     (Columbia's six metros on 15 March: 2.5 to 3.9)
A2_R_AFTER = 0.9       # A2: 0.9 others once distancing has settled in
                       #     (Columbia's six metros on 3 May: 0.27 to 1.32)
A3_RAMP_DAYS = 21      # A3: the slowdown takes three weeks to settle in
A4_LATENT = 3.5        # A4: days between catching it and spreading it
A5_INFECTIOUS = 3.5    # A5: days spent spreading it
A6_IFR = 0.007         # A6: 7 deaths per 1,000 infections

# TUNED: infections on 15 January, set by search so the real timeline gives REAL_DEATHS
SEED = 20261116
DT = 0.1
N_DAYS = int((END - DAY0).astype(int)) + 1


def delay_pdf(n):
    t = np.arange(n) + 0.5
    k, s = DEATH_DELAY_SHAPE, DEATH_DELAY_SCALE
    p = t ** (k - 1) * np.exp(-t / s) / (G(k) * s ** k)
    return p / p.sum()


def run(seed_inf, days_earlier=0, r0=A1_R_BEFORE, r1=A2_R_AFTER, ramp=A3_RAMP_DAYS,
        lat=A4_LATENT, inf=A5_INFECTIOUS, ifr=A6_IFR):
    """Return daily deaths (array) and total infections to END."""
    start = int((REAL_START - DAY0).astype(int)) - days_earlier
    S, E, I = POP - seed_inf, seed_inf / 2, seed_inf / 2
    new_inf = np.zeros(N_DAYS)
    steps = int(round(1 / DT))
    for d in range(N_DAYS):
        frac = min(max((d - start) / ramp, 0.0), 1.0)
        R = r0 + (r1 - r0) * frac
        beta = R / inf
        for _ in range(steps):
            ni = beta * S * I / POP * DT
            ne = E / lat * DT
            nr = I / inf * DT
            S -= ni; E += ni - ne; I += ne - nr
            new_inf[d] += ni
    deaths = np.convolve(new_inf, delay_pdf(N_DAYS))[:N_DAYS] * ifr
    return deaths, new_inf.sum()


def tune(**kw):
    """Find the starting infections that reproduce REAL_DEATHS on the real timeline."""
    lo, hi = 1e-6, 1e6
    for _ in range(60):
        mid = (lo * hi) ** 0.5
        if run(mid, 0, **kw)[0].sum() < REAL_DEATHS:
            lo = mid
        else:
            hi = mid
    return (lo * hi) ** 0.5


def main():
    rng = np.random.default_rng(SEED)
    seed = tune()
    print(f"TUNED starting infections on 15 Jan 2020: {seed:,.1f}")
    r = np.roots([A4_LATENT * A5_INFECTIOUS, A4_LATENT + A5_INFECTIOUS, 1 - A1_R_BEFORE]).max()
    print(f"Doubling time before distancing: {np.log(2) / r:.1f} days\n")

    base, base_inf = run(seed, 0)
    print("THE DIAL: how many days earlier does the country stay home?")
    print(f"{'days earlier':>12} {'start':>8} {'deaths to 3 May':>16} {'fewer':>9} {'% fewer':>8} {'peak/day':>9} {'infections':>12}")
    for k in (-7, 0, 3, 7, 10, 14, 21):
        d, ti = run(seed, k)
        date = str(REAL_START - np.timedelta64(k, "D"))[5:]
        print(f"{k:>12} {date:>8} {d.sum():>16,.0f} {base.sum() - d.sum():>9,.0f} "
              f"{100 * (1 - d.sum() / base.sum()):>7.1f}% {d.max():>9,.0f} {ti:>12,.0f}")

    pk = int(base.argmax())
    print(f"\nReal timeline: peak daily deaths {base.max():,.0f} on {DAY0 + np.timedelta64(pk, 'D')}")
    cum = np.cumsum(base)
    for date in ("2020-03-15", "2020-03-22", "2020-04-01", "2020-04-15", "2020-05-03"):
        i = int((np.datetime64(date) - DAY0).astype(int))
        print(f"  model deaths by {date}: {cum[i]:,.0f}")

    print("\nCOLUMBIA STUDY (published, 3,142 counties) vs THIS MODEL")
    for k in (7, 14):
        d, _ = run(seed, k)
        print(f"  {k:>2} days earlier: Columbia {COLUMBIA[k][0]:,} fewer deaths ({COLUMBIA[k][1]}%)"
              f" | this model {base.sum() - d.sum():,.0f} ({100 * (1 - d.sum() / base.sum()):.0f}%)")

    # ---- Stress test 1: every guess changed by up to half, 300 worlds --------
    out7, out14 = [], []
    for _ in range(300):
        f = rng.uniform(0.5, 1.5, 6)
        kw = dict(r0=max(A1_R_BEFORE * f[0], 1.3), r1=A2_R_AFTER * f[1],
                  ramp=max(A3_RAMP_DAYS * f[2], 1), lat=A4_LATENT * f[3],
                  inf=A5_INFECTIOUS * f[4], ifr=A6_IFR * f[5])
        s = tune(**kw)
        b = run(s, 0, **kw)[0].sum()
        out7.append(100 * (1 - run(s, 7, **kw)[0].sum() / b))
        out14.append(100 * (1 - run(s, 14, **kw)[0].sum() / b))
    out7, out14 = np.array(out7), np.array(out14)
    print("\nSTRESS TEST 1: every guess changed by up to half, re-tuned to the real total (300 worlds)")
    print(f"  1 week earlier: {np.percentile(out7, 5):.0f}% to {np.percentile(out7, 95):.0f}% fewer deaths"
          f" (middle 90%), lowest {out7.min():.0f}%, median {np.median(out7):.0f}%")
    print(f"  2 weeks earlier: {np.percentile(out14, 5):.0f}% to {np.percentile(out14, 95):.0f}% fewer deaths"
          f", lowest {out14.min():.0f}%, median {np.median(out14):.0f}%")
    print(f"  worlds where 1 week earlier saves at least a third: {100 * np.mean(out7 >= 33.3):.0f}%")
    print(f"  worlds where 2 weeks saves more than 1 week: {100 * np.mean(out14 > out7):.0f}%")

    # ---- Stress test 2: break it on purpose ----------------------------------
    print("\nSTRESS TEST 2: break it on purpose")
    kw = dict(r0=1.1)   # take away the fast doubling
    s = tune(**kw); b = run(s, 0, **kw)[0].sum()
    print(f"  slow spread before distancing (each spreader infects 1.1): 1 week earlier saves "
          f"{100 * (1 - run(s, 7, **kw)[0].sum() / b):.0f}%")
    kw = dict(r1=A1_R_BEFORE)  # distancing that does nothing
    s = tune(**kw); b = run(s, 0, **kw)[0].sum()
    print(f"  distancing that changes nothing: 1 week earlier saves "
          f"{100 * (1 - run(s, 7, **kw)[0].sum() / b):.0f}%")
    late = run(seed, -7)[0].sum()
    print(f"  flip it: one week LATER gives {late:,.0f} deaths, {late / base.sum():.1f} times the real total")


if __name__ == "__main__":
    main()
