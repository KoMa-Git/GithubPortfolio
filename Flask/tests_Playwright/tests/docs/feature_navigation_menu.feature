Feature: Navigation Menu
  As a user
  I want to use the navigation menu to go to different pages
  So that I can access site sections quickly and easily

@TC001
Scenario: Anonymous user sees correct navigation items and can navigate
  Given the user is not logged in
  When the user views the navigation menu
  Then the user sees menu items: "News", "Products", "Login"
  And the user sees the cart icon with item count
  But the user does not see menu items: "Logout", "User"
  
  When the user clicks on the "News" menu item
  Then the user is navigated to the news page
  
  When the user clicks on the "Products" menu item
  Then the user is navigated to the products page

  When the user clicks on the "Login" menu item
  Then the user is navigated to the login page

  When the user clicks on the cart icon
  Then the user is navigated to the cart page

@TC002
Scenario: Logged-in user sees correct navigation items and can navigate
  Given the user is logged in
  When the user views the navigation menu
  Then the user sees menu items: "News", "Products", "User", "Logout"
  And the user sees the cart icon with item count
  But the user does not see menu item: "Login"
  
  When the user clicks on the "News" menu item
  Then the user is navigated to the news page
  
  When the user clicks on the "Products" menu item
  Then the user is navigated to the products page

  When the user clicks on the "User" menu item
  Then the user is navigated to the user profile page

  When the user clicks on the "Logout" menu item
	Then user sees a "User successfully logged out" notification
  And the user is navigated to the login page

  When the user clicks on the cart icon
  Then the user is navigated to the cart page