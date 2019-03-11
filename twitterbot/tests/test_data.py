from  configparser import ConfigParser
import os
import unittest

from data_handler import get_data
import pandas as pd

class TestConfigFileExistence(unittest.TestCase):
    def setUp(self):
        self.file = os.path.join(os.pardir, 'configuration', 'config.ini')
        self.config = ConfigParser()
        self.config.read(self.file)
        self.section_names = ['api_key','api_secret','access_token',
                            'token_secret','datadotworld']

    def tearDown(self):
        pass

    def test_configfile_existence(self):
        self.assertEqual(os.path.join(os.pardir, 'configuration', 'config.ini'),
                        self.file)

    def test_configfile_sections(self):
        self.assertEqual(self.config.sections(), self.section_names)


class TestDataRetrieval(unittest.TestCase):
    def setUp(self):
        self.file = os.path.join(os.pardir, 'configuration', 'config.ini')
        self.config = ConfigParser()
        self.config.read(self.file)
        self.sections = self.config.sections()
        self.raw_data = data_handler.get_data(self.config.get(section='datadotworld',
                        option='key'), self.config.get(section='datadotworld',
                        option='data_name'))

    def tearDown():
        pass

    def test_get_data_function_return(self):
        self.assertEqual(type(self.raw_data), type(pd.DataFrame))

    def test_clean_data_function_return(self):
        self.assertEqual(type(data_handler.clean_data(self.raw_data)),
                        type(pd.DataFrame))

    # test that dataframe function returns certain basic columns




if __name__ == '__main__':
    unittest.main()
