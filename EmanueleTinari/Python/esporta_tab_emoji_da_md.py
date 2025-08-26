import os
import re
from collections import Counter
from datetime import datetime

# Percorso cartella locale
folder_path = r'I:\Md'

emoji_pattern = re.compile(
    "["  
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002700-\U000027BF"
    "\U0001F900-\U0001F9FF"
    "\U00002600-\U000026FF"
    "\U0001F700-\U0001F77F"
    "]+", flags=re.UNICODE
)

emoji_counter = Counter()

for filename in os.listdir(folder_path):
    if filename.lower().endswith('.md'):
        filepath = os.path.join(folder_path, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        emojis_found = emoji_pattern.findall(text)
        emoji_counter.update(emojis_found)

now = datetime.now()
date_str = now.strftime('%Y-%m-%d')
datetime_str = now.strftime('%d-%m-%Y %H:%M:%S')
md_filename = f'{date_str} - Icone estratte.md'
md_path = os.path.join(folder_path, md_filename)

lines = [
    f'# Icone estratte il {datetime_str}\n',
    '| Icona | Occorrenze |\n',
    '|-------|------------|\n'
]
for emoji_char, count in emoji_counter.items():
    lines.append(f'| {emoji_char} | {count} |\n')

with open(md_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f'Creato file: {md_path}')
