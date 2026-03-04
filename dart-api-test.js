const https = require('https');
const http = require('http');
const key = 'dsa_47147322712870568412e8b34a23e2f49c0744ec22e041d92d2515e2c39d7288';

const testEndpoint = (opts, name) => {
  return new Promise((resolve) => {
    const req = https.request(opts, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        console.log(`${name}: Status ${res.statusCode} Body: ${data}`);
        resolve();
      });
    });
    req.on('error', (e) => console.error(`${name} Error:`, e.message));
    req.end();
  });
};

async function testAll() {
  const base = { hostname: 'app.dartai.com', path: '/api/v0/config', method: 'GET', headers: { 'User-Agent': 'DartTest/1.0' } };

  // Variant 1: Bearer
  await testEndpoint({ ...base, headers: { ...base.headers, Authorization: `Bearer ${key}` } }, 'Bearer');

  // Variant 2: Token
  await testEndpoint({ ...base, headers: { ...base.headers, Authorization: `Token ${key}` } }, 'Token');

  // Variant 3: DSA
  await testEndpoint({ ...base, headers: { ...base.headers, Authorization: `DSA ${key}` } }, 'DSA');

  // Variant 4: No prefix
  await testEndpoint({ ...base, headers: { ...base.headers, Authorization: key } }, 'NoPrefix');

  // Variant 5: X-API-Key
  await testEndpoint({ ...base, headers: { ...base.headers, 'X-API-Key': key } }, 'X-API-Key');

  // Variant 6: No auth
  await testEndpoint(base, 'NoAuth');

  // Public schema (known good)
  await testEndpoint({ hostname: 'app.dartai.com', path: '/api/v0/public/schema/', method: 'GET' }, 'PublicSchema');
}

testAll();