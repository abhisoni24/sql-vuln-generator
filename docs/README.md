# Markdown Vulnerability Markdown Generator

This project generates a Markdown file containing a table that summarizes SQL code prompts, their corresponding SQL code, vulnerability verdicts, and ground truth.

## Project Structure

```
md-vuln-markdown-generator
├── src
│   ├── main.py          # Entry point of the application
│   ├── generator.py     # Contains MarkdownGenerator class for Markdown creation
│   ├── cli.py           # Command-line interface for the application
│   ├── api              # Directory for API clients
│   │   ├── __init__.py  # Marks the api directory as a package
│   │   ├── claude_client.py  # Interacts with the Claude API
│   │   └── openai_client.py   # Interacts with the OpenAI API
│   ├── models           # Directory for data models
│   │   └── types.py     # Defines data models used in the application
│   └── utils            # Directory for utility functions
│       └── io.py        # File input/output operations
├── tests                # Directory for tests
│   ├── test_generator.py # Unit tests for MarkdownGenerator
│   └── fixtures
│       └── sample_prompts.json # Sample prompts for testing
├── .env.example         # Template for environment variables
├── .gitignore           # Files and directories to ignore in version control
├── pyproject.toml       # Project configuration file
├── requirements.txt     # Required Python packages
└── README.md            # Documentation for the project
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd md-vuln-markdown-generator
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up your environment variables by copying `.env.example` to `.env` and filling in your API keys:
   ```
   cp .env.example .env
   ```

## Usage

To generate the Markdown file, run the following command:
```
python src/cli.py
```

This will create a Markdown file with a table containing the original prompt, returned SQL code, verdict of vulnerability, and ground truth.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.