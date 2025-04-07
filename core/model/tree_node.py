class DriveNode:
    def __init__(self, id, name, mime_type, is_checked=False):
        self.id = id
        self.name = name
        self.mime_type = mime_type
        self.is_checked = is_checked
        self.children = []

    def add_child(self, child: "DriveNode"):
        self.children.append(child)

    def __repr__(self):
        return f"DriveNode(name={self.name}, id={self.id}, type={self.mime_type}, children={len(self.children)})"