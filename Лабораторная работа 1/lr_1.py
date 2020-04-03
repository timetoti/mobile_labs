#! /usr/bin/env python3
import csv

def tariff(data, number, incoming_calls_cost, outgoing_calls_cost, free_sms, sms_cost):
    total = 0
    stats = []
    for row in data:
        if row['msisdn_origin'] == number:
            # Обработка исходящих вызовов
            duration = float(row['call_duration'])
            cost = duration * outgoing_calls_cost
            total += cost
            stats.append(f'Outgoing call, duration = {duration} minutes, cost = {cost} rubles')
            
            # Обработка смс сообщений
            sms_num = int(row['sms_number'])
            cost = (sms_num - free_sms) * sms_cost if sms_num > free_sms else 0
            total += cost
            stats.append(f'Sms, number = {sms_num}, cost = {cost} rubles')
            
        if row['msisdn_dest'] == number:
            # Обработка входящих вызовов
            duration = float(row['call_duration'])
            cost = duration * incoming_calls_cost
            total += cost
            stats.append(f'Incoming call, duration = {duration} minutes, cost = {cost} rubles')
        
    return stats, total

if __name__ == '__main__':
    with open('data.csv', 'r') as csvfile:
        file = list(csv.DictReader(csvfile))
    
    result = tariff(file, '915642913', 1, 1, 5, 1)
    for row in result[0]:
        print(row)
    print(f'total is {result[1]} rubles')
