import os
import sys
import shutil
import subprocess
import threading
import ctypes
import tkinter
from tkinter.constants import DISABLED, NORMAL
import tkinter.ttk
import tkinter.filedialog
import tkinter.messagebox
import re
from extractor import build_command_args, build_select_filter, validate_inputs

inputFileTypes = (
    ('Video files', '*.avi'),
    ('Video files', '*.flv'),
    ('Video files', '*.mov'),
    ('Video files', '*.mp4'),
    # ('Video files', '*.mkv'),
    ('Video files', '*.webm'),
    ('All files', '*.*')
)

def getAssetFile(filename):
    baseDirectory = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(baseDirectory, filename)

def getLocalFfmpegFile():
    if hasattr(sys, 'frozen'):
        baseDirectory = os.path.dirname(sys.executable)
    else:
        baseDirectory = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(baseDirectory, 'ffmpeg', 'bin', 'ffmpeg.exe')

def getFfmpegVersion(ffmpegFile):
    if not ffmpegFile or not os.path.isfile(ffmpegFile):
        return 'Not detected'

    try:
        result = subprocess.run(
            [ffmpegFile, '-version'],
            capture_output = True,
            text = True,
            timeout = 3,
            check = False,
            creationflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0),
        )
    except (OSError, subprocess.SubprocessError):
        return 'Not detected'

    firstLine = (result.stdout or result.stderr).splitlines()
    if not firstLine:
        return 'Not detected'

    versionMarker = ' version '
    if versionMarker not in firstLine[0]:
        return 'Not detected'
    version = firstLine[0].split(versionMarker, 1)[1].split()[0]
    versionParts = version.split('-')
    if re.fullmatch(r'\d{4}', versionParts[0]) and len(versionParts) >= 3:
        shortVersion = '-'.join(versionParts[:3])
    else:
        shortVersion = versionParts[0]
    return f'v{shortVersion}'

