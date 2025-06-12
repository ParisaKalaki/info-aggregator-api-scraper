import requests
import json
import os
import time
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from bs4 import BeautifulSoup
from wordcloud import WordCloud
from textblob import TextBlob
from newspaper import Article



class NewsFetcher:
    def __init__(self, api_key, cache_dir="cache"):
        self.api_key = api_key
        self.base_url = 'https://newsapi.org/v2/top-headlines'
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def fetch_news_from_api(self, category=None, num_articles=5):
        # Check cache first
        cache_file = os.path.join(self.cache_dir, f"{category}_news.json" if category else "keyword_news.json")
        
        if os.path.exists(cache_file) and time.time() - os.path.getmtime(cache_file) < 3600:
            print(f"Loading cached data for {category or 'keyword search'}")
            with open(cache_file, "r") as f:
                return json.load(f)[:num_articles]

        # Otherwise, fetch from API
        params = {
            'apiKey': self.api_key,
            'pageSize': num_articles
        }
        if category:
            params['category'] = category
        response = requests.get(self.base_url, params=params)

        if response.status_code == 200:
            articles = response.json().get('articles', [])
            with open(cache_file, "w") as f:
                json.dump(articles, f)
            return articles[:num_articles]
        else:
            print(f"Error fetching news: {response.status_code}")
            return []

    def fetch_news_by_keyword(self, keyword, num_articles=5):
        url = 'https://newsapi.org/v2/everything'
        params = {
            'apiKey': self.api_key,
            'q': keyword,
            'pageSize': num_articles
        }
        
        response = requests.get(url, params=params)

        if response.status_code == 200:
            return response.json().get('articles', [])
        else:
            print(f"Error fetching news by keyword: {response.status_code}")
            return []

    def fetch_news(self, category=None, num_articles=5):
        return self.fetch_news_from_api(category, num_articles)       

class ArticleScraper:
    def scrape(self, url):
        try:
            article = Article(url)
            article.download()
            article.parse()
            return {
                'full_content': article.text,
                'author': article.authors[0] if article.authors else None,
                'published_at': article.publish_date.isoformat() if article.publish_date else None
            }
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return {'full_content': None, 'author': None, 'published_at': None}



class NewsDataset:
    def __init__(self, fetcher, scraper):
        self.fetcher = fetcher
        self.scraper = scraper
        self.df = pd.DataFrame()

    def build_dataset(self, category, num_articles=5):
        articles = self.fetcher.fetch_news(category, num_articles)
        data = []

        for article in articles:
            extra = self.scraper.scrape(article['url'])
            data.append({
                'title': article.get('title'),
                'description': article.get('description'),
                'source': article['source']['name'],
                'url': article['url'],
                'full_content': extra['full_content'],
                'author': extra['author'] or article.get('author'),
                'published_at': self.format_date(extra['published_at'] or article.get('publishedAt'))
            })

        self.df = pd.DataFrame(data)
        self.clean_data()
        self.analyze_sentiment()


    def build_dataset_from_keyword(self, keyword, num_articles=5):
        articles = self.fetcher.fetch_news_by_keyword(keyword, num_articles)
        data = []

        for article in articles:
            extra = self.scraper.scrape(article['url'])
            data.append({
                'title': article.get('title'),
                'description': article.get('description'),
                'source': article['source']['name'],
                'url': article['url'],
                'full_content': extra['full_content'],
                'author': extra['author'] or article.get('author'),
                'published_at': self.format_date(extra['published_at'] or article.get('publishedAt'))
            })

        self.df = pd.DataFrame(data)
        self.clean_data()
        self.analyze_sentiment()


    def clean_data(self):
        self.df.drop_duplicates(subset=['title', 'url'], inplace=True)
        self.df.fillna('Unknown', inplace=True)

    @staticmethod
    def format_date(date_str):
        if not date_str:
            return "Unknown"
        try:
            return pd.to_datetime(date_str).strftime('%Y-%m-%d %H:%M')
        except Exception:
            return "Unknown"
        
    def analyze_sentiment(self):
        sentiments = []
        for idx, row in self.df.iterrows():
            text = (row['title'] or '') + ' ' + (row['description'] or '')
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            if polarity > 0:
                sentiments.append('Positive')
            elif polarity < 0:
                sentiments.append('Negative')
            else:
                sentiments.append('Neutral')
        
        self.df['sentiment'] = sentiments



class NewsVisualizer:
    def __init__(self, dataset):
        self.dataset = dataset

    def plot_sources(self):
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.countplot(y='source', data=self.dataset, order=self.dataset['source'].value_counts().index, ax=ax)
        ax.set_title('Distribution of News Articles by Source')
        ax.set_xlabel('Number of Articles')
        ax.set_ylabel('Source')
        fig.tight_layout()
        return fig

    def plot_dates(self):
        self.dataset['published_at'] = pd.to_datetime(self.dataset['published_at'], errors='coerce')
        data = self.dataset.dropna(subset=['published_at'])

        fig, ax = plt.subplots(figsize=(12, 6))
        data['published_at'].dt.date.value_counts().sort_index().plot(kind='bar', ax=ax)
        ax.set_title('Number of Articles Published per Day')
        ax.set_xlabel('Date')
        ax.set_ylabel('Number of Articles')
        fig.autofmt_xdate()
        fig.tight_layout()
        return fig

    def plot_authors(self):
        fig, ax = plt.subplots(figsize=(12, 6))
        top_authors = self.dataset['author'].value_counts().nlargest(10)
        sns.barplot(x=top_authors.values, y=top_authors.index, hue=top_authors.index, palette='viridis', ax=ax)
        ax.set_title('Top 10 Authors by Number of Articles')
        ax.set_xlabel('Number of Articles')
        ax.set_ylabel('Author')
        fig.tight_layout()
        return fig

    def plot_wordcloud(self):
        text = ' '.join(self.dataset['title'].dropna().tolist())
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('Word Cloud of News Titles', fontsize=20)
        return fig
    

    def plot_sentiment_distribution(self):
        fig, ax = plt.subplots(figsize=(8, 6))
        sentiment_counts = self.dataset['sentiment'].value_counts()
        sns.barplot(x=sentiment_counts.index, y=sentiment_counts.values, hue=sentiment_counts.values, palette='coolwarm', ax=ax)
        ax.set_title('Sentiment Distribution of News Articles')
        ax.set_xlabel('Sentiment')
        ax.set_ylabel('Number of Articles')
        fig.tight_layout()
        return fig
