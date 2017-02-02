"""Trees for Treemap

=== Module Description ===
This module contains the basic tree interface required by the treemap
visualiser.
"""
import os
from random import randint
import math


class AbstractTree:
    """A tree that is compatible with the treemap visualiser.

    This is an abstract class that should not be instantiated directly.

    === Public Attributes ===
    @type data_size: int
        The total size of all leaves of this tree.
    @type colour: (int, int, int)
        The RGB colour value of the root of this tree.
        Note: only the colours of leaves will influence what the user sees.

    === Private Attributes ===
    @type _root: obj | None
        The root value of this tree, or None if this tree is empty.
    @type _subtrees: list[AbstractTree]
        The subtrees of this tree.
    @type _parent_tree: AbstractTree | None
        The parent tree of this tree; i.e., the tree that contains this tree
        as a subtree, or None if this tree is not part of a larger tree.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.
    - colour's elements are in the range 0-255.

    - If _root is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.
    - _subtrees IS allowed to contain empty subtrees (this makes deletion
      a bit easier).

    - if _parent_tree is not empty, then self is in _parent_tree._subtrees
    """
    def __init__(self, root, subtrees, data_size=0):
        """Initialize a new AbstractTree.

        If <subtrees> is empty, <data_size> is used to initialize this tree's
        data_size. Otherwise, the <data_size> parameter is ignored, and this
        tree's data_size is computed from the data_sizes of the subtrees.

        If <subtrees> is not empty, <data_size> should not be specified.

        This method sets the _parent_tree attribute for each subtree to self.

        A random colour is chosen for this tree.

        Precondition: if <root> is None, then <subtrees> is empty.

        @type self: AbstractTree
        @type root: object
        @type subtrees: list[AbstractTree]
        @type data_size: int
        @rtype: None
        """
        self._root = root
        self._subtrees = subtrees
        self._parent_tree = None

        # 1. Initialize self.colour and self.data_size,
        # according to the docstring.
        self.colour = (randint(0, 255), randint(0, 255), randint(0, 255))
        self.data_size = data_size
        if self._subtrees:
            # 2. Properly set all _parent_tree attributes in self._subtrees
            for subtree in self._subtrees:
                self.data_size += subtree.data_size
                subtree._parent_tree = self

    def is_empty(self):
        """Return True if this tree is empty.

        @type self: AbstractTree
        @rtype: bool
        """
        return self._root is None

    def generate_treemap(self, rect):
        """Run the treemap algorithm on this tree and return the rectangles.

        Each returned tuple contains a pygame rectangle and a colour:
        ((x, y, width, height), (r, g, b)).

        One tuple should be returned per non-empty leaf in this tree.

        @type self: AbstractTree
        @type rect: (int, int, int, int)
            Input is in the pygame format: (x, y, width, height)
        @rtype: list[((int, int, int, int), (int, int, int))]
        """
        if self.data_size == 0:
            return []
        elif len(self._subtrees) == 0:
            return [(rect, self.colour)]

        # The "tuple unpacking assignment" is used to easily extract
        # coordinates of a rectangle:
        # x, y, width, height = rect
        x, y, w, h = rect
        result = []

        # These 2 variables ensure that the last subtree
        # fills the rest of the rectangle, since (x, y) may not be
        # the origin (0, 0).
        # NOTE: Due to rounding of <local_w> or <local_h>, the
        #       proportion of the last rectangle may not be truly
        #       correct.
        ini_x = x
        ini_y = y

        # If deletion occured, a tree may be empty.
        # So, <last_tree> is used to keep track of the last tree with
        # data_size > 0: (AbstractTree, int, int) -- (tree, index, x or y)
        last_tree = (None, 0, 0)

        for i in range(len(self._subtrees)):
            subtree = self._subtrees[i]

            # If width > height, form vertical rectangles;
            # only width should vary.
            if w > h:
                if i < len(self._subtrees) - 1:
                    local_w = int(subtree.data_size / self.data_size * w)
                else:
                    local_w = w - x + ini_x
                sub_treemap = subtree.generate_treemap((x, y, local_w, h))
                result.extend(sub_treemap)
                if sub_treemap:
                    last_tree = (subtree, len(sub_treemap), x)

                # If the last tree in _subtrees was empty,
                # this block of code stretches the last valid tree.
                if i == len(self._subtrees) - 1:
                    x = last_tree[2]
                    result = result[:-last_tree[1]]
                    local_w = w - x + ini_x
                    sub_treemap = last_tree[0].generate_treemap((x, y,
                                                                 local_w, h))
                    result.extend(sub_treemap)

                x += local_w

            # If width <= height, form horizontal rectangles;
            # only height should vary.
            else:
                if i < len(self._subtrees) - 1:
                    local_h = int(subtree.data_size / self.data_size * h)
                else:
                    local_h = h - y + ini_y
                sub_treemap = subtree.generate_treemap((x, y, w, local_h))
                result.extend(sub_treemap)
                if sub_treemap:
                    last_tree = (subtree, len(sub_treemap), y)

                # If the last tree in _subtrees was empty,
                # this block of code stretches the last valid tree.
                if i == len(self._subtrees) - 1:
                    y = last_tree[2]
                    result = result[:-last_tree[1]]
                    local_h = h - y + ini_y
                    sub_treemap = last_tree[0].generate_treemap((x, y,
                                                                 w, local_h))
                    result.extend(sub_treemap)

                y += local_h

        s = ''
        for i in result:
            s += str(i[0]) + '\n'
        file = open('testingmaterial.txt', 'w')
        file.write(s)
        file.close()

        return result

    def get_separator(self):
        """Return the string used to separate nodes in the string
        representation of a path from the tree root to a leaf.

        Used by the treemap visualiser to generate a string displaying
        the items from the root of the tree to the currently selected leaf.

        This should be overridden by each AbstractTree subclass, to customize
        how these items are separated for different data domains.

        @type self: AbstractTree
        @rtype: str
        """
        raise NotImplementedError

    def leaf_at(self, pos, rect):
        """Return the leaf at the given position

        Used by treemap visualiser to return the leaf at
        the cursor's position.

        The algorithm resembles generate_treemap in order to
        determine which rectangle is the leaf according to <pos>.
        * -- this asterisk indicates that the block of code is explained
             in generate_treemap

        @type self: AbstractTree
        @type pos: (int, int)
        @type rect: (int, int, int, int)
        @rtype: AbstractTree | None

        >>> fst = FileSystemTree('my-data')
        >>> leaf = fst.leaf_at((0, 0), (0, 0, 1024, 768))
        >>> leaf.data_size
        8308
        """
        x, y, w, h = rect

        if self.data_size == 0:
            return None
        elif len(self._subtrees) == 0:
            if x <= pos[0] <= x + w and y <= pos[1] <= y + h:
                return self
            else:
                return None

        # *
        ini_x = x
        ini_y = y

        # If deletion occured, a tree may be empty.
        # So, <last_tree> is used to keep track of the last rectangle
        # displayed: (AbstractTree, int, int) -- (tree, x, y)
        last_tree = (None, 0, 0)
        result = None

        for i in range(len(self._subtrees)):
            if result:  # Exit this loop if a leaf is found.
                return result
            subtree = self._subtrees[i]

            # *
            if w > h:
                local_w = int(subtree.data_size / self.data_size * w)
                if subtree.data_size > 0:
                    last_tree = (subtree, x, y)
                    result = subtree.leaf_at(pos, (x, y, local_w, h))

                # If the last tree in _subtrees was empty,
                # this block of code stretches the last valid tree
                # checks the position again of this tree.
                if i == len(self._subtrees) - 1:
                    local_w = w - last_tree[1] + ini_x
                    result = last_tree[0].leaf_at(pos,
                                                  (last_tree[1], last_tree[2],
                                                   local_w, h))
                x += local_w
            # *
            else:
                local_h = int(subtree.data_size / self.data_size * h)
                if subtree.data_size > 0:
                    last_tree = (subtree, x, y)
                    result = subtree.leaf_at(pos, (x, y, w, local_h))

                # If the last tree in _subtrees was empty,
                # this block of code stretches the last valid tree
                # checks the position again of this tree.
                if i == len(self._subtrees) - 1:
                    local_h = h - last_tree[2] + ini_y
                    result = last_tree[0].leaf_at(pos,
                                                  (last_tree[1], last_tree[2],
                                                   w, local_h))
                y += local_h

        return result

    def delete(self):
        """Remove this tree from its parent by making <self> an empty tree.

        This tree's ancestors' data size will also be updated.

        NOTE: Since delete is intended to be used on a leaf,
              setting <self._subtrees> to [] is redundant.

        @type self: AbstractTree
        @rtype: None
        >>> fst = FileSystemTree('my-data')
        >>> leaf = fst.leaf_at((0, 0), (0, 0, 1024, 768))
        >>> leaf.get_separator()
        'my-data\\\\2\\\\1\\\\1\\\\1.txt'
        >>> leaf.delete()
        >>> leaf = fst.leaf_at((0, 0), (0, 0, 1024, 768))
        >>> leaf.get_separator()
        'my-data\\\\2\\\\1\\\\1\\\\2.txt'
        """
        self._root = None
        self._parent_tree.update_size(self.data_size * -1)
        self._parent_tree = None
        self.data_size = 0

    def update_size(self, size_change):
        """Update this tree's data size according to <size_change> parameter.

        This also affects its ancestors if any.

        @type self: AbstractTree
        @type size_change: int
        @rtype: None

        >>> fst = FileSystemTree('my-data')
        >>> leaf = fst.leaf_at((0, 0), (0, 0, 1024, 768))
        >>> leaf.data_size
        8308
        >>> leaf.update_size(100)
        >>> leaf.data_size
        8408
        >>> leaf.update_size(1000 * -2)
        >>> leaf.data_size
        6408
        """
        self.data_size += size_change
        if self._parent_tree:
            self._parent_tree.update_size(size_change)

    def change_prop(self, proportion):
        """Change this tree's data size depending on the given proportion.

        NOTE: Data size will never go below 1.

        @type self: AbstractTree
        @type proportion: float
        @rtype: None
        >>> fst = FileSystemTree('my-data')
        >>> leaf = fst.leaf_at((0, 0), (0, 0, 1024, 768))
        >>> leaf.data_size
        8308
        >>> leaf.change_prop(0.25)
        >>> leaf.data_size
        10385
        >>> leaf.change_prop(0.4 * -1)
        >>> leaf.data_size
        6231
        """
        if proportion >= 0:  # increase size
            size_change = math.ceil(self.data_size * proportion)
        else:  # decrease size
            size_change = math.ceil(self.data_size * abs(proportion)) * -1

        if self.data_size + size_change < 1:
            size_change = self.data_size - 1

        self.update_size(size_change)


