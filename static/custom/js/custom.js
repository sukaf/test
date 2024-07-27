document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('modal');
    const variationsContainer = document.getElementById('variations-container');
    const articleVariations = JSON.parse(document.getElementById('article-variations').textContent);
    let isAddingToCart = false;
    let isRemovingFromCart = false;

    function initializeCartButtons() {
        const cartButtons = document.querySelectorAll('.cart-button');
        cartButtons.forEach(button => {
            const articleId = button.getAttribute('data-article-id');
            fetch(`/cart/check/${articleId}/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                updateCartButton(articleId, data.in_cart);
            })
            .catch(error => {
                console.error('Error checking cart:', error);
            });
        });
    }

    initializeCartButtons();

    document.addEventListener('click', function(event) {
        if (!isAddingToCart && !isRemovingFromCart) {
            if (event.target.classList.contains('openBtn')) {
                event.stopImmediatePropagation();
                const articleId = event.target.getAttribute('data-article-id');
                const variations = articleVariations[articleId];

                if (variations && variations.length > 0) {
                    variationsContainer.innerHTML = variations.map(variation => `
                        <div>
                            <input type="radio" name="variation" value="${variation.id}" id="variation-${variation.id}">
                            <label for="variation-${variation.id}">
                                <img src="${variation.image_url}" alt="${variation.name}" style="width: 50px; height: 50px;">
                                ${variation.name} - ${variation.price}
                            </label>
                        </div>
                    `).join('');
                    document.getElementById('btn-add-to-cart-dialog').setAttribute('data-article-id', articleId); // добавляем атрибут data-article-id кнопке
                    modal.showModal();
                } else {
                    isAddingToCart = true;
                    disableButton(event.target);
                    addToCart(null, articleId)
                        .then(data => {
                            updateCartButton(articleId, true);
                            updateCart(data.total_quantity, data.total_price, data.cart_items);
                            updateButtonsOnOtherPages(articleId, true);
                        })
                        .catch(error => {
                            console.error('Error adding to cart:', error);
                        })
                        .finally(() => {
                            isAddingToCart = false;
                            enableButton(event.target);
                        });
                }
            } else if (event.target.id === 'btn-add-to-cart-dialog') {
                event.stopImmediatePropagation();
                const selectedVariation = document.querySelector('input[name="variation"]:checked');
                const variationId = selectedVariation ? selectedVariation.value : null;
                const articleId = event.target.getAttribute('data-article-id'); // получаем articleId

                if (variationId) {
                    isAddingToCart = true;
                    disableButton(event.target);
                    addToCart(variationId, articleId)
                        .then(data => {
                            modal.close();
                            updateCart(data.total_quantity, data.total_price, data.cart_items);
                            updateCartButton(articleId, true); // обновление кнопки после закрытия модального окна
                        })
                        .catch(error => {
                            console.error('Error adding to cart:', error);
                        })
                        .finally(() => {
                            isAddingToCart = false;
                            enableButton(event.target);
                        });
                }
            } else if (event.target.id === 'closeBtn') {
                event.stopImmediatePropagation();
                modal.close();
            } else if (event.target.classList.contains('btn-add-to-cart')) {
                event.stopImmediatePropagation();
                const articleId = event.target.getAttribute('data-article-id');
                isRemovingFromCart = true;
                disableButton(event.target);
                removeFromCart(articleId)
                    .then(data => {
                        updateCartButton(articleId, false);
                        updateCart(data.total_quantity, data.total_price, data.cart_items);
                        updateButtonsOnOtherPages(articleId, false);
                    })
                    .catch(error => {
                        console.error('Error removing from cart:', error);
                    })
                    .finally(() => {
                        isRemovingFromCart = false;
                        enableButton(event.target);
                    });
            }
        }
    });

    function disableButton(button) {
        button.disabled = true;
    }

    function enableButton(button) {
        button.disabled = false;
    }

    function updateCartButton(articleId, inCart) {
        const button = document.querySelector(`.cart-button[data-article-id="${articleId}"] button`);
        if (!button) {
            console.error('Button not found for article_id:', articleId);
            return;
        }
        if (inCart) {
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
    }

    function updateCart(totalQuantity, totalPrice, cartItems) {
        const cartCountElement = document.getElementById('cart-count');
        const cartTotalPriceElement = document.getElementById('cart-total-price');
        const cartItemsContainer = document.getElementById('cart-items');

        if (cartCountElement) {
            cartCountElement.textContent = totalQuantity;
        }
        if (cartTotalPriceElement) {
            cartTotalPriceElement.textContent = totalPrice;
        }
        if (cartItemsContainer) {
            cartItemsContainer.innerHTML = '';
            cartItems.forEach(item => {
                const itemElement = document.createElement('li');
                itemElement.innerHTML = `
                    <h2>${item.title}</h2>
                    ${item.thumbnail ? `<img src="${item.thumbnail}" alt="${item.title}" width="100">` : ''}
                    <p>${item.variation_name}</p>
                    <p>Цена: ${item.price} руб.</p>
                    <p>Количество: ${item.quantity}</p>
                    <p>Общая стоимость: ${item.total_price} руб.</p>
                `;
                cartItemsContainer.appendChild(itemElement);
            });
        }
    }

    function addToCart(variationId, articleId = null) {
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
});






