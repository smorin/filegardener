#!/usr/bin/env python
#unittests for liten
import unittest
import doctest
from doctest import DocTestSuite

from liten import Liten, LitenController

class TestLitenBaseClass(unittest.TestCase):
    """Tests for LitenBaseClass Class."""

    def setUp(self):
        self.fakePath = 'testData/testDocOne.txt'
        self.dupeFileOne = 'testData/testDocOne.txt'
        self.dupeFileTwo = 'testData/testDocTwo.txt'
        self.nonDupeFile = 'testData/testDocThree_wrong_match.txt'

        #Tests byte size calculations and conversions
        self.byteFileSize = '1bytes' #1 bytes
        self.KBFileSize = '1KB' #1024 bytes
        self.MBFileSize = '1MB' #1048576 bytes
        self.GBFileSize = '1GB' #1073741824 bytes
        self.TBFileSize = '1TB' #1099511627776 bytes
        self.NoQualifier = '1' #No Qualifier defaults to MB/ 1048576 bytes
        self.Bogus = '9foo' #Bogus data


    def testModDate(self):
        """Test modDate method."""
        liten = Liten(spath='testData')
        modDate = liten.makeModDate(self.fakePath)

    def testCreateDate(self):
        """Test createDate method."""
        liten = Liten(spath='testData')
        createDate = liten.makeCreateDate(self.fakePath)

    def badChecksumDetection(self):
        """Bad Checksum Detection Should Raise Exception."""
        liten = Liten(spath='testData')
        badChecksumAttempt = liten.createChecksum('fileNotFound.txt')


    def testDupeFileDetection(self):
        """Test checksum of duplicate files"""
        liten = Liten(spath='testData')
        checksumOne = liten.createChecksum(self.dupeFileOne)
        checksumTwo = liten.createChecksum(self.dupeFileTwo)
        self.assertEqual(checksumOne, checksumTwo)

    def testDupeFileDetectionError(self):
        """Test checksum of Non-duplicate files"""
        liten = Liten(spath='testData')
        checksumOne = liten.createChecksum(self.dupeFileOne)
        checksumThree= liten.createChecksum(self.nonDupeFile)
        self.assertNotEqual(checksumOne, checksumThree)

    def testCreateExt(self):
        """Test Create Extension Method."""
        liten = Liten(spath='testData')
        createExt = liten.createExt(self.dupeFileOne)
        self.assertEqual(createExt, ".txt")

    def testByteSizeType(self):
        """Tests ByteSize Calculations based on Input."""
        liten = Liten(spath='testData', fileSize=self.byteFileSize)
        byteSizeType = liten.sizeType()
        self.assertEqual(byteSizeType, 1)

    def testKByteSizeType(self):
        """Tests KBSize Calculations based on Input."""
        liten = Liten(spath='testData', fileSize=self.KBFileSize)
        KBSizeType = liten.sizeType()
        self.assertEqual(KBSizeType, 1024)

    def testMBByteSizeType(self):
        """Tests MBSize Calculations based on Input."""
        liten = Liten(spath='testData', fileSize=self.MBFileSize)
        MBSizeType = liten.sizeType()
        self.assertEqual(MBSizeType, 1048576)

    def testGBSizeType(self):
        """Tests GBSize Calculations based on Input."""
        liten = Liten(spath='testData', fileSize=self.GBFileSize)
        GBSizeType = liten.sizeType()
        self.assertEqual(GBSizeType, 1073741824)

    def testTBSizeType(self):
        """Tests TBSize Calculations based on Input."""
        liten = Liten(spath='testData', fileSize=self.TBFileSize)
        TBSizeType = liten.sizeType()
        self.assertEqual(TBSizeType, 1099511627776)

    def testNoQualifier(self):
        """Tests NoSize Calculations based on Input.

        Should convert No Qualifiers to MB
        """
        liten = Liten(spath='testData', fileSize=self.NoQualifier)
        NoSizeType = liten.sizeType()

    def testBogus(self):
        """Tests Bogus Size Input.

        Should raise exception UnboundLocalError or fail
        """
        try:
            liten = Liten(spath='testData', fileSize=self.Bogus)
            BogusType = liten.sizeType()
        except UnboundLocalError:
            pass


if __name__ == '__main__':
    unittest.main()

