"""
Pearl Harbor, 7 December 1941: what if someone had believed the radar?

The game: the first bomb falls at minute 0. We give Oahu a head start of W
minutes (the one dial) and replay the first 15 minutes of the attack 2,000
times per setting. We count four things:
  1. battleships closed up (watertight doors shut) when the first torpedo comes
  2. Army fighters already in the air
  3. torpedo hits on the ships
  4. Japanese first-wave planes shot down

Run:  python3 pearl_harbor_radar_warning.py
Plain Python + numpy. Seed fixed so results repeat.
This is a toy model of a real tragedy. It is not a forecast and it does not
count lives.
"""
import numpy as np

# ----------------------------------------------------------------------------
# PARAMETERS
# ----------------------------------------------------------------------------
# SOURCED - US Navy fact sheet (NHHC): first wave
TORPEDO_PLANES = 40
OTHER_PLANES = 143            # 49 level bombers + 51 dive bombers + 43 fighters
# SOURCED - 7 December 1941: The Air Force Story (Arakaki & Kuborn), Appendix B
FIGHTERS_READY_TO_FLY = 94    # in commission: 64 P-40, 20 P-36, 10 P-26 (of 152 on hand)
# SOURCED - same book, ch. IV: 14 pilots fought, 11 kills claimed, 4 lost
# SOURCED - Star-Advertiser / NHHC: Japan lost 9 planes in wave one, 20 in wave two
# SOURCED - R. B. Frank, National WWII Museum: battleship general quarters takes
#           8-10 minutes at sea; he doubles it for a Sunday in port
SHIP_CLOSE_UP_MIN = (12, 24)  # minutes for one battleship to close up (Frank's 16-20, widened)
# SOURCED - torpedo attack lasted 11-15 minutes, most drops in the first 10
TORPEDO_ATTACK_MIN = 11
# SOURCED - USNI Naval History Dec 2026: torpedoes aimed 12 Oklahoma, 9 West Virginia,
#           3 California, 1 Nevada; the rest at ships on the far side of Ford Island
AIM_SHARE = {"Oklahoma": 12, "West Virginia": 9, "California": 3, "Nevada": 1, "other ships": 15}
TORPEDO_EXPOSED = ["Oklahoma", "West Virginia", "California", "Nevada"]

# ASSUMED
A1_ALARM_RELAY_MIN = (3, 10)      # A1: minutes for a believed warning to reach ships and airfields
A2_FIGHTER_MEDIAN_MIN = 40        # A2: typical minutes to get one parked, unarmed fighter airborne
A2_FIGHTER_SPREAD = 0.5           #     (real record: first two took off 35 min after the first bomb)
A3_GUNS_MANNED_MIN = (4, 8)       # A3: minutes from alarm to ship guns firing
A4_AIM_SPOILED = 0.6              # A4: a torpedo run under full gunfire hits 0.6 times as often
A5_FIGHTERS_FIND_ENEMY = 0.5      # A5: half the airborne fighters reach the fight (no radio control)
A6_KILLS_PER_FIGHTER = 0.5        # A6: kills per fighter in the fight (record: 11 claims by 14 pilots)
A7_SINK_HITS_OPEN = 2             # A7: torpedo hits that sink a battleship with doors open
A7_SINK_HITS_CLOSED = 5           #     and with doors shut (California sank with 2, doors open)

# TUNED so that zero warning matches the real morning
T1_HIT_CHANCE = 0.72              # torpedo hit chance with nobody shooting -> about 19-21 hits
T2_TORPEDO_PLANE_LOSS = 0.17      # loss chance per torpedo plane under full gunfire -> 5 lost
T3_OTHER_PLANE_LOSS = 0.035       # loss chance per other plane under full gunfire -> 4 lost

N_GAMES = 2000
SEED = 19411207
DIAL = (0, 10, 20, 35, 53)        # 35 = alarm at the 7:20 phone call; 53 = alarm at first blip, 7:02


