import { Locator, Page,expect } from "@playwright/test";

export class NavigationPage {

    private readonly page:Page;
    private readonly newsMenuItem: Locator;
    private readonly productsMenuItem: Locator;
    private readonly cartMenuItem: Locator;
    private readonly userMenuItem: Locator;
    private readonly loginMenuItem: Locator;
    private readonly logoutMenuItem: Locator;

    constructor(page:Page) {
        this.page = page;
        this.newsMenuItem = page.locator('.navbar').getByText('News');
        this.productsMenuItem = page.locator('.navbar').getByText('Products');
        this.cartMenuItem = page.locator('.navbar').locator('.bi.bi-bag');
        this.userMenuItem = page.locator('.navbar').locator('.bi-person-circle');
        this.loginMenuItem = page.locator('.navbar').getByRole('button', {name:'Login'});
        this.logoutMenuItem = page.locator('.navbar').getByRole('button', {name:'Logout'});
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

    async user() {
        await this.userMenuItem.click();
        await this.page.waitForURL('http://localhost:8000/user');
    }

    async login() {
        await this.loginMenuItem.click();
        await this.page.waitForURL('http://localhost:8000/login');
    }

    async logout() {
        await this.logoutMenuItem.click();
        await this.page.waitForURL('http://localhost:8000/login');
    }

    async register() {
        await this.loginMenuItem.click();
        await this.page.waitForURL('http://localhost:8000/login');
        this.page.getByText('Register now').click()
    }
};