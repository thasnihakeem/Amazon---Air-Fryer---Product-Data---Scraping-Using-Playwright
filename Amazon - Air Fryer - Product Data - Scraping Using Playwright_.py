
import re
import random
import asyncio
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


async def get_special_feature(page):
    try:
        special_feature_elem = await page.query_selector("tr:has-text('Special Feature') td.a-size-base")
        special_feature = await special_feature_elem.inner_text()
        special_feature = re.sub('\u200e', '', special_feature)
    except:
        special_feature = "Not Available"
    return special_feature


async def get_product_dimensions(page):
    try:
        product_dimensions_element = await page.query_selector("tr:has-text('Product Dimensions') td.a-size-base")
        product_dimensions = await product_dimensions_element.inner_text()
        product_dimensions = re.sub('\u200e', '', product_dimensions)
    except:
        product_dimensions = "Not Available"
    return product_dimensions


async def get_product_color(page):
    try:
        color = await (await page.query_selector("tr th:has-text('Colour')+ td.a-size-base")).text_content()
        color = re.sub('\u200e', '', color)
    except:
        color = "Not Available"
    return color.strip()


async def get_capacity(page):
    try:
        capacity = await (await page.query_selector("tr:has-text('Capacity') td.a-size-base")).inner_text()
        capacity = re.sub('\u200e', '', capacity)
    except:
        capacity = "Not Available"
    return capacity


async def get_material(page):
    try:
        material = await (await page.query_selector("tr th:has-text('Material') + td")).text_content()
        material = re.sub('\u200e', '', material)
    except:
        material = "Not Available"
    return material.strip()


async def get_recommended_uses(page):
    try:
        recommended_uses = await (
            await page.query_selector("tr th:has-text('Recommended Uses For Product') + td")).text_content()
        recommended_uses = re.sub('\u200e', '', recommended_uses)
    except:
        recommended_uses = "Not Available"
    return recommended_uses.strip()


async def get_output_wattage(page):
    try:
        output_wattage = await (
            await page.query_selector("tr:has-text('Output Wattage') td.a-size-base")).inner_text()
        output_wattage = re.sub('\u200e', '', output_wattage)
    except:
        output_wattage = "Not Available"
    return output_wattage


async def get_item_weight(page):
    try:
        item_weight = await (
            await page.query_selector("tr:has-text('Item Weight') td.a-size-base")).inner_text()
        item_weight = re.sub('\u200e', '', item_weight)
    except:
        item_weight = "Not Available"
    return item_weight



async def get_control_method(page):
    try:
        control_method = await (
            await page.query_selector("tr:has-text('Control Method') td.a-size-base")).inner_text()
        control_method = re.sub('\u200e', '', control_method)
    except:
        control_method = "Not Available"
    return control_method


async def get_model_name(page):
    try:
        model_name = await (await page.query_selector("tr:has-text('Model Name') td.a-size-base")).inner_text()
        model_name = re.sub('\u200e', '', model_name)
    except:
        model_name = "Not Available"
    return model_name.strip()


async def get_nonstick_coating(page):
    try:
        nonstick_coating = await (
            await page.query_selector("tr:has-text('Has Nonstick Coating') td.a-size-base")).inner_text()
        nonstick_coating = re.sub('\u200e', '', nonstick_coating)
    except:
        nonstick_coating = "Not Available"
    return nonstick_coating.strip()


async def get_is_dishwasher_safe(page):
    try:
        is_dishwasher_safe = await (
            await page.query_selector("tr:has-text('Is Dishwasher Safe') td.a-size-base")).inner_text()
        is_dishwasher_safe = re.sub('\u200e', '', is_dishwasher_safe)
    except:
        is_dishwasher_safe = "Not Available"
    return is_dishwasher_safe


async def get_manufacturer(page):
    try:
        manufacturer = await (
            await page.query_selector("tr th:has-text('Manufacturer') + td")).text_content()
        manufacturer = re.sub('\u200e', '', manufacturer)
    except:
        manufacturer = "Not Available"
    return manufacturer.strip()


