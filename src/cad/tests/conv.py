import unittest
import cad.calc.conv as conv

class TestConv(unittest.TestCase):

    def test_note(self):

        freq=conv.note_to_freq(0)
        self.assertEqual(freq, 440)

        name=conv.note_name(0)
        self.assertEqual(name, "A4")

        note=conv.freq_to_note(440)
        self.assertEqual(note, 0)

        for i in range(-24, 24):
            freq=conv.note_to_freq(i)
            note=conv.freq_to_note(freq)
            self.assertEqual(round(note), i)

# python -m unittest cad/tests/conv.py
if __name__ == '__main__':
    unittest.main()
