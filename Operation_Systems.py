import flet as ft
import logging
import json


def main(page: ft.Page):
    page.title = "Решение задач по управлению памятью"
    page.window_width = 700
    page.window_height = 500
    page.window_resizable = True

    # Настройка логирования
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

    # Задание 1: Страничная память
    def calculate_task1(e):
        try:
            # Входные данные
            x_bit = int(task1_inputs["x_bit"].value)  # Общее количество бит в адресе
            sv = int(task1_inputs["sv"].value)  # Биты для смещения
            virtual_address = int(task1_inputs["virtual_address"].value, 16)  # Виртуальный адрес

            # Преобразуем таблицу страниц
            raw_page_table = task1_inputs["page_table"].value.split(",")  # Таблица страниц
            page_table = {}
            for entry in raw_page_table:
                virtual, physical = entry.split(":")
                if virtual.strip().startswith("0b"):  # Если виртуальная страница двоичная
                    virtual = int(virtual.strip(), 2)
                else:
                    virtual = int(virtual.strip())
                if physical.strip().startswith("0b"):  # Если физическая страница двоичная
                    physical = int(physical.strip(), 2)
                else:
                    physical = int(physical.strip())
                page_table[virtual] = physical

            # Разделяем виртуальный адрес
            page_size = 2 ** sv  # Размер страницы
            page_number = virtual_address >> sv  # Номер виртуальной страницы
            offset = virtual_address & (page_size - 1)  # Смещение внутри страницы

            # Находим номер физической страницы
            if page_number in page_table:
                frame_number = page_table[page_number]
                physical_address = (frame_number << sv) | offset  # Физический адрес
                task1_result.value = (
                    f"Физический адрес: 0x{physical_address:X}\n"
                    f"Размер страницы: {page_size} байт\n"
                    f"Количество страниц: {2 ** (x_bit - sv)}\n"
                )
            else:
                task1_result.value = "Ошибка: Номер виртуальной страницы отсутствует в таблице."
        except Exception as ex:
            task1_result.value = f"Ошибка: {ex}"
        page.update()

    # Задание 2: Сегментная память
    def calculate_task2(e):  # e — это переданный параметр события
        try:
            # Входные данные
            g = int(task2_inputs["g"].value)  # Биты на номер сегмента
            s = int(task2_inputs["s"].value)  # Биты на смещение
            virtual_address_hex = task2_inputs["virtual_address"].value.strip()  # Виртуальный адрес (Hex)
            segments_input = task2_inputs["segment_table"].value.strip().split(",")  # Таблица сегментов

            # Проверка входных данных
            if not virtual_address_hex.startswith("0x"):
                raise ValueError("Виртуальный адрес должен быть в шестнадцатеричном формате (например, 0x1234).")
            if g + s != 32:
                raise ValueError("Сумма бит на номер сегмента и смещение должна быть равна 32.")

            # Преобразование виртуального адреса
            virtual_address = int(virtual_address_hex, 16)
            virtual_address_bin = f"{virtual_address:032b}"  # Преобразуем в 32-битное двоичное число

            # Вычисление номера сегмента и смещения
            segment_number_bin = virtual_address_bin[:g]
            segment_number = int(segment_number_bin, 2)  # Номер сегмента в десятичной системе
            offset_bin = virtual_address_bin[g:]
            offset = int(offset_bin, 2)  # Смещение в десятичной системе

            # Создание таблицы сегментов
            segment_table = {}
            for seg in segments_input:
                try:
                    segment, base, length = seg.split(":")
                    segment_table[int(segment)] = (int(base, 16), int(length, 16))
                except ValueError:
                    raise ValueError(f"Ошибка в формате данных сегмента: {seg}")

            # Проверка наличия сегмента в таблице
            if segment_number not in segment_table:
                task2_result.value = (
                    f"Виртуальный адрес: {virtual_address_hex}\n"
                    f"Ошибка: Сегмент с номером {segment_number} не найден в таблице."
                )
            else:
                base, length = segment_table[segment_number]

                # Проверка, входит ли смещение в допустимый диапазон
                if offset >= length:
                    task2_result.value = (
                        f"Виртуальный адрес: {virtual_address_hex}\n"
                        f"Номер сегмента: {segment_number}\n"
                        f"Ошибка: Смещение (0x{offset:X}) превышает длину сегмента (0x{length:X})."
                    )
                else:
                    # Вычисление физического адреса
                    physical_address = base + offset
                    task2_result.value = (
                        f"Виртуальный адрес: {virtual_address_hex}\n"
                        f"Двоичный адрес: {virtual_address_bin}\n"
                        f"Номер сегмента: {segment_number} (двоичный: {segment_number_bin})\n"
                        f"Смещение: 0x{offset:X} (двоичный: {offset_bin})\n"
                        f"Физический адрес: 0x{physical_address:X}"
                    )

        except Exception as ex:
            task2_result.value = f"Ошибка: {ex}"

        page.update()

    # Задание 3: Сегментно-страничная память
    def calculate_task3(e):
        try:
            # Чтение логического адреса
            logical_address_hex = task3_inputs["logical_address"].value.strip()
            if not logical_address_hex.startswith("0x"):
                raise ValueError("Логический адрес должен быть в формате 0x...")

            logical_address = int(logical_address_hex, 16)

            # Чтение параметров
            address_bits = int(task3_inputs["total_bits"].value.strip())
            max_segment_size = int(task3_inputs["max_segment_size"].value.strip())
            page_size = int(task3_inputs["page_size"].value.strip())

            # Расчёт параметров адресации
            segment_bits, page_bits, offset_bits = calculate_parameters(max_segment_size, page_size, address_bits)

            # Чтение и разбор таблицы сегментов
            segment_table_input = task3_inputs["segment_table"].value.strip().split(",")
            segment_table = parse_segment_table(segment_table_input)

            # Чтение и разбор таблиц страниц
            page_table_input = task3_inputs["page_table"].value.strip()
            page_tables = parse_page_tables(page_table_input)

            # Расчёт физического адреса
            physical_address = calculate_physical_address(
                logical_address, segment_table, page_tables, segment_bits, page_bits, offset_bits
            )

            # Вывод результатов
            task3_result.value = (
                f"Рассчитанные параметры:\n"
                f"- Биты под номер сегмента (segment_bits): {segment_bits}\n"
                f"- Биты под номер страницы (page_bits): {page_bits}\n"
                f"- Биты под смещение внутри страницы (offset_bits): {offset_bits}\n\n"
                f"Результаты вычислений физического адреса:\n"
                f"Логический адрес: {logical_address_hex}\n"
                f"Физический адрес: {physical_address}"
            )
        except Exception as ex:
            task3_result.value = f"Ошибка: {ex}"
        page.update()

    def calculate_parameters(segment_size, page_size, address_bits):
        """
        Функция для вычисления параметров адресации.
        """
        offset_bits = page_size.bit_length() - 1
        page_bits = (segment_size // page_size).bit_length() - 1
        segment_bits = address_bits - (page_bits + offset_bits)
        return segment_bits, page_bits, offset_bits

    def calculate_physical_address(logical_address, segment_table, page_tables, segment_bits, page_bits, offset_bits):
        """
        Функция для вычисления физического адреса из логического.
        """
        segment_mask = (1 << segment_bits) - 1
        segment_number = (logical_address >> (page_bits + offset_bits)) & segment_mask

        if segment_number not in segment_table:
            raise ValueError(f"Сегмент {segment_number} не найден.")

        segment_limit = segment_table[segment_number]
        segment_offset = logical_address & ((1 << (page_bits + offset_bits)) - 1)

        if segment_offset >= segment_limit:
            raise ValueError(f"Смещение {segment_offset:#x} выходит за пределы сегмента {segment_number}.")

        page_mask = (1 << page_bits) - 1
        page_number = (segment_offset >> offset_bits) & page_mask

        if page_number not in page_tables.get(segment_number, {}):
            raise ValueError(f"Страница {page_number} отсутствует в сегменте {segment_number}.")

        frame_number = page_tables[segment_number][page_number]
        page_offset = segment_offset & ((1 << offset_bits) - 1)
        frame_size = 1 << offset_bits
        physical_address = (frame_number * frame_size) + page_offset
        return f"0x{physical_address:X}"

    def parse_segment_table(segments_input):
        """
        Парсинг таблицы сегментов.
        """
        seg_table = {}
        for seg in segments_input:
            try:
                segment, length = seg.split(":")
                seg_table[int(segment)] = int(length, 16)
            except ValueError:
                raise ValueError(f"Ошибка в формате сегмента: {seg}")
        return seg_table

    def parse_page_tables(page_table_input):
        """
        Парсинг таблиц страниц.
        """
        try:
            page_tables = json.loads(page_table_input)
            # Проверяем, что все значения являются словарями
            if not all(isinstance(v, dict) for v in page_tables.values()):
                raise ValueError("Все значения в таблице страниц должны быть словарями.")
            return {int(k): {int(page): int(frame) for page, frame in v.items()} for k, v in page_tables.items()}
        except json.JSONDecodeError:
            raise ValueError("Таблицы страниц должны быть указаны в формате JSON.")

    # Задание 4: Ассоциативная память
    def calculate_task4(e):
        try:
            hit_ratio = float(task4_inputs["hit_ratio"].value)
            assoc_time = float(task4_inputs["assoc_time"].value)
            table_time = float(task4_inputs["table_time"].value)

            avg_time = hit_ratio * assoc_time + (1 - hit_ratio) * table_time
            task4_result.value = f"Среднее время доступа: {avg_time} нс"
        except Exception as ex:
            task4_result.value = f"Ошибка: {ex}"
        page.update()

    # Конвертер единиц памяти
    def convert_units(e):
        try:
            # Получение исходного значения
            input_value = float(converter_inputs["value"].value.strip())
            from_unit = converter_inputs["from_unit"].value
            to_unit = converter_inputs["to_unit"].value

            # Конвертация
            unit_multipliers = {
                "бит": 1,
                "байт": 8,
                "килобайт (КБ)": 8 * 1024,
                "мегабайт (МБ)": 8 * 1024 * 1024,
                "гигабайт (ГБ)": 8 * 1024 * 1024 * 1024,
            }

            if from_unit not in unit_multipliers or to_unit not in unit_multipliers:
                raise ValueError("Выберите корректные единицы.")

            # Преобразование значения
            bits = input_value * unit_multipliers[from_unit]  # Преобразуем всё в биты
            output_value = bits / unit_multipliers[to_unit]  # Преобразуем в целевую единицу

            # Отображение результата
            converter_result.value = f"{input_value} {from_unit} = {output_value:.2f} {to_unit}"
        except Exception as ex:
            converter_result.value = f"Ошибка: {ex}"
        page.update()

    # Поля ввода и выводы для задач
    task1_inputs = {
        "x_bit": ft.TextField(
            label="Всего бит в адресе:",
            hint_text="Например: 32",
            width=250
        ),
        "sv": ft.TextField(
            label="Биты на смещение:",
            hint_text="Например: 14",
            width=250
        ),
        "virtual_address": ft.TextField(
            label="Виртуальный адрес (Hex):",
            hint_text="Например: 0x14EE",
            width=250
        ),
        "page_table": ft.TextField(
            label="Таблица страниц (через запятую):",
            hint_text="Пример: 0b000:0b0101, 0b000:0b0010, 0b000:0b0011, 0b000:0b0100",
            width=250
        ),
    }
    task1_result = ft.Text(value="", size=14)

    task2_inputs = {
        "g": ft.TextField(label="Биты на номер сегмента:", width=250),
        "s": ft.TextField(label="Биты на смещение:", width=250),
        "virtual_address": ft.TextField(label="Виртуальный адрес (Hex):", width=250),
        "segment_table": ft.TextField(label="Сегментная таблица (сегмент:начало:длина через запятую):", width=400),
    }
    task2_result = ft.Text(value="", size=14)

    # Интерфейс
    task3_inputs = {
        "logical_address": ft.TextField(
            label="Логический адрес (Hex):",
            hint_text="Например: 0x034567B0",
            width=400,
        ),
        "total_bits": ft.TextField(
            label="Общий размер логического адреса (в битах):",
            hint_text="Например: 32",
            width=400,
        ),
        "max_segment_size": ft.TextField(
            label="Максимальный размер сегмента (в байтах):",
            hint_text="Например: 33554432 (32 МБ)",
            width=400,
        ),
        "page_size": ft.TextField(
            label="Размер страницы (в байтах):",
            hint_text="Например: 524288 (512 КБ)",
            width=400,
        ),
        "segment_table": ft.TextField(
            label="Сегментная таблица (формат: сегмент:длина через запятую):",
            hint_text="Пример: 1:0x1500000,4:0x2A0000",
            width=600,
        ),
        "page_table": ft.TextField(
            label="Таблицы страниц (формат JSON):",
            hint_text='Пример: {"1": {"30": 44, "40": 88}, "4": {"4": 55, "14": 77}}',
            width=600,
        ),
    }
    task3_result = ft.Text(value="", size=14)

    task4_inputs = {
        "hit_ratio": ft.TextField(label="Частота попаданий (0-1):", width=250),
        "assoc_time": ft.TextField(label="Время доступа к ассоциативной памяти (нс):", width=250),
        "table_time": ft.TextField(label="Время доступа к таблице страниц (нс):", width=250),
    }
    task4_result = ft.Text(value="", size=14)
    # Поля ввода и вывода для конвертера
    converter_inputs = {
        "value": ft.TextField(label="Значение:", width=300),
        "from_unit": ft.Dropdown(
            label="Из единицы:",
            options=[
                ft.dropdown.Option("бит"),
                ft.dropdown.Option("байт"),
                ft.dropdown.Option("килобайт (КБ)"),
                ft.dropdown.Option("мегабайт (МБ)"),
                ft.dropdown.Option("гигабайт (ГБ)"),
            ],
            width=300,
        ),
        "to_unit": ft.Dropdown(
            label="В единицу:",
            options=[
                ft.dropdown.Option("бит"),
                ft.dropdown.Option("байт"),
                ft.dropdown.Option("килобайт (КБ)"),
                ft.dropdown.Option("мегабайт (МБ)"),
                ft.dropdown.Option("гигабайт (ГБ)"),
            ],
            width=300,
        ),
    }
    converter_result = ft.Text(value="", size=14)

    # Создание вкладок с интерфейсом
    task1_tab = ft.Column(
        [
            ft.Text("Задача 1: Cтраничная организация памяти", size=16, weight="bold"),
            *task1_inputs.values(),
            ft.ElevatedButton("Рассчитать", on_click=calculate_task1),
            task1_result,
        ],
        spacing=10,
    )
    task2_tab = ft.Column(
        [
            ft.Text("Задача 2: Сегментная организация памяти", size=16, weight="bold"),
            *task2_inputs.values(),
            ft.ElevatedButton("Рассчитать", on_click=calculate_task2),
            task2_result,
        ],
        spacing=10,
    )
    # Интерфейс вкладки
    task3_tab = ft.Column(
        [
            ft.Text("Задача 3: Сегментно-страничная организация памяти", size=16, weight="bold"),
            *task3_inputs.values(),
            ft.ElevatedButton("Рассчитать", on_click=calculate_task3),
            task3_result,
        ],
        spacing=10,
    )
    task4_tab = ft.Column(
        [
            ft.Text("Задача 4: Ассоциативная память", size=16, weight="bold"),
            *task4_inputs.values(),
            ft.ElevatedButton("Рассчитать", on_click=calculate_task4),
            task4_result,
        ],
        spacing=10,
    )
    converter_tab = ft.Column(
        [
            ft.Text("Конвертер единиц памяти", size=16, weight="bold"),
            *converter_inputs.values(),
            ft.ElevatedButton("Конвертировать", on_click=convert_units),
            converter_result,
        ],
        spacing=10,
    )

    # Добавление вкладок в интерфейс
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="Задача 1", content=task1_tab),
            ft.Tab(text="Задача 2", content=task2_tab),
            ft.Tab(text="Задача 3", content=task3_tab),
            ft.Tab(text="Задача 4", content=task4_tab),
            ft.Tab(text="Конвертер величин", content=converter_tab),
        ],
        expand=True,
    )

    page.add(tabs)


ft.app(target=main)