import requests

def get_wikipedia_extract(title):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"

    headers = {
        "User-Agent": "MyDjangoBot/1.0 (https://example.com; contact@example.com)"
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()
            return data.get("extract", "No extract available.")
        else:
            return f"Wikipedia page not found. Status code: {response.status_code}"

    except requests.exceptions.RequestException as e:
        return f"Wikipedia service unavailable: {e}"
