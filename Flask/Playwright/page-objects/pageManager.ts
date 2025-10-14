import { Page,expect } from "@playwright/test";
import { NavigationPage } from "../page-objects/navigationPage";
import { ProductsPage } from "../page-objects/porductsPage";

export class PageManager {

    private readonly page:Page;
    private readonly navigationPage: NavigationPage;
    private readonly productsPage: ProductsPage;

    constructor(page:Page) {
        this.page = page;
        this.navigationPage = new NavigationPage(this.page);
        this.productsPage = new ProductsPage(this.page);
    };

    navigateTo () {
        return this.navigationPage;
    }

    onProductsPage () {
        return this.productsPage;
    }

};