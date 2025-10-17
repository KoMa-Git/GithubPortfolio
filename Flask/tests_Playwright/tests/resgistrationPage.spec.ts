import {test ,expect} from '@playwright/test';
import { PageManager } from '../page-objects/pageManager';

test.beforeEach("Go to registration page", async({page}) => {
    await page.goto('http://localhost:8000/register');
});

test("TC010 - Name field is required", async({page}) => {
    await page.locator('[name="nm"]').clear();
    await page.locator('[name="pwd"]').fill('securePass123');
    await page.locator('[name="email"]').fill('jane@example.com');
    await page.getByRole('button', {name:'submit'}).click();
    await expect(page.getByRole('alert')).toHaveText('All fields are required');
});

test("TC011 - Email field is required", async({page}) => {
    await page.locator('[name="nm"]').fill('Jane');
    await page.locator('[name="pwd"]').fill('securePass123');
    await page.getByRole('button', {name:'submit'}).click();
    await expect(page.getByRole('alert')).toHaveText('All fields are required');
});

test("TC012 - Password field is required", async({page}) => {
    await page.locator('[name="nm"]').fill('Jane');
    await page.locator('[name="email"]').fill('jane@example.com');
    await page.getByRole('button', {name:'submit'}).click();
    await expect(page.getByRole('alert')).toHaveText('All fields are required');
});

test("TC013 - Invalid email format", async({page}) => {
    await page.locator('[name="nm"]').fill('John Doe');
    await page.locator('[name="email"]').fill('invalid-email');
    await page.locator('[name="pwd"]').fill('secret123');
    await page.getByRole('button', {name:'submit'}).click();
    const activeElement = await page.locator('[name="email"]').evaluate(email => document.activeElement === email);
    expect(activeElement).toBe(true);
});

test("TC014 - Successful registration", async({page}) => {
    await page.locator('[name="nm"]').fill('Jane');
    await page.locator('[name="pwd"]').fill('securePass123');
    await page.locator('[name="email"]').fill('jane@example.com');
    await page.getByRole('button', {name:'submit'}).click();
    await expect(page.getByRole('alert')).toHaveText('Registered successfully! Please login.');
    await expect(page).toHaveTitle('Login Page');

    //confirm with login registration was successful
    await page.locator('[name="pwd"]').fill('securePass123');
    await page.locator('[name="email"]').fill('jane@example.com');
    await page.getByRole('button', {name:'submit'}).click();
    await expect(page.getByRole('alert')).toContainText('logged in successful!');
    
    //cleanup
    await page.getByRole('button', {name:'Delete account'}).click();
    await page.locator('#del').fill('DELETE');
    await page.getByRole('button', {name:'Delete account'}).click();

});