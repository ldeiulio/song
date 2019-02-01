from models import File, Song, Base, session, engine
import api
from create_app import app
import unittest, json
from uploads.utils import upload_path
from io import BytesIO
import os
from urllib.parse import urlparse


class TestAPI(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        Base.metadata.create_all(engine)

        for i in range(30):
            file = File(file_name="test{}".format(i))
            session.add(file)
            session.commit()

            song = Song(file_id=file.id)
            session.add(song)
            session.commit()

        # print(song.as_dictionary())
        # print(file.as_dictionary())

    def tearDown(self):
        """Test teardown"""
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

    def test_song_list_get(self):
        rv = self.client.get('api/songs')
        self.assertIn(b'test29', rv.data)

    def test_song_list_post(self):
        file = File(file_name="test30")
        session.add(file)
        session.commit()
        rv = self.client.post('api/songs', data=json.dumps(dict(file=dict(id=file.id))),
                              content_type='application/json', follow_redirects=True)
        print(rv.status_code)
        rv = self.client.get('api/songs')
        self.assertIn(b'test30', rv.data)

    def test_get_uploaded_file(self):
        path = upload_path("test.txt")
        with open(path, "wb") as f:
            f.write(b'File contents')

        response = self.client.get("uploads_text/test.txt")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/plain")
        self.assertEqual(response.data, b"File contents")

    def test_file_upload(self):
        data = {
            "file": (BytesIO(b'File contents'), "test2.txt")
        }

        response = self.client.post('api/files',
                                    data=data,
                                    content_type="multipart/form-data",
                                    headers=[("Accept", "application/json")]
                                    )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(urlparse(data["path"]).path, "uploads/test2.txt")
        path = upload_path("test2.txt")
        self.assertTrue(os.path.isfile(path))
        with open(path, "rb") as f:
            contents = f.read()
        self.assertEqual(contents, b'File contents')


if __name__ == '__main__':
    unittest.main()
