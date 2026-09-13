import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import get_cookie


class CookieTests(unittest.TestCase):
    def test_build_cookie_keeps_required_fields_in_order(self):
        values = {field: f"value-{index}" for index, field in enumerate(get_cookie.COOKIE_FIELDS)}

        cookie = get_cookie.build_cookie(values)

        self.assertEqual(cookie.split("; "), [f"{field}={values[field]}" for field in get_cookie.COOKIE_FIELDS])

    def test_build_cookie_rejects_missing_fields(self):
        with self.assertRaises(RuntimeError):
            get_cookie.build_cookie({"stoken": "value"})


class LoginTests(unittest.TestCase):
    def test_login_completes_the_app_cookie(self):
        app_fields = {
            field: f"value-{field}"
            for field in get_cookie.COOKIE_FIELDS
            if field not in {"ltoken_v2", "cookie_token_v2"}
        }
        result = mock.Mock()
        result.model_dump.return_value = app_fields
        client = mock.Mock()
        client.login_with_app_password = mock.AsyncMock(return_value=result)
        refreshed = {
            "ltoken_v2": "value-ltoken_v2",
            "cookie_token_v2": "value-cookie_token_v2",
        }

        with mock.patch("genshin.Client", return_value=client):
            refresh_patch = mock.patch(
                "genshin.client.manager.cookie.fetch_cookie_with_stoken_v2",
                new=mock.AsyncMock(return_value=refreshed),
            )
            with refresh_patch as refresh:
                with mock.patch("builtins.input", return_value="user@example.com"), \
                    mock.patch("getpass.getpass", return_value="secret"), \
                    mock.patch("get_cookie.load_device_id", return_value="abcdefghijklmnop"):
                    cookie = asyncio.run(get_cookie.get_cookie())

        self.assertIn("stoken=value-stoken", cookie)
        self.assertIn("cookie_token_v2=value-cookie_token_v2", cookie)
        refresh.assert_awaited_once()


class DeviceIdTests(unittest.TestCase):
    def test_device_id_is_reused(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "device-id"

            first = get_cookie.load_device_id(path)
            second = get_cookie.load_device_id(path)

        self.assertEqual(first, second)
        self.assertEqual(len(first), 16)
        self.assertTrue(all(char in get_cookie.DEVICE_ID_CHARS for char in first))


class ClipboardTests(unittest.TestCase):
    def test_windows_uses_clip(self):
        self.assertEqual(get_cookie.clipboard_command("Windows"), ["clip"])

    def test_macos_uses_pbcopy(self):
        self.assertEqual(get_cookie.clipboard_command("Darwin"), ["pbcopy"])

    @mock.patch("get_cookie.shutil.which", return_value=None)
    def test_linux_without_clipboard_tool_falls_back_to_output(self, _which):
        self.assertIsNone(get_cookie.clipboard_command("Linux"))


if __name__ == "__main__":
    unittest.main()
