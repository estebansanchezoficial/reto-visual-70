import sys,unittest
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'daily'))
import publish
import buffer_api

class BufferTests(unittest.TestCase):
    def record(self):
        return dict(status='APPROVED_PENDING_TIKTOK',date='2030-01-01',sha256='1'*64,music_embedded=True,approval_comment='https://github.com/example/comment-1',scheduled=False,published=False)

    def test_no_unapproved_or_already_attempted_version_can_be_sent(self):
        for state in ['READY_FOR_REVIEW','SUPERSEDED','BUFFER_RESERVED','SCHEDULED_VERIFIED_BUFFER','BUFFER_NEEDS_RECONCILIATION']:
            record=self.record();record['status']=state
            with self.assertRaises(ValueError):publish.validate(record)

    def test_only_final_music_mix_with_approval_is_eligible(self):
        for field,value in [('sha256','bad'),('approval_comment',None),('music_embedded',False),('scheduled',True),('published',True)]:
            record=self.record();record[field]=value
            with self.assertRaises(ValueError):publish.validate(record)

    def test_cdmx_19_is_next_day_01_utc_and_past_dates_stop(self):
        self.assertEqual(publish.validate(self.record(),datetime(2029,1,1,tzinfo=timezone.utc)),'2030-01-02T01:00:00Z')
        with self.assertRaises(ValueError):publish.validate(self.record(),datetime(2030,1,2,1,tzinfo=timezone.utc))

    def request(self,draft=False):
        return publish.payload('Cipher — Kevin MacLeod https://creativecommons.org/licenses/by/4.0/',f'https://github.com/{publish.cloud.REPO}/releases/download/rv70-publish-'+'1'*64+'/video.mp4','2030-01-02T01:00:00Z',draft)

    def test_ai_exact_channel_and_custom_time_are_mandatory(self):
        request=self.request()
        self.assertTrue(request['metadata']['tiktok']['isAiGenerated'])
        self.assertEqual(request['channelId'],buffer_api.CHANNEL_ID)
        self.assertEqual(request['mode'],'customScheduled')
        self.assertFalse(request['saveToDraft'])
        self.assertEqual(request['schedulingType'],'automatic')

    def test_transport_test_can_only_be_a_draft(self):
        request=self.request(True)
        self.assertTrue(request['saveToDraft']);self.assertNotIn('dueAt',request)
        post=dict(channelId=buffer_api.CHANNEL_ID,text=request['text'],metadata={'isAiGenerated':True},schedulingType='automatic',status='scheduled')
        with self.assertRaises(ValueError):publish.verify_post(post,request,draft=True)

    def test_lost_ai_or_different_time_fails_readback(self):
        request=self.request()
        good=dict(channelId=buffer_api.CHANNEL_ID,text=request['text'],metadata={'isAiGenerated':True},schedulingType='automatic',status='scheduled',dueAt=request['dueAt'])
        publish.verify_post(good,request)
        for changes in [{'metadata':{'isAiGenerated':False}},{'dueAt':'2030-01-02T02:00:00Z'},{'channelId':'other'},{'status':'draft'}]:
            with self.assertRaises(ValueError):publish.verify_post({**good,**changes},request)

    def test_private_or_unrelated_media_and_missing_credit_stop(self):
        for url in ['https://example.com/video.mp4','https://github.com/example/repo/releases/download/a/video.mp4']:
            with self.assertRaises(ValueError):publish.payload('Cipher Kevin MacLeod https://creativecommons.org/licenses/by/4.0/',url,None)
        with self.assertRaises(ValueError):publish.payload('missing credit',self.request()['assets'][0]['video']['url'],None)
