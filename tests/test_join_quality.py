import unittest
from scripts.join_quality import join


class JoinTests(unittest.TestCase):
    def test_keep_sessions_and_devices(self):
        efficiency = [{'run_id': 'a', 'image_group': 'light', 'device': device, 'measurement_id': str(i)}
                      for i, device in enumerate(['cuda:0', 'cpu'])]
        result = join(efficiency, [{'run_id': 'a', 'image_group': 'light', 'auroc': '0.8'}])
        self.assertEqual(len(result), 2)
        self.assertEqual(result[1]['device'], 'cpu')
        self.assertEqual(result[0]['quality_auroc'], '0.8')

    def test_duplicate_or_missing_quality_is_visible(self):
        row = {'run_id': 'a', 'image_group': 'light'}
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            join([row], [row, row])
        with self.assertRaisesRegex(ValueError, 'No quality'):
            join([row], [{'run_id': 'b', 'image_group': 'light'}])

    def test_quality_device_is_respected(self):
        with self.assertRaisesRegex(ValueError, 'No quality'):
            join([{'run_id': 'a', 'image_group': 'light', 'device': 'cpu'}],
                 [{'run_id': 'a', 'image_group': 'light', 'device': 'cuda:0'}])

    def test_smoke_cannot_be_used_as_model_efficiency(self):
        row = {'run_id': 'a', 'image_group': 'light'}
        with self.assertRaisesRegex(ValueError, 'Smoke'):
            join([{**row, 'kind': 'instrumentation_smoke'}], [row])
