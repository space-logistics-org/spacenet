"""
Tests of the web application which serves the user interface.
"""

import os
import tempfile
import unittest
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
pytest.importorskip("fastapi_users")
pytest.importorskip("aiosqlite")

# pylint: disable=wrong-import-position
from fastapi.testclient import TestClient


class TestApplication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # the user database is created in a temporary directory
        cls.directory = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        database = Path(cls.directory.name) / "users.db"
        os.environ["SPACENET_DB_URL"] = f"sqlite+aiosqlite:///{database.as_posix()}"
        from spacenet_app.main import (
            STATIC_DIR,
            app,
        )  # pylint: disable=import-outside-toplevel

        cls.static = STATIC_DIR
        cls.context = TestClient(app)
        cls.client = cls.context.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.context.__exit__(None, None, None)
        os.environ.pop("SPACENET_DB_URL", None)
        cls.directory.cleanup()

    def test_user_interface(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        self.assertIn("/static/js/main.js", response.text)

    def test_static_files(self):
        for path in self.static.rglob("*"):
            if path.is_file():
                url = "/static/" + path.relative_to(self.static).as_posix()
                self.assertEqual(self.client.get(url).status_code, 200, url)
        self.assertEqual(self.client.get("/static/js/missing.js").status_code, 404)

    def test_scripts_import_existing_modules(self):
        scripts = self.static / "js"
        for path in scripts.rglob("*.js"):
            for line in path.read_text(encoding="utf-8").splitlines():
                if ' from "./' in line or ' from "../' in line:
                    target = line.split(" from ")[-1].strip().strip(";").strip('"')
                    self.assertTrue(
                        (path.parent / target).resolve().is_file(), f"{path}: {target}"
                    )

    def test_interface_does_not_require_login(self):
        self.assertEqual(self.client.get("/api/meta/enums").status_code, 200)
        scenario = self.client.get("/api/meta/defaults").json()
        response = self.client.post("/api/simulate", json={"scenario": scenario})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["errorCount"], 0)

    def test_existing_routes(self):
        self.assertEqual(self.client.get("/docs").status_code, 200)
        self.assertEqual(self.client.get("/public").json(), {"message": "Hello World"})
        self.assertEqual(self.client.get("/private").status_code, 401)
        paths = self.client.get("/openapi.json").json()["paths"]
        for path in ("/auth/login", "/validate/scenario", "/api/manifest/auto"):
            self.assertIn(path, paths)

    def test_scenario_errors_respond_unprocessable(self):
        scenario = self.client.get("/api/meta/defaults").json()
        scenario["missionList"] = [
            {
                "name": "Mission",
                "startDate": scenario["startDate"],
                "events": [],
                "demandModels": [],
                "origin": "00000000-0000-0000-0000-000000000000",
                "destination": "00000000-0000-0000-0000-000000000000",
            }
        ]
        response = self.client.post("/api/simulate", json={"scenario": scenario})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"][0]["type"], "scenario_error")
