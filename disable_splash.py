import sys

# 1. Update splash.py
with open("splash.py", "r", encoding="utf-8") as f:
    splash_text = f.read()

dummy_class = """class DummySplashController:
    def set_progress(self, percent: int, text: str = ""):
        pass
    def set_status(self, text: str):
        pass
    def finish(self):
        pass
    def close(self):
        pass
    def is_alive(self) -> bool:
        return False

def run_splash_subprocess() -> int:
    return 0
"""

if "class DummySplashController:" not in splash_text:
    splash_text = splash_text.replace("def run_splash_subprocess() -> int:", dummy_class + "\ndef _old_run_splash_subprocess() -> int:")
    splash_text = splash_text.replace("def create_splash(image_path: str = \"\", is_first_run: bool = False) -> SplashController:\n    return SplashController(image_path=image_path, is_first_run=is_first_run)", "def create_splash(image_path: str = \"\", is_first_run: bool = False):\n    return DummySplashController()")
    splash_text = splash_text.replace("def create_splash(image_path: str = \"\", is_first_run: bool = False) -> SplashController:\r\n    return SplashController(image_path=image_path, is_first_run=is_first_run)", "def create_splash(image_path: str = \"\", is_first_run: bool = False):\r\n    return DummySplashController()")
    with open("splash.py", "w", encoding="utf-8") as f:
        f.write(splash_text)
    print("splash.py updated")
else:
    print("splash.py already updated")

# 2. Update launch_dev.py
with open("launch_dev.py", "r", encoding="utf-8") as f:
    launch_text = f.read()

# Disable splash in launch_dev.py unconditionally
old_launch_pattern = "no_splash = is_headless or '--no-splash' in sys.argv"
new_launch_pattern = "no_splash = True  # Splash completely disabled as requested for instant startup"

if old_launch_pattern in launch_text:
    launch_text = launch_text.replace(old_launch_pattern, new_launch_pattern)
    with open("launch_dev.py", "w", encoding="utf-8") as f:
        f.write(launch_text)
    print("launch_dev.py updated")
else:
    print("launch_dev.py pattern not matched or already updated")
