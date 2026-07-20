import os
import uuid
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8000")
ADMIN_USERNAME = os.environ["E2E_ADMIN_USERNAME"]
ADMIN_PASSWORD = os.environ["E2E_ADMIN_PASSWORD"]
PASSWORD = os.environ["E2E_USER_PASSWORD"]
run_id = uuid.uuid4().hex[:8]
alice_username = f"alice-{run_id}"
bob_username = f"bob-{run_id}"
product_title = f"E2E 노트북 {run_id}"
screenshot_dir = Path("test-results/screenshots")
screenshot_dir.mkdir(parents=True, exist_ok=True)


def signup_and_login(page, username, display_name):
    page.goto(f"{BASE_URL}/accounts/signup/")
    page.locator("#id_username").fill(username)
    page.locator("#id_display_name").fill(display_name)
    page.locator("#id_password1").fill(PASSWORD)
    page.locator("#id_password2").fill(PASSWORD)
    page.get_by_role("button", name="가입").click()
    expect(page).to_have_url(f"{BASE_URL}/accounts/login/")
    page.locator("#id_username").fill(username)
    page.locator("#id_password").fill(PASSWORD)
    page.get_by_role("button", name="로그인").click()
    expect(page.get_by_role("link", name="마이페이지")).to_be_visible()


with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    alice_context = browser.new_context()
    bob_context = browser.new_context()
    admin_context = browser.new_context()
    alice = alice_context.new_page()
    bob = bob_context.new_page()
    admin = admin_context.new_page()

    signup_and_login(alice, alice_username, "앨리스")
    alice.get_by_role("link", name="상품 등록").click()
    alice.locator("#id_title").fill(product_title)
    alice.locator("#id_description").fill("Playwright 핵심 흐름 상품")
    alice.locator("#id_price").fill("1500")
    alice.locator("#id_status").select_option("available")
    alice.locator("#id_visibility").select_option("public")
    alice.get_by_role("button", name="저장").click()
    expect(alice.get_by_role("heading", name=product_title)).to_be_visible()
    product_url = alice.url
    alice.screenshot(path=screenshot_dir / "01-product.png", full_page=True)

    signup_and_login(bob, bob_username, "밥")
    bob.locator("#id_q").fill(product_title)
    bob.get_by_role("button", name="검색").click()
    bob.get_by_role("link", name=product_title).click()
    expect(bob.get_by_role("heading", name=product_title)).to_be_visible()
    bob.get_by_role("link", name="앨리스").click()
    bob.get_by_role("button", name="1대1 채팅").click()
    conversation_url = bob.url
    alice.goto(conversation_url)
    expect(bob.get_by_role("button", name="전송")).to_be_enabled()
    expect(alice.get_by_role("button", name="전송")).to_be_enabled()
    bob.locator("#chat-input").fill("안녕하세요, 구매하고 싶습니다.")
    bob.get_by_role("button", name="전송").click()
    expect(alice.locator("#messages")).to_contain_text("안녕하세요, 구매하고 싶습니다.")
    alice.screenshot(path=screenshot_dir / "02-chat.png", full_page=True)

    bob.get_by_role("link", name="지갑").click()
    bob.get_by_role("link", name="송금").click()
    bob.locator("#id_recipient").select_option(label=alice_username)
    bob.locator("#id_amount").fill("500")
    bob.get_by_role("button", name="송금").click()
    expect(bob.get_by_text("송금이 완료되었습니다.")).to_be_visible()
    expect(bob.get_by_text("9500 포인트")).to_be_visible()
    alice.goto(f"{BASE_URL}/wallet/")
    expect(alice.get_by_text("10500 포인트")).to_be_visible()
    expect(alice.get_by_text(f"{bob_username} · 500")).to_be_visible()
    alice.screenshot(path=screenshot_dir / "03-wallet.png", full_page=True)

    bob.goto(product_url)
    bob.get_by_role("link", name="상품 신고").click()
    bob.locator("#id_reason").fill("E2E 관리자 제재 확인 신고")
    bob.get_by_role("button", name="신고").click()

    admin.goto(f"{BASE_URL}/accounts/login/")
    admin.locator("#id_username").fill(ADMIN_USERNAME)
    admin.locator("#id_password").fill(ADMIN_PASSWORD)
    admin.get_by_role("button", name="로그인").click()
    admin.goto(f"{BASE_URL}/moderation/manage/")
    expect(admin.get_by_text("E2E 관리자 제재 확인 신고")).to_be_visible()
    admin.get_by_role("link", name="상품 관리").click()
    admin.locator("#id_action").select_option("block")
    admin.locator("#id_reason").fill("E2E 검증 악성 상품 차단")
    admin.get_by_role("button", name="적용").click()
    expect(admin.get_by_role("heading", name="플랫폼 관리")).to_be_visible()
    admin.screenshot(path=screenshot_dir / "04-moderation.png", full_page=True)

    response = bob.goto(product_url)
    assert response is not None and response.status == 404
    response = bob.goto(f"{BASE_URL}/moderation/manage/")
    assert response is not None and response.status == 403

    alice_context.close()
    bob_context.close()
    admin_context.close()
    browser.close()