def play(warning, rng, p=None, guns_help=True, doors_help=True, fighters_help=True):
    """One replay. Returns (ships closed up, fighters airborne, hits, sunk, japanese lost)."""
    p = p or {}
    g = lambda k, d: p.get(k, d)
    surprise = warning <= 0
    relay = 0.0 if surprise else rng.uniform(*g("relay", A1_ALARM_RELAY_MIN))
    head_start = max(warning - relay, 0.0)          # useful minutes before the first bomb

    # 1. ships closing up
    close_t = rng.uniform(*g("close", SHIP_CLOSE_UP_MIN), len(TORPEDO_EXPOSED))
    closed = (close_t <= head_start) & doors_help
    # 2. fighters airborne at minute 0
    med = g("f_med", A2_FIGHTER_MEDIAN_MIN)
    t_up = rng.lognormal(np.log(med), A2_FIGHTER_SPREAD, FIGHTERS_READY_TO_FLY)
    airborne = int((t_up <= head_start).sum()) if fighters_help else 0
    in_fight = rng.binomial(airborne, g("find", A5_FIGHTERS_FIND_ENEMY))
    fighter_kills = rng.poisson(in_fight * g("kpf", A6_KILLS_PER_FIGHTER))
    fighter_kills = min(fighter_kills, TORPEDO_PLANES + OTHER_PLANES)
    torp_killed_by_fighters = rng.binomial(fighter_kills, TORPEDO_PLANES / (TORPEDO_PLANES + OTHER_PLANES))

    # 3. torpedo runs, spread over the attack; guns come alive after the alarm
    n_runs = TORPEDO_PLANES - min(torp_killed_by_fighters, TORPEDO_PLANES)
    t_run = rng.uniform(0, TORPEDO_ATTACK_MIN, n_runs)
    man = rng.uniform(*g("man", A3_GUNS_MANNED_MIN))
    gun_start = head_start if guns_help else 0.0   # break test: guns wake only at the first bomb
    guns = np.clip((t_run + gun_start) / man, 0, 1)
    lost = rng.random(n_runs) < g("tl", T2_TORPEDO_PLANE_LOSS) * guns
    lost_before_drop = lost & (rng.random(n_runs) < 0.5)
    hit_chance = T1_HIT_CHANCE * (1 - (1 - g("spoil", A4_AIM_SPOILED)) * guns)
    hit = (~lost_before_drop) & (rng.random(n_runs) < hit_chance)
    names = list(AIM_SHARE)
    w = np.array(list(AIM_SHARE.values()), float)
    target = rng.choice(len(names), n_runs, p=w / w.sum())
    sunk = 0
    for i, ship in enumerate(TORPEDO_EXPOSED):
        h = int((hit & (target == i)).sum())
        need = g("sink_closed", A7_SINK_HITS_CLOSED) if closed[i] else A7_SINK_HITS_OPEN
        sunk += h >= need
    # 4. Japanese losses in the first 15 minutes
    mean_guns = float(np.clip((TORPEDO_ATTACK_MIN / 2 + gun_start) / man, 0, 1))
    other_lost = rng.binomial(OTHER_PLANES, g("ol", T3_OTHER_PLANE_LOSS) * mean_guns)
    jp_lost = int(lost.sum()) + other_lost + fighter_kills
    return int(closed.sum()), airborne, int(hit.sum()), sunk, jp_lost


def run(warning, rng, n=N_GAMES, **kw):
    return np.array([play(warning, rng, **kw) for _ in range(n)], float)


