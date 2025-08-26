# === IMPORTAZIONI ===
import asyncio
import aiohttp
import aiofiles
import hashlib
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# array contenente i nomi delle sottocartelle della cartella /CEI 1974/
# Nessuna sottocartella dovrà essere nominata diversamente o essercene una in più o in meno.
# Questo array è usato per definire la struttura delle directory.
arrSubFolders = [
    "AT - 01 Genesi",
    "AT - 02 Esodo",
    "AT - 03 Levitico",
    "AT - 04 Numeri",
    "AT - 05 Deuteronomio",
    "AT - 06 Giosuè",
    "AT - 07 Giudici",
    "AT - 08 Rut",
    "AT - 09 1 Samuele",
    "AT - 10 2 Samuele",
    "AT - 11 1 Re",
    "AT - 12 2 Re",
    "AT - 13 1 Cronache",
    "AT - 14 2 Cronache",
    "AT - 15 Esdra",
    "AT - 16 Neemia",
    "AT - 17 Tobia",
    "AT - 18 Giuditta",
    "AT - 19 Ester",
    "AT - 20 1 Maccabei",
    "AT - 21 2 Maccabei",
    "AT - 22 Giobbe",
    "AT - 23 Salmi",
    "AT - 24 Proverbi",
    "AT - 25 Qoelet",
    "AT - 26 Cantico",
    "AT - 27 Sapienza",
    "AT - 28 Siracide",
    "AT - 29 Isaia",
    "AT - 30 Geremia",
    "AT - 31 Lamentazioni",
    "AT - 32 Baruc",
    "AT - 33 Ezechiele",
    "AT - 34 Daniele",
    "AT - 35 Osea",
    "AT - 36 Gioele",
    "AT - 37 Amos",
    "AT - 38 Abdia",
    "AT - 39 Giona",
    "AT - 40 Michea",
    "AT - 41 Naum",
    "AT - 42 Abacuc",
    "AT - 43 Sofonia",
    "AT - 44 Aggeo",
    "AT - 45 Zaccaria",
    "AT - 46 Malachia",
    "NT - 47 Matteo",
    "NT - 48 Marco",
    "NT - 49 Luca",
    "NT - 50 Giovanni",
    "NT - 51 Atti",
    "NT - 52 Romani",
    "NT - 53 1 Corinzi",
    "NT - 54 2 Corinzi",
    "NT - 55 Galati",
    "NT - 56 Efesini",
    "NT - 57 Filippesi",
    "NT - 58 Colossesi",
    "NT - 59 1 Tessalonicesi",
    "NT - 60 2 Tessalonicesi",
    "NT - 61 1 Timoteo",
    "NT - 62 2 Timoteo",
    "NT - 63 Tito",
    "NT - 64 Filemone",
    "NT - 65 Ebrei",
    "NT - 66 Giacomo",
    "NT - 67 1 Pietro",
    "NT - 68 2 Pietro",
    "NT - 69 1 Giovanni",
    "NT - 70 2 Giovanni",
    "NT - 71 3 Giovanni",
    "NT - 72 Giuda",
    "NT - 73 Apocalisse"
]

