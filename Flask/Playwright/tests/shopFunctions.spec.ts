import {test ,expect} from '@playwright/test';
import { PageManager } from '../page-objects/pageManager';

test.beforeEach("Go To page", async({page}) => {
    await page.goto('http://localhost:8000/');
    
});

test("All menu is visible and navigate to expected page", async({page}) => {
    const pm = new PageManager(page);
    
    await pm.navigateTo().news();
    await expect(page).toHaveTitle('News');
    await pm.navigateTo().products();
    await expect(page).toHaveTitle('Products');
    await pm.navigateTo().cart();
    await expect(page).toHaveTitle('Cart');
    await pm.navigateTo().login();
    await expect(page).toHaveTitle('Login Page');
    await pm.navigateTo().register();
    await expect(page).toHaveTitle('Register');

});

test("All products could add to cart", async({page}) => {
    const pm = new PageManager(page);
    await pm.navigateTo().products();
    const products = page.locator('.col .card');
    
    for(let product of await products.all()) {
        const productName = await product.locator('h5').textContent();
        if(productName) {
            await pm.onProductsPage().addToCart(productName);
            await expect(page.locator('.notification').last()).toContainText(`Added ${productName} to cart`);
        }
    }
    await expect(page.locator('#cart-count')).toHaveText(((await products.all()).length).toString());
});

test("Add product to cart", async({page})=> {
    const pm = new PageManager(page);
    await pm.navigateTo().products();

    // Give product name 
    const productName = 'Zero-G Coffee';
    //const productName = await page.locator('.card-title').last().textContent()
    //expect(productName).not.toBeNull();
    // Check cart badge is 0
    await expect(page.locator('#cart-count')).toHaveText('0');
    // Add product to cart. Use function return to validate is it existing product.
    const validProduct = await pm.onProductsPage().addToCart(productName);
        // If not existing product then test will fail, but console log will inform us.
    if(!validProduct)
        console.log("Not existing product, check product name!");
    // Check do we get notification with product name
    await expect(page.locator('.notification').last()).toContainText(`Added ${productName} to cart`);
    // Check cart badge number has changed
    await expect(page.locator('#cart-count')).toHaveText('1');

    //Visit cart page
    await pm.navigateTo().cart();
    //Check there is only 1 row
    const listItems = page.locator('.cart-item')
    expect((await listItems.all()).length).toEqual(1);
    //Check this row include product what we added earlier and there is only 1pc
    await expect(listItems.locator('td').nth(1)).toHaveText(productName);
    expect(await listItems.locator('.qty-input').inputValue()).toEqual('1');
});

