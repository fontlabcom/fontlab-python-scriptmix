# this_file: tests_docs/test_pipeline_batch_recipes.py
"""Preserve the output filename template in actual generated documentation."""
import unittest

from test_pipeline_site import Page, SITE


class BatchRecipeDocumentationTests(unittest.TestCase):
    def test_batch_recipe_when_rendered_then_output_filename_template_is_visible(self):
        page = Page((SITE / "scripts/font-ui-lab/batch-ufo-recipe-workbench.html").read_text())
        self.assertIn("<source-name>-transformed.ufo", "".join(page.text))
        self.assertNotIn("source-name", [tag for tag, _ in page.tags])
