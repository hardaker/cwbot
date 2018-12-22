import unittest

class CWTests(unittest.TestCase):
    def test_hhmm(self):
        import cwbot as s
        
        self.assertEqual(s.sec_to_hhmm(30), "00:30")
        self.assertEqual(s.sec_to_hhmm(59), "00:59")
        self.assertEqual(s.sec_to_hhmm(60), "01:00")
        self.assertEqual(s.sec_to_hhmm(61), "01:01")
        self.assertEqual(s.sec_to_hhmm(121), "02:01")

    def test_average(self):
        import cwbot as s

        scores=[{'date': "12/10", "time": 50}]

        self.assertEqual(s.average_score({}), 0.0)
        self.assertEqual(s.average_score(scores), 50)

        scores.append({'date': "12/11", "time": 150})
        self.assertEqual(s.average_score(scores), 100)

    # def test_date(self):
    #     import cwbot as s
    #     self.assertEqual(s.make_datestr(), "2018/12/22")
