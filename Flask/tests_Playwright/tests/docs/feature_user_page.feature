Feature: User Page
  As a logged-in user  
  I want to update my username or password, view my order history, or delete my account  
  So that I can manage my personal information and keep track of my purchases

	Background:
		Given the user is on the user page

@TC020 
Scenario: Change username
	When the user clicks the edit icon next to the username
	And enters a new username
	And confirms the changes
	Then the user sees a "New name was saved" notification
	And the updated username is displayed on the user page

@TC021A
Scenario: Successfully change password
	When the user clicks the "Change password" button
	And enters valid old password and new password
	And confirms the changes 
	Then the user sees a "Password has changed" notification
	And user password has changed

@TC021B
Scenario: Missing new password
	When the user clicks the "Change password" button
	And enters valid old password
	And confirms the changes
	Then the user sees a "Password fields cannot be empty!" notification

@TC021C
Scenario: Missing old password
	When the user clicks the "Change password" button
	And enters new password
	And confirms the changes
	Then the user sees a "Password fields cannot be empty!" notification

@TC021D
Scenario: Invalid old password 
	When the user clicks the "Change password" button
	And enters an invalid old password and a valid new password
	And confirms the changes 
	Then the user sees a "Your old password is not valid" notification

@TC022A  
Scenario: View order history when user has previous orders  
  Given a user with order history  
  When the user clicks on the "Previouse orders" button  
  Then the order history list is displayed  

@TC022B  
Scenario: No "Previous orders" button shown when user has no previous orders  
  Given a user without any previous orders  
  Then the "Orders" button is not visible on the user page

@TC023A  
Scenario: Successfully delete account  
  When the user clicks the "Delete account" button  
  And types "DELETE" into the confirmation input field  
  And confirms the deletion  
  Then the user sees an "Account deleted successfully" notification  
  And the user is logged out and redirected to the home page  

@TC023B  
Scenario: Incorrect confirmation prevents account deletion  
  When the user clicks the "Delete account" button  
  And types an incorrect confirmation text into the input field  
  And confirms the deletion  
  Then the user sees a "You didn't type DELETE correctly" notification  
  And the account is not deleted 