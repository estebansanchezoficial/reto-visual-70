"""New series: activation, finite rotation, unique solutions and readable boards."""
import copy
from datetime import date,timedelta
from fractions import Fraction
import json,sys,unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'daily'))
import catalog,generate,challenges,procedure,visual_puzzles,second_video as video

class VisualPuzzlesTests(unittest.TestCase):
    def test_forty_days_rotate_four_topics_without_reusing_an_exercise(self):
        history=json.loads((video.ROOT/'daily/content-history.json').read_text())
        keys=set()
        for offset in range(40):
            plan=generate.plan(str(date(2026,11,24)+timedelta(days=offset)),history=history)
            self.assertEqual(plan['family'],'catalog_'+visual_puzzles.TOPICS[offset%4])
            self.assertEqual(plan['duration_seconds'],106)
            self.assertEqual([r['level'] for r in plan['rounds']],[1,2,3])
            for r in plan['rounds']:
                key=catalog.exercise_key(r);self.assertNotIn(key,keys);keys.add(key)
                self.assertEqual(len(procedure.worked(r)),3)
            history.append(plan)
        self.assertEqual(len(keys),120)
        with self.assertRaisesRegex(ValueError,'Catálogo agotado'):
            generate.plan('2027-01-03',history=history)

    def test_activation_preserves_previous_plans(self):
        before=generate.plan('2026-11-23',history=[])
        self.assertNotIn(before['family'],['catalog_'+t for t in visual_puzzles.TOPICS])
        self.assertEqual(generate.plan('2026-11-24',history=[])['family'],'catalog_balanzas')

    def test_all_new_answers_satisfy_the_question_independently(self):
        packs=[p for p in catalog.load()['packs'] if p['topic'] in visual_puzzles.TOPICS]
        self.assertEqual(len(packs),40)
        for pack in packs:
            for r in pack['rounds']:
                p=r['params'];answer=int(r['next'])
                if r['kind']=='balance':
                    c=Fraction(p['circle_total'],p['circle_count']);t=p['pair_total']-p['circle_multiplier']*c
                    self.assertEqual(answer,t if p['mode']=='triangle' else c+t if p['mode']=='sum' else (p['square_total']-t)*t+c)
                elif r['kind']=='missing_digit':
                    solutions=[]
                    for digit in range(10):
                        text=p['pattern'].replace('?',str(digit))
                        if text[0]=='0':continue
                        n=int(text)
                        if (n+p.get('operand',0)==p.get('result') if p['mode']=='add' else n*p.get('operand',1)==p.get('result') if p['mode']=='multiply' else n%p['divisor']==0):solutions.append(digit)
                    self.assertEqual(solutions,[answer])
                elif r['kind']=='remainder':
                    self.assertEqual([n for n in range(p['low'],p['high']+1) if all(n%d==rem for d,rem in p['clues'])],[answer])
                else:
                    grid=visual_puzzles.candidates('magic',p)[0]
                    self.assertEqual(sorted(grid),p['values'])
                    self.assertTrue(all(sum(grid[i] for i in line)==p['total'] for line in visual_puzzles.LINES))
                    self.assertEqual(grid[p['target']],answer)

    def test_ambiguous_or_impossible_questions_fail_closed(self):
        for p in [dict(low=1,high=20,clues=[[2,1]]),dict(low=1,high=2,clues=[[3,0]])]:
            with self.assertRaisesRegex(AssertionError,'exactly one'):catalog.solve('remainder',p)

    def test_boards_render_all_new_puzzles_and_steps(self):
        base=video.BASE;data=challenges.DATA
        try:
            video.BASE=Image.open(video.ROOT/'assets/presenter/base-aprobada.png').convert('RGBA')
            for offset in range(4):
                history=[]
                for day in range(offset+1):
                    plan=generate.plan(str(date(2026,11,24)+timedelta(days=day)),history=history);history.append(plan)
                challenges.DATA=plan;challenges.board.cache_clear()
                for i,r in enumerate(plan['rounds']):
                    for phase in ['puzzle','answer','procedure1','procedure2','procedure3']:
                        self.assertEqual(challenges.board(i,phase,10).size,video.BASE.size)
        finally:
            video.BASE=base;challenges.DATA=data;challenges.board.cache_clear()

if __name__=='__main__':unittest.main()
