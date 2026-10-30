"""Safety gates and daily puzzle invariants, without external writes."""
import sys, unittest, json, os, tempfile
from pathlib import Path
from datetime import date,timedelta
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'daily'))
import cloud
import generate
import challenges

class CloudTests(unittest.TestCase):
    def test_unique_daily_puzzles_and_solutions(self):
        previous=set()
        for offset in range(366):
            day=(date(2026,11,1)+timedelta(days=offset)).isoformat()
            data=generate.plan(day)
            if data['family']=='color':
                generate.video.ROUNDS=data['rounds'];generate.video.validate_logic()
            else:challenges.validate(data)
            signature=json.dumps(data['rounds'],sort_keys=True)
            self.assertNotIn(signature,previous);previous.add(signature)
            self.assertEqual(data,generate.plan(day))
            self.assertFalse(data['scheduled']);self.assertFalse(data['published'])
            for r,text in zip(data['rounds'],data['answer_texts']):
                if data['family']=='color':
                    self.assertIn(r['new'],text);self.assertIn(dict(r['items'])[r['target']],text)
                else:self.assertIn('ABC'[r['correct']],text)

    def test_rotation_compares_actual_previous_episodes(self):
        history=json.loads((generate.video.ROOT/'daily/content-history.json').read_text(encoding='utf-8'))
        for n in range(40):
            data=generate.plan((date(2026,11,1)+timedelta(days=n)).isoformat(),history=history)
            self.assertNotIn(data['family'],challenges.recent_families(history,data['episode']))
            history.append(data)

    def test_changed_colors_alone_fail_the_similarity_gate(self):
        history=json.loads((generate.video.ROOT/'daily/content-history.json').read_text(encoding='utf-8'))
        with self.assertRaises(AssertionError):generate.plan('2026-11-01',history=history,requested_family='color')

    def test_repeated_puzzles_fail_even_with_a_new_date_and_choices(self):
        data=generate.plan('2026-11-01');older={**data,'episode':1}
        with self.assertRaises(AssertionError):challenges.compare(data,[older])

    def test_correction_changes_mechanic_and_requires_new_approval(self):
        data=generate.plan('2026-11-01',revision=2,rejected_family='color')
        self.assertNotEqual(data['family'],'color');self.assertEqual(data['revision'],2)
        self.assertFalse(data['scheduled']);self.assertFalse(data['published'])

    def test_owner_correction_dispatches_immediately_without_approval(self):
        tag=cloud.PREFIX+'2026-11-01-v2'
        event={'sender':{'login':cloud.OWNER},'comment':{'id':123,'html_url':'https://example.test/comment/123','user':{'login':cloud.OWNER},'body':'CORREGIR: cambia el reto repetido y vuelve a avisarme hoy.'},'issue':{'number':4,'body':f'<!-- {tag} -->'}}
        release={'tag_name':tag,'body':json.dumps({'status':'APPROVED_PENDING_TIKTOK','sha256':'1'*64,'approval_comment':'old'})}
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'event.json';path.write_text(json.dumps(event))
            with patch.dict(os.environ,{'GITHUB_EVENT_PATH':str(path)}),patch.object(cloud,'releases',return_value=[release]),patch.object(cloud,'api'),patch.object(cloud,'gh') as mutation:
                cloud.comment()
                dispatch=[c.args for c in mutation.call_args_list if c.args[0]=='workflow']
                self.assertEqual(len(dispatch),1);self.assertIn('mode=correct',dispatch[0])
                saved=json.loads(mutation.call_args_list[0].args[-1])
                self.assertEqual(saved['status'],'CORRECTION_REQUESTED')
                self.assertNotIn('approval_comment',saved)

    def test_a_handled_correction_does_not_run_twice(self):
        release={'tag_name':cloud.PREFIX+'2026-11-01-v1','body':json.dumps({'status':'SUPERSEDED'})}
        with patch.dict(os.environ,{'CORRECTION_TAG':release['tag_name']}),patch.object(cloud,'api',return_value={'private':False}),patch.object(cloud,'releases',return_value=[release]),patch.object(cloud,'gh') as mutation:
            cloud.correct();mutation.assert_not_called()

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

    def test_owner_cannot_approve_a_different_hash(self):
        tag=cloud.PREFIX+'2026-11-01-v1'
        event={'sender':{'login':cloud.OWNER},'comment':{'user':{'login':cloud.OWNER},'body':'APROBAR '+'0'*64},'issue':{'number':4,'body':f'<!-- {tag} -->'}}
        release={'tag_name':tag,'body':json.dumps({'status':'READY_FOR_REVIEW','sha256':'1'*64})}
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'event.json';path.write_text(json.dumps(event))
            with patch.dict(os.environ,{'GITHUB_EVENT_PATH':str(path)}),patch.object(cloud,'releases',return_value=[release]),patch.object(cloud,'gh') as mutation:
                cloud.comment();mutation.assert_not_called()

if __name__=='__main__':unittest.main()