def main():
    rng = np.random.default_rng(SEED)
    print(f"{N_GAMES} replays per setting. Averages (middle 90% of games in brackets).\n")
    print("warning | ships closed up (of 4) | fighters up (of 94) | torpedo hits | battleships sunk by torpedo | Japanese planes lost")
    base = {}
    for wmin in DIAL:
        r = run(wmin, rng)
        base[wmin] = r
        lo, hi = np.percentile(r, 5, axis=0), np.percentile(r, 95, axis=0)
        m = r.mean(axis=0)
        print(f"{wmin:>4} min | {m[0]:.1f} [{lo[0]:.0f}-{hi[0]:.0f}] | {m[1]:.0f} [{lo[1]:.0f}-{hi[1]:.0f}] | "
              f"{m[2]:.0f} [{lo[2]:.0f}-{hi[2]:.0f}] | {m[3]:.1f} [{lo[3]:.0f}-{hi[3]:.0f}] | {m[4]:.0f} [{lo[4]:.0f}-{hi[4]:.0f}]")
    for wmin in (20, 35, 53):
        r = base[wmin]
        print(f"  {wmin} min: games with every exposed battleship closed up: {100*np.mean(r[:,0]==4):.0f}%;"
              f" games with 10+ fighters up: {100*np.mean(r[:,1]>=10):.0f}%;"
              f" games with fewer battleships sunk than the zero-warning average: {100*np.mean(r[:,3] < base[0][:,3].mean()):.0f}%")

    # ---- Stress test 1: every assumed input changed at random by up to half ----
    print("\nSTRESS TEST 1: every assumed input changed by up to half, 300 worlds, 200 replays each (35 min warning)")
    rows = []
    for _ in range(300):
        s = lambda: rng.uniform(0.5, 1.5)
        a, b, c = s(), s(), s()
        p = dict(relay=(3 * a, 10 * a), f_med=A2_FIGHTER_MEDIAN_MIN * s(), man=(4 * b, 8 * b),
                 spoil=min(1.0, A4_AIM_SPOILED * s()), find=min(1.0, 0.5 * s()), kpf=0.5 * s(),
                 close=(12 * c, 24 * c), sink_closed=max(3, int(round(5 * s()))))
        w0 = run(0, rng, 200, p=p).mean(axis=0)
        w35 = run(35, rng, 200, p=p).mean(axis=0)
        rows.append(np.concatenate([w0, w35]))
    rows = np.array(rows)
    q = lambda col: (np.percentile(rows[:, col], 5), np.percentile(rows[:, col], 95))
    print(f"  fighters up at 35 min: {q(6)[0]:.0f} to {q(6)[1]:.0f}")
    print(f"  torpedo hits at 35 min: {q(7)[0]:.0f} to {q(7)[1]:.0f}  (zero warning: {q(2)[0]:.0f} to {q(2)[1]:.0f})")
    print(f"  battleships sunk at 35 min: {q(8)[0]:.1f} to {q(8)[1]:.1f}  (zero warning: {q(3)[0]:.1f} to {q(3)[1]:.1f})")
    print(f"  Japanese lost at 35 min: {q(9)[0]:.0f} to {q(9)[1]:.0f}  (zero warning: {q(4)[0]:.0f} to {q(4)[1]:.0f})")
    print(f"  worlds where 35 min sinks fewer battleships than zero: {100*np.mean(rows[:,8] < rows[:,3]):.0f}%")
    print(f"  worlds where 35 min still leaves 10+ torpedo hits: {100*np.mean(rows[:,7] >= 10):.0f}%")
    print(f"  worlds where 35 min still leaves at least one battleship sunk on average: {100*np.mean(rows[:,8] >= 1):.0f}%")

    # ---- Stress test 2: break it on purpose ----
    print("\nSTRESS TEST 2: break it on purpose (35 min warning)")
    for label, kw in (("everything on", {}), ("doors never shut", dict(doors_help=False)),
                      ("guns never fire early", dict(guns_help=False)), ("no fighters take off", dict(fighters_help=False))):
        m = run(35, rng, **kw).mean(axis=0)
        print(f"  {label:<22}: hits {m[2]:.0f}, sunk {m[3]:.1f}, Japanese lost {m[4]:.0f}")
    m = run(35, rng, p=dict(f_med=5)).mean(axis=0)
    print(f"  fighters on 5-minute alert : fighters up {m[1]:.0f}, hits {m[2]:.0f}, sunk {m[3]:.1f}, Japanese lost {m[4]:.0f}")

    # ---- Real-record check ----
    m0 = base[0].mean(axis=0)
    print("\nREAL-RECORD CHECK")
    print(f"  zero warning, model: {m0[2]:.0f} torpedo hits, {m0[3]:.1f} battleships sunk by torpedo, {m0[4]:.0f} Japanese planes lost")
    print("  real morning: 19-21 torpedo hits; Oklahoma, West Virginia, California sunk by torpedo; 9 first-wave planes lost")
    full = run(600, rng, fighters_help=False).mean(axis=0)
    print(f"  ship guns fully ready, no fighters, model: {full[4]:.0f} of 183 lost = {100*full[4]/183:.0f}%")
    print("  real second wave, which met alert guns: 20 of 167 lost = 12%  (model is cautious)")


if __name__ == "__main__":
    main()
