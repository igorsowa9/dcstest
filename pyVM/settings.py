import platform, sys

dbname = 'SAU_FC_pc'

#if str(platform.machine())=='x86_64':
#    IPinput = input("input your IP (leave empty for previous one): ")
#    if IPinput == "":
#        IPinput = '137.226.124.77'
#else: IPinput = '134.130.169.61' # for raspberry

IP_send = '134.130.169.96' # RTDS
IP_receive = '137.226.133.186' # VM/RPI
Port_send = 12345
Port_receive = 12345

NumData = 2
settings_fromRTDS = [['P5max', 28, 'ABCN', 4], ['P5min', 29, 'ABCN', 4]]
