import unittest
from unittest import mock
import ftplib
import datetime
from ftpfind import walk
from ftpfind import connect
from ftpfind import parse_date_delta
from ftpfind import val_to_int
from ftpfind import get_start_stop_day_dates
from ftpfind import parse_date


class TestParseDate(unittest.TestCase):

    def test_if_returns_good_values_on_good_input_day(self):
        test_start = "2016-10-07 12:20"
        test_stop = "2016-10-05 12:20"
        format = "%Y-%m-%d %H:%M"
        with mock.patch("ftpfind.datetime") as mock_datetime:
            mock_datetime.datetime.now.return_value = datetime.datetime(2016, 10, 7, 12, 20, 0)
            mock_datetime.side_effects = lambda *args, **kw: date(*args, **kw)
            start, stop = parse_date("2d")
            self.assertEqual(start.strftime(format), test_start)
            self.assertEqual(stop.strftime(format), test_stop)

    def test_if_returns_good_values_on_good_input_month(self):
        test_start = "2016-10-07 12:20"
        test_stop = "2016-09-07 12:20"
        format = "%Y-%m-%d %H:%M"
        with mock.patch("ftpfind.datetime") as mock_datetime:
            mock_datetime.datetime.now.return_value = datetime.datetime(2016, 10, 7, 12, 20, 0)
            mock_datetime.side_effects = lambda *args, **kw: date(*args, **kw)
            start, stop = parse_date("1m")
            self.assertEqual(start.strftime(format), test_start)
            self.assertEqual(stop.strftime(format), test_stop)

    def test_if_returns_good_values_on_good_input_year(self):
        test_start = "2016-10-07 12:20"
        test_stop = "2010-10-07 12:20"
        format = "%Y-%m-%d %H:%M"
        with mock.patch("ftpfind.datetime") as mock_datetime:
            mock_datetime.datetime.now.return_value = datetime.datetime(2016, 10, 7, 12, 20, 0)
            mock_datetime.side_effects = lambda *args, **kw: date(*args, **kw)
            start, stop = parse_date("6y")
            self.assertEqual(start.strftime(format), test_start)
            self.assertEqual(stop.strftime(format), test_stop)

    def test_if_returns_good_values_on_good_input_date(self):
        test_start = "2016-10-07 00:00"
        test_stop = "2016-10-07 23:59"
        format = "%Y-%m-%d %H:%M"
        start, stop = parse_date("2016-10-07")
        self.assertEqual(start.strftime(format), test_start)
        self.assertEqual(stop.strftime(format), test_stop)

    def test_if_raises_error_on_bad_input(self):
        with self.assertRaises(ValueError):
            start, stop = parse_date("test")


class TestGetStartStopDayDatesFunction(unittest.TestCase):

    def test_if_returns_good_values_on_good_input(self):
        test_start = datetime.datetime(2016, 11, 20, 0, 0, 0)
        test_stop = datetime.datetime(2016, 11, 20, 23, 59, 59)
        s = "2016-11-20"
        start, stop = get_start_stop_day_dates(s)
        self.assertEqual(test_start, start)
        self.assertEqual(test_stop, stop)

    def test_if_returns_good_values_on_bad_input(self):
        s = "Ala ma kota"
        with self.assertRaises(ValueError):
            start, stop = get_start_stop_day_dates(s)


class TestParseDateDelta(unittest.TestCase):

    def test_if_val_to_int_returns_int(self):
        self.assertEqual(1, val_to_int("1"))
        self.assertEqual(0, val_to_int(None))
        self.assertEqual(2, val_to_int(2))
        self.assertEqual(2, val_to_int("2"))
        self.assertEqual(0, val_to_int("10s"))
        self.assertEqual(-10, val_to_int("-10"))
        self.assertEqual(0, val_to_int("0"))
        self.assertEqual(0, val_to_int({}))
        self.assertEqual(0, val_to_int("a"))

    def test_if_return_good_values_days(self):
        val = parse_date_delta("2d")
        cmp = {"days": 2, "months": 0, "years": 0}
        self.assertEqual(val, cmp)

    def test_if_return_good_values_months(self):
        val = parse_date_delta("10m")
        cmp = {"days": 0, "months": 10, "years": 0}
        self.assertEqual(val, cmp)

    def test_if_return_good_values_years(self):
        val = parse_date_delta("30y")
        cmp = {"days": 0, "months": 0, "years": 30}
        self.assertEqual(val, cmp)

    def test_if_return_good_values_if_input_is_mistyped(self):
        val = parse_date_delta("30f")
        cmp = {"days": 0, "months": 0, "years": 0}
        self.assertEqual(val, cmp)

    def test_if_return_good_values_if_input_is_giberrish(self):
        val = parse_date_delta("fsdsdds")
        cmp = {"days": 0, "months": 0, "years": 0}
        self.assertEqual(val, cmp)

class TestWalkFunction(unittest.TestCase):
    pass
