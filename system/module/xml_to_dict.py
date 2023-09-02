import xmltodict


# Доработанная xmltodict
# XML в словарь: start_fields - поля которые пропустить, prefix_del - префиксы которые удалить,
# upper_case - перевести в верхний регистр
# Пример:
#  start_fields => 'Envelope>Body>RequestGIL'
#  prefix_del => ('ns2', 'ns4', 'SOAP-ENV')
def xml_to_dict(xml, start_fields='', prefix_del=(), upper_case=False):
    if xml and isinstance(xml, str):
        if isinstance(start_fields, str):  # если строка, то разбиваем
            start_fields = start_fields.split(">")
        if upper_case:  # Верхний регистр
            find_index = xml.find("?>")
            if find_index != -1:
                xml = xml[find_index+2:]
            xml_pre = xml.upper()
            start_fields = [val.upper() for val in start_fields]
            prefix_del = [val.upper() for val in prefix_del]
        else:
            xml_pre = xml
        for prefix in prefix_del:  # удаление префиксов при необходимости
            xml_pre = xml_pre.replace(f'{prefix}:', '')
        items = xmltodict.parse(xml_pre)  # преобразование xml в словарь
        for field in start_fields:  # Переход к необходимой ветке
            items = items[field]
        return items


def in_list(el):
    return el if isinstance(el, list) else [el]
