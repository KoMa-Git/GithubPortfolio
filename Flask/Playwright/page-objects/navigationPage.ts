import { Locator, Page,expect } from "@playwright/test";

export class NavigationPage {

    private readonly page:Page;
    private readonly newsMenuItem: Locator;
    private readonly productsMenuItem: Locator;
    private readonly cartMenuItem: Locator;
    private readonly loginMenuItem: Locator;

    constructor(page:Page) {
        this.page = page;
        this.newsMenuItem = page.getByText('News');
        this.productsMenuItem = page.getByText('Products');
        this.cartMenuItem = page.locator('.bi.bi-bag');
        this.loginMenuItem = page.getByRole('button', {name:'Login'});
    }

    async news() {
        await this.newsMenuItem.click();
        await this.page.waitForTimeout(500);
    }

    async products() {
        await this.productsMenuItem.click();
        await this.page.waitForURL('http://localhost:8000/products');
    }

    async cart() {
        await this.cartMenuItem.click();
        await this.page.waitForURL('http://localhost:8000/cart');
    }

    async login() {
        await this.loginMenuItem.click();
        await this.page.waitForURL('http://localhost:8000/login');
    }

    async register() {
        await this.loginMenuItem.click();
        await this.page.waitForURL('http://localhost:8000/login');
        this.page.getByText('Register now').click()
    }
};