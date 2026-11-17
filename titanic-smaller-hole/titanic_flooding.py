"""
How small a hole sank Titanic, and what if it had been smaller?

A small flooding model of RMS Titanic, 11:40 pm 14 April 1912 onward.
The ship is a simple hull cut into 16 watertight rooms. Sea water comes in
through small openings low in the first six rooms. Each room fills until the
water inside is level with the sea outside. As the bow gets heavier it dips,
and once water inside a room is higher than the top of its wall, it spills
into the next room.

The one dial: the total size of the openings.
Second test: openings in the first four rooms only (a head-on hit).

This is a toy model. The published work it is checked against:
  Wilding, British Wreck Commissioner's Inquiry, 1912 (12 sq ft estimate)
  Hackett & Bedford, Trans. RINA, 1996/97
  Paik, Kim & Thomas, Ships and Offshore Structures, 2025,
      doi 10.1080/17445302.2025.2603417

Run:  python3 titanic_flooding.py
Plain Python + numpy. Seed fixed so results repeat.
"""
import numpy as np, sys

# ----------------------------------------------------------------------------
# PARAMETERS
# ----------------------------------------------------------------------------
RHO, G = 1.025, 9.81
# SOURCED (ship particulars, widely published)
L, B, DRAFT = 269.0, 28.2, 10.5          # metres
DISP_T = 52_310 * 1.016                  # 52,310 long tons -> tonnes
REAL_MIN = 160                           # 11:40 pm to 2:20 am
RESCUE_MIN = 270                         # first lifeboat reached by Carpathia 4:10 am
HOLE_DEPTH = 7.6                         # Wilding 1912: damage about 25 ft below the waterline
TOTAL_OPENING = 12 * 0.0929              # Wilding 1912: "somewhere about 12 square feet" in total
# ASSUMED A0: how that total is shared between the six rooms
# (peak, hold 1, hold 2, hold 3, boiler room 6, boiler room 5; boiler room 5 only a small leak)
A0_SHARE = [0.054, 0.135, 0.269, 0.287, 0.237, 0.018]
HOLES = [TOTAL_OPENING * f for f in A0_SHARE]
# Published figures used only for comparison
WILDING_T, WILDING_MIN = 16_000 * 1.016, 40     # 16,000 long tons in the first 40 minutes
PAIK_AVG, PAIK_MIN_RATE = 243, 138               # tons per minute, first hour
PUMPS = 11.4                                     # tons per minute, all pumps (Paik et al.)

# ASSUMED
A1_ROOMS = [12, 14, 15.5, 15.5, 16, 17.5, 17.5, 17.5, 17.5, 12, 21, 16.5, 17, 14, 14, 13.5]  # room lengths, m, bow to stern
A2_WALL = [16.6, 16.6] + [13.9] * 9 + [16.6] * 5   # top of each room's aft wall above the keel, m (E deck / D deck)
A3_PERM = [0.9, 0.65, 0.65, 0.65] + [0.8] * 6 + [0.8] * 6  # share of each room that can hold water
A4_CD = 0.6            # how freely water passes a jagged opening
A5_HULLTOP = 22.0      # hull sides count as buoyant up to here, m above keel
A6_ENDS = 0.30         # bow and stern each taper over 30% of the length
A7_LOST_DEG = 10.0     # the ship is counted as lost at this bow-down angle (or when it can no longer float)
# TUNED: width of the paths water uses to spill over a wall along the decks, m.
SPILL_W = 1.0          # replaced by tune() so the real hole gives 160 minutes
SEED = 20261117
DT = 5.0

x = np.arange(0.5, L, 1.0)              # 1 m stations, bow = 0
def breadth(ends):
    le = ends * L
    s = np.ones_like(x)
    f = x < le; s[f] = 1 - (1 - x[f] / le) ** 2
    a = x > L - le; s[a] = 1 - (1 - (L - x[a]) / le) ** 2
    return B * s

def make(p):
    b = breadth(p["ends"])
    cs = DISP_T / RHO / (b.sum() * DRAFT)          # section fullness so she floats at her real draft
    edges = np.concatenate([[0], np.cumsum(p["rooms"])]); edges[-1] = L
    idx = np.clip(np.searchsorted(edges, x, side="right") - 1, 0, 15)
    area = np.array([b[idx == i].sum() for i in range(16)]) * cs * np.array(p["perm"])  # floor area that holds water
    xc = np.array([x[idx == i].mean() for i in range(16)])
    lcg = (b * x).sum() / b.sum()
    return dict(b=b * cs, area=area, xc=xc, lcg=lcg)