# array contenente le informazioni sui libri della Bibbia
arrVers = [
    ['Numero libro','1', 'Testamento','Antico Testamento', 'Gruppo','Il Pentateuco', 'Nome libro IT','Genesi','AbbrIT','Gn;Gen;Ge','Nome libro LT','Liber Genesis','AbbrLT','Gen','Nome libro EN','Genesis','AbbrEN','Gen'],
    ['Numero libro','2', 'Testamento','Antico Testamento', 'Gruppo','Il Pentateuco', 'Nome libro IT','Esodo','AbbrIT','Es;Eso;Eo','Nome libro LT','Liber Exodus','AbbrLT','Ex','Nome libro EN','Exodus','AbbrEN','Exod'],
    ['Numero libro','3', 'Testamento','Antico Testamento', 'Gruppo','Il Pentateuco', 'Nome libro IT','Levitico','AbbrIT','Lv;Le','Nome libro LT','Liber Leviticus','AbbrLT','Lev','Nome libro EN','Leviticus','AbbrEN','Lev'],
    ['Numero libro','4', 'Testamento','Antico Testamento', 'Gruppo','Il Pentateuco', 'Nome libro IT','Numeri','AbbrIT','Nm;Nu','Nome libro LT','Liber Numeri','AbbrLT','Num','Nome libro EN','Numbers','AbbrEN','Nun'],
    ['Numero libro','5', 'Testamento','Antico Testamento', 'Gruppo','Il Pentateuco', 'Nome libro IT','Deuteronomio','AbbrIT','Dt;Deut;De','Nome libro LT','Liber Deuteronomii','AbbrLT','Deut','Nome libro EN','Deuteronomy','AbbrEN','Deut'],
    ['Numero libro','6', 'Testamento','Antico Testamento', 'Gruppo','I libri storici', 'Nome libro IT','Giosuè','AbbrIT','Gs;Gios','Nome libro LT','Liber Josue','AbbrLT','Ios','Nome libro EN','Joshua','AbbrEN','Josh'],
    ['Numero libro','7', 'Testamento','Antico Testamento', 'Gruppo','I libri storici', 'Nome libro IT','Giudici','AbbrIT','Gdc; Giudic;Gc','Nome libro LT','Liber Judicum','AbbrLT','Iudc','Nome libro EN','Judges','AbbrEN','Judg'],
    ['Numero libro','8', 'Testamento','Antico Testamento', 'Gruppo','I libri storici', 'Nome libro IT','Rut','AbbrIT','Rt;Ru','Nome libro LT','Liber Ruth','AbbrLT','Ruth','Nome libro EN','Ruth','AbbrEN','Ruth'],
    ['Numero libro','9', 'Testamento','Antico Testamento', 'Gruppo','I libri storici', 'Nome libro IT','Primo libro di Samuele (=1 Re)','AbbrIT','1Sam;1 Sam;1S;ISam;I Sam;IS;I S','Nome libro LT','Liber Primus Regum','AbbrLT','1 Re','Nome libro EN','1 Samuel','AbbrEN','1 Sam'],
    ['Numero libro','10', 'Testamento','Antico Testamento', 'Gruppo','I libri storici', 'Nome libro IT','Secondo libro di Samuele (=2 Re)','AbbrIT','2Sam;2 Sam;2S;IISam;II Sam;IIS;II S','Nome libro LT','Liber Secundus Regum','AbbrLT','2 Re','Nome libro EN','2 Samuel','AbbrEN','2 Sam'],
    ['Numero libro','11', 'Testamento','Antico Testamento', 'Gruppo','I libri storici', 'Nome libro IT','Primo libro dei Re (=3 Re)','AbbrIT','1Re;1 Re;1R;1 R;IRe;I Re;IR;I R','Nome libro LT','Liber Tertius Regum','AbbrLT','3 Re','Nome libro EN','1 Kings','AbbrEN','1 Kgs'],
    ['Numero libro','12', 'Testamento','Antico Testamento', 'Gruppo','I libri storici', 'Nome libro IT','Secondo libro dei Re (=4 Re)','AbbrIT','2Re;2 Re;2R;2 R;IIRe;II Re;IIR;II R','Nome libro LT','Liber Quartus Regum','AbbrLT','4 Re','Nome libro EN','2 Kings','AbbrEN','2 Kgs'],
    ['Numero libro','13', 'Testamento','Antico Testamento', 'Gruppo','I libri storici', 'Nome libro IT','Primo libro delle Cronache (Paralipomeni)','AbbrIT','1Cr;1 Cr;I Cr;ICr','Nome libro LT','Liber Primus Paralipomenon','AbbrLT','1Par','Nome libro EN','1 Chronicles','AbbrEN','1 Chr'],
    ['Numero libro','14', 'Testamento','Antico Testamento', 'Gruppo','I libri storici', 'Nome libro IT','Secondo libro delle Cronache (Paralipomeni)','AbbrIT','2Cr;2 Cr;II Cr;IICr','Nome libro LT','Liber Secundus Paralipomenon','AbbrLT','2Par','Nome libro EN','2 Chronicles','AbbrEN','2 Chr'],
    ['Numero libro','15', 'Testamento','Antico Testamento', 'Gruppo','I libri storici', 'Nome libro IT','Esdra (= 1 Esdra)','AbbrIT','Esd;Ed','Nome libro LT','Liber Esdræ','AbbrLT','Esd','Nome libro EN','Ezra','AbbrEN','Ezra'],
    ['Numero libro','16', 'Testamento','Antico Testamento', 'Gruppo','I libri storici', 'Nome libro IT','Neemia (= 2 Esdra)','AbbrIT','Ne','Nome libro LT','Liber Nehemiæ','AbbrLT','Neh','Nome libro EN','Nehemiah','AbbrEN','Neh'],
    ['Numero libro','17', 'Testamento','Antico Testamento', 'Gruppo','I libri storici', 'Nome libro IT','Tobia','AbbrIT','Tb;Tob;To','Nome libro LT','Liber Tobiæ','AbbrLT','Tob','Nome libro EN','Tobit','AbbrEN','Tob'],
    ['Numero libro','18', 'Testamento','Antico Testamento', 'Gruppo','I libri storici', 'Nome libro IT','Giuditta','AbbrIT','Gdt;Giudit','Nome libro LT','Liber Judith','AbbrLT','Iudt','Nome libro EN','Judith','AbbrEN','Jdt'],
    ['Numero libro','19', 'Testamento','Antico Testamento', 'Gruppo','I libri storici', 'Nome libro IT','Ester','AbbrIT','Est;Et','Nome libro LT','Liber Esther','AbbrLT','Esth','Nome libro EN','Esther','AbbrEN','Esth'],
    ['Numero libro','20', 'Testamento','Antico Testamento', 'Gruppo','I libri storici', 'Nome libro IT','Primo libro dei Maccabei','AbbrIT','1Mac;1 Mac;1Macc;1 Macc;IMac;I Mac;IMacc;I Macc;1M;1 M;IM;I M','Nome libro LT','Liber I Machabæorum','AbbrLT','1 Mach','Nome libro EN','1 Maccabees','AbbrEN','1 Macc'],
    ['Numero libro','21', 'Testamento','Antico Testamento', 'Gruppo','I libri storici', 'Nome libro IT','Secondo libro dei Maccabei','AbbrIT','2Mac;2 Mac;2Macc;2 Macc;IIMac;II Mac;IIMacc;II Macc;2M;2 M;IIM;II M','Nome libro LT','Liber II Machabæorum','AbbrLT','2 Mach','Nome libro EN','2 Maccabees','AbbrEN','2 Macc'],
    ['Numero libro','22', 'Testamento','Antico Testamento', 'Gruppo','I libri poetici e sapienziali', 'Nome libro IT','Giobbe','AbbrIT','Gb;Giob','Nome libro LT','Liber Job','AbbrLT','Iob','Nome libro EN','Job','AbbrEN','Job'],
    ['Numero libro','23', 'Testamento','Antico Testamento', 'Gruppo','I libri poetici e sapienziali', 'Nome libro IT','Salmi','AbbrIT','Sal;Sl','Nome libro LT','Liber Psalmorum','AbbrLT','Ps','Nome libro EN','Psalms','AbbrEN','Ps(s)'],
    ['Numero libro','24', 'Testamento','Antico Testamento', 'Gruppo','I libri poetici e sapienziali', 'Nome libro IT','Proverbi','AbbrIT','Prv;Prov;P','Nome libro LT','Liber Proverbiorum','AbbrLT','Prov','Nome libro EN','Proverbs','AbbrEN','Prov'],
    ['Numero libro','25', 'Testamento','Antico Testamento', 'Gruppo','I libri poetici e sapienziali', 'Nome libro IT','Qoelet (=Ecclesiaste)','AbbrIT','Qo;Ec;Q','Nome libro LT','Liber Ecclesiastes','AbbrLT','Eccle','Nome libro EN','Ecclesiastes','AbbrEN','Eccl'],
    ['Numero libro','26', 'Testamento','Antico Testamento', 'Gruppo','I libri poetici e sapienziali', 'Nome libro IT','Cantico','AbbrIT','Ct;Ca;CC','Nome libro LT','Canticum Canticorum Salomonis','AbbrLT','Cant','Nome libro EN','Song of Songs','AbbrEN','Song'],
    ['Numero libro','27', 'Testamento','Antico Testamento', 'Gruppo','I libri poetici e sapienziali', 'Nome libro IT','Sapienza','AbbrIT','Sap','Nome libro LT','Liber Sapientiæ','AbbrLT','Sap','Nome libro EN','Wisdom of Solomon','AbbrEN','Wis'],
    ['Numero libro','28', 'Testamento','Antico Testamento', 'Gruppo','I libri poetici e sapienziali', 'Nome libro IT','Siracide (= Ecclesiastico)','AbbrIT','Sir;Si','Nome libro LT','Ecclesiasticus Jesu, filii Sirach','AbbrLT','Eccli','Nome libro EN','Sirach/ Ecclesiasticus','AbbrEN','Sir'],
    ['Numero libro','29', 'Testamento','Antico Testamento', 'Gruppo','I libri profetici: Profeti maggiori', 'Nome libro IT','Isaia','AbbrIT','Is','Nome libro LT','Prophetia Isaiæ','AbbrLT','Isai;Isa','Nome libro EN','Isaiah','AbbrEN','Isa'],
    ['Numero libro','30', 'Testamento','Antico Testamento', 'Gruppo','I libri profetici: Profeti maggiori', 'Nome libro IT','Geremia','AbbrIT','Ger;Gr','Nome libro LT','Prophetia Jeremiæ','AbbrLT','Ier','Nome libro EN','Jeremiah','AbbrEN','Jer'],
    ['Numero libro','31', 'Testamento','Antico Testamento', 'Gruppo','I libri profetici: Profeti maggiori', 'Nome libro IT','Lamentazioni','AbbrIT','Lam;La','Nome libro LT','Lamentationes Jeremiæ Prophetæ','AbbrLT','Lam','Nome libro EN','Lamentations','AbbrEN','Lam'],
    ['Numero libro','32', 'Testamento','Antico Testamento', 'Gruppo','I libri profetici: Profeti maggiori', 'Nome libro IT','Baruc','AbbrIT','Bar;B','Nome libro LT','Prophetia Baruch','AbbrLT','Bar','Nome libro EN','Baruch','AbbrEN','Bar'],
    ['Numero libro','33', 'Testamento','Antico Testamento', 'Gruppo','I libri profetici: Profeti maggiori', 'Nome libro IT','Ezechiele','AbbrIT','Ez','Nome libro LT','Prophetia Ezechielis','AbbrLT','Ez','Nome libro EN','Ezekiel','AbbrEN','Ezek'],
    ['Numero libro','34', 'Testamento','Antico Testamento', 'Gruppo','I libri profetici: Profeti maggiori', 'Nome libro IT','Daniele','AbbrIT','Dn;Dan;Da','Nome libro LT','Prophetia Danielis','AbbrLT','Dan','Nome libro EN','Daniel','AbbrEN','Dan'],
    ['Numero libro','35', 'Testamento','Antico Testamento', 'Gruppo','I libri profetici: Profeti minori', 'Nome libro IT','Osea','AbbrIT','Os;O','Nome libro LT','Prophetia Osee','AbbrLT','Os','Nome libro EN','Hosea','AbbrEN','Hos'],
    ['Numero libro','36', 'Testamento','Antico Testamento', 'Gruppo','I libri profetici: Profeti minori', 'Nome libro IT','Gioele','AbbrIT','Gl;Gioe;Gi','Nome libro LT','Prophetia Joël','AbbrLT','Ioel','Nome libro EN','Joel','AbbrEN','Joel'],
    ['Numero libro','37', 'Testamento','Antico Testamento', 'Gruppo','I libri profetici: Profeti minori', 'Nome libro IT','Amos','AbbrIT','Am','Nome libro LT','Prophetia Amos','AbbrLT','Am','Nome libro EN','Amos','AbbrEN','Amos'],
    ['Numero libro','38', 'Testamento','Antico Testamento', 'Gruppo','I libri profetici: Profeti minori', 'Nome libro IT','Abdia','AbbrIT','Abd;Ad','Nome libro LT','Prophetia Abdiæ','AbbrLT','Abd','Nome libro EN','Obadiah','AbbrEN','Obad'],
    ['Numero libro','39', 'Testamento','Antico Testamento', 'Gruppo','I libri profetici: Profeti minori', 'Nome libro IT','Giona','AbbrIT','Gio;Gion','Nome libro LT','Prophetia Jonæ','AbbrLT','Ion','Nome libro EN','Jonah','AbbrEN','Jonah'],
    ['Numero libro','40', 'Testamento','Antico Testamento', 'Gruppo','I libri profetici: Profeti minori', 'Nome libro IT','Michea','AbbrIT','Mi','Nome libro LT','Prophetia Michææ','AbbrLT','Mic','Nome libro EN','Micah','AbbrEN','Mic'],
    ['Numero libro','41', 'Testamento','Antico Testamento', 'Gruppo','I libri profetici: Profeti minori', 'Nome libro IT','Naum','AbbrIT','Na','Nome libro LT','Prophetia Nahum','AbbrLT','Nah','Nome libro EN','Nahum','AbbrEN','Nah'],
    ['Numero libro','42', 'Testamento','Antico Testamento', 'Gruppo','I libri profetici: Profeti minori', 'Nome libro IT','Abacuc','AbbrIT','Ab;Abac;Aba;Ac;H','Nome libro LT','Prophetia Habacuc','AbbrLT','Hab','Nome libro EN','Habakkuk','AbbrEN','Hab'],
    ['Numero libro','43', 'Testamento','Antico Testamento', 'Gruppo','I libri profetici: Profeti minori', 'Nome libro IT','Sofonia','AbbrIT','Sof;So','Nome libro LT','Prophetia Sophoniæ','AbbrLT','Soph','Nome libro EN','Zephaniah','AbbrEN','Zeph'],
    ['Numero libro','44', 'Testamento','Antico Testamento', 'Gruppo','I libri profetici: Profeti minori', 'Nome libro IT','Aggeo','AbbrIT','Ag;Agg','Nome libro LT','Prophetia Aggæi','AbbrLT','Agg','Nome libro EN','Haggai','AbbrEN','Hag'],
    ['Numero libro','45', 'Testamento','Antico Testamento', 'Gruppo','I libri profetici: Profeti minori', 'Nome libro IT','Zaccaria','AbbrIT','Zc;Zac;Z','Nome libro LT','Prophetia Zachariæ','AbbrLT','Zach','Nome libro EN','Zechariah','AbbrEN','Zech'],
    ['Numero libro','46', 'Testamento','Antico Testamento', 'Gruppo','I libri profetici: Profeti minori', 'Nome libro IT','Malachia','AbbrIT','Ml;Mal','Nome libro LT','Prophetia Malachiæ','AbbrLT','Mal','Nome libro EN','Malachi','AbbrEN','Mal'],
    ['Numero libro','47', 'Testamento','Nuovo Testamento', 'Gruppo','I Vangeli', 'Nome libro IT','Vangelo di san Matteo Apostolo','AbbrIT','Mt;Mat','Nome libro LT','Evangelium secundum Matthæum','AbbrLT','Matteo','Nome libro EN','Matthew','AbbrEN','Matt'],
    ['Numero libro','48', 'Testamento','Nuovo Testamento', 'Gruppo','I Vangeli', 'Nome libro IT','Vangelo di san Marco','AbbrIT','Mc;Mar;Mr','Nome libro LT','Evangelium secundum Marcum','AbbrLT','Marco','Nome libro EN','Mark','AbbrEN','Mark'],
    ['Numero libro','49', 'Testamento','Nuovo Testamento', 'Gruppo','I Vangeli', 'Nome libro IT','Vangelo di san Luca','AbbrIT','Lc;Lu','Nome libro LT','Evangelium secundum Lucam','AbbrLT','Luca','Nome libro EN','Luke','AbbrEN','Luke'],
    ['Numero libro','50', 'Testamento','Nuovo Testamento', 'Gruppo','I Vangeli', 'Nome libro IT','Vangelo di san Giovanni Apostolo','AbbrIT','Gv;Giov','Nome libro LT','Evangelium secundum Joannem','AbbrLT','Io','Nome libro EN','John','AbbrEN','John'],
    ['Numero libro','51', 'Testamento','Nuovo Testamento', 'Gruppo','Atti', 'Nome libro IT','Atti degli Apostoli','AbbrIT','At','Nome libro LT','Actus Apostolorum','AbbrLT','Act','Nome libro EN','Acts','AbbrEN','Acts'],
    ['Numero libro','52', 'Testamento','Nuovo Testamento', 'Gruppo','Le Lettere Paoline', 'Nome libro IT','Lettera di san Paolo Apostolo ai Romani','AbbrIT','Rm;Ro','Nome libro LT','Epistola B. Pauli Apostoli ad Romanos','AbbrLT','Rom','Nome libro EN','Romans','AbbrEN','Rom'],
    ['Numero libro','53', 'Testamento','Nuovo Testamento', 'Gruppo','Le Lettere Paoline', 'Nome libro IT','Prima lettera di san Paolo Apostolo ai Corinzi','AbbrIT','1Cor;1 Cor;I Cor;ICor;1Co;ICo;1 Co;I Co','Nome libro LT','Epistola B. Pauli Apostoli ad Corinthios Prima','AbbrLT','1Cor','Nome libro EN','1 Corinthians','AbbrEN','1 Cor'],
    ['Numero libro','54', 'Testamento','Nuovo Testamento', 'Gruppo','Le Lettere Paoline', 'Nome libro IT','Seconda lettera di san Paolo Apostolo ai Corinzi','AbbrIT','2Cor;2 Cor;II cor;IICor;2Co;IICo;2 Co;II Co','Nome libro LT','Epistola B. Pauli Apostoli ad Corinthios Secunda','AbbrLT','2Cor','Nome libro EN','2 Corinthians','AbbrEN','2 Cor'],
    ['Numero libro','55', 'Testamento','Nuovo Testamento', 'Gruppo','Le Lettere Paoline', 'Nome libro IT','Lettera di san Paolo Apostolo ai Galati','AbbrIT','Gal;Ga','Nome libro LT','Epistola B. Pauli Apostoli ad Galatas','AbbrLT','Gal','Nome libro EN','Galatians','AbbrEN','Gal'],
    ['Numero libro','56', 'Testamento','Nuovo Testamento', 'Gruppo','Le Lettere Paoline', 'Nome libro IT','Lettera di san Paolo Apostolo agli Efesini','AbbrIT','Ef','Nome libro LT','Epistola B. Pauli Apostoli ad Ephesios','AbbrLT','Eph','Nome libro EN','Ephesians','AbbrEN','Eph'],
    ['Numero libro','57', 'Testamento','Nuovo Testamento', 'Gruppo','Le Lettere Paoline', 'Nome libro IT','Lettera di san Paolo Apostolo ai Filippesi','AbbrIT','Fil;Fili;Fl','Nome libro LT','Epistola B. Pauli Apostoli ad Philippenses','AbbrLT','Phil','Nome libro EN','Philippians','AbbrEN','Phil'],
    ['Numero libro','58', 'Testamento','Nuovo Testamento', 'Gruppo','Le Lettere Paoline', 'Nome libro IT','Lettera di san Paolo Apostolo ai Colossesi','AbbrIT','Col;Cl;Co','Nome libro LT','Epistola B. Pauli Apostoli ad Colossenses','AbbrLT','Col','Nome libro EN','Colossians','AbbrEN','Col'],
    ['Numero libro','59', 'Testamento','Nuovo Testamento', 'Gruppo','Le Lettere Paoline', 'Nome libro IT','Prima Lettera di san Paolo Apostolo ai Tessalonicesi','AbbrIT','1Ts;1 Ts;1Te;1 Te;ITs;I Ts;ITe;I Te','Nome libro LT','Epistola B. Pauli Apostoli ad Thessalonicenses Prima','AbbrLT','1 Thess','Nome libro EN','1 Thessalonians','AbbrEN','1 Thess'],
    ['Numero libro','60', 'Testamento','Nuovo Testamento', 'Gruppo','Le Lettere Paoline', 'Nome libro IT','Seconda Lettera di san Paolo Apostolo ai Tessalonicesi','AbbrIT','2Ts;2 Ts;2Te;2 Te;IITs;II Ts;IITe;II Te','Nome libro LT','Epistola B. Pauli Apostoli ad Thessalonicenses Secunda','AbbrLT','2 Thess','Nome libro EN','2 Thessalonians','AbbrEN','2 Thess'],
    ['Numero libro','61', 'Testamento','Nuovo Testamento', 'Gruppo','Le Lettere Paoline', 'Nome libro IT','Prima Lettera di san Paolo Apostolo a Timoteo','AbbrIT','1Tm;1 Tm;1Ti;1 Ti;ITm;I Tm;ITi;I Ti','Nome libro LT','Epistola B. Pauli Apostoli ad Timotheum Prima','AbbrLT','1 Tim','Nome libro EN','1 Timothy','AbbrEN','1 Tim'],
    ['Numero libro','62', 'Testamento','Nuovo Testamento', 'Gruppo','Le Lettere Paoline', 'Nome libro IT','Seconda Lettera di san Paolo Apostolo a Timoteo','AbbrIT','2Tm;2 Tm;2Ti;2 Ti;IITm;II Tm;IITi;II Ti','Nome libro LT','Epistola B. Pauli Apostoli ad Timotheum Secunda','AbbrLT','2 Tim','Nome libro EN','2 Timothy','AbbrEN','2 Tim'],
    ['Numero libro','63', 'Testamento','Nuovo Testamento', 'Gruppo','Le Lettere Paoline', 'Nome libro IT','Lettera di san Paolo Apostolo a Tito','AbbrIT','Tt;Ti;Tit','Nome libro LT','Epistola B. Pauli Apostoli ad Titum','AbbrLT','Tit','Nome libro EN','Titus','AbbrEN','Titus'],
    ['Numero libro','64', 'Testamento','Nuovo Testamento', 'Gruppo','Le Lettere Paoline', 'Nome libro IT','Lettera di san Paolo Apostolo a Filemone','AbbrIT','Fm;File','Nome libro LT','Epistola B. Pauli Apostoli ad Philemonem','AbbrLT','Philem','Nome libro EN','Philemon','AbbrEN','Phlm'],
    ['Numero libro','65', 'Testamento','Nuovo Testamento', 'Gruppo','Le altre Lettere Cattoliche', 'Nome libro IT','Lettera agli Ebrei','AbbrIT','Eb','Nome libro LT','Epistola B. Pauli Apostoli ad Hebræos','AbbrLT','Hebr','Nome libro EN','Hebrews','AbbrEN','Heb'],
    ['Numero libro','66', 'Testamento','Nuovo Testamento', 'Gruppo','Le altre Lettere Cattoliche', 'Nome libro IT','Lettera di san Giacomo Apostolo','AbbrIT','Gc;Giac;Gia;Gm','Nome libro LT','Epistola Catholica B. Judæ Apostoli','AbbrLT','Iac','Nome libro EN','James','AbbrEN','Jas'],
    ['Numero libro','67', 'Testamento','Nuovo Testamento', 'Gruppo','Le altre Lettere Cattoliche', 'Nome libro IT','Prima Lettera di san Pietro Apostolo','AbbrIT','1Pt;1 Pt;1P;1 P;IP;I P','Nome libro LT','Epistola B. Petri Apostoli Prima','AbbrLT','1Pt','Nome libro EN','1 Peter','AbbrEN','1 Pet'],
    ['Numero libro','68', 'Testamento','Nuovo Testamento', 'Gruppo','Le altre Lettere Cattoliche', 'Nome libro IT','Seconda Lettera di san Pietro Apostolo','AbbrIT','2Pt;2 Pt;2P;2 P;IIP;II P','Nome libro LT','Epistola B. Petri Apostoli Secunda','AbbrLT','2Pt','Nome libro EN','2 Peter','AbbrEN','2 Pet'],
    ['Numero libro','69', 'Testamento','Nuovo Testamento', 'Gruppo','Le altre Lettere Cattoliche', 'Nome libro IT','Prima lettera di san Giovanni Apostolo ed Evangelista','AbbrIT','1Gv;1 Gv;I Gv;IGv;1G;1 G;IG;I G','Nome libro LT','Epistola B. Joannis Apostoli Prima','AbbrLT','I Io','Nome libro EN','1 John','AbbrEN','1 John'],
    ['Numero libro','70', 'Testamento','Nuovo Testamento', 'Gruppo','Le altre Lettere Cattoliche', 'Nome libro IT','Seconda lettera di san Giovanni Apostolo ed Evangelista','AbbrIT','2Gv;2 Gv;II Gv;IIGv;2G;2 G;IIG;II G','Nome libro LT','Epistola B. Joannis Apostoli Secunda','AbbrLT','II Io','Nome libro EN','2 John','AbbrEN','2 John'],
    ['Numero libro','71', 'Testamento','Nuovo Testamento', 'Gruppo','Le altre Lettere Cattoliche', 'Nome libro IT','Terza lettera di san Giovanni Apostolo ed Evangelista','AbbrIT','3Gv;3 Gv;III Gv;IIIGv;3G;3 G;IIIG;III G','Nome libro LT','Epistola B. Joannis Apostoli Tertia','AbbrLT','III Io','Nome libro EN','3 John','AbbrEN','3 John'],
    ['Numero libro','72', 'Testamento','Nuovo Testamento', 'Gruppo','Le altre Lettere Cattoliche', 'Nome libro IT','Lettera di san Giuda Apostolo','AbbrIT','Gd;Giuda','Nome libro LT','Epistola Catholica B. Judæ Apostoli','AbbrLT','Iud','Nome libro EN','Jude','AbbrEN','Jude'],
    ['Numero libro','73', 'Testamento','Nuovo Testamento', 'Gruppo','Scritti apocalittici e apocalittica', 'Nome libro IT','Apocalisse di san Giovanni Apostolo ed Evangelista','AbbrIT','Ap','Nome libro LT','Apocalypsis B. Joannis Apostoli','AbbrLT','Apoc','Nome libro EN','Revelation','AbbrEN','Rev']
]

