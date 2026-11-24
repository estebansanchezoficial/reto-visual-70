"""Readiness checks are read-only and fail closed on absent or incomplete QA."""
import sys,json,unittest,os,re,subprocess,tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'daily'))
import cloud

class MorningTests(unittest.TestCase):
    def release(self,status='READY_FOR_REVIEW'):
        return {'body':json.dumps(dict(date='2026-11-24',status=status,sha256='a'*64,duration_seconds=106,procedure_version=1,music_embedded=True)),
                'assets':[{'name':n} for n in ('video.mp4','portada.jpg','descripcion.txt','verificacion-final.json','plan.json','comparison.json','music.json')]}

    def check(self,releases):
        with patch.object(cloud,'NOW',return_value=datetime(2026,11,24,8,23)),patch.object(cloud,'releases',return_value=releases),patch.object(cloud,'gh') as mutation:
            try:cloud.morning_check()
            finally:mutation.assert_not_called()

    def test_complete_ready_or_scheduled_delivery_passes(self):
        for status in ('READY_FOR_REVIEW','APPROVED_PENDING_TIKTOK','SCHEDULED_VERIFIED_BUFFER'):
            self.check([self.release(status)])

    def test_missing_or_duplicate_deliveries_fail(self):
        for releases in ([],[self.release(),self.release()]):
            with self.assertRaisesRegex(AssertionError,'missing or ambiguous'):self.check(releases)

    def test_wrong_day_failed_status_or_missing_assets_fail(self):
        for field,value in [('date','2026-11-23'),('status','FAILED_NEEDS_REVIEW'),('duration_seconds',70),('sha256',''),('music_embedded',False),('procedure_version',0)]:
            r=self.release();record=json.loads(r['body']);record[field]=value;r['body']=json.dumps(record)
            with self.assertRaises(AssertionError):self.check([r])
        r=self.release();r['assets']=[]
        with self.assertRaisesRegex(AssertionError,'incomplete'):self.check([r])

    def test_fallback_hours_target_same_day_and_evening_targets_next(self):
        import os
        for hour in (2,6,8):
            with patch.object(cloud,'NOW',return_value=datetime(2026,11,24,hour,23)),patch.dict(os.environ,{'GENERATION_DATE':'','GITHUB_EVENT_NAME':'schedule'}):
                self.assertEqual(cloud.target_date(),'2026-11-24')

    def test_scheduled_modes_execute_the_expected_safe_path(self):
        source=(cloud.ROOT/'.github/workflows/produccion-diaria.yml').read_text()
        block=source.split('      - name: Determinar accion')[1].split('      - name: Comprobar cola')[0].split('        run: |\n')[1]
        script='\n'.join(line[10:] for line in block.splitlines())
        expected={'17 3 * * *':'prepare','23 8 * * *':'prepare','23 12 * * *':'prepare','7 14 * * *':'prepare','23 14 * * *':'morning-check','40 14 * * *':'notify','0 15 * * *':'notify','23 15 * * *':'prepare','50 0 * * *':'remind'}
        self.assertEqual(set(re.findall(r"cron: '([^']+)'",source)),set(expected))
        for cron,mode in expected.items():
            with tempfile.TemporaryDirectory() as tmp:
                path=Path(tmp)/'result'
                subprocess.run(['bash','-e','-c',script],check=True,env={**os.environ,'CRON':cron,'INPUT_MODE':'','GITHUB_OUTPUT':str(path)})
                self.assertEqual(path.read_text().strip(),'value='+mode)

if __name__=='__main__':unittest.main()
