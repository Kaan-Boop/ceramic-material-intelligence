import unittest
from pipelines.ingestion.tga_inspect import inspect_header


class HeaderTests(unittest.TestCase):
    def test_binary_is_not_decoded_as_measurements(self):
        raw = 'CLOSED\r\nSig1 Time (min)\r\nOperator private\r\nFile private-path\r\n'.encode('utf-16') + b'\x0c\x00\xff\xff'
        r = inspect_header(raw)
        self.assertEqual(r['header_fields'], ['Sig1 Time (min)'])
        self.assertFalse(r['vapor_replay_allowed'])
        self.assertEqual(r['numeric_rows_validated'], 0)

    def test_unknown_format_rejected(self):
        for raw in (b'csv', 'no delimiter'.encode('utf-16')):
            with self.assertRaises(ValueError):
                inspect_header(raw)
