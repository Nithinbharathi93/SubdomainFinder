import flet as ft
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def find_links(domain):
    base_url = f"https://{domain}"
    visited_links = set()
    html_files = []

    def crawl(url):
        if url in visited_links or not url.startswith(base_url):
            return
        visited_links.add(url)
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                for link in soup.find_all("a", href=True):
                    href = link["href"].strip()
                    full_url = urljoin(base_url, href)  # Handle relative URLs
                    if f"//{domain}" in full_url:
                        if full_url not in html_files:
                            html_files.append(full_url)
                    elif not full_url.endswith(
                        (".jpg", ".png", ".css", ".js", ".json", ".xml")
                    ):  # Skip non-relevant files
                        crawl(full_url)  # Recursively crawl other links
            else:
                print(f"Failed to access {url}. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error accessing {url}: {e}")

    crawl(base_url)
    return html_files if html_files else None


def get_subdomains_from_crtsh(domain):
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            cert_data = response.json()
            subdomains = {entry["name_value"] for entry in cert_data}
            return list(subdomains)
    except Exception as e:
        print(f"Error fetching data: {e}")
    return []


def main(page: ft.Page):
    page.title = "Nithin's Seyali"
    page.scroll = "auto"

    domain_input = ft.TextField(label="Domain Name", width=400)

    subdomains_output = ft.TextField(
        label="Subdomains",
        multiline=True,
        width=600,
        height=150,
        read_only=True,
    )

    sitemap_output = ft.TextField(
        label="Sitemap",
        multiline=True,
        width=600,
        height=150,
        read_only=True,
    )

    subdomains_flag = ft.Text(value="", color="red", size=16)
    sitemap_flag = ft.Text(value="", color="red", size=16)

    def search(event):
        domain = domain_input.value.strip()
        if not domain:
            subdomains_flag.value = "Please enter a domain!"
            subdomains_flag.color = "red"
            sitemap_flag.value = ""
            page.update()
            return

        # Clear previous outputs
        subdomains_output.value = ""
        sitemap_output.value = ""
        subdomains_flag.value = "Searching for subdomains..."
        sitemap_flag.value = "Searching for sitemap..."
        page.update()

        # Fetch subdomains
        subdomains = get_subdomains_from_crtsh(domain)
        if subdomains:
            subdomains_flag.value = "Found subdomains!"
            subdomains_flag.color = "green"
            subdomains_output.value = "\n".join(subdomains)
        else:
            subdomains_flag.value = "No subdomains found!"
            subdomains_flag.color = "red"

        # Fetch sitemap
        sitemap = find_links(domain)
        if sitemap:
            sitemap_flag.value = "Found sitemap!"
            sitemap_flag.color = "green"
            sitemap_output.value = "\n".join(sitemap)
        else:
            sitemap_flag.value = "No sitemap found!"
            sitemap_flag.color = "red"

        page.update()

    search_button = ft.ElevatedButton("Search", on_click=search)

    page.add(
        ft.Text(value="Nithin's Sub-Domain matrum SiteMap Thedum Seyali", size=24, weight="bold"),
        domain_input,
        subdomains_output,
        subdomains_flag,
        sitemap_output,
        sitemap_flag,
        search_button,
    )


if __name__ == "__main__":
    ft.app(target=main)
