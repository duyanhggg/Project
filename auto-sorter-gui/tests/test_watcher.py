import os
import unittest
from autosorter.watcher import FileWatcher

class TestFileWatcher(unittest.TestCase):
    def setUp(self):
        self.test_directory = "test_dir"
        os.makedirs(self.test_directory, exist_ok=True)
        self.file_watcher = FileWatcher(self.test_directory)

    def tearDown(self):
        for filename in os.listdir(self.test_directory):
            file_path = os.path.join(self.test_directory, filename)
            os.remove(file_path)
        os.rmdir(self.test_directory)

    def test_file_creation(self):
        test_file = os.path.join(self.test_directory, "test_file.txt")
        with open(test_file, 'w') as f:
            f.write("This is a test file.")
        
        # Simulate file creation event
        self.file_watcher.on_created(test_file)
        
        # Check if the file watcher detected the new file
        self.assertIn(test_file, self.file_watcher.files)

    def test_file_deletion(self):
        test_file = os.path.join(self.test_directory, "test_file.txt")
        with open(test_file, 'w') as f:
            f.write("This is a test file.")
        
        # Simulate file creation event
        self.file_watcher.on_created(test_file)
        
        # Simulate file deletion event
        self.file_watcher.on_deleted(test_file)
        
        # Check if the file watcher no longer has the file
        self.assertNotIn(test_file, self.file_watcher.files)

if __name__ == "__main__":
    unittest.main()