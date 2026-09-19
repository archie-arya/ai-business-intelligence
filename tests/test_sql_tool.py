import unittest

from bi_agent.sql_tool import UnsafeQueryError, validate_read_only_query


class ReadOnlyQueryTests(unittest.TestCase):
    def test_allows_select_and_trailing_semicolon(self):
        self.assertEqual(validate_read_only_query("SELECT 1;"), "SELECT 1")

    def test_allows_read_only_cte(self):
        self.assertEqual(validate_read_only_query("WITH x AS (SELECT 1) SELECT * FROM x"), "WITH x AS (SELECT 1) SELECT * FROM x")

    def test_rejects_multiple_statements(self):
        with self.assertRaises(UnsafeQueryError):
            validate_read_only_query("SELECT 1; DROP TABLE retail.fact_sales_line")

    def test_rejects_writing_cte(self):
        with self.assertRaises(UnsafeQueryError):
            validate_read_only_query("WITH x AS (DELETE FROM retail.fact_sales_line RETURNING *) SELECT * FROM x")

    def test_rejects_non_select(self):
        with self.assertRaises(UnsafeQueryError):
            validate_read_only_query("DELETE FROM retail.fact_sales_line")
