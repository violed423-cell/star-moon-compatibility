"""Original decorative design preserves the diagnosis and form contract."""
from html.parser import HTMLParser
from xml.etree import ElementTree
import unittest

import fortune_ornaments as ornaments
import fortune_ui
from test_public_app import call


class Controls(HTMLParser):
    def __init__(self):
        super().__init__()
        self.controls = []

    def handle_starttag(self, tag, attrs):
        if tag in ('form', 'input', 'button', 'a'):
            self.controls.append((tag, tuple(attrs)))


class OrnateDesignTests(unittest.TestCase):
    def test_shared_palette_and_original_vector_only(self):
        self.assertEqual(ornaments.PALETTE['gold_shadow'], '#9C702F')
        self.assertEqual(ornaments.PALETTE['gold'], '#BE984D')
        self.assertEqual(ornaments.PALETTE['gold_light'], '#F3DE9C')
        for markup in (ornaments.FRAME, ornaments.celestial_moon()):
            tree = ElementTree.fromstring(markup)
            self.assertEqual(tree.attrib['aria-hidden'], 'true')
            self.assertFalse(tree.findall('.//image'))
            self.assertFalse(tree.findall('.//script'))
            self.assertFalse(tree.findall('.//a'))
            self.assertFalse(any('id' in el.attrib for el in tree.iter()))
            self.assertNotIn('http', markup)
        moon = ElementTree.fromstring(ornaments.celestial_moon())
        self.assertEqual(moon.attrib['focusable'], 'false')
        self.assertEqual(len(moon.find("g[@class='celestial-lines']").findall('path')), 36)
        self.assertIsNotNone(moon.find("path[@class='moon-face']"))

    def test_decoration_is_idempotent_and_preserves_all_controls(self):
        body = fortune_ui.free_form()
        decorated = ornaments.decorate_body(body)
        self.assertEqual(decorated, ornaments.decorate_body(decorated))
        before, after = Controls(), Controls()
        before.feed(body)
        after.feed(decorated)
        self.assertEqual(before.controls, after.controls)
        self.assertEqual(decorated.count('data-ornate="true"'), 2)
        self.assertEqual(decorated.count('class="gilded-crest"'), 2)
        self.assertIn('pointer-events:none', ornaments.STYLE)
        self.assertIn('@media(max-width:650px)', ornaments.STYLE)
        self.assertIn('@media(max-width:360px)', ornaments.STYLE)

    def test_free_routes_show_new_design_without_changing_input_contract(self):
        for route in ('/', '/free', '/birth', '/self'):
            response, html = call(route)
            self.assertEqual(response['status'], '200 OK')
            self.assertIn(b'celestial-moon', html)
            self.assertIn(b'data-ornate="true"', html)
            self.assertIn(b'name="mode" value="free"', html)
            self.assertNotIn(b'name="include_self" value="yes" checked', html)
            self.assertNotIn(b'name="b_q1"', html)
            self.assertIn(b'name="consent" value="yes" required', html)
        response, html = call('/privacy')
        self.assertEqual(response['status'], '200 OK')
        self.assertIn('星と月 運営'.encode(), html)
        self.assertNotIn(b'mailto:', html)
        self.assertIn(b"form-action 'self'", response['headers']['Content-Security-Policy'].encode())


if __name__ == '__main__':
    unittest.main()
