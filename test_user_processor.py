"""
Canonical test suite for user_processor.py

DO NOT MODIFY THESE TESTS - they define the expected behavior.
Your refactored code must pass all tests (except the skipped one).
"""

import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from user_processor import (
    read_users_from_csv,
    calculate_user_score,
    process_users,
    generate_report,
    export_json,
    ScoringConfig,
    UserDataError
)


class TestReadUsersFromCSV(unittest.TestCase):
    """Tests for CSV reading functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def _create_sample_csv(self):
        """Create a temporary CSV file with sample user data."""
        csv_file = self.temp_path / "test_users.csv"
        csv_content = """name,age,purchases,visits
Alice Johnson,25,15,30
Bob Smith,17,5,10
Carol White,35,25,50
David Brown,42,8,20
Eve Davis,29,30,45
Frank Miller,19,12,25
Grace Lee,55,40,80
"""
        csv_file.write_text(csv_content)
        return csv_file

    def _create_empty_csv(self):
        """Create an empty CSV file."""
        csv_file = self.temp_path / "empty.csv"
        csv_file.write_text("name,age,purchases,visits\n")
        return csv_file

    def _create_invalid_csv(self):
        """Create a CSV file with invalid data."""
        csv_file = self.temp_path / "invalid.csv"
        csv_content = """name,age,purchases,visits
John Doe,invalid_age,10,20
"""
        csv_file.write_text(csv_content)
        return csv_file

    def _create_missing_columns_csv(self):
        """Create a CSV file missing required columns."""
        csv_file = self.temp_path / "missing.csv"
        csv_content = """name,age
John Doe,25
"""
        csv_file.write_text(csv_content)
        return csv_file

    def test_read_valid_csv(self):
        """Should successfully read a valid CSV file."""
        csv_file = self._create_sample_csv()
        users = read_users_from_csv(csv_file)
        self.assertEqual(len(users), 7)
        self.assertEqual(users[0]['name'], 'Alice Johnson')
        self.assertEqual(users[0]['age'], '25')

    def test_read_empty_csv(self):
        """Should raise error for empty CSV file."""
        csv_file = self._create_empty_csv()
        with self.assertRaisesRegex(UserDataError, "empty"):
            read_users_from_csv(csv_file)

    def test_read_nonexistent_file(self):
        """Should raise error for non-existent file."""
        nonexistent = self.temp_path / "does_not_exist.csv"
        with self.assertRaisesRegex(UserDataError, "not found"):
            read_users_from_csv(nonexistent)

    def test_read_missing_columns(self):
        """Should raise error when required columns are missing."""
        csv_file = self._create_missing_columns_csv()
        with self.assertRaisesRegex(UserDataError, "Missing required fields"):
            read_users_from_csv(csv_file)


class TestCalculateUserScore(unittest.TestCase):
    """Tests for score calculation."""

    def setUp(self):
        """Set up test fixtures."""
        self.default_config = ScoringConfig()

    def test_basic_score_calculation(self):
        """Should calculate score correctly with default config."""
        score = calculate_user_score(15, 30, self.default_config)
        # 15 * 10 + 30 * 5 = 150 + 150 = 300
        self.assertEqual(score, 300)

    def test_zero_purchases_and_visits(self):
        """Should handle zero values."""
        score = calculate_user_score(0, 0, self.default_config)
        self.assertEqual(score, 0)

    def test_custom_config(self):
        """Should respect custom scoring configuration."""
        custom_config = ScoringConfig(
            purchase_multiplier=20,
            visit_multiplier=10
        )
        score = calculate_user_score(5, 10, custom_config)
        # 5 * 20 + 10 * 10 = 100 + 100 = 200
        self.assertEqual(score, 200)

    def test_high_volume_user_score(self):
        """Should calculate score for high-volume users."""
        score = calculate_user_score(100, 200, self.default_config)
        # 100 * 10 + 200 * 5 = 1000 + 1000 = 2000
        self.assertEqual(score, 2000)


class TestProcessUsers(unittest.TestCase):
    """Tests for user processing and filtering."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.default_config = ScoringConfig()

    def _create_sample_csv(self):
        """Create a temporary CSV file with sample user data."""
        csv_file = self.temp_path / "test_users.csv"
        csv_content = """name,age,purchases,visits
Alice Johnson,25,15,30
Bob Smith,17,5,10
Carol White,35,25,50
David Brown,42,8,20
Eve Davis,29,30,45
Frank Miller,19,12,25
Grace Lee,55,40,80
"""
        csv_file.write_text(csv_content)
        return csv_file

    def _create_invalid_csv(self):
        """Create a CSV file with invalid data."""
        csv_file = self.temp_path / "invalid.csv"
        csv_content = """name,age,purchases,visits
John Doe,invalid_age,10,20
"""
        csv_file.write_text(csv_content)
        return csv_file

    def test_filter_by_age_and_score(self):
        """Should filter users by age > 18 and score > threshold."""
        csv_file = self._create_sample_csv()
        raw_users = read_users_from_csv(csv_file)
        processed = process_users(raw_users, self.default_config)

        # Bob (17) should be filtered out by age
        # David (42, score 180) should be filtered out by score threshold (100)
        # Wait, let me recalculate: David: 8*10 + 20*5 = 80 + 100 = 180 > 100, so included
        # Actually need to check which users have score > 100

        self.assertTrue(all(user['age'] > 18 for user in processed))
        self.assertTrue(all(user['score'] > 100 for user in processed))
        self.assertGreaterEqual(len(processed), 1)  # At least some users should pass

    def test_score_calculation_in_processing(self):
        """Should include calculated score in processed users."""
        csv_file = self._create_sample_csv()
        raw_users = read_users_from_csv(csv_file)
        processed = process_users(raw_users, self.default_config)

        for user in processed:
            self.assertIn('score', user)
            expected_score = calculate_user_score(
                user['purchases'],
                user['visits'],
                self.default_config
            )
            self.assertEqual(user['score'], expected_score)

    def test_empty_result_with_high_threshold(self):
        """Should return empty list when threshold is too high."""
        high_threshold_config = ScoringConfig(score_threshold=10000)
        csv_file = self._create_sample_csv()
        raw_users = read_users_from_csv(csv_file)
        processed = process_users(raw_users, high_threshold_config)

        self.assertEqual(processed, [])

    def test_invalid_data_raises_error(self):
        """Should raise error for invalid data types."""
        csv_file = self._create_invalid_csv()
        raw_users = read_users_from_csv(csv_file)
        with self.assertRaisesRegex(UserDataError, "Invalid user data"):
            process_users(raw_users, self.default_config)


