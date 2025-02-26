from argparse import ArgumentParser
from bs4 import BeautifulSoup
from datetime import datetime
from random import random, randint
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep

URL_AUTH = "https://conjuguemos.com/auth/oauth2/google"
URL_VERB = "https://conjuguemos.com/verb/verb_chart/"
URL_VOCAB = "https://conjuguemos.com/vocabulary/vocab_chart/"

PRONOUNS = [
    ["yo"],
    ["tú"],
    ["él", "ella", "usted"],
    ["nosotros", "nosotras"],
    ["vosotros", "vosotras"],
    ["ellos", "ellas", "ustedes"]
]

start_time = datetime.utcnow()
find = lambda a, b: b.find(a) != -1

def log(message: str, level="INFO"):
    elapsed_time = datetime.utcnow() - start_time
    formatted_time = str(elapsed_time).split(".")[0] + "." + str(elapsed_time).split(".")[1][:3]
    print(f"[Hackasteis] [{formatted_time}] [{level}] {message}")

def pronoun_index(noun):
    if find(" y ", noun):
        if find("yo", noun): return 3
        if find("tú", noun): return 4
        else: return 5
    else:
        for i in range(len(PRONOUNS)):
            if noun in PRONOUNS[i]: return i
        return 2

if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-e", "--email", help="Email")
    parser.add_argument("-p", "--password", help="Password")
    parser.add_argument("-c", "--count", type=int, default=2147483647, help="Number of questions to answer")
    parser.add_argument("-a", "--accuracy", type=int, default=87, help="Accuracy percentage to achieve")
    args = parser.parse_args()

    driver = webdriver.Firefox()
    log("Drivers initialized")

    if args.email is not None and args.password is not None:
        driver.get(URL_AUTH)

        google_email = driver.find_element(by=By.ID, value="identifierId")
        google_email.send_keys(args.email)
        google_email.send_keys(Keys.ENTER)
        sleep(2.5)

        try:
            microsoft_email = driver.find_element(by=By.ID, value="i0116")
            microsoft_email.send_keys(args.email)
            microsoft_email.send_keys(Keys.ENTER)
            sleep(1.5)

            microsoft_password = driver.find_element(by=By.ID, value="i0118")
            microsoft_password.send_keys(args.password)
            microsoft_password.send_keys(Keys.ENTER)
            sleep(0.5)
        except:
            google_password = driver.find_elements(by=By.NAME, value="Passwd")[0]
            google_password.send_keys(args.password)
            google_password.send_keys(Keys.ENTER)
            sleep(0.5)
        
        try:
            driver.find_elements(By.CLASS_NAME, "VfPpkd-LgbsSe-OWXEXe-dgl2Hf")[0].click()
        except:
            pass
        log("Logged in")
    else:
        log("Email and password not provided, manual login is necessary", "WARNING")
    
    sleep(3.5)
    try:
        driver.find_elements(By.CLASS_NAME, "js-cookie-confirm-close")[0].click()
    except:
        pass
    log("Please navigate to the correct assignment")
    
    while True:
        try:
            driver.find_element(by=By.ID, value="practice").click()
            break
        except:
            sleep(0.25)

    url_sections = driver.current_url.split("/")
    assignment_type = url_sections[3]
    assignment_id = url_sections[5].split("#")[0]

    log("[1/3] Assignment URL parsed")

    if assignment_type == "verb":
        pronoun = driver.find_element(by=By.ID, value="pronoun-input")
        verb = driver.find_element(by=By.ID, value="verb-input")
    elif assignment_type == "vocabulary":
        noun = driver.find_element(by=By.ID, value="question-input")
    else:
        log("Invalid assignment URL, do you have the correct page open?", "ERROR")
        exit()
    
    try:
        answer = driver.find_element(by=By.ID, value="answer-input")
    except NoSuchElementException:
        try:
            answer = driver.find_element(by=By.ID, value="assignment-answer-input")
        except NoSuchElementException:
            log("Invalid assignment URL, do you have the correct page open?", "ERROR")
            exit()
    
    log("[2/3] Input fields parsed")
    
    if assignment_type == "verb":
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(f"{URL_VERB}{assignment_id}")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        verbs = {}

        for table in soup.find_all("table"):
            infinitive = table.find_parent().find_all(class_="fw--bold")[0].text.strip()
            chart = []
            for row in table.find_all("tr"):
                columns = row.find_all("td")
                chart.append(columns[1].text.strip())
                chart.append(columns[3].text.strip())
            verbs[infinitive] = [chart[0], chart[2], chart[4], chart[1], chart[3], chart[5]]
        
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
    elif assignment_type == "vocabulary":
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(f"{URL_VOCAB}{assignment_id}")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        vocab = {}

        for row in soup.find_all("tr"):
            columns = row.find_all("td")
            if columns[0].text.strip() == "Prompt": continue
            if columns[1].text.strip() == "Answer": continue
            vocab[" ".join(columns[0].text.strip().split()[1:])] = " ".join(columns[1].text.strip().split()[1:])
        
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
    
    log("[3/3] Answer data parsed")

    while True:
        if assignment_type == "verb" and pronoun.text != "" and verb.text != "":
            break
        elif assignment_type == "vocabulary" and noun.text != "":
            break
        sleep(0.25)

    i = 0
    if assignment_type == "verb":
        while i < args.count:
            if pronoun.text == "-" and verb.text == "-":
                break

            conjugation = verbs[verb.text][pronoun_index(pronoun.text)]
            log(f"[{i+1}/{args.count}] {pronoun.text} {verb.text} => {conjugation}")

            if random() * 100 < args.accuracy:
                answer.send_keys(conjugation)
                answer.send_keys(Keys.ENTER)

                try:
                    driver.find_element(by=By.CLASS_NAME, value="incorrect")
                    input("=== Incorrect answer, provide correct answer and press Enter ===")
                except:
                    pass
            else:
                x = randint(0, len(conjugation)-1)
                wrong = ''.join(c for c in conjugation if c not in "áéíóúÁÉÍÓÚ") if any(char in "áéíóúÁÉÍÓÚ" for char in conjugation) else conjugation[:x-1] + conjugation[x+1:]
                
                answer.send_keys(wrong)
                answer.send_keys(Keys.ENTER)

                answer.clear()
                answer.send_keys(conjugation)
                answer.send_keys(Keys.ENTER)

                try:
                    driver.find_element(by=By.CLASS_NAME, value="incorrect")
                    input("=== Incorrect answer, provide correct answer and press Enter ===")
                except:
                    pass
            
            i += 1

    elif assignment_type == "vocabulary":
        while i < args.count:
            if noun.text == "-":
                break

            translation = vocab[noun.text]
            log(f"[{i+1}/{args.count}] {noun.text} => {translation}")

            if random() * 100 < args.accuracy:
                answer.send_keys(translation)
                answer.send_keys(Keys.ENTER)

                try:
                    driver.find_element(by=By.CLASS_NAME, value="incorrect")
                    input("=== Incorrect answer, provide correct answer and press Enter ===")
                except:
                    pass
            else:
                x = randint(0, len(translation)-1)
                wrong = ''.join(c for c in translation if c not in "áéíóúÁÉÍÓÚ") if any(char in "áéíóúÁÉÍÓÚ" for char in translation) else translation[:x-1] + translation[x+1:]
                
                answer.send_keys(wrong)
                answer.send_keys(Keys.ENTER)

                answer.clear()
                answer.send_keys(translation)
                answer.send_keys(Keys.ENTER)

                try:
                    driver.find_element(by=By.CLASS_NAME, value="incorrect")
                    input("=== Incorrect answer, provide correct answer and press Enter ===")
                except:
                    pass

            i += 1
    
    input("=== Assignment complete, press Enter to terminate ===")

    driver.close()