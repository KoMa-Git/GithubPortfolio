import {test ,expect} from '@playwright/test';
import { PageManager } from '../page-objects/pageManager';

test.beforeEach("Go to registration page", async({page}) => {
    await page.goto('http://localhost:8000/login');
});

test("TC015 - Email field is required", async({page}) => {
    await page.locator('[name="pwd"]').fill('securePass123');
    await page.getByRole('button', {name:'submit'}).click();
    await expect(page.getByRole('alert')).toHaveText('Incorrect email or password!');
});

test("TC016 - Password field is required", async({page}) => {
    await page.locator('[name="email"]').fill('jane@example.com');
    await page.getByRole('button', {name:'submit'}).click();
    await expect(page.getByRole('alert')).toHaveText('Incorrect email or password!');
});

test("TC017 - User tries to login with invalid email", async({page}) => {
    await page.locator('[name="email"]').fill('jane@example.com');
    await page.locator('[name="pwd"]').fill('securePass123');
    await page.getByRole('button', {name:'submit'}).click();
    await expect(page.getByRole('alert')).toHaveText('Incorrect email or password!');
});

test("TC018 - User tries to login with invalid password", async({page}) => {
    await page.locator('[name="email"]').fill('john.doe@valid.com');
    await page.locator('[name="pwd"]').fill('securePass123');
    await page.getByRole('button', {name:'submit'}).click();
    await expect(page.getByRole('alert')).toHaveText('Incorrect email or password!');
});

test("TC019 - Successful login", async({page}) => {
    await page.locator('[name="email"]').fill('john.doe@valid.com');
    await page.locator('[name="pwd"]').fill('johhnie123');
    await page.getByRole('button', {name:'submit'}).click();
    await expect(page.getByRole('alert')).toHaveText('John Doe logged in successful!');
    await expect(page).toHaveTitle('User');
});