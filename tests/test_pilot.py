import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('pilot',Path(__file__).resolve().parents[1]/'scripts/pilot.py')
pilot=importlib.util.module_from_spec(spec); spec.loader.exec_module(pilot)

class PilotTests(unittest.TestCase):
    def test_timeline_has_three_complete_solutions(self):
        pilot.validate_logic()
        expected=[(0,'intro'),(3,'memory'),(9,'mask'),(10,'search'),(18,'answer'),(22,'memory'),(29,'mask'),(30,'search'),(39,'answer'),(43,'memory'),(51,'mask'),(52,'search'),(61,'answer'),(65,'outro')]
        for t,phase in expected:
            with self.subTest(t=t): self.assertEqual(pilot.state(t)[1],phase)

    def test_answers_match_the_only_removed_object(self):
        for r in pilot.ROUNDS:
            self.assertEqual(set(r['objects'])-set(pilot.survivors(r)),{r['missing']})
            self.assertNotIn(r['missing'],pilot.survivors(r))
            self.assertEqual(len(pilot.survivors(r)),len(r['objects'])-1)

    def test_mask_board_identical_for_all_rounds(self):
        # The entire board is opaque and contains no original object pixels.
        boards=[pilot.base(i,'mask').crop((90,650,880,1330)).tobytes() for i in range(3)]
        self.assertEqual(boards[0],boards[1]); self.assertEqual(boards[1],boards[2])

    def test_reveal_restores_objects_and_highlights_answer(self):
        for i,r in enumerate(pilot.ROUNDS):
            self.assertNotEqual(pilot.base(i,'search').tobytes(),pilot.base(i,'answer').tobytes())
            self.assertTrue(pilot.NAMES[r['missing']])

if __name__=='__main__': unittest.main()
