# Pearl Harbor: what if someone had believed the radar?

Code for the simulation in the video *What If Someone Had Believed the Radar at Pearl Harbor? I Simulated It*.

At 7:02 a.m. on 7 December 1941, the Opana radar on Oʻahu picked up the incoming attack. The warning was dismissed. This model asks what a believed warning would have bought: it keeps the island exactly as unready as it was, gives it a head start of 0 to 53 minutes, and replays the first 15 minutes of the attack 2,000 times per setting.

This is a toy model of a real tragedy. It is not a forecast, and it does not count lives.

## What is here

| File | What it is |
|---|---|
| `pearl_harbor_radar_warning.py` | The model, the stress tests and a check against the real morning. |
| `results.txt` | The script's output, as used for the numbers in the video. |

## Run it

You need Python 3 and NumPy.

```
pip install numpy
python3 pearl_harbor_radar_warning.py
```

It takes about 15 seconds. The random seed is fixed, so you get the same numbers each time.

## What it counts

For each head start (0, 10, 20, 35 and 53 minutes), the averages of:

1. battleships in the torpedo lane with their watertight doors shut when the first torpedo comes (of 4)
2. Army fighters already in the air (of 94 ready to fly)
3. torpedo hits
4. battleships sunk by torpedo
5. attacking planes shot down in the first 15 minutes

35 minutes is the 7:20 phone call; 53 minutes is an alarm at the first blip.

## Change my guesses

All inputs sit at the top of the script, labelled:

- **SOURCED**: taken from the record, with the source in the comment.
- **ASSUMED**: my guess (A1 to A7). The biggest one is `A2_FIGHTER_MEDIAN_MIN`, the minutes it takes to get a parked, unarmed fighter into the air (40).
- **TUNED**: adjusted so that zero warning matches the real morning.

Change any of them and run it again.

## How much to trust it

- With every assumed input changed by up to half either way, the fighters in the air at 35 minutes swing from 7 to 65. Do not trust that number.
- In every one of those 300 versions, a 35-minute warning sank fewer battleships than no warning. That is the result the video relies on.
- The model leaves out the second wave, the high-level bomb that destroyed USS Arizona, damage on the ground and anything after the first 15 minutes.

Trust the pattern, not the exact number.

## Sources

- Richard B. Frank, National WWII Museum, "The Three Missed Tactical Warnings": https://www.nationalww2museum.org/war/articles/pearl-harbor-missed-tactical-warnings
- Arakaki & Kuborn, *7 December 1941: The Air Force Story*: https://ibiblio.org/hyperwar/AAF/7Dec41/index.html
- US Navy (NHHC), Pearl Harbor fact sheet: https://history.navy.mil/content/history/museums/nmusn/education/educational-resources/the-date-that-lives-in-infamy--pearl-harbor--high-school-/the-aftermath/pearl-harbor-fact-sheet.html
- USNI *Naval History*, December 2026, "Victory Undermined": https://www.usni.org/magazines/naval-history/2026/december/victory-undermined
