"""Safety gates and daily puzzle invariants, without external writes."""
import sys, unittest, json, os, tempfile
from pathlib import Path
from datetime import date,timedelta
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'daily'))
import cloud
import generate

class CloudTests(unittest.TestCase):
    def test_unique_daily_puzzles_and_solutions(self):
        previous=set()
        for offset in range(366):
            day=(date(2026,11,1)+timedelta(days=offset)).isoformat()
            data=generate.plan(day)
            generate.video.ROUNDS=data['rounds'];generate.video.validate_logic()
            signature=json.dumps(data['rounds'],sort_keys=True)
            self.assertNotIn(signature,previous);previous.add(signature)
            self.assertEqual(data,generate.plan(day))
            self.assertFalse(data['scheduled']);self.assertFalse(data['published'])
            for r,text in zip(data['rounds'],data['answer_texts']):
                self.assertIn(r['new'],text);self.assertIn(dict(r['items'])[r['target']],text)

    def test_protected_dates(self):
        with self.assertRaises(AssertionError):generate.plan('2026-10-31')

    def test_pending_package_blocks_generation_and_retries(self):
        for status in ['PREPARING','READY_FOR_REVIEW','FAILED_NEEDS_REVIEW','APPROVED_PENDING_TIKTOK','CORRECTION_REQUESTED']:
            with patch.object(cloud,'api',return_value={'private':False}),patch.object(cloud,'releases',return_value=[{'body':json.dumps({'status':status})}]),patch.object(cloud,'gh') as mutation:
                cloud.prepare();mutation.assert_not_called()

    def test_private_repo_stops_before_any_generation(self):
        with patch.object(cloud,'api',return_value={'private':True}),patch.object(cloud,'gh') as mutation:
            with self.assertRaises(AssertionError):cloud.prepare()
            mutation.assert_not_called()

    def test_repair_cannot_replace_an_uploaded_video(self):
        reserved={'tag_name':cloud.PREFIX+cloud.target_date()+'-v1','body':json.dumps({'status':'FAILED_NEEDS_REVIEW'}),'assets':[{'name':'video.mp4'}]}
        with patch.object(cloud,'api',return_value={'private':False}),patch.object(cloud,'releases',return_value=[reserved]),patch.object(cloud,'gh') as mutation:
            with self.assertRaises(AssertionError):cloud.prepare(repair=True)
            mutation.assert_not_called()

    def test_non_owner_comment_has_no_effect(self):
        with tempfile.TemporaryDirectory() as tmp:
            event=Path(tmp)/'event.json';event.write_text(json.dumps({'sender':{'login':'someone-else'}}))
            with patch.dict(os.environ,{'GITHUB_EVENT_PATH':str(event)}),patch.object(cloud,'gh') as mutation:
                cloud.comment();mutation.assert_not_called()

if __name__=='__main__':unittest.main()
