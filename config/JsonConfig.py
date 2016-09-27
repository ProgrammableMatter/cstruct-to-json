import json
from collections import OrderedDict

DefaultEnumByteSize = 2

# custom address labels definitions
Labels = OrderedDict({
    "labels": {
        # start address of the global struct
        "globalStateBase": 96
    }
})

NativeTypeToSimulatorBitfieldType = {
    "bit": "bit",

    "char": "bit",
    "uint8_t": "bit",
    "int8_t": "bit",

    "uint16_t": "dbit",
    "int16_t": "dbit",
}

NativeTypeToSimulatorType = {
    "bitfield": "bit",
    "dbitfield": "dbit",
    "char": "char",
    "hex": "hex",
    "uint8_t": "uint8_t",
    "int8_t": "int8_t",
    "uint16_t": "uint16_t",
    "int16_t": "int16_t",
    "dhex": "dhex",
    "hex16": "hex16",
    "<pointerType>": "hex16",
    "float": "float32",
# infers float32, float32[1],float32[2] and float32[3] which are handled exceptional by the sim.
    "int32_t": "int32_t",  # infers int32, int32[1], ...
    "uint32_t": "uint32_t",  # infers uint32, uint32[1], ...
}

Infer2ndByteSimulatorTypeToNextSmallerType = {
    "dbit": "bit",
    "dhex": "hex",
    "uint16_t": "hex",
    "int16_t": "hex",
    "16hex": "hex",
}

NativeTypeToSize = {
    "bitfield": 1,
    "uint8_t": 1,
    "int8_t": 1,
    "uint16_t": 2,
    "int16_t": 2,
    "float": 4,
    "int32_t": 4,
    "uint32_t": 4,
    "<pointerType>": 2,
}

TypeOverrides = [
    {
        # if a field's property contains this property,
        "property": "__structStartMarker",
        # and has the simulator type equals oldType
        "oldType": "uint8_t",
        # the type is overridden with newType
        "newType": "hex",
    },
    {
        "property": "__structEndMarker",
        "oldType": "uint8_t",
        "newType": "hex",
    },
    {
        "property": "row",
        "oldType": "hex",
        "newType": "unsigned",
    }, {
        "property": "column",
        "oldType": "hex",
        "newType": "unsigned",
    }, {
        "property": "loopCount",
        "oldType": "hex",
        "newType": "unsigned",
    }, {
        "property": "bitMask",
        "oldType": "hex",
        "newType": "bit",
    },
    {
        "property": "maxShortIntervalDurationOvertimePercentageRatio",
        "oldType": "hex",
        "newType": "unsigned"
    },
    {
        "property": "maxLongIntervalDurationOvertimePercentageRatio",
        "oldType": "hex",
        "newType": "unsigned"
    },
    {
        "property": "(timerValue[15:1] | isRisingEdge[0])",
        "oldType": "dbit",
        "newType": "unsigned int"
    },
    {
        "property": "(__pad[7] | startIndex[6:0])",
        "oldType": "bit",
        "newType": "unsigned"
    },
    {
        "property": "(__pad1[7] | endIndex[6:0])",
        "oldType": "bit",
        "newType": "unsigned"
    },

]

# infers an extra register description for the 2nd byte of 2 byte length types, i.e. uint16_t
Infer2ndByte = True

# infers extra register descriptions of 4 byte length types, i.e. u/int32, float
InferUpTo4thByte = True

# inference exceptions
InferUpTo4thByteExceptions = [
    {
        # do not infer 2nd byte if a field's property contains this property,
        "property": "state",
        # and has the simulator type contains type
        "type": "StateType",
    },
]
# inference exceptions
Infer2ndByteExceptions = [
    {
        # do not infer 2nd byte if a field's property contains this property,
        "property": "state",
        # and has the simulator type contains type
        "type": "StateType",
    }, {
        "property": "type",
        "type": "NodeType",
    }, {
        "property": "decodingState",
        "type": "ManchesterDecodingStateType",
    }, {
        "property": "xmissionState",
        "type": "XmissionType",
    },
    {
        "property": "initiatorState",
        "type": "CommunicationInitiatorStateTypes",
    },
    {
        "property": "receptionistState",
        "type": "CommunicationReceptionistStateTypes"
    },
    {
        "property": "executionState",
        "type": "ActuationStateType"
    },
    {
        "property": "blinkAddressState",
        "type": "AddressBlinkStates"
    },
    {
        "property": "blinkState",
        "type": "TimeIntervalBlinkStates"
    },
]

