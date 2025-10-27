import os
import unittest
from unittest.mock import patch, MagicMock
from autosorter.watcher import Handler

class TestHandler(unittest.TestCase):
    def setUp(self):
        self.source = "D:\\"
        self.handler = Handler(self.source)

    @patch('autosorter.watcher.move_file')
    @patch('autosorter.watcher.logging')
    @patch('autosorter.watcher.notification')
    def test_on_created_file(self, mock_notification, mock_logging, mock_move_file):
        event = MagicMock()
        event.is_directory = False
        event.src_path = os.path.join(self.source, "test_file.txt")

        self.handler.on_created(event)

        mock_logging.info.assert_called_once_with("New file detection: test_file.txt")
        mock_notification.notify.assert_called_once_with(
            title="AutoSorter",
            message="New file detection: test_file.txt",
            app_name="AutoSorter",
            timeout=3
        )
        mock_move_file.assert_called_once_with(event.src_path, self.source)

    @patch('autosorter.watcher.move_file')
    def test_on_created_directory(self, mock_move_file):
        event = MagicMock()
        event.is_directory = True
        event.src_path = os.path.join(self.source, "new_directory")

        self.handler.on_created(event)

        mock_move_file.assert_not_called()

if __name__ == '__main__':
    unittest.main()