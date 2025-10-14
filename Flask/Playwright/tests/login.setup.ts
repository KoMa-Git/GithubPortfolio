import {test as setup,expect} from '@playwright/test';
import fs from 'fs';

const authFile = './.auth/user.json';

setup('login', async({page}) => {
    await page.goto('http://localhost:8000');
    await page.getByRole('button',{name:'Login'}).click();
    await page.locator('[name="email"]').fill('john.doe@valid.com');
    await page.locator('[name="pwd"]').fill('johhnie123');
    await page.getByRole('button', {name:'submit'}).click();
    await expect(page.getByRole('alert')).toContainText('logged in successful');

    await page.context().storageState({path:authFile})

});