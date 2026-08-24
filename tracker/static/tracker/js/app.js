document.addEventListener('DOMContentLoaded', function () {
    function csrfToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute('content') : '';
    }

    function updateCountdowns() {
        const countdownElements = document.querySelectorAll('.countdown');
        const now = new Date();

        countdownElements.forEach((element) => {
            const raw = element.dataset.deadline;
            if (!raw) {
                return;
            }
            // Treat YYYY-MM-DD as local end-of-day so "days left" matches the UI.
            const deadline = raw.length <= 10
                ? new Date(`${raw}T23:59:59`)
                : new Date(raw);
            if (Number.isNaN(deadline.getTime())) {
                element.textContent = '—';
                return;
            }

            const diff = deadline - now;
            if (diff < 0) {
                element.textContent = 'Deadline passed';
                element.classList.add('text-danger');
                return;
            }

            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            element.textContent = `${days}d ${hours}h remaining`;
            element.classList.toggle('text-warning', days <= 30);
            element.classList.toggle('text-danger', days <= 7);
        });
    }

    updateCountdowns();
    setInterval(updateCountdowns, 60000);

    document.querySelectorAll('.task-toggle').forEach((checkbox) => {
        checkbox.addEventListener('change', function () {
            const taskId = this.dataset.taskId;
            const row = this.closest('.task-row');
            fetch(`/api/task/${taskId}/toggle`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken(),
                },
                body: JSON.stringify({ completed: this.checked }),
            })
                .then((response) => {
                    if (!response.ok) {
                        throw new Error('Toggle failed');
                    }
                    return response.json();
                })
                .then((data) => {
                    this.checked = data.completed;
                    if (row) {
                        row.classList.toggle('task-completed', data.completed);
                    }
                })
                .catch(() => {
                    this.checked = !this.checked;
                });
        });
    });
});
