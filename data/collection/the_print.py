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

    articles = soup.find_all('div', class_='tdb_module_loop td_module_wrap td-animation-stack td-cpt-post')

    for article in articles:
        title_element = article.find('h3', class_='entry-title td-module-title')
        title = title_element.find('a').text.strip()
        date = article.find('time', class_='entry-date').text.strip()
        article_url = title_element.find('a')['href']

        article_response = requests.get(article_url)
        article_response.raise_for_status()  # Raise an exception for non-200 status codes

        article_soup = BeautifulSoup(article_response.content, 'html.parser')

        postexcerpt_div = article_soup.find('div', id='postexcerpt')
        postcontent_div = article_soup.find('div', id='postcontent')

        if postcontent_div:
            ltr_paragraphs = postcontent_div.find_all('p', attrs={'dir': 'ltr'})
            for ltr_paragraph in ltr_paragraphs:
                ltr_paragraph.decompose()

        articles_prev_desc = postexcerpt_div.get_text(strip=True, separator=' ').replace('Show Full Article', '') if postexcerpt_div else ''
        article_more_desc = postcontent_div.get_text(strip=True, separator='') if postcontent_div else ''
        description = articles_prev_desc + ' ' + article_more_desc

        articles_data.append({'Title': title, 'Date': date, 'Description': description})

    # Write the data to a CSV file
    with open('articles.csv', 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Title', 'Date', 'Description']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if csvfile.tell() == 0:  # Check if file is empty
            writer.writeheader()

        for article_data in articles_data:
            writer.writerow(article_data)

# Url for the print news specified topic defence
url_pattern = 'https://theprint.in/category/defence/page/{}/'

# Range is specified according to scrap for 5 years of data
start_page = 0
end_page = 276

for page_num in range(start_page, end_page + 1):
    print('Scraping page', page_num)
    url = url_pattern.format(page_num)
    scrape_articles(url)
    # Add a delay to avoid overwhelming the server
    time.sleep(1)
