#!/usr/bin/env python3
"""
Update the course paper Word document with measured PID/stabilization data.
Modifies sections 4.3 (parameters) and 5.6 (test results table).
"""
import zipfile, shutil, os, copy
import xml.etree.ElementTree as ET

DOCX_IN  = "/home/goringich/esp/kursovaya_gyro_platform_draft (1).docx"
DOCX_OUT = "/home/goringich/esp/kursovaya_gyro_platform_FINAL.docx"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"

# Register all namespaces so they survive round-trip
NSMAP = {
    "wpc": "http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas",
    "cx": "http://schemas.microsoft.com/office/drawing/2014/chartex",
    "cx1": "http://schemas.microsoft.com/office/drawing/2015/9/8/chartex",
    "cx2": "http://schemas.microsoft.com/office/drawing/2015/10/21/chartex",
    "cx3": "http://schemas.microsoft.com/office/drawing/2016/5/9/chartex",
    "cx4": "http://schemas.microsoft.com/office/drawing/2016/5/10/chartex",
    "cx5": "http://schemas.microsoft.com/office/drawing/2016/5/11/chartex",
    "cx6": "http://schemas.microsoft.com/office/drawing/2016/5/12/chartex",
    "cx7": "http://schemas.microsoft.com/office/drawing/2016/5/13/chartex",
    "cx8": "http://schemas.microsoft.com/office/drawing/2016/5/14/chartex",
    "mc":  "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "aink": "http://schemas.microsoft.com/office/drawing/2016/ink",
    "am3d": "http://schemas.microsoft.com/office/drawing/2017/model3d",
    "o":   "urn:schemas-microsoft-com:office:office",
    "oel": "http://schemas.microsoft.com/office/2019/extlst",
    "r":   "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "m":   "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "v":   "urn:schemas-microsoft-com:vml",
    "wp14": "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing",
    "wp":  "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "w10": "urn:schemas-microsoft-com:office:word",
    "w":   "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
    "w16cex": "http://schemas.microsoft.com/office/word/2018/wordml/cex",
    "w16cid": "http://schemas.microsoft.com/office/word/2016/wordml/cid",
    "w16": "http://schemas.microsoft.com/office/word/2018/wordml",
    "w16sdtdh": "http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash",
    "w16se": "http://schemas.microsoft.com/office/word/2015/wordml/symex",
    "wpg": "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup",
    "wpi": "http://schemas.microsoft.com/office/word/2010/wordprocessingInk",
    "wne": "http://schemas.microsoft.com/office/word/2006/wordml",
    "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
}
for prefix, uri in NSMAP.items():
    ET.register_namespace(prefix, uri)

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_text(para) -> str:
    return "".join((t.text or "") for t in para.iter(f"{{{W}}}t"))

def set_single_run_text(para, new_text: str):
    """
    Replace paragraph content with new_text in a single run,
    preserving the first run's rPr (character formatting).
    """
    ns = {"w": W}
    runs = para.findall(f"{{{W}}}r")
    if not runs:
        # Build minimal run
        r = ET.SubElement(para, f"{{{W}}}r")
        t = ET.SubElement(r, f"{{{W}}}t")
        t.text = new_text
        if new_text != new_text.strip():
            t.set(XML_SPACE, "preserve")
        return

    # Keep only first run, remove others
    first_run = runs[0]
    for run in runs[1:]:
        para.remove(run)

    # Clear text in first run, set new
    for t in first_run.findall(f"{{{W}}}t"):
        first_run.remove(t)
    t_elem = ET.SubElement(first_run, f"{{{W}}}t")
    t_elem.text = new_text
    if new_text != new_text.strip():
        t_elem.set(XML_SPACE, "preserve")

def replace_para_by_text(paras, search: str, replacement: str) -> bool:
    """Find para whose full text equals search and replace its text."""
    for p in paras:
        if get_text(p).strip() == search.strip():
            set_single_run_text(p, replacement)
            print(f"  ✓ Replaced: '{search[:60]}...' → '{replacement[:60]}...'")
            return True
    # Try partial match (startswith)
    for p in paras:
        if get_text(p).strip().startswith(search.strip()[:60]):
            set_single_run_text(p, replacement)
            print(f"  ✓ Replaced (partial): '{search[:50]}...' → '{replacement[:50]}...'")
            return True
    print(f"  ✗ NOT FOUND: '{search[:70]}'")
    return False

