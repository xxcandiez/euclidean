import copy
import lxml.etree as ET
import os
import subprocess as sp
import sys
from hashlib import sha256

from . import tatr
from animation.Frameable import Frameable
from .constants import DEFAULT_FILL
from .constants import TEMPLATE_FILE
from .constants import TEX_AUXILIARY
from .constants import STD_TEX_NS
from .constants import TEX_OUTPUT
from .constants import TEX_SVG_OUTPUT
from .styles import DEFAULT_TEX_STYLE
from .TexWriter import TexWriter

class Tex(Frameable):
    """
    parent class for handling all objects that need to be typeset in TeX
    """

    def __init__(self, config):
        """
        does not mutate config

        dict -> None

        :param config: dictionary that represents the configuration of the
        object

        :config [cache]: whether you want to use the cached svg file for this
        object if one is available, if you choose not to use the cached one it
        will be overwritten during the creation of this object anyways
        :config [content]: a string that represents a the content you want to
        typeset, 'content' must be a valid string in the document environment
        of a TeX document
        :config [fill]:
        :config [opacity]:
        :config [position]:
        :config [size]: the size in px of the svg in form '(width, height)'
        """
        self.config = Tex.makeConfig(config)
        node = Tex.makeNode(self.config)
        Frameable.__init__(self, node)

    @staticmethod
    def applyFill(node, config):
        group = Tex.getGroup(node)
        fill = config[tatr.fill]
        group.set('fill', fill)

    @staticmethod
    def applyOpacity(node, config):
        opacity = str(config[tatr.opacity])
        node.set('opacity', opacity)

    @staticmethod
    def applyPosition(node, config):
        group = Tex.getGroup(node)
        x, y = config[tatr.position]

        # this block accomodates for the viewbox in the svg that dvisvgm outputs
        old_x, old_y = node.get('viewBox').split(' ')[-2:]
        old_x, old_y = float(old_x), float(old_y)
        ratio = Tex.getScaleOfFrameToViewBox(node, config)
        x, y = (1 / ratio) * x, (1 / ratio) * y
        transform = group.get('transform')
        if transform == None:
            transform = ''
        transform = f'{transform} translate({x} {y})'
        group.set('transform', transform)

    @staticmethod
    def applySize(node, config):
        new_size = Tex.applySizeResults(node, config)
        new_size = [str(x) for x in new_size]
        node.set('width', new_size[0])
        node.set('height', new_size[1])

    @staticmethod
    def applySizeResults(node, config):
        size = config[tatr.size]
        old_size = [node.get('width'), node.get('height')]

        for i, dim in enumerate(old_size):
            temp = dim[:-2]
            temp = float(temp)
            old_size[i] = temp

        scale = Tex.getScaleOfFrameToViewBox(node, config)

        new_size = [x * scale for x in old_size]

        return new_size

    @staticmethod
    def getGroup(node):
        return node.find('./svg:g', namespaces=STD_TEX_NS)

    @staticmethod
    def getGroups(node):
        return node.findall('./svg:g', namespaces=STD_TEX_NS)

    @staticmethod
    def getScaleOfFrameToViewBox(node, config):

        old_size = [node.get('width'), node.get('height')]

        for i, dim in enumerate(old_size):
            temp = dim[:-2]
            temp = float(temp)
            old_size[i] = temp

        old_aspect_ratio = old_size[0]/old_size[1]

        new_size = config[tatr.size]
        new_aspect_ratio = new_size[0]/new_size[1]
        if new_aspect_ratio > old_aspect_ratio:
            scale = new_size[1]/old_size[1]
        else:
            scale = new_size[0]/old_size[0]

        return scale

    @staticmethod
    def getUse(node):
        return node.find('./svg:g/svg:use', namespaces=STD_TEX_NS)

    @staticmethod
    def getUses(node):
        return node.findall('./svg:g/svg:use', namespaces=STD_TEX_NS)

    @staticmethod
    def makeConfig(config):
        DEF_CACHE = True
        DEF_CONTENT = 'no content'
        DEF_SIZE = (sys.maxsize, 1080/4)
        DEF_FILL = '#ffffff'
        DEF_POSITION = (0, 0)

        res = copy.deepcopy(config)

        if not tatr.cache in res:
            res[tatr.cache] = DEF_CACHE

        if not tatr.content in res:
            res[tatr.content] = DEF_CONTENT
        res[tatr.content] = Tex.makeContent(res)

        if not tatr.fill in res:
            res[tatr.fill] = DEF_FILL

        if not tatr.opacity in res:
            res[tatr.opacity] = 1

        if not tatr.position in res:
            res[tatr.position] = DEF_POSITION

        if not tatr.size in res:
            res[tatr.size] = DEF_SIZE

        return res

    @staticmethod
    def makeContent(config):
        res = config[tatr.content]
        res = r'\pagenumbering{gobble}' + '\n' + res
        return res

    @staticmethod
    def makeName(config):
        content = config[tatr.content]
        hashObj = sha256()
        hashObj.update(content.encode('utf-8'))
        res = hashObj.hexdigest()
        return res

    @staticmethod
    def makeNode(config):
        """
        None -> ET.Element
        this only works if you wrote the file already
        """
        res = Tex.makeNodeGet(config)

        Tex.applyFill(res, config)
        Tex.applyOpacity(res, config)
        Tex.applyPosition(res, config)
        Tex.applySize(res, config)

        return res

    @staticmethod
    def makeNodeGet(config):
        """
        dict -> ET.Element
        :helper:

        makes the node if it doesnt exist, gets it afterwards
        """
        name = Tex.makeName(config)
        path = Tex.makePath(config)

        if not os.path.isfile(path) or not config[tatr.cache]:
            writer = TexWriter(config[tatr.content])
            writer.write(clean=True)
        res = ET.parse(path).getroot()

        return res

    @staticmethod
    def makePath(config):
        name = Tex.makeName(config)
        return f'{TEX_SVG_OUTPUT}/{name}.svg'

    def __copy__(self):
        """
        this is pretty much a deep copy

        None -> Tex
        :returns: copied Tex object
        """
        config_copy = copy.deepcopy(self.config)
        return Tex(config_copy)

    def partialCopy(self, config):
        """
        allows you to copy the current tex object while making some
        modifications

        [str], [dict], [list] -> Tex
        """
        if config:
            config = {**self.config, **config}
        else:
            config = self.config
        return Tex(config)
