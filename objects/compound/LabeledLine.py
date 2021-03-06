import geometry.Line as Line
import lxml.etree as ET
import typesetting.Label as Label
from animation.Frameable import Frameable
import copy

class LabeledLine(Frameable):
    def __init__(self, line, label):
        lineNode = line.node
        labelNode = label.node
        node = LabeledLine.makeNode(lineNode, labelNode)
        Frameable.__init__(self, node)

    @staticmethod
    def makeNode(lineNode, labelNode):
        # TODO: HECK!
        lineNode = copy.deepcopy(lineNode)
        labelNode = copy.deepcopy(labelNode)
        res = ET.Element('g')
        res.append(lineNode)
        res.append(labelNode)
        return res