def float_at(m, w, mom, top, guess):
    """Find sinkage and tilt where buoyancy balances weight. Returns (Tmid, slope) or None."""
    Tm, s = guess
    xm = L / 2
    for _ in range(40):
        T = Tm + s * (xm - x)
        Tc = np.clip(T, 0, top)
        live = ((T > 0) & (T < top)) * m["b"]
        F = RHO * (m["b"] * Tc).sum() - w
        M = RHO * (m["b"] * Tc * x).sum() - mom
        J = RHO * np.array([[live.sum(), (live * (xm - x)).sum()],
                            [(live * x).sum(), (live * x * (xm - x)).sum()]])
        if abs(np.linalg.det(J)) < 1e-6: return None
        d = np.linalg.solve(J, [F, M])
        Tm -= d[0]; s -= d[1]
        if abs(d[0]) < 1e-5 and abs(d[1]) < 1e-8: return Tm, s
        if not (-5 < Tm < 60 and abs(s) < 1): return None
    return None

def run(scale=1.0, holes=None, spill=None, hours=12, trace=False, **kw):
    p = dict(rooms=A1_ROOMS, wall=A2_WALL, perm=A3_PERM, cd=A4_CD, top=A5_HULLTOP,
             ends=A6_ENDS, lost=A7_LOST_DEG); p.update(kw)
    spill = SPILL_W if spill is None else spill
    m = make(p)
    a = np.zeros(16); h = HOLES if holes is None else holes
    a[:len(h)] = np.array(h) * scale
    zh = DRAFT - HOLE_DEPTH                       # opening height above keel
    V = np.zeros(16); wall = np.array(p["wall"])
    st = (DRAFT, 0.0); log = []
    n = int(hours * 3600 / DT)
    for k in range(n):
        w = DISP_T + RHO * V.sum()
        mom = DISP_T * m["lcg"] + RHO * (V * m["xc"]).sum()
        st = float_at(m, w, mom, p["top"], st)
        t = k * DT / 60
        if st is None: return (t, log) if trace else t
        Tm, s = st
        if np.degrees(np.arctan(s)) > p["lost"]: return (t, log) if trace else t
        z = V / m["area"]
        out = Tm + s * (L / 2 - m["xc"])          # sea level outside each room, above keel
        head = out - np.maximum(z, zh)
        q = p["cd"] * a * np.sign(head) * np.sqrt(2 * G * np.abs(head))
        q[(out < zh) & (z < zh)] = 0
        dV = q * DT
        for i in range(15):                       # spilling over the wall between room i and i+1
            hi, lo = (i, i + 1) if z[i] >= z[i + 1] else (i + 1, i)
            over = z[hi] - max(wall[i], z[lo])
            if over > 0:
                flow = min(1.7 * spill * over ** 1.5 * DT, 0.25 * over * m["area"][hi])
                dV[hi] -= flow; dV[lo] += flow
        V = np.maximum(V + dV, 0)
        if trace and k % int(60 / DT) == 0: log.append((t, RHO * V.sum(), np.degrees(np.arctan(s)), RHO * q.sum() * 60))
    return (None, log) if trace else None        # still afloat at the end

def tune(n=22, **kw):
    lo, hi = 0.001, 50.0
    for _ in range(n):
        mid = (lo * hi) ** 0.5
        t = run(spill=mid, hours=6, **kw)
        if t is None or t > REAL_MIN: lo = mid
        else: hi = mid
    return (lo * hi) ** 0.5

def fmt(t): return "still afloat after 12 hours" if t is None else f"{int(t // 60)} h {int(t % 60):02d} min"