class App:
    def __init__(self, root):
        self.inputFile = tkinter.StringVar()
        self.outputDirectory = tkinter.StringVar()
        self.outputFileType = tkinter.StringVar()
        self.outputJpgQuality = tkinter.DoubleVar(value = 1)
        self.outputWebpQuality = tkinter.DoubleVar(value = 75)
        self.outputLossless = tkinter.BooleanVar()

        self.methodRadioVariety = tkinter.IntVar(value = 0)
        self.methodEveryNFramesN = tkinter.StringVar()
        self.methodSpecificFrames = tkinter.StringVar()
        self.ffmpegSource = tkinter.IntVar(value = 0)
        self.extractProcess = None
        self.isExtracting = False
        self.isCancelRequested = False
        self.isShuttingDown = False

        self.root = root

        self.root.iconbitmap(getAssetFile('assets/icon.ico'))

        self.fileSection = tkinter.LabelFrame(window, text = 'File')
        self.fileSection.grid(column = 0, row = 0, padx = 8, pady = 4, sticky = 'NSEW')
        self.fileSection.columnconfigure(1, weight = 1)

        self.inputFileLabel = tkinter.Label(self.fileSection, text = 'Input file')
        self.inputFileLabel.grid(column = 0, row = 0)

        self.inputFileEntry = tkinter.Entry(self.fileSection, textvariable = self.inputFile)
        self.inputFileEntry.grid(column = 1, row = 0, sticky = 'EW')

        self.inputFileSelectButton = tkinter.Button(self.fileSection, text = 'Select', command = self.selectInputFile)
        self.inputFileSelectButton.grid(column = 2, row = 0)

        self.outputDirectoryLabel = tkinter.Label(self.fileSection, text = 'Output directory')
        self.outputDirectoryLabel.grid(column = 0, row = 1)

        self.outputDirectoryEntry = tkinter.Entry(self.fileSection, textvariable = self.outputDirectory)
        self.outputDirectoryEntry.grid(column = 1, row = 1, sticky = 'EW')

        self.outputDirectorySelectButton = tkinter.Button(self.fileSection, text = 'Select', command = self.selectOutputDirectory)
        self.outputDirectorySelectButton.grid(column = 2, row = 1)

        self.outputFileTypeLabel = tkinter.Label(self.fileSection, text = 'Output file type')
        self.outputFileTypeLabel.grid(column = 0, row = 2)

        self.outputFileTypeCombobox = tkinter.ttk.Combobox(self.fileSection, state = 'readonly', values = ('.jpg', '.png', '.webp'), textvariable = self.outputFileType)
        self.outputFileTypeCombobox.grid(column = 1, row = 2, columnspan = 2, sticky = 'E')
        self.outputFileTypeCombobox.current(0)

        self.outputJpgQualityLabel = tkinter.Label(self.fileSection, text = 'JPG Quality\n(Lower is better)')
        self.outputJpgQualityLabel.grid(column = 0, row = 3)

        self.outputJpgQualityScale = tkinter.ttk.Scale(self.fileSection, variable = self.outputJpgQuality, orient = 'horizontal', from_ = 1, to_ = 31)
        self.outputJpgQualityScale.grid(column = 1, row = 3, sticky = 'EW')

        self.outputJpgQualityValueLabel = tkinter.Label(self.fileSection, text = '1')
        self.outputJpgQualityValueLabel.grid(column = 2, row = 3)

        self.outputWebpQualityLabel = tkinter.Label(self.fileSection, text = 'WebP Quality\n(Higher is better)')
        self.outputWebpQualityLabel.grid(column = 0, row = 4)

        self.outputWebpQualityScale = tkinter.ttk.Scale(self.fileSection, variable = self.outputWebpQuality, orient = 'horizontal', from_ = 0, to_ = 100)
        self.outputWebpQualityScale.grid(column = 1, row = 4, sticky = 'EW')
        self.outputWebpQualityScale.state(['disabled'])

        self.outputWebpQualityValueLabel = tkinter.Label(self.fileSection, text = '75')
        self.outputWebpQualityValueLabel.grid(column = 2, row = 4)

        self.outputLosslessCheckButton = tkinter.Checkbutton(self.fileSection, text = 'Lossless (WebP only)', variable = self.outputLossless, state = DISABLED)
        self.outputLosslessCheckButton.grid(column = 1, row = 5)

        self.methodSection = tkinter.LabelFrame(root, text = 'Method')
        self.methodSection.grid(column = 0, row = 1, padx = 8, pady = 4, sticky = 'NSEW')
        self.methodSection.grid_columnconfigure(0, weight = 1)

        self.methodEveryNFramesRadio = tkinter.Radiobutton(self.methodSection, text = 'Every # frames', value = 0, variable = self.methodRadioVariety)
        self.methodEveryNFramesRadio.grid(column = 0, row = 0, sticky = 'W')

        self.methodEveryNFramesParamsSection = tkinter.Frame(self.methodSection)
        self.methodEveryNFramesParamsSection.grid(column = 0, row = 1, sticky = 'EW')
        self.methodEveryNFramesParamsSection.grid_columnconfigure(1, weight = 1)

        self.methodEveryNFramesNLabel = tkinter.Label(self.methodEveryNFramesParamsSection, text = '# Frames')
        self.methodEveryNFramesNLabel.grid(column = 0, row = 0)

        self.methodEveryNFramesNEntry = tkinter.Entry(self.methodEveryNFramesParamsSection, textvariable = self.methodEveryNFramesN)
        self.methodEveryNFramesNEntry.grid(column = 1, row = 0, sticky = 'EW')

        self.methodSpecificFramesMethod1Radio = tkinter.Radiobutton(self.methodSection, text = 'Specific frames (Method 1)', value = 1, variable = self.methodRadioVariety)
        self.methodSpecificFramesMethod1Radio.grid(column = 0, row = 2, sticky = 'W')

        self.methodSpecificFramesMethod2Radio = tkinter.Radiobutton(self.methodSection, text = 'Specific frames (Method 2)', value = 2, variable = self.methodRadioVariety)
        self.methodSpecificFramesMethod2Radio.grid(column = 0, row = 3, sticky = 'W')

        self.methodSpecificFramesParamsSection = tkinter.Frame(self.methodSection)
        self.methodSpecificFramesParamsSection.grid(column = 0, row = 4, sticky = 'EW')
        self.methodSpecificFramesParamsSection.grid_columnconfigure(0, weight = 1)

        self.methodSpecificFramesLabel = tkinter.Label(self.methodSpecificFramesParamsSection, text = 'Frame numbers (split with spaces or commas)')
        self.methodSpecificFramesLabel.grid(column = 0, row = 0, sticky = 'W')

        self.methodSpecificFramesEntry = tkinter.Entry(self.methodSpecificFramesParamsSection, textvariable = self.methodSpecificFrames)
        self.methodSpecificFramesEntry.grid(column = 0, row = 1, sticky = 'EW')

        self.ffmpegSection = tkinter.LabelFrame(root, text = 'FFmpeg')
        self.ffmpegSection.grid(column = 0, row = 2, padx = 8, pady = 4, sticky = 'NSEW')
        self.ffmpegSection.grid_columnconfigure(0, weight = 1)

        self.localFfmpegRadio = tkinter.Radiobutton(
            self.ffmpegSection,
            text = 'Use FFmpeg next to the application',
            value = 0,
            variable = self.ffmpegSource,
        )
        self.localFfmpegRadio.grid(column = 0, row = 0, padx = 4, sticky = 'W')
        self.localFfmpegVersionLabel = tkinter.Label(self.ffmpegSection, text = '')
        self.localFfmpegVersionLabel.grid(column = 1, row = 0, padx = 4, sticky = 'W')

        self.systemFfmpegRadio = tkinter.Radiobutton(
            self.ffmpegSection,
            text = 'Use FFmpeg from system PATH',
            value = 1,
            variable = self.ffmpegSource,
        )
        self.systemFfmpegRadio.grid(column = 0, row = 1, padx = 4, sticky = 'W')
        self.systemFfmpegVersionLabel = tkinter.Label(self.ffmpegSection, text = '')
        self.systemFfmpegVersionLabel.grid(column = 1, row = 1, padx = 4, sticky = 'W')

        self.infoSection = tkinter.Frame(root)
        self.infoSection.grid(column = 0, row = 3, padx = 8, pady = 4, sticky = 'NSEW')
        self.infoSection.grid_columnconfigure(0, weight = 1)

        self.commandToRunLabel = tkinter.Label(self.infoSection, text = 'Command to run')
        self.commandToRunLabel.grid(column = 0, row = 0, sticky = 'W')

        self.commandToRunText = tkinter.Text(self.infoSection, width = 0, height = 4)
        self.commandToRunText.grid(column = 0, row = 1, sticky = 'EW')
        self.commandToRunText.config(state = tkinter.DISABLED)

        # Keep this area separate so the status label can later be replaced
        # with a determinate or indeterminate progress bar.
        self.progressSection = tkinter.LabelFrame(root, text = 'Progress')
        self.progressSection.grid(column = 0, row = 4, padx = 8, pady = 4, sticky = 'NSEW')
        self.progressSection.grid_columnconfigure(0, weight = 1)

        self.progressStatusLabel = tkinter.Label(self.progressSection, text = 'Ready')
        self.progressStatusLabel.grid(column = 0, row = 0, padx = 4, sticky = 'W')

        self.cancelButton = tkinter.Button(self.progressSection, text = 'Cancel', command = self.cancelExtract, state = DISABLED)
        self.cancelButton.grid(column = 1, row = 0, padx = 4)

        self.actionSection = tkinter.Frame(root)
        self.actionSection.grid(column = 0, row = 5, padx = 8, pady = 4, sticky = 'NSEW')
        self.actionSection.grid_columnconfigure(0, weight = 1)

        self.extractButton = tkinter.Button(self.actionSection, text = 'Extract', command = self.startExtract)
        self.extractButton.grid(column = 0, row = 0)

        self.inputFile.trace_add('write', lambda name, index, mode: self.updateCommand())
        self.outputDirectory.trace_add('write', lambda name, index, mode: self.updateCommand())
        self.outputFileType.trace_add('write', lambda name, index, mode: self.updateCommandAndQuality())
        self.outputJpgQuality.trace_add('write', lambda name, index, mode: self.updateCommandAndQuality())
        self.outputWebpQuality.trace_add('write', lambda name, index, mode: self.updateCommandAndQuality())
        self.outputLossless.trace_add('write', lambda name, index, mode: self.updateCommandAndQuality())
        self.methodRadioVariety.trace_add('write', lambda name, index, mode: self.updateCommand())
        self.methodEveryNFramesN.trace_add('write', lambda name, index, mode: self.updateCommand())
        self.methodSpecificFrames.trace_add('write', lambda name, index, mode: self.updateCommand())
        self.ffmpegSource.trace_add('write', lambda name, index, mode: self.updateCommand())

        self.localFfmpegVersionLabel.configure(text = 'Checking...')
        self.systemFfmpegVersionLabel.configure(text = 'Checking...')
        threading.Thread(target = self.checkFfmpegVersions, daemon = True).start()
        self.updateCommand()
        self.updateExtractButton()

    def checkFfmpegVersions(self):
        localVersion = getFfmpegVersion(getLocalFfmpegFile())
        systemVersion = getFfmpegVersion(shutil.which('ffmpeg'))
        self.root.after(0, lambda: self.updateFfmpegVersionLabels(localVersion, systemVersion))

    def updateFfmpegVersionLabels(self, localVersion, systemVersion):
        self.localFfmpegVersionLabel.configure(text = localVersion)
        self.systemFfmpegVersionLabel.configure(text = systemVersion)

    def selectInputFile(self):
        selected = tkinter.filedialog.askopenfilename(title = 'Select File', filetypes = inputFileTypes)
        if selected != '':
            self.inputFile.set(selected)

    def selectOutputDirectory(self):
        selected = tkinter.filedialog.askdirectory(title = 'Select Output Directory')
        if selected != '':
            self.outputDirectory.set(selected)

    def startExtract(self):
        errors = self.validateInputs()
        if errors:
            tkinter.messagebox.showerror(
                'Invalid input',
                '\n'.join(f'- {error}' for error in errors),
            )
            self.updateExtractButton()
            return

        self.extractButton.configure(state = DISABLED)
        self.cancelButton.configure(state = NORMAL)
        self.progressStatusLabel.configure(text = 'Extracting...')
        self.isExtracting = True
        self.isCancelRequested = False
        threading.Thread(target = self.runExtract, args = (self.getCommandArgs(),), daemon = True).start()

    def runExtract(self, commandArgs):
        try:
            if self.isShuttingDown:
                return

            self.extractProcess = subprocess.Popen(
                commandArgs,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                text = True,
                encoding = 'utf-8',
                errors = 'replace',
            )
            if self.isShuttingDown:
                self.extractProcess.terminate()
            stdout, stderr = self.extractProcess.communicate()
            returncode = self.extractProcess.returncode
            if not self.isShuttingDown:
                self.root.after(0, self.finishExtract, returncode, stderr)
        except OSError as error:
            if not self.isShuttingDown:
                self.root.after(0, self.failExtract, str(error))

    def cancelExtract(self):
        self.isCancelRequested = True
        if self.extractProcess is not None and self.extractProcess.poll() is None:
            self.extractProcess.terminate()
            self.progressStatusLabel.configure(text = 'Cancelling...')
            self.cancelButton.configure(state = DISABLED)

    def finishExtract(self, returncode, stderr):
        self.extractProcess = None
        self.isExtracting = False
        self.cancelButton.configure(state = DISABLED)
        if self.isCancelRequested:
            self.progressStatusLabel.configure(text = 'Cancelled')
        elif returncode == 0:
            self.progressStatusLabel.configure(text = 'Completed')
        else:
            self.progressStatusLabel.configure(text = 'Failed')
            tkinter.messagebox.showerror(
                'Extraction failed',
                stderr or f'FFmpeg exited with code {returncode}',
            )
        self.updateExtractButton()

    def failExtract(self, message):
        self.extractProcess = None
        self.isExtracting = False
        self.cancelButton.configure(state = DISABLED)
        if self.isCancelRequested:
            self.progressStatusLabel.configure(text = 'Cancelled')
        else:
            self.progressStatusLabel.configure(text = 'Failed')
            tkinter.messagebox.showerror('Unable to run FFmpeg', message)
        self.updateExtractButton()

    def updateExtractButton(self):
        state = NORMAL if not self.isExtracting and not self.validateInputs() else DISABLED
        self.extractButton.configure(state = state)

    def validateInputs(self):
        try:
            ffmpeg_file = self.getFfmpegFile()
        except FileNotFoundError:
            ffmpeg_file = None

        return validate_inputs(
            self.inputFile.get(),
            self.outputDirectory.get(),
            self.methodRadioVariety.get(),
            self.methodEveryNFramesN.get(),
            self.methodSpecificFrames.get(),
            ffmpeg_file,
        )

    def updateCommand(self):
        try:
            displayCommand = self.getDisplayCommand()
        except (FileNotFoundError, ValueError) as error:
            displayCommand = str(error)

        self.commandToRunText.config(state = tkinter.NORMAL)
        self.commandToRunText.delete('1.0', tkinter.END)
        self.commandToRunText.insert('1.0', displayCommand)
        self.commandToRunText.config(state = tkinter.DISABLED)
        self.updateExtractButton()

    def updateCommandAndQuality(self):
        self.updateCommand()

        if self.outputFileType.get() == '.jpg':
            self.outputJpgQualityScale.state(['!disabled'])
        else:
            self.outputJpgQualityScale.state(['disabled'])

        self.outputJpgQualityValueLabel.config(text = str(int(self.outputJpgQualityScale.get())))

        if self.outputFileType.get() == '.webp':
            self.outputWebpQualityScale.state(['!disabled'])
            self.outputLosslessCheckButton.configure(state=NORMAL)
        else:
            self.outputWebpQualityScale.state(['disabled'])
            self.outputLosslessCheckButton.configure(state=DISABLED)

        self.outputWebpQualityValueLabel.config(text = str(int(self.outputWebpQualityScale.get())))

    def getSelect(self):
        return build_select_filter(
            self.methodRadioVariety.get(),
            self.methodEveryNFramesN.get(),
            self.methodSpecificFrames.get(),
        )

    def getFfmpegFile(self):
        if self.ffmpegSource.get() == 0:
            ffmpegFile = getLocalFfmpegFile()
            if os.path.isfile(ffmpegFile):
                return ffmpegFile
            raise FileNotFoundError(
                'Unable to find FFmpeg next to the application: '
                + ffmpegFile
            )

        ffmpegFile = shutil.which('ffmpeg')
        if ffmpegFile is not None:
            return ffmpegFile
        raise FileNotFoundError(
            'Unable to find FFmpeg in the system PATH.'
        )

    def getCommandArgs(self):
        return build_command_args(
            self.getFfmpegFile(),
            self.inputFile.get(),
            self.outputDirectory.get(),
            self.outputFileType.get(),
            self.outputJpgQualityScale.get(),
            self.outputWebpQualityScale.get(),
            self.outputLossless.get() == True,
            self.methodRadioVariety.get(),
            self.methodEveryNFramesN.get(),
            self.methodSpecificFrames.get(),
        )

    def getDisplayCommand(self):
        return subprocess.list2cmdline(self.getCommandArgs())

    def close(self):
        if self.isShuttingDown:
            return

        self.isShuttingDown = True
        self.stopExtractProcess()
        self.root.destroy()

    def stopExtractProcess(self):
        process = self.extractProcess
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout = 2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

if __name__ == '__main__':
    window = tkinter.Tk()
    window.title('Video Frame Extractor')
    window.grid_columnconfigure(0, weight = 1)
    # window.resizable(False, False)
    app = App(window)
    window.protocol('WM_DELETE_WINDOW', app.close)
    window.update()
    w = window.winfo_width()
    h = window.winfo_height()
    if w < 400:
        window.geometry('{w}x{h}'.format(w = 400, h = h))
    # Python's normal SIGINT handler can remain pending while Tkinter is
    # inside Tcl's Windows event loop.  A native console handler lets Ctrl+C
    # clean up immediately, without waiting for another GUI event.
    consoleHandler = None
    if os.name == 'nt':
        consoleHandlerType = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_uint)

        def handleConsoleEvent(eventType):
            if eventType in (0, 2):  # CTRL_C_EVENT / CTRL_CLOSE_EVENT
                app.isShuttingDown = True
                app.stopExtractProcess()
                os._exit(0)
            return False

        consoleHandler = consoleHandlerType(handleConsoleEvent)
        ctypes.windll.kernel32.SetConsoleCtrlHandler(consoleHandler, True)

    try:
        window.mainloop()
    except KeyboardInterrupt:
        app.close()
