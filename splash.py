"""splash.py — Splash Screen สำหรับ Broadcast Playroom 3 (PySide6)

- สัดส่วนภาพกว้าง 500px x สูงตาม ratio (500x282)
- Zero GPU Freeze: ทำงานบน Subprocess แยก ทำให้ Animation ลื่นไหล 60 FPS เสมอ
- Border Chase Capsule: ลำแสงหมุนรอบกรอบแสดงสถานะการโหลดอย่างสวยงาม
- Base64 IPC: ป้องกันปัญหาการเข้ารหัสภาษาไทยบน Windows คมชัด ไม่เป็นภาษาต่างดาว
- ปิดอัตโนมัติเมื่อหน้าต่างหลักของโปรแกรมพร้อมทำงาน
"""
from __future__ import annotations

import os
import sys
import time
import base64
import threading
import subprocess
import logging
from typing import Optional

logger = logging.getLogger("splash")


def get_default_splash_image() -> str:
    bases = []
    if hasattr(sys, "_MEIPASS"):
        bases.append(sys._MEIPASS)
        bases.append(os.path.join(sys._MEIPASS, "src"))
    exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    bases.append(exe_dir)
    bases.append(os.path.join(exe_dir, "_internal"))
    bases.append(os.path.join(exe_dir, "_internal", "src"))
    base_dir = os.path.dirname(os.path.abspath(__file__))
    bases.append(base_dir)
    bases.append(os.path.join(base_dir, "src"))

    for b in bases:
        for sub in ("assets/splash/splash_500.png", "assets/splash/splash_raw.png", "src/assets/splash/splash_500.png"):
            cand = os.path.normpath(os.path.join(b, sub))
            if os.path.exists(cand):
                return cand
    return ""


class BorderChaseCapsule:
    pass  # Defined inside PySide6 scope


