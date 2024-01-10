# Welcome to QuantGPT 🚀 🌒
Interface AI with Quantitative Analysis for Enhanced Strategy Building

`QuantGPT` is an open-source tool designed for quants who seek to harness the power of vectorbt PRO's extensive documentation through an intuitive UI. Our aim is to provide a seamless bridge between complex documentation and the end-user, utilizing the capabilities of advanced natural language processing.

![screenshot of complex question](/public/screenshot.png "How would you implement breakeven after first take profit?")

## Features
AI-Powered Documentation Search: Query the full breadth of vectorbt PRO documentation using natural language, making the search for information as simple as typing out a question.
Contextual Understanding: Gain insights and contextual information directly related to your search queries, ensuring that you grasp not just the "how," but the "why" behind various analytical strategies.
Efficient Strategy Development: Quickly find the functions, parameters, and modules you need, saving you time and streamlining the process from conception to execution.
Core Philosophy
`QuantGPT` is built with the belief that the right tools can significantly enhance the capability and efficiency of quantitative strategy development. By fusing AI with strategy creation, we're not just simplifying the search process; we're redefining how quants interact with information.

## Community and Collaboration
As a community-driven project, `QuantGPT` thrives on collaborative efforts and contributions. Whether it's through code, ideas, or feedback, your input helps shape the future of quantitative strategy development tools.

## Get Started
Dive into the `QuantGPT` experience to elevate your trading strategies and contribute to the evolving landscape of quantitative analysis.

Star or fork the repo to show your support and stay updated.
Check out the contribution guidelines to see how you can be a part of the journey.
Note: `QuantGPT` is an ever-evolving project. We start with vectorbt PRO, but the horizon is expansive. The goal is to eventually integrate a multitude of analytical tools and libraries, crafting a versatile ecosystem for quantitative analysis.

Explore `QuantGPT` — where algorithms meet strategies at the speed of thought.

## Installation

