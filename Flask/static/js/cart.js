// add to cart function with AJAX
function addToCart(productId) {
  fetch('/add_to_cart', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    },
    body: JSON.stringify({ product_id: productId })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      showNotification(data.message);

      // update cart badge
      const cartBadge = document.getElementById('cart-count');
      if (cartBadge) {
          cartBadge.innerText = data.cartItemCount;
      }
    } else {
        showNotification(data.message, 'error');
    }
  })
  .catch(error => {
      console.error('Error:', error);
  });
}

// update cart function with AJAX. Could increase, decrease or set a specific quantity
function updateCart(productId, action, quantity = null) {
  const payload = { product_id: productId, action: action };
  if (action === 'set') {
      payload.quantity = quantity;
  }

  fetch('/update_cart', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === "success") {
      const item = data.cart[productId];
      if (item) {
          document.getElementById('qty-input-' + productId).value = item.quantity;
          document.getElementById('total-' + productId).textContent =
              (item.price * item.quantity).toFixed(2) + " €";
      } else {
          document.getElementById('row-' + productId)?.remove();
      }

      const cartBadge = document.getElementById('cart-count');
        if (cartBadge) {
            cartBadge.innerText = data.cartItemCount;
        }
      updateTotal();
      showNotification(data.message);
    } else {
        showNotification(data.message || "Something went wrong.");
    }
    });
}

// update total price on cart page
function updateTotal() {
    let totalPrice = 0;
    
    // Iterate through all cart items total and add them
    document.querySelectorAll('.total-line').forEach(item => {
        totalPrice += parseFloat(item.textContent);
    });
    
    document.getElementById('end-total').innerHTML = "<strong>" + totalPrice.toFixed(2) + " €</strong>";
    
}

// add function to cart page:
// if user types amount and 500ms pass from last keystroke then update quantity
// plus dinamically change input field width according how many characters are in it
let debounceTimers = {};

document.querySelectorAll('.qty-input').forEach(input => {
  // change input width to actual length plus 1 character
  input.style.width = `${input.value.length + 1}ch`;

  // add eventlistener to all input
  input.addEventListener('input', () => {
    // if there is a change in character length then change input width
    input.style.width = `${input.value.length + 1}ch`;

    // take data- element from input
    const productId = input.dataset.productId;

    // clear timer, cancel any pending update for that particular product ID
    clearTimeout(debounceTimers[productId]);

    debounceTimers[productId] = setTimeout(() => {
      const qty = parseInt(input.value);
      if (!isNaN(qty)) {
          updateCart(productId, 'set', qty);
          
      }
  }, 500);
  });
});

// show notification on success response on addToCart and updateCart
function showNotification(message, type = 'success') {
  const notif = document.createElement('div');
  notif.className = 'notification ' + type;
  notif.innerText = message;
  document.body.appendChild(notif);

  setTimeout(() => {
    notif.remove();
  }, 2000);
}