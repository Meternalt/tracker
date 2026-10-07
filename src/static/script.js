async function loadState() {
    const res = await fetch('/api/state');
    const data = await res.json();

    document.getElementById('char-name').textContent = data.name;
    document.getElementById('level').textContent = data.level;
    document.getElementById('gold').textContent = data.gold;
    document.getElementById('freeze').textContent = data.freeze;

    // HP
    const hpPct = (data.hp / data.hp_max) * 100;
    document.getElementById('hp-bar').style.width = hpPct + '%';
    document.getElementById('hp-text').textContent =
        `${data.hp} / ${data.hp_max}`;

    // XP
    const xpPct = (data.xp / data.xp_max) * 100;
    document.getElementById('xp-bar').style.width = xpPct + '%';
    document.getElementById('xp-text').textContent =
        `${data.xp} / ${data.xp_max}`;

    // Привычки
    const list = document.getElementById('habits-list');
    list.innerHTML = '';
    data.habits.forEach(h => {
        const li = document.createElement('li');
        li.className = h.done_today ? 'done' : '';
        li.innerHTML = `
            <span>${h.done_today ? '✓' : '○'} ${h.name}</span>
            <span class="streak">streak: ${h.streak} | XP ${h.xp_reward}</span>
        `;
        li.onclick = () => completeHabit(h.name);
        list.appendChild(li);
    });
}

async function completeHabit(name) {
    const res = await fetch('/api/complete', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name})
    });
    const data = await res.json();
    showMessage(data.message);
    loadState();
}

async function addHabit() {
    const name = document.getElementById('new-habit-name').value.trim();
    const difficulty = document.getElementById('new-habit-diff').value;
    if (!name) return;

    await fetch('/api/new_habit', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name, difficulty})
    });
    document.getElementById('new-habit-name').value = '';
    showMessage(`Привычка "${name}" добавлена`);
    loadState();
}

async function saveGame() {
    await fetch('/api/save', {method: 'POST'});
    showMessage('Сохранено');
}

function showMessage(text) {
    const el = document.getElementById('message');
    el.textContent = text;
    setTimeout(() => el.textContent = '', 3000);
}

loadState();
setInterval(loadState, 5000);