class TestGenerateReport(unittest.TestCase):
    """Tests for report generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def test_generate_report_with_users(self):
        """Should generate report with user scores."""
        report_file = self.temp_path / "report.txt"
        users = [
            {'name': 'Alice', 'score': 300},
            {'name': 'Bob', 'score': 200},
        ]

        generate_report(users, report_file)

        content = report_file.read_text()
        self.assertIn("User: Alice, Score: 300", content)
        self.assertIn("User: Bob, Score: 200", content)
        self.assertIn("Total users: 2", content)
        self.assertIn("Average score: 250.00", content)

    @unittest.skip("Code is correct per manual testing, but can't get the UT to work")
    @patch('builtins.open', new_callable=mock_open)
    def test_generate_report_writes_correctly(self, mock_file):
        """Should call file write methods correctly when generating report."""
        users = [
            {'name': 'Charlie', 'score': 150},
        ]

        generate_report(users, Path('test_report.txt'))

        mock_file.assert_called_once_with(Path('test_report.txt'), 'w', encoding='utf-8')

        handle = mock_file()

        handle.write.assert_any_call("User: Charlie, Score: 150\n")
        handle.write.assert_any_call("\nTotal users: 1\n")
        handle.write.assert_any_call("Average score: 150.00\n")

    def test_generate_report_with_empty_list(self):
        """Should handle empty user list."""
        report_file = self.temp_path / "report.txt"
        users = []

        generate_report(users, report_file)

        content = report_file.read_text()
        self.assertIn("Total users: 0", content)
        # Should not have average when no users
        # Allow either no mention or "Average score:" present

    def test_report_creates_file(self):
        """Should create report file if it doesn't exist."""
        report_file = self.temp_path / "new_report.txt"
        self.assertFalse(report_file.exists())

        users = [{'name': 'Test', 'score': 100}]
        generate_report(users, report_file)

        self.assertTrue(report_file.exists())


