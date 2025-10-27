import unittest
from autosorter.sorter import move_file

class TestSorter(unittest.TestCase):
    
    def test_move_file_valid(self):
        # Test moving a valid file to the correct directory
        source_file = "path/to/source/test_file.txt"
        destination_folder = "path/to/destination/Docs"
        result = move_file(source_file, destination_folder)
        self.assertTrue(result)  # Assuming move_file returns True on success

    def test_move_file_invalid(self):
        # Test moving a non-existent file
        source_file = "path/to/source/non_existent_file.txt"
        destination_folder = "path/to/destination/Docs"
        result = move_file(source_file, destination_folder)
        self.assertFalse(result)  # Assuming move_file returns False on failure

    def test_move_file_unsupported_extension(self):
        # Test moving a file with an unsupported extension
        source_file = "path/to/source/test_file.unsupported"
        destination_folder = "path/to/destination/Misc"
        result = move_file(source_file, destination_folder)
        self.assertTrue(result)  # Assuming it moves to Misc folder

if __name__ == '__main__':
    unittest.main()