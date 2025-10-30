import argparse
from generator import MarkdownGenerator

def main():
    parser = argparse.ArgumentParser(description="Generate a Markdown file with SQL vulnerability data.")
    parser.add_argument('--output', type=str, required=True, help='Output Markdown file path')
    args = parser.parse_args()

    generator = MarkdownGenerator()
    # Here you would typically gather data to populate the Markdown table
    # For simplicity, let's assume we have a list of prompts and their results
    data = [
        {
            "prompt": "SELECT * FROM users WHERE id = 1;",
            "sql_code": "SELECT * FROM users WHERE id = 1;",
            "verdict": "Safe",
            "ground_truth": "No vulnerabilities detected."
        },
        # Add more data as needed
    ]

    for entry in data:
        generator.add_row(entry["prompt"], entry["sql_code"], entry["verdict"], entry["ground_truth"])

    markdown_content = generator.generate_markdown()
    
    with open(args.output, 'w') as f:
        f.write(markdown_content)

if __name__ == "__main__":
    main()