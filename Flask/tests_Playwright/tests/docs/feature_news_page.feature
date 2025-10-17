Feature: News Page
  As a user
  I want to see the latest news updates
  So that I stay informed with fresh and relevant information

@TC008
Scenario: Display 5 news items when user visits the news page
  Given the user is on the news page
  Then the user sees 5 news items displayed

@TC009
Scenario: Display different 5 news items when user revisits the news page
  Given the user has visited the news page before
  When the user visits the news page again
  Then the user sees 5 news items displayed
  And the news items are different from the previous visit