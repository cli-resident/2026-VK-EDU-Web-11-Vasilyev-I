const votes = document.querySelectorAll('.vote');

for (const vote of votes) {
    const buttons = vote.querySelectorAll('button');
    const counter = vote.querySelector('output');
    let selected = 0;

    for (const button of buttons) {
        if (button.getAttribute('aria-pressed') === 'true') {
            selected = Number(button.dataset.vote);
        }
    }

    const startRating = Number(counter.value) - selected;

    for (const button of buttons) {
        button.addEventListener('click', function () {
            const value = Number(button.dataset.vote);

            if (selected === value) {
                selected = 0;
            } else {
                selected = value;
            }

            counter.value = startRating + selected;

            for (const otherButton of buttons) {
                const pressed = Number(otherButton.dataset.vote) === selected;
                otherButton.setAttribute('aria-pressed', pressed);
            }
        });
    }
}
const answers = document.querySelectorAll('.correct input');

for (const answer of answers) {
    answer.addEventListener('change', function () {
        if (answer.checked) {
            for (const otherAnswer of answers) {
                if (otherAnswer !== answer) {
                    otherAnswer.checked = false;
                }
            }
        }
    });
}

const forms = document.querySelectorAll('.editor-form');

for (const form of forms) {
    const result = form.querySelector('.form-result');
    const error = form.querySelector('.alert');
    const fields = form.querySelectorAll('input:not([type=hidden]), textarea');

    for (const field of fields) {
        const message = document.createElement('div');
        message.id = field.id + '-error';
        message.className = 'invalid-feedback';
        message.hidden = true;
        field.insertAdjacentElement('afterend', message);
        const description = field.getAttribute('aria-describedby') || '';
        field.setAttribute('aria-describedby', (description + ' ' + message.id).trim());
    }

    form.addEventListener('input', function (event) {
        result.textContent = '';
        error.hidden = true;
        const input = event.target;
        const message = document.getElementById(input.id + '-error');
        if (message) {
            message.textContent = '';
            message.hidden = true;
        }
        input.classList.remove('is-invalid');
        input.removeAttribute('aria-invalid');
        input.setCustomValidity('');

        const hint = document.getElementById(input.id + '-hint');
        if (hint && hint.classList.contains('invalid-feedback')) {
            hint.classList.remove('d-block');
            hint.hidden = true;
        }
    });

    form.addEventListener('submit', function (event) {
        event.preventDefault();

        result.textContent = '';
        const password = form.elements.password;
        const repeatPassword = form.elements.confirm;
        const tags = form.elements.tags;

        if (repeatPassword) {
            repeatPassword.setCustomValidity('');
            if (repeatPassword.value !== password.value) {
                repeatPassword.setCustomValidity('Пароли не совпадают.');
            }
        }

        if (tags) {
            let count = 0;
            for (const tag of tags.value.split(',')) {
                if (tag.trim() !== '') {
                    count++;
                }
            }

            tags.setCustomValidity('');
            if (count > 3) {
                tags.setCustomValidity('Можно указать не более 3 тегов.');
            }
        }

        for (const field of fields) {
            const message = document.getElementById(field.id + '-error');
            const invalid = !field.validity.valid;
            field.classList.toggle('is-invalid', invalid);
            field.setAttribute('aria-invalid', String(invalid));
            message.textContent = invalid ? field.validationMessage : '';
            message.hidden = !invalid;
        }

        if (!form.checkValidity()) {
            const invalidInput = form.querySelector(':invalid');
            error.textContent = 'Проверьте заполнение полей. ' + invalidInput.validationMessage;
            error.hidden = false;
            invalidInput.focus();
            return;
        }

        error.hidden = true;
        form.querySelector('.form-result').textContent =
            'Форма заполнена корректно. Это демонстрация: данные не отправлены на сервер.';
    });
}
const avatarInput = document.querySelector('input[type="file"]');

if (avatarInput) {
    avatarInput.addEventListener('change', function () {
        const file = avatarInput.files[0];
        if (!file || !file.type.startsWith('image/')) {
            return;
        }

        const preview = avatarInput.closest('form').querySelector('.avatar');
        if (preview) {
            const imageUrl = URL.createObjectURL(file);
            preview.onload = function () {
                URL.revokeObjectURL(imageUrl);
            };
            preview.src = imageUrl;
        }
    });
}
