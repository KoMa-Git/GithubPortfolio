Feature: Cart page
	This feature allows users to manage the items in their shopping cart,
  including increasing, decreasing, and changing item quantities.

@TC004
Scenario: Increase item quantity in cart
	Given the user is on the cart page with products in the cart
  When the user clicks the "+" button next to a product
  Then the product quantity increases by 1 in the cart
  And the user sees a "Cart updated" notification
  And the total cost increases by the product price
  And the cart badge number increases by 1

@TC005
Scenario: Decrease item quantity in cart
	Given the user is on the cart page with products in the cart
  When the user clicks the "-" button next to a product
  Then the product quantity decreases by 1 in the cart
  And the user sees a "Cart updated" notification
  And the total cost decreases by the product price
  And the cart badge number decreases by 1

@TC006
Scenario: Remove product from cart when only 1 item is left
  Given the user is on the cart page with 1 quantity of a product in the cart
  When the user clicks the "-" button next to that product
  Then the product is removed from the cart
  And the user sees a "Product deleted from cart" notification
	And the total cost is 0
  And the cart badge number is 0

@TC007A
Scenario: Update product quantity with a valid number
	Given the user is on the cart page with products in the cart
  When the user enters a valid number greater than 0 in the quantity input field next to a product
  Then the product quantity is updated to that number
  And the user sees a "Cart updated" notification
  And the total cost updates accordingly
  And the cart badge number reflects the total quantity

@TC007B
Scenario: Remove product by setting quantity to 0
  Given the user is on the cart page with products in the cart
  When the user enters 0 in the quantity input field next to a product
  Then the product is removed from the cart
  And the user sees a "Cart updated" notification
  And the total cost updates accordingly
  And the cart badge number decreases accordingly

@TC007C
Scenario: Enter negative quantity — system corrects to positive
  Given the user is on the cart page with products in the cart
  When the user enters "-3" in the quantity input field next to the product
  Then the cart updates the product amount to "3"
  And the user gets a "Cart updated" notification
  And the total cost is updated based on quantity "3"
  And the cart badge number shows "3"
	
@TC007D
Scenario: Reject non-numeric input in quantity field
  Given the user is on the cart page with products in the cart
  When the user enters a non-numeric value (e.g., letters or symbols) in the quantity input field
  Then the input is rejected
  And the product quantity remains unchanged