# === CONFIGURAZIONE ===
startHost = "www.bibbiaedu.it"
startUrl = "https://www.bibbiaedu.it/CEI1974/"
allowed_path_prefix = "/CEI1974/"
depth = 10
base_folder = Path("I:/scraper")
download_folder = base_folder / startHost
index_file = download_folder / "index bibbiaedu.html"
wait_seconds = 2
concurrency = 10
force = False

# === VARIABILI GLOBALI ===
visited = set()
index_links = []
domain = startHost
semaphore = asyncio.Semaphore(concurrency)

# === FUNZIONI DI SUPPORTO ===
def get_book_metadata_and_folder_map() -> Tuple[Dict[str, Dict[str, str]], Dict[str, str]]:
    """
    Converte arrVers e arrSubFolders in due dizionari:
    - book_metadata_map: mappatura abbreviazioni URL -> metadati completi del libro.
    - book_folder_map: mappatura abbreviazioni URL -> nome esatto della cartella.
    """
    book_metadata_map = {}
    book_folder_map = {}
    
    # Crea un dizionario per una ricerca più efficiente dei nomi delle cartelle
    subfolders_map = {re.sub(r'^\w{2} - \d{2} ', '', name).strip().lower(): name for name in arrSubFolders}

    for entry in arrVers:
        book_dict = {}
        for i in range(0, len(entry), 2):
            book_dict[entry[i]] = entry[i+1]
        
        # Mappa le abbreviazioni della Bibbia ai metadati completi.
        abbr = book_dict.get('AbbrIT', '').split(';')[0].strip().replace(" ", "").lower()
        if abbr:
            book_metadata_map[abbr] = book_dict

        # Trova e mappa il nome della cartella esatto
        book_name_it = book_dict.get('Nome libro IT', '').lower()
        # Gestisce i casi speciali come "Primo libro di Samuele (=1 Re)"
        clean_book_name = re.sub(r' \(.+\)', '', book_name_it).strip()
        
        if clean_book_name in subfolders_map:
            book_folder_map[abbr] = subfolders_map[clean_book_name]

    # Gestione di casi speciali e abbreviazioni non univoche
    # Ad es. Esodo con AbbrIT = "Es"
    if 'esodo' in subfolders_map:
        book_folder_map['es'] = subfolders_map['esodo']

    # Ad es. Matteo con AbbrIT = "Mt"
    if 'matteo' in subfolders_map:
        book_folder_map['mt'] = subfolders_map['matteo']
    
    # Ad es. Luca con AbbrIT = "Lc"
    if 'luca' in subfolders_map:
        book_folder_map['lc'] = subfolders_map['luca']

    # Ad es. Giacomo con AbbrIT = "Gc"
    if 'giacomo' in subfolders_map:
        book_folder_map['gc'] = subfolders_map['giacomo']
    
    # Ad es. Giovanni con AbbrIT = "Gv"
    if 'giovanni' in subfolders_map:
        book_folder_map['gv'] = subfolders_map['giovanni']

    return book_metadata_map, book_folder_map

