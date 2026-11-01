import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'daily'))
import music


class MusicTests(unittest.TestCase):
    def test_music_rises_only_in_long_pauses_and_never_covers_speech(self):
        speech=[{'start':.25,'duration':2.24},{'start':3.1,'duration':2.624},
                {'start':6.15,'duration':.92},{'start':14.15,'duration':1.43}]
        gaps=music.pause_windows(speech,20)
        self.assertIn((7.32,13.95),gaps)
        for a,b in gaps:
            self.assertGreaterEqual(b-a,1)
            for s in speech:
                self.assertTrue(b<=s['start'] or a>=s['start']+s['duration'])
        data,_=music.checked_license()
        expr=music.volume_expression(data,gaps)
        self.assertIn('0.036904266',expr)

    def test_actual_music_matches_license_and_required_credit(self):
        data, track = music.checked_license()
        self.assertEqual(music.digest(track), data['sha256'])
        self.assertIn('Kevin MacLeod', data['attribution'])
        self.assertIn(data['license_url'], data['attribution'])

    def test_changed_track_stops_before_encoding(self):
        with patch.object(music, 'digest', return_value='0'*64):
            with self.assertRaises(ValueError):
                music.checked_license()

    def test_wrong_video_hash_stops_before_encoding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'video.mp4').write_bytes(b'changed')
            (root/'verificacion-final.json').write_text(json.dumps({
                'status': 'PASS_PENDING_USER_APPROVAL', 'sha256': '0'*64}))
            with patch.object(music.subprocess, 'run') as run:
                with self.assertRaises(ValueError):
                    music.mix(root)
                run.assert_not_called()

    def test_double_mix_stops_before_encoding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'verificacion-final.json').write_text('{"music_embedded":true}')
            with patch.object(music.subprocess, 'run') as run:
                with self.assertRaises(ValueError):
                    music.mix(root)
                run.assert_not_called()
