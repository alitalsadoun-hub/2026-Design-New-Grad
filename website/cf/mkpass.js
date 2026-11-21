// usage: PW='...' node mkpass.js  -> prints ADMIN_SALT / ADMIN_HASH / SESSION_SECRET lines (PBKDF2-SHA256, 100k iterations)
const c=require('crypto');const salt=c.randomBytes(16),b=x=>x.toString('base64url');
const hash=c.pbkdf2Sync(process.env.PW,salt,100000,32,'sha256');
console.log(`ADMIN_SALT=${b(salt)}\nADMIN_HASH=${b(hash)}\nSESSION_SECRET=${b(c.randomBytes(32))}`);
