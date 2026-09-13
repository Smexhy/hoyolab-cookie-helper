# HoYoLAB cookie helper

This small script gets the complete HoYoLAB cookie needed for automatic cookie
refresh in tools such as [HoyoLab Auto](https://github.com/torikushiii/hoyolab-auto).
It includes `stoken`, which is normally missing when you copy cookies from a
browser.

The script runs on your own computer. Your password is hidden while you type and
is not saved. A random device ID is saved locally so later logins appear to come
from the same device; this can reduce repeated email checks, but HoYo may still
ask for one.

## Download

1. Click the **Code** button above, then **Download ZIP**.
2. Extract the ZIP and open the extracted folder.

## Run it

Python 3.9 or newer is required. The launchers create an isolated environment,
install the pinned dependency, and start the helper.

### Windows

Double-click `run-windows.bat` in the extracted folder.

If it says Python was not found, install the official
[Python Install Manager](https://www.python.org/downloads/), close the launcher,
and double-click it again.

### macOS

1. Open Terminal.
2. Type `cd `, including the space.
3. Drag the extracted folder onto the Terminal window and press Enter.
4. Paste this command and press Enter:

```bash
sh run-macos-linux.sh
```

If it says Python was not found, install the latest supported
[macOS installer](https://www.python.org/downloads/macos/), reopen Terminal, and
run the command again.

### Linux

1. Right-click the extracted folder and choose **Open in Terminal**.
2. Paste this command and press Enter:

```bash
sh run-macos-linux.sh
```

If Python is missing on Ubuntu or Debian, run
`sudo apt install python3 python3-venv`, then run the launcher again. Other Linux
distributions provide Python 3 through their normal package manager.

Enter your HoYo account email or username, then your password. The password will
not appear while you type. A browser window may open for a captcha, and HoYo may
send an email verification code.

When login succeeds, the complete cookie is copied to your clipboard. Keep the
helper open while you add it to HoyoLab Auto using the steps below.

Run this on your desktop, not inside Docker or Portainer. The login may need to
open a browser on the same computer.

## Add it to HoyoLab Auto

1. Open the `config.json5` file used by HoyoLab Auto.
2. Find the same `cookie:` line where you previously pasted the old browser
   cookie for the login you just used.
3. Replace only that cookie value with the complete cookie. Keep the surrounding
   quotes and keep the cookie on one line:

```json5
cookie: 'paste the complete cookie here',
```

4. Optionally add a comment after the entry so you recognize it later:

```json5
cookie: 'paste the complete cookie here', // main account
```

5. Save `config.json5` and restart HoyoLab Auto or its container.
6. Return to this helper and press Enter. It will clear the cookie from your
   clipboard.

For a new setup with no existing cookie to search, paste it into the game entry
you want to use for that login.

If the same HoYoLAB login is used for several games, replace its cookie in any
one of those game entries. HoyoLab Auto recognizes the shared account from the
cookie and refreshes all of them. You do not need to inspect any account IDs.
Run the helper once for each different HoYoLAB login.

For Docker Compose, edit the `config.json5` file on the host, normally beside
`docker-compose.yml`. Do not edit the read-only copy inside the container. A
Portainer stack must likewise mount the edited file at `/app/config.json5`.

## Security and privacy

This is an unofficial community tool. It runs on your computer and does not send
your password to this repository or to HoyoLab Auto. The password is passed to
the open-source [`genshin.py`](https://github.com/seriaati/genshin.py) library,
which encrypts it and sends the login request over HTTPS to HoYoverse. If a
captcha is required, its temporary page is available only on your computer.

The helper does not write your email, username, password, or cookie to its files.
It saves only a random 16-character device ID in your user configuration folder.
Delete the `hoyolab-cookie-helper` configuration folder if you want a new device
ID; HoYo will probably ask for email verification again on the next login.

Treat the cookie like a password. Anyone who gets it may be able to use your
HoYoLAB session until it is revoked. Never paste it into a GitHub issue, Discord
message, or screenshot, and run the helper only on a computer you trust. Do not
commit or upload your `config.json5` file because it contains the same cookies.

The helper clears the cookie from your clipboard after you return and press
Enter. If you close it before then, clear the clipboard yourself. If clipboard
access is unavailable, the cookie is shown in the terminal instead and may
remain in its scrollback.

The launcher installs `genshin.py` and its dependencies from PyPI. Version
1.7.30 of `genshin.py` is pinned in `requirements.txt`; its dependencies may
still receive compatible updates.
