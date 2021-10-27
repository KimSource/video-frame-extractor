import re
import os
import sys
import tkinter
from tkinter.constants import DISABLED, NORMAL
import tkinter.ttk
import tkinter.filedialog

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
    if not hasattr(sys, 'frozen'):
        return os.path.join(os.path.dirname(__file__), filename)
    else:
        return os.path.join(sys.prefix, filename)

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

        self.infoSection = tkinter.Frame(root)
        self.infoSection.grid(column = 0, row = 2, padx = 8, pady = 4, sticky = 'NSEW')
        self.infoSection.grid_columnconfigure(0, weight = 1)

        self.commandToRunLabel = tkinter.Label(self.infoSection, text = 'Command to run')
        self.commandToRunLabel.grid(column = 0, row = 0, sticky = 'W')

        self.commandToRunText = tkinter.Text(self.infoSection, width = 0, height = 4)
        self.commandToRunText.grid(column = 0, row = 1, sticky = 'EW')
        self.commandToRunText.config(state = tkinter.DISABLED)

        self.actionSection = tkinter.Frame(root)
        self.actionSection.grid(column = 0, row = 3, padx = 8, pady = 4, sticky = 'NSEW')
        self.actionSection.grid_columnconfigure(0, weight = 1)

        self.extractButton = tkinter.Button(self.actionSection, text = 'Extract', command = self.startExtract)
        self.extractButton.grid(column = 0, row = 0)

        self.inputFile.trace('w', lambda name, index, mode: self.updateCommand())
        self.outputDirectory.trace('w', lambda name, index, mode: self.updateCommand())
        self.outputFileType.trace('w', lambda name, index, mode: self.updateCommandAndQuality())
        self.outputJpgQuality.trace('w', lambda name, index, mode: self.updateCommandAndQuality())
        self.outputWebpQuality.trace('w', lambda name, index, mode: self.updateCommandAndQuality())
        self.outputLossless.trace('w', lambda name, index, mode: self.updateCommandAndQuality())
        self.methodRadioVariety.trace('w', lambda name, index, mode: self.updateCommand())
        self.methodEveryNFramesN.trace('w', lambda name, index, mode: self.updateCommand())
        self.methodSpecificFrames.trace('w', lambda name, index, mode: self.updateCommand())

        self.updateCommand()

    def selectInputFile(self):
        selected = tkinter.filedialog.askopenfilename(title = 'Select File', filetypes = inputFileTypes)
        if selected != '':
            self.inputFile.set(selected)

    def selectOutputDirectory(self):
        selected = tkinter.filedialog.askdirectory(title = 'Select Output Directory')
        if selected != '':
            self.outputDirectory.set(selected)

    def startExtract(self):
        os.system('start cmd /c ' + ' '.join(self.getCommand()) + ' ^& pause')

    def updateCommand(self):
        self.commandToRunText.config(state = tkinter.NORMAL)
        self.commandToRunText.delete('1.0', tkinter.END)
        self.commandToRunText.insert('1.0', ' '.join(self.getCommand()))
        self.commandToRunText.config(state = tkinter.DISABLED)

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
        select = ''
        if self.methodRadioVariety.get() == 0:
            select = "'not(mod(n,{n}))'".format(n = self.methodEveryNFramesN.get().strip())
        elif self.methodRadioVariety.get() == 1:
            frames =  re.compile(' +| *,+ *').split(self.methodSpecificFrames.get().strip())
            select = "'" + '+'.join(['eq(n,{n})'.format(n = n) for n in frames]) + "'"
        else:
            frames =  re.compile(' +| *,+ *').split(self.methodSpecificFrames.get().strip())
            select = "'" + '+'.join(['eq(pts,{pts})'.format(pts = pts) for pts in frames]) + "'"
        return 'select={select}'.format(select = select)

    def getCommand(self):
        jpgQualityOption = []
        if self.outputFileType.get() == '.jpg':
            jpgQualityOption = [
                '-qscale:v',
                str(int(self.outputJpgQualityScale.get()))
            ]

        webpQualityOption = []
        if self.outputFileType.get() == '.webp':
            lossless = self.outputLossless.get() == True;
            webpQualityOption = [
                '-qscale:v',
                str(int(self.outputWebpQualityScale.get())),
                '-lossless',
                '1' if lossless else '0'
            ]

        return [
            'ffmpeg\\bin\\ffmpeg.exe',
            '-i',
            '"' + self.inputFile.get() + '"',
            '-vf',
            self.getSelect(),
            '-vsync',
            '0',
            '-frame_pts',
            '1',
            *jpgQualityOption,
            *webpQualityOption,
            '"' + self.outputDirectory.get() + '/%d' + self.outputFileType.get() + '"'
        ]

if __name__ == '__main__':
    window = tkinter.Tk()
    window.title('Video Frame Extractor')
    window.grid_columnconfigure(0, weight = 1)
    # window.resizable(False, False)
    App(window)
    window.update()
    w = window.winfo_width()
    h = window.winfo_height()
    if w < 400:
        window.geometry('{w}x{h}'.format(w = 400, h = h))
    window.mainloop()