def main():
    global SPILL_W
    SPILL_W = tune()
    print(f"TUNED spill width: {SPILL_W:.2f} m (set so the real openings give {REAL_MIN} minutes)")
    print(f"Total opening: {sum(HOLES):.3f} m2 = {sum(HOLES) * 10.764:.1f} sq ft\n")
    t0, log = run(trace=True)
    print("REAL NIGHT (tuned): lost after", fmt(t0))
    for t, tons, deg, rate in log:
        if int(t) in (1, 10, 20, 40, 60, 90, 120, 150): print(f"  {int(t):>3} min: {tons:>7,.0f} t aboard, bow down {deg:4.1f} deg, coming in {rate:5.0f} t/min")
    t40 = [r for r in log if int(r[0]) == 40][0][1]; t60 = [r for r in log if int(r[0]) == 60][0][1]
    rates60 = [r[3] for r in log if 1 <= r[0] <= 60]
    print(f"\nCHECK AGAINST PUBLISHED WORK")
    print(f"  water aboard after 40 min: this model {t40:,.0f} t | Wilding 1912 {WILDING_T:,.0f} t")
    print(f"  first-hour average inflow: this model {t60 / 60:.0f} t/min (lowest {min(rates60):.0f}) | Paik et al. 2025 {PAIK_AVG} t/min (lowest {PAIK_MIN_RATE})")
    print(f"  pumps: {PUMPS} t/min, about 1/{t60 / 60 / PUMPS:.0f} of the first-hour inflow in this model")

    print("\nTHE DIAL: size of the openings (share of the real size)")
    print(f"{'share':>6} {'sq ft':>6} {'m2':>6}  time afloat")
    res = {}
    for f in (2.0, 1.5, 1.0, 0.75, 0.6, 0.5, 0.4, 0.25, 0.1):
        res[f] = run(scale=f)
        print(f"{f:>6.2f} {sum(HOLES) * f * 10.764:>6.1f} {sum(HOLES) * f:>6.2f}  {fmt(res[f])}")
    lo, hi = 0.2, 1.0
    for _ in range(14):
        mid = (lo + hi) / 2
        t = run(scale=mid)
        if t is None or t >= RESCUE_MIN: lo = mid
        else: hi = mid
    print(f"\nLargest opening that still lasts {RESCUE_MIN} min (first lifeboat reached): {lo:.2f} of real = {sum(HOLES) * lo * 10.764:.1f} sq ft")

    print("\nWHICH ROOMS ARE OPEN (same opening per room as the real night)")
    for nrooms in (2, 3, 4, 5, 6):
        print(f"  first {nrooms} rooms open: {fmt(run(holes=HOLES[:nrooms]))}")
    print("  HEAD-ON TEST: first 4 rooms wide open (20 sq ft each):", fmt(run(holes=[1.86] * 4)))
    print("  first 5 rooms wide open:", fmt(run(holes=[1.86] * 5)))

    if "--fast" in sys.argv: return
    rng = np.random.default_rng(SEED)
    N, ok, ratio, half_rescue, four = 60, 0, [], [], []
    for _ in range(N):
        f = rng.uniform(0.5, 1.5, 6)
        kw = dict(cd=A4_CD * f[0], perm=list(np.clip(np.array(A3_PERM) * f[1], 0.3, 0.98)),
                  wall=list(np.array(A2_WALL) + (f[2] - 1) * 4), top=A5_HULLTOP + (f[3] - 1) * 6,
                  ends=A6_ENDS * f[4], lost=A7_LOST_DEG * f[5])
        sp = tune(n=11, **kw)
        tb = run(spill=sp, hours=6, **kw)
        if tb is None or abs(tb - REAL_MIN) > 8: continue      # this world cannot match the real night at all
        ok += 1
        th = run(scale=0.5, spill=sp, hours=12, **kw); th = 720 if th is None else th
        ratio.append(th / tb); half_rescue.append(th >= 260)
        four.append(run(holes=[1.86] * 4, spill=sp, hours=8, **kw) is None)
    ratio = np.array(ratio)
    print(f"\nSTRESS TEST 1: every guess changed by up to half, then re-tuned to the real {REAL_MIN} minutes ({N} worlds)")
    print(f"  worlds that can match the real night: {ok} of {N}")
    print(f"  half-size openings last {np.percentile(ratio, 5):.1f} to {np.percentile(ratio, 95):.1f} times as long (middle 90%), median {np.median(ratio):.1f}, lowest {ratio.min():.1f}")
    print(f"  worlds where half-size openings last longer: {100 * np.mean(ratio > 1.05):.0f}%")
    print(f"  worlds where half-size openings last to 4:00 am (260 min): {100 * np.mean(half_rescue):.0f}%")
    print(f"  worlds where the ship floats with the first 4 rooms wide open: {100 * np.mean(four):.0f}%")
    print("\nSTRESS TEST 2: break it on purpose")
    print("  walls with no top (nothing can spill):", fmt(run(wall=[99] * 16)))
    print("  no walls at all (every wall 3 m high):", fmt(run(wall=[3] * 16)))
    print("  walls one deck higher (+2.7 m):", fmt(run(wall=list(np.array(A2_WALL) + 2.7))))

if __name__ == "__main__":
    main()