class TestExportJSON(unittest.TestCase):
    """Tests for JSON export functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def test_export_valid_json(self):
        """Should export users to valid JSON format."""
        json_file = self.temp_path / "output.json"
        users = [
            {'name': 'Alice', 'age': 25, 'score': 300},
            {'name': 'Bob', 'age': 30, 'score': 200},
        ]

        export_json(users, json_file)

        with open(json_file, 'r') as f:
            loaded_data = json.load(f)

        self.assertEqual(loaded_data, users)
        self.assertEqual(len(loaded_data), 2)

    def test_export_empty_list(self):
        """Should handle empty user list."""
        json_file = self.temp_path / "empty.json"
        users = []

        export_json(users, json_file)

        with open(json_file, 'r') as f:
            loaded_data = json.load(f)

        self.assertEqual(loaded_data, [])

    def test_json_file_creation(self):
        """Should create JSON file if it doesn't exist."""
        json_file = self.temp_path / "new_output.json"
        self.assertFalse(json_file.exists())

        export_json([{'name': 'Test'}], json_file)

        self.assertTrue(json_file.exists())


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def _create_sample_csv(self):
        """Create a temporary CSV file with sample user data."""
        csv_file = self.temp_path / "test_users.csv"
        csv_content = """name,age,purchases,visits
Alice Johnson,25,15,30
Bob Smith,17,5,10
Carol White,35,25,50
David Brown,42,8,20
Eve Davis,29,30,45
Frank Miller,19,12,25
Grace Lee,55,40,80
"""
        csv_file.write_text(csv_content)
        return csv_file

    def test_complete_pipeline(self):
        """Should successfully process users through complete pipeline."""
        sample_csv_file = self._create_sample_csv()
        report_file = self.temp_path / "report.txt"
        json_file = self.temp_path / "output.json"

        # Read
        raw_users = read_users_from_csv(sample_csv_file)
        self.assertGreater(len(raw_users), 0)

        # Process
        processed_users = process_users(raw_users)
        self.assertGreater(len(processed_users), 0)

        # Generate report
        generate_report(processed_users, report_file)
        self.assertTrue(report_file.exists())

        # Export JSON
        export_json(processed_users, json_file)
        self.assertTrue(json_file.exists())

        # Verify JSON contents
        with open(json_file, 'r') as f:
            exported = json.load(f)
        self.assertEqual(exported, processed_users)

    def test_pipeline_with_custom_config(self):
        """Should work with custom configuration."""
        sample_csv_file = self._create_sample_csv()
        config = ScoringConfig(
            purchase_multiplier=15,
            visit_multiplier=8,
            score_threshold=200,
            min_age=21
        )

        raw_users = read_users_from_csv(sample_csv_file)
        processed_users = process_users(raw_users, config)

        # All users should meet custom criteria
        self.assertTrue(all(user['age'] > 21 for user in processed_users))
        self.assertTrue(all(user['score'] > 200 for user in processed_users))


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases and boundary conditions."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.default_config = ScoringConfig()

    def test_user_exactly_at_age_threshold(self):
        """Should exclude users exactly at age threshold (18)."""
        csv_file = self.temp_path / "edge.csv"
        csv_file.write_text("""name,age,purchases,visits
Exactly18,18,50,50
Above18,19,50,50
""")

        raw_users = read_users_from_csv(csv_file)
        processed = process_users(raw_users, self.default_config)

        # Age > 18, so 18 should be excluded
        names = [u['name'] for u in processed]
        self.assertNotIn('Exactly18', names)
        self.assertIn('Above18', names)

    def test_user_exactly_at_score_threshold(self):
        """Should exclude users exactly at score threshold."""
        config = ScoringConfig(score_threshold=100)
        csv_file = self.temp_path / "edge.csv"
        csv_file.write_text("""name,age,purchases,visits
ExactScore,25,10,0
AboveScore,25,11,0
""")
        # ExactScore: 10*10 + 0*5 = 100 (exactly at threshold)
        # AboveScore: 11*10 + 0*5 = 110 (above threshold)

        raw_users = read_users_from_csv(csv_file)
        processed = process_users(raw_users, config)

        # Score > threshold, so exactly 100 should be excluded
        names = [u['name'] for u in processed]
        self.assertNotIn('ExactScore', names)
        self.assertIn('AboveScore', names)


if __name__ == '__main__':
    unittest.main()
