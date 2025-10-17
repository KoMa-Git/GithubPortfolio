Feature: Register Page
  As a new user
  I want to fill out the registration form with my name, email, and password
  So that I can create an account and use the webshop

  Background:
    Given the user is on the register page

@TC010
Scenario: Name field is required
  When the user fills in "jane@example.com" in the email field
  And the user fills in "securePass123" in the password field
  And the user clicks the "submit" button
  Then the user sees an error message "All fields are required"

@TC011
Scenario: Email field is required
  When the user fills in "Jane" in the name field
  And the user fills in "securePass123" in the password field
  And the user clicks the "submit" button
  Then the user sees an error message "All fields are required"

@TC012
Scenario: Password field is required
  When the user fills in "Jane" in the name field
  And the user fills in "jane@example.com" in the email field
  And the user clicks the "submit" button
  Then the user sees an error message "All fields are required"

@TC013
Scenario: Invalid email format
  When the user fills in "John Doe" in the name field
  And the user fills in "invalid-email" in the email field
  And the user fills in "secret123" in the password field
  And the user clicks the "submit" button
  Then the user sees an error message "Enter a valid email address"
  And cursor is active at email field
  And the registration does not proceed

@TC014
Scenario: Successful registration
  When the user fills in "Jane Smith" in the name field
  And the user fills in "jane@example.com" in the email field
  And the user fills in "securePass123" in the password field
  And the user clicks the "submit" button
  Then the user is redirected to the login page
  And the user sees a "Registered successfully! Please login." notification 