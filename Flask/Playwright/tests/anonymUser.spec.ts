import {test ,expect} from '@playwright/test';
import { PageManager } from '../page-objects/pageManager';

test.beforeEach("Go To page", async({page}) => {
    await page.goto('http://localhost:8000/');
    
});

test("Menu items for logged in users is not visible", async({page}) => {
    const pm = new PageManager(page);
    
    // Not visible elements
    await expect(page.locator('.bi.bi-person-circle')).not.toBeAttached();
    await expect(page.getByRole('button', {name:'Logout'})).not.toBeAttached();
    
});

test("Check out anonymously", async({page}) => {
    const pm = new PageManager(page);
    await pm.navigateTo().products();
    
    //put random products in the cart
    const item1 = await pm.onProductsPage().getRandomProductName();
    let item2 = await pm.onProductsPage().getRandomProductName();
    //be sure they are not the same
    while(item1 === item2)
        item2 = await pm.onProductsPage().getRandomProductName();
    await pm.onProductsPage().addToCart(item1);
    await expect(page.locator('.notification')).toHaveText(`Added ${item1} to cart`);
    await pm.onProductsPage().addToCart(item2);
    await expect(page.locator('.notification').last()).toHaveText(`Added ${item2} to cart`);
    //go to cart and check out
    await pm.navigateTo().cart();
    await page.getByRole('button', {name:'Checkout'}).click();
    //get a thank you message
    await page.waitForURL('http://localhost:8000/checkout')
    await expect(page.locator('h2')).toHaveText('Dear Client,');
    await expect(page.locator('h3')).toHaveText('Thank you for your order!');

    //visit view page and check order saved in the database
    await page.goto('http://localhost:8000/view');
    await expect(page.locator('.collapse').last()).toContainText(item1);
    await expect(page.locator('.collapse').last()).toContainText(item2);

});