HardwareRegisters = OrderedDict({
    "structs": {
        # /* state in register of pin (input) A  */
        "A.in": [
            {
                "property": "(EAST_TX | EAST_SW | TP3 | PA4 | SOUTH_TX | SOUTH_SW | TP2 | ERROR)",
                "type": "bit",
                "address": 57
            }
        ],
        # /* state in direction register of port A */
        "A.dir": [
            {
                "property": "(EAST_TX | EAST_SW | TP3 | PA4 | SOUTH_TX | SOUTH_SW | TP2 | ERROR)",
                "type": "bit",
                "address": 58
            }
        ],
        # /* state in register of port (output) A  */
        "A.out": [
            {
                "property": "(EAST_TX | EAST_SW | TP3 | PA4 | SOUTH_TX | SOUTH_SW | TP2 | ERROR)",
                "type": "bit",
                "address": 59
            }
        ],
        # /* state in register of pin (input) B  */
        "B.in": [
            {
                "property": "(B7 | B6 | B5 | STAT0 | STAT1 | NRTH_RX | HTBEAT | B0)",
                "type": "bit",
                "address": 54
            }
        ],
        # /* state in direction register of port B */
        "B.dir": [
            {
                "property": "(B7 | B6 | B5 | STAT0 | STAT1 | NRTH_RX | HTBEAT | B0)",
                "type": "bit",
                "address": 55
            }
        ],
        # /* state in register of port (output) B  */
        "B.out": [
            {
                "property": "(B7 | B6 | B5 | STAT0 | STAT1 | NRTH_RX | HTBEAT | B0)",
                "type": "bit",
                "address": 56
            }
        ],
        # /* state in register of pin (input) C  */
        "C.in": [
            {
                "property": "(C7 | C6 | C5 | NRTH_SW | C3 | TP1 | C1 | NRTH_TX)",
                "type": "bit",
                "address": 51
            }
        ],
        # /* state in direction register of port C */
        "C.dir": [
            {
                "property": "(C7 | C6 | C5 | NRTH_SW | C3 | TP1 | C1 | NRTH_TX)",
                # /* how to print the port value */
                "type": "bit",
                "address": 52
            }
        ],
        # /* state in register of port (output) C  */
        "C.out": [
            {
                "property": "(C7 | C6 | C5 | NRTH_SW | C3 | TP1 | C1 | NRTH_TX)",
                "type": "bit",
                "address": 53
            }
        ],
        # /* state in direction register of port D*/
        "D.dir": [
            {
                "property": "(D7 | D6 | D5 | D4 | EAST_RX | SOUTH_RX | D1 | D0)",
                "type": "bit",
                "address": 49
            }
        ],
        # /* state in register of port (output) D */
        "D.out": [
            {
                "property": "(D7 | D6 | D5 | D4 | EAST_RX | SOUTH_RX | D1 | D0)",
                "type": "bit",
                "address": 50
            }
        ],
        # /* state in register of pin (input) D */
        "D.in": [
            {
                "property": "(D7 | D6 | D5 | D4 | EAST_RX | SOUTH_RX | D1 | D0)",
                "type": "bit",
                "address": 48
            }
        ],
        # /* UDR usart i/o register */
        "char-out": [
            {
                "property": "",
                "type": "char",
                "address": 44
            }
        ],
        # /*  serial programming interface data register */
        "SPDR": [
            {
                "property": "",
                "type": "hex",
                "address": 47
            }
        ],
        # /* state in general interrupt control register */
        "GICR": [
            {
                "property": "(INT1 | INT0 | INT2 | - | - | - | IVSEL | IVCE)",
                "type": "bit",
                "address": 91
            }
        ],
        # /* state in EEPROM EEARL register */
        "int16H-out": [
            {
                "property": "",
                "type": "hex",
                "address": 62
            }
        ],
        # /* state in EEPROM EEDR register including the following register */
        "int16-out": [
            {
                "property": "",
                "type": "unsigned int",
                "address": 61
            }
        ],
        # /* state in timer/counter interrupt flag register */
        "TIFR": [
            {
                "property": "(OCF2 | TOV2 | ICF1 | OCF1A | OCF1B | TOV1 | OCF0 | TOV0)",
                "type": "bit",
                "address": 88
            }
        ],
        # /* state in timer compare register 1A */
        "TCCR1A": [
            {
                "property": "(COM1A1 | COM1A0 | COM1B1 | COM1B0 | OCF1B | FOC1A | WGM11 | WGM10)",
                "type": "bit",
                "address": 79
            }
        ],
        # /* state in timer compare register 1B */
        "TCCR1B": [
            {
                "property": "(ICNC1 | ICES1 | - | WGM13 | WGM12 | CS12 | CS11 | CS10)",
                "type": "bit",
                "address": 78
            }
        ],
        # /* state in the timer counter compare register 0 */
        "TCCR0": [
            {
                "property": "(FOC0 | WGM00 | COM01 | COM00 | WGM01 | CS02 | CS01 | CS00)",
                "type": "bit",
                "address": 83
            }
        ],
        # /* state in timer/counter1 compare register high byte */
        # "OCR1AH": [
        #     {
        #         "property": "",
        #         "type": "hex",
        #         "address": 75
        #     }
        # ],
        # /* state in timer/counter1 compare register low byte */
        "OCR1A": [
            {
                "property": "",
                "type": "uint16_t",
                "address": 74
            }
        ],
        # /* state in timer/counter1 compare register high byte*/
        # "OCR1BH": [
        #     {
        #         "property": "",
        #         "type": "hex",
        #         "address": 73
        #     }
        # ],
        # /* state in timer/counter1 compare register low byte*/
        "OCR1B": [
            {
                "property": "",
                "type": "uint16_t",
                "address": 72
            }
        ],
        # /* state in timer counter0 compare register */
        "OCR0": [
            {
                "property": "",
                "type": "uint8_t",
                "address": 92
            }
        ],
        # /* state in MCU control register*/
        "MCUCR": [
            {
                "property": "(SM2 | SE | SM1 | SM0 | ISC11 | ISC10 | ISC01 | ISC00)",
                "type": "bit",
                "address": 85
            }
        ],
        # /* state in MCU control and status register */
        "MCUCSR": [
            {
                "property": "(JTD | ISC2 | - | JTRF | WDRF | BORF | EXTRF | PORF)",
                "type": "bit",
                "address": 84
            }
        ],
        # /* state in Timer/Counter0 (8 Bits) register */
        "TCNT0": [
            {
                "property": "",
                "type": "signed",
                "address": 82
            }
        ],
        # /* state in timer/counter1 - counter high byte register */
        "TCNT1H": [
            {
                "property": "",
                "type": "hex",
                "address": 77
            }
        ],
        # /* state in timer/counter1 - counter low byte register */
        "TCNT1L": [
            {
                "property": "",
                "type": "hex",
                "address": 76
            }
        ],
        # /* state in timer/counter interrupt mask register */
        "TIMSK": [
            {
                "property": "(OCIE2 | TOIE2 | TICIE1 | OCIE1A | OCIE1B | TOIE1 | OCIE0 | TOIE0)",
                "type": "bit",
                "address": 89
            }
        ],
        # /* state in general interrupt flag register*/
        "GIFR": [
            {
                "property": "(INTF1 | INTF0 | INTF2 | - | - | - | - | -)",
                "type": "bit",
                "address": 90
            }
        ],
        # /* status register */
        "SREG": [
            {
                "property": "(I | T | H | S | V | N | Z | C)",
                "type": "bit",
                "address": 95
            }
        ],
        # /* status register */
        "SPH": [
            {
                "property": "(- | - | - | - | - | SP10 | SP9 | SP8)",
                "type": "hex",
                "address": 94
            }
        ],
        # /* status register */
        "SPL": [
            {
                "property": "(SP7 | SP6 | SP5 |SP4 | SP3 | SP2 | SP1 | SP0)",
                "type": "hex",
                "address": 93
            }
        ],
    }
})

StaticJson = [Labels, HardwareRegisters]
if __name__ == "__main__":

    for j in StaticJson:
        print(json.dumps(j, sort_keys=False, indent=2, separators=(',', ': ')))
