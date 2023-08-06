import json
from abc import ABC, abstractmethod
from config import BASE_LINK, STORE_PATH
from bs4 import BeautifulSoup
import requests
from logger import setup_logging
from utils import create_directory, pdf_generator, rename_file

data_crawler_logger = setup_logging('./Logs/data_crawling_logs.txt')
link_crawler_logger = setup_logging('./Logs/link_crawling_logs.txt')


class CrawlerBase(ABC):
    """
    Abstract to enforce all classes to have start and store method.
    """
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def store(self):
        pass


class LinkCrawler(CrawlerBase):
    """
        LinkCrawler is a class that efficiently crawls a website to extract post links.

        Attributes:
            base_url (str): The base URL of the website to be crawled.
            path (str): The path where the scraped post links will be stored.
            all_post_links (list): A list to store all the extracted post links.
  """
    def __init__(self, base_url=BASE_LINK, path=STORE_PATH):
        self.all_post_links = []
        self.path = path
        self.base_url = base_url

    def get_page(self, url, start=1):

        """
        The function send request based on url and start, it will return response back.
        The start values used to crawl special pages based on navigation
        :param url: base url link
        :param start: number of the page
        :return: response data
        """
        try:
            response = requests.get(url+f"/page/{start}")
        except:
            return None
        return response

    def find_last_page(self):
        """
        This method finds last page number in the site.
        :return: The int number of the last page
        """
        # request and receive response of the first page
        html_doc = self.get_page(self.base_url).text
        # find last page number
        soup = BeautifulSoup(html_doc, features="html.parser")
        return int(soup.find_all('a', attrs={'class': 'page-numbers'})[-2].text)

    @staticmethod
    def find_post_links_for_page(html_doc):
        """
        Finds all post links in a page
        :param html_doc: html source code
        :return: A list of links
        """
        soup = BeautifulSoup(html_doc, features="html.parser")
        post_list = soup.find('div', attrs={'class': "posts-list"})
        h2_headers = post_list.find_all('h2')
        links = []
        for h2 in h2_headers:
            a_tag = h2.find('a')
            links.append(a_tag.get('href'))
        return links

    def start_crawling_all_pages(self):
        """
        Finds all post links in the website
        """
        # the start page is page 1 and the final page refers to the oldest page in the site
        start, stop = 1, self.find_last_page()
        crawl = True
        # iterate on all list of pages in the site
        while crawl:
            # shows logs and store it in link_crawling_logs.txt
            link_crawler_logger.info(f"start crawling on the page {start}...")
            # sends request
            resp = self.get_page(self.base_url, start)
            page_links = self.find_post_links_for_page(resp.text)
            start += 1
            if start > stop:
                crawl = False
            self.all_post_links.extend(page_links)
        # Creates a directory to save posts link in .json file
        create_directory(STORE_PATH)
        self.store()

    def store(self):
        """
        Store post links in a text file with the name self.path
        """
        link_crawler_logger.error(f"\n{60*'*'}\n storing all links on {STORE_PATH}'post_urls.json' file\n{60*'*'}")
        with open(STORE_PATH + 'post1_urls.json', 'w') as f:
            json.dump(self.all_post_links, f)

    def start(self):
        """
        start crawling all post links
        """
        self.start_crawling_all_pages()


class DataCrawler(CrawlerBase):
    """
    DataCrawler is a class that efficiently crawls a website to extract post data, including content and metadata.

    Attributes:
        content (str): The HTML content of the post.
        url (str): The URL of the post to be scraped.
        category (str): The category of the post.
        index (int): The index of the post in the list of scraped URLs.
        date (str): The release date of the post.
        title (str): The title of the post.
        file_name (str): The name of the file to store the generated PDF.
    """
    def __init__(self):
        self.post_count = None
        self.content, self.url, self.category, self.index = None, None, None, 0
        self.date, self.title, self.file_name, = None, None, None

    def get_page(self):
        """
        Takes an url of a post as input
        :return: the response of the request for the specific url
        """
        try:
            response = requests.get(self.url)
        except:
            return None
        return response.text

    def find_post_metadata(self, soup):
        """
        Extracts post's title, post's release date, post's category
        :param soup:
        :return: None
        """
        # Finds title
        content_div = soup.find('div', attrs={'id': 'content'})
        self.title = content_div.find('h2').text
        # Finds date and category
        post_meta = content_div.find('div', attrs={'class': 'post-meta'})
        self.category = post_meta.find('span', attrs={'class': 'category'}).find('a').text
        self.date = post_meta.find('span', attrs={'class': 'info'}).find('span').text

    def crawl_posts_content(self):
        # TODO : Add multithreading option to this method
        """
        Reads urls from .json file, scrapes each urls data and makes html file based on post's
        data. After that converts it pdf and stores it in a directory.
        :return: None
        """
        # transfers urls from .json file into urls list
        with open(f'./{STORE_PATH}post_urls.json', 'r') as file:
            urls = json.load(file)
        # finds the number of all posts
        self.post_count = len(urls)
        # scrapes each post's data and store it as .html and .pdf files
        for index, url in enumerate(urls):
            self.url = url
            self.index = index
            # Sends request to the site
            html_doc = self.get_page()
            # Finds post's metadata: self.date, self.title, self.category
            html_soup = BeautifulSoup(html_doc, features="html.parser")
            self.find_post_metadata(html_soup)
            # Finds the post's content: self.content
            self.content = str(html_soup.find('div', attrs={'class': 'entry'}))
            self.file_name = f"post_{self.index}"
            self.generate_html()
            self.store()

    def store(self):
        """
        Takes a html code as input
        :return: store the pdf in a directory as final output with pdfkit package
        """
        # converts .html files to .pdf files
        pdf_generator(self.file_name)
        # renames .pdf files with the self.title
        post_number = self.post_count - self.index
        rename_file(f"Output_PDFs/{self.file_name}", self.title.replace(' ', '_'), post_number)

    def generate_html(self):
        """
        Generates html code for each post in the site and stores it in html_codes directory
        :return: None
        """

        # Read the template HTML file for each post
        with open('template_html_code.html', 'r') as file:
            template = file.read()

        # Replace the placeholders with title, date, category and content
        final_html_code = (template.replace('%%{title}%%', self.title).replace('%%{content}%%', self.content)
                           .replace('%%{category}%%', self.category).replace('%%{date}%%', self.date))

        # Write the final HTML code to a new file
        with open(f"Output_PDFs/output.html", 'w') as file:
            file.write(final_html_code)

    def start(self):
        # start crawling all posts content
        self.crawl_posts_content()

    def show(self):
        pass
