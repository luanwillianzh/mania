from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests
from bs4 import BeautifulSoup
import urllib.parse
app = FastAPI()

@app.get("/novel/{novel}")
def get_novel_info(novel):
    response = requests.get(f"https://novelmania.com.br/novels/{novel}/", verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    name = soup.find_all("h1",{"class": "font-400 mb-2 wow fadeInRight mr-3"})[0].text.strip().replace("\n", " ")
    desc = "\n".join([ p.text for p in soup.find_all("div", {"class": "text"})[0] ])
    cover = soup.select_one(".img-responsive")["src"]
    chapters = [(a.find_all("strong")[0].text, a["href"].split("/")[-1]) for a in soup.select("ol.list-inline li a")]
    genres = [ [a["href"].split("/")[-1], a["title"]] for a in soup.select(".list-tags a") ]
    return {"nome": name, "desc": desc, "cover": cover, "chapters": chapters, "genres": genres}

@app.get("/novel/{novel}/chapter/{chapter}")
def get_chapter(novel, chapter):
    response = requests.get(f"https://novelmania.com.br/novels/{novel}/capitulos/{chapter}", verify=False)
    soup = BeautifulSoup(response.text)
    title = soup.select_one("h3.mb-0").text.strip().replace("\n", " ")
    try:
      subtitle = soup.select_one("h2.mt-0").text.strip().replace("\n", " ")
    except:
      subtitle = ""
    content = soup.select_one("#chapter-content").prettify().split("<div data-reactionable")[0].split("/h2>\n ")[1]
    return {"title": title, "subtitle": subtitle, "content": content}

@app.get("/search/{text}")
def search(text):
    url = f"https://novelmania.com.br/novels?titulo={urllib.parse.quote_plus(text)}&categoria=&nacionalidade=&status=&ordem=&commit=Pesquisar novel"
    resp = requests.get(url, verify=False).text
    soup = BeautifulSoup(resp, 'html.parser')
    return {"sucesso": True, "resultado": [ {"nome": a.select_one("h5").text, "url": a.select_one("a")["href"].split("/")[-1], "cover": a.select_one("img")["src"]} for a in soup.select(".top-novels") ]}
