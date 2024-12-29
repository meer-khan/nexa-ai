from pyModbusTCP.client import ModbusClient

def make_announcement():
    c = ModbusClient(host='192.168.18.49', port=502,unit_id=1,auto_open=True)
    v = 0
    # v can be 0 or 1. If 0 it will not open door and with one it will open door
    regs = c.write_multiple_registers(0,[v])
    regs = c.read_holding_registers(0,1)