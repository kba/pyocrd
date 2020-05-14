from tests.base import TestCase, main, assets

from ocrd_models.ocrd_page_generateds import TextTypeSimpleType
from ocrd_models.ocrd_page import (
    AlternativeImageType,
    PcGtsType,
    PageType,
    TextRegionType,
    TextLineType,
    OrderedGroupIndexedType,
    RegionRefIndexedType,
    WordType,
    GlyphType,

    parseString,
    parse,
    to_xml
)

simple_page = """\
<PcGts xmlns="http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15 http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15/pagecontent.xsd">
    <Metadata>
        <Creator>OCR-D</Creator>
        <Created>2016-09-20T11:09:27.041+02:00</Created>
        <LastChange>2018-04-25T17:44:49.605+01:00</LastChange>
    </Metadata>
    <Page
        imageFilename="https://github.com/OCR-D/assets/raw/master/data/kant_aufklaerung_1784/data/OCR-D-IMG/INPUT_0017.tif"
        imageWidth="1457"
        imageHeight="2083"
        type="content">
        <TextRegion type="heading" id="r_1_1" custom="readingOrder {index:0;} structure {type:heading;}">
            <Coords points="113,365 919,365 919,439 113,439"/>
            <TextLine id="tl_1" primaryLanguage="German" custom="readingOrder {index:0;} textStyle {offset:0; length:26;fontFamily:Arial; fontSize:17.0; bold:true;}">
                <Coords points="114,366 918,366 918,438 114,438"/>
                <Baseline points="114,429 918,429"/>
                <Word id="w_w1aab1b1b2b1b1ab1" language="German" custom="readingOrder {index:0;} textStyle {offset:0; length:11;fontFamily:Arial; fontSize:17.0; bold:true;}">
                    <Coords points="114,368 442,368 442,437 114,437"/>
                    <TextEquiv conf="1">
                        <Unicode>Berliniſche</Unicode>
                    </TextEquiv>
                </Word>
            </TextLine>
        </TextRegion>
    </Page>
</PcGts>
"""

# pylint: disable=protected-access

