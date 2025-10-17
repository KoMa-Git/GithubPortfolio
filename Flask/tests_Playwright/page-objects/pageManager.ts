import { Page,expect } from "@playwright/test";
import { NavigationPage } from "../page-objects/navigationPage";
import { ProductsPage } from "../page-objects/porductsPage";
import { LoginPage } from "../page-objects/loginPage";
import { RegisterPage } from "../page-objects/registerPage";

export class PageManager {

    private readonly page:Page;
    private readonly navigationPage: NavigationPage;
    private readonly productsPage: ProductsPage;
    private readonly loginPage: LoginPage;
    private readonly registerPage: RegisterPage;

    constructor(page:Page) {
        this.page = page;
        this.navigationPage = new NavigationPage(this.page);
        this.productsPage = new ProductsPage(this.page);
        this.loginPage = new LoginPage(this.page);
        this.registerPage = new RegisterPage(this.page);
    };

    navigateTo () {
        return this.navigationPage;
    }

    onProductsPage () {
        return this.productsPage;
    }

    onLoginPage () {
        return this.loginPage;
    }

    onRegisterPage () {
        return this.registerPage;
    }

};