class ParseError(Exception):
    pass


def parse_add_command(text: str) -> tuple[str, str]:
    payload = text.replace("/add", "", 1).strip()
    if not payload:
        raise ParseError("📝 Введите слово в формате:\n" "`/add слово:перевод`")
    if ":" not in payload:
        raise ParseError(
            "❌ Неверный формат.\n" "Используйте:\n" "`/add слово:перевод`"
        )

    word, translation = map(str.strip, payload.split(":", 1))

    if not word or not translation:
        raise ParseError("❌ Слово и перевод не могут быть пустыми")
    return word.lower(), translation.lower()


def parse_settings_command(text: str) -> int | None:
    parts = text.strip().split()

    if len(parts) == 1:
        return None
    if len(parts) != 2:
        raise ParseError("Неверный формат. Используйте: /settings 3")
    value = parts[1]
    if not value.isdigit() and value[0] != "-":
        raise ParseError("Нужно указать число")
    count = int(value)
    if count < 1 or count > 23:
        raise ParseError("Число должно быть от 1 до 23")
    return count
