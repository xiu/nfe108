from app import Server, db
import yaml
import sys

# constructors for puppet to be able to read our yaml :)
def construct_ruby_object(loader, suffix, node):
    return loader.construct_yaml_map(node)
def construct_ruby_sym(loader, node):
    return loader.construct_yaml_str(node)
yaml.add_multi_constructor(u"!ruby/object:", construct_ruby_object)
yaml.add_constructor(u"!ruby/sym", construct_ruby_sym)

if __name__ == "__main__":
    host = sys.argv[1]
    server = Server.query.filter_by(host=host).one()
    enc = server.get_enc()
    print(yaml.safe_dump(enc, default_flow_style=False))

