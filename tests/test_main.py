import unittest
from unittest.mock import MagicMock, Mock, patch

from main import App


class ExtractCancellationTests(unittest.TestCase):
    def makeApp(self):
        app = App.__new__(App)
        app.root = MagicMock()
        app.isShuttingDown = False
        app.isCancelRequested = False
        app.extractProcess = None
        return app

    def test_cancel_during_duration_lookup_does_not_start_ffmpeg(self):
        app = self.makeApp()

        def cancelDuringDurationLookup(_):
            app.isCancelRequested = True
            return 10

        app.getInputDuration = Mock(side_effect=cancelDuringDurationLookup)

        with patch('main.subprocess.Popen') as popen:
            app.runExtract(['ffmpeg', '-i', 'input.mp4'])

        popen.assert_not_called()
        app.root.after.assert_called_once_with(
            0,
            app.finishExtract,
            -1,
            '',
        )

    def test_cancel_after_process_creation_terminates_ffmpeg(self):
        app = self.makeApp()
        app.getInputDuration = Mock(return_value=10)

        process = MagicMock()
        process.stdout = []
        process.returncode = 0

        def cancelAfterProcessCreation(*args, **kwargs):
            app.isCancelRequested = True
            return process

        with patch(
            'main.subprocess.Popen',
            side_effect=cancelAfterProcessCreation,
        ) as popen:
            app.runExtract(['ffmpeg', '-i', 'input.mp4'])

        popen.assert_called_once()
        process.terminate.assert_called_once()
        app.root.after.assert_called_once_with(
            0,
            app.finishExtract,
            0,
            '',
        )


if __name__ == '__main__':
    unittest.main()
