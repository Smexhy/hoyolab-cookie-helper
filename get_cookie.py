import asyncio
import getpass
import os
import platform
import secrets
import shutil
import string
import subprocess
import sys
from pathlib import Path


COOKIE_FIELDS = (
    "stoken",
    "ltoken_v2",
    "ltuid_v2",
    "ltmid_v2",
    "cookie_token_v2",
    "account_mid_v2",
    "account_id_v2",
)
DEVICE_ID_CHARS = string.ascii_lowercase + string.digits


def device_id_path():
    if sys.platform == "win32":
        root = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        root = Path.home() / "Library" / "Application Support"
    else:
        root = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))

    return root / "hoyolab-cookie-helper" / "device-id"


def load_device_id(path=None):
    path = path or device_id_path()

    try:
        device_id = path.read_text(encoding="ascii").strip()
    except FileNotFoundError:
        device_id = ""

    if len(device_id) == 16 and all(char in DEVICE_ID_CHARS for char in device_id):
        return device_id

    device_id = "".join(secrets.choice(DEVICE_ID_CHARS) for _ in range(16))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(device_id, encoding="ascii")
    if os.name != "nt":
        path.chmod(0o600)
    return device_id


def build_cookie(cookies):
    missing = [field for field in COOKIE_FIELDS if not cookies.get(field)]
    if missing:
        raise RuntimeError("HoYo did not return a complete cookie")

    return "; ".join(f"{field}={cookies[field]}" for field in COOKIE_FIELDS)


def clipboard_command(system=None):
    system = system or platform.system()

    if system == "Windows":
        return ["clip"]
    if system == "Darwin":
        return ["pbcopy"]

    linux_commands = (
        ["wl-copy"],
        ["xclip", "-selection", "clipboard"],
        ["xsel", "--clipboard", "--input"],
    )
    for command in linux_commands:
        if shutil.which(command[0]):
            return command

    return None


def copy_cookie(cookie):
    command = clipboard_command()
    if not command:
        return False

    try:
        subprocess.run(command, input=cookie, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None

    return command


def clear_clipboard(command):
    try:
        subprocess.run(command, input="", text=True, check=False)
    except OSError:
        pass


async def get_cookie():
    try:
        import genshin
        from genshin.client.manager import cookie as cookie_utility
    except ImportError:
        raise RuntimeError("genshin.py is not installed; follow the install step in the README") from None

    account = input("HoYo account email or username: ").strip()
    password = getpass.getpass("HoYo account password (hidden): ")
    if not account or not password:
        raise RuntimeError("account and password cannot be empty")

    client = genshin.Client()
    result = await client.login_with_app_password(
        account,
        password,
        port=5000,
        device_id=load_device_id(),
        device_name="HoYoLAB Cookie Helper",
        device_model=platform.system(),
    )
    cookies = {key: value for key, value in result.model_dump().items() if value}
    cookies.update(await cookie_utility.fetch_cookie_with_stoken_v2(cookies, token_types=[2, 4]))
    return build_cookie(cookies)


async def main():
    print("This runs locally. Your password is hidden and is not saved.")

    while True:
        cookie = await get_cookie()
        clipboard = copy_cookie(cookie)
        if clipboard:
            print("\nComplete cookie copied to your clipboard.")
            try:
                input("Paste it into HoyoLab Auto, then press Enter here to clear the clipboard. ")
            finally:
                clear_clipboard(clipboard)
        else:
            print("\nClipboard access is unavailable. Copy this entire line:\n")
            print(cookie)

        print("Keep the cookie private; it grants access to your HoYoLAB account.")
        if input("\nGet a cookie for another HoYo account? [y/N]: ").strip().lower() != "y":
            break


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nCancelled.")
    except Exception as error:
        print(f"\nLogin failed: {error}")
        raise SystemExit(1) from None
