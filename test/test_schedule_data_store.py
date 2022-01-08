from unittest import TestCase

from data_stores.schedule.schedule_data_store import ScheduleDataStore, Time


class TestScheduleDataStore(TestCase):

    def test_schedule_data_store(self):
        schedule_ds = ScheduleDataStore()
        schedule_ds.clear()

        times = [Time(1, 0, 10)]
        schedule_ds.save_schedule(times)

        self.assertEqual(schedule_ds.load_schedule(), times)

    def test_time_culling(self):
        self.assertEqual(Time(25, 0, 10).culled(), Time(1, 0, 10))
        self.assertEqual(Time(-2, 0, 10).culled(), Time(22, 0, 10))