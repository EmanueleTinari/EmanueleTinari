import time
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

print("[INFO] Caricamento indice dal disco…")

# === Configurazioni ===
modello_ollama = "llama3:8b"
percorso_indice = r"I:\LLM_RAG\Indice"

# === LLM locale via Ollama ===
llm = Ollama(model=modello_ollama)

# === Embedding locale (NO OpenAI) ===
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# === Caricamento indice da disco con embedding locale ===
storage_context = StorageContext.from_defaults(persist_dir=percorso_indice)
index = load_index_from_storage(storage_context, embed_model=embed_model)

# === Query engine con retriever basato su similarità ===
retriever = index.as_retriever(similarity_top_k=5)
query_engine = RetrieverQueryEngine.from_args(retriever=retriever, llm=llm)

# === Loop interattivo ===
print("📚 Inserisci la tua domanda (scrivi 'esci' per terminare):")
while True:
    domanda = input("\n❓ Domanda: ")
    if domanda.lower() in ["esci", "exit", "quit"]:
        print("👋 Fine sessione.")
        break
    start = time.time()
    risposta = query_engine.query(domanda)
    end = time.time()
    print("\n🧠 Risposta:\n")
    print(risposta)
    print(f"\n⏱️ Tempo impiegato: {end - start:.2f} secondi")
