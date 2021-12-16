; size=2, offset=0, typ=2, data='0000', chksum=0xC

; size=16, offset=6, typ=0, data='00006FEF3FEF1FEF0000609510956127', chksum=0xE

; size=16, offset=22, typ=0, data='312360953623609563276095062F0000', chksum=0xF

; size=4, offset=38, typ=0, data='0C941200', chksum=0x4

; size=0, offset=0, typ=1, data='', chksum=0xFF


; DISASSEMBLY:

address_0x0:
NOP
address_0x1:
NOP
address_0x2:
NOP
address_0x3:
NOP
LDI	R22,	255 (=0b11111111)
SEP	R19
LDI	R17,	255 (=0b11111111)
address_0x7:
NOP
COM	R22
COM	R17
EOR	R22,	R17
AND	R19,	R17
COM	R22
AND	R19,	R22
COM	R22
EOR	R22,	R19
COM	R22
MOV	R16,	R22
address_0x12:
NOP
JMP	0x12 (=0b0000000000000000010010)

;; f = ~((~a^~c)^((b&~c)&~(~a^~c)))