import os
import shutil
import unittest
from autosorter.mover import move_file

class TestMover(unittest.TestCase):
    def setUp(self):
        self.test_dir = 'test_dir'
        self.images_dir = os.path.join(self.test_dir, 'Images')
        self.docs_dir = os.path.join(self.test_dir, 'Docs')
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.docs_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_move_image_file(self):
        test_file = os.path.join(self.test_dir, 'test_image.png')
        with open(test_file, 'w') as f:
            f.write('test')

        move_file(test_file, self.test_dir)

        self.assertFalse(os.path.exists(test_file))
        self.assertTrue(os.path.exists(os.path.join(self.images_dir, 'test_image.png')))

    def test_move_document_file(self):
        test_file = os.path.join(self.test_dir, 'test_document.pdf')
        with open(test_file, 'w') as f:
            f.write('test')

        move_file(test_file, self.test_dir)

        self.assertFalse(os.path.exists(test_file))
        self.assertTrue(os.path.exists(os.path.join(self.docs_dir, 'test_document.pdf')))

    def test_move_unknown_file_type(self):
        test_file = os.path.join(self.test_dir, 'test_unknown.xyz')
        with open(test_file, 'w') as f:
            f.write('test')

        move_file(test_file, self.test_dir)

        self.assertFalse(os.path.exists(test_file))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'Misc', 'test_unknown.xyz')))

if __name__ == '__main__':
    unittest.main()