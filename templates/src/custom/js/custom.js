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
                updateCartButton(articleId, data.in_cart, data.already_purchased);
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
                    document.getElementById('btn-add-to-cart-dialog').setAttribute('data-article-id', articleId);
                    modal.showModal();
                } else {
                    isAddingToCart = true;
                    disableButton(event.target);
                    addToCart(null, articleId)
                        .then(data => {
                            updateCartButton(articleId, true, false);
                            updateCart(data.total_quantity, data.total_price, data.cart_items);
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
                const articleId = event.target.getAttribute('data-article-id');

                if (variationId) {
                    isAddingToCart = true;
                    disableButton(event.target);
                    addToCart(variationId, articleId)
                        .then(data => {
                            modal.close();
                            updateCart(data.total_quantity, data.total_price, data.cart_items);
                            updateCartButton(articleId, true, false);
                        })
                        .catch(error => {
                            console.error('Error adding to cart:', error);
                        })
                        .finally(() => {
                            isAddingToCart = false;
                            enableButton(event.target);
                        });
                } else {
                    alert('Пожалуйста, выберите вариацию курса.');
                }
            } else if (event.target.classList.contains('btn-add-to-cart')) {
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
                    document.getElementById('btn-add-to-cart-dialog').setAttribute('data-article-id', articleId);
                    modal.showModal();
                } else {
                    isAddingToCart = true;
                    disableButton(event.target);
                    addToCart(null, articleId)
                        .then(data => {
                            updateCartButton(articleId, true, false);
                            updateCart(data.total_quantity, data.total_price, data.cart_items);
                        })
                        .catch(error => {
                            console.error('Error adding to cart:', error);
                        })
                        .finally(() => {
                            isAddingToCart = false;
                            enableButton(event.target);
                        });
                }
            } else if (event.target.classList.contains('btn-remove-from-cart')) {
                event.stopImmediatePropagation();
                const articleId = event.target.getAttribute('data-article-id');
                isRemovingFromCart = true;
                disableButton(event.target);
                removeFromCart(articleId)
                    .then(data => {
                        updateCart(data.total_quantity, data.total_price, data.cart_items);
                        updateCartButton(articleId, false, false);
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

    function updateCartButton(articleId, inCart, alreadyPurchased) {
        const button = document.querySelector(`.cart-button[data-article-id="${articleId}"] button`);
        if (alreadyPurchased) {
            button.className = 'btn btn-sm btn-success';
            button.textContent = 'Уже приобретено';
            button.disabled = true;
        } else if (inCart) {
            button.className = 'btn btn-sm btn-secondary btn-add-to-cart';
            button.textContent = 'Добавлено';
            button.disabled = false;
        } else {
            button.className = 'btn btn-sm btn-primary openBtn';
            button.textContent = 'Добавить в корзину';
            button.disabled = false;
        }
    }

    function addToCart(variationId, articleId) {
        const url = '/cart/add/';
        const data = {
            variation_id: variationId,
            article_id: articleId
        };

        return fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json());
    }

    function removeFromCart(articleId) {
        const url = `/cart/remove/${articleId}/`;
        return fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json());
    }

    function updateCart(totalQuantity, totalPrice, cartItems) {
        const cartCountElement = document.getElementById('cart-count');
        const cartTotalElement = document.getElementById('cart-total');
        cartCountElement.textContent = totalQuantity;
        cartTotalElement.textContent = totalPrice;

        const cartItemsContainer = document.getElementById('cart-items');
        cartItemsContainer.innerHTML = cartItems.map(item => `
            <div class="cart-item" data-article-id="${item.article_id}">
                <img src="${item.image_url}" alt="${item.name}" style="width: 50px; height: 50px;">
                <span>${item.name}</span>
                <span>${item.price}</span>
                <button class="btn btn-sm btn-danger btn-remove-from-cart" data-article-id="${item.article_id}">Удалить</button>
            </div>
        `).join('');
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







