# convertitore_base64.py
import base64
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

def convert_to_base64(source: Path, destination: Path) -> None:
    # Controlla che il file sorgente esista
    if not source.exists():
        raise FileNotFoundError(f"File non trovato: {source}")

    # Legge il file e lo codifica in base64
    encoded = base64.b64encode(source.read_bytes()).decode('utf-8')

    # Scrive il contenuto codificato nel file di destinazione
    destination.write_text(encoded, encoding='utf-8')

    # Mostra un messaggio di conferma all'utente
    messagebox.showinfo("Completato", f"File salvato:\n{destination}")

def ask_output_filename(default_name: str, center_x: int, center_y: int) -> str | None:
    result = None  # Variabile che conterrà il nome finale scelto

    def conferma():
        # Recupera il testo inserito e chiude la finestra
        nonlocal result
        result = entry.get().strip()
        win.destroy()

    # Crea una finestra modale per la scelta del nome
    win = tk.Toplevel()
    win.title("Nome file di output")
    win.geometry("550x100+{0}+{1}".format(center_x, center_y))  # Centra la finestra
    win.resizable(False, False)
    win.grab_set()  # Rende la finestra modale

    # Etichetta
    tk.Label(win, text="Nome file .txt:").pack(pady=(10, 0))

    # Campo di inserimento testo, largo
    entry = tk.Entry(win, width=60)
    entry.insert(0, default_name)
    entry.pack(pady=5)
    entry.focus()

    # Tasto INVIO equivale a confermare
    entry.bind("<Return>", lambda _: conferma())

    # Pulsante OK
    tk.Button(win, text="OK", command=conferma).pack()

    # Attende che la finestra venga chiusa
    win.wait_window()
    return result

def ensure_unique_filename(directory: Path, name: str) -> Path:
    # Genera un Path dalla directory e nome file
    candidate = directory / name
    if not candidate.exists():
        return candidate

    # Se esiste, aggiunge _ver1, _ver2, ecc.
    stem, suffix = Path(name).stem, Path(name).suffix
    counter = 1
    while True:
        new_name = f"{stem}_ver{counter}{suffix}"
        new_path = directory / new_name
        if not new_path.exists():
            return new_path
        counter += 1

def main():
    # Inizializza tkinter
    root = tk.Tk()
    root.withdraw()  # Nasconde la finestra principale

    # Ottiene dimensioni schermo per centrare finestre
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    center_x = screen_w // 2 - 275  # 550 larghezza / 2
    center_y = screen_h // 2 - 50   # 100 altezza / 2

    # Directory dello script attuale
    base_dir = Path(__file__).resolve().parent

    # Tipi file supportati
    filetypes = [
        ("PNG files", "*.png"),
        ("JPEG files", "*.jpg;*.jpeg"),
        ("WebP files", "*.webp"),
        ("GIF files", "*.gif"),
        ("SVG files", "*.svg"),
        ("Tutti i file", "*.*")
    ]

    # Finestra di selezione file, centrata
    root.update()  # Aggiorna il gestore della GUI
    root.geometry(f"+{center_x}+{center_y}")  # Centra il file dialog
    selected = filedialog.askopenfilename(
        title="Seleziona un file immagine",
        initialdir=base_dir,
        filetypes=filetypes
    )
    if not selected:
        return  # Uscita se annullato

    src_path = Path(selected)

    # Proposta iniziale del nome txt
    default_txt_name = src_path.stem + "_base64.txt"

    # Input nome file txt (centrata)
    chosen_name = ask_output_filename(default_txt_name, center_x, center_y)
    if not chosen_name:
        return  # Uscita se annullato

    # Verifica se esiste già un file con lo stesso nome, e genera uno univoco
    dst_path = ensure_unique_filename(src_path.parent, chosen_name)

    # Conversione vera e propria
    convert_to_base64(src_path, dst_path)

if __name__ == "__main__":
    main()
