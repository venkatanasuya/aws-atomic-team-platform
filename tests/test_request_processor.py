import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("request_processor", ROOT / "scripts" / "request_processor.py")
rp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rp)

class RequestValidationTests(unittest.TestCase):
    def setUp(self):
        self.valid = {
            "request_id": "req-test-001",
            "resource_type": "s3_bucket",
            "team_name": "payments",
            "team_owner": "payments@example.com",
            "application_name": "payments-api",
            "environment": "dev",
            "project": "atomic-team-demo",
            "cost_center": "CC-1001",
            "region": "us-east-1",
            "bucket_suffix": "test-bucket-001",
            "purpose": "Unit test request"
        }

    def test_valid_request(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", encoding="utf-8", delete=False) as f:
            json.dump(self.valid, f)
            path = Path(f.name)
        try:
            self.assertEqual(rp.load_request(path)["resource_type"], "s3_bucket")
        finally:
            path.unlink(missing_ok=True)

    def test_missing_owner_rejected(self):
        data = dict(self.valid)
        del data["team_owner"]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", encoding="utf-8", delete=False) as f:
            json.dump(data, f)
            path = Path(f.name)
        try:
            with self.assertRaises(ValueError):
                rp.load_request(path)
        finally:
            path.unlink(missing_ok=True)

    def test_wrong_region_rejected(self):
        data = dict(self.valid)
        data["region"] = "eu-west-1"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", encoding="utf-8", delete=False) as f:
            json.dump(data, f)
            path = Path(f.name)
        try:
            with self.assertRaises(ValueError):
                rp.load_request(path)
        finally:
            path.unlink(missing_ok=True)

    def test_unsupported_resource_rejected(self):
        data = dict(self.valid)
        data["resource_type"] = "ec2"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", encoding="utf-8", delete=False) as f:
            json.dump(data, f)
            path = Path(f.name)
        try:
            with self.assertRaises(ValueError):
                rp.load_request(path)
        finally:
            path.unlink(missing_ok=True)

if __name__ == "__main__":
    unittest.main()
