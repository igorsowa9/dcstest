import platform, sys

IP_send = '134.130.169.96' # RTDS
IP_receive = '134.130.169.12' # VM
Port_send = 12345
Port_receive = 12345

NumData = 6
settings_fromRTDS = ['V1', 'V1', 'V1', 'V2', 'V2', 'V2']

IP_broker = ['localhost', # broker between VM and DCS1
             'localhost', # between VM and DSO
             'localhost', # between DSO and DCS2
             'localhost'] # between DSO and BRGW

dcssim = True
wait_dcs = 3
wait_lte = 2

attack = True
DSO_control = True