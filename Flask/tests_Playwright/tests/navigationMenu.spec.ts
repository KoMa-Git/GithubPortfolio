import {test ,expect} from '@playwright/test';
import { PageManager } from '../page-objects/pageManager';

test.beforeEach("Go To page", async({page}) => {
    await page.goto('http://localhost:8000/');
    
});

test("TC001 - Anonymous user sees correct navigation items and can navigate", async({page}) => {
    const pm = new PageManager(page);
    
    await expect(page.locator('.navbar')).toContainText('News');
    await expect(page.locator('.navbar')).toContainText('Products');
    await expect(page.locator('.navbar').locator('.bi-bag')).toBeAttached();
    await expect(page.locator('.navbar')).toContainText('Login');

    await expect(page.locator('.navbar')).not.toContainText('Logout');
    await expect(page.locator('.navbar').locator('.bi-person-circle')).not.toBeAttached();

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

test("TC002 - Logged-in user sees correct navigation items and can navigate", async({page}) => {
    const pm = new PageManager(page);

    await pm.navigateTo().login();
    await pm.onLoginPage().login('john.doe@valid.com', 'johhnie123');
    
    await expect(page.locator('.navbar')).toContainText('News');
    await expect(page.locator('.navbar')).toContainText('Products');
    await expect(page.locator('.navbar').locator('.bi-bag')).toBeAttached();
    await expect(page.locator('.navbar').locator('.bi-person-circle')).toBeAttached();
    await expect(page.locator('.navbar')).toContainText('Logout');

    await expect(page.locator('.navbar')).not.toContainText('Login');
    
    await pm.navigateTo().news();
    await expect(page).toHaveTitle('News');
    await pm.navigateTo().products();
    await expect(page).toHaveTitle('Products');
    await pm.navigateTo().cart();
    await expect(page).toHaveTitle('Cart');
    await pm.navigateTo().user();
    await expect(page).toHaveTitle('User');
    await pm.navigateTo().logout();
    await expect(page).toHaveTitle('Login Page');
    
});