import json
from Tkinter import *
from collections import OrderedDict

from config import JsonConfig
from config.JsonConfig import NativeTypeToSimulatorType, NativeTypeToSize, DefaultStructByteSize, TypeOverrides
from parsing.EnumsToJson import EnumsToJson
from parsing.ParseCTypes import CTypesParser, StructDeclVisitor, EnumDeclVisitor

Verbose = True


def printLeaf(fieldPath, fieldMame, fullyQualifiedName, type, bitSize, dimension):
    if bitSize is not None and bitSize is not "":
        bitSize = ":" + bitSize
    else:
        bitSize = ""

    if dimension is not None and dimension is not "":
        dimension = "[" + dimension + "]"
    else:
        dimension = ""

    if Verbose:
        print("%s%s <%s%s>" % (fullyQualifiedName, dimension, type, bitSize))


def traverseStructMembersDF(structs, nativeTypesToSize, enumTypesToValue, rootStructName, prefix, callback=printLeaf):
    for structSubDecl in structs[rootStructName]:
        structSubDeclTypeName = StructDeclVisitor.getStructTypeName(structSubDecl)
        structSubDeclName = structSubDecl.name

        dimension = None
        if hasattr(structSubDecl.type, "dim"):
            dimension = int(structSubDecl.type.dim.value)

        if structSubDeclTypeName in nativeTypesToSize.keys() or \
                        structSubDeclTypeName in enumTypesToValue.keys():  # on enum/native type

            bitSize = None
            if structSubDecl.bitsize != None:
                bitSize = structSubDecl.bitsize.value

            callback(prefix, structSubDeclName, prefix + "." + structSubDeclName, structSubDeclTypeName, bitSize,
                     dimension)
        else:  # on struct type
            if dimension != None:
                for dim in range(dimension):
                    traverseStructMembersDF(structs, nativeTypesToSize, enumTypesToValue,
                                            rootStructName=structSubDeclTypeName, callback=callback,
                                            prefix=prefix + "." + structSubDeclName + "[" + str(dim) + "]")
            else:
                traverseStructMembersDF(structs, nativeTypesToSize, enumTypesToValue,
                                        rootStructName=structSubDeclTypeName, callback=callback,
                                        prefix=prefix + "." + structSubDeclName)


def appendEnumToSize(enumToSize, typeToSizeMapping):
    for enum in enumToSize.keys():
        typeToSizeMapping[enum] = 2


def appendEnumNames(enumDict, nativeTypeToSimulatorTypeMaping):
    for enum in enumDict.keys():
        nativeTypeToSimulatorTypeMaping[enum] = enum


