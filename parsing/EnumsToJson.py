import json
from collections import OrderedDict

import config.SourceConfig as sourceConfig
from parsing.ParseCTypes import CTypesParser, EnumDeclVisitor


class EnumsToJson:
    def __init__(self):
        ctp = CTypesParser(sourceConfig)
        parsedEnums = ctp.getEntities(EnumDeclVisitor())

        self.enums = OrderedDict()
        self.enums["enums"] = {}
        self.enums["enums"]["StateType"] = []

        for enum in parsedEnums:
            self.enums["enums"][enum] = []
            for enumerator in parsedEnums[enum]:
                self.enums["enums"][enum].append(enumerator.name)

    def show(self):
        print(json.dumps(self.enums, sort_keys=False, indent=2, separators=(',', ': ')))

    def getObject(self):
        return self.enums

    def getEnumNames(self):
        return self.enums["enums"].keys()


if __name__ == "__main__":
    etj = EnumsToJson()
    etj.show()
