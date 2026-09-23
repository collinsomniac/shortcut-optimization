import unittest
from urllib.parse import parse_qs, urlsplit
from shortcut_url import build_url

class URLTests(unittest.TestCase):
    def test_round_trip_reserved_and_unicode(self):
        name = "SO Echo & 100%"
        payload = '{"text":"👋 & ? # = + %20"}\nsecond line'
        url = build_url(name, payload)
        parts = urlsplit(url)
        self.assertEqual(parts.scheme, "shortcuts")
        self.assertEqual(parts.netloc, "run-shortcut")
        self.assertEqual(parts.fragment, "")
        self.assertEqual(parse_qs(parts.query), {
            "name": [name], "input": ["text"], "text": [payload]
        })

    def test_empty_input_is_preserved(self):
        query = urlsplit(build_url("SO Echo", "")).query
        self.assertEqual(parse_qs(query, keep_blank_values=True)["text"], [""])

    def test_name_required(self):
        for name in ("", "  ", None):
            with self.assertRaises(ValueError):
                build_url(name, "test")

    def test_text_required(self):
        with self.assertRaises(TypeError):
            build_url("SO Echo", {"text": "not serialized"})

if __name__ == "__main__":
    unittest.main()
