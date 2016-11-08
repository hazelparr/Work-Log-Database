import unittest
import unittest.mock

import work_log



from peewee import *
from playhouse.test_utils import test_database

test_db = SqliteDatabase(':memory:')
test_db.connect()
test_db.create_tables([work_log.Entry], safe=True)

TEST = {"name": "test name",
         "task_name": "test",
         "date": "2000-01-01",
         "time_spent": 200,
         "notes": "test notes"
         }


class AddTests(unittest.TestCase):

    @staticmethod
    def create_entries():
        work_log.Entry.create(
            name=TEST["name"],
            task_name=TEST["task_name"],
            date=TEST["date"],
            time_spent=TEST["time_spent"],
            notes=TEST["notes"])


    def test_get_name(self):
        with unittest.mock.patch('builtins.input', return_value=
            TEST["name"]):
            assert work_log.get_name() == TEST["name"]
        with unittest.mock.patch('builtins.input', side_effect = ["", "", 
            "daisy"]):
            assert work_log.get_name() == "daisy"

    def test_get_minutes(self):
        with unittest.mock.patch('builtins.input', side_effect = ["one", 
            "", 5]):
            assert work_log.get_minutes() == 5

    def test_get_task_name(self):
        with unittest.mock.patch('builtins.input', side_effect = ["", 
            "", "studying"]):
            assert work_log.get_task_name() == "studying"

    def test_get_date(self):
        with unittest.mock.patch('builtins.input', side_effect = ["05/05/2016", 
            "", "2016-05-05"]):
            assert work_log.get_date() == "2016-05-05"

    def test_add_entry(self): 
        with unittest.mock.patch('builtins.input', side_effect = ["test name",
            "eating", "2016-11-06", 50, "nom nom nom", "y", ""], return_value=
            TEST):
            assert work_log.add_entry()["name"] == TEST["name"]

    def test_search_entry(self):
        with test_database(test_db, (work_log.Entry, )):
            self.create_entries()
            with unittest.mock.patch('builtins.input', side_effect = 
            ["n", "test name", "", "m"]):
                assert work_log.search_entry().count() == 1
                
            
            with unittest.mock.patch('builtins.input', side_effect = 
            ["d", "2000-01-01","2000-01-01", "", "m"]):
                assert work_log.search_entry().count() == 1             
            
            with unittest.mock.patch('builtins.input', side_effect = 
            ["t", 200, "", "m"]):
                assert work_log.search_entry().count() == 1

            with unittest.mock.patch('builtins.input', side_effect = 
            ["s", "test", "", "m"]):
                assert work_log.search_entry().count() == 1           

    def test_edit_entry(self):
        with test_database(test_db, (work_log.Entry, )):
            entry = work_log.Entry.create(**TEST)
            
            with unittest.mock.patch('builtins.input', side_effect = 
            ["s","coding", ""]):
                work_log.edit_entry(entry)
                self.assertEqual(entry.notes, "coding")
            
            with unittest.mock.patch('builtins.input', side_effect = 
            ["e","marley", ""]):
                work_log.edit_entry(entry)
                self.assertEqual(entry.name, "marley")

            with unittest.mock.patch('builtins.input', side_effect = 
            ["d","2000-01-01", ""]):
                work_log.edit_entry(entry)
                self.assertEqual(entry.date, "2000-01-01")

            with unittest.mock.patch('builtins.input', side_effect = 
            ["t", 500, ""]):
                work_log.edit_entry(entry)
                self.assertEqual(entry.time_spent, 500)              

            with unittest.mock.patch('builtins.input', side_effect = 
            ["n","techdegree", ""]):
                work_log.edit_entry(entry)
                self.assertEqual(entry.task_name, "techdegree")  
    def test_delete_entry(self):
        with test_database(test_db, (work_log.Entry, )):
            entry = work_log.Entry.create(**TEST)        
            with unittest.mock.patch('builtins.input', side_effect = 
            ["y",""]):
                work_log.delete_entry(entry)
                self.assertEqual(work_log.Entry.select().count(), 0)
    

            



if __name__ == "__main__":
    unittest.main()