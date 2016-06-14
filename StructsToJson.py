import json
from collections import OrderedDict
from google.protobuf.internal.decoder import EnumDecoder

from ParseCTypes import CTypesParser, StructDeclVisitor, EnumDeclVisitor


def printLeaf(fieldPath, fieldMame, fullyQualifiedName, type, bitSize, dimension):
    if bitSize is not None and bitSize is not "":
        bitSize = ":" + bitSize
    else:
        bitSize = ""

    if dimension is not None and dimension is not "":
        dimension = "[" + dimension + "]"
    else:
        dimension = ""

    print("%s%s <%s%s>" % (fullyQualifiedName, dimension, type, bitSize))


def traverseStructMembersDF(structs, nativeTypesToSize, enumTypesToValue, rootStructName, prefix, callback=printLeaf):
    for structSubDecl in structs[rootStructName]:
        structSubDeclTypeName = StructDeclVisitor.getStructTypeName(structSubDecl)
        structSubDeclName = structSubDecl.name

        if structSubDeclTypeName in nativeTypesToSize.keys() or \
                        structSubDeclTypeName in enumTypesToValue.keys():  # on enum/native type

            bitSize = None
            if structSubDecl.bitsize != None:
                bitSize = structSubDecl.bitsize.value

            dimension = None
            if hasattr(structSubDecl.type, "dim"):
                try:
                    dimension = int(structSubDecl.type.dim.value)
                except:
                    pass

            callback(prefix, structSubDeclName, prefix + "." + structSubDeclName, structSubDeclTypeName, bitSize,
                     dimension)
        else:  # on struct type
            traverseStructMembersDF(structs, nativeTypeToSize, enumTypesToValue,
                                    rootStructName=structSubDeclTypeName, callback=callback,
                                    prefix=prefix + "." + structSubDeclName)


class FieldDescription:
    def __init__(self, description, fieldPath, fieldName, typeName, startBit=None, bitsLength=None):
        self.startBit = startBit
        self.length = bitsLength
        self.endBit = None
        self.fieldPath = fieldPath
        self.fieldName = fieldName
        self.typeName = typeName

        if self.startBit != None:
            self.startBit = int(self.startBit)

        if self.length != None:
            self.length = int(self.length)
        else:
            self.length = 0

        if self.startBit != None and self.length != None:
            self.endBit = self.startBit + self.length - 1

        self.description = description

    def getFieldName(self):
        return self.fieldName

    def getFieldPath(self):
        return self.fieldPath

    def getTypeName(self):
        return self.typeName

    def getStartBit(self):
        return self.startBit

    def getEndBit(self):
        return self.endBit

    def getLength(self):
        return self.length

    def getDescription(self):
        return self.description

    def __str__(self):
        return "st[%s], \t\t len=%s, \t\t end[%s] \t\t desc=%s p=%s f=%s t=<%s>" % (
            self.startBit, self.length, self.endBit, self.description, self.fieldPath, self.fieldName, self.typeName)


class RegisterEntry:
    def __init__(self, name, type, bitSize=None, arraySize=None):
        self.name = name
        self.type = type
        self.fieldDescriptions = {}

        if bitSize != None:
            self.isBitField = True
            self.bitSize = bitSize

        if arraySize != None:
            self.isArray = True
            self.arraySize = arraySize

    def addFieldDescription(self, fieldDescription):
        self.fieldDescriptions[fieldDescription.getStartBit()] = fieldDescription


