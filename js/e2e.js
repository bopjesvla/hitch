const playwright = require('playwright');
const USER1 = 'Test' + Math.random().toString().slice(2);

(async () => {
    const browser = await playwright['chromium'].launch({
        // headless: false, slowMo: 100, // Uncomment to visualize test
    });
    const page = await browser.newPage();

    // Load "http://localhost:5000/"
    await page.goto('http://localhost:5000/');

    // Resize window to 1854 x 963
    await page.setViewportSize({ width: 1854, height: 963 });

    // Click on <a> "👤 Your account"
    await Promise.all([
        page.click('[href="/me"]'),
        page.waitForNavigation()
    ]);

    // Click on <a> "Register"
    await Promise.all([
        page.click('[href="/register"]'),
        page.waitForNavigation()
    ]);

    // Click on <input> #email > #email
    await page.click('#email > #email');

    // Fill "ab@cd.nl" on <input> #email > #email
    await page.fill('#email > #email', `${USER1}@cd.nl`);

    // Press Tab on input
    await page.press('#email > #email', 'Tab');

    // Fill "User1" on <input> #username > #username
    await page.fill('#username > #username', USER1);

    // Press Tab on input
    await page.press('#username > #username', 'Tab');

    // Fill "12345678" on <input> #password > #password
    await page.fill('#password > #password', '12345678');

    // Press Tab on input
    await page.press('#password > #password', 'Tab');

    // Fill "12345678" on <input> #password_confirm > #password_confirm
    await page.fill('#password_confirm > #password_confirm', '12345678');

    // Press Tab on input
    await page.press('#password_confirm > #password_confirm', 'Tab');

    // Press Enter on input
    await Promise.all([
        page.press('#submit > #submit', 'Enter'),
        page.waitForNavigation()
    ]);

    // Click on <a> "📍 Add spot"
    await page.click('.add-spot > a');

    // Click on <button> "Done"
    await page.click('.step1 > button:nth-child(3)');

    // Click on <button> "Skip"
    await page.click('.step2 > button:nth-child(3)');

    // Click on <label> "★"
    await page.click('[title="4 stars"]');

    // Click on <input> [name="wait"]
    await page.click('[name="wait"]');

    // Fill "20" on <input> [name="wait"]
    await page.fill('[name="wait"]', '20');

    // Press Tab on input
    await page.press('[name="wait"]', 'Tab');

    // Fill "abcde" on <textarea> [name="comment"]
    await page.fill('[name="comment"]', 'abcde');

    // Click on <summary> "more optional fields"
    await page.click('#details-summary');

    // Click on <select> #signal
    await page.click('#signal');

    // Fill "sign" on <select> #signal
    await page.selectOption('#signal', 'sign');

    // Click on <input> #datetime_ride
    await page.click('#datetime_ride');

    // Fill "1994-01-01T01:01" on <input> #datetime_ride
    await page.fill('#datetime_ride', '1994-01-01T01:01');

    // Click on <button> "Submit"
    await page.click('#spot-form > button');

    await browser.close();

    console.log('Test successful!')
})();
