import time
from datetime import datetime
import serial
from serial.tools import list_ports

VENDOR_ID = 0x2E8A
PRODUCT_ID = 0x000A
TASK = "2.2.5"
PROJECT = "221-command-time"
LOG_NAME = "device-2-2-5.log"

def find_board():
    for port in list_ports.comports():
        if port.vid == VENDOR_ID and port.pid == PRODUCT_ID:
            return port
    return None

def send_cmd(port, cmd, wait=1.0):
    port.write((cmd + "\n").encode("ascii"))
    print("--> " + cmd, end="\r\n")
    time.sleep(wait)
    res = []
    while True:
        line = port.readline().decode("ascii", "replace").strip()
        if not line:
            break
        print("<-- " + line, end="\r\n")
        res.append((cmd, line))
    return res

def talk(board):
    exchange = []
    with serial.Serial(board.device, timeout=1.0) as port:
        time.sleep(0.2)
        port.reset_input_buffer()
        
        exchange += send_cmd(port, "clk_info", 1.0)
        exchange += send_cmd(port, "main_time_exec", 1.0)
        
        # Запускаем calc_pi на 125 МГц
        exchange += send_cmd(port, "calc_pi", 6.0)
        
        # Понижаем частоту
        exchange += send_cmd(port, "clk_sys_low", 1.0)
        time.sleep(2.0) # Ждем, пока среднее наберется
        
        exchange += send_cmd(port, "clk_info", 1.0)
        exchange += send_cmd(port, "main_time_exec", 1.0)
        
        # Запускаем calc_pi на 62.5 МГц
        exchange += send_cmd(port, "calc_pi", 12.0)
        
        # Проверяем uptime
        exchange += send_cmd(port, "uptime", 1.0)
        exchange += send_cmd(port, "uptime", 1.0)
        
        # Возвращаем частоту
        exchange += send_cmd(port, "clk_sys_default", 1.0)
        time.sleep(2.0)
        
        exchange += send_cmd(port, "clk_info", 1.0)
        exchange += send_cmd(port, "calc_pi", 6.0)
        
    return exchange

def write_log(board, exchange):
    with open(LOG_NAME, "w", encoding="utf-8") as log:
        log.write("задание: " + TASK + "\n")
        log.write("проект: " + PROJECT + "\n")
        log.write("устройство: %04x:%04x\n" % (board.vid, board.pid))
        log.write("серийный номер: " + str(board.serial_number) + "\n")
        log.write("порт: " + board.device + "\n")
        log.write("начало: " + datetime.now().isoformat(timespec="seconds") + "\n")
        
        for cmd, text in exchange:
            log.write("--> %s\n<-- %s\n" % (cmd, text))
            
        log.write("итог: отправлено команд %d\n" % len(exchange))

board = find_board()
if board is None:
    print("Плата не найдена. Проверьте кабель и запишите на плату прошивку задания.", end="\r\n")
else:
    print("Плата на порту " + board.device + ", посылаю команды", end="\r\n")
    exchange = talk(board)
    write_log(board, exchange)
    print("Обмен записан в " + LOG_NAME, end="\r\n")
