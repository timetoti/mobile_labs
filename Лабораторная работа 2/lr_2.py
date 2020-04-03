#! /usr/bin/env python3
import csv
import matplotlib
import matplotlib.pyplot as plt
import datetime
import itertools

def tariff(data, ip_addr, traffic_cost, free_traffic):
    total_bytes = 0
    stats = []
    for row in data:
        if row['sa'] == ip_addr or row['da'] == ip_addr:
            # Обработка входящих и исходящих пакетов
            bytes_len = int(row['ibyt'])
            total_bytes += bytes_len
            stats.append(('Incoming' if row['sa'] == ip_addr else 'Outcoming') + \
                f' traffic, bytes length = {bytes_len} bytes')
            
    total_mb = total_bytes / 2 ** 20
    total = (total_mb - free_traffic) * traffic_cost if total_mb > free_traffic else 0
    return stats, total
    
def make_plot(data, ip_addr, filename):
    dates_lens = []
    for row in data:
        if row['sa'] == ip_addr or row['da'] == ip_addr:
            dates_lens.append((datetime.datetime.strptime(row['ts'], "%Y-%m-%d %H:%M:%S"), int(row['ibyt']) / 1024))
    
    # group traffic by minutes
    def group_filter(x):
        return datetime.datetime.strptime(x[0].strftime('%Y-%m-%d %H:%M:0'), '%Y-%m-%d %H:%M:%S')
        
    dates_lens = itertools.groupby(sorted(dates_lens, key=group_filter), group_filter)
    dates_lens = [(key, sum([x[1] for x in group])) for key, group in dates_lens]
    dates = [x[0] for x in dates_lens]
    kb_len = [x[1] for x in dates_lens]
    
    dates = matplotlib.dates.date2num(dates)
    ax = plt.subplot(111)
    ax.plot(dates, kb_len)
    ax.xaxis_date()
    plt.xlabel('Time')
    xformatter = matplotlib.dates.DateFormatter('%H:%M')
    plt.gcf().axes[0].xaxis.set_major_formatter(xformatter)
    plt.ylabel('Bytes transferred (kB)')
    plt.savefig(filename)
    print(f'plot saved as {filename}')

if __name__ == '__main__':
    with open('dump.csv', 'r') as csvfile:
        file = list(csv.DictReader(csvfile))
    
    result = tariff(file, '192.168.250.59', 1, 1)
    for row in result[0]:
        print(row)
    print(f'total is {result[1]} rubles')
    
    make_plot(file, '192.168.250.59', 'plot.png')
