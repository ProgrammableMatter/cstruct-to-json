import json
import sys
import config.SourceConfig as sourceConfig
from ParseCTypes import CTypesParser, EnumDeclVisitor

if __name__ == "__main__":
    if len(sys.argv) > 1:
        sourceConfig.sourceRoots = [sys.argv[1]]

    ctp = CTypesParser(sourceConfig)
    enums =  ctp.getEntities(EnumDeclVisitor())

    Enums = {}
    Enums["enums"] = {}
    Enums["enums"]["StateType"] = []

    for enum in enums:
        Enums["enums"][enum] = []
        for e in enums[enum]:
            Enums["enums"][enum].append(e.name)

    print(json.dumps(Enums, sort_keys=False, indent=2, separators=(',', ': ')))