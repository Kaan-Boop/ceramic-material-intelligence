import unittest
from pipelines.ingestion.moisture_observations import reported_number, normalize


class MoistureObservationTests(unittest.TestCase):
    def test_dash_is_unknown_not_zero(self):
        self.assertIsNone(reported_number('-', 'degC', 260)['value'])
        self.assertEqual(reported_number('0', 'degC', 260)['value'], 0)

    def test_invalid_values(self):
        for value in ('nan', 'inf', '-1', '101', 'unknown'):
            with self.assertRaises(ValueError):
                reported_number(value, 'percent', 100)

    def test_unreviewed_structure_rejected(self):
        with self.assertRaisesRegex(ValueError, 'TABLE_REQUIRED'):
            normalize(b'<article/>', {})