def run_splash_subprocess() -> int:
    """Entry point สำหรับ Subprocess ของ Splash Screen"""
    import argparse
    from PySide6.QtWidgets import (
        QApplication,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QLabel,
    )
    from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QPen, QColor, QFont
    from PySide6.QtCore import Qt, QTimer, QRectF, QObject, Signal

    if hasattr(sys.stdin, "reconfigure"):
        try:
            sys.stdin.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="Broadcast Playroom 3 Splash Subprocess")
    parser.add_argument("--splash-subprocess", action="store_true")
    parser.add_argument("--image", type=str, default="")
    parser.add_argument("--first-run", action="store_true")
    parser.add_argument("--save-screenshot", type=str, default="")
    args, _ = parser.parse_known_args()

    app = QApplication(sys.argv)
    app.setApplicationName("Broadcast Playroom 3")
    try:
        from PySide6.QtGui import QIcon
        from app_window_frame import find_app_icon_path
        ico = find_app_icon_path()
        if ico and os.path.exists(ico):
            app.setWindowIcon(QIcon(ico))
    except Exception:
        pass

    img_path = args.image or get_default_splash_image()

    class CapsuleWidget(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setAttribute(Qt.WA_TranslucentBackground, True)
            self._offset = 0.0
            self._beam_len = 110.0
            self._pen_w = 2.5
            self._speed = 135.0
            self._last_time = time.perf_counter()

            self._timer = QTimer(self)
            self._timer.timeout.connect(self._step)
            self._timer.start(16)

            layout = QVBoxLayout(self)
            layout.setContentsMargins(18, 10, 18, 10)
            layout.setSpacing(0)
            self._inner_layout = layout

        def set_content_layout(self, cl):
            self._inner_layout.addLayout(cl)

        def _step(self):
            now = time.perf_counter()
            dt = now - self._last_time
            self._last_time = now
            if dt > 0.1:
                dt = 0.016
            self._offset += self._speed * dt
            self.update()

        def stop(self):
            if self._timer.isActive():
                self._timer.stop()

        def paintEvent(self, event):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            w = float(self.width())
            h = float(self.height())
            m = self._pen_w / 2.0
            rect = QRectF(m + 1, m + 1, w - (2 * m + 2), h - (2 * m + 2))
            radius = 12.0

            bg_path = QPainterPath()
            bg_path.addRoundedRect(rect, radius, radius)
            painter.fillPath(bg_path, QColor(15, 23, 42, 245))

            track_pen = QPen(QColor(30, 41, 59, 220), self._pen_w)
            painter.strokePath(bg_path, track_pen)

            total_len = bg_path.length()
            if total_len > 0:
                beam_dash = self._beam_len / self._pen_w
                space_dash = max(1.0, (total_len - self._beam_len) / self._pen_w)
                chase_pen = QPen(QColor(56, 189, 248), self._pen_w)
                chase_pen.setCapStyle(Qt.RoundCap)
                chase_pen.setDashPattern([beam_dash, space_dash])
                chase_pen.setDashOffset(self._offset / self._pen_w)
                painter.strokePath(bg_path, chase_pen)

    class SplashWindow(QWidget):
        def __init__(self, image_path: str, is_first_run: bool = False):
            super().__init__()
            self.setWindowFlags(
                Qt.FramelessWindowHint | Qt.Window
            )
            self.setAttribute(Qt.WA_TranslucentBackground, True)
            self.is_first_run = is_first_run

            layout = QVBoxLayout(self)
            layout.setContentsMargins(12, 12, 12, 12)
            layout.setSpacing(10)

            # 1. ภาพ Splash สัดส่วน 500px
            self.img_lbl = QLabel()
            self.img_lbl.setAlignment(Qt.AlignCenter)
            if image_path and os.path.exists(image_path):
                pix = QPixmap(image_path)
                if not pix.isNull():
                    if pix.width() != 500:
                        pix = pix.scaledToWidth(500, Qt.SmoothTransformation)
                    self.img_lbl.setPixmap(pix)
            layout.addWidget(self.img_lbl)

            # 2. แคปซูลแสดงสถานะการโหลด
            self.capsule = CapsuleWidget()
            text_layout = QHBoxLayout()
            text_layout.setContentsMargins(0, 0, 0, 0)
            text_layout.setAlignment(Qt.AlignCenter)

            default_msg = (
                "กำลังเตรียมการจากการเปิดครั้งแรก..."
                if self.is_first_run
                else "กำลังเริ่มต้นระบบ Broadcast Playroom..."
            )
            self.status_lbl = QLabel(default_msg)
            self.status_lbl.setAlignment(Qt.AlignCenter)
            self.status_lbl.setStyleSheet("""
                font-size: 13px;
                font-weight: 600;
                color: #f1f5f9;
                background: transparent;
                font-family: 'Segoe UI', 'Noto Sans Thai', Tahoma, sans-serif;
            """)
            text_layout.addWidget(self.status_lbl)
            self.capsule.set_content_layout(text_layout)
            layout.addWidget(self.capsule)

            self.adjustSize()
            self._center()

        def _center(self):
            screen = QApplication.primaryScreen()
            if screen:
                geo = screen.availableGeometry()
                x = geo.x() + (geo.width() - self.width()) // 2
                y = geo.y() + (geo.height() - self.height()) // 2
                self.move(x, y)

        def set_progress(self, percent: int, text: str):
            if text:
                self.status_lbl.setText(text)
            qapp = QApplication.instance()
            if qapp:
                qapp.processEvents()

        def finish(self):
            try:
                self.capsule.stop()
                self.close()
                self.deleteLater()
            except Exception:
                pass

    splash = SplashWindow(img_path, args.first_run)
    splash.show()

    if args.save_screenshot:
        QTimer.singleShot(300, lambda: splash.grab().save(args.save_screenshot))

    class Bridge(QObject):
        update_progress = Signal(int, str)
        should_close = Signal()

    bridge = Bridge()
    bridge.update_progress.connect(splash.set_progress)
    bridge.should_close.connect(lambda: (splash.finish(), app.quit()))

    # Watchdog safety timer: auto-close splash after 7s max under any circumstances
    QTimer.singleShot(7000, lambda: (splash.finish(), app.quit()))

    def listen_stdin():
        try:
            while True:
                line = sys.stdin.readline()
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue
                if line == "CLOSE":
                    break
                elif line.startswith("PROGRESS:"):
                    parts = line.split(":", 2)
                    pct = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
                    txt = ""
                    if len(parts) > 2 and parts[2]:
                        raw = parts[2]
                        try:
                            txt = base64.b64decode(raw.encode("ascii")).decode("utf-8")
                        except Exception:
                            txt = raw
                    bridge.update_progress.emit(pct, txt)
        except Exception:
            pass
        bridge.should_close.emit()

    t = threading.Thread(target=listen_stdin, daemon=True)
    t.start()

    return app.exec()


class SplashController:
    """Controller สำหรับเรียกใช้งาน Splash Screen ในโปรแกรมหลักผ่าน Subprocess"""

    def __init__(self, image_path: str = "", is_first_run: bool = False):
        self.image_path = image_path or get_default_splash_image()
        self.is_first_run = is_first_run
        self.proc: Optional[subprocess.Popen] = None
        self._start_process()

    def _start_process(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if getattr(sys, "frozen", False):
            cmd = [sys.executable, "--splash-subprocess"]
        else:
            cmd = [
                sys.executable,
                "-u",
                os.path.join(base_dir, "splash.py"),
                "--splash-subprocess",
            ]
        if self.image_path and os.path.exists(self.image_path):
            cmd.extend(["--image", os.path.abspath(self.image_path)])
        if self.is_first_run:
            cmd.append("--first-run")

        creationflags = 0
        if sys.platform == "win32":
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        try:
            self.proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
                encoding="utf-8",
                cwd=base_dir,
                env=env,
                creationflags=creationflags,
            )
        except Exception as e:
            logger.warning(f"Failed to launch splash subprocess: {e}")
            self.proc = None

    def set_progress(self, percent: int, text: str = ""):
        if not self.proc or self.proc.poll() is not None:
            return
        try:
            safe_text = (text or "").replace("\n", " ").strip()
            b64_text = base64.b64encode(safe_text.encode("utf-8")).decode("ascii")
            self.proc.stdin.write(f"PROGRESS:{percent}:{b64_text}\n")
            self.proc.stdin.flush()
        except Exception:
            pass

    def finish(self):
        if not self.proc:
            return
        p = self.proc
        self.proc = None
        try:
            if p.poll() is None:
                try:
                    p.stdin.write("CLOSE\n")
                    p.stdin.flush()
                    p.stdin.close()
                except Exception:
                    pass
                try:
                    p.wait(timeout=0.3)
                except Exception:
                    pass
                if p.poll() is None:
                    p.kill()
        except Exception:
            try:
                p.kill()
            except Exception:
                pass

    def close(self):
        self.finish()


def create_splash(image_path: str = "", is_first_run: bool = False) -> SplashController:
    return SplashController(image_path=image_path, is_first_run=is_first_run)


if __name__ == "__main__":
    if "--splash-subprocess" in sys.argv:
        sys.exit(run_splash_subprocess())
    else:
        # Quick test run
        ctrl = create_splash()
        time.sleep(1.0)
        ctrl.set_progress(30, "กำลังเริ่มต้นเซิร์ฟเวอร์ระบบ...")
        time.sleep(1.0)
        ctrl.set_progress(70, "กำลังโหลดการตั้งค่า...")
        time.sleep(1.0)
        ctrl.set_progress(100, "พร้อมใช้งาน!")
        time.sleep(0.8)
        ctrl.finish()
