import sys
from crawl import LinkCrawler, DataCrawler


def main():
    """
    Command-line interface for scraping post links or data.

    Usage:
        python script_name.py scrape_posts_links
            - Starts the LinkCrawler to scrape post links.

        python script_name.py scrape_posts_data
            - Starts the DataCrawler to scrape post data.
    """
    if len(sys.argv) != 2:
        print("Usage: python script_name.py [scrape_posts_links|scrape_posts_data]")
        return

    cmd = sys.argv[1]
    if cmd == 'scrape_posts_links':
        # Initialize and start the LinkCrawler to scrape post links.
        crawler = LinkCrawler()
        crawler.start()
    elif cmd == 'scrape_posts_data':
        # Initialize and start the DataCrawler to scrape post data.
        crawler = DataCrawler()
        crawler.start()
    else:
        print("Invalid command. Use 'scrape_posts_links' or 'scrape_posts_data'.")


if __name__ == "__main__":
    main()
