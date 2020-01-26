#!/usr/bin/python
# (c) Shahar Gino, July-2017, sgino209@gmail.com

import wx
import sys
from ast import literal_eval
from main import main as lpr_analyzer
from auxiliary import draw_roi as draw_roi_aux
from numpy import zeros, uint8, max, frombuffer
from cv2 import imread, resize, cvtColor, COLOR_RGB2BGR

PANEL_SIZE = (1300,800)
IMAGE_SIZE = (600,600)

# ---------------------------------------------------------------------------------------------------------------
class main_gui_frame(wx.Frame):
    """ GUI class for LPR application """

    def __init__(self, parent):
        """ Frame Constructor """

        # -----------------------------------------------------------------------------------------------------
        # Frame initialization:

        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title="Bracelet Decoder GUI",
                          pos=wx.DefaultPosition, size=wx.Size(PANEL_SIZE[0], PANEL_SIZE[1]),
                          style=(wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL) & ~wx.MAXIMIZE_BOX ^ wx.RESIZE_BORDER)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        # -----------------------------------------------------------------------------------------------------
        # Main Sizer, Top side: Image Browser + Go button:

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        self.gSizer31 = wx.GridSizer(1, 2, 0, 0)

        self.m_filePicker1 = wx.FilePickerCtrl(self, wx.ID_ANY, wx.EmptyString, u"Select a file", u"*.*",
                                               wx.DefaultPosition, (IMAGE_SIZE[0],-1), wx.FLP_DEFAULT_STYLE)
        self.m_filePicker1.SetToolTipString(u"Choose input image file")
        self.m_filePicker1.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnSaveLogCheckBox)
        self.gSizer31.Add(self.m_filePicker1, 0, wx.ALL, 5)

        self.m_button2 = wx.Button(self, wx.ID_ANY, u"Go!", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_button2.Bind(wx.EVT_BUTTON, self.OnGoButton)
        self.gSizer31.Add(self.m_button2, 0, wx.ALL, 5)

        bSizer1.Add(self.gSizer31, 1, wx.EXPAND, 5)

        # -----------------------------------------------------------------------------------------------------
        # Main Sizer, Bottom side: Image viewer + User parameters:

        gSizer1 = wx.GridSizer(1, 2, 0, 0)

        bSizer2 = wx.BoxSizer(wx.VERTICAL)

        self.m_bitmap1 = wx.StaticBitmap(self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0)
        self.update_image(zeros((IMAGE_SIZE[0],IMAGE_SIZE[1], 3), uint8))
        bSizer2.Add(self.m_bitmap1, 0, wx.ALL, 5)

        m_textCtrl0 = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (IMAGE_SIZE[0],100), wx.TE_MULTILINE|wx.VSCROLL)
        bSizer2.Add(m_textCtrl0, 0, wx.ALL, 5)
        sys.stdout = m_textCtrl0

        gSizer1.Add(bSizer2, 0, wx.ALL, 5)

        self.gSizer3 = wx.GridSizer(20, 2, 0, 0)

        self.m_textCtrl = []

        self.add_attribute("PreprocessGaussKernel", "(5,5)", "Preprocessing: gaussian kernel, for smoothing")
        self.add_attribute("PreprocessThreshBlockSize", "19", "Preprocessing: adaptive threshold, block size")
        self.add_attribute("PreprocessThreshweight", "7", "Preprocessing: adaptive threshold, weight")
        self.add_attribute("PreprocessMorphKernel", "(3,3)", "Preprocessing: morphological structuring kernel")
        self.add_attribute("ROI", "(400,400,650)", "ROI = (startX, startY, width, height)\n(startX, startY, R)-->width=height=R\n(0,0)=whole image\nDiplayed image is 600x600")
        self.add_attribute("MinPixelWidth", "7", "Minimal width (#pixels) for a character to be detected")
        self.add_attribute("MaxPixelWidth", "30", "Maximal width (#pixels) for a character to be detected")
        self.add_attribute("MinPixelHeight", "7", "Minimal height (#pixels) for a character to be detected")
        self.add_attribute("MaxPixelHeight", "30", "Maximal height (#pixels) for a character to be detected")
        self.add_attribute("MinAspectRatio", "0.6", "Minimal aspect ratio (W/H) for a character to be detected")
        self.add_attribute("MaxAspectRatio", "2.5", "Maximal aspect ratio (W/H) for a character to be detected")
        self.add_attribute("MinPixelArea", "150", "Minimal area (#pixels) for a character to be detected")
        self.add_attribute("MaxPixelArea", "600", "Maximal area (#pixels) for a character to be detected")
        self.add_attribute("MinExtent", "0.4", "Minimal extent ratio (area ext/int) for a character to be detected")
        self.add_attribute("MaxExtent", "0.9", "Maximal extent ratio (area (ext/int) for a character to be detected")
        self.add_attribute("MaxDrift", "2.5", "Maximal drift distance, for removing outlier marks")
        self.add_attribute("MarksRows", "3", "Number of Mark's rows")
        self.add_attribute("MarksCols", "10", "Number of Mark's columns")
        self.add_attribute_combo("imgEnhancementEn", ["True", "False"], "False", "Enable preliminary image-enhancement phase")
        self.add_attribute_combo("debugMode", ["True", "False"], "False", "Enable debug printouts and intermediate figures")

        self.m_textCtrl[4].Bind(wx.EVT_TEXT_ENTER, self.OnRoiText)

        gSizer1.Add(self.gSizer3, 1, wx.EXPAND, 5)

        bSizer1.Add(gSizer1, 1, wx.EXPAND, 5)

        # -----------------------------------------------------------------------------------------------------
        # Closure:
        self.SetSizer(bSizer1)
        self.Layout()

        self.Centre(wx.BOTH)

    # -----------------------------------------------------------------------------------------------------
    def OnSaveLogCheckBox(self, browseInfo):
        """ Image broswer handler, called when browser is updated """

        frame = imread(browseInfo.Path)
        if frame is None:
            self.update_image(zeros((IMAGE_SIZE[0], IMAGE_SIZE[1], 3), uint8))
        else:
            self.update_image(frame)

        if max(frame) > 0:
            h, w = frame.shape[:2]
            self.draw_roi(w, h)

    # -----------------------------------------------------------------------------------------------------
    def OnGoButton(self, buttonInfo):
        """ Go button handler, called when Go button is clicked """

        in_frame = self.m_filePicker1.GetPath()
        if in_frame != "":
            cmd = ["-i", self.m_filePicker1.GetPath().encode("utf-8"),
                   "--PreprocessGaussKernel", self.m_textCtrl[0].GetValue().encode("utf-8"),
                   "--PreprocessThreshBlockSize", self.m_textCtrl[1].GetValue().encode("utf-8"),
                   "--PreprocessThreshweight", self.m_textCtrl[2].GetValue().encode("utf-8"),
                   "--PreprocessMorphKernel", self.m_textCtrl[3].GetValue().encode("utf-8"),
                   "--ROI", self.m_textCtrl[4].GetValue().encode("utf-8"),
                   "--MinPixelWidth", self.m_textCtrl[5].GetValue().encode("utf-8"),
                   "--MaxPixelWidth", self.m_textCtrl[6].GetValue().encode("utf-8"),
                   "--MinPixelHeight", self.m_textCtrl[7].GetValue().encode("utf-8"),
                   "--MaxPixelHeight", self.m_textCtrl[8].GetValue().encode("utf-8"),
                   "--MinAspectRatio", self.m_textCtrl[9].GetValue().encode("utf-8"),
                   "--MaxAspectRatio", self.m_textCtrl[10].GetValue().encode("utf-8"),
                   "--MinPixelArea", self.m_textCtrl[11].GetValue().encode("utf-8"),
                   "--MaxPixelArea", self.m_textCtrl[12].GetValue().encode("utf-8"),
                   "--MinExtent", self.m_textCtrl[13].GetValue().encode("utf-8"),
                   "--MaxExtent", self.m_textCtrl[14].GetValue().encode("utf-8"),
                   "--MaxDrift", self.m_textCtrl[15].GetValue().encode("utf-8"),
                   "--MarksRows", self.m_textCtrl[16].GetValue().encode("utf-8"),
                   "--MarksCols", self.m_textCtrl[17].GetValue().encode("utf-8")]

            if self.m_textCtrl[18].GetValue() == "True":
                cmd.append("--imgEnhancementEn")
            
            if self.m_textCtrl[19].GetValue() == "True":
                cmd.append("--debug")

            out_frame = lpr_analyzer(cmd)
            if out_frame is not None:
                self.update_image(out_frame)

    # -----------------------------------------------------------------------------------------------------
    def OnRoiText(self, RoiInfo):
        """ ROI text control handler, called when text is updated """

        frame = imread(self.m_filePicker1.GetPath().encode("utf-8"))
        h, w = frame.shape[:2]
        self.update_image(frame)
        self.draw_roi(w,h)

    # -----------------------------------------------------------------------------------------------------
    def update_image(self, in_frame):
        """ Auxiliary method for updating the image figure """

        frame_cvt = cvtColor(in_frame, COLOR_RGB2BGR)
        frameResized = resize(frame_cvt, (IMAGE_SIZE[0], IMAGE_SIZE[1]))
        w, h = frameResized.shape[:2]
        self.m_bitmap1.SetBitmap(wx.BitmapFromBuffer(w, h, frameResized))

    # -----------------------------------------------------------------------------------------------------
    def add_attribute(self, name, defval, tooltip):
        """ Auxiliary method for adding attribute parameter """

        m_staticText = wx.StaticText(self, wx.ID_ANY, name, wx.DefaultPosition, wx.DefaultSize, 0)
        m_staticText.Wrap(-1)
        m_staticText.SetToolTipString(tooltip)
        self.gSizer3.Add(m_staticText, 0, wx.ALL, 5)

        m_textCtrl = wx.TextCtrl(self, id=wx.ID_ANY, name=wx.EmptyString, pos=wx.DefaultPosition, size=(200,-1), style=wx.TE_PROCESS_ENTER)
        m_textCtrl.SetLabel(defval)
        m_textCtrl.SetToolTipString(tooltip)
        self.m_textCtrl.append(m_textCtrl)
        self.gSizer3.Add(m_textCtrl, 0, wx.ALL, 5)

    # -----------------------------------------------------------------------------------------------------
    def add_attribute_combo(self, name, combovals, defval, tooltip):
        """ Auxiliary method for adding attribute parameter """

        m_staticText = wx.StaticText(self, wx.ID_ANY, name, wx.DefaultPosition, wx.DefaultSize, 0)
        m_staticText.Wrap(-1)
        m_staticText.SetToolTipString(tooltip)
        self.gSizer3.Add(m_staticText, 0, wx.ALL, 5)

        m_comboBox = wx.ComboBox(self, wx.ID_ANY, defval, wx.DefaultPosition, (200,-1), combovals, 0)
        m_comboBox.SetToolTipString(tooltip)
        self.m_textCtrl.append(m_comboBox)
        self.gSizer3.Add(m_comboBox, 0, wx.ALL, 5)

    # -----------------------------------------------------------------------------------------------------
    def draw_roi(self, w, h):
        """ Auxiliary method for drawing ROI on the displayed image """

        bitmap = self.m_bitmap1.GetBitmap()
        image = wx.ImageFromBitmap(bitmap)
        buf = image.GetDataBuffer()
        frame = frombuffer(buf, dtype='uint8')
        frame = frame.reshape((IMAGE_SIZE[0],IMAGE_SIZE[1],3))
        roi = literal_eval(self.m_textCtrl[4].GetValue().encode("utf-8"))

        roi_scaled = []
        if len(roi) > 2:
            roi_scaled.append(int(roi[0] * (float(IMAGE_SIZE[0]) / w)))
            roi_scaled.append(int(roi[1] * (float(IMAGE_SIZE[1]) / h)))
            roi_scaled.append(int(roi[2] * (float(IMAGE_SIZE[0]) / w)))
        if len(roi) > 3:
            roi_scaled.append(int(roi[3] * (float(IMAGE_SIZE[1]) / h)))

        draw_roi_aux(frame, roi_scaled)

        self.m_bitmap1.SetBitmap(wx.BitmapFromBuffer(IMAGE_SIZE[0], IMAGE_SIZE[1], frame))

    # -----------------------------------------------------------------------------------------------------
    def __del__(self):
        """ Destructor """
        pass

# ---------------------------------------------------------------------------------------------------------------
app = wx.App(False)
frame = main_gui_frame(None)
frame.Show()
app.MainLoop()
sys.stdout = sys.__stdout__