test.describe("Check cart manipulate functions", () => {

    test.beforeEach("Add a product to cart", async({page}) => {
        const pm = new PageManager(page);
        await pm.navigateTo().products();
        await pm.onProductsPage().addToCartRandomProduct();
        await pm.navigateTo().cart();
    });
    
    test("Check plus and minus button functionality", async({page}) => {
        let cartItemAmount = parseInt(await page.locator('.cart-item').locator('.qty-input').inputValue());
        //Use plus to add 1pc and check product amount is equal with cart badge
        await page.locator('.cart-item').getByRole('button', {name: '+'}).click();
        //Check do we get notification about update cart 
        await expect(page.locator('.notification')).toHaveText('Cart updated');
        //Check item amount increased with 1 in product line
        await expect(page.locator('.qty-input')).toHaveValue(`${cartItemAmount+1}`);
        //Check item amount equal with cart badge
        await expect(page.locator('#cart-count')).toHaveText(`${cartItemAmount+1}`);
        cartItemAmount = cartItemAmount + 1

        //Use minus to decrease product amount with 1pc and check product amount is equal with cart badge
        await page.locator('.cart-item').getByRole('button', {name: '-'}).click();
        //Check do we get notification about update cart 
        await expect(page.locator('.notification').last()).toHaveText('Cart updated');
        //Check item amount decreased with 1 in product line
        await expect(page.locator('.qty-input')).toHaveValue(`${cartItemAmount-1}`);
        //Check item amount equal with cart badge
        await expect(page.locator('#cart-count')).toHaveText(`${cartItemAmount-1}`);

        //When there is only 1pc of an item in the cart and minus button is clicked, item is removed from cart
        await page.locator('.cart-item').getByRole('button', {name: '-'}).click();
        await expect(page.locator('.notification').last()).toHaveText('Product removed from cart');
        await expect(page.locator('#cart-count')).toHaveText('0');
    });
    
    test("Check inputfield functionality", async({page}) => {
        //Use inputfield to change product item amount
        await page.locator('.qty-input').clear();
        await page.locator('.qty-input').pressSequentially('200', {delay:300});
        //check item amount increased to 200 and we get notification
        await expect(page.locator('.notification').last()).toHaveText('Cart updated');
        await expect(page.locator('.qty-input')).toHaveValue('200');
        await expect(page.locator('#cart-count')).toHaveText('200');

        //Add 0 to inputfield
        await page.locator('.qty-input').clear();
        await page.locator('.qty-input').fill('0');
        await expect(page.locator('.notification').last()).toHaveText('Cart updated');
        await expect(page.locator('#cart-count')).toHaveText('0');
    });
    
    test("Add negative number to inputfield is not possible", async({page}) =>{
        await page.locator('.qty-input').clear();
        await page.locator('.qty-input').fill('-10');
        await expect(page.locator('.notification').last()).toHaveText('Cart updated');
        await expect(page.locator('.qty-input')).toHaveValue('10');
        await expect(page.locator('#cart-count')).toHaveText('10');
    });

    test("Add characters to inputfield is not possible", async({page}) =>{
        await page.locator('.qty-input').clear();
        await page.locator('.qty-input').fill('aS_?');
        await expect(page.locator('.qty-input')).toBeEmpty();
        await expect(page.locator('#cart-count')).toHaveText('1');
    });

    test("Check total calculation", async({page}) => {
        const pm = new PageManager(page);
        await pm.navigateTo().cart();
        let item1Name = await page.locator('.cart-item').locator('td').nth(1).textContent() ?? 'Unnamed'; 
        await pm.navigateTo().products();
        let item2Name = await pm.onProductsPage().getRandomProductName();
        while(item1Name === item2Name)
            item2Name = await pm.onProductsPage().getRandomProductName();
        
        await pm.onProductsPage().addToCart(item2Name);
        await pm.navigateTo().cart();

        item1Name = await page.locator('.cart-item').nth(0).locator('td').nth(1).textContent() ?? 'Unnamed';
        const item1PriceWithCurrency = await page.locator('.cart-item').nth(0).locator('td').nth(3).innerText();
        const item1Price = parseFloat(item1PriceWithCurrency.split(" ")[0]);
        
        item2Name = await page.locator('.cart-item').nth(1).locator('td').nth(1).textContent() ?? 'Unnamed';
        const item2PriceWithCurrency = await page.locator('.cart-item').nth(1).locator('td').nth(3).innerText();
        const item2Price = parseFloat(item2PriceWithCurrency.split(" ")[0]);
        
        let endTotalWithCurrency = await page.locator('#end-total').innerText();
        let endTotal = parseFloat(endTotalWithCurrency.split(" ")[0]);
        expect(endTotal.toFixed(2)).toEqual((item1Price + item2Price).toFixed(2));
        
        // change amount of item 1, check line total and end total
        const addAmountItem1 = 25;
        await page.locator('.cart-item', {hasText:item1Name}).locator('.qty-input').clear();
        await page.locator('.cart-item', {hasText:item1Name}).locator('.qty-input').fill(addAmountItem1.toString());
        
        await expect(page.locator('.notification')).toHaveText('Cart updated');
        const line1TotalWithCurrency = await page.locator('.cart-item').nth(0).locator('td').nth(3).innerText();
        const line1Total = parseFloat(line1TotalWithCurrency.split(" ")[0]);
        // check line total is correct
        expect(line1Total.toFixed(2)).toEqual((item1Price*addAmountItem1).toFixed(2));
        // check end total is correct
        endTotalWithCurrency = await page.locator('#end-total').innerText();
        endTotal = parseFloat(endTotalWithCurrency.split(" ")[0]);
        expect(endTotal.toFixed(2)).toEqual((line1Total+item2Price).toFixed(2));

        //change amount of item 2, check line total and end total
        const addAmountItem2 = 13;
        await page.locator('.cart-item', {hasText:item2Name}).locator('.qty-input').clear();
        await page.locator('.cart-item', {hasText:item2Name}).locator('.qty-input').fill(addAmountItem2.toString());
    
        await expect(page.locator('#cart-count')).toContainText((addAmountItem1+addAmountItem2).toString());
        const line2TotalWithCurrency = await page.locator('.cart-item').nth(1).locator('td').nth(3).innerText();
        const line2Total = parseFloat(line2TotalWithCurrency.split(" ")[0]);
        // check line total is correct
        expect(line2Total.toFixed(2)).toEqual((item2Price*addAmountItem2).toFixed(2));
        // check end total is correct
        endTotalWithCurrency = await page.locator('#end-total').innerText();
        endTotal = parseFloat(endTotalWithCurrency.split(" ")[0]);
        expect(endTotal.toFixed(2)).toEqual((line1Total+line2Total).toFixed(2));
        
        // take out item 1 and check it will not break calculation
        if(item1Name) {
            await page.locator('.cart-item', {hasText:item1Name}).locator('.qty-input').clear();
            await page.locator('.cart-item', {hasText:item1Name}).locator('.qty-input').fill('0');
        }
        await expect(page.locator('#cart-count')).toContainText((addAmountItem2).toString());
        // check end total is correct
        endTotalWithCurrency = await page.locator('#end-total').innerText();
        endTotal = parseFloat(endTotalWithCurrency.split(" ")[0]);
        expect(endTotal).toEqual(line2Total);
    });
});

