from selenium import webdriver
import time
from load_model import load_model
from utils import stringToRGB
from decode_captcha import decode
import signal
from contextlib import contextmanager


@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


USERNAME = "20173749"
PASSWORD = "164657188"
URL = "https://dk-sis.hust.edu.vn/Users/Login.aspx"


def login():

    model = load_model()

    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    driver = webdriver.Chrome(
        executable_path='/home/tuhalang/Documents/Python/auto_register/chromedriver')  # ,chrome_options=options)
    driver.set_script_timeout(10)

    driver.get(URL)
    time.sleep(0.5)

    driver.find_element_by_xpath('//*[@id="tbUserName"]').send_keys(USERNAME)
    # time.sleep(0.5)

    current_url = URL
    while current_url == URL:
        captcha_code = ""
        try:
            with time_limit(1):
                ele_captcha = driver.find_element_by_xpath(
                    '//*[@id="ccCaptcha_IMG"]')
                # get the captcha as a base64 string
                img_captcha_base64 = driver.execute_async_script("""
                        var ele = arguments[0], callback = arguments[1];
                        ele.addEventListener('load', function fn(){
                        ele.removeEventListener('load', fn, false);
                        var cnv = document.createElement('canvas');
                        cnv.width = this.width; cnv.height = this.height;
                        cnv.getContext('2d').drawImage(this, 0, 0);
                        callback(cnv.toDataURL('image/png').substring(22));
                        }, false);
                        ele.dispatchEvent(new Event('load'));
                        """, ele_captcha)
                image = stringToRGB(img_captcha_base64)
                captcha_code = decode(image, model)
        except Exception as e:
            print(e)
        driver.find_element_by_xpath('//*[@id="tbPassword_CLND"]').click()
        driver.find_element_by_xpath(
            '//*[@id="tbPassword"]').send_keys(PASSWORD)
        driver.find_element_by_xpath(
            '//*[@id="ccCaptcha_TB_I"]').send_keys(captcha_code)
        driver.find_element_by_xpath('//*[@id="ctl01"]/p[4]/button').click()
        time.sleep(0.5)
        current_url = driver.current_url
    return driver


def main():
    driver = login()
    pass


if __name__ == '__main__':
    main()

			
