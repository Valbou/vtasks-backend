from tests import BaseTestCase
from vtasks.tasks.models import Task
from vtasks.tasks.persistence import TaskDB

URL_API = "/api/v1"


class TestTasksAPI(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.headers = self.get_json_headers()
        self.task_db = TaskDB()

    def test_create_task_no_login(self):
        task_data = {"nodata": "nodata"}
        response = self.client.post(
            f"{URL_API}/tasks", json=task_data, headers=self.headers
        )
        self.assertEqual(response.status_code, 401)

    def test_create_task(self):
        headers = self.get_token_headers()
        title = self.fake.sentence(nb_words=8)
        task_data = {
            "title": title,
        }
        response = self.client.post(f"{URL_API}/tasks", json=task_data, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json.get("title"), title)
        self.assertIsInstance(response.json.get("id"), str)
        with self.app.sql.get_session() as session:
            self.assertTrue(self.task_db.exists(session, response.json.get("id")))

    def test_get_tasks_no_login(self):
        response = self.client.get(f"{URL_API}/tasks", headers=self.headers)
        self.assertEqual(response.status_code, 401)

    def test_get_tasks(self):
        headers = self.get_token_headers()
        task = Task(user_id=self.user.id, title=self.fake.sentence(nb_words=8))
        with self.app.sql.get_session() as session:
            self.task_db.save(session, task)

            response = self.client.get(f"{URL_API}/tasks", headers=headers)
            self.assertEqual(response.status_code, 200)
            result = response.json
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].get("id"), task.id)

    def test_no_put(self):
        response = self.client.put(
            f"{URL_API}/users/me/change-email", headers=self.headers
        )
        self.assertEqual(response.status_code, 405)

    def test_no_patch(self):
        response = self.client.patch(
            f"{URL_API}/users/me/change-email", headers=self.headers
        )
        self.assertEqual(response.status_code, 405)

    def test_no_delete(self):
        response = self.client.delete(
            f"{URL_API}/users/me/change-email", headers=self.headers
        )
        self.assertEqual(response.status_code, 405)
