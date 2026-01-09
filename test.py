def draw_table(data):
    if not data: return
    
    # Ширина колонок
    w = [max(len(str(r[i])) for r in data) for i in range(len(data[0]))]
    
    # Верхняя граница
    print("┌" + "┬".join("─" * (x + 2) for x in w) + "┐")
    
    # Данные
    for row in data:
        line = "│".join(f" {str(x).ljust(w)} " for x, w in zip(row, w))
        print(f"│{line}│")
        if row == data[0]:  # Разделитель после заголовка
            print("├" + "┼".join("─" * (x + 2) for x in w) + "┤")
    
    # Нижняя граница
    print("└" + "┴".join("─" * (x + 2) for x in w) + "┘")

# Тест
draw_table([
    ["Товар", "Цена", "Кол-во"],
    ["Хлеб", "50", "10"],
    ["Молокыфввввввввввввввввввввввввввввввввввво", "80", "5"],
    ["Сыр", "300", "2"]
])