async def get_country_of_origin(page):
    try:
        country_of_origin = await (await page.query_selector("tr th:has-text('Country of Origin') + td")).inner_html()
        country_of_origin = re.sub('\u200e', '', country_of_origin)
    except:
        country_of_origin = "Not Available"
    return country_of_origin.strip()


async def get_item_model_number(page):
    try:
        item_model_number = await (
            await page.query_selector("tr:has-text('Item model number') td.a-size-base")).inner_text()
        item_model_number = re.sub('\u200e', '', item_model_number)
    except:
        item_model_number = "Not Available"
    return item_model_number


async def get_wattage(page):
    try:
        wattage = await (await page.querySelector("tr:has-text('Wattage') td.a-size-base")).inner_text()
        wattage = re.sub('\u200e', '', wattage)
    except:
        wattage = "Not Available"
    return wattage


async def get_asin(page):
    try:
        asin = await (await page.query_selector("tr:has-text('ASIN') td.a-size-base")).inner_text()
        asin = re.sub('\u200e', '', asin)

    except:
        asin = "Not Available"
    return asin


async def get_min_temperature_setting(page):
    try:
        min_temperature = await (
            await page.query_selector("tr:has-text('Min Temperature Setting') td.a-size-base")).inner_text()
        min_temperature = re.sub('\u200e', '', min_temperature)
    except:
        min_temperature = "Not Available"
    return min_temperature


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
        await perform_request_with_retry(page, 'https://www.amazon.in/s?k=air+fryer&crid=3EWKFR0AZLVMY&sprefix=air+fryer%2Caps%2C3150&ref=nb_sb_noss_1')
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
            item_model_number = await get_item_model_number(page)
            output_wattage = await get_output_wattage(page)
            wattage = await get_wattage(page)
            country_of_origin = await get_country_of_origin(page)
            manufacturer = await get_manufacturer(page)
            is_dishwasher_safe = await get_is_dishwasher_safe(page)
            nonstick_coating = await get_nonstick_coating(page)
            model_name = await get_model_name(page)
            control_method = await get_control_method(page)
            item_weight = await get_item_weight(page)
            recommended_uses = await get_recommended_uses(page)
            material = await get_material(page)
            capacity = await get_capacity(page)
            product_color = await get_product_color(page)
            product_dimensions = await get_product_dimensions(page)
            special_feature = await get_special_feature(page)
            asin = await get_asin(page)
            min_temperature = await get_min_temperature_setting(page)
            bullet_points = await get_bullet_points(page)


            if i % 10 == 0 and i > 0:
                print(f"Processed {i} links.")
            if i == len(product_links) - 1:
                print(f"All information for link {i} has been scraped.")


            data.append((link, product_name, brand, star_rating, num_ratings, original_price, offer_price,
                         best_sellers_rank, output_wattage, asin, item_model_number, min_temperature, wattage, country_of_origin, manufacturer,
                        is_dishwasher_safe, nonstick_coating, model_name, control_method, item_weight, recommended_uses,
                        material, capacity, product_color, product_dimensions, special_feature, bullet_points))


        df = pd.DataFrame(data, columns=['Product Link', 'Product Name', 'Brand', 'Star Rating', 'Number of Ratings',
                                         'Original Price', 'Offer Price', 'Best Sellers Rank', 'output_wattage', 'asin', 'item_model_number', 'min_temperature', 'wattage',
                                   'country_of_origin', 'manufacturer', 'is_dishwasher_safe', 'nonstick_coating',
                                   'model_name', 'control_method', 'item_weight', 'recommended_uses', 'material',
                                   'capacity', 'product_color', 'product_dimensions', 'special_feature', 'bullet_points'])
        

        df.to_csv('product_details_new_day_3.csv', index=False)
        print('CSV file has been written successfully.')
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main()

