# screensaver-fprint

*[English](README.md) · **Deutsch***

Entsperren per Fingerabdruck am Cinnamon-Sperrbildschirm, das sagt, was es
gerade tut.

Ein Fork von
[cinnamon-screensaver](https://github.com/linuxmint/cinnamon-screensaver) mit
derselben Anzeige, die [greeter-fprint](https://github.com/SoulInfernoDE/greeter-fprint)
auf den Anmeldebildschirm bringt. Inoffiziell: nicht mit Linux Mint verbunden
und weder von Linux Mint unterstützt noch empfohlen.

![Die Anzeige in ihren Zuständen: gelb, solange der Leser wartet, rot bei einem
abgelehnten Finger, grün bei einem erkannten, danach das Passwort-Schild und ein
abgelehntes Passwort](docs/states.de.gif)

## Warum

Am normalen Cinnamon-Sperrbildschirm:

- **Ein abgelehnter Finger zeigt überhaupt nichts an.** Der Fehler des Lesers
  erreicht den Bildschirm nie; ein Fehlversuch sieht genauso aus wie ein Leser,
  der gar nicht zuhört.
- **Oder es heißt „Falsches Passwort“** – obwohl du nichts getippt hast.
- **Meldungen stapeln sich**, eine unter der anderen.

screensaver-fprint zeigt immer genau eine Meldung, mit einem kurzen Ton im Stil
von Cinnamon, wenn ein Finger erkannt oder abgelehnt wird, das Passwort gebraucht
wird oder falsch ist:

| | |
| --- | --- |
| **Gelb** | der Leser wartet |
| **Rot** | Finger nicht erkannt – nach 1,5 s wieder gelb |
| **Grün** | Finger erkannt – der Bildschirm wird entsperrt |
| **Passwort-Schild** | der Leser hat aufgegeben; gib dein Passwort ein |
| **Schild, rote Meldung** | falsches Passwort |

## Voraussetzungen

- Cinnamon und eine funktionierende Fingerabdruck-Einrichtung: `fprintd`,
  `libpam-fprintd`, ein eingelesener Finger
- [greeter-fprint](https://github.com/SoulInfernoDE/greeter-fprint) installiert –
  der Sperrbildschirm nimmt Tux, die Töne und die Übersetzungen von dort

## Installation

Nur Python, nichts zu bauen. **Sichere zuerst die Datei, die du ersetzt** – es
geht um den Sperrbildschirm:

```bash
sudo cp /usr/share/cinnamon-screensaver/unlock.py \
        /usr/share/cinnamon-screensaver/unlock.py.bak-$(date +%Y%m%d%H%M%S)

sudo install -m 644 src/fingerprintPanel.py src/fingerprintMessages.py src/unlock.py \
        /usr/share/cinnamon-screensaver/

cinnamon-screensaver-command --exit
```

Wenn sich der Sperrbildschirm danebenbenimmt: auf eine Textkonsole wechseln
(Strg+Alt+F2), die Sicherung zurückspielen und `pkill -f cinnamon-screensaver`
ausführen.

## Wie es funktioniert

| | |
| --- | --- |
| [`docs/HOW-IT-WORKS.de.md`](docs/HOW-IT-WORKS.de.md) | der Upstream-Fehler, der die Meldung des Lesers verschluckt, wie die Anzeige ihn umgeht, Sicherheit, Fehlersuche |

Auch auf Englisch verfügbar; der Link steht oben.

## Verwandt

[greeter-fprint](https://github.com/SoulInfernoDE/greeter-fprint) – dieselbe
Anzeige für den LightDM-Anmeldebildschirm.

## Für Linux Mint

Alles, was in diesem Fork neu ist, darf Linux Mint frei verwenden, anpassen und
neu lizenzieren – ohne zu fragen und ohne Namensnennung, allen voran die
Korrektur für `PAM_ERROR_MSG`. Den genauen Umfang beschreibt
[COPYRIGHT.md](COPYRIGHT.md) (englisch).

## Lizenz

GPL-2+ wie cinnamon-screensaver – siehe [COPYING](COPYING) und
[COPYRIGHT.md](COPYRIGHT.md). Tux ist das Linux-Maskottchen von Larry Ewing; das
Linux-Mint-Logo liegt nicht in diesem Repository, sondern wird zur Laufzeit vom
System geladen. Die ursprüngliche README von cinnamon-screensaver:
[README.cinnamon-screensaver.md](README.cinnamon-screensaver.md).
