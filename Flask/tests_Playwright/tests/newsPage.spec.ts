import {test ,expect} from '@playwright/test';
import { PageManager } from '../page-objects/pageManager';

test.beforeEach("Go to News page", async({page}) => {
    await page.goto('http://localhost:8000/news');
    
});

test("TC008 - Display 5 news items when user visits the news page", async({page}) => {
    const articles = await page.locator('.article').all();
    expect(articles.length).toEqual(5);
});

test("TC009 - Display different 5 news items when user revisits the news page", async({page}) => {
    
    let articles = await page.locator('tbody h4').all();
    const headlines = [];
    for(const item of articles) {
        const articleHeadline = await item.innerText();
        headlines.push(articleHeadline);
    }

    const pm = new PageManager(page);
    await pm.navigateTo().news();

    articles = await page.locator('tbody h4').all();
    
    const newHeadlines = [];
    for(const item of articles) {
        const articleHeadline = await item.innerText();
        newHeadlines.push(articleHeadline);
    }

    expect(headlines).not.toEqual(newHeadlines);
});
