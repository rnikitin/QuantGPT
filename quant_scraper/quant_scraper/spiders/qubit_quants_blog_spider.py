import os
import scrapy
from readability.readability import Document
import html2text

class VbtProSpider(scrapy.Spider):
    name = "qubit_quants_blog"
    allowed_domains = ['qubitquants.github.io']

    # Initialize the spider for the blog
    def __init__(self, *args, **kwargs):
        super(VbtProSpider, self).__init__(*args, **kwargs)
        self.start_urls = [
                "https://qubitquants.github.io/aligning-mtf-data/index.html",
                "https://qubitquants.github.io/strategydev/index.html",
                "https://qubitquants.github.io/vbt_plot_strategy/index.html",
                "https://qubitquants.github.io/multi_asset_portfolio_simulation/index.html",
                "https://qubitquants.github.io/parameter-optimization/index.html",
                "https://qubitquants.github.io/customsim_0/index.html",
                "https://qubitquants.github.io/customsim_1/index.html",
                "https://qubitquants.github.io/customsim_2/index.html",
                "https://qubitquants.github.io/customsim_3/index.html"
        ]

        # Combine and centralize data directories from both spiders
        self.base_dir = 'docs/qubit_quants_blog'


    def start_requests(self):
        # Ensure base directories exist
        os.makedirs(self.base_dir, exist_ok=True)

        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Decode the response body explicitly with UTF-8 if necessary
        response_body = response.body.decode('utf-8', errors='replace')

        # Identify the section of the URL to determine the output directory and file naming
        blog_title = response.url.split('/')[-2]

        # Using readability to extract the main content
        document = Document(response_body)
        summary = document.summary()

        # Converting HTML summary to Markdown using html2text
        html_converter = html2text.HTML2Text()
        markdown_content = html_converter.handle(summary)

        # Write content to appropriate files depending on the URL section
        filename = os.path.join(self.base_dir, f'{blog_title}.md')

        # Write main content as Markdown with UTF-8 encoding
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        # Follow links according to the logic of both spiders
        for href in response.css('a::attr(href)').getall():
            yield response.follow(href, self.parse)
