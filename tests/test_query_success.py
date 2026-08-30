from fastapi.testclient import TestClient
from langchain_core.documents import Document

import fast


def test_query_returns_answer_and_sources(monkeypatch):
      fake_documents = [
          Document(
              page_content="Regression predicts continuous numerical values.",
              metadata={
                  "source": "sample.pdf",
                  "page": 2,
              },
          )
      ]

      monkeypatch.setattr(
          fast,
          "retriever",
          lambda query: fake_documents,
      )

      monkeypatch.setattr(
          fast,
          "chatbot",
          lambda question, context: "Regression predicts a continuous value.",
      )

      with TestClient(fast.app) as client:
          response = client.post(
              "/query",
              json={"query": "What is regression?"},
          )

      assert response.status_code == 200

      body = response.json()
      assert body["answer"] == "Regression predicts a continuous value."
      assert body["sources"] == [
          {
              "filename": "sample.pdf",
              "page": 3,
          }
      ]