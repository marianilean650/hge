import base64
import random
import requests
from seleniumbase import SB


def get_geo_data():
    """Fetch geolocation data safely."""
    try:
        response = requests.get("http://ip-api.com/json/", timeout=5)
        response.raise_for_status()
        data = response.json()

        return {
            "lat": data.get("lat"),
            "lon": data.get("lon"),
            "timezone": data.get("timezone"),
            "country_code": data.get("countryCode", "").lower(),
        }
    except Exception as e:
        print(f"[ERROR] Failed to fetch geo data: {e}")
        return None


def decode_username(encoded_name: str) -> str:
    """Decode base64 username safely."""
    try:
        return base64.b64decode(encoded_name).decode("utf-8")
    except Exception as e:
        print(f"[ERROR] Failed to decode username: {e}")
        return None


def click_if_present(driver, selector, timeout=4):
    """Utility to click an element if it exists."""
    if driver.is_element_present(selector):
        driver.cdp.click(selector, timeout=timeout)


def start_stream_session(driver, url, timezone, geoloc):
    """Open Twitch stream and handle prompts."""
    driver.activate_cdp_mode(url, tzone=timezone, geoloc=geoloc)
    driver.sleep(2)

    click_if_present(driver, 'button:contains("Accept")')
    driver.sleep(2)

    driver.sleep(12)
    click_if_present(driver, 'button:contains("Start Watching")')
    driver.sleep(2)
    click_if_present(driver, 'button:contains("Accept")')


def main():
    geo = get_geo_data()
    if not geo:
        print("[FATAL] Cannot continue without geolocation.")
        return

    geoloc = (geo["lat"], geo["lon"])
    timezone_id = geo["timezone"]

    encoded_name = "YnJ1dGFsbGVz"
    username = decode_username(encoded_name)
    if not username:
        print("[FATAL] Cannot decode username.")
        return

    url = f"https://www.twitch.tv/{username}"
    proxy_str = False

    while True:
        with SB(
            uc=True,
            locale="en",
            ad_block=True,
            chromium_arg="--disable-webgl",
            proxy=proxy_str,
        ) as driver:

            rnd = random.randint(450, 800)

            start_stream_session(driver, url, timezone_id, geoloc)

            # Check if live stream is present
            if driver.is_element_present("#live-channel-stream-information"):

                # Open second viewer session
                driver2 = driver.get_new_driver(undetectable=True)
                start_stream_session(driver2, url, timezone_id, geoloc)

                driver.sleep(rnd)

            else:
                print("[INFO] Stream offline. Exiting loop.")
                break


if __name__ == "__main__":
    main()
