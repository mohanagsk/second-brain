// Run this in Chrome DevTools Console while on Instagram
// 1. Go to instagram.com and make sure you're logged in
// 2. Open DevTools (F12) → Console tab
// 3. Paste and run this code
// 4. Send me the output

(function() {
    const cookies = document.cookie.split(';').map(c => {
        const [name, ...rest] = c.trim().split('=');
        return { name, value: rest.join('='), domain: '.instagram.com' };
    });
    
    const essential = ['sessionid', 'csrftoken', 'ds_user_id', 'mid', 'ig_did'];
    const filtered = cookies.filter(c => essential.includes(c.name));
    
    console.log('=== INSTAGRAM COOKIES ===');
    console.log(JSON.stringify(filtered, null, 2));
    console.log('=========================');
    console.log('Copy the JSON above and send to Mohana');
    
    return filtered;
})();
