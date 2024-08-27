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



def get_user_agent():
    # List of user agents Custom headers to mimic a browser
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/88.0',
        # Add more user agents
    ]
    return {
        'User-Agent': random.choice(user_agents),
    }


def check_duplicates(df):
    initial_df_total = df.shape[0]
    duplicates = df.duplicated(subset=['URL']).sum()
    df = df.drop_duplicates(subset=['URL'])
    cleaned_df_total = df.shape[0]
    st.info(f'{initial_df_total} articles retrieved.\n'
            f'{duplicates} article(s) with duplicate URL(s) found.\n'
            f'{cleaned_df_total} articles remain after cleaning.')
    return df, duplicates

# Function to scrap news from Ghanaweb
@st.cache_data
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
        headers = get_user_agent()
        try:
            url = f'https://www.ghanaweb.com/GhanaHomePage/{category}/browse.archive.php?date={date_posted}'
            response = requests.get(url, headers=headers)
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
                                "Source": "Ghanaweb",
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

#@st.cache_data
def ghanaweb_multi_scraper(source_data):
    scraped_df = pd.DataFrame(columns=["Source", "Category", "Date Posted", "Title", "URL", "Content"])
    start_date = source_data['start_date'].strftime('%Y%m%d')
    end_date = source_data['end_date'].strftime('%Y%m%d')

    for category in source_data['categories']:
        with st.spinner(f'Fetching articles from Ghanaweb. Category = {category.upper()}'):
            df = ghanaweb_scraper(category, end_date, start_date)
            if df is not None and not df.empty:
                scraped_df = pd.concat([scraped_df, df], axis=0, ignore_index=True)
    return scraped_df




# Function to scrap news from My Joyonline
@st.cache_data
def joynews_scraper(category, sub_category, end_date):
    data = []
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    page_num = 1
    max_pages = 100  
    stop_scraping = False  
    while page_num <= max_pages and not stop_scraping:
        headers = get_user_agent()
        try:
            url = f'https://www.myjoyonline.com/{category}/{sub_category}/page/{page_num}/'
            response = requests.get(url, headers=headers)
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


#@st.cache_data
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
            with st.spinner(f'Fetching articles from MyJoyOnline. Category = {category.upper()}'):
                for sub_category in categories[category]:
                    df = joynews_scraper(category, sub_category, end_date)
                    if df is not None and not df.empty:
                        scraped_df = pd.concat([scraped_df, df], axis=0, ignore_index=True)

    scraped_df = scraped_df[scraped_df['Date Posted']<= start_date]
    return scraped_df



@st.cache_data
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

    while start_date >= end_date:
        headers = get_user_agent()
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
            st.write(f"Failed to retrieve articles from Moodern Ghana on {date_posted}. Status code: {response.status_code}")
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
    


#@st.cache_data
def modernghana_multi_scraper(source_data):
    scraped_df = pd.DataFrame(columns=["Source", "Category", "Date Posted", "Title", "URL", "Content"])
    start_date = source_data['start_date'].strftime('%Y%m%d')
    end_date = source_data['end_date'].strftime('%Y%m%d')

    with st.spinner('Fetching articles from Modern Ghana.'):
        scraped_df = modernghana_scraper(end_date, start_date)

    return scraped_df





