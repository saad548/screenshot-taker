from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
from playwright.async_api import async_playwright
import uuid
import os

app = FastAPI(title="Screenshot-as-a-Service", version="1.0")

SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

DEVICE_VIEWPORTS = {
    "desktop": {"width": 1280, "height": 720},
    "mobile": {"width": 375, "height": 667},
    "tablet": {"width": 768, "height": 1024},
}

@app.get("/screenshot")
async def screenshot(
    url: str = Query(..., description="Website URL to capture"),
    device: str = Query("desktop", description="Device type: desktop, mobile, tablet")
):
    if device not in DEVICE_VIEWPORTS:
        raise HTTPException(status_code=400, detail="Invalid device type")

    filename = f"{uuid.uuid4()}.png"
    path = os.path.join(SCREENSHOT_DIR, filename)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(viewport=DEVICE_VIEWPORTS[device])
        page = await context.new_page()

        try:
            await page.goto(url, timeout=10000)
            await page.screenshot(path=path, full_page=True)
        except Exception as e:
            await browser.close()
            raise HTTPException(status_code=500, detail=f"Screenshot failed: {str(e)}")

        await browser.close()

    return FileResponse(path, media_type="image/png", filename=filename)
