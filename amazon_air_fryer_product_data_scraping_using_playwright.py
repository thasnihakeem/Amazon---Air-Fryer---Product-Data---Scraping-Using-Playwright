import re
import random
import asyncio
import datetime
import pandas as pd
from playwright.async_api import async_playwright


async def perform_request_with_retry(page, link):
    MAX_RETRIES = 5
    retry_count = 0
    while retry_count < MAX_RETRIES:
        try:
            await page.goto(link, timeout=60000)
            break
        except:
            retry_count += 1
            if retry_count == MAX_RETRIES:
                raise Exception("Request timed out")
            await asyncio.sleep(random.uniform(1, 5))


async def extract_product_links(browser, page, num_products=0, num_clicks=0):
    all_items = await page.query_selector_all(
        '.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal')
    product_links = set()
    for item in all_items:
        link = await item.get_attribute('href')
        full_link = 'https://www.amazon.in' + link
        product_links.add(full_link)  
    num_products += len(product_links)
    print(f"Scraped {num_products} products.")

    next_button = await page.query_selector(
        "a.s-pagination-item.s-pagination-next.s-pagination-button.s-pagination-separator")
    if next_button:
        num_clicks += 1
        await next_button.click()
        await page.wait_for_selector('.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal')
        product_links.update(
            await extract_product_links(browser, page, num_products,
                                        num_clicks)) 
    print(f"Finished scraping {num_products} products after {num_clicks} clicks.")
    return list(product_links)


async def get_product_name(page):
    try:
        product_name = await (await page.query_selector("#productTitle")).text_content()
    except:
        product_name = "Not Available"
    return product_name


async def get_brand(page):
    try:
        brand = await (await page.query_selector("tr:has-text('Brand') td.a-size-base")).inner_text()
        brand = re.sub('\u200e', '', brand)
    except:
        brand = "Not Available"
    return brand


async def get_star_rating(page):
    try:
        star_rating = await (await page.query_selector(".a-icon-row .a-icon-alt")).inner_text()
        star_rating = star_rating.split(" ")[0]
    except:
        star_rating = "Not Available"
    return star_rating


async def get_num_ratings(page):
    try:
        num_ratings_elem = await page.query_selector("#acrCustomerReviewLink #acrCustomerReviewText")
        num_ratings = await num_ratings_elem.inner_text()
        num_ratings = num_ratings.split(" ")[0]
    except:
        num_ratings = "Not Available"
    return num_ratings


async def get_original_price(page):
    try:
        original_price = await (await page.query_selector(".a-price.a-text-price")).text_content()
        original_price = original_price.split("₹")[1]
    except:
        original_price = "Not Available"
    return original_price


async def get_offer_price(page):
    try:
        offer_price = await (await page.query_selector(".a-price-whole")).text_content()
    except:
        offer_price = "Not Available"
    return offer_price


async def extract_technical_details(page):
    try:
        table_element = await page.query_selector("#productDetails_techSpec_section_1")
        rows = await table_element.query_selector_all("tr")
        technical_details = {}
        for row in rows:
            key_element = await row.query_selector("th")
            value_element = await row.query_selector("td")
            key = await page.evaluate('(element) => element.textContent', key_element)
            value = await page.evaluate('(element) => element.textContent', value_element)
            value = value.strip().replace('\u200e', '')
            technical_details[key.strip()] = value
        return technical_details
    except:
        return {}


async def get_best_sellers_rank(page):
    try:
        best_sellers_rank = await (
            await page.query_selector("tr th:has-text('Best Sellers Rank') + td span:nth-child(1)")).text_content()
    except:
        best_sellers_rank = "Not Available"
    return best_sellers_rank


async def get_bullet_points(page):
    bullet_points = []
    try:
        ul_element = await page.query_selector('#feature-bullets ul.a-vertical')
        li_elements = await ul_element.query_selector_all('li')
        for li in li_elements:
            bullet_points.append(await li.inner_text())
    except:
        bullet_points = []
    return bullet_points


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        await perform_request_with_retry(page,
                                         'https://www.amazon.in/s?k=air+fryer&crid=3EWKFR0AZLVMY&sprefix=air+fryer%2Caps%2C3150&ref=nb_sb_noss_1')
        product_links = await extract_product_links(browser, page)

        data = []
        for i, link in enumerate(product_links):
            await perform_request_with_retry(page, link)

            product_name = await get_product_name(page)
            brand = await get_brand(page)
            star_rating = await get_star_rating(page)
            num_ratings = await get_num_ratings(page)
            original_price = await get_original_price(page)
            offer_price = await get_offer_price(page)
            best_sellers_rank = await get_best_sellers_rank(page)
            technical_details = await extract_technical_details(page)
            bullet_points = await get_bullet_points(page)

            if i % 10 == 0 and i > 0:
                print(f"Processed {i} links.")
            if i == len(product_links) - 1:
                print(f"All information for link {i} has been scraped.")

            today = datetime.datetime.now().strftime("%Y-%m-%d")
            data.append((today, link, product_name, brand, star_rating, num_ratings, original_price, offer_price,
                         best_sellers_rank, technical_details, bullet_points))

        df = pd.DataFrame(data,
                          columns=['Date', 'Product Link', 'Product Name', 'Brand', 'Star Rating', 'Number of Ratings',
                                   'Original Price', 'Offer Price', 'Best Sellers Rank', 'Technical Details',
                                   'Description'])

        df.to_csv('product_details_new_day_4.1.csv', index=False)
        print('CSV file has been written successfully.')
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