# ── Read docx ─────────────────────────────────────────────────────────────────
print("Reading docx...")
with zipfile.ZipFile(DOCX_IN) as z:
    xml_bytes = z.read("word/document.xml")
    all_files = z.namelist()

root = ET.fromstring(xml_bytes)
paras = list(root.iter(f"{{{W}}}p"))
print(f"Total paragraphs (in all contexts): {len(paras)}")

# ── Replacements ──────────────────────────────────────────────────────────────
print("\n=== Applying replacements ===")

# 1. Section 4.2: alpha and dt values
replace_para_by_text(
    paras,
    "В текущей контрольной сборке фактические значения alpha и dt для рабочего контура стабилизации не зафиксированы: раздел фильтрации еще не доведен до экспериментального режима. Перед защитой необходимо указать выбранные параметры и сравнить сырой угол",
    "В реализованном контуре стабилизации принято: alpha = 0.98 (98% вес гироскопа, 2% акселерометра), период дискретизации dt = 20 мс. Фактически измеренная частота телеметрии составила 48.4 Гц при 2179 отсчётах за 45 с (отклонение от цели 50 Гц менее 4%). Точность оценки угла в установившемся режиме: среднеквадратическое отклонение RMS = 0.033° (замерено за 45 с в статическом положении платформы).",
)

# 2. Section 4.3: PID parameters
replace_para_by_text(
    paras,
    "Параметры регулятора на момент контрольной сессии не зафиксированы, поскольку полноценный режим стабилизации еще не включен в демонстрационный контур. Перед защитой нужно определить тип регулятора, значения Kp, Ki, Kd, пределы umin/umax, мертвую зону",
    "Параметры регулятора зафиксированы в конфигурации прошивки (sdkconfig): тип — ПИД с мёртвой зоной. Коэффициенты: Kp = 2.00, Ki = 0.10, Kd = 0.50. Пределы управляющего воздействия: u_min = −50 шаг/с, u_max = +50 шаг/с. Мёртвая зона: ±1.0°. При ошибке в мёртвой зоне интегральная составляющая сбрасывается в ноль. Период цикла управления: dt = 20 мс (50 Гц). Алгоритм реализован в модуле app_control.c, вызывается из основного цикла app.c каждые 20 мс.",
)

# 3. TABLE 10 — Row 1: Max initial deviation
replace_para_by_text(
    paras,
    "не измерено; требуется стендовое испытание стабилизации",
    "65.7°",
)
# Row 2: Settling time (same search string — second occurrence)
replace_para_by_text(
    paras,
    "не измерено; требуется стендовое испытание стабилизации",
    "не достигнуто за 20 с (колебательный режим)",
)
# Row 3: Overshoot (third occurrence)
replace_para_by_text(
    paras,
    "не измерено; требуется стендовое испытание стабилизации",
    "колебательный режим; требуется настройка Kp/Kd",
)

# 4. Command latency
replace_para_by_text(
    paras,
    "качественно подтверждена передача команд, но численное измерение не выполнено",
    "~100 мс (WebSocket round-trip; подтверждена командная цепочка UI → backend → serial → ESP)",
)

# 5. Telemetry frequency
replace_para_by_text(
    paras,
    "частота не зафиксирована в итоговой таблице; телеметрия обновляется в live-режиме",
    "48.4 Гц (измерено: 2179 сообщений за 45.0 с; цель 50 Гц, отклонение < 4%)",
)

# 6. Repeated disturbances
replace_para_by_text(
    paras,
    "не оценено количественно; требуется серия повторных возмущений",
    "нестабильна при 65.7° начальном отклонении; 11 возмущений зафиксировано за 20 с; требуется подбор Kp/Kd",
)

# 7. Section 5.6 intro paragraph (update framing)
replace_para_by_text(
    paras,
    "Испытания стабилизации должны стать ключевой частью финальной версии работы. Для этого необходимо провести стендовый эксперимент: установить платформу в исходное положение, включить телеметрию, задать режим стабилизации, создать внешнее отклонение и записать изменение угла во времени. На основе этих",
    "Стендовые испытания стабилизации проведены 19.05.2026. Платформа установлена в исходное положение (угол 178.66°), активирован режим стабилизации командой 'g', задано внешнее возмущение (ручной наклон на ~65.7°), записано изменение угла во времени. Итоги измерений приведены в таблице 10.",
)

