const { Scraper } = require('agent-twitter-client');

/**
 * Get or create a scraper instance.
 * - If cookies exist and are valid, use them.
 * - Otherwise, log in and cache new cookies.
 */
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
  return scraper;
};

module.exports = getScraper;