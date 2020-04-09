#!/usr/bin/env python3

import csv
import fpdf
import os

def tariff_calls(data, number, incoming_calls_cost, outgoing_calls_cost, free_sms, sms_cost):
    total = 0
    stats = []
    for row in data:
        if row['msisdn_origin'] == number:
            # Обработка исходящих вызовов
            duration = float(row['call_duration'])
            cost = duration * outgoing_calls_cost
            total += cost
            stats.append(('Исходящие звонки', str(round(duration, 1)), 'Минуты', str(outgoing_calls_cost), str(round(cost, 1))))
            
            # Обработка смс сообщений
            sms_num = int(row['sms_number'])
            cost = (sms_num - free_sms) * sms_cost if sms_num > free_sms else 0
            total += cost
            stats.append(('СМС', str(sms_num), 'Штук', str(sms_cost), str(round(cost, 1))))
            
        if row['msisdn_dest'] == number:
            # Обработка входящих вызовов
            duration = float(row['call_duration'])
            cost = duration * incoming_calls_cost
            total += cost
            stats.append(('Входящие звонки', str(round(duration, 1)), 'Минуты', str(incoming_calls_cost), str(round(cost, 1))))
        
    return stats, total

def tariff_internet(data, ip_addr, traffic_cost, free_traffic):
    total_bytes = 0
    for row in data:
        if row['sa'] == ip_addr or row['da'] == ip_addr:
            # Обработка входящих и исходящих пакетов
            bytes_len = int(row['ibyt'])
            total_bytes += bytes_len
            
    total_mb = total_bytes / 2 ** 20
    total = round((total_mb - free_traffic) * traffic_cost, 1) if total_mb > free_traffic else 0
    return ('Интернет трафик', str(round(total_mb, 1)), 'Мб', str(traffic_cost), str(total)), total
    
def to_pdf(filename, bank_name, inn, kpp, bik, recipient, acc_num1, acc_num2, \
                bill_num, bill_date, provider, customer, cause, \
                stats, total):
    pdf = fpdf.FPDF()
    pdf.set_right_margin(15)
    pdf.set_left_margin(15)
    pdf.add_page()
    # adding fonts for russian letters
    pdf.add_font('DejaVu', '', os.path.join('.', 'fonts_for_fpdf', 'DejaVuSansCondensed.ttf'), uni=True)
    pdf.add_font('DejaVu', 'B', os.path.join('.', 'fonts_for_fpdf', 'DejaVuSansCondensed-Bold.ttf'), uni=True)
    
    pdf.set_font('DejaVu', '', 10)
    headers = [[f'Банк получателя: {bank_name}', f'БИК: {bik}'],
            [f'ИНН: {inn}', f'КПП: {kpp}', f'Сч. № {acc_num1}'],
            [f'Получатель: {recipient}', f'Сч. № {acc_num2}']]
    col_width = (pdf.w - 30) / 2
    row_height = pdf.font_size * 2
    for row in headers:
        for col in row:
            pdf.cell(col_width / 2 if 'ИНН' in col or 'КПП' in col else col_width , row_height,
                     txt=col, border=1)
        pdf.ln(row_height)

    pdf.set_font('DejaVu', 'B', 14)
    s = f'Счёт №{bill_num} от {bill_date} г.'
    margins = int((pdf.w - pdf.get_string_width(s) - 30) / 2 / pdf.get_string_width(' ')) * ' '
    pdf.write(14, margins + s)
    pdf.ln(5)
    pdf.write(14, '_' * int((pdf.w - 30) / pdf.get_string_width('_')))
    
    pdf.set_font('DejaVu', '', 10)
    pdf.ln(10)
    pdf.write(10, 'Поставщик')
    pdf.ln(5)
    pdf.write(10, f'(Исполнитель): {provider}')
    pdf.ln(10)
    pdf.write(10, 'Покупатель')
    pdf.ln(5)
    pdf.write(10, f'(Заказчик): {customer}')
    pdf.ln(10)
    pdf.write(10, f'Основание: {cause}')
    pdf.ln(10)
    
    row_height = pdf.font_size * 2
    pdf.cell(10, row_height, txt='№', border=1) # №
    pdf.cell(70, row_height, txt='Наименование работ, услуг', border=1) # Наименование
    pdf.cell(15, row_height, txt='Кол-вo', border=1) # Кол-во
    pdf.cell(30, row_height, txt='Ед.', border=1) # Ед.
    pdf.cell(25, row_height, txt='Цена', border=1) # Ценна
    pdf.cell(25, row_height, txt='Сумма', border=1) # Сумма
    pdf.ln(row_height)
    for row_num, row in enumerate(stats):
        pdf.cell(10, row_height, txt=str(row_num + 1), border=1) # №
        pdf.cell(70, row_height, txt=row[0], border=1) # Наименование
        pdf.cell(15, row_height, txt=row[1], border=1) # Кол-во
        pdf.cell(30, row_height, txt=row[2], border=1) # Ед.
        pdf.cell(25, row_height, txt=row[3], border=1) # Ценна
        pdf.cell(25, row_height, txt=row[4], border=1) # Сумма
        pdf.ln(row_height)
        
    strings = [f'Итого: {total} руб.', f'В том числе НДС: 0 руб.', f'Всего к оплате: {total} руб.']
    pdf.set_font('DejaVu', 'B', 10)
    for s in strings:
        margins = int((pdf.w - pdf.get_string_width(s) - 36) / pdf.get_string_width(' ')) * ' '
        pdf.write(10, margins + s)
        pdf.ln(5)
    pdf.ln(5)
        
    pdf.set_font('DejaVu', '', 10)
    strings = ['Внимание!', 'Оплата данного счета означает согласие с условиями поставки товара.', \
    'Уведомление об оплате обязательно, в противном случае не гарантируется наличие товара на складе.',\
    'Товар отпускается по факту прихода денег на р/с Поставщика, самовывозом, при наличии', 'доверенности и паспорта.']
    for s in strings:
        pdf.write(10, s)
        pdf.ln(5)
    pdf.set_font('DejaVu', 'B', 14)
    pdf.write(14, '_' * int((pdf.w - 30) / pdf.get_string_width('_')))
    pdf.ln(20)
    pdf.set_font('DejaVu', '', 10)
    margins = int((pdf.w - pdf.get_string_width('РуководительБухгалтер') - 30) / 2 / pdf.get_string_width('_')) * '_'
    pdf.write(10, f'Руководитель{margins}Бухгалтер{margins}')
    
    pdf.output(name=filename)
    
if __name__ == '__main__':
    stats = []
    # Data from first lab
    with open('data.csv', 'r') as csvfile:
        file = list(csv.DictReader(csvfile))
    
    stats_temp, calls_total = tariff_calls(file, '915642913', 1, 1, 5, 1)
    stats.extend(stats_temp)
    
    # Data from second lab
    with open('dump.csv', 'r') as csvfile:
        file = list(csv.DictReader(csvfile))
    
    stats_temp, internet_total = tariff_internet(file, '192.168.250.59', 1, 1)
    stats.append(stats_temp)

    to_pdf('lab3_output.pdf', 'Имя банка', 'ИНН', 'КПП', 'БИК', 'Иванов', '1', '2',\
            '1', '9.04.2020', 'ОАО Провайдер', 'Иванов', 'Стандартная подписка',\
            stats, calls_total + internet_total)
    
