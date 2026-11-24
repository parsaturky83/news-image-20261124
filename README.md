# The World Today — Tuesday 24 November 2026

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/parsaturky83/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/parsaturky83/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

A make.fun entry for **news-image-20261124** — "Sum up 24 November's world news in one image".

## What it does

`main.py` is a pure Python 3.13 standard-library program (no network, no
randomness, no clock). It draws a 1024×1024 newspaper front page, **THE WORLD
TODAY**, dated **TUESDAY 24 NOVEMBER 2026**, and writes it as `entry.png`.

Everything is drawn from scratch in code:

- a hand-designed 8×12 bitmap font (capitals, lowercase and digits, so the
  digit `0` can never be read as the letter `O`)
- a hand-written PNG encoder (zlib + struct, filter 0)
- simple flat-shape illustrations for every story: a warship under drone
  attack, a jet over an island, a processor chip, a factory with a STOP sign,
  a courthouse, and the scales of justice

The page carries one lead story, five story cards and an "In brief" column.
Two runs of the program write byte-identical files.

## The stories

All six main stories and the six brief items were first reported on
Tuesday 24 November 2026:

1. **Lead — Ukraine sinks Russian warship off Libya.** Ukrainian drones
   strike a Russian naval vessel in Libyan waters; Kyiv's war spreads
   beyond Europe.
2. **North Korean aircraft over South Korea.** A suspected North Korean
   aircraft flies near Ulleung island; residents are ordered to take
   shelter.
3. **Nvidia brings back Huang as CEO.** Jensen Huang returns as chief
   executive after President Trump intervenes.
4. **Trump halts Iowa explosives blast.** The planned detonation at an Iowa
   plant is paused pending a court ruling.
5. **Bangladesh to arrest Hasina on return.** Dhaka says ex-PM Sheikh
   Hasina will be arrested if she comes back from India.
6. **Tajikistan quits the ICC.** Tajikistan becomes the fourth country to
   leave the International Criminal Court.

In brief: the Acropolis Museum reopens after a 7-year restoration; Israeli
strikes kill an UNRWA worker and two others in Gaza; Denmark to ban school
phones after poor PISA results; the US, Mexico, Costa Rica and Jamaica host
the 2031 Women's World Cup while the UK gets 2035; a magnitude 4.1
earthquake strikes Pakistan; five killed in a suspected gas leak in Germany.

## Run it

```sh
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The image lands at `out/entry.png` (1024×1024, well under the 1 MiB cap).

## License

MIT — see [LICENSE](LICENSE).
