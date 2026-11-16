# History, simulated

The code behind each simulation video on the channel. Every video gets its own folder with the model, its results and a README on how to run it and how much to trust it.

| Folder | Video | What it simulates |
|---|---|---|
| [`mongoose-island/`](mongoose-island/) | *The Island That Said No* | What happened after 72 mongooses were released in Hawaiʻi in 1883, and what it would take for them to reach Kauaʻi. |
| [`pearl-harbor-radar/`](pearl-harbor-radar/) | *What If Someone Had Believed the Radar at Pearl Harbor? I Simulated It* | The first 15 minutes of the attack, replayed with a head start of 0 to 53 minutes. |

## Run any of them

You need Python 3 and NumPy.

```
pip install numpy
cd <folder>
python3 <script>.py
```

Random seeds are fixed, so you get the same numbers as the video.

These are simple models with labelled guesses. They show how a situation behaves; they are not forecasts. Change the guesses at the top of each script and see what you get.
