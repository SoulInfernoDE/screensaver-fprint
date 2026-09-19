# Wie es funktioniert

*[English](HOW-IT-WORKS.md) · **Deutsch***

## Was sich ändert

Upstream leitet die Meldungen von `pam_fprintd` in `authinfo_label`, eine Zeile
unter die andere. Meldungen des Lesers gehen jetzt stattdessen an die Anzeige;
alles andere erreicht das ursprüngliche Label unverändert.

Damit verschwinden drei Fehler:

- `on_authentication_failure()` meldete „Falsches Passwort“, auch wenn nichts
  getippt war. Ein abgelehnter Finger wird jetzt als solcher gemeldet; ein
  abgelehntes Passwort meldet weiter, was es immer gemeldet hat.
- `on_authentication_success()` lässt es grün aufleuchten und entsperrt, sobald
  das zu sehen war, statt unter dem Aufleuchten weg zu entsperren.
- Kommt eine Passwortabfrage, nachdem der Leser gesprochen hat, hat
  `pam_fprintd` seine Versuche aufgebraucht. Genau das gibt Tux das Schild in
  die Hand – gesteuert von PAM, nicht durch Zählen von Versuchen.

## Der Upstream-Fehler, den das umgeht

`cinnamon-screensaver-pam-helper.c` verwirft `PAM_ERROR_MSG`, ohne es
weiterzugeben:

```c
case CS_AUTH_MESSAGE_ERROR_MSG:
    DEBUG ("CS_AUTH_MESSAGE_ERROR_MSG\n");
    break;
```

Genau so meldet `pam_fprintd` „Failed to match fingerprint“ – ein abgelehnter
Finger kommt am Bildschirm also als gar nichts an. Das betrifft die Fehlertexte
jedes PAM-Moduls an diesem Sperrbildschirm, nicht nur die des Lesers.

Statt ein Authentifizierungs-Hilfsprogramm mit setuid-root zu verändern,
erschließt dieser Fork die Ablehnung aus dem, was ankommt: Der Leser macht sich
wieder bereit, indem er seine gewöhnliche Aufforderung erneut schickt, und das
tut er nur, nachdem er etwas abgelehnt hat. Diese Schlussfolgerung hängt an
einem ausdrücklichen Schalter, `rearm_means_failure`, der nur hier gesetzt ist –
der Anmeldebildschirm bekommt die echte Meldung und braucht ihn nicht.

## Töne

Die Anzeige spielt die drei Töne von greeter-fprint: einen steigenden Dreiklang,
wenn der Finger erkannt wird, eine sanft fallende Terz, wenn nicht, einen
neutralen Doppelton, wenn das Passwort gebraucht wird. Ein falsches Passwort
bekommt denselben Ton wie ein abgelehnter Finger – abgelehnt ist abgelehnt –, und
das Schild, das nach dem roten Aufblitzen zurückkommt, bleibt still. Das Warten
bleibt still. Die Töne folgen dem, was angezeigt wird; ein
Zustand, der hinter einem Aufblitzen wartet, ist also zusammen mit seiner Farbe
zu hören.

Ob sie spielen, folgt Cinnamons eigener Regel aus `soundManager.js`: Ein
Ereignis ist nur zu hören, wenn sein `-enabled`-Schlüssel an ist. Cinnamon hat
keinen Schlüssel für den Fingerabdruck, und ein eigenes Schema müsste mit root
installiert werden. Deshalb folgen die Töne **Klang → Benachrichtigungen
anzeigen** (`org.cinnamon.sounds notification-enabled`) – dem, was Cinnamon am
ehesten für „das System teilt dir etwas mit“ hat. Schaltest du das ab, bleibt
auch der Sperrbildschirm still.

Die Dateien werden aus `/usr/share/greeter-fprint/sounds/` geladen, wo
greeter-fprint sie installiert. Abgespielt wird über GSound, abgesichert wie
alles andere in der Anzeige: Schlägt es fehl, bleibt der Sperrbildschirm still
und meldet das auf stderr.

## Sicherheit

Jeder Einstieg in die Anzeige ist abgesichert. Das hier ist eine Ergänzung zu
einem Anmeldedialog: Eine Anzeige, die sich nicht aktualisiert, ist ein
Schönheitsfehler, ein abstürzender Sperrbildschirm nicht. Fehler gehen mit
`traceback.format_exc()` direkt nach stderr; das umgeht auch den eigenen
`sys.excepthook` von cinnamon-screensaver, der beim Ausgeben scheitert und im
Journal nur `Original exception was:` hinterlässt.

## Grafik und Übersetzungen

Beides kommt von greeter-fprint, statt doppelt vorzuliegen. Tux wird aus
`/usr/share/greeter-fprint/tux-fprint.svg` geladen und jeder Text aus dem
gettext-Katalog dieses Projekts, mit Englisch als Basis und Rückfall – siehe
dessen [Hinweise zu Übersetzungen](https://github.com/SoulInfernoDE/greeter-fprint/blob/main/docs/TRANSLATIONS.de.md).

Der Katalog ist als `_p()` eingebunden, nicht als `_`: cinnamon-screensaver legt
sein eigenes `_` in die Builtins, und es zu überdecken, würde den Rest des
Dialogs stillschweigend unübersetzt lassen.

Anders als am Anmeldebildschirm können die Meldungen des Lesers hier schon auf
Deutsch ankommen, weil dieser Prozess `setlocale()` aufruft. Sie werden deshalb
auf Englisch und auf Deutsch *erkannt* – angezeigt wird aber immer, was der
Katalog liefert.

## Fehlersuche

```bash
cinnamon-screensaver-command --exit
CS_FPRINT_DEBUG=1 cinnamon-screensaver --debug
```

Gibt jede Meldung aus, die der Dialog empfängt. Beende vorher die laufende
Instanz, sonst bekommt die neue den D-Bus-Namen nicht und beendet sich sofort.

## Die Animation

Mit dem eigenen Zeichencode der Anzeige gerendert, die Zeiten sind also die
echten: Jedes Aufleuchten hält 1,5 s. Standbilder der wichtigsten Zustände:

![Die wichtigsten Zustände der Anzeige](panel.png)
