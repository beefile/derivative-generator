import unittest

from main import compute_derivative_report


class VerificationTests(unittest.TestCase):
    def test_rule_based_polynomial_verification_passes(self):
        result = compute_derivative_report("2x^2 - 5x - 3", "rule_based")

        self.assertTrue(result.success)
        self.assertTrue(result.verification.symbolic_passed)
        self.assertTrue(result.verification.overall_passed)
        self.assertIn("VERIFICATION:", result.lines)
        self.assertIn("5. Overall verification: PASSED", result.lines)

    def test_rule_based_product_rule_has_numeric_backcheck_samples(self):
        result = compute_derivative_report("x*sin(x)", "rule_based")

        self.assertTrue(result.success)
        self.assertTrue(result.verification.numeric_check_ran)
        self.assertGreaterEqual(len(result.verification.numeric_samples), 1)
        self.assertTrue(result.verification.numeric_passed)

    def test_direct_sympy_log_expression_verification_passes(self):
        result = compute_derivative_report("log(x)", "direct_sympy")

        self.assertTrue(result.success)
        self.assertTrue(result.verification.symbolic_passed)
        self.assertTrue(result.verification.numeric_passed)
        self.assertEqual(result.verification.status_text, "PASSED")

    def test_constant_expression_still_shows_passed_verification(self):
        result = compute_derivative_report("5", "rule_based")

        self.assertTrue(result.success)
        self.assertTrue(result.is_constant)
        self.assertTrue(result.verification.overall_passed)
        self.assertIn("Stopped early: derivative of a constant is 0", result.lines)

    def test_invalid_input_still_includes_verification_section(self):
        result = compute_derivative_report("", "rule_based")

        self.assertFalse(result.success)
        self.assertIn("VERIFICATION:", result.lines)
        self.assertIn("Overall verification: NOT AVAILABLE", result.lines)


if __name__ == "__main__":
    unittest.main()
