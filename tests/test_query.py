from fastapi.testclient import TestClient

from fast import app


def test_query_rejects_whitespace_only_input():
      with TestClient(app) as client:
          response = client.post(
              "/query",
              json={"query": "   "},
          )

      assert response.status_code == 422
      assert response.json()["detail"] == "Query cannot contain only spaces."