class TestOcrdPage(TestCase):

    def setUp(self):
        self.maxDiff = 5000
        with open(assets.path_to('glyph-consistency/data/OCR-D-GT-PAGE/FAULTY_GLYPHS.xml'), 'rb') as f:
            self.xml_as_str = f.read()
            self.pcgts = parseString(self.xml_as_str, silence=True)

    def test_to_xml(self):
        # with open('/tmp/test.xml', 'w') as f:
        #     f.write(to_xml(self.pcgts))
        as_xml = to_xml(self.pcgts)
        self.assertIn(' xmlns:pc="http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15"', as_xml[:1000])
        self.assertIn(' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15 http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15/pagecontent.xsd"', as_xml[:1000])
        self.assertIn('<pc:PcGts', as_xml[0:100])
        self.assertIn('<pc:TextRegion', as_xml[1000:3000])

    # https://github.com/OCR-D/core/pull/474#issuecomment-621477590 for context
    def test_to_xml_unicode_nsprefix(self):
        with open(assets.path_to('kant_aufklaerung_1784-binarized/data/OCR-D-GT-WORD/INPUT_0020.xml'), 'rb') as f:
            from_xml = f.read()
            self.assertIn('<Unicode>', from_xml.decode('utf-8'), 'without NS prefix')
            self.assertIn('<Created', from_xml.decode('utf-8'), 'without NS prefix')
            pcgts = parseString(from_xml, silence=True)
            as_xml = to_xml(pcgts)
            self.assertIn('<pc:Unicode>', as_xml, 'with NS prefix')
            self.assertIn('<pc:Created>', as_xml, 'with NS prefix')

    def test_issue_269(self):
        """
        @conf is parsed as str but should be float
        https://github.com/OCR-D/core/issues/269
        """
        # GIGO
        self.pcgts.get_Page().get_TextRegion()[0].get_TextEquiv()[0].set_conf(1.0)
        self.assertEqual(type(self.pcgts.get_Page().get_TextRegion()[0].get_TextEquiv()[0].get_conf()), float)
        self.pcgts.get_Page().get_TextRegion()[0].get_TextEquiv()[0].set_conf('1.0')
        self.assertEqual(type(self.pcgts.get_Page().get_TextRegion()[0].get_TextEquiv()[0].get_conf()), str)
        # test with parseString that @conf in TextEquiv won't throw an error
        parseString(simple_page, silence=True)
        #  self.assertTrue(True)

    def test_pcGtsId(self):
        self.assertEqual(self.pcgts.pcGtsId, 'glyph-test')

    def test_delete_region(self):
        pcgts = parseString(simple_page, silence=True)
        self.assertEqual(len(pcgts.get_Page().get_TextRegion()), 1)
        del pcgts.get_Page().get_TextRegion()[0]
        self.assertEqual(len(pcgts.get_Page().get_TextRegion()), 0)

    def test_imageFileName(self):
        #  print(self.pcgts.export(sys.stdout, 0))
        self.assertEqual(self.pcgts.get_Page().imageFilename, '00000259.sw.tif')
        self.pcgts.get_Page().imageFilename = 'foo'
        self.assertEqual(self.pcgts.get_Page().imageFilename, 'foo')

    def test_alternativeImage(self):
        pcgts = PcGtsType(pcGtsId="foo")
        self.assertEqual(pcgts.pcGtsId, 'foo')
        # Page/AlternativeImage
        page = PageType()
        pcgts.set_Page(page)
        page.add_AlternativeImage(AlternativeImageType())
        # TextRegion/AlternativeImage
        region = TextRegionType()
        page.add_TextRegion(region)
        region.add_AlternativeImage(AlternativeImageType())
        # TextLine/AlternativeImage
        line = TextLineType()
        region.add_TextLine(line)
        line.add_AlternativeImage(AlternativeImageType())
        # Word/AlternativeImage
        word = WordType()
        line.add_Word(word)
        word.add_AlternativeImage(AlternativeImageType())
        # Glyph/AlternativeImage
        glyph = GlyphType()
        word.add_Glyph(glyph)
        glyph.add_AlternativeImage(AlternativeImageType())

    def test_simple_types(self):
        regions = self.pcgts.get_Page().get_TextRegion()
        reg = regions[0]
        # print([l.get_type() for l in regions])
        self.assertTrue(isinstance(reg.get_type(), str))
        self.assertEqual(reg.get_type(), TextTypeSimpleType.CREDIT)
        self.assertTrue(isinstance(TextTypeSimpleType.CREDIT, str))
        self.assertEqual(reg.get_type(), 'credit')
        self.assertTrue(isinstance(TextTypeSimpleType.CREDIT, str))
        reg.set_type(TextTypeSimpleType.PAGENUMBER)
        self.assertEqual(reg.get_type(), 'page-number')
        self.assertTrue(isinstance(reg.get_type(), str))

    def test_orderedgroup_export_order(self):
        """
        See https://github.com/OCR-D/core/issues/475
        """
        with open('tests/model/TEMP1_Gutachten2-2.xml', 'r') as f:
            pcgts = parseString(f.read().encode('utf8'), silence=True)
            og = pcgts.get_Page().get_ReadingOrder().get_OrderedGroup()
            xml_before = to_xml(og)
            children = og.get_AllIndexed()
            self.assertEqual(len(children), 20)
            self.assertEqual([c.index for c in children], list(range(0, 20)))
            # mix up the indexes
            children[0].index = 11
            children[11].index = 3
            children[3].index = 0
            self.assertEqual([c.index for c in children], [11, 1, 2, 0, 4, 5, 6, 7, 8, 9, 10, 3, 12, 13, 14, 15, 16, 17, 18, 19])
            self.assertEqual([c.index for c in og.get_AllIndexed()], list(range(0, 20)))
            self.assertEqual(og.get_AllIndexed()[1].__class__, OrderedGroupIndexedType)
            # serialize and make sure the correct order was serialized
            new_pcgts = parseString(to_xml(pcgts).encode('utf8'), silence=True)
            new_og = new_pcgts.get_Page().get_ReadingOrder().get_OrderedGroup()
            self.assertEqual([c.index for c in new_og.get_AllIndexed()], list(range(0, 20)))
            # xml_after = to_xml(new_og)
            # self.assertEqual(xml_after, xml_before)

    def test_empty_groups_to_regionrefindexed(self):
        """
        Corrolary See https://github.com/OCR-D/core/issues/475
        """
        with open('tests/model/TEMP1_Gutachten2-2.xml', 'r') as f:
            pcgts = parseString(f.read().encode('utf8'), silence=True)
            og = pcgts.get_Page().get_ReadingOrder().get_OrderedGroup()
            children = og.get_AllIndexed()
            self.assertTrue(isinstance(children[1], OrderedGroupIndexedType))
            # empty all the elements in the first orederdGroupIndexed
            children[1].set_RegionRefIndexed([])
            # serialize apnd parse to see empty group converted
            pcgts = parseString(to_xml(pcgts).encode('utf8'), silence=True)
            og = pcgts.get_Page().get_ReadingOrder().get_OrderedGroup()
            children = og.get_AllIndexed()
            self.assertTrue(isinstance(children[1], RegionRefIndexedType))

    def test_all_regions_without_reading_order(self):
        """
        https://github.com/OCR-D/core/pull/479
        https://github.com/OCR-D/core/issues/240#issuecomment-493135797
        """
        with open('tests/model/TEMP1_Gutachten2-2.xml', 'r') as f:
            pcgts = parseString(f.read().encode('utf8'), silence=True)
            pg = pcgts.get_Page()
            self.assertEqual(len(pg.get_AllRegions()), 45)
            self.assertEqual(len(pg.get_AllRegions(['Separator'])), 25)
            self.assertEqual(len(pg.get_AllRegions(['Table'])), 3)
            self.assertEqual(len(pg.get_AllRegions(['Text'])), 17)

if __name__ == '__main__':
    main()
