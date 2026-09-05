import subprocess
import tempfile
import unittest
from pathlib import Path

from extractor import build_command_args


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FFMPEG_FILE = PROJECT_ROOT / 'ffmpeg' / 'bin' / 'ffmpeg.exe'
FFPROBE_FILE = PROJECT_ROOT / 'ffmpeg' / 'bin' / 'ffprobe.exe'


@unittest.skipUnless(
    FFMPEG_FILE.is_file() and FFPROBE_FILE.is_file(),
    'Repository FFmpeg tools are not available',
)
class ExtractorIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tempDirectory = tempfile.TemporaryDirectory()
        self.tempPath = Path(self.tempDirectory.name)
        self.inputFile = self.tempPath / 'input.mp4'

        result = subprocess.run(
            [
                str(FFMPEG_FILE),
                '-y',
                '-f', 'lavfi',
                '-i', 'color=c=red:s=16x16:r=1:d=3',
                str(self.inputFile),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        result = subprocess.run(
            [
                str(FFPROBE_FILE),
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'frame=pts',
                '-of', 'csv=p=0',
                str(self.inputFile),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.ptsValues = [
            int(line.rstrip(',').strip())
            for line in result.stdout.splitlines()
            if line.strip()
        ]

    def tearDown(self):
        self.tempDirectory.cleanup()

    def runExtraction(self, method, frameInterval='', specificFrames=''):
        outputDirectory = self.tempPath / f'output-{method}'
        outputDirectory.mkdir()
        args = build_command_args(
            str(FFMPEG_FILE),
            str(self.inputFile),
            str(outputDirectory),
            '.jpg',
            2,
            75,
            False,
            method,
            frameInterval,
            specificFrames,
        )
        result = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return list(outputDirectory.glob('*.jpg'))

    def test_every_n_frames_extracts_expected_count(self):
        outputFiles = self.runExtraction(0, frameInterval='2')
        self.assertEqual(len(outputFiles), 2)

    def test_specific_frame_numbers_extract_expected_count(self):
        outputFiles = self.runExtraction(1, specificFrames='1,2')
        self.assertEqual(len(outputFiles), 2)

    def test_specific_pts_values_extract_expected_count(self):
        specificPts = f'{self.ptsValues[0]},{self.ptsValues[1]}'
        outputFiles = self.runExtraction(2, specificFrames=specificPts)
        self.assertEqual(len(outputFiles), 2)


if __name__ == '__main__':
    unittest.main()
