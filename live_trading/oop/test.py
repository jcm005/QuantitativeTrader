import unittest
import analyzer

class TestAnalyzerSMA(unittest.TestCase):

    def test_sma_data(self):
        data = [i for i in range(400,420)]
        results = analyzer.Analyzer.sma
        self.assertEqual(results(data,window=20),409.5)

    def test_sma_none(self):
        none = None
        results = analyzer.Analyzer.sma
        self.assertIsNotNone(results(none))




if __name__ == '__main__':

    unittest.main()


