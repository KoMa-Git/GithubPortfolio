import {test ,expect} from '@playwright/test';
import { PageManager } from '../page-objects/pageManager';

const email = 'john.doe@valid.com';
const oldPassword = 'johhnie123';
const newPassword = 'john12';


test.beforeEach("Go to registration page", async({page}) => {
    await page.goto('http://localhost:8000/login');
    const pm = new PageManager(page);
    await pm.onLoginPage().login(email, oldPassword);
    await expect(page.getByRole('alert')).toContainText('logged in successful!');
});

test("TC020 - Change username", async({page}) => {
    const newName = 'John';
    await page.locator('.bi-pencil').click();
    await page.locator('[name="nm"]').clear();
    await page.locator('[name="nm"]').fill(newName);
    await page.locator('[name="nm"]').press('Enter');
    await expect(page.getByRole('alert')).toHaveText('New name was saved');
    await expect(page.locator('#stg')).toHaveText(newName);
});

test.describe("TC021 - Change password", () => {
    test("TC021A - Successfully change password", async({page}) => {
        await page.getByRole('button', {name:'Change password'}).click();
        await page.locator('[name="old_pass"]').fill(oldPassword);
        await page.locator('[name="new_pass"]').fill(newPassword);
        await page.getByRole('button', {name:'Change password'}).click();
        await expect(page.getByRole('alert')).toHaveText('Password has changed');

        const pm = new PageManager(page);
        await pm.navigateTo().logout();
        await pm.navigateTo().login();
        await pm.onLoginPage().login(email, newPassword);
        await expect(page.getByRole('alert')).toContainText('logged in successful!');

        //cleanup, change back to old password
        await page.getByRole('button', {name:'Change password'}).click();
        await page.locator('[name="old_pass"]').fill(newPassword);
        await page.locator('[name="new_pass"]').fill(oldPassword);
        await page.getByRole('button', {name:'Change password'}).click();
    });

    test("TC021B - Missing new password", async({page}) => {
        await page.getByRole('button', {name:'Change password'}).click();
        await page.locator('[name="old_pass"]').fill(oldPassword);
        await page.getByRole('button', {name:'Change password'}).click();
        await expect(page.getByRole('alert')).toHaveText('Password fields cannot be empty!');
    });

    test("TC021C - Missing old password", async({page}) => {
        await page.getByRole('button', {name:'Change password'}).click();
        await page.locator('[name="new_pass"]').fill(newPassword);
        await page.getByRole('button', {name:'Change password'}).click();
        await expect(page.getByRole('alert')).toHaveText('Password fields cannot be empty!');
    });

    test("TC021D - Invalid old password", async({page}) => {
        await page.getByRole('button', {name:'Change password'}).click();
        await page.locator('[name="old_pass"]').fill(newPassword);
        await page.locator('[name="new_pass"]').fill(newPassword);
        await page.getByRole('button', {name:'Change password'}).click();
        await expect(page.getByRole('alert')).toHaveText('Your old password is not valid');
    });

});

test.describe("TC022 - Order history", () => {
    
    test("TC022A - View order history when user has previous orders", async({page}) => {
        //setup - login with user which has order history
        const pm = new PageManager(page);
        await pm.navigateTo().logout();
        await pm.navigateTo().login();
        await pm.onLoginPage().login('herk@ancientgreek.com','herc');
        await expect(page.getByRole('button', {name: 'Previous orders'})).toBeAttached();
        await page.getByRole('button', {name: 'Previous orders'}).click();
        await expect(page.locator('.usr-prev-ord')).toBeVisible();
        
    });

    test("TC022B - No 'Previous orders' button shown when user has no previous orders", async({page}) => {
        await expect(page.getByRole('button', {name: 'Previous orders'})).not.toBeAttached();
        await expect(page.locator('.usr-prev-ord')).not.toBeVisible();
    });
});

test.describe("TC023 - Delete account", () => {
    
    //register new account with old credentials
    test.afterEach("Try to register account", async({page}) => {
        if(await page.getByRole('button', {name: 'Login'}).isVisible()) {
            const pm = new PageManager(page);
            await pm.navigateTo().register()
            await pm.onRegisterPage().register('John',email,oldPassword);
        }
    });

    test("TC023A - Successfully delete account", async({page}) => {
        await page.getByRole('button', {name: 'Delete account'}).click();
        await page.locator('[name="del"]').fill('DELETE');
        await page.getByRole('button', {name: 'Delete account'}).click();

        await expect(page.getByRole('alert')).toHaveText('Account deleted');
    });

    test("TC023B - Incorrect confirmation prevents account deletion", async({page}) => {
        await page.getByRole('button', {name: 'Delete account'}).click();
        await page.locator('[name="del"]').fill('DEL');
        await page.getByRole('button', {name: 'Delete account'}).click();

        await expect(page.getByRole('alert')).toHaveText('You didn\'t type DELETE correctly');
    });
});    
