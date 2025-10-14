import { Page } from "@playwright/test";

export class ProductsPage {

    private readonly page:Page

    constructor(page:Page) {
        this.page = page
    }

    async addToCart(itemName:string) {
        const products = this.page.locator('.col .card');
        let foundItem = false;
        for(const product of await products.all()) {
            const productName = await product.locator('h5').textContent();
            if(productName === itemName) {
                foundItem = true;
                await product.getByRole("button", {name:"Add to cart"}).click();
            }
        }
        if(foundItem) {
            return foundItem;
        } else {
            throw new Error('No products with this name.');
        }
        
    }

    async getRandomProductName(): Promise<string> {
        const productNameLocators = await this.page.locator('.card-title').all();
        const numberOfProducts = productNameLocators.length;

        if (numberOfProducts === 0) {
            throw new Error('No products found on the page.');
        }

        const randomIndex = Math.floor(Math.random()*numberOfProducts)
        const productName = await productNameLocators[randomIndex].textContent();
        return productName ?? 'Unknown product';
    }

    async addToCartRandomProduct() {
        const randomProductName = await this.getRandomProductName();
        await this.addToCart(randomProductName);
    }
};