from fastapi.testclient import TestClient

from fast import app


def test_upload_rejects_non_pdf_file():
      with TestClient(app) as client:
          response = client.post(
              "/upload",
              files={
                  "file": (
                      "notes.txt",
                      b"This is not a PDF.",
                      "text/plain",
                  )
              },
          )

      assert response.status_code == 400
      assert response.json()["detail"] == "Only pdf files are allowed."