from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PIL import Image
from selenium.webdriver.firefox.options import Options 

# Configuration
URL = 'https://www.canyon.com/de-de/rennrad/race-rennrad/ultimate/cf-sl/ultimate-cf-sl-8-aero/3558.html?dwvar_3558_pv_rahmenfarbe=R101_P03'
CHECK_INTERVAL = 60  # Time between checks in seconds
EMAIL_ADDRESS = 'your-email@example.com'
EMAIL_PASSWORD = 'your-email-password'
RECIPIENT_EMAIL = 'recipient-email@example.com'

def has_stock(image_path, region):
    """
    Check if there are black pixels in the specified region of the image.

    :param image_path: Path to the image file
    :param region: A tuple (left, top, right, bottom) defining the region to check
    :return: True if there are black pixels, False otherwise
    """
    with Image.open(image_path) as img:
        # Crop the image to the defined region
        cropped_img = img.crop(region)
        cropped_img.save("cropped_stock_info.png")
        # Convert the cropped image to grayscale
        gray_img = cropped_img.convert("L")
        # Get the pixel data
        pixels = gray_img.load()

        # Check each pixel in the cropped region
        for x in range(cropped_img.width):
            for y in range(cropped_img.height):
                #print(f"X: {x}, Y: {y}, Value: {pixels[x, y]}")
                if pixels[x, y] < 50:  # <50 represents black in grayscale
                    return False
        return True

def check_website():
    options = Options() 
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    driver.get(URL)
    
    size_selectors = {"3XS":"1",
                      "2XS":"2",
                      "XS": "3",
                      "S": "4",
                      "M": "5",
                      "L": "6",
                      "XL": "7",
                      "XXL": "8",
                      }
    selector_preamble = "li.productConfiguration__optionListItem:nth-child("
    selector_postamble = ")"
    css_selectors = []



    for sel in size_selectors:
        css_selectors.append(selector_preamble + size_selectors[sel] + selector_postamble)

    

    # Adjust this wait time as needed for the content to load
    time.sleep(1)

    # Replace this selector with the one you copied
    elements = []
    availability = []
    img_region_of_interest = [180, 30, 190, 40]

    for i, sel in enumerate(css_selectors):
        try:
            element = driver.find_element(By.CSS_SELECTOR, sel)
            elements.append(driver.find_element(By.CSS_SELECTOR, sel))
            print(f"Found Size {i}")
            path_image = "stock_info.png"
            element.screenshot(path_image)
            availability.append(has_stock(path_image, img_region_of_interest))
        except:
            print(f"Did not find Size {i}")

    print(f"Availability: {availability}")

    driver.quit()
    return path_image

def send_email_notification(stock_status):
    subject = 'Product Back in Stock!'
    body = f'The product is now {stock_status}. Check it out at {URL}'
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, text)

def main():
    previous_status = None
    #:param region: A tuple (left, top, right, bottom) 
    #img_region_of_interest = [155, 15, 170, 30]
    img_region_of_interest = [180, 30, 190, 40]
    while True:
        image_path = check_website()
        size_has_stock = has_stock(image_path, img_region_of_interest)
        print(time.ctime(), end=" ")
        if  size_has_stock:
            print("Bike is available")
        else:
            print("Bike not available")

        
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main()
