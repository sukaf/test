// cart_summary.js

document.addEventListener('DOMContentLoaded', function() {

    // Функция для обновления отображения корзины
    function updateCartSummary(total_quantity, total_price, cart_items) {
        document.getElementById('total_quantity').innerText = total_quantity;
        document.getElementById('total_price').innerText = total_price + ' ₽';

        const cartItemsSummary = document.getElementById('cart-items-summary');
        cartItemsSummary.innerHTML = '';

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
    }


    const paymentForm = document.getElementById('payment-form');
    if (paymentForm) {
        paymentForm.addEventListener('submit', function(event) {
            event.preventDefault();  // Предотвращаем стандартное поведение отправки формы
            const formData = new FormData(paymentForm);

            fetch(paymentForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.paymentUrl) {
                    window.location.href = data.paymentUrl; // Перенаправляем пользователя на страницу оплаты
                } else {
                    console.error('Ошибка при создании платежа:', data);
                }
            })
            .catch(error => {
                console.error('Ошибка при создании платежа:', error);
            });
        });
    }



    // Обработчик нажатия на кнопку "Перейти к оплате"
    document.querySelectorAll('.pay-button').forEach(button => {
        button.addEventListener('click', function() {
            const amount = this.getAttribute('data-amount');
            const description = this.getAttribute('data-description');
            const courseId = this.getAttribute('data-course-id');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch('/my_courses/payment_success/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    amount: amount,
                    description: description,
                    course_id: courseId
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.paymentUrl) {
                    window.location.href = data.paymentUrl;
                } else {
                    console.error('Ошибка при создании платежа:', data.error);
                }
            })
            .catch(error => {
                console.error('Ошибка при создании платежа:', error);
            });
        });
    });

    // Добавьте другие обработчики и функции по необходимости

    // Остальной JavaScript код для работы с корзиной

    function fetchCartSummaryData() {
        // Реализуйте логику для получения или обновления данных корзины
        // Пример: использование AJAX-запроса для получения актуальных данных
        // Для простоты, эти данные могут быть уже доступны или переданы из backend
    }

    // Инициализация отображения корзины при загрузке страницы
    fetchCartSummaryData();

    // Слушаем события cart-updated, генерируемые в cart.js
    window.addEventListener('cart-updated', function(event) {
        const summary = event.detail;
        updateCartSummary(summary.total_quantity, summary.total_price, summary.cart_items);
    });
});



