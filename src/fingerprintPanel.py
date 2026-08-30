#!/usr/bin/python3
"""
The fingerprint panel for the unlock dialog.

Same behaviour, same artwork and the same timings as greeter-fprint's panel,
so the lock screen and the login screen tell the user the same story:

    WAITING   Mint logo glows yellow, breathing, while the reader waits.
    FAILED    Mint logo flashes red for FLASH_MS, then back to WAITING.
    SUCCESS   Mint logo glows green for FLASH_MS, then success_finished.
    PASSWORD  Tux swaps the logo for a "Passwort:" sign, because the reader
              gave up and PAM fell through to the password.

A flash owns the panel for its full duration: pam_fprintd sends "Failed to
match fingerprint" and, milliseconds later, the next "place your finger", and
without that rule the red is set and overwritten before it can be seen. States
arriving mid-flash are queued and applied when it ends.

The artwork is shared with greeter-fprint rather than duplicated - see
TUX_PATHS.
"""

import gettext
import math

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, GObject, Pango, PangoCairo
import cairo

# See fingerprintMessages.py: shared catalogue, and not named "_" because
# cinnamon-screensaver installs its own _ into builtins.
_p = gettext.translation("greeter-fprint", "/usr/share/locale",
                         fallback=True).gettext

HIDDEN = "hidden"
WAITING = "waiting"
FAILED = "failed"
SUCCESS = "success"
PASSWORD = "password"

# The spec is 1.5s for both flashes. SUCCESS spends it before the screen
# actually unlocks, so it is a real (deliberate) delay.
FLASH_MS = 1500

# Tux is installed by greeter-fprint; the in-tree copy is the fallback for a
# machine that only has the screensaver fork.
TUX_PATHS = [
    "/usr/share/greeter-fprint/tux-fprint.svg",
    "/usr/share/cinnamon-screensaver/tux-fprint.svg",
]

MINT_LOGO = "/usr/share/icons/hicolor/scalable/apps/linuxmint-logo-badge-symbolic.svg"

TUX_WIDTH = 132
LOGO_SIZE = int(TUX_WIDTH * 0.26)

# Room for the glow: it hangs above and outside Tux's own outline, and would
# otherwise be clipped by the drawing area.
TOP_PAD = int(LOGO_SIZE * 0.9)
SIDE_PAD = int(LOGO_SIZE * 1.6)

# Where the logo hangs, as a fraction of the artwork's viewBox: just beyond the
# raised flipper's tip, above and to the left of the head. Keep in sync with
# tux-fprint.svg.
HAND_X = 0.105
HAND_Y = 0.085

COLOURS = {
    FAILED:  (0.90, 0.22, 0.21),
    SUCCESS: (0.24, 0.72, 0.34),
    WAITING: (1.00, 0.80, 0.10),
}

# The message takes the colour the logo has right now - the sentence and the
# glow are one signal, not two. PASSWORD has no signal colour, so it is white.
LABEL_COLOURS = {
    FAILED:   "#e63836",
    SUCCESS:  "#3db857",
    PASSWORD: "#ffffff",
    WAITING:  "#ffcc1a",
}


