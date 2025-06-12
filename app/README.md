# 🗞️ Python News Aggregator

## 📌 About the Project

This is a Python-based news aggregator app with a clean, interactive Tkinter GUI. It lets you fetch the latest news either by category (like sports, business, etc.) or custom keyword (like "AI", "Bitcoin"). The app scrapes extra info from articles, analyzes sentiment, and gives you visual insights using graphs and word clouds.

The project is modularized into:

- **gui_app.py** — The main Tkinter GUI app, managing user interaction, displaying news, and showing visualizations.
- **news_fetcher.py** — Contains the core news fetching, scraping, dataset building, and visualization logic.
- **test_news_app.py** — Automated unit tests to verify news fetching, scraping, dataset integrity, and sentiment analysis.

## ✨ Features

- 🔍 Search news by **category** or **custom keyword** (one input disables the other for clarity).
- 📄 Scrapes full article details including author, full text, and publish date.
- 📊 Provides visual breakdowns including:
  - Articles per **news source**
  - Daily **publication counts**
  - **Top authors**
  - **Word cloud** of headlines
  - **Sentiment analysis** (positive / neutral / negative)
- ⚡ Implements caching to reduce API calls and speed up fetching.
- 🖥️ Simple, clean **Tkinter-based GUI** for easy interaction.
- 🧪 Includes **automated unit tests** in `test_news_app.py` to ensure reliability of fetching, scraping, and analysis.

## 🚀 How to Use

1. Open the app (`python GUI_app.py`).
2. Enter a news **category** (like `technology`) or a **keyword** (like `football`).
3. Choose how many articles you want.
4. Hit **Fetch News** to see results.
5. Use **Visualize News** to explore graphs and sentiment stats.

> Tip: If you enter a keyword, the category field is auto-disabled (and vice versa) so you don’t have to worry about choosing both.

## 🧪 Installation

1. Download and extract the project files to any folder.
2. Navigate to the app directory:
   ```bash
   cd app
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python GUI_app.py
   ```

## 🧪 Testing

- Automated unit tests are included in `test_news_app.py`.
- Tests cover:
  - News fetching by category and keyword.
  - Article scraping and extraction of content, author, and publish date.
  - Dataset building, cleaning, and deduplication.
  - Sentiment analysis correctness and presence in the dataset.
- Run tests with:
  ```bash
  python -m unittest test_news_app.py
  ```

## Usage

1. When the application starts, select a news category (e.g., sports, technology, business).
2. Enter the number of articles you want to fetch.
3. Click the "Fetch News" button to retrieve and display articles.
4. View visualizations like top sources, publication dates, authors, and word clouds.

## License

This project is licensed under the [MIT License](LICENSE).