Ensure Conda is installed on your system. If not, download it from the [official Conda website](https://www.anaconda.com/products/distribution). Follow these steps to set up `QuantGPT`:

### Step 1: Clone the Repository

Begin by cloning the `QuantGPT` repository to your local machine:

```bash
git clone https://github.com/rnikitin/quantgpt.git
cd quantgpt
```

### Step 2: Create and Activate Conda Environment

Create a Conda environment with Python 3.10 and activate it:

```bash
conda create --name quantgpt python=3.10
conda activate quantgpt
```

### Step 3: Install Scrapy

Within the Conda environment, install Scrapy using either Conda or pip:

```bash
conda install -c conda-forge scrapy
```

or

```bash
pip install Scrapy
```

Refer to the [official Scrapy documentation](https://docs.scrapy.org/en/latest/intro/install.html) for more details.

### Step 4: Install Remaining Dependencies

With Scrapy installed, use `pip` to install the other necessary dependencies:

```bash
pip install -r requirements.txt
```

### Step 5: Set Up Environment Variables

Rename `env.example` to `.env` and fill in the necessary variables:

**Mandatory Variables:**
```plaintext
OPENAI_API_KEY="sk-XXXX"
GPT_MODEL="gpt-4"
```

**Optional Variables:**
(Acquire these from Chainlit Cloud if needed [here](https://cloud.chainlit.io/))
How to generate `CHAINLIT_AUTH_SECRET` you can read [here](https://docs.chainlit.io/authentication/overview)
```plaintext
CHAINLIT_API_KEY="cl_XXX"
CHAINLIT_AUTH_SECRET="XXX"
```

### Step 6: Run the Scraper

Navigate to the `quant_scraper` directory to prepare for running the scraper:

```bash
cd quant_scraper
```

Execute the scraper, passing in the `secret_url` directly into the command:

```bash
scrapy crawl vbt_pro -a secret_url="pvt_XXXX"
```

`pvt_XXXX` should be obtained from [VectorBT Pro Membership](https://vectorbt.pro/become-a-member/).

After completion, navigate back to the project's root directory:

```bash
cd ..
```

### Step 7: Launch the UI

With everything set up, initiate the user interface:

```bash
chainlit run quantgpt.py
```

Allow 3-5 minutes on the first run to build the Vector Store index, depending on your internet connection speed.

### Start Using QuantGPT

Your setup of `QuantGPT` is complete. The default AI model is GPT-4, but you can adjust this in the `.env` file. Be aware of the costs for indexing and requests, which may be around $1 for indexing and $0.2 per request.

## How It Works

`QuantGPT` operates on a sequence of steps involving data extraction, transformation, and response generation:

1. **Data Extraction:**
   - **Web Crawling:** Utilizing `Scrapy`, the system programmatically navigates the vectorbt pro documentation website to retrieve content.

2. **Transformation:**
   - **Indexing:** The `llama_index` module processes the collected data, segmenting documents based on markdown headers ("## ") into indexed sections.
   - **Question Generation:** To augment the indexed content, `gpt-3.5-turbo` generates related questions for each section, expanding the metadata for the documents.
   - **VectorIndex Integration:** The resulting document sections, along with their metadata, are stored in the `VectorIndex`.

3. **Response Generation:**
   - **Document Retrieval:** In response to user queries, the system extracts relevant sections from the `VectorIndex`.
   - **Summary Composition:** It employs the tree_summary method to synthesize the information into a coherent and contextually relevant answer.

The approach aims to deliver SOTA quality answers from extensive documentation, with the trade-off being higher payment costs per query.

## Usage

`QuantGPT` is designed to interface with Chainlit, leveraging its robust chatbot UI capabilities, ideal for interacting with and evaluating large language models (LLMs) for quantitative trading applications.

### Initial Access

Upon launching the app, you may be prompted for login credentials. Use the following default combination:

**Username:** admin
**Password:** admin

This authentication step is required by Chainlit for those who require persistence within their instance. It is a placeholder and should be replaced with proper authentication measures in production or if sensitive data is being handled.

### Conversational Interface

The application presents itself as a chat interface, providing an intuitive way to interact with the underlying AI. However, it's important to note some current limitations:

#### Contextual Awareness

- Each interaction is treated independently. The AI does not retain the context from previous questions. To compensate for this, provide comprehensive information within each query to facilitate a more accurate response.

#### Indexing

- The indexing feature is in the early stages of development. It is anticipated that incorporating metadata extraction, as demonstrated in [LlamaIndex's Metadata Extraction Guide](https://docs.llamaindex.ai/en/stable/examples/metadata_extraction/MetadataExtraction_LLMSurvey.html), will significantly enhance the AI's ability to retrieve and utilize relevant information from the indexed documentation.

### Limitations and Development Opportunities

As `QuantGPT` evolves, so will its capabilities. Current limitations are opportunities for growth and development:

- **Context Memory:** Future iterations could include context memory for seamless conversations.
- **Metadata Indexing:** Improvements in metadata indexing are expected to refine the AI's understanding and response accuracy.

### Calling All LLM Developers!

If you are an LLM developer or enthusiast, your expertise can help `QuantGPT` reach its full potential. Experimentation, trial, and contributions are highly encouraged. If you have ideas or improvements, please fork the repository, make your changes, and submit a pull request. Your contributions are valuable and always welcome!

## Roadmap

Here's what's on the horizon for `QuantGPT`:

**Near Future:**
- **Context-Aware Conversations:** Implement a full chat mode with memory for richer context.
- **Decoupled Architecture:** Move indexing/querying out of `quantgpt.py` to enable flexible experimentation via a Python notebook.
- **Metadata Enhancements:** Introduce metadata extractions for better search precision.

**Looking Ahead:**
- **Direct Link Indexing:** Add chat capabilities to parse and index content from links in real-time.
- **File Parsing:** Expand the indexing to include file parsing for diverse data formats.

**Long-Term Vision:**
- **LLM Agent Teamwork:** Assemble a team of LLM agents to support advanced research and potentially automate trading analysis.

Each step is aimed at making `QuantGPT` a smarter, more intuitive assistant for the quantitative trading community.

## Vision for QuantGPT

QuantGPT began as a personal project out of the need to navigate and leverage the capabilities of the powerful but intricate vectorbt.pro library. However, the vision for quantgpt extends far beyond a single tool or library. It's about building a comprehensive ecosystem that empowers quantitative traders and developers to turn complex data and sophisticated strategies into actionable insights and operational trading systems.

### Expanding the Ecosystem

Here are some ideas on how `QuantGPT` could evolve:

- **Strategy Translation:** Automate the translation of backtested strategies from vectorbt into other trading platforms like freqtrade, enabling users to easily shift from research to live trading environments.

- **Knowledge Integration:** Incorporate a broad range of quantitative finance resources, such as academic papers, tutorials, and books, into the `QuantGPT` index. This would allow users to query and apply complex theories and models directly to their trading strategies.

- **Interactive Learning:** Use the conversational UI to create an interactive learning environment where less experienced traders can ask questions and receive explanations, code snippets, or references to relevant materials, thus flattening the learning curve for complex quantitative concepts.

- **Real-Time Data Analysis:** Connect `QuantGPT` with real-time market data feeds, enabling it to provide on-the-fly analysis and insights based on current market conditions.

- **Custom Indexing:** Allow users to create custom indexes from their own datasets, enabling personalized insights and strategy development based on proprietary information.

### A Call for Collective Innovation

`QuantGPT` is not just a tool; it's a platform for innovation. Here's how it could serve the community:

- **Collaborative Development:** Encourage developers and quants to contribute to the growth of `QuantGPT`, whether through code contributions, sharing datasets, or developing plugins for additional functionalities.

- **Bridging Gaps:** By acting as a liaison between various quantitative tools and platforms, `QuantGPT` could streamline the workflow for strategy development and backtesting, making it more efficient and accessible.

- **Democratizing Quantitative Trading:** Help to break down the barriers to entry in the quantitative trading space, making advanced trading tools and analytics accessible to a broader audience.

The future of `QuantGPT` is only as limited as our collective creativity. As it grows and adapts, `QuantGPT` aims to become a cornerstone in the toolkit of every quantitative trader, from the curious beginner to the seasoned professional. Join us in shaping the future of quantitative trading.

## Special Thanks

A heartfelt thank you goes out to the individuals and teams whose work has been fundamental to the development of `QuantGPT`:

- **[@polakowo](https://github.com/polakowo)**, for creating vectorbt.pro, a library that has significantly democratized quantitative trading.
- **OpenAI**, for the GPT models that have redefined our interaction with machine learning and data analysis.
- **LlamaIndex**, for the powerful indexing tool that makes vast amounts of data accessible and actionable.
- **Chainlit**, for providing a user-friendly UI, enabling a seamless and intuitive way to interact with `QuantGPT`.

Your collective contributions have not only inspired but also enabled this project to come to fruition.

## License

`QuantGPT` is made available under the MIT License. This permissive license allows for reuse within proprietary software provided that all copies of the licensed software include a copy of the MIT License terms and the copyright notice.

To view the full license, see the [LICENSE](https://github.com/rnikitin/quantgpt/blob/main/LICENSE) file in the GitHub repository.