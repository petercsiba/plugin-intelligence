import re
from typing import Optional

import latex2mathml.converter
import markdown


def parse_fuzzy_list(
    list_str: Optional[str], max_elements: int = None
) -> Optional[list]:
    if list_str is None:
        return None

    list_str = list_str.replace("'", "").replace('"', "")

    # Split the string by commas and handle special cases
    items = re.split(r",\s*(?![^[]*\])", list_str)  # noqa
    # Further refine each item description
    structured_items = [re.sub(r"[\*]\s*", "", item.strip()) for item in items]  # noqa

    if max_elements:
        structured_items = structured_items[:max_elements]

    structured_items = [item.capitalize() for item in structured_items if item]

    return structured_items


def convert_latex_to_mathml(latex_str: str) -> str:
    return latex2mathml.converter.convert(latex_str)


def prompt_output_to_html(prompt_output: Optional[str]) -> Optional[str]:
    if prompt_output is None:
        return None

    # Pattern to detect LaTeX within \( ... \) or \[ ... \] delimiters
    patterns = [r"\\\((.*?)\\\)", r"\\\[(.*?)\\\]"]

    def replace_latex(match):
        latex_content = match.group(1).strip()
        return convert_latex_to_mathml(latex_content)

    # Replace all LaTeX formulas with HTML
    for pattern in patterns:
        prompt_output = re.sub(pattern, replace_latex, prompt_output)

    # Convert the rest of the Markdown to HTML
    extensions = [
        "fenced_code",  # Allows using fenced code blocks (```code```)
        "codehilite",  # Syntax highlighting for code blocks
    ]
    extension_configs = {"codehilite": {"use_pygments": True, "css_class": "highlight"}}
    html = markdown.markdown(
        prompt_output, extensions=extensions, extension_configs=extension_configs
    )

    return html.replace("\\$", "$")


def get_formatted_sql(peewee_query):
    # Extract the SQL query and parameters from the Peewee query object
    sql, params = peewee_query.sql()

    # Format the SQL query with the parameters
    formatted_query = sql % tuple(params)

    return formatted_query
