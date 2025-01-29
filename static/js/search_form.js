document.getElementById('searchField').addEventListener('input', function () {
    const searchValue = this.value.toLowerCase();
    const items = document.querySelectorAll('.rest_item');
    let hasVisibleItems = false;

    items.forEach(item => {
        const name = item.querySelector('.card-title').textContent.toLowerCase();
        if (name.includes(searchValue)) {
            item.classList.remove('hidden'); // Zeige Element
            hasVisibleItems = true;
        } else {
            item.classList.add('hidden'); // Verstecke Element
        }
    });

    // Scroll nach oben, wenn ein Suchergebnis gefunden wird
    if (hasVisibleItems) {
        document.querySelector('.container').scrollIntoView({ behavior: 'smooth' });
    }

    // Zeige "Keine Ergebnisse"-Meldung
    document.getElementById('noResults').style.display = hasVisibleItems ? 'none' : 'block';
});
