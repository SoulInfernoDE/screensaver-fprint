#!/usr/bin/python3
# Copyright (C) 2026 soul-inferno <nofunction@gmx.net>
#
# This file is part of screensaver-fprint, a fork of cinnamon-screensaver.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Classification of pam_fprintd's messages.

This is a port of greeter-fprint's fingerprint-messages.vala, and it exists for
the same reason: PAM messages arrive as plain strings with nothing saying where
they came from, so recognising the text is the only way to tell a fingerprint
message from any other one.

Unlike in the greeter, the strings here may well arrive *translated*: the
screensaver's PAM helper runs inside a process that does call setlocale(), so
pam_fprintd's own gettext can fire if a fprintd translation happens to be
installed. That is why matching is done against both the English msgids and
the German wording - whichever arrives, the same state comes out.

classify() returns None when the message is not fingerprint-related; the
caller then handles it exactly as before.
"""

import gettext

# The panel's strings live in greeter-fprint's catalogue: the login screen and
# the lock screen say exactly the same sentences, so they share one set of
# translations instead of keeping two in step. Deliberately NOT called "_":
# cinnamon-screensaver installs its own _ into builtins, and shadowing that
# would silently untranslate the rest of the dialog.
_p = gettext.translation("greeter-fprint", "/usr/share/locale",
                         fallback=True).gettext

WAITING = "waiting"   # reader is armed and wants a finger
RETRY = "retry"       # scan didn't take; try again, still armed
FAILURE = "failure"   # this attempt is over and failed

# Longest first: "left index finger" has to win over a bare "finger".
_FINGERS = [
    ("left index finger", "linken Zeigefinger"),
    ("left middle finger", "linken Mittelfinger"),
    ("left ring finger", "linken Ringfinger"),
    ("left little finger", "linken kleinen Finger"),
    ("right index finger", "rechten Zeigefinger"),
    ("right middle finger", "rechten Mittelfinger"),
    ("right ring finger", "rechten Ringfinger"),
    ("right little finger", "rechten kleinen Finger"),
    ("left thumb", "linken Daumen"),
    ("right thumb", "rechten Daumen"),
]


def classify(raw):
    """Return (kind, display_text) or None if this isn't about the reader."""
    if not raw:
        return None

    text = raw.lower()

    # --- failures ---------------------------------------------------------
    if "failed to match" in text or "no match" in text or "nicht erkannt" in text:
        return FAILURE, _p("Fingerprint not recognised")

    if ("timed out" in text or "zeitüberschreitung" in text) and (
            "verification" in text or "finger" in text or "leser" in text):
        return FAILURE, _p("The reader timed out")

    if "no prints enrolled" in text:
        return FAILURE, _p("No fingerprint enrolled")

    # --- retry hints ------------------------------------------------------
    if "too short" in text or "zu schnell" in text:
        return RETRY, _p("Swiped too fast - once more, please")

    if "not centered" in text or "not centred" in text or "nicht mittig" in text:
        return RETRY, _p("Not centred - once more, please")

    if "remove your finger" in text or "finger weg" in text:
        return RETRY, _p("Lift your finger and try again")

    if ("place your finger" in text or "swipe your finger" in text) and "again" in text:
        return RETRY, _p("Once more, please")

    if "erneut" in text and ("finger" in text or "leser" in text):
        return RETRY, _p("Once more, please")

    # --- the ordinary "reader is waiting" messages ------------------------
    placing = "place your" in text or "legen sie" in text
    swiping = "swipe your" in text or "ziehen sie" in text

    if placing or swiping:
        for english, german in _FINGERS:
            if english in text or german.lower() in text:
                if placing:
                    return WAITING, _p("Place your %s on the reader") % german
                return WAITING, _p("Swipe your %s across the reader") % german

        if placing:
            return WAITING, _p("Place your finger on the reader")
        return WAITING, _p("Swipe your finger across the reader")

    # Anything else unmistakably about the reader: keep it in the panel rather
    # than in the dialog's message label, but say something generic rather than
    # showing raw English.
    if "fingerprint" in text or "fingerabdruck" in text:
        return WAITING, _p("Waiting for the fingerprint reader")

    return None