class FileSystemTree(AbstractTree):
    """A tree representation of files and folders in a file system.

    The internal nodes represent folders, and the leaves represent regular
    files (e.g., PDF documents, movie files, Python source code files, etc.).

    The _root attribute stores the *name* of the folder or file, not its full
    path. E.g., store 'Documents', not '/Users/James/Documents'

    The data_size attribute for regular files as simply the size of the file,
    as reported by os.path.getsize.
    """
    def __init__(self, path):
        """Store the file tree structure contained in the given file or folder.

        Precondition: <path> is a valid path for this computer.

        @type self: FileSystemTree
        @type path: str
        @rtype: None
        """
        if os.path.isdir(path):  # if the path is a folder
            entries = os.listdir(path)
            tree_list = []

            # Form a FileSystemTree for each entry in this folder
            for entry in entries:
                tree_list.append(FileSystemTree(os.path.join(path, entry)))
            AbstractTree.__init__(self, os.path.basename(path), tree_list)

        else:  # if the path is a file
            AbstractTree.__init__(self, os.path.basename(path),
                                  [], os.path.getsize(path))

    def get_separator(self):
        """Return the string used to separate nodes in the string
        representation of a path from the tree root to a leaf.

        @type self: FileSystemTree
        @rtype: str

        >>> fst = FileSystemTree('my-data')
        >>> fst.leaf_at((0, 0), (0, 0, 1024, 768)).get_separator()
        'my-data\\\\2\\\\1\\\\1\\\\1.txt'
        """
        if self._parent_tree is None:
            result = self._root
        else:
            result = os.path.join(self._parent_tree.get_separator(), self._root)
        return result
