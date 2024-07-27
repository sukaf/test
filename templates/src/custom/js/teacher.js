// JavaScript для обработки выбора преподавателя
document.addEventListener('DOMContentLoaded', function () {
    const dropdown = document.getElementById('teacher-dropdown');
    const dropdownMenu = dropdown.querySelector('.dropdown-menu');

    // Показываем меню при наведении
    dropdown.addEventListener('mouseenter', function () {
        dropdownMenu.classList.add('show');
    });

    // Скрываем меню при уходе мыши с области dropdown
    dropdown.addEventListener('mouseleave', function () {
        dropdownMenu.classList.remove('show');
    });

    const teacherLinks = dropdownMenu.querySelectorAll('.dropdown-item');

    teacherLinks.forEach(function (link) {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            const teacherId = this.getAttribute('data-teacher-id');
            filterArticlesByTeacher(teacherId);
        });
    });

    function filterArticlesByTeacher(teacherId) {
        const articles = document.querySelectorAll('.card');
        articles.forEach(function (article) {
            const articleTeacherId = article.getAttribute('data-teacher-id');
            if (teacherId === 'all' || teacherId === articleTeacherId) {
                article.style.display = 'block';
            } else {
                article.style.display = 'none';
            }
        });
    }
});