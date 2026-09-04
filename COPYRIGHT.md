# Copyright and licensing

screensaver-fprint is a fork of **cinnamon-screensaver**. Almost every file here
is upstream's work, under upstream's terms. This file records who holds what,
since the machine-readable `debian/copyright` that carried it upstream is not
part of this fork.

## The fork as a whole

**GPL-2+**, the licence cinnamon-screensaver is under. The full text is in
[COPYING](COPYING); [COPYING.LIB](COPYING.LIB) is the LGPL-2 text, also shipped
upstream.

    Files: *
    Copyright: 2003, Bill Nottingham <notting@redhat.com>
               1989-1991, Free Software Foundation, Inc
               1991-2004, Jamie Zawinski <jwz@jwz.org>
               2016, Michael Webster <miketwebster@gmail.com>
               2006, Ray Strode <rstrode@redhat.com>
               2002, Sun Microsystems
               2004-2006, William Jon McCann <mccann@jhu.edu>
               2013-2024, Linux Mint Project <root@linuxmint.com>
               2026, soul-inferno <nofunction@gmx.net>
    License: GPL-2+

    Files: libcscreensaver/setuid.c
           libcscreensaver/setuid.h
           libcscreensaver/subprocs.c
           libcscreensaver/subprocs.h
    Copyright: 1991-2004, Jamie Zawinski <jwz@jwz.org>
    License: GPL-2+

Upstream's per-file copyright headers are untouched. The files added by this
fork carry their own headers naming the same licence:

    src/fingerprintPanel.py
    src/fingerprintMessages.py

`src/unlock.py` is upstream's file with this fork's changes in it.

## Artwork and translations

Neither is redistributed here. Both come from
[greeter-fprint](https://github.com/SoulInfernoDE/greeter-fprint):

- **Tux** — loaded at runtime from `/usr/share/greeter-fprint/tux-fprint.svg`.
  An original drawing, GPL-3, depicting Tux, the Linux mascot created by
  **Larry Ewing** with The GIMP in 1996.
- **The German strings** — from greeter-fprint's gettext catalogue, GPL-3, bound
  as the `greeter-fprint` text domain.

## The Linux Mint logo

Not in this repository. The panel loads the system's own installed icon
(`linuxmint-logo-badge-symbolic`) at runtime and uses it as a Cairo mask, so no
Linux Mint trademark is redistributed here.

"Linux Mint" and "Cinnamon" are trademarks of the Linux Mint project, registered
through the Linux Mark Institute. This fork is not affiliated with, endorsed by,
or supported by Linux Mint, and deliberately does not carry their name.

## Additional grant to the Linux Mint project

Beyond the GPL, and specifically for the **Linux Mint project**: the parts of
this repository that are ours — the changes made in this fork, chiefly
`src/fingerprintPanel.py`, `src/fingerprintMessages.py` and the additions to
`src/unlock.py` — may be used, adapted, relicensed and shipped by Linux Mint in
any way they see fit, without permission and without attribution.

This is a one-way grant from the copyright holder of those parts
(soul-inferno <nofunction@gmx.net>) and cannot reach further than that. It does
not touch upstream cinnamon-screensaver's code, which stays with its own
copyright holders under GPL-2+.

Everyone else has the GPL-2+, which is the licence of the fork as a whole.
