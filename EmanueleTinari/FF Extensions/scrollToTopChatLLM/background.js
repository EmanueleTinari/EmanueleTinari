browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message === 'openOptions') {
    browser.runtime.openOptionsPage();
  }
});
