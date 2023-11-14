import os
import scrapy
from readability import Document
import html2text

class VbtProSpider(scrapy.Spider):
    name = "vbt_pro"
    allowed_domains = ['vectorbt.pro']

    # Initialize the spider with the secret_url parameter
    def __init__(self, secret_url=None, *args, **kwargs):
        super(VbtProSpider, self).__init__(*args, **kwargs)
        self.secret_url = secret_url
        self.start_urls = [
            f'https://vectorbt.pro/{self.secret_url}/features/',
            f'https://vectorbt.pro/{self.secret_url}/tutorials/',
            f'https://vectorbt.pro/{self.secret_url}/documentation/',
            f'https://vectorbt.pro/{self.secret_url}/api/',
            f'https://vectorbt.pro/{self.secret_url}/cookbook/'
        ]

        # Combine and centralize data directories from both spiders
        self.base_dir = 'docs/vbt_pro'
        self.api_dir = os.path.join(self.base_dir, 'api')
        self.file_map = {
            'features': 'features.md',
            'tutorials': 'tutorials.md',
            'documentation': 'documentation.md',
            'api': 'api.md',
            'cookbook': 'cookbook.md'
        }

    def start_requests(self):
        # Ensure base directories exist
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(self.api_dir, exist_ok=True)

        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Identify the section of the URL to determine the output directory and file naming
        section = response.url.split('/')[4]

        # Using readability to extract the main content
        document = Document(response.text)
        summary = document.summary()

        # Converting HTML summary to Markdown using html2text
        converter = html2text.HTML2Text()
        markdown_content = converter.handle(summary)

        # Write content to appropriate files depending on the URL section
        if section == 'api':
            # The filename is set using the last part of the URL path for the API section
            filename = os.path.join(self.api_dir, f'{response.url.split("/")[-2]}.md')
        else:
            # Use predefined filenames for other sections
            filename = os.path.join(self.base_dir, self.file_map.get(section, 'unknown.md'))

        # Write main content as Markdown
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        # Follow links according to the logic of both spiders
        for href in response.css('a::attr(href)').getall():
            # The spider should follow links found in the API pages, as well as those containing the secret URL
            if href.startswith(f'/{self.secret_url}/api/') or self.secret_url in href:
                yield response.follow(href, self.parse)
