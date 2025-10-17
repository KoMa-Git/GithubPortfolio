
# Flask microsite for manual and automate testing

Test cases made from User Journeys you can reach at: https://koma-git.github.io/GithubPortfolio/TestCases/

Test reports deployed on Github pages.

**Playwright test report**: 
https://koma-git.github.io/GithubPortfolio/Playwright/
github action build webshop from docker then runs playwright tests, finally upload on GH pages
test files available in [tests_Playwright](/Flask/tests_Playwright/tests/) folder.

**Pytest and Selenium test report made with Allure**: 
https://koma-git.github.io/GithubPortfolio/Flask/
| not following full test documentation above. Selenium makes just few UI tests from these test cases.
| Plus there are unittests and a user journey from register to delete account using pytest.
| test files available in [tests_Playwright](/Flask/tests_Selenium/) folder.

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
