import sys
import os
import platform
import asyncio
from playwright.async_api import async_playwright

if platform.system() == "Windows":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

async def test_download():
    async with async_playwright() as p:
        print("[1/5] Connecting to Chromium CDP at http://192.168.31.101:9222 ...")
        browser = await p.chromium.connect_over_cdp("http://192.168.31.101:9222")
        context = browser.contexts[0]
        page = await context.new_page()

        url = "https://goodinfo.tw/tw/StockDividendPolicy.asp?STOCK_ID=2330"
        print(f"[2/5] Navigating to {url} ...")
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)
        title = await page.title()
        print(f"[3/5] Page title: {title}")

        print("[4/5] Extracting table tblDetail ...")
        table_html = await page.evaluate("""() => {
            const tbl = document.getElementById('tblDetail') || window['tblDetail'];
            if (tbl) return tbl.outerHTML;
            const tables = Array.from(document.querySelectorAll('table')).filter(
                t => t.rows && t.rows.length >= 2 && t.innerText.length > 80
            );
            if (tables.length > 0) return tables[0].outerHTML;
            return null;
        }""")

        if table_html:
            out_dir = os.path.join(os.getcwd(), "DividendDetail")
            os.makedirs(out_dir, exist_ok=True)
            out_file = os.path.join(out_dir, "DividendDetail_2330_台積電.xls")
            
            clean_html = "<html><head><meta charset='UTF-8'></head><body>" + table_html + "</body></html>"
            with open(out_file, "w", encoding="utf-8-sig") as f:
                f.write(clean_html)
            file_size = os.path.getsize(out_file)
            print(f"[5/5] SUCCESS! File saved to: {out_file} ({file_size} bytes)")
        else:
            print("[5/5] ERROR: Table tblDetail not found!")

        await page.close()

if __name__ == "__main__":
    asyncio.run(test_download())