class FieldDescription:
    def __init__(self, description, fieldPath, fieldName, typeName, arrayIdx=None, isBitField=False, startBit=None,
                 bitsLength=None):
        self.startBit = startBit
        self.length = bitsLength
        self.endBit = None
        self.fieldPath = fieldPath
        self.fieldName = fieldName
        self.typeName = typeName
        self.arrayIndex = arrayIdx

        self.__isBitField = isBitField

        if self.startBit != None:
            self.startBit = int(self.startBit)

        if self.length != None:
            self.length = int(self.length)
        else:
            self.length = 0

        if self.startBit != None and self.length != None:
            self.endBit = self.startBit + self.length - 1

        self.description = description

    def getArrayIdx(self):
        return self.arrayIndex

    def isArrayField(self):
        return self.arrayIndex != None

    def isBitField(self):
        return self.__isBitField

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
        return "st[%s]\tlen=%s\tend[%s]\tdesc=%s p=%s f=%s t=<%s>" % (
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

        isBitField = True
        if bitSize == None:
            isBitField = False
            bitSize = self.typeToSize[type] * 8
        if dimension == None:
            startBit = 0
            if bitSize != None:
                if len(self.linearFields) > 0:
                    lastField = self.linearFields[-1]
                    startBit = (1 + lastField.getEndBit()) % (self.typeToSize[lastField.getTypeName()] * 8)
            fieldDescription = FieldDescription(fullyQualifiedName, fieldPath, fieldName, type, arrayIdx=None,
                                                isBitField=isBitField,
                                                startBit=startBit,
                                                bitsLength=bitSize)
            self.linearFields.append(fieldDescription)
        else:  # on array decl
            for i in range(dimension):
                fieldDescription = FieldDescription("%s[%i]" % (fullyQualifiedName, i), fieldPath, fieldName, type,
                                                    arrayIdx=i, isBitField=isBitField, startBit=0, bitsLength=8)
                self.linearFields.append(fieldDescription)

    def __createDescriptionDictIfNotAvailable(self, key):
        if key not in self.aggregatedLinearFields:
            self.aggregatedLinearFields[key] = OrderedDict()

    def aggregateDescriptions(self):
        currentBitFieldId = 0
        for description in reversed(self.linearFields):
            if description.isBitField():
                bitFieldKey = description.getFieldPath() + "<" + str(currentBitFieldId) + ">"
                self.__createDescriptionDictIfNotAvailable(bitFieldKey)
                self.aggregatedLinearFields[bitFieldKey][description.getStartBit()] = description
                if description.getStartBit() == 0:
                    currentBitFieldId += 1
            else:
                bitFieldKey = description.getDescription() + "<" + str(currentBitFieldId) + ">"
                self.__createDescriptionDictIfNotAvailable(bitFieldKey)
                self.aggregatedLinearFields[bitFieldKey][description.getStartBit()] = description
                currentBitFieldId += 1


class LinearStructFieldsToJson:
    jsonSource = None
    doInfer2ndByteFromUint16_t = True

    def __init__(self):
        pass

    def __compactBitFieldDescriptions(self, fieldDescriptions):
        desc = "("
        isFirst = True
        for fieldDescription in fieldDescriptions:
            d = fieldDescriptions[fieldDescription]
            if not isFirst:
                desc += " | "
            isFirst = False

            if d.getStartBit() == d.getEndBit():
                fromTo = str(d.getStartBit())
            else:
                fromTo = str(d.getStartBit()) + ":" + str(d.getEndBit())

            desc += d.getFieldName() + "[" + fromTo + "]"
        return desc + ")"

    def __infer2ndByte(self, startAddressLabel, addressOffet, property, fieldDescription, entries, type, nativeTypeToSize):
        if self.doInfer2ndByteFromUint16_t and \
                        fieldDescription.getTypeName() in nativeTypeToSize and \
                        2 == nativeTypeToSize[fieldDescription.getTypeName()]:
            p2 = property + "[1]"
            if startAddressLabel != "":
                a2 = startAddressLabel + "+" + str(addressOffet + 1)
            else:
                a2 = addressOffet + 1
            entries[fieldDescription.getFieldPath()].append(
                {"property": p2, "type": type, "address": a2})

    def toJson(self, structFields, nativeTypeToSize={}, nativeTypeToSimulatorType={}, startAddressLabel=""):

        addressOffet = 0
        entries = OrderedDict()
        for field in structFields:

            fieldDescription = structFields[field][structFields[field].keys()[0]]
            if fieldDescription.getFieldPath() not in entries:
                entries[fieldDescription.getFieldPath()] = []

            fieldTypeName = fieldDescription.getTypeName()

            if fieldDescription.isBitField():
                type = nativeTypeToSimulatorType["bitfield"]
                property = self.__compactBitFieldDescriptions(structFields[field])
            else:
                if fieldDescription.isArrayField():
                    property = structFields[field][0].getFieldName() + "[" + str(fieldDescription.getArrayIdx()) + "]"
                else:
                    property = structFields[field][0].getFieldName()
                type = nativeTypeToSimulatorType[fieldTypeName]

                self.__infer2ndByte(startAddressLabel, addressOffet, property, fieldDescription, entries,
                                    type, nativeTypeToSize)

            if startAddressLabel != "":
                address = startAddressLabel + "+" + str(addressOffet)
            else:
                address = addressOffet
            addressOffet += nativeTypeToSize[fieldTypeName]

            entries[fieldDescription.getFieldPath()].append({"property": property, "type": type, "address": address})
        self.jsonSource = OrderedDict({"structs": entries})

    def show(self):
        print(json.dumps(self.jsonSource, sort_keys=False, indent=2, separators=(',', ': ')))

    def getDump(self):
        return json.dumps(self.jsonSource, sort_keys=False, indent=2, separators=(',', ': '))

    def getObject(self):
        return self.jsonSource


def parseEnumTypesAndStructs():
    ctp = CTypesParser()
    sdv = StructDeclVisitor()
    structs = ctp.getEntities(sdv)

    if Verbose:
        print("parsed structs")

    if Verbose:
        sdv.show()
    edv = EnumDeclVisitor()
    parsedEnums = ctp.getEntities(edv)

    if Verbose:
        print("\nparsed enums")
        edv.show()
    return structs, parsedEnums


def aggregateFields(structs, enumTypesToByteSize):
    enumToSize = {}
    for enum in enumTypesToByteSize:
        enumToSize[enum] = DefaultStructByteSize
    typeToSizeMapping = dict(NativeTypeToSize.viewitems() | enumToSize.viewitems())
    composer = LinearStructComposer(typeToSizeMapping)
    traverseStructMembersDF(structs, NativeTypeToSize, enumTypesToByteSize, "ParticleState", "ParticleState",
                            callback=composer.consumeStructField)

    if Verbose:
        print("\nlinear ordered struct member list")
        for d in composer.linearFields:
            print ("%s" % d)
    composer.aggregateDescriptions()
    structFieldToDescription = OrderedDict()

    if Verbose:
        print("\naggregated linear ordered struct member list")
    for fieldPath in reversed(composer.aggregatedLinearFields.keys()):
        if Verbose:
            print ("%s" % fieldPath)
        fieldDescriptions = composer.aggregatedLinearFields[fieldPath]
        structFieldToDescription[fieldPath] = OrderedDict()
        for startBitPosition in reversed(fieldDescriptions.keys()):
            field = fieldDescriptions[startBitPosition]
            if Verbose:
                print(" -- %s" % (field))
            structFieldToDescription[fieldPath][field.getStartBit()] = field
    return enumToSize, structFieldToDescription


def generateCStructJson(enumToSize, structFieldToDescription):
    appendEnumToSize(enumToSize, NativeTypeToSize)
    appendEnumNames(enumToSize, NativeTypeToSimulatorType)

    lsfj = LinearStructFieldsToJson()
    lsfj.toJson(structFieldToDescription, nativeTypeToSize=NativeTypeToSize,
                nativeTypeToSimulatorType=NativeTypeToSimulatorType, startAddressLabel="globalStateBase")
    # lsfj.show()
    return lsfj.getObject(), lsfj.getDump()


class Gui:
    def __init__(self, txt):
        self.rootWindow = Tk()
        self.rootWindow.resizable(True, False)
        self.rootWindow.title("content it copied to clipboard")

        self.rootWindow.clipboard_clear()
        self.rootWindow.clipboard_append(txt)

        sb = Scrollbar(self.rootWindow)
        sb.pack(side=RIGHT, fill=Y)
        textField = Text(self.rootWindow, height=30, width=74)
        textField.pack(side=LEFT, fill=Y)
        sb.config(command=textField.yview)
        textField.config(yscrollcommand=sb.set)
        textField.insert(END, "\n" + txt + "\n")

        self.rootWindow.mainloop()


def aggregateToJsonDumpableDescription(structsObject, enumsObject):
    jsonDescription["enums"] = enumsObject["enums"]

    # add sizeof structs
    jsonDescription["sizeofTypes"] = OrderedDict()
    for enumType in enumToSize:
        jsonDescription["sizeofTypes"][enumType] = DefaultStructByteSize

    # add labels
    jsonDescription["labels"] = JsonConfig.Labels["labels"]

    jsonDescription["structs"] = OrderedDict()
    # append staticly defined register description
    for key in JsonConfig.HardwareRegisters["structs"]:
        jsonDescription["structs"][key] = JsonConfig.HardwareRegisters["structs"][key]

    # append parsed c structs
    for key in structsObject["structs"]:
        jsonDescription["structs"][key] = structsObject["structs"][key]

    if Verbose:
        print("\ntype overridings")
    # override types
    for descriptionSetKey in jsonDescription["structs"]:
        for description in jsonDescription["structs"][descriptionSetKey]:
            # jsonDescription["structs"][descriptionSet][key]
            for override in TypeOverrides:
                substring = override["property"]
                oldType = override["oldType"]
                newType = override["newType"]
                if substring in description["property"] and oldType == description["type"]:
                    if Verbose:
                        print(descriptionSetKey + "." + description["property"] + " " + description[
                            "type"] + " <== " + newType)
                    description["type"] = newType

    return jsonDescription


if __name__ == "__main__":
    structs, parsedEnums = parseEnumTypesAndStructs()
    enumToSize, structFieldToDescription = aggregateFields(structs, parsedEnums)

    jsonDescription = OrderedDict()

    etj = EnumsToJson()
    enumsObject = etj.getObject()

    structsObject, jsonDump = generateCStructJson(enumToSize, structFieldToDescription)
    # print(jsonDump)

    jsonDescription = aggregateToJsonDumpableDescription(structsObject, enumsObject)

    # print(json.dumps(jsonDescription, sort_keys=False, indent=2, separators=(',', ': ')))
    Gui(json.dumps(jsonDescription, sort_keys=False, indent=2, separators=(',', ': ')))
