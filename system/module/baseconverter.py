import xmltodict
import orjson as json
from jinja2 import Template  # https://lectureswww.readthedocs.io/6.www.sync/2.codding/3.templates/jinja2.html
import re


# Класс конвертор преобразует из словаря в любой загруженный шаблон (XML, JSON, txt, yaml,...)
class BaseConverter:
    name_file_template = None

    def __init__(self, name_file_template=None):
        if name_file_template:
            self.name_file_template = name_file_template
        self.template = Template(self.read_file(self.name_file_template))

    # Удаление тега из текстового xml
    def del_tag_xml_text(self, xml_text, tag, count=1):
        return re.sub(f"<{tag}>(.*?)</{tag}>", "", xml_text, count=count, flags=re.DOTALL)
        
    def set_template(self,str):
        self.template = Template(str)
    # Чтение файла из template
    def read_file(self,name_file):
        if not name_file:
            return ""
        with open(f'./template/{name_file.split(".")[-1].lower()}/{name_file}', 'r',encoding='utf-8') as f:  # открываем файл на чтение
            return f.read()

    def only_digitals(self,str):
       return re.sub("\D", "", str)

    # Преобразование строки в int, даже если строка без чисел!
    def int(self,s):
        res = 0
        if isinstance(s, str):
            s_digital = self.only_digitals(s)
            if s_digital:
                res = int(s_digital)
        elif isinstance(s, (float, int)):
            res = int(s)
        return res

    # XML в словарь: start_fields - поля которые пропустить, prefix_del - префиксы которые удалить,
    # upper_case - перевести в верхний регистр
    # Пример:
    #  start_fields => 'Envelope>Body>RequestGIL'
    #  prefix_del => ('ns2', 'ns4', 'SOAP-ENV')
    def xml_to_dict(self, xml, start_fields='', prefix_del=(), upper_case=False):
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

    # Генерация для кэша
    def generate_cache(self, xml_dict, name_fields, upper_case=False):
        if upper_case:  # Верхний регистр
            name_fields = [val.upper() for val in name_fields]
        cache = {}
        for fields in name_fields:
            listFields = fields.split(">")
            cur_item = xml_dict
            for field in listFields:
                cur_item = cur_item[field]
            cache[fields] = cur_item
        return cache

    def get_json(self, text, sort_keys=True):
        return json.dumps(text, sort_keys=sort_keys)

    def prepare_vars_for_template(self,vars):
        return vars

    # рендер XML/JSON и пр. по шаблону
    def render_template(self, vars, name_file_template = None):
        vars_template = self.prepare_vars_for_template(vars)
        if name_file_template:
            template = Template(self.read_file(name_file_template))
        else:
            template = self.template
        return template.render(**vars_template)

    def __call__(self, *args, **kwargs):
        return self.render_template(*args)
