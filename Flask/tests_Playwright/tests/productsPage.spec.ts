import {test ,expect} from '@playwright/test';
import { PageManager } from '../page-objects/pageManager';

test.beforeEach("Go to homepage", async({page}) => {
    await page.goto('http://localhost:8000/');
    
});

test("TC003 - Add item to cart", async({page})=> {
    const pm = new PageManager(page);
    await pm.navigateTo().products();

    // Check cart count
    const cartCounter = Number(await page.locator('#cart-count').innerText());
    
    // Add item to cart
    const productName = await pm.onProductsPage().addToCartRandomProduct();

    // Check do we get notification with product name
    await expect(page.locator('.notification').last()).toContainText(`Added ${productName} to cart`);
    // Check cart badge number has changed
    await expect(page.locator('#cart-count')).toHaveText(`${cartCounter + 1}`);

    //Visit cart page
    await pm.navigateTo().cart();
    //Check products is in the cart
    await expect(page.locator('tbody')).toContainText(productName);
});

test("TC004 - Add all visible products to the cart", async({page}) => {
    const pm = new PageManager(page);
    await pm.navigateTo().products();
    const products = await page.locator('.col .card').all();
    
    const allProductNames = [];
    let cartCounter = Number(await page.locator('#cart-count').innerText());
    
    for(let product of products) {
        const productName = await product.locator('h5').textContent();
        if(productName) {
            await pm.onProductsPage().addToCart(productName);
            await expect(page.locator('.notification').last()).toContainText(`Added ${productName} to cart`);
            await expect(page.locator('#cart-count')).toHaveText((cartCounter + 1).toString());
            cartCounter = Number(await page.locator('#cart-count').innerText());
            allProductNames.push(productName);
        }
    };
    await expect(page.locator('#cart-count')).toHaveText(`${products.length}`);
    
    //Visit cart page
    await pm.navigateTo().cart();
    //Check products are in the cart
    for (const item of allProductNames) {
        await expect(page.locator('tbody')).toContainText(item);
    }
    

});