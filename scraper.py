import streamlit as st
import pandas as pd
import numpy as np
import os 
import random
from requests.exceptions import RequestException

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timedelta



def check_duplicates(df):
    initial_df_total = df.shape[0]
    duplicates = df.duplicated(subset=['URL']).sum()
    df = df.drop_duplicates(subset=['URL'])
    cleaned_df_total = df.shape[0]
    st.info(f'{initial_df_total} articles retrieved.\n'
            f'{duplicates} article(s) with same URL found.\n'
            f'{cleaned_df_total} articles remain after cleaning.')
    return df

# Function to scrap news from Ghanaweb
def ghanaweb_scraper(category, end_date_str, start_date_str=None):
    data = []
    base_url = 'https://www.ghanaweb.com'

    end_date = datetime.strptime(end_date_str, '%Y%m%d')
    
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y%m%d')
    else:
        start_date = datetime.today()
    date_posted = start_date.strftime('%Y%m%d')

    while start_date >= end_date:
        try:
            url = f'https://www.ghanaweb.com/GhanaHomePage/{category}/browse.archive.php?date={date_posted}'
            response = requests.get(url)
        except:
            continue

        if response.status_code == 200:
            print(f"Fetching articles posted on {date_posted} for category {category}")

            soup = BeautifulSoup(response.text, 'html.parser')
            article_div = soup.find('div', {'class': 'upper'})

            if article_div:
                articles = article_div.find_all('a')
                for article in articles:
                    title = article.get('title')
                    relative_url = article.get('href')

                    if not relative_url or not title:
                        continue  
                    absolute_url = urljoin(base_url, relative_url)

                    print(f"Fetching article from: {absolute_url}")
                    try:
                        response2 = requests.get(absolute_url)
                    except:
                        continue

                    if response2.status_code == 200:
                        soup2 = BeautifulSoup(response2.text, 'html.parser')
                        content = soup2.find('p', {'id': 'article-123'})  
                        if content:
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

            start_date = start_date - timedelta(days=1)
            date_posted = start_date.strftime('%Y%m%d')

        else:
            print(f"Failed to retrieve the main page. Status code: {response.status_code}")
            break

    if data:
        return pd.DataFrame(data)
    else:
        print(f"No data was retrieved for {category}.")
        return pd.DataFrame(columns=["Source", "Category", "Date Posted", "Title", "URL", "Content"])


def ghanaweb_multi_scraper(source_data):
    scraped_df = pd.DataFrame(columns=["Source", "Category", "Date Posted", "Title", "URL", "Content"])
    start_date = source_data['start_date'].strftime('%Y%m%d')
    end_date = source_data['end_date'].strftime('%Y%m%d')

    for category in source_data['categories']:
        with st.spinner(f'Scraping articles from Ghanaweb. Category = {category}'):
            df = ghanaweb_scraper(category, end_date, start_date)
            if df is not None and not df.empty:
                scraped_df = pd.concat([scraped_df, df], axis=0, ignore_index=True)
    return scraped_df




