import platform
import os
import subprocess

from loguru import logger


def is_headless():
    system = platform.system()

    # Linux/macOS
    if system in ["Linux", "Darwin"]:
        # 1. Check display server
        if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
            logger.info("Headless check: neither DISPLAY nor WAYLAND_DISPLAY is set.")
            return True

        # 2. Check session type
        if os.environ.get("XDG_SESSION_TYPE") == "tty":
            logger.info("Headless check: XDG_SESSION_TYPE='tty' detected.")
            return True

        # 3. Check SSH
        if os.environ.get("SSH_CLIENT") and not os.environ.get("DISPLAY"):
            logger.info("Headless check: SSH_CLIENT is present but DISPLAY is absent")
            return True

        # 4. Check by command
        try:
            result = subprocess.run(
                ["xset", "q"],  # Run X11 command, returns != 0 if headless
                capture_output=True,
                timeout=1
            )
            if result.returncode != 0:
                logger.info(f"Headless check: 'xset q' failed (rc={result.returncode}).")
                return True
        except FileNotFoundError:
            logger.info("Headless check: 'xset' not found—assuming no X11.")
            return True
        except subprocess.TimeoutExpired:
            logger.info("Headless check: 'xset q' timed out—assuming no X11.")
            return True

    # Windows
    elif system == "Windows":
        # Server Core or SSH session?
        import ctypes
        width = ctypes.windll.user32.GetSystemMetrics(0)  # SM_CXSCREEN
        if width == 0:
            logger.info("Headless check: GetSystemMetrics(0) == 0 (no screen).")
            return True

    return False

if is_headless():
    logger.info("Zerolan Live Robot: GUI disabled.")
else:
    logger.info("Zerolan Live Robot: GUI enabled.")