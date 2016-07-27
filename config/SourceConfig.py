import os

__baseDir = os.path.dirname(os.path.realpath('__file__'))
__subDir = "../../src/avr-common/utils/"

defines = [
    r'-DSIMULATION',
]
includes = [
    r'-Iutils/fake_libc_include/',
    r'-I%s/%s' % (__baseDir, __subDir),
]

sourceRoots = [
    __baseDir + "/" + __subDir + "uc-core/communication-protocol/CommunicationProtocolTypes.h",
    __baseDir + "/" + __subDir + "uc-core/communication/ManchesterDecodingTypes.h",
    __baseDir + "/" + __subDir + "uc-core/communication/CommunicationTypes.h",
    __baseDir + "/" + __subDir + "uc-core/particle/ParticleStateTypes.h",
]
