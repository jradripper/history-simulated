# Nvidia without Jensen: does the price come back?

Code for the simulation in the video *I Simulated Nvidia Without Jensen 20,000 Times*.

Jensen Huang resigned as Nvidia's chief executive on 12 November 2026. Between the last close before the story broke (28 October, $215.38) and the close the day after the first results without him (18 November, $150.96), the shares fell 30%. This model asks one thing: starting from that real price, in how many of 20,000 two-year runs does the price get back above where it was the day before the story broke?

**This is a simulation about odds. It is not a forecast and it is not financial advice.** It was run on 18 November 2026 and the story was still moving. It says nothing about any person.

## What is here

| File | What it is |
|---|---|
| `nvidia_without_jensen.py` | The model, the dial, the check against analysts and the stress tests. |
| `data/sp500_monthly.csv` | Monthly S&P 500 history (Shiller data, from [datasets/s-and-p-500](https://github.com/datasets/s-and-p-500)). The model uses January 1950 to September 2026. |
| `results.txt` | The script's output, as used for the numbers in the video. |
| `sample_paths.json` | A handful of single runs, used to draw the lines on screen. |

## Run it

You need Python 3, NumPy and pandas.

```
pip install numpy pandas
python3 nvidia_without_jensen.py data/sp500_monthly.csv
```

The random seed is fixed, so you get the same numbers each time.

## How it works

Each run is two years, one month at a time. Every month the model rolls three things:

1. **The stock market.** It picks months from the market's own real history since 1950.
2. **Nvidia's own luck.** Nvidia swings harder than the market, and has good and bad months of its own. These dice are fair on average.
3. **Life after the founder.** The one dial: how much losing the founder costs, or gives back, each year.

There is also a small chance of one serious legal or export-rule blow somewhere in the two years. Then it counts how many runs end above the old price.

## What it says

| Question | Model |
|---|---|
| Back above the old price ($215.38) at two years | about one run in three (33%) |
| Touches the old price at some point on the way | about half of all runs (51%) |
| Ends two years lower than the start price | 44% |
| Ends below half the start price | 10% |
| Middle run at two years | about $166 a share (nine runs in ten between $60 and $427) |

| The dial: life after the founder | Back above the old price |
|---|---|
| Costs nothing (the price already has it right) | 36% |
| Costs a little (4.4% a year) | 30% |
| Costs a lot (8.3% a year) | 25% |

| The stock market you happen to get | Back above the old price |
|---|---|
| Worst third of markets | 11% |
| Middle third | 30% |
| Best third | 57% |

The gap between a bad and a good stock market (46 points) is about four times the gap between the dial at nothing and at a lot (11 points). In this model the market matters more than the founder.

## Checked against the real record

Analysts' average 12-month price target when this was run was about $256. The model's middle run at one year is $159, and it gives that target about a 12% chance. The model is blind to profits: it only knows prices. If the profit forecasts come true, the old price is not a stretch, so the model may be too gloomy.

## Change my guesses

All inputs sit at the top of the script, labelled:

- **SOURCED**: prices, share count, market history, the published five-year beta, and the two studies that anchor the dial.
- **ASSUMED** (A1 to A4): how hard Nvidia swings with the market, the size of its own luck, the dial, and the chance and size of one legal or export-rule blow. The dial (A3) is the biggest guess.
- **TUNED**: nothing.

To update it, change `PRICE_NOW` to the latest close and run it again.

## How much to trust it

- With every guess nudged by up to half, over 500 re-runs, the headline ranged from 19% to 46%. It never reached a coin flip.
- With a flat stock market for two years it drops to 12%.
- Even if life after the founder *gave* Nvidia the full founder edge (+8.3% a year), it is 47%.

Trust the shape (the odds are against a full recovery inside two years, and the market matters more than the dial), not the exact number.

## Sources

- R. Fahlenbrach, "Founder-CEOs, Investment Decisions, and Stock Market Performance", *Journal of Financial and Quantitative Analysis*, 2009: founder-CEO firms beat their benchmarks by 8.3% a year, 4.4% after controls, 1993 to 2002.
- S. Jory and co-authors, *Applied Economics*, 2015: across 80 CEO scandals, shares fell 6.5% to 9.5% in the month after, with no gap left three years on.
- Prices, share count and beta: stockanalysis.com, 17 and 18 November 2026.
- S&P 500 monthly history: https://github.com/datasets/s-and-p-500
