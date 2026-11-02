"""Independent correctness, exhaustion, history and layout checks for the bank."""
import sys, unittest, copy, itertools, tempfile
from unittest.mock import patch
from pathlib import Path
from fractions import Fraction
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'daily'))
import catalog, generate, challenges
import cloud

class CatalogTests(unittest.TestCase):
    def test_full_catalog_has_three_tiers_and_exact_answers(self):
        bank=catalog.load()
        self.assertEqual(len(bank['packs']),30)
        self.assertEqual(len({p['topic'] for p in bank['packs']}),10)
        for pack in bank['packs']:
            self.assertEqual([r['level'] for r in pack['rounds']],[1,2,3])
            for r in pack['rounds']:
                p=r['params'];answer=Fraction(r['next'])
                if r['kind']=='linear': self.assertEqual(p['a']*answer+p['c'],p['b'])
                elif r['kind']=='quadratic':
                    self.assertGreater(answer,0)
                    self.assertEqual(answer**2-p['a']*answer,p['constant'])
                elif r['kind']=='probability':
                    balls=list(range(p['red']+p['blue']))
                    draws=list(itertools.combinations(balls,p['draws']))
                    self.assertEqual(answer,Fraction(sum(all(b<p['red'] for b in d) for d in draws),len(draws)))
                elif r['kind']=='counting':
                    if p['mode']=='product': expected=len(list(itertools.product(range(p['a']),range(p['b']))))
                    elif p['mode']=='choose': expected=len(list(itertools.combinations(range(p['a']),p['b'])))
                    else: expected=len(list(itertools.permutations(range(p['a']),p['b'])))
                    self.assertEqual(answer,expected)
                elif r['kind']=='average': self.assertEqual((sum(p['known'])+answer)/p['count'],p['target'])
                elif r['kind']=='system':
                    if p['mode']=='sum': self.assertEqual(2*answer-p['difference'],p['total'])
                    else:
                        self.assertTrue(0<=answer<=p['count'])
                        self.assertEqual(answer*p['expensive']+(p['count']-answer)*p['cheap'],p['cost'])

    def test_rejected_and_same_episode_versions_are_never_reused(self):
        first=generate.plan('2026-11-03',history=[])
        first['status']='SUPERSEDED'
        second=generate.plan('2026-11-03',revision=4,history=[first],rejected_family=first['family'])
        self.assertNotEqual(first['pack_id'],second['pack_id'])
        reused=copy.deepcopy(second);reused['rounds'][0]=first['rounds'][0]
        with self.assertRaisesRegex(AssertionError,'Individual exercise'): challenges.compare(reused,[first])

    def test_changed_id_or_choices_cannot_disguise_used_content(self):
        first=generate.plan('2026-11-03',history=[])
        r=copy.deepcopy(first['rounds'][0]);r['catalog_id']='new-id';r['choices'].reverse()
        self.assertEqual(catalog.exercise_key(r),catalog.exercise_key(first['rounds'][0]))

    def test_wrong_answer_or_difficulty_is_rejected(self):
        r=copy.deepcopy(catalog.load()['packs'][0]['rounds'][0]);r['next']='999'
        with self.assertRaises(AssertionError):catalog.validate_round(r)
        r=copy.deepcopy(catalog.load()['packs'][0]['rounds'][0]);r['difficulty']='AVANZADO'
        with self.assertRaises(AssertionError):catalog.validate_round(r)

    def test_explicit_math_request_uses_only_math_bank(self):
        data=generate.plan('2026-11-03',history=[],requested_family='catalog_math',rejected_family='color')
        self.assertTrue(data['family'].startswith('catalog_'))
        self.assertEqual([r['difficulty'] for r in data['rounds']],catalog.LEVELS)

    def test_exhaustion_stops_before_downloading_models_and_notifies_reason(self):
        history=[{'episode':i,'revision':1,'family':'catalog_'+p['topic'],'rounds':p['rounds']} for i,p in enumerate(catalog.load()['packs'])]
        record={'date':'2026-12-01'}
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'output').mkdir()
            with patch.object(cloud,'ROOT',root),patch.object(cloud,'OUT',root/'output/current'),patch.object(cloud,'gh'),patch.object(cloud.subprocess,'run') as run:
                with self.assertRaisesRegex(ValueError,'Catálogo agotado'):cloud.deliver('test',record,history)
                run.assert_not_called()
        self.assertEqual(record['status'],'FAILED_NEEDS_REVIEW')
        self.assertIn('Catálogo agotado',record['correction_block_reason'])

if __name__=='__main__':unittest.main()
