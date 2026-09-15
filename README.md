# screensaver-fprint

***English** · [Deutsch](README.de.md)*

Fingerprint unlock for the Cinnamon lock screen that says what it is doing.

A fork of
[cinnamon-screensaver](https://github.com/linuxmint/cinnamon-screensaver), with
the same panel [greeter-fprint](https://github.com/SoulInfernoDE/greeter-fprint)
puts on the login screen. Unofficial: not affiliated with, endorsed by, or
supported by Linux Mint.

![The panel cycling through its states: yellow while the reader waits, red for a
rejected finger, green for a recognised one, then the password sign and a
rejected password](docs/states.gif)

## Why

On the stock Cinnamon lock screen:

- **A rejected finger shows nothing at all.** The reader's error never reaches
  the screen, so a miss looks exactly like a reader that is not listening.
- **Or it says "Incorrect password"** — although you typed nothing.
- **Messages pile up**, one under the other.

screensaver-fprint shows exactly one message at a time:

| | |
| --- | --- |
| **Yellow** | the reader is waiting |
| **Red** | finger not recognised — back to yellow after 1.5 s |
| **Green** | finger recognised — the screen unlocks |
| **Password sign** | the reader gave up; type your password |
| **Sign, red message** | wrong password |

## Requirements

- Cinnamon and a working fingerprint setup: `fprintd`, `libpam-fprintd`, an
  enrolled finger
- [greeter-fprint](https://github.com/SoulInfernoDE/greeter-fprint) installed —
  the lock screen takes Tux and the translations from it

## Install

Python only, nothing to build. **Back up the file you replace first** — this is
the lock screen:

```bash
sudo cp /usr/share/cinnamon-screensaver/unlock.py \
        /usr/share/cinnamon-screensaver/unlock.py.bak-$(date +%Y%m%d%H%M%S)

sudo install -m 644 src/fingerprintPanel.py src/fingerprintMessages.py src/unlock.py \
        /usr/share/cinnamon-screensaver/

cinnamon-screensaver-command --exit
```

If the lock screen misbehaves: switch to a text console (Ctrl+Alt+F2), restore
the backup and run `pkill -f cinnamon-screensaver`.

## How it works

| | |
| --- | --- |
| [`docs/HOW-IT-WORKS.md`](docs/HOW-IT-WORKS.md) | the upstream bug that swallows the reader's error, how the panel works around it, safety, debugging |

Also available in German; the link sits at the top.

## Related

[greeter-fprint](https://github.com/SoulInfernoDE/greeter-fprint) — the same
panel for the LightDM login screen.

## For Linux Mint

Everything new in this fork may be used, adapted and relicensed by Linux Mint
freely, without asking and without attribution — the `PAM_ERROR_MSG` fix first
of all. The exact scope is in [COPYRIGHT.md](COPYRIGHT.md).

## License

GPL-2+, like cinnamon-screensaver — see [COPYING](COPYING) and
[COPYRIGHT.md](COPYRIGHT.md). Tux is the Linux mascot created by Larry Ewing; the
Linux Mint logo is not in this repository but loaded from the system at runtime.
Upstream's own README: [README.cinnamon-screensaver.md](README.cinnamon-screensaver.md).
