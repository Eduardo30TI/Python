from playwright.sync_api import sync_playwright
import time

link='https://app.lojaintegrada.com.br/painel/login'

with sync_playwright() as p:

    nav=p.chromium.launch(headless=False,)
    page=nav.new_page()
    nav.start_tracing
    page.goto(link)
    
    time.sleep(5)

    pass