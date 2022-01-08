from unittest import TestCase

from datetime import datetime, timedelta
from freezegun.api import freeze_time

from data_stores.data_persisters import DataNotFreshException, FileDataPersister, StackDataPersister, FreshDataStore


class TestDataPersisters(TestCase):

    def test_file_persister(self):
        file_dp = FileDataPersister('test')
        file_dp.clear()

        file_dp.save_raw_data("some data")

        self.assertEqual(file_dp.load_raw_data(), "some data")

    def test_stack_persister(self):
        stack_dp = StackDataPersister('test', 2)
        stack_dp.clear()

        stack_dp.add_stack_item("item 1")
        stack_dp.add_stack_item("item 2")

        self.assertEqual(stack_dp.read_stack(), ["item 1", "item 2"])

        stack_dp.add_stack_item("item 3")

        self.assertEqual(stack_dp.read_stack(), ["item 2", "item 3"])

    def test_fresh_data_store_fresh(self):
        fresh_ds = FreshDataStore[int]('test', 100, timedelta(days=1))
        fresh_ds.clear()

        with freeze_time(datetime(2022, 1, 1)):
            fresh_ds.add_value(1)

            self.assertEqual(fresh_ds.read_all_values(), [1])

    def test_fresh_data_store_not_fresh(self):
        fresh_ds = FreshDataStore[int]('test', 100, timedelta(days=1))
        fresh_ds.clear()

        with freeze_time(datetime(2022, 1, 1)):
            fresh_ds.add_value(1)

        self.assertRaises(DataNotFreshException, fresh_ds.read_all_values)