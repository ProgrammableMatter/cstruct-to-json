import os

__homeDir = os.getenv("HOME")
__subDir = "msc/git/particle-firmware/src"

defines = [
    r'-DSIMULATION',
]
includes = [
    r'-Iutils/fake_libc_include/',
    r'-I%s/%s/avr-common/utils/' % (__homeDir, __subDir),
]

sourceRoots = [
    __homeDir + "/" + __subDir + "/avr-common/utils/uc-core/communication-protocol/CommunicationProtocolTypes.h",
    __homeDir + "/" + __subDir + "/avr-common/utils/uc-core/communication/ManchesterDecodingTypes.h",
    __homeDir + "/" + __subDir + "/avr-common/utils/uc-core/communication/CommunicationTypes.h",
    __homeDir + "/" + __subDir + "/avr-common/utils/uc-core/particle/ParticleStateTypes.h",
]
