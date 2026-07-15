import json
from opensearchpy import OpenSearch, helpers

from config import OPENSEARCH_HOST, OPENSEARCH_PORT, INDEX_NAME

client = OpenSearch(
    hosts=[{"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}],
    use_ssl=False,
    verify_certs=False,
)


def create_index():
    if client.indices.exists(index=INDEX_NAME):
        client.indices.delete(index=INDEX_NAME)
        print("Старый индекс удалён")

    client.indices.create(
        index=INDEX_NAME,
        body={
            "settings": {
                "analysis": {
                    "analyzer": {
                        "russian_analyzer": {"type": "russian"}
                    }
                }
            },
            "mappings": {
                "properties": {
                    "text": {"type": "text", "analyzer": "russian_analyzer"},
                    "date": {"type": "date"},
                    "link": {"type": "keyword"},
                }
            },
        },
    )
    print(f"Индекс '{INDEX_NAME}' создан")


def load_posts():
    with open("posts.json", "r", encoding="utf-8") as f:
        return json.load(f)


def bulk_index(posts: list):
    """
    Загружаем документы пачкой (bulk) — это намного быстрее,
    чем добавлять по одному через client.index() в цикле.
    """
    actions = [
        {
            "_index": INDEX_NAME,
            "_id": post["id"],
            "_source": post,
        }
        for post in posts
    ]

    success, errors = helpers.bulk(client, actions, raise_on_error=False)
    print(f"Загружено документов: {success}")
    if errors:
        print(f"Ошибок при загрузке: {len(errors)}")


def main():
    create_index()
    posts = load_posts()
    print(f"Постов в файле: {len(posts)}")
    bulk_index(posts)
    print("Готово! Индекс наполнен.")


if __name__ == "__main__":
    main()