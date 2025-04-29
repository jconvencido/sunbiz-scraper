import requests
from bs4 import BeautifulSoup
import urllib.parse 

def scrape_business_info(doc_id):
    url = f"https://irs4gov.orapiz.net/dm/fl/{doc_id}"

    headers = { "User-Agent": "Mozilla/5.0" }
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    def get_text(selector, remove_label=None, parent=None):
        el = (parent or soup).select_one(selector)
        if not el:
            print(f"Warning: Selector '{selector}' not found.")
            return "N/A"
        text = el.get_text(strip=True)
        if remove_label:
            text = text.replace(remove_label, "").strip()
        return text

    corporation_name = get_text(".corpInfo div:nth-of-type(1)", remove_label="Corporation Name:")
    corporation_name_encoded = corporation_name.replace(" ", "%20")
    search_name_order = ''.join(c for c in corporation_name if c.isalnum()).upper()

    corporation_search_url = f"https://search.sunbiz.org/Inquiry/CorporationSearch/SearchResults/EntityName/{corporation_name_encoded}/Page1?searchNameOrder={search_name_order}"

    # Visit the corporation_search_url and scrape additional data
    search_res = requests.get(corporation_search_url, headers=headers)
    search_soup = BeautifulSoup(search_res.text, 'html.parser')

    def get_matching_link(corporation_id):
        td_with_id = search_soup.find("td", string=corporation_id)
        if td_with_id:
            parent_tr = td_with_id.find_parent("tr")
            if parent_tr:
                link_tag = parent_tr.select_one("td.large-width a")
                if link_tag and link_tag.get("href"):
                    return f"https://search.sunbiz.org{link_tag['href']}"
        return "N/A"

    corporation_id = get_text(".corpInfo div:nth-of-type(2)", remove_label="Corporation Id:")
    matching_link = get_matching_link(corporation_id)

    if matching_link != "N/A":
        one_item_search_res = requests.get(matching_link, headers=headers)
        one_item_search_soup = BeautifulSoup(one_item_search_res.text, 'html.parser')

        principal_address = get_text("div.detailSection:has(span:contains('Principal Address')) div", parent=one_item_search_soup)

        authorized_persons = []
        authorized_section = one_item_search_soup.select_one("div.detailSection:has(span:contains('Authorized Person(s) Detail'))")
        
        if authorized_section:
            # Find all text nodes directly inside the detailSection
            text_nodes = authorized_section.find_all(string=True, recursive=False)
            clean_texts = []  # Collect all clean text nodes
            for text in text_nodes:
                clean_text = text.strip()
                if clean_text:  # Ignore empty or whitespace-only text nodes
                    clean_texts.append(clean_text)

            # Join all clean text nodes into a single string
            clean_text = " ".join(clean_texts)

    return {
        "umbracoUrl": url,
        "corporation_name": corporation_name,
        "corporation_id": corporation_id,
        "corporation_search_url": corporation_search_url,
        "matching_link": matching_link,
        "principal_address": principal_address,
        "authorized_persons": authorized_persons,
        "clean_text": clean_text,
    }
