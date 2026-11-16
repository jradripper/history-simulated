# Mongoose island simulations

> Also in this repo: [`pearl-harbor-radar/`](pearl-harbor-radar/), the simulation from *What If Someone Had Believed the Radar at Pearl Harbor?*

Code for the two toy models in the video *The Island That Said No* (the Hawaiian island with no breeding mongooses).

These are simple models with assumed inputs. They show how the system behaves. They are not a forecast, and they are not fitted to field data. Mongooses are not established on Kauaʻi.

## What is here

| File | What it does |
|---|---|
| `part1_1883_release.py` | Rats, ground-nesting birds and mongooses on one island region after the 1883 release of 72 mongooses. Tests what happens when mongooses hunt by day and rats are active at night. |
| `part2_kauai_founding.py` | How few mongooses it takes to start a breeding population on Kauaʻi, and how much trapping stops it. Each run rolls dice month by month. |
| `part1_results.json`, `part2_results.json` | The output of each script, as used for the numbers in the video. |

## Run it

You need Python 3 and NumPy.

```
pip install numpy
python3 part1_1883_release.py
python3 part2_kauai_founding.py
```

Part 1 takes a few seconds. Part 2 takes about half a minute. Both print their results as JSON. The random seeds are fixed, so you get the same numbers each time.

## Reading the results

**Part 1.** Each scenario reports rats and birds as a percentage of where they started, and mongooses per square kilometre, after 140 years. `overlap` is the share of time mongooses and rats are active together: 0.15 for the real day hunter, 0.9 for an imagined night hunter. The `robustness_real` block reruns the real scenario 500 times with every input changed by up to 50% either way.

**Part 2.** Each entry is a pair: the percentage of runs where the population reached 200 animals ("established"), and the median number of years that took. Trapping levels are the share of animals caught per year. The robustness block varies the birth and death inputs by up to 50% either way.

## Assumptions to know about

- Every input marked `assumed` in the code is a plausible guess, not a measurement.
- Part 1 treats other food (insects, fruit, frogs) as constant and unlimited by mongoose numbers.
- Part 2 ignores where animals are on the island. Two animals can always find each other, which makes establishment easier in the model than in real life.
- "Established" means 200 animals. A different cut-off shifts the percentages.

Trust the pattern, not the exact number.
