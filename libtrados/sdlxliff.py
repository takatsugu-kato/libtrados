"""
This modules is to handle sdlxliff file
"""

import re
from lxml import etree

class Sdlxliff():
    """
    Object handling sdlxliff file

    Args:
        path (str): path of the sdlxliff file
    """

    def __init__(self, path):
        self.source_language = ""
        self.target_language = ""
        self.trans_unit_count = 0
        self.path = path
        self.tree = etree.parse(path)
        etree.register_namespace('xliff', 'urn:oasis:names:tc:xliff:document:1.2')
        etree.register_namespace('sdl', 'http://sdl.com/FileTypes/SdlXliff/1.0')
        self.root = self.tree.getroot()
        self.namespace = {
            'xliff': 'urn:oasis:names:tc:xliff:document:1.2',
            'sdl': 'http://sdl.com/FileTypes/SdlXliff/1.0'
        }
        self.files = self.__get_segment()
        self.__set_language()

    def __set_language(self):
        """
        Set language code from sdlxliff file to this class const
        """

        files = self.root.findall('xliff:file', self.namespace)
        self.source_language = files[0].get('source-language')
        self.target_language = files[0].get('target-language')

    def __get_segment(self):
        """
        Create File obcject from sdlxliff file

        Returns:
            File: File objects
        """
        trans_unit_count = 0
        files = []
        for file in self.root.findall('xliff:file', self.namespace):
            file_obj = File(file.get('original'))
            for trans_unit_element in file.findall('xliff:body/xliff:group/xliff:trans-unit', self.namespace):
                trans_unit_obj = TransUnit(trans_unit_element.get('id'))
                trans_unit_obj.source = self.__create_seg_obj(trans_unit_element, "source")
                trans_unit_obj.set_only_tag_flag()

                if not trans_unit_obj.only_tag:
                    trans_unit_obj.seg_source = self.__create_seg_mrk(trans_unit_element.find('xliff:seg-source', self.namespace))
                    trans_unit_obj.target = self.__create_seg_mrk(trans_unit_element.find('xliff:target', self.namespace))

                # セグメントがMT由来かどうかはここで取得する<sdl:seg-defs><sdl:seg id="3" conf="Draft" origin="mt" origin-system="Google Cloud Translation API"/>
                trans_unit_count = trans_unit_count + 1
                file_obj.trans_units.append(trans_unit_obj)
            files.append(file_obj)
        self.trans_unit_count = trans_unit_count
        return files

    def __create_seg_obj(self, trans_unit_element, tag):
        """
        Creale Segment object from etree.Element

        Args:
            trans_unit_element (etree.Element): Element object of etree
            tag (str): tag name (source, seg-source, target)

        Returns:
            Segment: Segment object in this class
        """

        element = trans_unit_element.find('xliff:'+tag, self.namespace)

        seg_obj = Segment()
        seg_obj.string = self.__convert_element_to_string(element)
        return seg_obj


    def __create_seg_mrk(self, seg_element):
        mrk_elements = seg_element.findall('.//xliff:mrk', self.namespace)
        mrks = []
        for mrk_element in mrk_elements:
            mrk_obj = Mrk(mrk_element.get('mid'), etree.tostring(mrk_element), mrk_element.tail)
            mrk_obj.string = self.__delete_element_tag(etree.tostring(mrk_element))
            mrks.append(mrk_obj)

        return mrks

    def __convert_element_to_string(self, element):
        """
        Convert Element object to string

        Args:
            element (etree.Element): Element object of etree

        Returns:
            str: plain text of Element
        """

        string = etree.tostring(element, encoding='unicode')
        return self.__clean_element_string(string)

    def back_to_xlf(self, out_path=None):
        """Generate to xlf file from File object

        Args:
            out_path (str, optional): Out put file path. Defaults to ovierwrite original file.
        """

        if out_path is None:
            out_path = self.path

        for file in self.files:
            for trans_unit in file.trans_units:

                for target in trans_unit.target:
                    new_mrk_element = self.__create_xml_string_for_mrk_element(target)
                    condition = (
                        'xliff:file[@original="{0}"]/xliff:body/xliff:group/xliff:trans-unit[@id="{1}"]/xliff:target//xliff:mrk[@mid="{2}"]'
                        .format(file.original, trans_unit.trans_unit_id, target.mid))
                    mrk_element = self.root.find(condition, self.namespace)
                    parent = mrk_element.getparent()
                    parent.replace(mrk_element, new_mrk_element)
        self.tree.write(out_path, encoding="utf-8", xml_declaration=True)

    @staticmethod
    def __delete_element_tag(string):
        string = string.decode()
        string = re.sub('<mrk.*?>(.*?)</mrk>.*', r"\1", string, flags=re.DOTALL)
        return string

    @staticmethod
    def __clean_element_string(string):
        """
        Clean the string of Element

        Args:
            string (str): plain text of Element

        Returns:
            str: string of deleted xml tag
        """
        string = string.strip()
        string = re.sub('<.*?>', "", string, flags=re.DOTALL)
        return string

    @staticmethod
    def __create_xml_string_for_mrk_element(mrk_obj):
        """
        Create xml string for Mrk element

        Args:
            mrk_obj (Mrk): Mrk object in this class

        Returns:
            str: xml string
        """
        xml_string = '<mrk mtype="seg" mid="{0}">{1}</mrk>'.format(mrk_obj.mid, mrk_obj.string)
        tree = etree.fromstring(xml_string)
        tree.tail = mrk_obj.tail
        return tree

class File():
    """
    Object of <file> tag in sdlxliff
    """

    def __init__(self, original):
        self.original = original
        self.trans_units = []


class TransUnit():
    """
    Object of <trans-unit> tag in sdlxliff
    """

    def __init__(self, trans_unit_id):
        self.trans_unit_id = trans_unit_id
        self.source = ""
        self.seg_source = []
        self.target = []
        self.mt_processed = False
        self.only_tag = False
        self.metadata = dict()

    def set_only_tag_flag(self):
        """
        Set only_tag flag using source string
        """
        if self.source.string == "":
            self.only_tag = True


class Segment():
    """
    Object of <source> and <target> tag in sdlxliff
    """

    def __init__(self):
        self.string = ""

class Mrk():
    """
    Object of <mrk>
    """
    def __init__(self, mid, string, tail):
        self.mid = mid
        self.string = string
        self.tail = tail
