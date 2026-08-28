import json
import urllib.request
import urllib.parse
from xml.sax.saxutils import escape

PROJECT_ID = "ronpa-7b4ae"
BASE_URL = "https://sm-mask.github.io/RONPA/"

FIRESTORE_URL = (
    f"https://firestore.googleapis.com/v1/projects/"
    f"{PROJECT_ID}/databases/(default)/documents/topics"
)

topic_ids = []
page_token = None

while True:

    params = {
        "pageSize": "1000"
    }

    if page_token:
        params["pageToken"] = page_token

    url = (
        FIRESTORE_URL
        + "?"
        + urllib.parse.urlencode(params)
    )

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "RONPA-Sitemap-Generator"
        }
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=30
        ) as response:

            data = json.loads(
                response.read().decode("utf-8")
            )

    except Exception as error:

        print("Firestoreから議題を取得できませんでした。")
        print(error)

        raise


    for document in data.get(
        "documents",
        []
    ):

        name = document.get(
            "name",
            ""
        )

        topic_id = name.split("/")[-1]

        if topic_id:
            topic_ids.append(topic_id)


    page_token = data.get(
        "nextPageToken"
    )

    if not page_token:
        break


lines = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    "",
    "  <url>",
    f"    <loc>{escape(BASE_URL)}</loc>",
    "  </url>",
]


for topic_id in topic_ids:

    topic_url = (
        BASE_URL
        + "?topic="
        + urllib.parse.quote(
            topic_id,
            safe=""
        )
    )

    lines.extend([
        "",
        "  <url>",
        f"    <loc>{escape(topic_url)}</loc>",
        "  </url>",
    ])


lines.extend([
    "",
    "</urlset>",
    ""
])


with open(
    "sitemap.xml",
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "\n".join(lines)
    )


print(
    f"sitemap.xmlを更新しました："
    f"{len(topic_ids)}件の議題"
)