test.describe("check registration", () => {
    test.beforeEach("navigate to register", async({page}) => {
        const pm = new PageManager(page);
        pm.navigateTo().register();
    });

    test("all input is mandatory, invalid email form not accepted", async({page}) => {
        //missing email
        await page.locator('[name="nm"]').fill('test');
        await page.locator('[name="pwd"]').fill('password123');
        await page.getByRole('button', {name:'submit'}).click();
        await expect(page.getByRole('alert')).toHaveText('All fields are required');
        await page.locator('[aria-label="Close"]').click();
        //missing password
        await page.locator('[name="pwd"]').clear();
        await page.locator('[name="email"]').fill('tester@example.com');
        await page.getByRole('button', {name:'submit'}).click();
        await expect(page.getByRole('alert')).toHaveText('All fields are required');
        await page.locator('[aria-label="Close"]').click();
        //missing name
        await page.locator('[name="nm"]').clear();
        await page.locator('[name="pwd"]').fill('password123');
        await page.locator('[name="email"]').fill('tester@example.com');
        await page.getByRole('button', {name:'submit'}).click();
        await expect(page.getByRole('alert')).toHaveText('All fields are required');
        await page.locator('[aria-label="Close"]').click();
        //not valid email
        await page.locator('[name="nm"]').fill('test');
        await page.locator('[name="pwd"]').fill('password123');
        await page.locator('[name="email"]').fill('testerexample.com');
        await page.getByRole('button', {name:'submit'}).click();
        const activeElement = await page.locator('[name="email"]').evaluate(email => document.activeElement === email);
        expect(activeElement).toBe(true);
    });

    test("registration successful", async({page}) => {
        await page.locator('[name="nm"]').fill('test');
        await page.locator('[name="pwd"]').fill('password123');
        await page.locator('[name="email"]').fill('tester@example.com');
        await page.getByRole('button', {name:'submit'}).click();
        await expect(page.getByRole('alert')).toHaveText('Registered successfully! Please login.');

        //confirm with login registration was successful
        await page.locator('[name="pwd"]').fill('password123');
        await page.locator('[name="email"]').fill('tester@example.com');
        await page.getByRole('button', {name:'submit'}).click();
        await expect(page.getByRole('alert')).toContainText('logged in successful!');
        
        //cleanup
        await page.getByRole('button', {name:'Delete account'}).click();
        await page.locator('#del').fill('DELETE');
        await page.getByRole('button', {name:'Delete account'}).click();

    });
});
