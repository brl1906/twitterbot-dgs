import configparser.ConfigParser
import os
import unittest

class TestDataRetrieval(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('test dataframe type'.upper(),'TEST DATAFRAME TYPE')

        # test for existence of key, data_name variables for datadotworld

        # test that clean_data function returns target number of columns

        # test that the dataframe function returns the target column names

        # test that the config.ini file exists

        # test that teh config.ini file has the required sections for .get call

        # test that the data function call has all required arguments

if __name__ == '__main__':
    unittest.main()
