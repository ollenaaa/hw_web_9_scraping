import requests
import json
from bs4 import BeautifulSoup
from mongoengine import connect
from models import Author, Quote

connect(db='AuthorsAndQuotes', host='127.0.0.1', port=27017)


def parse_data():
    url = 'https://quotes.toscrape.com/'
    next_url = url

    result_quotes = []
    links = set()

    while next_url:
        response = requests.get(next_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            try:
                next_url = f"{url}{soup.find(attrs={'class': 'next'}).find('a').attrs['href']}"
            except:
                break
            quotes = soup.find_all(attrs={'class': 'quote'})

            for quote in quotes:
                result_quotes.append({
                    "tags": quote.find(attrs={'class': 'keywords'}).attrs['content'].split(','),
                    "author": quote.find(attrs={'class': 'author'}).text.replace(" fils", ""),
                    "quote": quote.find(attrs={'class': 'text'}).text
                })
                links.add(f"{url}{quote.find('a').attrs['href']}")

    result_authors = []

    for link in links:
        response = requests.get(link)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            result_authors.append({
                "fullname": soup.find(attrs={'class': 'author-title'}).text.replace("-fils", ""),
                "born_date": soup.find(attrs={'class': 'author-born-date'}).text,
                "born_location": soup.find(attrs={'class': 'author-born-location'}).text,
                "description": soup.find(attrs={'class': 'author-description'}).text.replace('    \n    ', '').replace('\n        ', '')
            })
    return result_quotes, result_authors
    

def write_to_json(quotes, authors):
    with open("json/quotes.json", "w", encoding="utf-8") as fd:
        json.dump(quotes, fd, ensure_ascii=False, indent=4)

    with open("json/authors.json", "w", encoding="utf-8") as fd:
        json.dump(authors, fd, ensure_ascii=False, indent=4)


def load_authors_from_json():
    with open('json/authors.json', 'r') as file:
        data = json.load(file)

    for item in data:
        if Author.objects(fullname=item['fullname']).first():
            print(f"Author '{item['fullname']}' already exists in the database.")
        else:
            author_data = {
                    'fullname': item['fullname'],
                    'born_date': item['born_date'],
                    'born_location': item['born_location'],
                    'description': item['description']
                }
            
            author = Author(**author_data)
            author.save()
            
            print(f"New author '{author.fullname}' created.")


def load_quotes_from_json():
    with open('json/quotes.json', 'r') as file:
        data = json.load(file)

    for item in data:
        if Quote.objects(text=item['quote']).first():
            print(f"Quote '{item['quote']}' already exists in the database.")
        else:
            author_name = item['author']
            author = Author.objects(fullname=author_name).first().id

            quote_data = {
                        'text': item['quote'],
                        'author': author,
                        'tags': item['tags']
                    }
            
            quote = Quote(**quote_data)
            quote.save()
            print(f"New quote created.")


if __name__ == "__main__":
    quotes, authors = parse_data()
    write_to_json(quotes, authors)

    load_authors_from_json()
    load_quotes_from_json()
