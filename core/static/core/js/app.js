async function sendRequest(url, values) {
    const token = document.querySelector('#csrf-form input').value;
    const response = await fetch(url, {
        method: 'POST',
        headers: {'X-CSRFToken': token},
        body: new URLSearchParams(values)
    });
    if (!response.headers.get('content-type')?.includes('application/json')) {
        throw new Error('Не удалось выполнить запрос. Обновите страницу и попробуйте снова.');
    }
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'Не удалось сохранить изменения.');
    }
    return data;
}

for (const vote of document.querySelectorAll('.vote')) {
    const buttons = vote.querySelectorAll('button');
    const error = vote.nextElementSibling;
    for (const button of buttons) {
        button.addEventListener('click', async function () {
            error.textContent = '';
            for (const current of buttons) current.disabled = true;
            try {
                const data = await sendRequest(vote.dataset.url, {value: button.dataset.vote});
                vote.querySelector('output').value = data.rating;
                for (const current of buttons) {
                    current.setAttribute('aria-pressed', Number(current.dataset.vote) === data.selected);
                }
            } catch (problem) {
                error.textContent = problem.message;
            } finally {
                for (const current of buttons) current.disabled = false;
            }
        });
    }
}

const answerBoxes = document.querySelectorAll('.correct input');
for (const checkbox of answerBoxes) {
    checkbox.addEventListener('change', async function () {
        const previous = !checkbox.checked;
        for (const current of answerBoxes) current.disabled = true;
        try {
            const data = await sendRequest(checkbox.dataset.url, {
                question_id: checkbox.dataset.question,
                answer_id: checkbox.dataset.answer
            });
            for (const current of answerBoxes) {
                current.checked = Number(current.dataset.answer) === data.answer_id;
            }
        } catch (problem) {
            checkbox.checked = previous;
            alert(problem.message);
        } finally {
            for (const current of answerBoxes) current.disabled = false;
        }
    });
}
