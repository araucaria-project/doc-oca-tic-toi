import unittest

from obsplanparse import readFileAndConvert, writeDictToFile


class ParserCase(unittest.TestCase):
    def test_parsing_file1(self):
        result = readFileAndConvert('file1.txt')
        expected = {'commands': [
            {'command': 'ZERO', 'args': [], 'kwargs': {'seq': ['15/I/0']}},
            {'command': 'DARK', 'args': [], 'kwargs': {'seq': ['10/V/300', '10/I/200']}},
            {'command': 'DOMEFLAT', 'args': [], 'kwargs': {'seq': ['7/V/20', '7/I/20']}},
            {'command': 'DOMEFLAT', 'args': [], 'kwargs': {'seq': ['10/str_u/100'], 'domeflat_lamp': ['0.7']}}]}
        self.assertDictEqual(result, expected)

    def test_parsing_file2(self):
        result = readFileAndConvert('file2.txt')
        expected = {'commands': [
            {'command': 'BEGINSEQUENCE', 'args': [], 'kwargs': {'execute_at_dawn': ['-6'], 'priority': ['+10']}},
            {'command': 'SKYFLAT', 'args': [],
             'kwargs': {'alt': ['60:00:00'], 'az': ['270:00:00'], 'seq': ['10/I/20', '10/V/30']}},
            {'command': 'SKYFLAT', 'args': [], 'kwargs': {'seq': ['10/I/0', '10/V/0'], 'skyflat_adu': ['30']}},
            {'command': 'SKYFLAT', 'args': [],
             'kwargs': {'alt': ['60:00:00'], 'az': ['270:00:00'], 'seq': ['10/I/20', '10/V/30']}},
            {'command': 'SKYFLAT', 'args': [], 'kwargs': {'seq': ['10/I/0', '10/V/0'], 'skyflat_adu': ['30']}},
            {'command': 'ENDSEQUENCE', 'args': [], 'kwargs': {}}]}
        self.assertDictEqual(result, expected)

    def test_parsing_file3(self):
        result = readFileAndConvert('file3.txt')
        expected = {'commands': [
            {'command': 'BEGINSEQUENCE', 'args': [], 'kwargs': {'execute_at_time': ['02:21:43'], 'priority': ['+30']}},
            {'command': 'OBJECT', 'args': ['FF_Aql', '18:58:14.75', '17:21:39.29'],
             'kwargs': {'seq': ['2/I/60', '2/V/70']}},
            {'command': 'ENDSEQUENCE', 'args': [], 'kwargs': {}}]}
        self.assertDictEqual(result, expected)

    def test_parsing_file3_with_sequence(self):
        result = readFileAndConvert('file3.txt')
        expected =[
            {'begin_sequence': 'begin',
              'args': ['x', 'y', 'z'],
              'kwargs': {},
              'all_commands': [
                  {'command_name': 'ZERO',
                   'args': [],
                   'kwargs': {'seq': ['15/I/0']}},
                  {'command_name': 'DARK',
                   'args': [],
                   'kwargs': {'seq': ['10/V/300,10/I/200']}},
                  {'begin_sequence': 'begin',
                   'args': [],
                   'kwargs': {},
                   'all_commands': [
                       {'command_name': 'DOMEFLAT',
                        'args': [],
                        'kwargs': {'seq': ['7/V/20,7/I/20']}},
                       {'begin_sequence': 'begin',
                        'args': [],
                        'kwargs': {},
                        'all_commands': [
                            {'command_name': 'DOMEFLAT',
                             'args': [],
                             'kwargs': {'seq': ['10/str_u/100'], 'domeflat_lamp': ['0.7']}}
                        ]}
                   ]},
                  {'command_name': 'OBJECT',
                   'args': ['FF_Aql', '18:58:14.75', '17:21:39.29'],
                   'kwargs': {'seq': ['2/I/60,2/V/70']}}]},
             {'begin_sequence': 'begin',
              'args': [],
              'kwargs': {},
              'all_commands': [
                  {'command_name': 'FOCUS',
                   'args': ['NG31', '12:12:12', '20:20:20'],
                   'kwargs': {}}
              ]}
             ]

        self.assertListEqual(result, expected)

    def test_writing_to_file(self):
        dictionary = {'word1': 'hello', 'word2': 'world', 'word3': '!'}
        writeDictToFile("test_file.txt", dictionary)

        file = open("test_file.txt")
        result = file.readlines()  # should return list of file lines
        file.close()

        expected = ["{'word1': 'hello', 'word2': 'world', 'word3': '!'}"]

        self.assertListEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
