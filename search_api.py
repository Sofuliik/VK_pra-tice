from fastapi import FastAPI, Query
from opensearchpy import OpenSearch

from config import OPENSEARCH_HOST, OPENSEARCH_PORT, INDEX_NAME

app = FastAPI(title="MISIS Search")

client = OpenSearch(
    hosts=[{"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}],
    use_ssl=False,
    verify_certs=False,
)


@app.get("/")
def root():
    return {"status": "ok", "info": "Поисковик по паблику VK. Используйте /search?q=ваш запрос"}


@app.get("/search")
def search(q: str = Query(..., description="Поисковый запрос"),
           size: int = Query(5, ge=1, le=50, description="Сколько результатов вернуть")):
    body = {
        "query": {
            "match": {"text": q}
        },
        "size": size,
    }

    response = client.search(index=INDEX_NAME, body=body)
    hits = response["hits"]["hits"]

    results = [
        {
            "score": hit["_score"],
            "text": hit["_source"]["text"],
            "link": hit["_source"]["link"],
            "date": hit["_source"]["date"],
        }
        for hit in hits
    ]

    return {"query": q, "count": len(results), "results": results}