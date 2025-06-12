import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from news_fetcher import NewsFetcher, ArticleScraper, NewsDataset, NewsVisualizer

class NewsFetcherApp(tk.Tk):
    def __init__(self, fetcher, scraper):
        super().__init__()
        self.title("News Fetcher App")
        self.geometry("600x500")

        # Store fetcher, scraper, and dataset
        self.fetcher = fetcher
        self.scraper = scraper
        self.dataset = None
        self.visualizer = None

        # Search type option
        self.search_type_label = tk.Label(self, text="Search By:", font=("Helvetica", 12))
        self.search_type_label.pack(pady=5)
        
        self.search_type_var = tk.StringVar(value="category")
        search_type_option = ttk.Combobox(self, textvariable=self.search_type_var, values=["category", "keyword"], font=("Helvetica", 12))
        search_type_option.pack(pady=5)

        # Category Entry
        self.category_label = tk.Label(self, text="Enter News Category:", font=("Helvetica", 12))
        self.category_label.pack(pady=5)
        
        self.category_entry = tk.Entry(self, width=40, font=("Helvetica", 12))
        self.category_entry.pack(pady=5)

        # Keyword Entry
        self.keyword_label = tk.Label(self, text="Enter Search Keyword:", font=("Helvetica", 12))
        self.keyword_label.pack(pady=5)
        
        self.keyword_entry = tk.Entry(self, width=40, font=("Helvetica", 12))
        self.keyword_entry.pack(pady=5)

        # Number of Articles Entry
        self.num_articles_label = tk.Label(self, text="Number of Articles:", font=("Helvetica", 12))
        self.num_articles_label.pack(pady=5)
        
        self.num_articles_entry = tk.Entry(self, width=40, font=("Helvetica", 12))
        self.num_articles_entry.pack(pady=5)

        # Fetch Button
        self.fetch_button = tk.Button(self, text="Fetch News", font=("Helvetica", 12), command=self.fetch_news)
        self.fetch_button.pack(pady=10)

        # Visualize Button
        self.visualize_button = tk.Button(self, text="Visualize News", font=("Helvetica", 12), command=self.open_visualization_window)
        self.visualize_button.pack(pady=10)

        # Text area for displaying articles
        self.news_display_text = tk.Text(self, height=15, width=70, font=("Helvetica", 10), wrap=tk.WORD)
        self.news_display_text.pack(pady=10, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self, command=self.news_display_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.news_display_text.config(yscrollcommand=self.scrollbar.set)

        # Bind search type change event to disable Category/Keyword field accordingly
        self.search_type_var.trace("w", self.toggle_fields)

    def toggle_fields(self, *args):
        search_type = self.search_type_var.get()

        if search_type == "category":
            self.category_entry.config(state="normal")  # Enable Category entry
            self.keyword_entry.config(state="disabled")  # Disable Keyword entry
        else:
            self.category_entry.config(state="disabled")  # Disable Category entry
            self.keyword_entry.config(state="normal")  # Enable Keyword entry

    def fetch_news(self):
        category = self.category_entry.get()
        keyword = self.keyword_entry.get()
        num_articles = self.num_articles_entry.get()

        if not num_articles.isdigit():
            messagebox.showerror("Input Error", "Please enter a valid number of articles.")
            return
        
        num_articles = int(num_articles)

        # Fetch news based on search type
        if self.search_type_var.get() == "category" and category:
            self.dataset = NewsDataset(self.fetcher, self.scraper)
            self.dataset.build_dataset(category, num_articles)
        elif self.search_type_var.get() == "keyword" and keyword:
            self.dataset = NewsDataset(self.fetcher, self.scraper)
            self.dataset.build_dataset_from_keyword(keyword, num_articles)

        # Create Visualizer
        self.visualizer = NewsVisualizer(self.dataset.df)

        # Display articles after fetching
        self.display_news()

    def display_news(self):
        self.news_display_text.delete(1.0, tk.END)
        
        if self.dataset is None or self.dataset.df.empty:
            self.news_display_text.insert(tk.END, "No articles found.\n")
            return

        for idx, row in self.dataset.df.iterrows():
            self.news_display_text.insert(tk.END, f"{idx+1}. {row['title']}\n")
            self.news_display_text.insert(tk.END, f"Source: {row['source']}\n")
            self.news_display_text.insert(tk.END, f"Author: {row['author']}\n")
            self.news_display_text.insert(tk.END, f"Published At: {row['published_at']}\n")
            self.news_display_text.insert(tk.END, f"Description: {row['description']}\n")

            MAX_CONTENT_LENGTH = 1000
            content = row['full_content']
            if len(content) > MAX_CONTENT_LENGTH:
                content = content[:MAX_CONTENT_LENGTH] + "..."
            self.news_display_text.insert(tk.END, f"Full Content: {content}\n")


            # Insert the URL as clickable text
            start_idx = self.news_display_text.index(tk.END)
            self.news_display_text.insert(tk.END, f"Link: {row['url']}\n")
            end_idx = self.news_display_text.index(tk.END)

            # Tag the link and make it look like a hyperlink
            self.news_display_text.tag_add(f"link{idx}", start_idx, end_idx)
            self.news_display_text.tag_config(f"link{idx}", foreground="blue", underline=True)

            # Correct event binding by passing URL correctly
            self.news_display_text.tag_bind(f"link{idx}", "<Button-1>", lambda e, url=row['url']: self.open_url(url))

            self.news_display_text.insert(tk.END, "-"*50 + "\n\n")

    def open_url(self, url):
        import webbrowser
        webbrowser.open_new(url)

    def open_visualization_window(self):
        if self.visualizer is None:
            messagebox.showinfo("No Data", "Please fetch news first.")
            return

        # Create a new window
        vis_window = tk.Toplevel(self)
        vis_window.title("News Visualization")
        vis_window.geometry("900x700")

        # Dropdown for choosing visualization
        options = ["Source Distribution", "Publication Dates", "Top Authors", "Word Cloud", "Sentiment Distribution"]
        choice_var = tk.StringVar(value=options[0])

        dropdown = ttk.Combobox(vis_window, textvariable=choice_var, values=options, font=("Helvetica", 12))
        dropdown.pack(pady=10)

        # Area to draw the graph
        canvas_frame = tk.Frame(vis_window)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        def plot_selected(event=None):
            selected = choice_var.get()

            # Clear frame
            for widget in canvas_frame.winfo_children():
                widget.destroy()

            # Create figure
            if selected == "Source Distribution":
                fig = self.visualizer.plot_sources()
            elif selected == "Publication Dates":
                fig = self.visualizer.plot_dates()
            elif selected == "Top Authors":
                fig = self.visualizer.plot_authors()
            elif selected == "Word Cloud":
                fig = self.visualizer.plot_wordcloud()
            elif selected == "Sentiment Distribution":
                fig = self.visualizer.plot_sentiment_distribution()
            else:
                return

            # Draw figure in tkinter
            canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Plot when dropdown changes
        dropdown.bind("<<ComboboxSelected>>", plot_selected)

        # Initial plot
        plot_selected()

if __name__ == "__main__":
    # API key
    api_key = "5c90ea31921c45a58ada0e88494c2fdb"

    # Create fetcher and scraper
    fetcher = NewsFetcher(api_key)
    scraper = ArticleScraper()

    # Launch the App
    app = NewsFetcherApp(fetcher, scraper)
    app.mainloop()
