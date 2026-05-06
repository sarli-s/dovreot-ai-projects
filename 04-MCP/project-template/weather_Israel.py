from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright

mcp = FastMCP("weather-Israel")
FORECAST_URL = "https://www.weather2day.co.il/forecast"

playwright_instance = None
browser = None
page = None

@mcp.tool()
async def open_weather_forecast_israel() -> str:
    """פותח את אתר תחזית מזג האויר הישראלי"""
    global playwright_instance, browser, page
    playwright_instance = await async_playwright().start()
    browser = await playwright_instance.chromium.launch(headless=False)
    page = await browser.new_page()
    await page.goto(FORECAST_URL)
    await page.wait_for_load_state("networkidle")
    return "האתר נפתח בהצלחה"

@mcp.tool()
async def enter_weather_forecast_city_israel(city: str) -> str:
    """מזינה שם עיר בשדה החיפוש
    
    Args:
        city: שם העיר
    """
    global page
    await page.locator("#city_search_forecast").fill(city)
    await page.wait_for_timeout(1500)
    return f"העיר {city} הוזנה"

@mcp.tool()
async def select_weather_forecast_city_israel() -> str:
    """בוחרת את העיר הראשונה מהרשימה הנפתחת"""
    global page
    first = page.locator("#city_search_forecastautocomplete-list .autocomplete-items div").first
    await first.click()
    await page.wait_for_load_state("networkidle")
    return "העיר נבחרה בהצלחה"

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()