BOOKS_METADATA_MAP, BOOK_FOLDER_MAP = get_book_metadata_and_folder_map()

def is_internal_link(link: str) -> bool:
    """Verifica se un link è interno al dominio e al percorso consentito."""
    parsed = urlparse(link)
    return (
        (parsed.netloc == "" or parsed.netloc == domain) and
        parsed.path.startswith(allowed_path_prefix)
    )

def normalize_link(base: str, link: str) -> str:
    """Normalizza un link rimuovendo gli anchor e unendolo all'URL base."""
    parsed_link = urlparse(link)
    cleaned_link = parsed_link._replace(fragment="").geturl()
    return urljoin(base, cleaned_link)

def get_local_path(url: str) -> Path:
    """
    Crea il percorso locale per salvare il file, utilizzando l'array arrSubFolders
    per definire la struttura delle directory.
    """
    parsed_url = urlparse(url)
    url_path = parsed_url.path
    
    path_without_prefix = url_path.lstrip(allowed_path_prefix).lstrip('/')
    
    cei_folder = download_folder / "CEI1974"

    # Gestisce URL speciali (radice e testamenti)
    if not path_without_prefix:
        return cei_folder / "index.html"
    
    path_segments = [seg for seg in path_without_prefix.split('/') if seg]
    
    if len(path_segments) >= 2:
        testamento_abbr = path_segments[0]
        book_abbr = path_segments[1].lower()
        
        book_info = BOOKS_METADATA_MAP.get(book_abbr)
        folder_name = BOOK_FOLDER_MAP.get(book_abbr)

        if book_info and folder_name:
            book_folder_path = cei_folder / folder_name

            if len(path_segments) == 2:
                # Pagina di introduzione al libro (es. /at/gn/)
                file_name = f"CEI 74 {book_info['Nome libro IT']}.html"
                return book_folder_path / file_name
            elif len(path_segments) == 3 and path_segments[2].isdigit():
                # Pagina di un capitolo (es. /at/gn/1)
                chapter_num = int(path_segments[2])
                abbr_to_use = book_info['AbbrIT'].split(';')[0].strip().replace(" ", "")
                file_name = f"CEI 74 {abbr_to_use} {chapter_num:02d}.html"
                return book_folder_path / file_name

    # Gestione di tutti gli altri URL (ad es. risorse o altre pagine)
    local_path = cei_folder / path_without_prefix
    
    if url.endswith('/'):
        return local_path / "index.html"
    else:
        if not local_path.suffix:
            return local_path.with_suffix('.html')
        return local_path

