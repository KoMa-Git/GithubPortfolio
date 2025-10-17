
# Flask microsite for manual and automate testing

Test cases made from User Journeys you can reach at: https://koma-git.github.io/GithubPortfolio/TestCases/

Test reports deployed on Github pages.

**Playwright test report**: <br>
https://koma-git.github.io/GithubPortfolio/Playwright/ <br>
Github action build webshop from docker then runs playwright tests, finally upload on GH pages <br>
Test files available in [tests_Playwright](/Flask/tests_Playwright/tests/) folder.

**Pytest and Selenium test report made with Allure**: <br>
https://koma-git.github.io/GithubPortfolio/Flask/ <br>
Not following full test documentation above. Selenium makes just few UI tests from these test cases. <br>
Plus there are unittests and a user journey from register to delete account using pytest. <br>
Test files available in [tests_Playwright](/Flask/tests_Selenium/) folder. <br>

## Beyond testing its a Flask learning project:

Its a basic webshop imitation. There are login, register, user settings, products, cart pages with limited functions and a live database connection. Minimal html and css handling with Bootstrap. AI generated product images, descriptions.

You can check deployed page thanks to Render.com on the following link:
https://githubportfolio.onrender.com
Please note its a free service, startup could take 50 seconds.

Or you can run locally with docker, just download docker-compose-flask.yaml and run:
    docker-compose -f docker-compose-flask.yaml up -d

then open in browser:
    http://localhost:8000

## 🛠 Skills
Python, Typescript, SQL, HTML, CSS, JS, Docker
