"""
Automated Screenshot Capture Script for Smart Factory Dashboard
Uses Playwright to capture pixel-perfect screenshots of all tabs and views.
"""
import os
import time
from playwright.sync_api import sync_playwright

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "docs", "screenshots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        print("Navigating to http://localhost:8501 ...")
        page.goto("http://localhost:8501", wait_until="networkidle")
        time.sleep(3)

        # 1. Overview View
        print("Capturing 01_factory_overview.png ...")
        page.screenshot(path=os.path.join(OUTPUT_DIR, "01_factory_overview.png"), full_page=False)

        # Helper to click radio buttons in sidebar
        def select_nav(text_match):
            labels = page.locator('div[data-testid="stRadio"] label')
            count = labels.count()
            for i in range(count):
                lbl = labels.nth(i)
                if text_match in lbl.inner_text():
                    lbl.click()
                    time.sleep(2)
                    page.wait_for_load_state("networkidle")
                    time.sleep(1)
                    return True
            return False

        # 2. Predictive Maintenance
        print("Navigating to Predictive Maintenance ...")
        select_nav("Predictive Maintenance")
        time.sleep(2)
        print("Capturing 02_predictive_maintenance.png ...")
        page.screenshot(path=os.path.join(OUTPUT_DIR, "02_predictive_maintenance.png"), full_page=False)

        # 3. Production Orders Queue
        print("Navigating to Production Orders Queue ...")
        select_nav("Production Orders Queue")
        time.sleep(2)
        print("Capturing 03_production_orders.png ...")
        page.screenshot(path=os.path.join(OUTPUT_DIR, "03_production_orders.png"), full_page=False)

        # 4. Energy Analytics
        print("Navigating to Energy & Power Analytics ...")
        select_nav("Energy & Power Analytics")
        time.sleep(2)
        print("Capturing 04_energy_analytics.png ...")
        page.screenshot(path=os.path.join(OUTPUT_DIR, "04_energy_analytics.png"), full_page=False)

        # 5. AI Production Optimizer
        print("Navigating to AI Production Optimizer ...")
        select_nav("AI Production Optimizer")
        time.sleep(2)
        # Click Run Optimization button to show comparison and Gantt chart
        opt_btn = page.locator('button:has-text("Run AI Production Optimization")')
        if opt_btn.count() > 0:
            print("Clicking Run AI Production Optimization ...")
            opt_btn.first.click()
            time.sleep(4)
        print("Capturing 05_ai_production_optimizer.png ...")
        page.screenshot(path=os.path.join(OUTPUT_DIR, "05_ai_production_optimizer.png"), full_page=False)

        # 6. What-If Simulation
        print("Navigating to What-If Simulation & Demo ...")
        select_nav("What-If Simulation & Demo")
        time.sleep(2)
        print("Capturing 06_whatif_simulation.png ...")
        page.screenshot(path=os.path.join(OUTPUT_DIR, "06_whatif_simulation.png"), full_page=False)

        # Switch to sandbox tab
        tabs = page.locator('button[role="tab"]')
        if tabs.count() >= 2:
            print("Clicking Interactive What-If Scenario Sandbox tab ...")
            tabs.nth(1).click()
            time.sleep(2)
            print("Capturing 07_whatif_sandbox.png ...")
            page.screenshot(path=os.path.join(OUTPUT_DIR, "07_whatif_sandbox.png"), full_page=False)

        # 7. ML Governance & Metrics
        print("Navigating to ML Governance & Metrics ...")
        select_nav("ML Governance & Metrics")
        time.sleep(2)
        print("Capturing 08_ml_governance_metrics.png ...")
        page.screenshot(path=os.path.join(OUTPUT_DIR, "08_ml_governance_metrics.png"), full_page=False)

        browser.close()
        print("All screenshots successfully captured!")

if __name__ == "__main__":
    run()
