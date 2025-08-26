# -*- coding: utf-8 -*-
# Script per estrarre i paragrafi del 27 luglio dal PDF e generare file Markdown strutturati

# Importo tutte le librerie necessarie
from pdfminer.high_level import extract_text          # Per leggere il testo completo del PDF
import os                                              # Per gestire i percorsi e le cartelle
import re                                              # Per cercare con espressioni regolari
from pathlib import Path                               # Per gestire i path in modo più chiaro e cross-platform

# Percorso assoluto del file PDF da leggere
pdf_path = r"D:\Documents\GitHub\EmanueleTinari\Obsidian\Chiesa\_03 - PDF\Martirologio\pdf_da_elaborare\584-587.pdf"

# Cartella di destinazione per i file Markdown temporanei
output_folder = r"D:\Documents\GitHub\EmanueleTinari\Obsidian\Chiesa\_03 - PDF\Martirologio\santi_md_tmp"

# Verifico se la cartella esiste, altrimenti la creo
os.makedirs(output_folder, exist_ok=True)

# Estraggo tutto il testo dal PDF
full_text = extract_text(pdf_path)

# Trovo solo il blocco che inizia da "27 luglio" fino a "28 luglio"
# Uso lookahead (?=28 luglio) per NON includere "28 luglio" nel match
match = re.search(r"27 luglio(.*?)28 luglio", full_text, re.DOTALL | re.IGNORECASE)

# Se il blocco non viene trovato, interrompo lo script
if not match:
    raise ValueError("Blocco del 27 luglio non trovato nel PDF")

# Estraggo il blocco corrispondente al giorno 27 luglio
giorno_text = match.group(1).strip()

# Divido il blocco in paragrafi numerati: ogni paragrafo inizia con un numero seguito da punto e spazio (es. "1. ")
# Uso una regex per separare i blocchi mantenendo anche l'indice del paragrafo
paragrafi = re.split(r"\n(?=\d{1,2}\. )", giorno_text)

# Ciclo su ogni paragrafo, escludendo eventuali righe vuote
for idx, paragrafo in enumerate(paragrafi, start=1):

    # Pulisco eventuali spazi laterali
    paragrafo = paragrafo.strip()

    # Salto i blocchi troppo brevi o vuoti
    if len(paragrafo) < 20:
        continue

    # Applico sostituzioni per i punti, ? e ! → <br> (come da istruzioni)
    paragrafo_md = re.sub(r'(?<=[.!?])\s+', '<br> ', paragrafo)
    paragrafo_md = paragrafo_md.replace('\n', ' ')  # Rimuove eventuali a capo

    # Nome file Markdown da generare, es: santo_01.md, santo_02.md, ecc.
    file_name = f"santo_{str(idx).zfill(2)}.md"

    # Percorso completo del file da salvare
    file_path = os.path.join(output_folder, file_name)

    # Apro il file in scrittura e salvo tutto il contenuto Markdown
    with open(file_path, "w", encoding="utf-8") as f:

        # Scrivo il frontmatter YAML (lasciato vuoto nei campi variabili)
        f.write('''---
cssclasses: santi
prefisso: 
apostrofato: false
nome: 
giorno: 27
mese: luglio
posizione-Martirologio: %d
genere: 
martire: false
vergine: false
città: 
paese: 
patronato: 
patrono: 
etimologia: 
emblema: 
servo_di_Dio: true
venerabile: true
beato: true
beatificato_da: 
data_beatificazione: 
santo: true
canonizzato_da: 
data_canonizzazione: 
tags:
  - San
  - Santo
  - Santi
  - Santa
  - Sante
  - Giorno
stato: Mancano ancora i link ai riferimenti.
completato: false
licenza-nota: "[Copyright © 2025 Emanuele Tinari under Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)"
---

# 

***

***

> [!foto]- Foto

***

## Dal Martirologio

''' % idx)

        # Inserisco il testo del PDF riformattato nella sezione corretta
        f.write(paragrafo_md + '\n')
        f.write("[Fonte: Vaticano]()\n\n")

        # Aggiungo il resto delle sezioni vuote come da modello
        f.write('''***
### Informazioni aggiuntive
[Fonte: Wikipedia]()

***

## Nota agiografica estesa
[Fonte Santi e Beati]()
''')

# Stampo messaggio finale
print(f"✅ Generati {len(paragrafi)} file Markdown nella cartella:\n{output_folder}")
