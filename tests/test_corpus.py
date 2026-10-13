"""Integrity fixtures, not CTM parsing tests."""
import importlib.util
import pathlib
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('corpus_tools', pathlib.Path(__file__).resolve().parents[1] / 'scripts/corpus.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class IntegrityFixtures(unittest.TestCase):
    def test_byte_change_missing_and_extra_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            for name in ['ctm/in', 'ctm/invalid', 'ctm/baseline']:
                (root / name).mkdir(parents=True)
            source = root / 'ctm/in/fixture.ctm'
            source.write_bytes(b'infrastructure fixture\x00\xff')
            baseline = root / 'ctm/baseline/fixture.ctm.cxtm'
            baseline.write_bytes(b'independent baseline fixture')
            lock = dict(files=module.inventory(root))
            self.assertEqual(module.verify(lock, root)['valid'], 1)
            source.write_bytes(b'changed')
            with self.assertRaises(SystemExit):
                module.verify(lock, root)
            source.write_bytes(b'infrastructure fixture\x00\xff')
            baseline.unlink()
            with self.assertRaises(SystemExit):
                module.verify(lock, root)
            baseline.write_bytes(b'independent baseline fixture')
            extra = root / 'unexpected.ctm'
            extra.write_text('not an input')
            with self.assertRaises(SystemExit):
                module.verify(lock, root)
            extra.unlink()
            self.assertEqual(module.inventory(root), lock['files'])

    def test_auxiliary_and_correspondence_inventory(self):
        root = pathlib.Path(__file__).parent / 'fixtures/corpus'
        result = module.recount(root)
        self.assertEqual((result['valid'], result['invalid'], result['baselines'], result['auxiliary']), (2, 1, 2, 2))
        self.assertEqual(result['missingBaselines'], ['ctm/baseline/beta.ctm.cxtm'])
        self.assertEqual(result['unmatchedBaselines'], ['ctm/baseline/orphan.ctm.cxtm'])


if __name__ == '__main__':
    unittest.main()
