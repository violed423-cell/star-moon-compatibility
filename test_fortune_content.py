"""Presentation regression tests. Birth-engine calls are explicitly test doubles.

Run the existing calendar tests separately with the real pyswisseph dependency.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from xml.etree import ElementTree
import re
import unittest
from unittest.mock import patch

import fortune_content as content
import fortune_ui
import public_app
from compatibility_v1_6 import CHAR_BY_ID, calculate_compatibility
from independent_12_animal_diagnosis_v1_3 import CHARACTERS
from love_type_16_v1_4 import QUESTIONS, TYPES
from test_public_app import call


def fixture(character):
    return SimpleNamespace(character_id=character.id, character_name=character.name,
                           element=character.element, keywords=character.keywords,
                           warnings=(), love_code='0000')


class PresentationTests(unittest.TestCase):
    def setUp(self):
        self.form = {'date_a': '2000-01-07', 'date_b': '2001-03-21', 'consent': 'yes', 'mode': 'free'}
        self.a, self.b = fixture(CHARACTERS[0]), fixture(CHARACTERS[2])
        self.engine = patch.object(content, 'diagnose', side_effect=lambda date, time: self.a if date == self.form['date_a'] else self.b)
        self.engine.start()
        self.environment = patch.dict('os.environ', {'COCONALA_PRODUCT_URL': ''})
        self.environment.start()
        self.addCleanup(self.engine.stop)
        self.addCleanup(self.environment.stop)

    def test_all_twelve_explicit_artwork_names_and_bounds(self):
        self.assertEqual(set(content.ARTWORK), set(CHAR_BY_ID))
        self.assertEqual(set(content.PERSONALITY), set(CHAR_BY_ID))
        for ident, (name, (x, y, w, h)) in content.ARTWORK.items():
            self.assertEqual(name, CHAR_BY_ID[ident].name)
            self.assertTrue(0 <= x < x + w <= 1312 and 0 <= y < y + h <= 1199)
            html = fortune_ui.character_portrait(ident, True)
            self.assertIn(f'aria-label="{name}"', html)
            self.assertIn(f'viewBox="{x} {y} {w} {h}"', html)
        self.assertEqual(CHAR_BY_ID['star_squirrel'].element, '火')
        self.assertEqual(content.ARTWORK['stardew_rabbit'][0], '星雫の月兎')

    def test_144_scores_match_existing_engine_and_pair_reversal(self):
        explanations = set()
        for ca in CHARACTERS:
            for cb in CHARACTERS:
                a, b = fixture(ca), fixture(cb)
                with patch.object(content, 'diagnose', side_effect=[a, b, b, a]):
                    forward = content.read_birth_pair('a', 'b')
                    reverse = content.read_birth_pair('b', 'a')
                self.assertEqual(forward.score, calculate_compatibility(a, b).character_score)
                self.assertEqual(forward.score, reverse.score)
                self.assertEqual(forward.explanation, reverse.explanation)
                self.assertIn(ca.name, forward.explanation)
                self.assertIn(cb.name, forward.explanation)
                explanations.add(forward.explanation)
        self.assertEqual(len(explanations), 78)

    def test_portrait_clips_source_roi_and_preserves_aspect_ratio(self):
        for ident, (_, (x, y, width, height)) in content.ARTWORK.items():
            svg = ElementTree.fromstring(fortune_ui.character_portrait(ident, True, 'a'))
            self.assertEqual(svg.attrib['viewBox'], f'{x} {y} {width} {height}')
            self.assertEqual(svg.attrib['preserveAspectRatio'], 'xMidYMid meet')
            clip = svg.find('./defs/clipPath')
            self.assertIsNotNone(clip)
            self.assertEqual(clip.attrib['clipPathUnits'], 'userSpaceOnUse')
            self.assertEqual(clip.find('rect').attrib, {
                'x': str(x), 'y': str(y), 'width': str(width), 'height': str(height)})
            image = svg.find('image')
            self.assertEqual(image.attrib['clip-path'], f'url(#{clip.attrib["id"]})')
            self.assertEqual(image.attrib['width'], '1312')
            self.assertEqual(image.attrib['height'], '1199')
            self.assertEqual(image.attrib['href'], content.ARTWORK_URL)

    def test_same_character_cards_have_distinct_stable_clip_ids(self):
        self.b = self.a
        with patch.object(content, 'artwork_bytes', return_value=b'verified test double'):
            _, first = call('/diagnose', 'POST', self.form)
            _, second = call('/diagnose', 'POST', self.form)
        self.assertEqual(first, second)
        ids = re.findall(rb'<clipPath id="([^"]+)"', first)
        self.assertEqual(len(ids), 2)
        self.assertEqual(len(set(ids)), 2)
        references = re.findall(rb'clip-path="url\(#([^\)]+)\)"', first)
        self.assertEqual(references, ids)

    def test_no_answers_partial_and_ties_do_not_invent_answers(self):
        empty = content.read_self_answers({})
        self.assertEqual((empty.answered_count, empty.statements, empty.complete_type), (0, (), None))
        with patch.object(content, 'diagnose_answers', side_effect=AssertionError('partial input must not classify')):
            result = content.read_self_answers({'q1': 'B', 'q4': 'A'})
            self.assertEqual(result.answered_count, 2)
            self.assertEqual(len(result.statements), 2)
            self.assertIn('相手の様子を見ながら', result.statements[0])
            self.assertFalse(any('恋のペース' in s for s in result.statements))
            tie = content.read_self_answers({'q1': 'A', 'q2': 'B'})
            self.assertIn('同じくらい', tie.statements[0])
        with self.assertRaises(ValueError):
            content.read_self_answers({'q1': 'X'})

    def test_complete_answers_all_sixteen_types_and_corrected_copy(self):
        for code in TYPES:
            answers = {q.id: 'A' if code[q.axis] == '0' else 'B' for q in QUESTIONS}
            result = content.read_self_answers(answers)
            self.assertEqual(result.answered_count, 12)
            self.assertEqual(result.complete_type.code, code)
        self.assertIn('新しい体験', TYPES['0010'].tagline)
        self.assertIn('行動', TYPES['1100'].tagline)
        self.assertIn('行動', TYPES['1101'].tagline)

    def test_percentage_placement_optional_and_partner_ignored(self):
        _, base = call('/diagnose', 'POST', self.form)
        for additions in ({'include_self': 'yes'}, {'include_self': 'yes', 'a_q1': 'A'},
                          {'include_self': 'yes', **{f'a_q{i}': 'B' for i in range(1, 13)}}):
            r, html = call('/diagnose', 'POST', dict(self.form, **additions))
            self.assertEqual(r['status'], '200 OK')
            self.assertIn(b'data-score="95"', html)
        r, html = call('/diagnose', 'POST', dict(self.form, include_self='yes', a_q1='A'))
        self.assertIn('回答した1問だけ'.encode(), html)
        self.assertIn('お相手の恋愛タイプは未診断'.encode(), html)
        self.assertNotIn('恋のペース：'.encode(), html)
        self.assertLess(html.index(b'<small>%</small>'), html.index(b'<p class="pair-explanation"'))
        self.assertLess(html.index(b'<p class="pair-explanation"'), html.index(b'<div class="cols character-grid"'))
        self.assertLess(html.index(b'class="panel relationship-tips"'), html.index(b'class="panel premium-cta"'))
        _, ignored = call('/diagnose', 'POST', dict(self.form, a_q1='INVALID', b_q1='A', b_q2='B'))
        self.assertEqual(base, ignored)

    def test_missing_invalid_and_untrusted_input(self):
        for missing in ('date_a', 'date_b', 'consent'):
            r, _ = call('/diagnose', 'POST', {k: v for k, v in self.form.items() if k != missing})
            self.assertEqual(r['status'], '400 Bad Request')
        for wrong in ('2001-02-29', '2000-13-01', '1899-01-01', '2999-01-01', '20000107', '<script>'):
            r, _ = call('/diagnose', 'POST', dict(self.form, date_a=wrong))
            self.assertEqual(r['status'], '400 Bad Request', wrong)
        for wrong in ('25:00', '12:99', '<script>'):
            r, _ = call('/diagnose', 'POST', dict(self.form, time_a=wrong))
            self.assertEqual(r['status'], '400 Bad Request')
        r, html = call('/diagnose', 'POST', dict(self.form, include_self='yes', a_q1='<script>'))
        self.assertEqual(r['status'], '400 Bad Request')
        self.assertNotIn(b'<script>', html)

    def test_images_missing_corrupt_and_unknown_mapping_fail_closed(self):
        with TemporaryDirectory() as d, patch.object(content, 'ARTWORK_PATH', Path(d) / 'missing.jpeg'):
            self.assertIsNone(content.artwork_bytes())
            r, _ = call(content.ARTWORK_URL)
            self.assertEqual(r['status'], '404 Not Found')
            r, html = call('/diagnose', 'POST', self.form)
            self.assertEqual(r['status'], '200 OK')
            self.assertIn('画像は準備中'.encode(), html)
            self.assertNotIn(b'<image href=', html)
            content.ARTWORK_PATH.write_bytes(b'x' * 840342)
            self.assertIsNone(content.artwork_bytes())
        self.assertIn('画像は準備中', fortune_ui.character_portrait('unknown', True))
        with patch.dict(content.ARTWORK, {'moonlight_fox': ('WRONG', (1, 2, 3, 4))}):
            self.assertIn('画像は準備中', fortune_ui.character_portrait('moonlight_fox', True))

    def test_approved_artwork_asset_is_served_without_modification(self):
        data = content.artwork_bytes()
        self.assertIsNotNone(data, 'The approved source artwork must be packaged with the site')
        self.assertEqual(len(data), 840342)
        self.assertEqual(content.sha256(data).hexdigest(), content.ARTWORK_SHA256)
        response, body = call(content.ARTWORK_URL)
        self.assertEqual(response['status'], '200 OK')
        self.assertEqual(response['headers']['Content-Type'], 'image/jpeg')
        self.assertEqual(body, data)
        response, html = call('/diagnose', 'POST', self.form)
        self.assertEqual(response['status'], '200 OK')
        self.assertEqual(html.count(b'<image href="/assets/characters-source.jpeg"'), 2)
        self.assertNotIn('画像は準備中'.encode(), html)

    def test_purchase_links_stay_on_hold_even_with_a_valid_configured_url(self):
        # URLs are synthetic test inputs. No listing is asserted to be published.
        for configured in ('', 'https://coconala.com/services/1234567',
                           'https://coconala.com/services/1234567/',
                           'http://coconala.com/services/123', 'https://evil.test/services/123',
                           'https://coconala.com.evil.test/services/123',
                           'https://coconala.com@evil.test/services/123',
                           'https://coconala.com/services/123?birth=2000-01-01',
                           'https://[', 'javascript:alert(1)'):
            with patch.dict('os.environ', {'COCONALA_PRODUCT_URL': configured}):
                self.assertIsNone(content.coconala_product_url())
                html = fortune_ui.premium_cta()
                self.assertIn('鑑定書は準備中です', html)
                self.assertIn('販売・購入のご案内は現在行っていません', html)
                self.assertNotIn('premium-button', html)
                self.assertNotIn('<a ', html)
                self.assertNotIn('href=', html)
                self.assertNotIn('1,480', html)
                self.assertNotIn('レポート', html)
                for route in ('/', '/premium', '/commercial', '/both'):
                    response, body = call(route)
                    self.assertEqual(response['status'], '403 Forbidden' if route == '/both' else '200 OK')
                    self.assertNotIn(b'href="https://coconala.com', body)
                    self.assertNotIn(b'class="button premium-button"', body)
                    if configured:
                        self.assertNotIn(configured.encode(), body)
                response, body = call('/diagnose', 'POST', self.form)
                self.assertEqual(response['status'], '200 OK')
                self.assertNotIn(b'href="https://coconala.com', body)
                self.assertNotIn(b'class="button premium-button"', body)
                self.assertIn('鑑定書は準備中です'.encode(), body)
        # The public full-questionnaire endpoint remains gated, independent of URL state.
        response, _ = call('/diagnose', 'POST', dict(self.form, mode='both', paid='true', entitled='yes'))
        self.assertEqual(response['status'], '403 Forbidden')

    def test_repeated_submissions_and_fresh_form(self):
        _, first = call('/diagnose', 'POST', self.form)
        _, second = call('/diagnose', 'POST', self.form)
        self.assertEqual(first, second)
        _, initial = call('/')
        self.assertNotIn(b'2000-01-07', initial)
        self.assertNotIn(b'value="yes" checked', initial)
        self.assertNotIn(b'name="b_q1"', initial)
        self.assertIn('答えたい質問だけ'.encode(), initial)
        r, html = call('/privacy')
        self.assertIn(b'violed423@gmail.com', html)


if __name__ == '__main__':
    unittest.main()