@st.cache_data
def yenghana_scraper(category, end_date):
    
    data = []
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    page_num = 1
    max_pages = 100  
    stop_scraping = False 

    while page_num <= max_pages and not stop_scraping:
        headers = get_user_agent()
            
        try:
            url = url = f"https://yen.com.gh/ajax/posts/?page={page_num}&category_id={category}"
            response = requests.get(url, headers=headers)
        except requests.RequestException as e:
            print(f"Failed to get {url}: {e}")
            page_num += 1
            continue

        if response.status_code == 200:
            print(f"Fetching page {page_num}: {category}...")
            
            json_data = response.json()
            html_content = json_data['response']

            soup = BeautifulSoup(html_content, 'html.parser')

            # Find all article elements
            articles = soup.find_all('article', class_='c-article-card-horizontal')

            # Extract titles and URLs
            for article in articles:
                title_tag = article.find('img', class_='thumbnail-picture__img')
                if title_tag:
                    title = title_tag['alt'].strip()

                    # Find the article's URL
                    url_tag = article.find('a')
                    if url_tag and 'href' in url_tag.attrs:
                        article_url = url_tag['href']

                print(f"Fetching article from: {article_url}")

                response2 = requests.get(article_url)

                if response2.status_code == 200:
                    soup2 = BeautifulSoup(response2.text, 'html.parser')

                    # Find the posted date and compare
                    date_posted = soup2.find('div', {'class': 'c-article-info post__info'})
                    if date_posted:
                        date_posted = date_posted.find('time').get('datetime')
                        date_posted = datetime.strptime(date_posted, '%Y-%m-%dT%H:%M:%S%z').date()
                        print(f"Article posted on: {date_posted}")

                        # Check if the date exceeds the specified end_date
                        if date_posted < end_date:
                            print("Article date is older than end date. Stopping.")
                            stop_scraping = True
                            break  # Break out of the inner loop and stop processing further

                    # Find the content paragraph
                    content = soup2.find('div', {'class': 'post__content'})
                    if content:
                        paragraphs = content.find_all('p')
                        article_text = " ".join([p.text for p in paragraphs])
                        if article_text:
                            data.append({
                                "Source": "Yen Ghana",
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
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            page_num += 1  
            continue  
        
    if data:
        return pd.DataFrame(data)
    else:
        print(f"No data was retrieved for {category}.")
        return pd.DataFrame(columns=["Source", "Category", "Date Posted", "Title", "URL", "Content"])
    


def yenghana_multi_scraper(source_data):
    scraped_df = pd.DataFrame(columns=["Source", "Category", "Date Posted", "Title", "URL", "Content"])

    categories_id = {
        'Politics': [53],
        'Ghana': [21079],
        'Business': [21084, 21087, 21088, 21089, 21090],
        'Entertainment': [21097, 21098, 21099, 21116, 21096],
        'Sports': [21103, 21102],
        'World': [21081, 21083, 21077, 21082],
    }

    start_date = source_data['start_date']
    end_date = source_data['end_date'].strftime('%Y-%m-%d')

    for source_category in source_data['categories']:
        if source_category in categories_id:
            category_ids = categories_id[source_category]
            with st.spinner(f'Fetching articles from Yen Ghana. Category = {source_category.upper()}'):
                for sub_category in category_ids:
                    df = yenghana_scraper(sub_category, end_date)
                    if df is not None and not df.empty:
                        df['Date Posted'] = pd.to_datetime(df['Date Posted']).dt.date
                        scraped_df = pd.concat([scraped_df, df], axis=0, ignore_index=True)

    # Filter the articles based on the start date
    scraped_df = scraped_df[scraped_df['Date Posted'] <= start_date]
    return scraped_df



@st.cache_data
def news3_scraper(category, sub_category, end_date_str):
    data = []
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    page_num = 1
    max_pages = 100
    stop_scraping = False

    while page_num <= max_pages and not stop_scraping:
        headers = get_user_agent()
        try:
            url = f'https://3news.com/{category}{sub_category}/page/{page_num}/'
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to get {url}: {e}")
            break  # Break if there's a request error

        if response.status_code == 200:
            print(f"Fetching page {page_num}: {category}{sub_category}...")
            soup = BeautifulSoup(response.text, 'html.parser')
            article_div = soup.find('div', {'id': 'tdi_51'})

            if article_div:
                h3_tags = article_div.find_all('h3', {'class': 'entry-title td-module-title'})

                for h3 in h3_tags:
                    tag = h3.find('a')
                    title = tag.text.strip()
                    article_url = tag.get('href')

                    if not article_url or not title:
                        continue

                    print(f"Fetching article from: {article_url}")
                    try:
                        response2 = requests.get(article_url, headers=headers)
                        response2.raise_for_status()
                    except requests.RequestException as e:
                        print(f"Failed to get article {article_url}: {e}")
                        continue

                    if response2.status_code == 200:
                        soup2 = BeautifulSoup(response2.text, 'html.parser')
                        p_head = soup2.find('header', class_='td-post-title')
                        date_tag = p_head.find('time', class_='entry-date updated td-module-date')
                        
                        if date_tag:
                            datetime_str = date_tag['datetime']
                            date_posted = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S%z').date()
                            print(date_posted)


                            # Check if the date is older than the specified end_date
                            if date_posted < end_date:
                                print(f"Article date {date_posted} is older than end date {end_date}. Stopping.")
                                stop_scraping = True
                                break
                            
                            content = soup2.find('div', class_='td-post-content tagdiv-type')
                            paragraphs = content.find_all('p')
                            article_text = " ".join([p.text for p in paragraphs])
                            if article_text:
                                data.append({
                                    "Source": "3News",
                                    "Category": category,
                                    "Date Posted": date_posted,
                                    "Title": title,
                                    "URL": article_url,
                                    "Content": article_text
                                })
                            else:
                                print(f"Content not found in {article_url}")
                    else:
                        print(f"Failed to retrieve the article page. Status code: {response2.status_code}")
                        continue
            else:
                print(f"No articles found for {category} on page {page_num}.")
                break  

        else:
            print(f"Failed to retrieve the page {page_num} for {category}{sub_category}. Status code: {response.status_code}")
            page_num += 1
            continue  

        page_num += 1

    if data:
        return pd.DataFrame(data)
    else:
        print(f"No data was retrieved for {category}.")
        return pd.DataFrame(columns=["Source", "Category", "Date Posted", "Title", "URL", "Content"])
    


def new3_multi_scraper(source_data):
    scraped_df = pd.DataFrame(columns=["Source", "Category", "Date Posted", "Title", "URL", "Content"])

    categories = {
        'news': ['', '/politics', '/education', '/world'],
        'elections': [''],
        'business': [''],
        'showbiz': ['', '/celebrities', '/movies', '/music'],
        'sports': [''],
        'health': [''],
        'opinion': ['', '/cartoon'],
    }

    start_date = source_data['start_date']
    end_date = source_data['end_date'].strftime('%Y-%m-%d')
    
    for source_category in source_data['categories']:
        if source_category in categories:
            category = categories[source_category]
            with st.spinner(f'Fetching articles from 3News. Category = {source_category.upper()}'):
                for sub_category in category:
                    df = news3_scraper(source_category, sub_category, end_date)
                    if df is not None and not df.empty:
                        df['Date Posted'] = pd.to_datetime(df['Date Posted']).dt.date
                        scraped_df = pd.concat([scraped_df, df], axis=0, ignore_index=True)

    # Filter the articles based on the start date
    scraped_df = scraped_df[scraped_df['Date Posted'] <= start_date]
    return scraped_df

