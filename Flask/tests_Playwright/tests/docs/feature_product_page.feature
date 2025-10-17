Feature: Products page
  As a shopper,
  I want to view a list of available products
  So that I can browse and add items to my cart.

  Background:
    Given the user is on the products page
    And the user sees a list of products

@TC003A
Scenario: Add item to cart
  When the user clicks the "Add to cart" button on a product card
  Then the user sees an "Added product to cart" notification
  And the cart badge number increases by 1

@TC003B
Scenario: Add all visible products to the cart
  When the user adds each visible product to the cart
  Then each product should be added successfully
  And the user sees an "Added product to cart" notification for each product
  And the cart badge number increases accordingly