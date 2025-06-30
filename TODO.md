# TODO: House Scraper Modernization & Improvements

## Backend (Scrapy + FastAPI)
- [x] Switch backend scraping from FastAPI/Playwright to Scrapy-based script
- [x] Add robust logging and debug output to the scraper
- [x] Serve scraped data via FastAPI endpoint (`/api/listings`)
- [x] Automate running both scraper and API server with a shell script
- [ ] Add error handling for failed requests or changes in Funda's HTML structure
- [ ] Add query parameters to `/api/listings` endpoint (e.g., city, price range)
- [ ] Implement caching or smarter update logic (currently, scraper runs on schedule)
- [ ] Add pagination support for Funda results in API
- [ ] Write unit tests for the scraping and API logic
- [ ] Add environment variable support for configuration (e.g., default city)
- [ ] Respect Funda's robots.txt and add request throttling

## Frontend (React)
- [x] Connect frontend to new `/api/listings` endpoint
- [ ] Add loading and error states when fetching listings
- [ ] Add a search/filter UI for city, price, etc.
- [ ] Improve UI/UX with a modern design (e.g., Material UI or Tailwind CSS)
- [ ] Add pagination or infinite scroll for listings
- [ ] Add notifications for new listings (optional, future)
- [ ] Add user authentication (optional, future)

## DevOps & Deployment
- [ ] Dockerize backend and frontend for easy deployment
- [ ] Set up CI/CD (e.g., GitHub Actions)
- [ ] Deploy backend (e.g., on Render, Heroku, or your own server)
- [ ] Deploy frontend (e.g., Vercel, Netlify, or GitHub Pages)

---

Let me know which item you want to tackle first, or I can suggest a recommended order!
