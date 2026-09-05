import tempfile
import unittest
from pathlib import Path

from extractor import (
    build_command_args,
    build_select_filter,
    parse_specific_frames,
    validate_inputs,
)


class ExtractorTests(unittest.TestCase):
    def test_parse_specific_frames_accepts_spaces_and_commas(self):
        self.assertEqual(parse_specific_frames('1 4, 7'), ['1', '4', '7'])

    def test_parse_specific_frames_rejects_empty_value(self):
        with self.assertRaisesRegex(ValueError, 'required'):
            parse_specific_frames('')

    def test_parse_specific_frames_rejects_non_integer(self):
        with self.assertRaisesRegex(ValueError, 'non-negative integers'):
            parse_specific_frames('1,abc')

    def test_build_select_filter_for_every_n_frames(self):
        self.assertEqual(
            build_select_filter(0, '3', ''),
            r'select=not(mod(n\,3))',
        )

    def test_build_select_filter_rejects_empty_every_n_frames(self):
        with self.assertRaisesRegex(ValueError, 'positive integer'):
            build_select_filter(0, '', '')

    def test_build_select_filter_for_specific_n_frames(self):
        self.assertEqual(
            build_select_filter(1, '', '1, 4'),
            'select=eq(n,1)+eq(n,4)',
        )

    def test_build_select_filter_for_specific_pts_frames(self):
        self.assertEqual(
            build_select_filter(2, '', '0 3072'),
            'select=eq(pts,0)+eq(pts,3072)',
        )

    def test_build_command_args_keeps_paths_as_separate_arguments(self):
        args = build_command_args(
            r'C:\Tools\ffmpeg.exe',
            r'C:\Videos\input file.mp4',
            r'C:\Videos\output folder',
            '.jpg',
            2,
            75,
            False,
            0,
            '3',
            '',
        )
        self.assertEqual(args[2], r'C:\Videos\input file.mp4')
        self.assertEqual(args[-1], r'C:\Videos\output folder/%d.jpg')
        self.assertIn('-qscale:v', args)

    def test_build_command_args_adds_webp_options(self):
        args = build_command_args(
            'ffmpeg', 'input.mp4', 'output', '.webp', 2, 80, True,
            1, '', '0,2',
        )
        self.assertIn('-c:v', args)
        self.assertIn('libwebp', args)
        self.assertIn('-lossless', args)
        self.assertIn('1', args)
        self.assertIn('80', args)

    def test_validate_inputs_accepts_existing_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            input_file = Path(directory) / 'input.mp4'
            input_file.touch()
            self.assertEqual(
                validate_inputs(
                    str(input_file), directory, 0, '3', '', 'ffmpeg'
                ),
                [],
            )

    def test_validate_inputs_rejects_invalid_values(self):
        errors = validate_inputs('', '', 0, '0', '', None)
        self.assertIn('Input file is required.', errors)
        self.assertIn('Output directory is required.', errors)
        self.assertIn('The frame interval must be a positive integer.', errors)
        self.assertIn('Unable to find FFmpeg.', errors)


if __name__ == '__main__':
    unittest.main()
