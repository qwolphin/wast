# single
@attrs.define()
class TemplateVariable:
    id: str = attrs.field(converter=convert_identifier)

    def _to_builtin(self):
        raise TypeError(f"{self} has no related ast.AST node")

    @classmethod
    def _from_builtin(cls, node):
        raise TypeError(f"{self} has no related ast.AST node")

    def _transform(self, node_transformer, context=TransformerContext()):
        context = TransformerContext(parents=[self, *context.parents])
        return TemplateVariable(id=self.id)

    def _children(self):
        yield self
