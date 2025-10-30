import unittest
from src.generator import MarkdownGenerator

class TestMarkdownGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = MarkdownGenerator()

    def test_generate_markdown_empty(self):
        result = self.generator.generate_markdown([])
        expected = "| Original Prompt | SQL Code | Vulnerability Verdict | Ground Truth |\n|------------------|----------|----------------------|--------------|\n"
        self.assertEqual(result, expected)

    def test_generate_markdown_single_row(self):
        data = [
            {
                "original_prompt": "SELECT * FROM users;",
                "sql_code": "SELECT * FROM users;",
                "verdict": "No Vulnerability",
                "ground_truth": "No Vulnerability"
            }
        ]
        result = self.generator.generate_markdown(data)
        expected = "| Original Prompt          | SQL Code                | Vulnerability Verdict | Ground Truth      |\n|--------------------------|-------------------------|----------------------|--------------------|\n| SELECT * FROM users;     | SELECT * FROM users;    | No Vulnerability      | No Vulnerability    |\n"
        self.assertEqual(result, expected)

    def test_add_row(self):
        row_data = {
            "original_prompt": "SELECT * FROM users;",
            "sql_code": "SELECT * FROM users;",
            "verdict": "No Vulnerability",
            "ground_truth": "No Vulnerability"
        }
        self.generator.add_row(row_data)
        self.assertEqual(len(self.generator.rows), 1)

if __name__ == '__main__':
    unittest.main()