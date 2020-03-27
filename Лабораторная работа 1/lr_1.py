import csv

def tariff(data, number, free_incoming_minutes, incoming_calls_cost, outgoing_calls_cost, free_sms, sms_cost):
    total = 0
    for row in data:
        if row['msisdn_origin'] == number:
            # Обработка исходящих вызовов
            total += float(row['call_duration']) * outgoing_calls_cost
            
            # Обработка смс сообщений
            sms_num = int(row['sms_number'])
            total += (sms_num - free_sms) * sms_cost if sms_num > free_sms else 0
            
        if row['msisdn_dest'] == number:
            # Обработка входящих вызовов
            duration = float(row['call_duration'])
            total += (duration - free_incoming_minutes) * incoming_calls_cost \
                if duration > free_incoming_minutes else 0
        
    return total

if __name__ == '__main__':
    with open('data.csv', 'r') as csvfile:
        file = list(csv.DictReader(csvfile))
    
    print(tariff(file, '968247916', 5, 1, 4, 5, 1))

