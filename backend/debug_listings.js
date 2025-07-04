// Debug utility to print all keys of the first listing
function debugListingKeys(listings) {
    if (!Array.isArray(listings) || listings.length === 0) {
        console.log('No listings to debug.');
        return;
    }
    const l = listings[0];
    console.log('First listing keys:', Object.keys(l));
    console.log('First listing:', l);
}

window.debugListingKeys = debugListingKeys;
