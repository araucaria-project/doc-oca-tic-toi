import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        a = 2+2
        b = 4
        self.assertEqual(a, b)

if __name__ == '__main__':
    unittest.main()
