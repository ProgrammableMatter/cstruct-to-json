import sys
from config import SourceConfig as sourceConfig

from pycparser import parse_file, c_ast

Verbose = False

class StructDeclVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.structDecls = {}

    def visit_Struct(self, node):
        if node.name not in self.structDecls:
            self.structDecls[node.name] = []
        else:
            return
        for structSubDecls in node.decls:
            self.structDecls[node.name].append(structSubDecls)

    def getEnums(self):
        return self.structDecls

    def show(self):
        for structDecl in self.structDecls:
            print("struct %s" % structDecl)
            for structSubDecl in self.structDecls[structDecl]:
                if structSubDecl.bitsize != None:
                    print("  -- %s <%s:%s>" % (
                    structSubDecl.name, StructDeclVisitor.getStructTypeName(structSubDecl), structSubDecl.bitsize.value))
                else:
                    print("  -- %s <%s>" % (structSubDecl.name, StructDeclVisitor.getStructTypeName(structSubDecl)))

    @staticmethod
    def getStructTypeName(structSubDecl):
        root = structSubDecl
        if hasattr(root, "names"):
            return root.names[0]

        while hasattr(root, "type"):
            if hasattr(root, "names"):
                return root.names[0]
            root = getattr(root, "type")

        if hasattr(root, "names"):
            return root.names[0]
        return "NA"


class EnumDeclVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.enums = {}

    def visit_Enum(self, node):
        if node.name not in self.enums:
            self.enums[node.name] = []
        else:
            return

        for enumerator in node.values.enumerators:
            self.enums[node.name].append(enumerator)

    def getEnums(self):
        return self.enums

    def show(self):
        for enum in self.enums:
            print("enum %s" % enum)
            for enumerator in self.enums[enum]:
                print("  -- %s" % enumerator.name)


class CTypesParser:
    def __init__(self, configModule=sourceConfig):
        self.asts = []
        cpp_path = '/usr/bin/gcc'
        cpp_args = ["-E"]
        for include in configModule.includes:
            cpp_args.append(include)

        for define in configModule.defines:
            cpp_args.append(define)

        for fileName in configModule.sourceRoots:
            self.asts.append(parse_file(fileName, use_cpp=True, cpp_path=cpp_path, cpp_args=cpp_args))
            pass

    def getEntities(self,  visitor=EnumDeclVisitor()):
        for ast in self.asts:
            visitor.visit(ast)
        return visitor.getEnums()

    def showEntities(self,  visitor=EnumDeclVisitor()):
        for ast in self.asts:
            visitor.visit(ast)
        visitor.show()

    def show(self):
        for ast in self.asts:
            ast.show()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        sourceConfig.sourceRoots = [sys.argv[1]]

    # ctp = CTypesParser(sourceConfig)
    # ctp.show()

    # ctp.getEntities(EnumDeclVisitor())
    # ctp.showEntities(EnumDeclVisitor())

    ctp = CTypesParser(sourceConfig)
    # ctp.getEntities(StructDeclVisitor())
    if Verbose:
        ctp.showEntities(StructDeclVisitor())

