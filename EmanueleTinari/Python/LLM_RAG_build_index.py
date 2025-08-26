import os
import time
from tqdm import tqdm
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.settings import Settings

# === CONFIGURAZIONI ===
cartella_markdown = r"D:\Documents\GitHub\EmanueleTinari\Obsidian\Chiesa"
cartella_output = r"I:\LLM_RAG\Indice"

# === MODELLO LOCALE ===
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# === TIMER INIZIALE ===
inizio = time.time()

# === CONTROLLO SE INDICE ESISTE ===
if os.path.exists(cartella_output) and any(os.scandir(cartella_output)):
    print("[INFO] Caricamento indice esistente da:", cartella_output)
    storage_context = StorageContext.from_defaults(persist_dir=cartella_output)
    index = load_index_from_storage(storage_context)
else:
    print("[INFO] Nessun indice trovato, creazione da zero…")
    print("[INFO] Caricamento documenti da:", cartella_markdown)

    # CREA READER CON LE ESTENSIONI SUPORTATE
    reader = SimpleDirectoryReader(cartella_markdown, recursive=True, required_exts=[".md", ".pdf", ".txt", ".epub"])
    
    print("[INFO] Caricamento documenti con SimpleDirectoryReader.load_data() ...")
    documents = reader.load_data()

    print(f"[INFO] Documenti caricati: {len(documents)}")

    # Creazione indice
    index = VectorStoreIndex.from_documents(documents)

    # Salvataggio
    os.makedirs(cartella_output, exist_ok=True)
    index.storage_context.persist(persist_dir=cartella_output)
    print(f"[INFO] Indice salvato in: {cartella_output}")

# === TIMER FINALE ===
fine = time.time()
durata = fine - inizio
minuti = int(durata // 60)
secondi = int(durata % 60)
print(f"[FINE] Tempo impiegato: {minuti} minuti e {secondi} secondi")