class LinearStructComposer:
    def __init__(self, typeToSizeMapping):
        self.linearFields = []
        self.typeToSize = typeToSizeMapping
        self.aggregatedLinearFields = OrderedDict()

    def consumeStructField(self, fieldPath, fieldName, fullyQualifiedName, type, bitSize, dimension):

        if bitSize == None:
            bitSize = self.typeToSize[type] * 8
        if dimension == None:
            startBit = 0
            if bitSize != None:
                if len(self.linearFields) > 0:
                    lastField = self.linearFields[-1]
                    startBit = (1 + lastField.getEndBit()) % (self.typeToSize[lastField.getTypeName()] * 8)
            fieldDescription = FieldDescription(fullyQualifiedName, fieldPath, fieldName, type, startBit=startBit,
                                                bitsLength=bitSize)
            self.linearFields.append(fieldDescription)
        else:
            for i in range(dimension):
                fieldDescription = FieldDescription("%s[%i]" % (fullyQualifiedName, i), fieldPath, fieldName, type,
                                                    startBit=0, bitsLength=8)
                self.linearFields.append(fieldDescription)

    def __createDescriptionDictIfNotAvailable(self, key):
        if key not in self.aggregatedLinearFields:
            self.aggregatedLinearFields[key] = OrderedDict()

    def aggregateDescriptions(self):

        currentBitFieldPath = None
        for description in reversed(self.linearFields):
            if description.getStartBit() != 0:
                currentBitFieldPath = description.getFieldPath()
                self.__createDescriptionDictIfNotAvailable(description.getFieldPath())
                self.aggregatedLinearFields[description.getFieldPath()][description.getStartBit()] = description
            else:
                if currentBitFieldPath == None:
                    self.__createDescriptionDictIfNotAvailable(description.getDescription())
                    self.aggregatedLinearFields[description.getDescription()][description.getStartBit()] = description
                else:
                    if currentBitFieldPath == description.getFieldPath():
                        self.__createDescriptionDictIfNotAvailable(description.getFieldPath())
                        self.aggregatedLinearFields[description.getFieldPath()][description.getStartBit()] = description
                        if description.getStartBit() == 0:
                            currentBitFieldPath = None




        # fieldPathsWithBitFields = {}
        # for description in self.linearFields:
        #     if description.getStartBit() != 0:
        #         fieldPathsWithBitFields[description.getFieldPath()] = None
        #
        # for description in self.linearFields:
        #     if description.getFieldPath() in fieldPathsWithBitFields:
        #         if description.getFieldPath() not in self.aggregatedLinearFields:
        #             self.aggregatedLinearFields[description.getFieldPath()] = OrderedDict()
        #
        #         lastFieldDescription = self.aggregatedLinearFields[description.getFieldPath()]
        #         lastFieldDescription[description.getStartBit()] = description
        #     else:
        #         dd = OrderedDict()
        #         dd[description.getStartBit()] = description
        #         self.aggregatedLinearFields[description.getDescription()] = dd


if __name__ == "__main__":
    nativeTypeToSize = {"int16_t": 2,
                        "uint16_t": 2,
                        "int8_t": 1,
                        "uint8_t": 1,
                        }

    ctp = CTypesParser()
    sdv = StructDeclVisitor()
    structs = ctp.getEntities(sdv)
    print("parsed structs")
    sdv.show()
    edv = EnumDeclVisitor()
    enumTypesToValue = ctp.getEntities(edv)

    print("\nparsed enums")
    edv.show()

    enumToSize = {}
    for enum in enumTypesToValue:
        enumToSize[enum] = 2

    typeToSizeMapping = dict(nativeTypeToSize.viewitems() | enumToSize.viewitems())

    composer = LinearStructComposer(typeToSizeMapping)
    traverseStructMembersDF(structs, nativeTypeToSize, enumTypesToValue, "ParticleState", "ParticleState",
                            callback=composer.consumeStructField)

    print("\nlinear ordered struct member list")
    for d in composer.linearFields:
        print ("%s" % d)

    composer.aggregateDescriptions()
    print("\naggregated linear ordered struct member list")
    for fieldPath in reversed(composer.aggregatedLinearFields.keys()):
        print ("%s" % fieldPath)
        fieldDescriptions = composer.aggregatedLinearFields[fieldPath]
        for startBitPosition in fieldDescriptions:
            print(" -- %s %s" % (startBitPosition, fieldDescriptions[startBitPosition]))

    # Todo:
    # generate json dumpabe from composer.aggregatedLinearFields
    # add "patch" to config to override autogenerated
    #       for 2byte types: treat as uint8_t for low byte, uint16 for high byte
    #       for type overriding of auto generated: uint8_t vs. char, hex, bin
    # add static code to config (i.e. MCU static register description)
