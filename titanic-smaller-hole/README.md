# Titanic: what if the hole had been half the size?

Code for the simulation in the video *The Hole That Sank Titanic Was Smaller Than a Door. I Simulated Half.*

The iceberg did not tear a long gash in Titanic. It opened a row of thin gaps that add up to about 12 square feet, spread across six of her sixteen watertight rooms. She was built to float with the first four flooded. This model asks what one change does: make every opening smaller, keep everything else the same, and count how long she stays afloat.

This is a toy model of a real tragedy. It counts water and minutes only. It says nothing about how many people an extra hour would have helped, and it is not a statement about blame. The numbers to trust are the published ones it is checked against.

## What is here

| File | What it is |
|---|---|
| `titanic_flooding.py` | The model, the comparison with the published work and the stress tests. |
| `results.txt` | The script's output, as used for the numbers in the video. |

## Run it

You need Python 3 and NumPy.

```
pip install numpy
python3 titanic_flooding.py
```

It takes about two and a half minutes. Add `--fast` to skip the stress tests (about 15 seconds). The random seed is fixed, so you get the same numbers each time.

## How it works

The ship is a simple hull, the real length and weight, cut into 16 rooms by walls that stop below the upper decks. Six rooms at the bow have small openings low down. Every five seconds the model asks three things:

1. How hard is the sea pushing at each opening? Deeper water pushes harder, and the push fades as the water inside rises to meet the sea outside.
2. How heavy is the bow now, and how far has the ship dipped?
3. Is the water in any room higher than its wall? If so, it spills into the next room.

The ship counts as lost when she tips 10 degrees bow-down or can no longer float. The one dial is the size of the openings.

## What it says

| Openings | Time afloat (model) |
|---|---|
| Double the real size (24 sq ft) | 1 h 39 min |
| The real size (12 sq ft) | 2 h 40 min (tuned to match, not a result) |
| Three quarters | 3 h 16 min |
| Half (6 sq ft) | 4 h 23 min, to about 4:03 am |
| A quarter | 7 h 25 min |

The rescue ship Carpathia reached the scene at about 4:00 am.

| Which rooms are open | Result (model) |
|---|---|
| The first 4, wide open (a head-on hit) | still afloat after 12 hours |
| The first 5, wide open | 1 h 59 min |
| No walls at all | 1 h 46 min |
| Walls one deck taller | 3 h 51 min |
| Walls that cannot be spilled over | 6 h 43 min (still sinks) |

## Checked against published work

| | This model | Published |
|---|---|---|
| Water aboard after 40 minutes | about 13,800 tonnes | about 16,300 tonnes (Wilding, 1912) |
| Inflow in the first hour, average | 261 tons a minute | 243 tons a minute (Paik, Kim and Thomas, 2025) |
| Inflow in the first hour, lowest | 65 tons a minute | 138 tons a minute (same study) |
| Bow-down angle | 4.0 degrees at 90 minutes | about 4 degrees at 100 minutes (S. Halpern) |
| First four rooms flooded | floats | floats (the 1912 design; the 2025 study's head-on test) |

The two agree on the first hour, on the pumps being overwhelmed about twenty to one, and on four rooms. This model slows down more than the big study does later on, because it has sixteen plain rooms and one guess standing in for every stair, hatch and corridor. Trust the study.

## Change my guesses

All inputs sit at the top of the script, labelled:

- **SOURCED**: the ship's size and weight, the times, the 12 square feet and the depth of the damage (Wilding, 1912).
- **ASSUMED**: my guesses (A0 to A7): how the 12 square feet is shared between the six rooms, the room lengths, the wall heights, how much of each room can hold water, the hull shape, and when the ship counts as lost.
- **TUNED**: `SPILL_W`, how easily water spills over a wall along the decks. It is found by search so that the real openings give the real 2 hours 40 minutes. It is the biggest guess.

Change any of them and run it again.

## How much to trust it

- With every guess changed by up to half either way and the model re-tuned each time, only 22 of 60 versions could match the real night at all. The model is fragile.
- In those 22, half-size openings always bought more time: 1.5 to 1.9 times as long. But only about six in ten lasted to 4:00 am, and only about half kept the four-room ship afloat.
- The real-size row proves nothing, because the model is tuned to it.
- It has no list to one side, does not break the ship in two, and knows nothing about people, lifeboats or the cold.

Trust the pattern (a smaller hole means a longer night), not the exact minute.

## Sources

- Edward Wilding's 1912 estimate of about 12 square feet, explained in S. Halpern, "Somewhere About 12 Square Feet": https://encyclopedia-titanica.org/somewhere-about-12-square-feet.html
- Paik, Kim and Thomas, "The digital reconstruction and resurrection of the RMS Titanic's sinking", *Ships and Offshore Structures*, 2025, doi 10.1080/17445302.2025.2603417: https://www.tandfonline.com/doi/full/10.1080/17445302.2025.2603417
- Hackett and Bedford, "The Sinking of S.S. Titanic, Investigated by Modern Techniques", *Transactions of the Royal Institution of Naval Architects*, 1996/97.
- Stettler and Thomas, "Flooding and structural forensic analysis of the sinking of the RMS Titanic", *Ships and Offshore Structures*, 2013.
