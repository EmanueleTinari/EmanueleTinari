# === IMPORTAZIONI ===
# Librerie per operazioni asincrone, file I/O, parsing URL, manipolazione HTML, ecc.
import asyncio
import aiohttp
import aiofiles
import hashlib
from urllib.parse import urljoin, urlparse
from pathlib import Path
from bs4 import BeautifulSoup
import re

# === ARRAY arrVers ===
# Import dell'array arrVers contenente metadati dei libri
from arr_vers import arrVers

# === CONFIGURAZIONE ===
# Dominio iniziale e da cui non uscire
startHost = "www.vatican.va"
# URL da cui partire
startUrl = "https://www.vatican.va/archive/bible/nova_vulgata/documents/nova-vulgata_index_lt.html"
# Prefisso di path consentito
allowed_path_prefix = "/archive/bible/nova_vulgata/documents/"
# Profondità massima del crawling
depth = 4
# Base cartella locale dove salvare (corretta per evitare duplicati)
base_folder = Path("I:/scraper")
# Cartella finale corretta
download_folder = base_folder / startHost
# File HTML con indice locale
index_file = download_folder / "index.html"
# Pausa tra download (per worker)
wait_seconds = 3
# Numero massimo di download paralleli
concurrency = 15
# Se True forza il riscaricamento di tutti i file
force = False

# === VARIABILI GLOBALI ===
# Insieme dei link già visitati
visited = set()
# Lista dei link per l'indice finale
index_links = []
# Dominio principale per i controlli
domain = startHost
# Semaforo per limitare le richieste concorrenti
semaphore = asyncio.Semaphore(concurrency)

# === FUNZIONI DI SUPPORTO ===

# Verifica se un link è interno al dominio e alla sezione Nova Vulgata
def is_internal_link(link):
    parsed = urlparse(link)
    return (
        (parsed.netloc == "" or parsed.netloc == domain) and
        parsed.path.startswith(allowed_path_prefix)
    )

# Costruisce un link assoluto pulito da ancore
def normalize_link(base, link):
    return urljoin(base, link.split('#')[0])

# Genera il path locale dove salvare il contenuto dell'URL (fallback)
def get_local_filename(url):
    parsed = urlparse(url)
    path = parsed.path
    if path.endswith("/") or path == "":
        path += "index.html"
    elif not Path(path).suffix:
        path += ".html"
    return download_folder / path.lstrip("/")

# Genera nome file personalizzato per AT/NT basato su _vt_/_nt_
def get_custom_filename(url):
    nome_file = Path(urlparse(url).path).name.lower()
    if "_vt_" in nome_file:
        return download_folder / "AT" / nome_file
    elif "_nt_" in nome_file:
        return download_folder / "NT" / nome_file
    return None

# Calcola hash SHA256 di un file locale (se esiste)
async def file_hash(path):
    h = hashlib.sha256()
    try:
        async with aiofiles.open(path, 'rb') as f:
            while True:
                chunk = await f.read(4096)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
    except FileNotFoundError:
        return None

# Salva contenuto in locale, evitando duplicati se hash coincide
async def save_file(url, content):
    custom_path = get_custom_filename(url)
    path = custom_path if custom_path else get_local_filename(url)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists() and not force:
        existing_hash = await file_hash(path)
        new_hash = hashlib.sha256(content if isinstance(content, bytes) else content.encode("utf-8")).hexdigest()
        if existing_hash == new_hash:
            print(f"🟡 Già presente identico: {url}")
            index_links.append((url, path.relative_to(base_folder).as_posix()))
            return False

    mode = "wb" if isinstance(content, bytes) else "w"
    async with aiofiles.open(path, mode, encoding=None if mode == "wb" else "utf-8") as f:
        await f.write(content)
    print(f"✅ Salvato: {url} → {path}")
    index_links.append((url, path.relative_to(base_folder).as_posix()))
    return True

# Scarica il contenuto dell'URL, restituendo tipo e contenuto
async def fetch(session, url):
    async with semaphore:
        try:
            async with session.get(url) as resp:
                if resp.status != 200:
                    print(f"❌ Errore {resp.status} su {url}")
                    return None, None
                content_type = resp.headers.get("Content-Type", "")
                if "text/html" in content_type:
                    return "html", await resp.text()
                return "binary", await resp.read()
        except Exception as e:
            print(f"⚠️ Errore su {url}: {e}")
            return None, None

# Crawling asincrono ricorsivo, salva file e segue link interni validi
async def crawl(session, url, current_depth):
    if current_depth > depth or url in visited:
        return
    visited.add(url)

    tipo, content = await fetch(session, url)
    if content is None:
        return

    scritto = await save_file(url, content)
    if tipo == "html":
        soup = BeautifulSoup(content, "html.parser")
        tasks = []
        for tag in soup.find_all(["a", "img", "script", "link"]):
            href = tag.get("href") or tag.get("src")
            if not href:
                continue
            link = normalize_link(url, href)
            if is_internal_link(link) and link not in visited:
                tasks.append(crawl(session, link, current_depth + 1))
        if tasks:
            await asyncio.gather(*tasks)

    if scritto:
        print(f"⏳ Attendo {wait_seconds} secondi prima di continuare...")
        await asyncio.sleep(wait_seconds)

# Crea file HTML cliccabile con elenco dei file salvati localmente
async def genera_indice_html():
    async with aiofiles.open(index_file, "w", encoding="utf-8") as f:
        await f.write("<!DOCTYPE html><html><head><meta charset='utf-8'><title>Indice</title></head><body>\n")
        await f.write(f"<h1>Contenuti scaricati da {startUrl}</h1>\n<ul>\n")
        for url, rel_path in sorted(index_links):
            await f.write(f"<li><a href='{rel_path}' target='_blank'>{url}</a></li>\n")
        await f.write("</ul>\n</body></html>")
    print(f"📄 Indice HTML creato: {index_file}")

# Avvia la sessione e lo scraping a partire da startUrl
async def main():
    async with aiohttp.ClientSession() as session:
        await crawl(session, startUrl, 0)
    await genera_indice_html()
    print("🏍️ Fine scraping.")

# Esecuzione diretta
if __name__ == "__main__":
    asyncio.run(main())