async def file_hash(path: Path) -> Optional[str]:
    """Calcola l'hash SHA256 di un file per verificare se è già stato scaricato."""
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

async def save_file(url: str, content: Any) -> bool:
    """Salva il contenuto di una pagina su disco."""
    path = get_local_path(url)
    
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists() and not force:
        try:
            new_hash = hashlib.sha256(content if isinstance(content, bytes) else content.encode("utf-8")).hexdigest()
            existing_hash = await file_hash(path)
            if existing_hash == new_hash:
                print(f"🟡 Già presente identico: {url}")
                index_links.append((url, path.relative_to(base_folder).as_posix()))
                return False
        except IsADirectoryError:
            print(f"🟡 Conflitto nome file/cartella ignorato per: {url}")
            return False
            
    mode = "wb" if isinstance(content, bytes) else "w"
    async with aiofiles.open(path, mode, encoding=None if mode == "wb" else "utf-8") as f:
        await f.write(content)
    print(f"✅ Salvato: {url} -> {path.relative_to(base_folder)}")
    index_links.append((url, path.relative_to(base_folder).as_posix()) )
    return True
    
async def fetch(session: aiohttp.ClientSession, url: str) -> Optional[tuple[str, Any]]:
    """
    Scarica il contenuto di un URL e gestisce i reindirizzamenti e gli errori.
    """
    try:
        async with semaphore:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            async with session.get(url, headers=headers, allow_redirects=True) as response:
                if response.status != 200:
                    print(f"❌ Errore HTTP {response.status} per {url}")
                    return None

                content_type = response.headers.get('Content-Type', '')
                if 'text/html' in content_type:
                    return 'html', await response.text()
                else:
                    return 'other', await response.read()

    except Exception as e:
        print(f"💥 Errore durante il recupero di {url}: {e}")
        return None

