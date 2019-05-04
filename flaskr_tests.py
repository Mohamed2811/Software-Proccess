import os
from app import app
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        pass

    def test_delete_failing(self):
        rv = self.app.get('/delete_game/1')
        assert b'Method Not Allowed' in rv.data

    def test_games_exist(self):
        rv = self.app.get('/games')
        assert b'1 + 1' in rv.data

    def test_single_game(self):
        rv = self.app.get("/game/1", follow_redirects=True)
        assert b'No games Found' in rv.data



if __name__ == '__main__':
    unittest.main()