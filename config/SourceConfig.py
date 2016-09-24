import os

__homeDir = os.getenv("HOME")
__subDir = "msc/git/particle-firmware/src"

defines = [
    r'-DSIMULATION',
    # typedef workaround: typedefs are not supported by the underlying pycparser
    r'-DC_STRUCTS_TO_JSON_PARSER_TYPEDEF_NOT_SUPPORTED_SUPPRESS_REGULAR_TYPEDEFS',
    # r'-DSampleValueType uint16_t',
    # r'-DCalculationType float',
    # r'-DDeviationType float',
]
includes = [
    r'-Iutils/fake_libc_include/',
    r'-I%s/%s/avr-common/utils/' % (__homeDir, __subDir),
]

sourceRoots = [
    __homeDir + "/" + __subDir + "/avr-common/utils/uc-core/communication-protocol/CommunicationProtocolTypes.h",
    __homeDir + "/" + __subDir + "/avr-common/utils/uc-core/communication/ManchesterDecodingTypes.h",
    __homeDir + "/" + __subDir + "/avr-common/utils/uc-core/communication/CommunicationTypes.h",
    __homeDir + "/" + __subDir + "/avr-common/utils/uc-core/synchronization/SynchronizationTypes.h",
    __homeDir + "/" + __subDir + "/avr-common/utils/uc-core/periphery/PeripheryTypes.h",
    __homeDir + "/" + __subDir + "/avr-common/utils/uc-core/particle/ParticleStateTypes.h",
]
