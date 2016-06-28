import os

__homeDir = os.getenv("HOME")
__subDir = "msc/git/software/src"

defines = [
    r'-DSIMULATION',
]
includes = [
    r'-Iutils/fake_libc_include/',
    r'-I%s/%s/avr/avr-common/utils/' % (__homeDir, __subDir),
]

sourceRoots = [
    __homeDir + "/" + __subDir + "/avr/avr-common/utils/uc-core/communication-protocol/CommunicationProtocolTypes.h",
    __homeDir + "/" + __subDir + "/avr/avr-common/utils/uc-core/communication/ManchesterDecodingTypes.h",
    __homeDir + "/" + __subDir + "/avr/avr-common/utils/uc-core/communication/CommunicationTypes.h",
    __homeDir + "/" + __subDir + "/avr/avr-common/utils/uc-core/communication-protocol/InterpreterTypes.h",
    __homeDir + "/" + __subDir + "/avr/avr-common/utils/uc-core/particle/ParticleStateTypes.h",
]
