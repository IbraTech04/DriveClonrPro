from __future__ import annotations
# Class which represents a node in a tree
# This is the tree that will be traversesd (most likly in-order) to get the files to download

class TreeNode:
    """
    Class representing a node in an IbraTree
    
    ==== Public Attributes ====
    root: string - A file ID representing the file at this node
    children: list[TreeNode] - A list of the children of this node
    
    === Representation Invariants ===
    - root is a valid file ID
    - children is a list of TreeNode objects
    - If children is None, then this node is a file, not a folder
    - If root is None, then this node is the root of the tree
    """
    
    root: str
    children: list[TreeNode]
    
    def __init__(self, root: str, children: list[TreeNode] = []) -> None:
        self.root = root
        self.children = children
    
    def add_child(self, child: TreeNode) -> None:
        """
        Add a child to this node
        """
        self.children.append(child)
    
    def get_child(self, child_id: str) -> TreeNode:
        """
        Return the child with the given ID
        """
        for child in self.children:
            if child.root == child_id:
                return child
        return None