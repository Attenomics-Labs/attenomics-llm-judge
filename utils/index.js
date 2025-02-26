// index.js
require('dotenv').config(); // Load environment variables
const getScraper = require('./scraper');
const { handleResponse, handleError } = require('./ResponseHandler.js');
const { formatDate } = require('./someUtil');

(async () => {
  try {
    // Get or create the scraper instance and perform scraping
    const scraper = await getScraper();
    console.log("Scraper is ready!");

    // Example usage of someUtil: format the current date
    const formattedDate = formatDate(new Date());
    console.log("Formatted date:", formattedDate);

    // Simulate a successful response handling (this is just for demonstration)
    const fakeData = { message: "Scraping complete", date: formattedDate };
    handleResponse({ status: (code) => ({ json: console.log }) }, fakeData, "Success");

  } catch (error) {
    handleError({ status: (code) => ({ json: console.error }) }, error);
  }
})();
