// Per test sostituisco tutte le occorrenze di browser.storage.sync
// con browser.storage.local Ricordare poi di rifare procedura contraria

// Carica lista dal storage.sync
async function loadSites() {
  const data = await browser.storage.local.get('activeHosts');
  const sites = data.activeHosts || [];
  const listEl = document.getElementById('sitesList');
  listEl.innerHTML = '';
  console.log('Lista caricata da storage:', sites);
  sites.forEach((site, idx) => {
    const li = document.createElement('li');
    li.textContent = site;

    const btnRemove = document.createElement('button');
    btnRemove.textContent = '❌';
    btnRemove.className = 'remove-btn';
    btnRemove.title = 'Rimuovi sito';
    btnRemove.onclick = () => removeSite(idx);

    li.appendChild(btnRemove);
    listEl.appendChild(li);
  });
}

// Salva lista nel storage.sync
async function saveSites(sites) {
  await browser.storage.local.set({ activeHosts: sites });
}

// Aggiungi un sito nuovo
async function addSite() {
  const input = document.getElementById('newSite');
  const site = input.value.trim();
  if (!site) {
    alert('Inserisci un URL valido');
    return;
  }
  const data = await browser.storage.local.get('activeHosts');
  const sites = data.activeHosts || [];

  if (sites.includes(site)) {
    alert('Il sito è già nella lista');
    return;
  }

  sites.push(site);
  await browser.storage.local.set({ activeHosts: sites });
  input.value = '';
  await loadSites();
  console.log('Sito aggiunto e lista aggiornata:', sites);
}


// Rimuovi sito per indice
async function removeSite(idx) {
  const data = await browser.storage.local.get('activeHosts');
  const sites = data.activeHosts || [];
  sites.splice(idx, 1);
  await saveSites(sites);
  await loadSites();
}

// Event listeners
document.getElementById('addSiteBtn').addEventListener('click', addSite);

window.addEventListener('load', loadSites);
