import time, subprocess, signal, uuid, datetime, os
from xvfbwrapper import Xvfb
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class CampaignRecorder:
    def __init__(
        self,
        preview_url: str,
        width: int,
        height: int,
        loops: int = 1,
        target_fps: int = 24,
        compress: bool = False,
        timeout: int = 30,
    ) -> None:
        current_date = str(datetime.datetime.now().date())
        self.id = current_date + "-" + uuid.uuid4().hex
        self.preview_url = preview_url
        self.width = width
        self.height = height
        self.record_height = height + 55  # 55px is for Chrome's infobar;
        self.loops = loops
        self.target_fps = target_fps
        self.compress = compress
        self.timeout = timeout
        self.record_directory = "recordings"
        os.makedirs(self.record_directory, exist_ok=True)

    def __initialize_selenium(self) -> webdriver.Chrome:
        id = self.id
        width = self.width
        record_height = self.record_height
        options = webdriver.ChromeOptions()

        chrome_args = [
            "--mute-audio",
            "--disable-gpu",
            "--hide-scrollbars",
            "--disable-infobars",
            "--disable-web-security",
            "--disable-notifications",
            "--app=http://google.com",
            "--disable-site-isolation-trials",
            f"--window-size={width},{record_height}",
            f"--user-data-dir=/tmp/chrome/{id}",
            "--no-zygote",
            "--no-sandbox",
            "--enable-webgl",
            "--no-first-run",
            "--disable-breakpad",
            "--disable-canvas-aa",
            "--use-gl=swiftshader",
            "--disable-dev-shm-usage",
            "--disable-setuid-sandbox",
            "--disable-2d-canvas-clip-aa",
            "--disable-gl-drawing-for-tests",
        ]

        [options.add_argument(arg) for arg in chrome_args]
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def __wait_for_playcount_increase(self, driver: webdriver.Chrome, count: int = 1):
        timeout = self.timeout
        initial_time = int(time.time())
        script = "return window.PLAY_COUNT"
        first_count = int(driver.execute_script(script))
        while True:
            play_count = int(driver.execute_script(script))
            if play_count > first_count + (count - 1):
                break
            time.sleep(0.01)
            current_time = int(time.time())
            if play_count == first_count and (current_time - initial_time) > timeout:
                message = f"Timeout after {timeout} seconds"
                raise Exception(message)

    def __generate_local_preview_url(self) -> str:
        width = self.width
        height = self.height
        preview_url = self.preview_url

        base_url = "http://localhost:8000"
        preview_campaign_url = "/preview-campaign"
        url = base_url + preview_campaign_url + f"?preview_url={preview_url}&width={width}&height={height}"
        return url

    def record(self) -> str:
        target_fps = self.target_fps
        loop_count = self.loops
        width = self.width
        height = self.height
        compress = self.compress
        record_height = self.record_height
        record_directory = self.record_directory
        url = self.__generate_local_preview_url()

        vdisplay = Xvfb(width=width, height=record_height, colordepth=24)
        vdisplay.start()

        driver = self.__initialize_selenium()

        try:
            print("Navigating to: " + url)
            driver.get(url)

            self.__wait_for_playcount_increase(driver, count=1)

            filename = f"{self.id}.mp4"
            filepath = f"{record_directory}/{filename}"

            ffmpeg_stream_cmd = f"ffmpeg -y -r {target_fps} -f x11grab -s {width}x{record_height} -i :{vdisplay.new_display}+nomouse -draw_mouse 0 -filter:v crop={width}:{height}:0:{record_height - height} -an -c:v libx264rgb -preset:v ultrafast {filepath}"
            record_process = subprocess.Popen([str(x) for x in ffmpeg_stream_cmd.split(" ")])

            self.__wait_for_playcount_increase(driver, count=loop_count)

            record_process.send_signal(signal.SIGINT)
            time.sleep(2)

            driver.close()
            vdisplay.stop()

            if compress:
                new_filename = f"{self.id}-compressed.mp4"
                new_filepath = f"{record_directory}/{new_filename}"
                ffmpeg_compress_cmd = f"ffmpeg -y -an -i {filepath} -vcodec libx265 {new_filepath}"
                subprocess.run([str(x) for x in ffmpeg_compress_cmd.split(" ")])
                return new_filepath

            return filepath

        except Exception as e:
            driver.close()
            vdisplay.stop()
            raise e
