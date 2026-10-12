"""Browser regression tests. Run: uv run --with playwright python tests/mobile_navigation_test.py.

SITE_BASE_URL optionally tests a published site. Third-party requests, including
Analytics, Ads and WhatsApp, are blocked to avoid creating real conversions.
"""
import functools
import os
from pathlib import Path
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import unittest
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright, expect

PAGES = {"/": "#como-funciona", "/infantil/online/": "#consulta"}


class MobileNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = None
        cls.base = os.environ.get("SITE_BASE_URL", "").rstrip("/")
        if not cls.base:
            root = Path(__file__).resolve().parents[1]

            class QuietHandler(SimpleHTTPRequestHandler):
                def log_message(self, *_args):
                    pass

            cls.server = ThreadingHTTPServer(
                ("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(root))
            )
            threading.Thread(target=cls.server.serve_forever, daemon=True).start()
            cls.base = f"http://127.0.0.1:{cls.server.server_port}"
        cls.driver = sync_playwright().start()
        cls.browser = cls.driver.chromium.launch(
            executable_path=os.environ.get(
                "CHROME_PATH", "C:/Program Files/Google/Chrome/Application/chrome.exe"
            ), headless=True
        )

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.driver.stop()
        if cls.server:
            cls.server.shutdown()
            cls.server.server_close()

    def setUp(self):
        self.context = self.browser.new_context(
            viewport={"width": 390, "height": 844}, reduced_motion="reduce"
        )
        host = urlparse(self.base).netloc
        self.context.route(
            "**/*", lambda route: route.continue_()
            if urlparse(route.request.url).netloc == host else route.abort()
        )
        self.page = self.context.new_page()

    def tearDown(self):
        self.context.close()

    def test_mobile_menu_can_be_opened(self):
        for path in PAGES:
            with self.subTest(path=path):
                self.page.goto(self.base + path, wait_until="load")
                menu = self.page.locator("details.mobile-nav")
                self.assertEqual(menu.count(), 1, "Missing mobile navigation")
                expect(menu.locator("summary")).to_be_visible()
                expect(self.page.locator("header .nav > .btn-wa")).to_be_hidden()
                menu.locator("summary").click()
                self.assertTrue(menu.evaluate("e => e.open"))
                self.assertEqual(menu.locator("nav a").count(), 5)
                expect(menu.locator("nav a").first).to_be_visible()

    def test_selecting_shortcut_closes_menu_and_reaches_section(self):
        for path in PAGES:
            with self.subTest(path=path):
                self.page.goto(self.base + path, wait_until="load")
                menu = self.page.locator("details.mobile-nav")
                links = menu.locator("nav a")
                self.assertEqual(links.all_text_contents(), [
                    "Como funciona", "Quem atende", "Avaliações", "Onde atendo", "Perguntas frequentes"
                ])
                for index in range(links.count()):
                    menu.locator("summary").click()
                    target = links.nth(index).get_attribute("href")
                    self.assertEqual(self.page.locator(target).count(), 1)
                    links.nth(index).click()
                    self.assertFalse(menu.evaluate("e => e.open"), "Menu must close after selection")
                    self.assertEqual(urlparse(self.page.url).fragment, target[1:])
                    expect(self.page.locator(target)).to_be_focused()
                    top = self.page.locator(target).bounding_box()["y"]
                    header_bottom = self.page.locator("header").bounding_box()["height"]
                    self.assertGreaterEqual(top, header_bottom - 1, "Sticky header hides the destination")

    def test_keyboard_can_open_navigate_and_dismiss_menu(self):
        for path in PAGES:
            with self.subTest(path=path):
                self.page.goto(self.base + path, wait_until="load")
                menu = self.page.locator("details.mobile-nav")
                summary = menu.locator("summary")
                summary.focus()
                self.page.keyboard.press("Enter")
                self.assertTrue(menu.evaluate("e => e.open"))
                self.page.keyboard.press("Tab")
                expect(menu.locator("nav a").first).to_be_focused()
                self.page.keyboard.press("Escape")
                self.assertFalse(menu.evaluate("e => e.open"))
                expect(summary).to_be_focused()
                self.page.keyboard.press("Space")
                self.assertTrue(menu.evaluate("e => e.open"))
                self.page.keyboard.press("Space")
                self.assertFalse(menu.evaluate("e => e.open"))

    def test_menu_closes_when_clicking_outside_or_switching_to_desktop(self):
        for path in PAGES:
            with self.subTest(path=path):
                self.page.set_viewport_size({"width": 390, "height": 844})
                self.page.goto(self.base + path, wait_until="load")
                menu = self.page.locator("details.mobile-nav")
                menu.locator("summary").click()
                bottom_bar = self.page.locator(".sticky-bar").bounding_box()
                self.page.mouse.click(4, bottom_bar["y"] - 10)
                self.assertFalse(menu.evaluate("e => e.open"))
                menu.locator("summary").click()
                self.page.set_viewport_size({"width": 1440, "height": 1000})
                expect(menu).to_be_hidden()
                expect(menu).not_to_have_attribute("open", "")
                self.page.set_viewport_size({"width": 390, "height": 844})
                self.assertFalse(menu.evaluate("e => e.open"))

    def test_small_and_landscape_viewports_have_usable_menu(self):
        for path in PAGES:
            for width, height in [(320, 568), (360, 740), (430, 932), (768, 1024), (900, 844), (844, 390), (568, 320)]:
                with self.subTest(path=path, width=width, height=height):
                    self.page.set_viewport_size({"width": width, "height": height})
                    self.page.goto(self.base + path, wait_until="load")
                    menu = self.page.locator("details.mobile-nav")
                    summary = menu.locator("summary")
                    box = summary.bounding_box()
                    self.assertGreaterEqual(box["height"], 44)
                    self.assertGreaterEqual(box["x"], 0)
                    self.assertLessEqual(box["x"] + box["width"], width)
                    summary.click()
                    panel = menu.locator("nav").bounding_box()
                    self.assertGreaterEqual(panel["x"], 0)
                    self.assertLessEqual(panel["x"] + panel["width"], width)
                    sticky = self.page.locator(".sticky-bar").bounding_box()
                    self.assertLessEqual(panel["y"] + panel["height"], sticky["y"])
                    self.assertLessEqual(self.page.evaluate("document.documentElement.scrollWidth"), width)
                    menu.locator("nav a").last.click()
                    self.assertFalse(menu.evaluate("e => e.open"))
                    self.assertEqual(urlparse(self.page.url).fragment, "faq")

    def test_desktop_retains_existing_header(self):
        for path in PAGES:
            for width in [901, 1440]:
                with self.subTest(path=path, width=width):
                    self.page.set_viewport_size({"width": width, "height": 1000})
                    self.page.goto(self.base + path, wait_until="load")
                    expect(self.page.locator("details.mobile-nav")).to_be_hidden()
                    expect(self.page.locator("header .nav-links")).to_be_visible()
                    expect(self.page.locator("header .nav > .btn-wa")).to_be_visible()
                    expect(self.page.locator(".sticky-bar")).to_be_hidden()

    def test_menu_opens_even_when_javascript_is_disabled(self):
        host = urlparse(self.base).netloc
        with self.browser.new_context(viewport={"width": 390, "height": 844}, java_script_enabled=False) as context:
            context.route("**/*", lambda route: route.continue_()
                          if urlparse(route.request.url).netloc == host else route.abort())
            page = context.new_page()
            for path in PAGES:
                with self.subTest(path=path):
                    page.goto(self.base + path, wait_until="load")
                    menu = page.locator("details.mobile-nav")
                    menu.locator("summary").click()
                    expect(menu).to_have_attribute("open", "")
                    expect(menu.locator("nav a").last).to_be_visible()
                    menu.locator("summary").click()
                    expect(menu).not_to_have_attribute("open", "")

    def test_sticky_whatsapp_link_still_opens_in_new_tab(self):
        # Intercept the destination locally. No request reaches WhatsApp or Ads.
        self.context.route("https://wa.me/**", lambda route: route.fulfill(
            status=200, content_type="text/plain", body="Test interception. No message sent."
        ))
        for path in PAGES:
            with self.subTest(path=path):
                self.page.goto(self.base + path, wait_until="load")
                link = self.page.locator(".sticky-bar a")
                expect(link).to_be_visible()
                self.assertEqual(link.get_attribute("target"), "_blank")
                expected_url = link.get_attribute("href")
                with self.page.expect_popup() as popup_info:
                    link.click()
                popup = popup_info.value
                popup.wait_for_load_state("load")
                self.assertEqual(popup.url, expected_url)
                self.assertEqual(urlparse(self.page.url).path, path)
                popup.close()

    def test_header_menu_does_not_inherit_faq_card_spacing(self):
        for path in PAGES:
            with self.subTest(path=path):
                self.page.goto(self.base + path, wait_until="load")
                menu = self.page.locator("details.mobile-nav")
                self.assertEqual(menu.bounding_box()["height"], menu.locator("summary").bounding_box()["height"])
                self.assertEqual(self.page.locator("header .nav").bounding_box()["height"], 70)

    def test_native_accessibility_reports_expanded_state(self):
        for path in PAGES:
            with self.subTest(path=path):
                self.page.goto(self.base + path, wait_until="load")
                session = self.context.new_cdp_session(self.page)
                for expanded in [False, True]:
                    if expanded:
                        self.page.locator(".mobile-nav summary").click()
                    nodes = session.send("Accessibility.getFullAXTree")["nodes"]
                    controls = [node for node in nodes if node.get("name", {}).get("value") == "Menu"
                                and node.get("role", {}).get("value") == "DisclosureTriangle"]
                    self.assertEqual(len(controls), 1)
                    properties = {item["name"]: item["value"].get("value")
                                  for item in controls[0]["properties"]}
                    self.assertTrue(properties["focusable"])
                    self.assertEqual(properties["expanded"], expanded)
                session.detach()


if __name__ == "__main__":
    unittest.main(verbosity=2)