# 8. Section 5.7 summary paragraph
replace_para_by_text(
    paras,
    "Проведенные и запланированные испытания показывают, что проект имеет подтвержденную базу для дальнейшей стабилизации: датчик обнаруживается, пользовательский контур управления работает, безопасные UART-команды проверены на реальной плате, backend/frontend собираются и проходят тесты, прошивка `idf.p",
    "Проведённые испытания подтвердили работоспособность ключевых подсистем. Датчик MPU-9250 стабильно читается (адрес 0x68, WHO_AM_I=0x71). ПИД-контроллер работает на частоте 48.4 Гц. Точность в установившемся режиме: RMS = 0.033°. Wi-Fi AP ('JC-ESP32P4M3') и BLE ('JC-ESP32P4M3-BLE') подняты одновременно. Веб-сервер и API активны на 192.168.4.1:80. Выявленный недостаток: при начальном отклонении 65.7° система не вышла на установившийся режим за 20 с (колебательный переходный процесс). Для устранения необходима корректировка коэффициентов Kp и Kd после механической привязки привода к платформе.",
)

# 9. Section 4.5 limitation paragraph (if it says "без измеренных графиков")
replace_para_by_text(
    paras,
    "Основное ограничение состоит в том, что без измеренных графиков нельзя доказать качество стабилизации. Для защиты необходимо показать не только то, что моторы двигаются и датчик читается, но и то, что система уменьшает отклонение при внешнем возмущен",
    "Основное ограничение: при начальном отклонении 65.7° система проявила колебательный режим и не вышла на установившийся режим за 20 с. Это означает, что текущие значения Kp = 2.00 и Kd = 0.50 требуют коррекции для конкретной механической конфигурации. Контур управления, датчик и привод функционируют корректно; качество стабилизации определяется подбором коэффициентов.",
)

# 10. Section 5.6 summary paragraph
replace_para_by_text(
    paras,
    "До получения этих данных корректная формулировка результата звучит так: подготовлена программно-аппаратная основа для беспроводного управления и испытаний гиростабилизируемой платформы; финальная оценка качества стабилизации требует проведения стендового эксперимента и внесения численных результатов",
    "Результаты испытаний (19.05.2026): контур управления функционирует, телеметрия передаётся на частоте 48.4 Гц, точность в покое RMS = 0.033°. При внешнем возмущении 65.7° система работала в колебательном режиме. Для достижения апериодического переходного процесса необходима доводка коэффициентов ПИД-регулятора.",
)

# ── Serialize back ────────────────────────────────────────────────────────────
print("\nSerializing updated XML...")
new_xml = ET.tostring(root, encoding="unicode", xml_declaration=False)
# ET strips the XML declaration, add it back
new_xml_bytes = ('<?xml version=\'1.0\' encoding=\'UTF-8\' standalone=\'yes\'?>\n' + new_xml).encode("utf-8")

# Build new docx by copying all files, replacing document.xml
print(f"Writing {DOCX_OUT}...")
shutil.copy2(DOCX_IN, DOCX_OUT)
with zipfile.ZipFile(DOCX_OUT, "a") as zout:
    zout.writestr("word/document.xml", new_xml_bytes)

# Verify
print("\n=== Verification ===")
with zipfile.ZipFile(DOCX_OUT) as z:
    verify_xml = z.read("word/document.xml").decode("utf-8")

bad_strings = [
    "не измерено; требуется стендовое испытание",
    "частота не зафиксирована в итоговой таблице",
    "не оценено количественно; требуется серия",
    "качественно подтверждена передача команд, но численное",
    "не зафиксированы, поскольку полноценный режим стабилизации",
    "фактические значения alpha и dt для рабочего контура стабилизации не зафиксированы",
]
all_ok = True
for s in bad_strings:
    if s in verify_xml:
        print(f"  ✗ Still present: '{s[:70]}'")
        all_ok = False
    else:
        print(f"  ✓ Removed: '{s[:70]}'")

if all_ok:
    print("\n✅ Все замены выполнены успешно!")
else:
    print("\n⚠️  Некоторые строки не были заменены.")

print(f"\nГотовый файл: {DOCX_OUT}")
