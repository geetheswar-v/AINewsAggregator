import time
import requests
from bs4 import BeautifulSoup
import csv

# A custom defined function scrap article title, date of publication, article_description
def scrape_articles(url):
    articles_data = []

    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for non-200 status codes

    soup = BeautifulSoup(response.content, 'html.parser')

    articles = soup.find_all('listing-with-preview')
    for article in articles:
        article_url = article['article-url']
        # print(article_url)
        if 'pdf' in article_url.lower():
            continue
        title = article['article-title']
        date = article['publish-date-ap']
        temp = date.split(',')[0]
        date = temp.split(' ')[1] + ' ' + temp.split(' ')[0] + ',' + date.split(',')[1]

        article_response = requests.get(article_url)
        article_response.raise_for_status()  # Raise an exception for non-200 status codes

        article_soup = BeautifulSoup(article_response.content, 'html.parser')
        article_data = article_soup.find("div", attrs= {"class":"body"})

        if not article_data:
            continue

        description = article_data.get_text(strip=True, separator=" ")

        articles_data.append({'Title': title, 'Date': date, 'Description': description})

    # Write the data to a CSV file
    with open('articles_us.csv', 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Title', 'Date', 'Description']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if csvfile.tell() == 0:  # Check if file is empty
            writer.writeheader()

        for article_data in articles_data:
            writer.writerow(article_data)

# Url for the print news specified topic defence related to us
url_pattern = 'https://www.defense.gov/News/?Page={}'

# Range is specified according to scrap for 5 years of data
start_page = 1
end_page = 1149

for page_num in range(start_page, end_page + 1):
    print('Scraping page', page_num)
    url = url_pattern.format(page_num)
    scrape_articles(url)
    # Add a delay to avoid overwhelming the server
    time.sleep(1)