class FingerprintPanel(Gtk.Box):
    __gsignals__ = {
        "success-finished": (GObject.SignalFlags.RUN_LAST, None, ()),
    }

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        self.set_halign(Gtk.Align.CENTER)
        self.set_no_show_all(True)

        self.state = HIDDEN
        self.pulse = 0.0
        self.pulse_timer = 0
        self.flash_timer = 0
        self.pending = None          # (state, text) queued during a flash

        self.tux = self._load_tux()
        self.logo = self._load(MINT_LOGO, LOGO_SIZE, LOGO_SIZE)

        self.canvas = Gtk.DrawingArea()
        height = self.tux.get_height() if self.tux else 150
        self.canvas.set_size_request(TUX_WIDTH + 2 * SIDE_PAD, height + TOP_PAD + 12)
        self.canvas.connect("draw", self.on_draw)
        self.canvas.show()
        self.pack_start(self.canvas, False, False, 0)

        self.message_label = Gtk.Label("")
        self.message_label.set_halign(Gtk.Align.CENTER)
        self.message_label.set_justify(Gtk.Justification.CENTER)

        # NOT the "auth-message" class: in cinnamon-screensaver's theme that is
        # the error label, which is red whatever it says - so every fingerprint
        # message came out looking like a failure. Own provider, colour follows
        # the state instead.
        self.label_style = Gtk.CssProvider()
        self.message_label.get_style_context().add_provider(
            self.label_style, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self._apply_label_colour()

        self.message_label.show()
        self.pack_start(self.message_label, False, False, 0)

    def _apply_label_colour(self):
        colour = LABEL_COLOURS.get(self.state, LABEL_COLOURS[WAITING])
        css = ("label { color: %s; font-size: 15px; font-weight: 500;"
               " text-shadow: 0 1px 4px rgba(0, 0, 0, 0.75); }" % colour)
        self.label_style.load_from_data(css.encode())

    # --- loading ---------------------------------------------------------

    def _load(self, path, width, height):
        try:
            return GdkPixbuf.Pixbuf.new_from_file_at_scale(path, width, height, True)
        except GLib.Error:
            return None

    def _load_tux(self):
        for path in TUX_PATHS:
            pixbuf = self._load(path, TUX_WIDTH, -1)
            if pixbuf is not None:
                return pixbuf
        print("fingerprintPanel: no tux artwork found in %s" % ", ".join(TUX_PATHS))
        return None

    # --- state transitions ------------------------------------------------

    def show_waiting(self, text):
        self._set_state(WAITING, text)

    def show_failure(self, text):
        self._set_state(FAILED, text)

    def show_success(self, text):
        self._set_state(SUCCESS, text)

    def show_password_fallback(self, text):
        self._set_state(PASSWORD, text)

    def reset(self):
        self._set_state(HIDDEN, "")

    def is_active(self):
        return self.state != HIDDEN

    def _set_state(self, new_state, text):
        # A flash owns the panel for its full FLASH_MS; see the module
        # docstring for why. Another failure restarts it, reset() is a hard
        # stop that clears the queue.
        if self.flash_timer != 0 and new_state not in (HIDDEN, FAILED):
            self.pending = (new_state, text)
            return

        if self.flash_timer != 0:
            GLib.source_remove(self.flash_timer)
            self.flash_timer = 0

        if new_state == HIDDEN:
            self.pending = None

        self.state = new_state
        self.message_label.set_text(text)

        if new_state == HIDDEN:
            self._stop_pulse()
            self.hide()
            return

        self.show()
        self.message_label.set_visible(text != "")

        if new_state == WAITING:
            self._start_pulse()
        else:
            self._stop_pulse()

        if new_state in (FAILED, SUCCESS):
            self.flash_timer = GLib.timeout_add(FLASH_MS, self._flash_done, new_state)

        self._apply_label_colour()
        self.canvas.queue_draw()

    def _flash_done(self, flashed_state):
        self.flash_timer = 0

        if flashed_state == SUCCESS:
            self.emit("success-finished")
            return GLib.SOURCE_REMOVE

        if self.pending is not None:
            state, text = self.pending
            self.pending = None
            self._set_state(state, text)
        else:
            # Nothing queued: back to waiting, pam_fprintd retries on its own.
            self.state = WAITING
            self._start_pulse()
            self._apply_label_colour()
            self.canvas.queue_draw()

        return GLib.SOURCE_REMOVE

    # --- animation --------------------------------------------------------

    def _start_pulse(self):
        if self.pulse_timer != 0:
            return
        self.pulse_timer = GLib.timeout_add(40, self._tick)

    def _tick(self):
        self.pulse += 0.09
        if self.pulse > 2 * math.pi:
            self.pulse -= 2 * math.pi
        self.canvas.queue_draw()
        return GLib.SOURCE_CONTINUE

    def _stop_pulse(self):
        if self.pulse_timer != 0:
            GLib.source_remove(self.pulse_timer)
            self.pulse_timer = 0

    # --- drawing ----------------------------------------------------------

    def on_draw(self, widget, cr):
        if self.state == HIDDEN or self.tux is None:
            return False

        alloc = widget.get_allocation()
        tux_x = (alloc.width - self.tux.get_width()) / 2.0
        tux_y = float(TOP_PAD)

        Gdk.cairo_set_source_pixbuf(cr, self.tux, tux_x, tux_y)
        cr.paint()

        hx = tux_x + self.tux.get_width() * HAND_X
        hy = tux_y + self.tux.get_height() * HAND_Y

        if self.state == PASSWORD:
            self._draw_sign(cr, hx, hy)
        else:
            r, g, b = COLOURS.get(self.state, COLOURS[WAITING])
            intensity = 0.55 + 0.30 * math.sin(self.pulse) if self.state == WAITING else 1.0
            self._draw_logo(cr, hx, hy, r, g, b, intensity)

        return False

    def _draw_logo(self, cr, hx, hy, r, g, b, intensity):
        radius = LOGO_SIZE * 0.95

        glow = cairo.RadialGradient(hx, hy, 2, hx, hy, radius)
        glow.add_color_stop_rgba(0.0, r, g, b, 0.80 * intensity)
        glow.add_color_stop_rgba(0.55, r, g, b, 0.35 * intensity)
        glow.add_color_stop_rgba(1.0, r, g, b, 0.0)
        cr.set_source(glow)
        cr.arc(hx, hy, radius, 0, 2 * math.pi)
        cr.fill()

        if self.logo is None:
            return

        # The logo pixbuf is used purely as an alpha mask, so the silhouette
        # takes the state colour - one file, three colours.
        Gdk.cairo_set_source_pixbuf(cr, self.logo,
                                    hx - self.logo.get_width() / 2.0,
                                    hy - self.logo.get_height() / 2.0)
        mask = cr.get_source()
        cr.set_source_rgba(r, g, b, 0.55 + 0.45 * intensity)
        cr.mask(mask)

    def _draw_sign(self, cr, hx, hy):
        # Proportional to Tux: at a fixed size the sign covered his face on the
        # lock screen, where the artwork is drawn smaller than in the greeter.
        width = int(TUX_WIDTH * 0.62)
        height = int(width * 0.44)
        radius = 8
        x, y = hx - width / 2, hy - height / 2

        cr.set_source_rgba(0.42, 0.31, 0.20, 1.0)
        cr.rectangle(hx - 3, y + height - 4, 6, 24)
        cr.fill()

        cr.new_sub_path()
        cr.arc(x + width - radius, y + radius, radius, -math.pi / 2, 0)
        cr.arc(x + width - radius, y + height - radius, radius, 0, math.pi / 2)
        cr.arc(x + radius, y + height - radius, radius, math.pi / 2, math.pi)
        cr.arc(x + radius, y + radius, radius, math.pi, 1.5 * math.pi)
        cr.close_path()

        cr.set_source_rgba(0.99, 0.99, 0.99, 0.97)
        cr.fill_preserve()
        cr.set_source_rgba(0.55, 0.68, 0.29, 1.0)
        cr.set_line_width(2.2)
        cr.stroke()

        layout = PangoCairo.create_layout(cr)
        layout.set_text(_p("Password:"), -1)
        layout.set_font_description(Pango.FontDescription("Ubuntu Bold 10"))

        tw, th = layout.get_pixel_size()
        cr.move_to(x + (width - tw) / 2, y + (height - th) / 2)
        cr.set_source_rgba(0.15, 0.16, 0.17, 1.0)
        PangoCairo.show_layout(cr, layout)
