function confirmDelete(count, warningText) {
    if (count > 0) {
        return confirm(warningText);
    }
    return true;
}