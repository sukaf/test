document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.remove-item-btn').forEach(button => {
        button.addEventListener('click', function() {
            const enrollmentId = this.getAttribute('data-enrollment-id');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch(`/remove_enrollment/${enrollmentId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    console.log(`Successfully removed enrollment with ID: ${enrollmentId}, article ID: ${data.article_id}`);
                    this.parentElement.remove();
                } else {
                    console.error('Ошибка при удалении записи:', data.error);
                }
            })
            .catch(error => {
                console.error('Ошибка при удалении записи:', error);
            });
        });
    });
});
