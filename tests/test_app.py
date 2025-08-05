import asyncio
from importlib import resources
from remove_desktop_ini.app import RemoveDesktopIniApp


def test_css_resource_exists():
    css = resources.read_text("remove_desktop_ini", "remove_desktop_ini.css")
    assert css.strip()


def test_app_can_start_and_load_css():
    app = RemoveDesktopIniApp()

    async def run_app():
        async with app.run_test():
            # Ensure stylesheet rules were loaded
            assert len(app.stylesheet.rules) > 0

    asyncio.run(run_app())
