import unittest
import sys
import os
import py_compile
from vcf_annotation_tools import vcf_readcount_annotator
import tempfile
from filecmp import cmp

class VcfExpressionEncoderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_dir          = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
        cls.executable    = os.path.join(base_dir, 'vcf_annotation_tools', 'vcf_readcount_annotator.py')
        cls.test_data_dir = os.path.join(base_dir, 'tests', 'test_data')

    def test_source_compiles(self):
        self.assertTrue(py_compile.compile(self.executable))

    def test_error_more_than_one_sample_without_sample_name(self):
        with self.assertRaises(Exception) as context:
            command = [
                os.path.join(self.test_data_dir, 'multiple_samples.vcf'),
                os.path.join(self.test_data_dir, 'snvs.bam_readcount'),
                'DNA',
            ]
            vcf_readcount_annotator.main(command)
        self.assertTrue('contains more than one sample. Please use the -s option to specify which sample to annotate.' in str(context.exception))

    def test_error_more_than_one_sample_with_wrong_sample_name(self):
        with self.assertRaises(Exception) as context:
            command = [
                os.path.join(self.test_data_dir, 'multiple_samples.vcf'),
                os.path.join(self.test_data_dir, 'snvs.bam_readcount'),
                'DNA',
                '-s', 'nonexistent_sample',
            ]
            vcf_readcount_annotator.main(command)
        self.assertTrue('does not contain a sample column for sample nonexistent_sample.' in str(context.exception))

    def test_single_sample_vcf_without_readcounts_annotations_dna_mode(self):
        temp_path = tempfile.TemporaryDirectory()
        os.symlink(os.path.join(self.test_data_dir, 'input.vcf'), os.path.join(temp_path.name, 'input.vcf'))
        command = [
            os.path.join(temp_path.name, 'input.vcf'),
            os.path.join(self.test_data_dir, 'snvs.bam_readcount'),
            'DNA',
        ]
        vcf_readcount_annotator.main(command)
        self.assertTrue(cmp(os.path.join(self.test_data_dir, 'single_sample.dna.readcount.vcf'), os.path.join(temp_path.name, 'input.readcount.vcf')))
        temp_path.cleanup()

    def test_single_sample_vcf_without_readcounts_annotations_rna_mode(self):
        temp_path = tempfile.TemporaryDirectory()
        os.symlink(os.path.join(self.test_data_dir, 'input.vcf'), os.path.join(temp_path.name, 'input.vcf'))
        command = [
            os.path.join(temp_path.name, 'input.vcf'),
            os.path.join(self.test_data_dir, 'snvs.bam_readcount'),
            'RNA',
        ]
        vcf_readcount_annotator.main(command)
        self.assertTrue(cmp(os.path.join(self.test_data_dir, 'single_sample.rna.readcount.vcf'), os.path.join(temp_path.name, 'input.readcount.vcf')))
        temp_path.cleanup()

    def test_single_sample_vcf_with_existing_readcount_annotations(self):
        temp_path = tempfile.TemporaryDirectory()
        os.symlink(os.path.join(self.test_data_dir, 'input.readcount.vcf'), os.path.join(temp_path.name, 'input.vcf'))
        command = [
            os.path.join(temp_path.name, 'input.vcf'),
            os.path.join(self.test_data_dir, 'snvs.bam_readcount'),
            'DNA',
        ]
        vcf_readcount_annotator.main(command)
        self.assertTrue(cmp(os.path.join(self.test_data_dir, 'single_sample_with_existing_readcount_annotations.readcount.vcf'), os.path.join(temp_path.name, 'input.readcount.vcf')))
        temp_path.cleanup()

    def test_mutation_without_matching_readcount_value(self):
        temp_path = tempfile.TemporaryDirectory()
        os.symlink(os.path.join(self.test_data_dir, 'no_matching_readcount.vcf'), os.path.join(temp_path.name, 'input.vcf'))
        command = [
            os.path.join(temp_path.name, 'input.vcf'),
            os.path.join(self.test_data_dir, 'snvs.bam_readcount'),
            'DNA',
        ]
        vcf_readcount_annotator.main(command)
        self.assertTrue(cmp(os.path.join(self.test_data_dir, 'no_matching_readcount.readcount.vcf'), os.path.join(temp_path.name, 'input.readcount.vcf')))
        temp_path.cleanup()

    def test_multi_sample_vcf(self):
        temp_path = tempfile.TemporaryDirectory()
        os.symlink(os.path.join(self.test_data_dir, 'multiple_samples.vcf'), os.path.join(temp_path.name, 'input.vcf'))
        command = [
            os.path.join(temp_path.name, 'input.vcf'),
            os.path.join(self.test_data_dir, 'snvs.bam_readcount'),
            'DNA',
            '-s', 'H_NJ-HCC1395-HCC1395',
        ]
        vcf_readcount_annotator.main(command)
        self.assertTrue(cmp(os.path.join(self.test_data_dir, 'multiple_samples.readcount.vcf'), os.path.join(temp_path.name, 'input.readcount.vcf')))
        temp_path.cleanup()

    def test_multiple_alts(self):
        temp_path = tempfile.TemporaryDirectory()
        os.symlink(os.path.join(self.test_data_dir, 'multiple_samples.readcount.vcf'), os.path.join(temp_path.name, 'input.vcf'))
        command = [
            os.path.join(temp_path.name, 'input.vcf'),
            os.path.join(self.test_data_dir, 'snvs.bam_readcount'),
            'DNA',
            '-s', 'H_NJ-HCC1395-HCC1396',
        ]
        vcf_readcount_annotator.main(command)
        self.assertTrue(cmp(os.path.join(self.test_data_dir, 'multiple_samples_second_alt.readcount.vcf'), os.path.join(temp_path.name, 'input.readcount.vcf')))
        temp_path.cleanup()
