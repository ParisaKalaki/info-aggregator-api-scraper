import unittest
import pandas as pd
from news_fetcher import NewsFetcher, ArticleScraper, NewsDataset

class TestNewsApp(unittest.TestCase):

    def setUp(self):
        self.api_key = '5c90ea31921c45a58ada0e88494c2fdb'
        self.fetcher = NewsFetcher(self.api_key)
        self.scraper = ArticleScraper()

    def test_fetch_news_by_category(self):
        """Ensure fetch_news returns articles when using a category."""
        articles = self.fetcher.fetch_news(category='technology', num_articles=5)
        self.assertIsInstance(articles, list)
        self.assertGreater(len(articles), 0, "No articles fetched by category")

    def test_fetch_news_by_keyword(self):
        """Ensure fetch_news_by_keyword returns articles."""
        articles = self.fetcher.fetch_news_by_keyword(keyword='climate', num_articles=5)
        self.assertIsInstance(articles, list)
        self.assertGreater(len(articles), 0, "No articles fetched by keyword")

    def test_scrape_article_returns_valid_structure(self):
        """Ensure scraper returns required fields."""
        result = self.scraper.scrape('https://edition.cnn.com')
        self.assertIsInstance(result, dict)
        for key in ['full_content', 'author', 'published_at']:
            self.assertIn(key, result, f"Missing '{key}' in scrape result")

    def test_dataset_building_and_cleaning(self):
        """Ensure dataset builds and cleans properly."""
        dataset = NewsDataset(self.fetcher, self.scraper)
        dataset.build_dataset(category='business', num_articles=3)
        df = dataset.df

        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(df.shape[0], 0, "Dataset is empty after build")

        # Check that no nulls exist after cleaning
        self.assertFalse(df.isnull().any().any(), "Dataset contains NaN values after cleaning")

        # Check for deduplication
        duplicates = df.duplicated(subset=['title', 'url']).sum()
        self.assertEqual(duplicates, 0, "Duplicates not removed properly")

    def test_sentiment_column_exists(self):
        """Ensure sentiment analysis column is created and contains valid values."""
        dataset = NewsDataset(self.fetcher, self.scraper)
        dataset.build_dataset(category='health', num_articles=3)

        self.assertIn('sentiment', dataset.df.columns, "Sentiment column not found in dataset")

        valid_sentiments = {'Positive', 'Neutral', 'Negative'}
        actual_sentiments = set(dataset.df['sentiment'].dropna().unique())
        self.assertTrue(
            actual_sentiments.issubset(valid_sentiments),
            f"Invalid sentiment values found: {actual_sentiments}"
        )

if __name__ == '__main__':
    unittest.main()
