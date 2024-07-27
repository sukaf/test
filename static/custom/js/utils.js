function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function updateCart(totalQuantity, totalPrice, cartItems, totalDiscount = 0) {
    document.getElementById('total_quantity').innerText = totalQuantity;
    document.getElementById('total_price').innerText = totalPrice + ' ₽';
    document.getElementById('total_discount').innerText = `-${totalDiscount} ₽`;

    const cartCounter = document.getElementById('cart-count');
    if (cartCounter) {
        cartCounter.innerText = totalQuantity;
    }

    const cartItemsContainer = document.getElementById('cart-items');
    if (cartItemsContainer) {
        cartItemsContainer.innerHTML = '';
        cartItems.forEach(item => {
            const itemElement = document.createElement('li');
            itemElement.classList.add('cart-item-summary');
            itemElement.innerHTML = `
                <div class="cart-item-details-summary">
                    <p>${item.title}</p>
                    <p>${item.price} ₽</p>
                </div>
            `;
            cartItemsContainer.appendChild(itemElement);
        });
    }
}

function removeFromCart(articleId) {
    return fetch(`/cart/remove/${articleId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    });
}

function addToCart(articleId, variationId = null) {
    const bodyData = variationId ? `variation_id=${variationId}` : `article_id=${articleId}`;
    return fetch('/cart/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: bodyData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    });
}


function updateButtonsOnOtherPages(articleId, isInCart) {
    const buttons = document.querySelectorAll(`[data-article-id="${articleId}"] button`);
    buttons.forEach(button => {
        if (isInCart) {
            button.classList.add('btn-secondary');
            button.classList.remove('btn-primary');
            button.textContent = 'Добавлено';
            button.classList.remove('openBtn');
            button.classList.add('btn-add-to-cart');
        } else {
            button.classList.remove('btn-secondary');
            button.classList.add('btn-primary');
            button.textContent = 'Добавить в корзину';
            button.classList.add('openBtn');
            button.classList.remove('btn-add-to-cart');
        }
    });
}


