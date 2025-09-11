
# Flask microsite for automate testing

This is a small project where i could show my enthusiasm about coding, testing and connecting things together.

You can check deployed page thanks to Render.com on the following link:
https://githubportfolio.onrender.com

Or you can run locally with docker, just download docker-compose-flask.yaml and run:

    docker-compose -f docker-compose-flask.yaml up -d

then open in browser:

    http://localhost:8000


Manual test documentation, userflow charts, decision tables coming in /testdocumentation folder

## Ready:
- microsite simulating a login, register and user settings with a live database connection. Passwords keep hashed in db of course. Minimal html and css handling with Bootstrap, just to don't hurt our eyes.
- update:add a basic webshop to the page with products, cart and checkout function. It gives more test object and more complex test cases.
- seed with AI generated dummy data, login credentials could find in /seed folder [users.csv](/Flask/seed/users.csv)

- Unit and other functional tests made with pytest
- Test results deployed on GitHub Pages with help of Allure. 
    Check it out at: https://koma-git.github.io/GithubPortfolio/Flask
- Automate tests made with Selenium, screenshot on fails, check allure report on the link above

## In progress... :
- Automate tests made with Playwright

## 🛠 Skills
Python, SQL, HTML, CSS, JS, Docker...
