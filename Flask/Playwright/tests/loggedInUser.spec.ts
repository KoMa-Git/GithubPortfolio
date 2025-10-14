import {test ,expect} from '@playwright/test';
import { PageManager } from '../page-objects/pageManager';

test.beforeEach("Go To page", async({page}) => {
    await page.goto('http://localhost:8000/');
    
});

test("Menu items for logged in users are visible and navigate to expected page", async({page}) => {
    const pm = new PageManager(page);
    
    await page.locator('.bi.bi-person-circle').click();
    await page.waitForTimeout(250);
    await expect(page).toHaveTitle('User');
    // Not visible elements
    await expect(page.getByRole('button', {name:'Login'})).not.toBeAttached();

    await page.getByRole('button', {name:'Logout'}).click();
    await page.waitForTimeout(250);
    await expect(page).toHaveTitle('Login Page');
    
});
