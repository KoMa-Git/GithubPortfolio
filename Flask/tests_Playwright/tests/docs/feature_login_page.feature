Feature: Login Page
  As a user
  I want to login with my email, and password
  So that I can use the webshop

	Background:
  	Given the user is on the login page

@TC015
Scenario: Email field is required
	When the user enters a password and clicks "Submit" button
	Then the user sees an "Incorrect email or password!" notification

@TC016
Scenario: Password field is required
	When the user enters an email and clicks "Submit" button
	Then the user sees an "Incorrect email or password!" notification

@TC017
Scenario: User tries to login with invalid email
	When the user enters an invalid email and password
	And the user clicks the "Submit" button
	Then the user sees an "Incorrect email or password!" notification

@TC018
Scenario: User tries to login with invalid password
	When the user enters a valid email and invalid password
	And the user clicks the "Submit" button
	Then the user sees an "Incorrect email or password!" notification

@TC019
Scenario: Successful login
	When the user fills email and password
	And the user clicks the "Submit" button
	Then the user sees a "User logged in successful!" notification
	And the user is redirected to user page