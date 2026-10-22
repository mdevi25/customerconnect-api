import unittest
from fastapi.testclient import TestClient
from app.main import app


class ServiceCatalogTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_services_returns_200(self):
        response = self.client.get("/services")
        self.assertEqual(response.status_code, 200)

    def test_02_services_returns_three_records(self):
        response = self.client.get("/services")
        services = response.json()
        self.assertEqual(len(services), 3)

    def test_03_services_have_required_fields(self):
        response = self.client.get("/services")
        services = response.json()

        for service in services:
            with self.subTest(service=service):
                self.assertIn("service_id", service)
                self.assertIn("name", service)
                self.assertIn("description", service)
                self.assertTrue(service["service_id"])
                self.assertTrue(service["name"])
                self.assertTrue(service["description"])

    def test_04_expected_services_available(self):
        response = self.client.get("/services")
        service_ids = {
            service["service_id"]
            for service in response.json()
        }

        self.assertEqual(
            service_ids,
            {"TECH", "BILLING", "ACCOUNT"}
        )


if __name__ == "__main__":
    unittest.main()
