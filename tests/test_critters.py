import unittest

from app import app
from app.critters import catalog, format_hour, hours_label, months_label, parse_hours, status
from app.types import Critter, CritterKind, Hemisphere

NORTH, SOUTH = Hemisphere.NORTHERN, Hemisphere.SOUTHERN


def find(kind: CritterKind, name: str) -> Critter:
    return next(critter for critter in catalog(kind) if critter.name == name)


class DataTests(unittest.TestCase):
    def test_full_critterpedia_in_game_order(self) -> None:
        self.assertEqual([len(catalog(kind)) for kind in CritterKind], [80, 80, 40])
        for kind in CritterKind:
            numbers = [critter.number for critter in catalog(kind)]
            self.assertEqual(numbers, list(range(1, len(numbers) + 1)))

    def test_every_critter_is_in_season_sometime(self) -> None:
        for kind in CritterKind:
            for critter in catalog(kind):
                self.assertTrue(any(critter.hours_by_month), critter.name)


class AvailabilityTests(unittest.TestCase):
    def test_second_time_window_counts(self) -> None:
        piranha = find(CritterKind.FISH, "Piranha")
        self.assertTrue(status(piranha, NORTH, 7, 22).available)
        self.assertFalse(status(piranha, NORTH, 7, 17).available)
        self.assertTrue(status(find(CritterKind.BUGS, "Evening cicada"), NORTH, 7, 17).available)

    def test_hours_that_change_by_month(self) -> None:
        char = find(CritterKind.FISH, "Char")
        self.assertTrue(status(char, NORTH, 10, 12).available)
        self.assertFalse(status(char, NORTH, 4, 12).available)
        self.assertEqual(status(char, NORTH, 4, 12).schedule,
                         (("Mar – Jun", "4 PM – 9 AM"), ("Sep – Nov", "All day")))

    def test_southern_hemisphere_is_six_months_ahead(self) -> None:
        bitterling = find(CritterKind.FISH, "Bitterling")
        self.assertEqual(status(bitterling, NORTH, 1, 12).months_label, "Nov – Mar")
        self.assertEqual(status(bitterling, SOUTH, 1, 12).months_label, "May – Sep")
        self.assertTrue(status(bitterling, SOUTH, 6, 12).available)

    def test_corrected_rows(self) -> None:
        self.assertTrue(status(find(CritterKind.SEA_CREATURES, "Venus' flower basket"), NORTH, 12, 3).available)
        self.assertEqual(status(find(CritterKind.FISH, "Gar"), NORTH, 1, 0).months_label, "Jun – Sep")
        self.assertEqual(status(find(CritterKind.FISH, "Blowfish"), NORTH, 1, 0).hours_label, "9 PM – 4 AM")
        self.assertEqual(find(CritterKind.FISH, "Pale chub").price, 200)

    def test_new_and_leaving(self) -> None:
        bitterling = find(CritterKind.FISH, "Bitterling")
        self.assertTrue(status(bitterling, NORTH, 11, 12).is_new)
        self.assertTrue(status(bitterling, NORTH, 3, 12).is_leaving)
        self.assertFalse(status(find(CritterKind.FISH, "Sea bass"), NORTH, 3, 12).is_leaving)

    def test_status_labels(self) -> None:
        self.assertEqual(status(find(CritterKind.FISH, "Piranha"), NORTH, 7, 17).next_label, "Back at 9 PM")
        self.assertEqual(status(find(CritterKind.FISH, "Bitterling"), NORTH, 7, 12).next_label, "Returns in November")
        self.assertEqual(status(find(CritterKind.FISH, "Blowfish"), NORTH, 12, 22).until_label, "Until 4 AM")


class LabelTests(unittest.TestCase):
    def test_format_hour(self) -> None:
        self.assertEqual([format_hour(hour) for hour in (0, 11, 12, 23)], ["12 AM", "11 AM", "12 PM", "11 PM"])

    def test_hours_and_months_labels(self) -> None:
        self.assertEqual(hours_label(parse_hours("9 - 16 & 21 - 4")), "9 AM – 4 PM & 9 PM – 4 AM")
        self.assertEqual(hours_label(parse_hours("All day")), "All day")
        self.assertEqual(months_label(frozenset({12, 1, 2, 6})), "Jun, Dec – Feb")

    def test_rejects_empty_window(self) -> None:
        with self.assertRaises(ValueError):
            parse_hours("5 - 5")


class RouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = app.test_client()

    def test_pages_render_with_saved_time_zone(self) -> None:
        self.client.set_cookie("cc_timezone", "America/Los_Angeles")
        for path in ("/", "/index", "/fish", "/bugs", "/sea_creatures"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'data-timezone="America/Los_Angeles"', response.data)
                self.assertNotIn(b"data-tz-detect", response.data)

    def test_first_visit_asks_the_browser(self) -> None:
        self.assertIn(b'data-tz-detect="required"', self.client.get("/fish").data)

    def test_ip_time_zone_is_used_then_verified(self) -> None:
        response = self.client.get("/fish", headers={"X-Vercel-IP-Timezone": "Asia/Tokyo"})
        self.assertIn(b'data-timezone="Asia/Tokyo"', response.data)
        self.assertIn(b'data-tz-detect="verify"', response.data)

    def test_unknown_time_zone_falls_back_to_utc_without_looping(self) -> None:
        response = self.client.get("/fish?timezone=Nowhere/Atlantis")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'data-timezone="UTC"', response.data)
        self.assertNotIn(b"data-tz-detect", response.data)
        self.assertIn(b"Nowhere/Atlantis", response.data)

    def test_legacy_browser_time_zone_names(self) -> None:
        self.assertIn(b'data-timezone="Asia/Calcutta"', self.client.get("/fish?timezone=Asia/Calcutta").data)

    def test_southern_default_for_southern_time_zones(self) -> None:
        self.assertIn(b"in the Southern Hemisphere", self.client.get("/fish?timezone=Australia/Sydney").data)

    def test_settings_from_the_url_are_remembered(self) -> None:
        response = self.client.get("/fish?hemisphere=Southern&timezone=Australia/Sydney")
        cookies = response.headers.getlist("Set-Cookie")
        self.assertTrue(any(cookie.startswith("cc_timezone=Australia/Sydney;") for cookie in cookies))
        self.assertTrue(any(cookie.startswith("cc_hemisphere=Southern;") for cookie in cookies))

    def test_planning_a_time(self) -> None:
        self.assertIn(b"in July at 10 PM", self.client.get("/fish?timezone=UTC&month=7&hour=22").data)

    def test_legacy_form_post_redirects(self) -> None:
        response = self.client.post("/bugs", data={"hemisphere": "Southern", "timezone": "Asia/Tokyo"})
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["Location"], "/bugs?hemisphere=Southern&timezone=Asia/Tokyo")

    def test_versioned_assets_are_cached_forever(self) -> None:
        response = self.client.get("/static/css/app.css?v=1")
        self.assertEqual(response.status_code, 200)
        self.assertIn("immutable", response.headers["Cache-Control"])

    def test_missing_page(self) -> None:
        self.assertEqual(self.client.get("/nope").status_code, 404)


if __name__ == "__main__":
    unittest.main()
