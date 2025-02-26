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

  let data;
  try {
    // Use target username from .env (or default to "elonmusk")
    const targetUser = 'Anjanay_Raina';
    console.log(`Fetching tweets for user: ${targetUser}`);
    // Fetch the latest 10 tweets from the target user
    data = await scraper.getTweets('Anjanay_Raina', 10);
    console.log(data);
    console.log('Tweet fetching complete. Preparing to store data as JSON...');
  } catch (err) {
    console.error('Error during tweet fetching:', err);
    data = {
      message: 'Tweet fetching failed; using dummy data.',
      tweets: []
    };
  }

  try {
    // Convert the fetched tweet data to a formatted JSON string
    const jsonData = JSON.stringify(data, null, 2);
    // Define the output directory (../output relative to this file)
    const outputDir = path.join(__dirname, '../output');
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    const outputFile = path.join(outputDir, 'tweets.json');
    // Write the JSON string to the file
    fs.writeFileSync(outputFile, jsonData, 'utf8');
    console.log(`Tweet data saved to ${outputFile}`);
  } catch (err) {
    console.error('Error during storing tweet data as JSON:', err);
  }
  
  return scraper;
}

module.exports = getScraper;
