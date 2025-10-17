import {test ,expect} from '@playwright/test';
import { PageManager } from '../page-objects/pageManager';

test.beforeEach("Add an item to the cart and go to cart page", async({page}) => {
    await page.goto('http://localhost:8000/products');
    const pm = new PageManager(page);
    await pm.onProductsPage().addToCartRandomProduct();    
    await pm.navigateTo().cart();
});

test("TC004 - Increase item quantity in cart", async({page}) => {
    //store data before action
    const cartItemAmount = Number(await page.locator('.cart-item').locator('.qty-input').inputValue());
    const cartCounter = Number(await page.locator('#cart-count').innerText());
    expect(cartCounter).toEqual(cartItemAmount);
    const itemPriceWithCurrency = await page.locator('.total-line').innerText();
    const itemPrice = Number(itemPriceWithCurrency.split(" ")[0]);
    let totalWithCurrency = await page.locator('#end-total').innerText();
    let total = Number(totalWithCurrency.split(" ")[0]);
    expect(itemPrice).toEqual(total);
    
    //lets click it
    await page.locator('.cart-item').getByRole('button', {name: '+'}).click();
    //Check do we get notification about update cart 
    await expect(page.locator('.notification')).toHaveText('Cart updated');
    //Check item amount increased with 1 in product line
    await expect(page.locator('.cart-item').locator('.qty-input')).toHaveValue(`${cartItemAmount+1}`);
    //Check item amount increased with 1 at cart badge
    await expect(page.locator('#cart-count')).toHaveText(`${cartCounter+1}`);
    //Check total price changed correctly
    totalWithCurrency = await page.locator('#end-total').innerText();
    total = Number(totalWithCurrency.split(" ")[0]);
    expect(total).toEqual(2*itemPrice);
});

test("TC005 - Decrease item quantity in cart", async({page}) => {
    //store item price at the beginning
    const itemPriceWithCurrency = await page.locator('.total-line').innerText();
    const itemPrice = Number(itemPriceWithCurrency.split(" ")[0]);
    //add 1 more product
    await page.locator('.cart-item').getByRole('button', {name: '+'}).click();
    await expect(page.locator('.notification').last()).toHaveText('Cart updated');
    //store data before test action
    const totalWithCurrency = await page.locator('#end-total').innerText();
    const total = Number(totalWithCurrency.split(" ")[0]);
    const cartItemAmount = Number(await page.locator('.cart-item').locator('.qty-input').inputValue());
    const cartCounter = Number(await page.locator('#cart-count').innerText());
    expect(cartCounter).toEqual(cartItemAmount);
    
    //lets click it
    await page.locator('.cart-item').getByRole('button', {name: '-'}).click();
    //Check do we get notification about update cart 
    await expect(page.locator('.notification').last()).toHaveText('Cart updated');
    //Check item amount increased with 1 in product line
    await expect(page.locator('.cart-item').locator('.qty-input')).toHaveValue(`${cartItemAmount-1}`);
    //Check item amount increased with 1 at cart badge
    await expect(page.locator('#cart-count')).toHaveText(`${cartCounter-1}`);
    //Check total price changed correctly
    const newTotalWithCurrency = await page.locator('#end-total').innerText();
    const newTotal = Number(newTotalWithCurrency.split(" ")[0]);
    expect(newTotal).toEqual(total-itemPrice);
});

test("TC006 - Remove product from cart when only 1 item is left", async({page}) => {
    //lets click it
    await page.locator('.cart-item').getByRole('button', {name: '-'}).click();
    //Check do we get notification about update cart 
    await expect(page.locator('.notification').last()).toHaveText('Product removed from cart');
    //Check item amount is 0 at cart badge
    await expect(page.locator('#cart-count')).toHaveText('0');
    //Check total is 0
    await expect(page.locator('#end-total')).toHaveText('0.00 €');
});

test.describe("TC007 - Change item amount in cart", () => {
    
    test("TC007A - Update product quantity with a valid number", async({page}) => {
        //Store item price
        const itemPriceWithCurrency = await page.locator('.total-line').innerText();
        const itemPrice = Number(itemPriceWithCurrency.split(" ")[0]);
        //Use inputfield to change product item amount
        const itemAmount = 200;
        await page.locator('.qty-input').clear();
        await page.locator('.qty-input').pressSequentially(`${itemAmount}`, {delay:300});
        //check item amount increased to itemAmount and we get notification, total cost has changed correctly
        await expect(page.locator('.notification').last()).toHaveText('Cart updated');
        await expect(page.locator('.qty-input')).toHaveValue(`${itemAmount}`);
        await expect(page.locator('#cart-count')).toHaveText(`${itemAmount}`);
        const totalWithCurrency = await page.locator('#end-total').innerText();
        const total = Number(totalWithCurrency.split(" ")[0]);
        expect(total).toEqual(itemPrice*itemAmount);
    });

    test("TC007B - Remove product by setting quantity to 0", async({page}) => {
        // Add 0 to input field
        await page.locator('.qty-input').clear();
        await page.locator('.qty-input').fill('0');
        await expect(page.locator('.notification').last()).toHaveText('Cart updated');
        await expect(page.locator('#cart-count')).toHaveText('0');
        await expect(page.locator('#end-total')).toHaveText('0.00 €');
    });
    
    test("TC007C - Enter negative quantity — system corrects to positive", async({page}) =>{
        //Store item price
        const itemPriceWithCurrency = await page.locator('.total-line').innerText();
        const itemPrice = Number(itemPriceWithCurrency.split(" ")[0]);
        await page.locator('.qty-input').clear();
        await page.locator('.qty-input').fill('-3');
        await expect(page.locator('.notification').last()).toHaveText('Cart updated');
        await expect(page.locator('.qty-input')).toHaveValue('3');
        await expect(page.locator('#cart-count')).toHaveText('3');
        const totalWithCurrency = await page.locator('#end-total').innerText();
        const total = Number(totalWithCurrency.split(" ")[0]);
        expect(total).toEqual(itemPrice*3);
    });

    test("TC007D - Reject non-numeric input in quantity field", async({page}) =>{
        await page.locator('.qty-input').clear();
        await page.locator('.qty-input').fill('aS_?');
        await expect(page.locator('.qty-input')).toBeEmpty();
        await expect(page.locator('#cart-count')).toHaveText('1');
    });
});