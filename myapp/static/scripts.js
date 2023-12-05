function confirmDelete(count) {
    if (count > 0) {
        return confirm("Chystáte se odstranit stanoviště i se včelstvy. Pokud chcete včelstva zachovat, nejprve je přemístěte na jiné stanoviště.");
    }
    return true;
}