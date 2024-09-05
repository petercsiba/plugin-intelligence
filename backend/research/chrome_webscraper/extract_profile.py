from typing import Dict

from bs4 import BeautifulSoup, Comment

from gpt_form_filler.openai_client import OpenAiClient, gpt_response_to_json


def tag_visible(element):
    if element.parent.name in [
        "style",
        "script",
        "head",
        "title",
        "meta",
        "[document]",
    ]:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(soup: BeautifulSoup):
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return "\n".join(t.strip() for t in visible_texts if len(t.strip()) > 1)


def split_text(text, chunk_size=2500, overlap=400):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = words[i : i + chunk_size]
        chunks.append(" ".join(chunk))
    return chunks


def extract_profile_data(gpt_client: OpenAiClient, text_only_data: str) -> Dict:
    print(f"extract_profile_data from {len(text_only_data)} bytes of data")
    chunks = split_text(text_only_data)
    first_result = None
    results = {}
    query_template = """
this web page in visible text only format talks about {} profile
extract all relevant information for this person,
omit general sounding information
also omit other peoples bio
be sure to describe all relevant experiences for this person
only output a json for all the found structured data
text: {}"""

    for i, chunk in enumerate(chunks):
        if i == 0:
            name = "a person"
        else:
            name = first_result.get("name", "a person")

        query = query_template.format(name, chunk)
        result = gpt_client.run_prompt(query, print_prompt=True)
        result_dict = gpt_response_to_json(result)
        if result_dict is None:
            result_dict = {}
        if first_result is None:
            first_result = result_dict

        # "Safe" merge new results with the old ones.
        for key, value in result_dict.items():
            if key in results:
                if isinstance(results[key], list):
                    results[key].extend(value)
                elif isinstance(results[key], dict):
                    results[key].update(value)
                else:
                    results[key] = [results[key], value]
            else:
                results[key] = value

    return results
