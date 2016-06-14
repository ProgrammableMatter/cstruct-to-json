import json
from collections import OrderedDict
from google.protobuf.internal.decoder import EnumDecoder

from ParseCTypes import CTypesParser, StructDeclVisitor, EnumDeclVisitor


def printLeaf(name, fullyQualifiedName, type, bitSize, dimension):
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

            callback(structSubDeclName, prefix + "." + structSubDeclName, structSubDeclTypeName, bitSize, dimension)
        else:  # on struct type
            traverseStructMembersDF(structs, nativeTypeToSize, enumTypesToValue,
                                    rootStructName=structSubDeclTypeName, callback=callback,
                                    prefix=prefix + "." + structSubDeclName)

class FieldDescription:
    def __init__(self, description, typeName, startBit = None, bitsLength = None):
        self.startBit = startBit
        self.length = bitsLength
        self.endBit = None
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
        return "st[%s], \t\t len=%s, \t\t end[%s] \t\t desc=[%s] <%s>" %(self.startBit, self.length, self.endBit, self.description, self.typeName)

class RegisterEntry:
    def __init__(self, name, type, bitSize=None, arraySize=None):
        self.name = name
        self.type = type
        self.fieldDescriptions = {}

        if bitSize != None:
            self.isBitField =True
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

    def consumeStructField(self, name, fullyQualifiedName, type, bitSize, dimension):

        if bitSize == None:
            bitSize = self.typeToSize[type] * 8
        if dimension == None:
            startBit = 0
            if bitSize != None:
                if len(self.linearFields) > 0:
                    lastField = self.linearFields[-1]
                    startBit = (1 + lastField.getEndBit()) % (self.typeToSize[lastField.getTypeName()] * 8)
            fieldDescription = FieldDescription(fullyQualifiedName, type, startBit=startBit, bitsLength=bitSize)
            self.linearFields.append(fieldDescription)
        else:
            for i in range(dimension):
                fieldDescription = FieldDescription("%s[%i]" % (fullyQualifiedName, i), type, startBit=0, bitsLength=8)
                self.linearFields.append(fieldDescription)


if __name__ == "__main__":
    nativeTypeToSize = {"int16_t": 2,
                        "uint16_t": 2,
                        "int8_t": 1,
                        "uint8_t": 1,
                        }

    ctp = CTypesParser()
    structs = ctp.getEntities(StructDeclVisitor())
    enumTypesToValue = ctp.getEntities(EnumDeclVisitor())

    enumToSize = {}
    for enum in enumTypesToValue:
        enumToSize[enum] = 2

    typeToSizeMapping = dict(nativeTypeToSize.viewitems() | enumToSize.viewitems())

    composer = LinearStructComposer(typeToSizeMapping)
    traverseStructMembersDF(structs, nativeTypeToSize, enumTypesToValue, "ParticleState", "ParticleState", callback=composer.consumeStructField)

    print("linear ordered struct member list")
    for d in composer.linearFields:
        print ("%s" % d)
