import requests
from bs4 import BeautifulSoup


def google_dork(url):
    dorks = [
        f"site:{url} ext:php inurl:?",
        f"site:openbugbounty.org inurl:reports intext:\"{url}\"",
        f"site:{url} ext:log | ext:txt | ext:conf | ext:cnf | ext:ini | ext:env | ext:sh | ext:bak | ext:backup | ext:swp | ext:old | ext:~ | ext:git | ext:svn | ext:htpasswd | ext:htaccess | ext:json",
        f"inurl:q= | inurl:s= | inurl:search= | inurl:query= | inurl:keyword= | inurl:lang= inurl:& site:{url}",
        f"inurl:url= | inurl:return= | inurl:next= | inurl:redirect= | inurl:redir= | inurl:ret= | inurl:r2= | inurl:page= inurl:& inurl:http site:{url}",
        f"inurl:id= | inurl:pid= | inurl:category= | inurl:cat= | inurl:action= | inurl:sid= | inurl:dir= inurl:& site:{url}",
        f"inurl:http | inurl:url= | inurl:path= | inurl:dest= | inurl:html= | inurl:data= | inurl:domain= | inurl:page= inurl:& site:{url}"
    ]

    results = []
    for dork in dorks:
        query = f"https://www.google.com/search?q={dork}"
        response = requests.get(query)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a')
            for link in links:
                href = link.get('href')
                if href.startswith("http") and url in href:
                    results.append(href)

    return results


# Read URLs from url.txt
with open('url.txt', 'r') as file:
    urls = file.readlines()
    urls = [url.strip() for url in urls]

# Perform Google dorking and write results to out.txt
with open('out.txt', 'w') as file:
    for url in urls:
        results = google_dork(url)
        if results:
            file.write(f"Dorks for {url}:\n")
            for result in results:
                file.write(result + "\n")
            file.write("\n")
