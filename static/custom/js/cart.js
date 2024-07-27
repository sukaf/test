document.addEventListener('DOMContentLoaded', function() {
    function setRemoveButtonListeners() {
        const removeButtons = document.querySelectorAll('.btn-remove-from-cart');
        removeButtons.forEach(button => {
            button.addEventListener('click', function() {
                const articleId = this.getAttribute('data-article-id');
                console.log(`Attempting to remove article with ID: ${articleId}`);
                if (articleId) {
                    const cartItemElement = this.closest('li.cart-item');
                    removeFromCart(articleId, cartItemElement);
                } else {
                    console.error('Article ID is not provided');
                }
            });
        });
    }

    setRemoveButtonListeners(); // Установим обработчики событий при загрузке страницы

    function removeFromCart(articleId, cartItemElement) {
        if (!articleId) {
            console.error('Article ID is not provided');
            return;
        }

        fetch(`/cart/remove/${articleId}/`, {
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
        })
        .then(data => {
            if (data.status === 'removed') {
                console.log(`Successfully removed article with ID: ${articleId}`);
                if (cartItemElement) {
                    cartItemElement.remove(); // Удаление элемента из DOM после успешного удаления из корзины
                }
                updateCart(data.total_quantity, data.total_price, data.cart_items, data.total_discount);
            } else {
                console.error('Failed to remove item:', data);
            }
        })
        .catch(error => {
            console.error('Error removing item from cart:', error);
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

    function updateCart(total_quantity, total_price, cart_items, total_discount) {
        document.getElementById('total_quantity').innerText = total_quantity;
        document.getElementById('total_price').innerText = total_price + ' ₽';
        document.getElementById('total_discount').innerText = `-${total_discount} ₽`;

        const cartCounter = document.getElementById('cart-count');
        if (cartCounter) {
            cartCounter.innerText = total_quantity;
        }

        // Обновим кнопку "Перейти к оплате"
        const payButton = document.querySelector('.btn-pay');
        if (payButton) {
            payButton.innerText = `Перейти к оплате ${total_price} ₽`;
        }

        // Найдем существующие элементы и обновим их данные, а не полностью перерисовывая
        cart_items.forEach(item => {
            const existingCartItem = document.querySelector(`.cart-item[data-article-id="${item.article_id}"]`);
            if (existingCartItem) {
                existingCartItem.querySelector('.cart-item-quantity p').innerText = `Количество: ${item.quantity}`;
                existingCartItem.querySelector('.cart-item-quantity p:nth-child(2)').innerText = `Общая стоимость: ${item.total_price} ₽`;
            }
        });

        // Обновим cart summary
        const cartItemsSummary = document.getElementById('cart-items-summary');
        cartItemsSummary.innerHTML = ''; // Очистим список
        cart_items.forEach(item => {
            const summaryItem = document.createElement('li');
            summaryItem.classList.add('cart-item-summary');
            summaryItem.innerHTML = `
                <div class="cart-item-details-summary">
                    <p>${item.title}</p>
                    <p>${item.price_month} ₽</p>
                </div>
            `;
            cartItemsSummary.appendChild(summaryItem);
        });

        document.getElementById('total_quantity').innerText = total_quantity;
        document.getElementById('total_price').innerText = total_price + ' ₽';

        setRemoveButtonListeners(); // Переустановим обработчики событий для новых элементов
    }
});




