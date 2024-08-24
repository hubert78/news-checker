import pandas as pd
import numpy as np

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timedelta
import re
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer


# Function to scrap news from Ghanaweb
def ghanaweb_scraper(category, end_date_str, start_date_str=None):
    data = []
    base_url = 'https://www.ghanaweb.com'

    # Convert the end_date from string to datetime object
    end_date = datetime.strptime(end_date_str, '%Y%m%d')
    
    # If no start_date is provided, default to today's date
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y%m%d')
    else:
        start_date = datetime.today()
        
    #date = start_date
    date_posted = start_date.strftime('%Y%m%d')

    while start_date >= end_date:
        url = f'https://www.ghanaweb.com/GhanaHomePage/{category}/browse.archive.php?date={date_posted}'
        response = requests.get(url)

        if response.status_code == 200:
            print(f"Fetching articles posted on {date_posted} for category {category}")

            # Parse the page content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the div with the specific class that contains the article links
            article_div = soup.find('div', {'class': 'upper'})

            if article_div:
                # Extract all links within that div
                articles = article_div.find_all('a')

                # Print each article's content
                for article in articles:
                    # Extract the title and relative URL from the href attribute
                    title = article.get('title')
                    relative_url = article.get('href')

                    if not relative_url or not title:
                        continue  # Skip if href or title is not present

                    # Construct the absolute URL
                    absolute_url = urljoin(base_url, relative_url)

                    print(f"Fetching article from: {absolute_url}")

                    response2 = requests.get(absolute_url)

                    if response2.status_code == 200:
                        soup2 = BeautifulSoup(response2.text, 'html.parser')

                        # Find the content paragraph, update the selector as needed
                        content = soup2.find('p', {'id': 'article-123'})  # Adjust selector as needed
                        if content:
                            #paragraphs = content.find_all('p')
                            #article_text = " ".join([p.text for p in paragraphs])
                            data.append({
                                "Source": "GhanaWeb",
                                "Category": category,
                                "Date Posted": start_date.date(),
                                "Title": title,
                                "URL": absolute_url,
                                "Content": content.text
                            })
                        else:
                            print(f"Content not found in {absolute_url}")
                    else:
                        print(f"Failed to retrieve the article page. Status code: {response2.status_code}")

            else:
                print(f"No articles found for {category} on {date_posted}.")

            # Go to the previous day
            start_date = start_date - timedelta(days=1)
            date_posted = start_date.strftime('%Y%m%d')

        else:
            print(f"Failed to retrieve the main page. Status code: {response.status_code}")
            break

    # Return a DataFrame if data was collected
    if data:
        return pd.DataFrame(data)
    else:
        print(f"No data was retrieved for {category}.")
        return pd.DataFrame(columns=["Source", "Category", "Date Posted", "Title", "URL", "Content"])







# Function to scrap news from My Joyonline
def joynews_scraper(category, sub_category, end_date):
    data = []
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    page_num = 1
    max_pages = 100  # Limit the maximum number of pages to scrape
    stop_scraping = False  # Flag to stop the outer loop

    while page_num <= max_pages and not stop_scraping:
        url = f'https://www.myjoyonline.com/{category}/{sub_category}/page/{page_num}/'
        response = requests.get(url)

        if response.status_code == 200:
            print(f"Fetching page {page_num}: {category} - {sub_category} ...")
            
            # Parse the page content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract all article divs
            articles = soup.find_all('div', {'class': 'home-section-story-list text-center'})

            if not articles:
                print("No more articles found. Stopping.")
                break  # Exit the loop if no articles are found

            # Print each article's content
            for article in articles:
                # Extract the relative URL from the href attribute
                article_url = article.find('a').get('href')
                title = article.find('h4').text
                if not article_url:
                    continue  # Skip if href is not present

                print(f"Fetching article from: {article_url}")

                response2 = requests.get(article_url)

                if response2.status_code == 200:
                    soup2 = BeautifulSoup(response2.text, 'html.parser')

                    # Find the posted date and compare
                    date_posted = soup2.find('i', class_='far fa-clock')
                    if date_posted:
                        date_posted = date_posted.parent.get_text(strip=True)
                        date_posted = datetime.strptime(date_posted, "%d %B %Y %I:%M%p").date()
                        print(f"Article posted on: {date_posted}")

                        # Check if the date exceeds the specified end_date
                        if date_posted < end_date:
                            print("Article date is older than end date. Stopping.")
                            stop_scraping = True
                            break  # Break out of the inner loop and stop processing further

                    # Find the content paragraph
                    content = soup2.find('div', {'id': 'article-text'})
                    if content:
                        paragraphs = content.find_all('p')
                        article_text = " ".join([p.text for p in paragraphs])
                        if article_text:
                            data.append({
                                "Source": "My Joy Online",
                                "Category": category,
                                "Date Posted": date_posted,
                                "Title": title,
                                "URL": article_url,
                                "Content": article_text
                            })
                            
                        else:
                            print(f"Content not found in {article_url}")
                    else:
                        print(f"Failed to find content in {article_url}")
                else:
                    print(f"Failed to retrieve the article page. Status code: {response2.status_code}")

            page_num += 1  # Move to the next page

        else:
            print(f"Failed to retrieve the main page. Status code: {response.status_code}")
            break  # Exit the loop if the main page can't be fetched
        
    if data:
        return pd.DataFrame(data)
    else:
        print(f"No data was retrieved for {category}.")
        return pd.DataFrame(columns=["Source", "Category", "Date Posted", "Title", "URL", "Content"])




# Download NLTK resources
#nltk.download('stopwords')
#nltk.download('punkt')
#nltk.download('wordnet')
#nltk.download('averaged_perceptron_tagger')

# Set of English stopwords
#stop_words = set(stopwords.words('english'))

# Initialize WordNet Lemmatizer
#lemmatizer = WordNetLemmatizer()


# Function for preprocessing
def get_wordnet_pos(word):
    """Map POS tag to first character lemmatize() accepts"""
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}
    return tag_dict.get(tag, wordnet.NOUN)

def clean_text(text):
    # Convert to lowercase
    text = text.lower()

    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)

    # Remove non-alphabetic characters, except spaces
    text = re.sub(r'[^a-z\s]', '', text)

    # Tokenization (split the text into words)
    tokens = nltk.word_tokenize(text)

    # Remove stopwords and words with length <= 1
    tokens = [word for word in tokens if word not in stop_words and len(word) > 1]

    # Lemmatization using NLTK's WordNetLemmatizer with POS tagging
    lemmatized_tokens = [lemmatizer.lemmatize(word, get_wordnet_pos(word)) for word in tokens]

    # Rejoin tokens into a single string
    cleaned_text = " ".join(lemmatized_tokens)
    return cleaned_text
