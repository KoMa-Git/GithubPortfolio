import requests
from bs4 import BeautifulSoup
import random

def random_quote():
    URL = "https://www.goodreads.com/quotes?page=" + str(random.randint(1,100))
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    response = requests.get(URL, headers=headers,timeout=10)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        print("clearly worked")
    else:
        print(f"Failed to get page. Status code: {response.status_code}")

    div_quotes = soup.find_all("div", class_="quoteText")
    #for q in div_quotes:
    #    print(q.text.split("\n")[1].strip(), "-", q.text.split("\n")[5].strip())
    random_index = random.randint(0, len(div_quotes)-1)

    return {div_quotes[random_index].text.split("\n")[5].strip() : div_quotes[random_index].text.split("\n")[1].strip()}