def find_links_to_crawl(soup: BeautifulSoup, base_url: str) -> List[str]:
    """Estrae tutti i link rilevanti da una pagina HTML."""
    links = set()
    for tag in soup.find_all(['a', 'link', 'script', 'img']):
        href = tag.get('href') or tag.get('src')
        if href and 'void(0)' not in href and '#' not in href:
            full_url = normalize_link(base_url, href)
            if is_internal_link(full_url) and urlparse(full_url).path not in visited:
                links.add(full_url)
    
    return list(links)
    
async def crawl(session: aiohttp.ClientSession, url: str, current_depth: int):
    """
    Funzione di crawling ricorsiva.
    """
    normalized_path = urlparse(url).path
    if current_depth > depth or normalized_path in visited:
        return
    visited.add(normalized_path)

    result = await fetch(session, url)
    if result is None:
        return
        
    tipo, content = result

    await save_file(url, content)

    if tipo == "html":
        soup = BeautifulSoup(content, "html.parser")
        tasks = []
        
        all_links = find_links_to_crawl(soup, url)

        for link in all_links:
            normalized_link_path = urlparse(link).path
            if normalized_link_path not in visited:
                tasks.append(crawl(session, link, current_depth + 1))

        if tasks:
            await asyncio.gather(*tasks)

    print(f"⏳ Attendo {wait_seconds} secondi prima di continuare...")
    await asyncio.sleep(wait_seconds)

async def genera_indice_html():
    """Genera un file HTML con l'indice dei link scaricati."""
    async with aiofiles.open(index_file, "w", encoding="utf-8") as f:
        await f.write("<!DOCTYPE html><html><head><meta charset='utf-8'><title>Indice bibbiaedu</title></head><body>\n")
        await f.write(f"<h1>Contenuti scaricati da {startUrl}</h1>\n<ul>\n")
        for url, rel_path in sorted(index_links):
            await f.write(f"<li><a href='{rel_path}' target='_blank'>{url}</a></li>\n")
        await f.write("</ul>\n</body></html>")
    print(f"📄 Indice HTML creato: {index_file}")

async def main():
    """Funzione principale per l'esecuzione dello scraper."""
    print("🚀 Avvio dello scraping...")
    async with aiohttp.ClientSession() as session:
        await crawl(session, startUrl, 0)
    await genera_indice_html()
    print("🏍️ Fine scraping.")

if __name__ == "__main__":
    asyncio.run(main())
