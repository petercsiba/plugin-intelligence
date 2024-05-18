import ast
import re
from typing import Optional

import latex2mathml.converter
import markdown


def extract_list_from_str_best_effort(list_str: str) -> list:
    list_str = list_str.replace("'", "").replace('"', "")

    # Split the string by commas and handle special cases
    items = re.split(r",\s*(?![^[]*\])", list_str)  # noqa
    # Further refine each item description
    structured_items = [re.sub(r"[\*]\s*", "", item.strip()) for item in items]  # noqa
    return structured_items


def parse_fuzzy_list(
    list_str: Optional[str], max_elements: int = None
) -> Optional[list]:
    if list_str is None:
        return None

    parsed_list = None
    # Maybe it is just a str(list_object)
    try:
        parsed_list = ast.literal_eval(list_str)
    except (ValueError, SyntaxError) as e:
        pass

    if parsed_list is None:
        parsed_list = extract_list_from_str_best_effort(str(list_str))

    if max_elements:
        parsed_list = parsed_list[:max_elements]

    parsed_list = [item.capitalize() for item in parsed_list if item]

    return parsed_list


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


def rating_in_bounds(rating: Optional[float], debug_str="") -> Optional[float]:
    if rating is None:
        return None
    if rating < 0 or rating > 5:
        print(f"Rating out of bounds {rating}. To debug: {debug_str}")

    return min(5.0, max(0.0, rating))


def get_formatted_sql(peewee_query):
    # Extract the SQL query and parameters from the Peewee query object
    sql, params = peewee_query.sql()

    # Format the SQL query with the parameters
    formatted_query = sql % tuple(params)

    return formatted_query
