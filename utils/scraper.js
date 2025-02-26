// src/scraper.js
const { Scraper } = require('agent-twitter-client');
const fs = require('fs');
const path = require('path');

async function getScraper() {
  const scraper = new Scraper();

  // Check if the scraper is logged in
  const isLoggedIn = await scraper.isLoggedIn();
  if (!isLoggedIn) {
    console.log('Not logged in. Logging in with credentials...');
    await scraper.login(
      process.env.TWITTER_USERNAME || '',
      process.env.TWITTER_PASSWORD || '',
      process.env.TWITTER_EMAIL || '',
      process.env.TWITTER_API_KEY || '',
      process.env.TWITTER_API_SECRET_KEY || '',
      process.env.TWITTER_ACCESS_TOKEN || '',
      process.env.TWITTER_ACCESS_TOKEN_SECRET || ''
    );
  } else {
    console.log('Scraper is already logged in.');
  }

  // Here we assume the Scraper instance has a method called `scrape` that returns data.
  // If your API is different, adjust accordingly.
  try {
    console.log('Starting scraping...');
    const data = await scraper.scrape(); // Hypothetical method
    console.log('Scraping complete. Preparing to store data as JSON...');

    // Convert data to JSON
    const jsonData = JSON.stringify(data, null, 2);

    // Define output directory and file path
    const outputDir = path.join(__dirname, '../output');
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    const outputFile = path.join(outputDir, 'scrapedData.json');

    // Write JSON data to file
    fs.writeFileSync(outputFile, jsonData, 'utf8');
    console.log(`Scraped data saved to ${outputFile}`);
  } catch (err) {
    console.error('Error during scraping and saving data:', err);
  }
  
  return scraper;
};

module.exports = getScraper;