# Function to scrap news from My Joyonline
def joynews_scraper(category, sub_category, end_date):
    data = []
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    page_num = 1
    max_pages = 100  
    stop_scraping = False  
    while page_num <= max_pages and not stop_scraping:
        try:
            url = f'https://www.myjoyonline.com/{category}/{sub_category}/page/{page_num}/'
            response = requests.get(url)
        except:
            print(f"Failed to get to {url}")
            continue

        if response.status_code == 200:
            print(f"Fetching page {page_num}: {category} - {sub_category} ...")

            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find_all('div', {'class': 'home-section-story-list text-center'})
            if not articles:
                print("No more articles found. Stopping.")
                break  

            for article in articles:
                # Extract the relative URL from the href attribute
                article_url = article.find('a').get('href')
                title = article.find('h4').text
                if not article_url:
                    continue  

                print(f"Fetching article from: {article_url}")
                try:
                    response2 = requests.get(article_url)
                except: 
                    break

                if response2.status_code == 200:
                    soup2 = BeautifulSoup(response2.text, 'html.parser')

                    date_posted = soup2.find('i', class_='far fa-clock')
                    if date_posted:
                        date_posted = date_posted.parent.get_text(strip=True)
                        date_posted = datetime.strptime(date_posted, "%d %B %Y %I:%M%p").date()
                        print(f"Article posted on: {date_posted}")

                        if date_posted < end_date:
                            print("Article date is older than end date. Stopping.")
                            stop_scraping = True
                            break  

                    content = soup2.find('div', {'id': 'article-text'})
                    if content:
                        paragraphs = content.find_all('p')
                        article_text = " ".join([p.text for p in paragraphs])
                        if article_text:
                            data.append({
                                "Source": "MyJoyOnline",
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

            page_num += 1  
        else:
            print(f"Failed to retrieve the main page. Status code: {response.status_code}")
            break 

    if data:
        return pd.DataFrame(data)
    else:
        print(f"No data was retrieved for {category}.")
        return pd.DataFrame(columns=["Source", "Category", "Date Posted", "Title", "URL", "Content"])


def joynews_multi_scraper(source_data):
    scraped_df = pd.DataFrame(columns=["Source", "Category", "Date Posted", "Title", "URL", "Content"])
    categories = {
        "news": ["national", "politics", "crime", "africa" "regional", "technology", "oddly-enough", "diaspora", "international", "health", "education", "obituary"],
        "business": ["economy", "energy", "finance", "mining", "agribusiness", "real-estate", "telecom", "aviation", "banking", "technology-business"],
        "entertainment": ["movies", "music", "radio-tv", "stage", "art-design", "books"],
        "sports": ["football", "boxing", "athletics", "tennis", "golf", "other-sports"],
        "opinion": [""],
    }

    start_date = source_data['start_date']
    end_date = source_data['end_date'].strftime('%Y-%m-%d')

    for category in categories:
        if category in source_data['categories']:
            with st.spinner(f'Scraping articles from MyJoyOnline. Category = {category}'):
                for sub_category in categories[category]:
                    df = joynews_scraper(category, sub_category, end_date)
                    if df is not None and not df.empty:
                        scraped_df = pd.concat([scraped_df, df], axis=0, ignore_index=True)

    scraped_df = scraped_df[scraped_df['Date Posted']<= start_date]
    return scraped_df




def modernghana_scraper(end_date_str, start_date_str=None):
    data = []
    base_url = 'https://www.modernghana.com'
    end_date = datetime.strptime(end_date_str, '%Y%m%d')
    
    # If no start_date is provided, default to today's date
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y%m%d')
    else:
        start_date = datetime.today()
        
    # Date to start scraping
    date_posted = start_date.strftime('%Y%m%d')

    # List of user agents Custom headers to mimic a browser
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/88.0',
        # Add more user agents
    ]
    while start_date >= end_date:
        headers = {
            'User-Agent': random.choice(user_agents),
        }
        try:
            url = f'https://www.modernghana.com/archive/{date_posted}/'
            response = requests.get(url, headers=headers)
        except:
            continue
            
        if response.status_code == 200:
            print(f"Fetching articles posted on {date_posted}")

            # Parse the page content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the div with the specific class that contains the article links
            article_div = soup.find('div', {'class': 'row news-archive2'})

            if article_div:
                # Extract all links within that div
                a_tags = article_div.find_all('a')

                # Print each article's content
                for a in a_tags:
                    # Extract the title and relative URL from the href attribute
                    title = a.text.strip()
                    relative_url = a.get('href')

                    if not relative_url or not title:
                        continue  # Skip if href or title is not present

                    # Construct the absolute URL
                    absolute_url = urljoin(base_url, relative_url)

                    print(f"Fetching article from: {absolute_url}")
                    
                    try:
                        response2 = requests.get(absolute_url, headers=headers)
                    except:
                        continue
                    
                    if response2.status_code == 200:
                        soup2 = BeautifulSoup(response2.text, 'html.parser')

                        # Find the content paragraph
                        content = soup2.find('div', {'id': 'article-123'})
                        if content:
                            paragraphs = content.find_all('p')
                            article_text = " ".join([p.text for p in paragraphs])
                            if article_text:
                                data.append({
                                    "Source": "Modern Ghana",
                                    "Category": "",
                                    "Date Posted": date_posted,
                                    "Title": title,
                                    "URL": absolute_url,
                                    "Content": article_text
                                })
                        else:
                            print(f"Content not found in {absolute_url}")
                    else:
                        print(f"Failed to retrieve the article page. Status code: {response2.status_code}")
            else:
                print(f"No articles found on {date_posted}.")

            # Go to the previous day
            start_date = start_date - timedelta(days=1)
            date_posted = start_date.strftime('%Y%m%d')

        else:
            st.write(f"Failed to retrieve articles from Moodern Ghana. Status code: {response.status_code}")
            # Go to the previous day
            start_date = start_date - timedelta(days=1)
            date_posted = start_date.strftime('%Y%m%d')
            
            continue

    # Return a DataFrame if data was collected
    if data:
        return pd.DataFrame(data)
    else:
        print(f"No data was retrieved.")
        return pd.DataFrame(columns=["Source", "Category", "Date Posted", "Title", "URL", "Content"])
    



def modernghana_multi_scraper(source_data):
    scraped_df = pd.DataFrame(columns=["Source", "Category", "Date Posted", "Title", "URL", "Content"])
    start_date = source_data['start_date'].strftime('%Y%m%d')
    end_date = source_data['end_date'].strftime('%Y%m%d')

    with st.spinner('Scraping articles from Modern Ghana.'):
        scraped_df = modernghana_scraper(end_date, start_date)

    return scraped_df





