# COVID: what if America had stayed home one week earlier?

Code for the simulation in the video *What If America Had Stayed Home One Week Earlier? (I Simulated It)*.

The Columbia study the video is built around marks 15 March 2020 as the day the United States began staying home. This model asks what moving that one date does: it keeps the same virus and the same behaviour, shifts the start of distancing earlier or later, and counts deaths up to 3 May 2020.

This is a toy model of a real tragedy. It is not a forecast and it is not a statement about blame. The numbers to trust are the published ones it is checked against: Pei, Kandula and Shaman (Columbia University), *Science Advances*, 2020.

## What is here

| File | What it is |
|---|---|
| `covid_one_week_earlier.py` | The model, the comparison with the Columbia study and the stress tests. |
| `results.txt` | The script's output, as used for the numbers in the video. |

## Run it

You need Python 3 and NumPy.

```
pip install numpy
python3 covid_one_week_earlier.py
```

It takes about 20 seconds. The random seed is fixed, so you get the same numbers each time.

## How it works

Everyone in the country sits in one of four boxes: can catch it, caught it but not spreading yet, spreading it, finished. Before the country stays home, each spreader infects 2.8 others. After, that falls to 0.9 over three weeks. The one dial is the day the fall begins.

## What it says

| Stay home from | Deaths by 3 May (model) | Compared with 15 March |
|---|---|---|
| 22 March (one week later) | about 177,000 | 2.7 times as many |
| 15 March (the record) | about 65,000 | tuned to match, not a result |
| 8 March (one week earlier) | about 22,000 | about two thirds fewer (67%) |
| 1 March (two weeks earlier) | about 7,000 | nine in ten fewer (90%) |

The Columbia study, which modelled 3,142 counties with real travel data, found 49.4% fewer deaths for one week earlier (32,335) and 90.8% for two weeks (59,351).

The two models agree on two weeks and disagree on one week. Trust the study. This model treats the whole country as one pond; the real epidemic was thousands of local ones that started on different days, so one week helped some places much more than others.

## Change my guesses

All inputs sit at the top of the script, labelled:

- **SOURCED**: taken from the Columbia study (the dates, the delay from infection to death, the real total).
- **ASSUMED**: my guesses (A1 to A6). The biggest one is `A1_R_BEFORE`, how many people each spreader infects before staying home (2.8).
- **TUNED**: the number of infections on 15 January 2020, found by search so that the real timeline ends on the real total.

Change any of them and run it again.

## How much to trust it

- With every guess changed by up to half either way, 300 times, one week earlier saved anything from 25% to 87% of deaths (the middle 90% of versions). Do not trust the 67%.
- In every one of those 300 versions, two weeks earlier saved more than one week. In 9 out of 10, one week saved at least a third.
- Make the virus slow (each spreader infects 1.1) and one week earlier saves only 6%. The week matters because the virus was doubling about every three and a half days.
- The 15 March row proves nothing, because the model is tuned to it. The model also runs ahead of the reported deaths in early March and peaks about a week later than the real spring did.
- It stops on 3 May 2020, counts none of the costs of staying home, and assumes people would have behaved the same way a week sooner.

Trust the pattern, not the exact number.

## Source

- Pei, Kandula and Shaman, "Differential effects of intervention timing on COVID-19 spread in the United States", *Science Advances* 6(49), 2020, doi 10.1126/sciadv.abd6370: https://pmc.ncbi.nlm.nih.gov/articles/PMC7821895
