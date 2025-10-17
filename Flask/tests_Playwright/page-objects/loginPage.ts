import { Page } from "@playwright/test";

export class LoginPage {

    private readonly page:Page

    constructor(page:Page) {
        this.page = page
    }

    async login(email:string, password:string) {
        await this.page.locator('[name="email"]').fill(email);
        await this.page.locator('[name="pwd"]').fill(password);
        await this.page.getByRole('button', {name:'submit'}).click(); 
    };
};
