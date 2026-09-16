"""
Automated Screenshot Capture Script for Smart Factory Dashboard
Uses Playwright with Chrome to capture pixel-perfect screenshots of all tabs, views, and themes.
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
        page.goto("http://localhost:8501")
        time.sleep(4)

        # Helper to click radio buttons in sidebar
        def select_nav(text_match):
            # Target the Control Navigation radio group specifically
            labels = page.locator('div[data-testid="stRadio"] label')
            count = labels.count()
            for i in range(count):
                lbl = labels.nth(i)
                if text_match in lbl.inner_text():
                    lbl.click()
                    time.sleep(2)
                    return True
            return False

        # Reset factory to pristine baseline first to have a clean initial overview
        reset_btn = page.locator('button:has-text("Reset Factory State")')
        if reset_btn.count() > 0:
            print("Resetting factory to clean state...")
            reset_btn.first.click()
            time.sleep(2)

        # 1. Overview View
        print("Capturing 01_factory_overview.png ...")
        select_nav("Factory Overview & Twin")
        time.sleep(2)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "01_factory_overview.png"), full_page=False)

        # 2. Predictive Maintenance - Top
        print("Navigating to Predictive Maintenance ...")
        select_nav("Predictive Maintenance")
        time.sleep(2)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1)
        print("Capturing 02_predictive_maintenance.png ...")
        page.screenshot(path=os.path.join(OUTPUT_DIR, "02_predictive_maintenance.png"), full_page=False)

        # 2b. Predictive Maintenance - Scrolled to show physical gauges & history chart
        print("Scrolling stMain to capture 02b_pdm_sensor_gauges.png ...")
        page.evaluate("() => { const el = document.querySelector('[data-testid=\"stMain\"]') || document.querySelector('section.stMain'); if (el) el.scrollTop = 480; }")
        time.sleep(1.5)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "02b_pdm_sensor_gauges.png"), full_page=False)

        # 3. Production Orders Queue
        print("Navigating to Production Orders Queue ...")
        select_nav("Production Orders Queue")
        time.sleep(2)
        page.evaluate("() => { const el = document.querySelector('[data-testid=\"stMain\"]') || document.querySelector('section.stMain'); if (el) el.scrollTop = 0; }")
        time.sleep(1)
        print("Capturing 03_production_orders.png ...")
        page.screenshot(path=os.path.join(OUTPUT_DIR, "03_production_orders.png"), full_page=False)

        # 4. Energy Analytics
        print("Navigating to Energy & Power Analytics ...")
        select_nav("Energy & Power Analytics")
        time.sleep(2)
        page.evaluate("() => { const el = document.querySelector('[data-testid=\"stMain\"]') || document.querySelector('section.stMain'); if (el) el.scrollTop = 0; }")
        time.sleep(1)
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
        page.evaluate("() => { const el = document.querySelector('[data-testid=\"stMain\"]') || document.querySelector('section.stMain'); if (el) el.scrollTop = 0; }")
        time.sleep(1)
        print("Capturing 05_ai_production_optimizer.png ...")
        page.screenshot(path=os.path.join(OUTPUT_DIR, "05_ai_production_optimizer.png"), full_page=False)

        # 5b. AI Production Optimizer - Scrolled to show Gantt schedule & reallocations table
        print("Scrolling stMain to capture 05b_optimized_gantt_schedule.png ...")
        page.evaluate("() => { const el = document.querySelector('[data-testid=\"stMain\"]') || document.querySelector('section.stMain'); if (el) el.scrollTop = 580; }")
        time.sleep(1.5)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "05b_optimized_gantt_schedule.png"), full_page=False)

        # 6. What-If Simulation (Tab 1: 10-Step Guided Demonstration Flow)
        print("Navigating to What-If Simulation & Demo ...")
        select_nav("What-If Simulation & Demo")
        time.sleep(2)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1)
        print("Capturing 06_whatif_simulation.png ...")
        page.screenshot(path=os.path.join(OUTPUT_DIR, "06_whatif_simulation.png"), full_page=False)

        # 7. What-If Simulation (Tab 2: Interactive Sandbox)
        print("Switching to Interactive What-If Scenario Sandbox tab ...")
        # Try multiple tab selectors
        sandbox_tab = page.locator('button:has-text("Interactive What-If Scenario Sandbox")')
        if sandbox_tab.count() == 0:
            sandbox_tab = page.locator('[data-baseweb="tab"]:has-text("Interactive What-If Scenario Sandbox")')
        if sandbox_tab.count() == 0:
            sandbox_tab = page.get_by_text("Interactive What-If Scenario Sandbox")

        if sandbox_tab.count() > 0:
            sandbox_tab.first.click()
            time.sleep(2)
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(1)
            print("Capturing 07_whatif_sandbox.png ...")
            page.screenshot(path=os.path.join(OUTPUT_DIR, "07_whatif_sandbox.png"), full_page=False)
        else:
            print("WARNING: Sandbox tab not found!")

        # 8. ML Governance & Metrics
        print("Navigating to ML Governance & Metrics ...")
        select_nav("ML Governance & Metrics")
        time.sleep(2)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1)
        print("Capturing 08_ml_governance_metrics.png ...")
        page.screenshot(path=os.path.join(OUTPUT_DIR, "08_ml_governance_metrics.png"), full_page=False)

        # 9. Clean Light Theme Showcase
        print("Switching to Clean Light Theme ...")
        light_label = page.locator('div[data-testid="stRadio"] label:has-text("Clean Light")')
        if light_label.count() > 0:
            light_label.first.click()
            time.sleep(2)
            select_nav("Factory Overview & Twin")
            time.sleep(2)
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(1)
            print("Capturing 09_clean_light_theme.png ...")
            page.screenshot(path=os.path.join(OUTPUT_DIR, "09_clean_light_theme.png"), full_page=False)

            # Switch back to Dark SCADA
            dark_label = page.locator('div[data-testid="stRadio"] label:has-text("Dark SCADA")')
            if dark_label.count() > 0:
                dark_label.first.click()
                time.sleep(1)

        browser.close()
        print("All 11 screenshots successfully captured!")

if __name__ == "__main__":
    run()

