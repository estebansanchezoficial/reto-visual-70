"""Worked math, timeline boundaries, legibility and historical compatibility."""
import sys,unittest,copy,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'daily'))
import catalog,procedure,generate,challenges,second_video as video

class ProcedureTests(unittest.TestCase):
    def test_all_ninety_exercises_have_three_readable_worked_steps(self):
        for pack in catalog.load()['packs']:
            for r in pack['rounds']:
                steps=procedure.worked(r)
                self.assertEqual(len(steps),3)
                self.assertIn(r['next'],steps[-1]['calculation'])
                for s in steps:
                    self.assertTrue(s['instruction'])
                    for line in s['lines']:self.assertLessEqual(video.font(25).getlength(line),380)
                    self.assertLessEqual(video.font(22).getlength(s['calculation']),380)

    def test_timeline_shows_answer_then_each_step_without_overlap(self):
        data=generate.plan('2026-11-04',history=[])
        challenges.DATA=data
        self.assertEqual(data['duration_seconds'],106)
        self.assertEqual(data['procedure_title'],'ESTE ES EL PROCEDIMIENTO')
        for i,r in enumerate(data['rounds']):
            self.assertEqual(challenges.state(r['answer'])[1],'answer')
            self.assertEqual(r['procedure_start']-r['answer'],5)
            for j in range(3):
                at=r['procedure_start']+4*j
                self.assertEqual(challenges.state(at)[1],f'procedure{j+1}')
                self.assertEqual(challenges.state(at+3.99)[1],f'procedure{j+1}')
                self.assertIn(float(at+2),procedure.samples(data))
            if i<2:self.assertEqual(challenges.state(r['end'])[1],'puzzle')
        self.assertEqual(challenges.state(102),(3,'outro',106))

    def test_existing_approved_70_second_plan_is_not_changed(self):
        path=video.ROOT/'daily/content-history.json'
        history=json.loads(path.read_text(encoding='utf-8'));before=copy.deepcopy(history)
        generate.plan('2026-11-04',history=history)
        self.assertEqual(before,history)
        old={'family':'arithmetic','rounds':[{'start':6,'answer':20,'end':25},{'start':25,'answer':40,'end':45},{'start':45,'answer':61,'end':66}]}
        challenges.DATA=old
        self.assertEqual(challenges.state(25),(1,'puzzle',40))
        self.assertEqual(challenges.state(66),(3,'outro',70))

    def test_explicit_arithmetic_request_also_has_a_procedure(self):
        data=generate.plan('2026-11-04',history=[],requested_family='arithmetic')
        self.assertEqual(data['procedure_version'],1)
        self.assertEqual(data['duration_seconds'],106)

    def test_single_discount_does_not_invent_a_second_price_change(self):
        pack=next(p for p in catalog.load()['packs'] if p['topic']=='porcentajes')
        steps=procedure.worked(pack['rounds'][0])
        self.assertIn('sin otro cambio',steps[-1]['instruction'])
        self.assertNotIn('segundo',steps[-1]['instruction'])

if __name__=='__main__':unittest.main()
