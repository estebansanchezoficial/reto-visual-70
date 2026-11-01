import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'daily'))
import music


class MusicTests(unittest.TestCase):
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
