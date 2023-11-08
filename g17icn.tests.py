import unittest
import tempfile
import g17jwt

# contributors: [nrobinso-7.11.23]
import tempfile
import unittest
class TestJWTManager(unittest.TestCase):
    def test_jwt_operations(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            jwts = g17jwt.JWT()
            jwts.init_jwt()
            payload = {"user_id": 123, "username": "john_doe"}
            encoded_token = jwts.encode(payload)
            decoded_payload = jwts.decode(encoded_token)
            self.assertEqual(decoded_payload, payload)

if __name__ == "__main__":
    unittest.main()