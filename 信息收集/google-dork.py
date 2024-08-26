import requests
from bs4 import BeautifulSoup


def google_dork_search(domain):
    query = f'site:{domain} filetype:php'
    url = f'https://www.google.com/search?q={query}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f'Failed to fetch search results for {domain}')
        return None


def extract_php_links(html):
    if html is None:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a')
    php_links = []
    for link in links:
        href = link.get('href')
        if href and href.endswith('.php'):
            php_links.append(href)
    return php_links


def save_to_file(links, output_file):
    with open(output_file, 'w') as f:
        for link in links:
            f.write(link + '\n')


def main(input_file, output_file):
    with open(input_file, 'r') as f:
        domains = [line.strip() for line in f]

    php_links = []
    for domain in domains:
        html = google_dork_search(domain)
        if html:
            links = extract_php_links(html)
            php_links.extend(links)

    save_to_file(php_links, output_file)
    print(f'PHP links saved to {output_file}')


if __name__ == '__main__':
    input_file = 'url.txt'
    output_file = 'output.txt'
    main(input_file, output_file)
