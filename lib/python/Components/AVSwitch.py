from config import config, ConfigSlider, ConfigSelection, ConfigYesNo, ConfigEnableDisable, ConfigSubsection, ConfigBoolean, ConfigSelectionNumber, ConfigNothing, NoSave
from enigma import eAVSwitch, getDesktop
from SystemInfo import SystemInfo
import os
from boxbranding import getBoxType

class AVSwitch:
	def setInput(self, input):
		INPUT = { "ENCODER": 0, "SCART": 1, "AUX": 2 }
		eAVSwitch.getInstance().setInput(INPUT[input])

	def setColorFormat(self, value):
		eAVSwitch.getInstance().setColorFormat(value)

	def setAspectRatio(self, value):
		eAVSwitch.getInstance().setAspectRatio(value)

	def setSystem(self, value):
		eAVSwitch.getInstance().setVideomode(value)

	def getOutputAspect(self):
		valstr = config.av.aspectratio.value
		if valstr in ("4_3_letterbox", "4_3_panscan"): # 4:3
			return (4,3)
		elif valstr == "16_9": # auto ... 4:3 or 16:9
			try:
				if "1" in open("/proc/stb/vmpeg/0/aspect", "r").read(): # 4:3
					return (4,3)
			except IOError:
				pass
		elif valstr in ("16_9_always", "16_9_letterbox"): # 16:9
			pass
		elif valstr in ("16_10_letterbox", "16_10_panscan"): # 16:10
			return (16,10)
		return (16,9)

	def getFramebufferScale(self):
		aspect = self.getOutputAspect()
		fb_size = getDesktop(0).size()
		return (aspect[0] * fb_size.height(), aspect[1] * fb_size.width())

	def getAspectRatioSetting(self):
		valstr = config.av.aspectratio.value
		if valstr == "4_3_letterbox":
			val = 0
		elif valstr == "4_3_panscan":
			val = 1
		elif valstr == "16_9":
			val = 2
		elif valstr == "16_9_always":
			val = 3
		elif valstr == "16_10_letterbox":
			val = 4
		elif valstr == "16_10_panscan":
			val = 5
		elif valstr == "16_9_letterbox":
			val = 6
		return val

	def setAspectWSS(self, aspect=None):
		if not config.av.wss.value:
			value = 2 # auto(4:3_off)
		else:
			value = 1 # auto
		eAVSwitch.getInstance().setWSS(value)

def InitAVSwitch():
	config.av = ConfigSubsection()
	config.av.yuvenabled = ConfigBoolean(default=True)
	colorformat_choices = {"cvbs": _("CVBS"), "rgb": _("RGB"), "svideo": _("S-Video")}

	# when YUV is not enabled, don't let the user select it
	if config.av.yuvenabled.value:
		colorformat_choices["yuv"] = _("YPbPr")

	config.av.colorformat = ConfigSelection(choices=colorformat_choices, default="rgb")
	config.av.aspectratio = ConfigSelection(choices={
			"4_3_letterbox": _("4:3 Letterbox"),
			"4_3_panscan": _("4:3 PanScan"),
			"16_9": _("16:9"),
			"16_9_always": _("16:9 always"),
			"16_10_letterbox": _("16:10 Letterbox"),
			"16_10_panscan": _("16:10 PanScan"),
			"16_9_letterbox": _("16:9 Letterbox")},
			default = "16_9")
	config.av.aspect = ConfigSelection(choices={
			"4_3": _("4:3"),
			"16_9": _("16:9"),
			"16_10": _("16:10"),
			"auto": _("Automatic")},
			default = "auto")

 # Some boxes have a redundant proc entry for policy2 choices, but some don't (The choices are from a 16:9 point of view anyways)
	if os.path.exists("/proc/stb/video/policy2_choices"):
		policy2_choices_proc="/proc/stb/video/policy2_choices"
	else:
		policy2_choices_proc="/proc/stb/video/policy_choices"

	try:
		policy2_choices_raw=open(policy2_choices_proc, "r").read()
	except:
		policy2_choices_raw="letterbox"

	policy2_choices = {}

	if "letterbox" in policy2_choices_raw:
		# TRANSLATORS: (aspect ratio policy: black bars on top/bottom) in doubt, keep english term.
		policy2_choices.update({"letterbox": _("Letterbox")})

	if "panscan" in policy2_choices_raw:
		# TRANSLATORS: (aspect ratio policy: cropped content on left/right) in doubt, keep english term
		policy2_choices.update({"panscan": _("Pan&scan")})

	if "nonliner" in policy2_choices_raw and not "nonlinear" in policy2_choices_raw:
		# TRANSLATORS: (aspect ratio policy: display as fullscreen, with stretching the top/bottom (Center of picture maintains aspect, top/bottom lose aspect heaver than on linear stretch))
		policy2_choices.update({"nonliner": _("Stretch nonlinear")})
	if "nonlinear" in policy2_choices_raw:
		# TRANSLATORS: (aspect ratio policy: display as fullscreen, with stretching the top/bottom (Center of picture maintains aspect, top/bottom lose aspect heaver than on linear stretch))
		policy2_choices.update({"nonlinear": _("Stretch nonlinear")})

	if "scale" in policy2_choices_raw and not "auto" in policy2_choices_raw and not "bestfit" in policy2_choices_raw:
		# TRANSLATORS: (aspect ratio policy: display as fullscreen, with stretching all parts of the picture with the same factor (All parts lose aspect))
		policy2_choices.update({"scale": _("Stretch linear")})
	if "auto" in policy2_choices_raw and not "bestfit" in policy2_choices_raw:
		# TRANSLATORS: (aspect ratio policy: display as fullscreen, with stretching all parts of the picture with the same factor (All parts lose aspect))
		policy2_choices.update({"auto": _("Stretch linear")})
	if "bestfit" in policy2_choices_raw:
		# TRANSLATORS: (aspect ratio policy: display as fullscreen, with stretching all parts of the picture with the same factor (All parts lose aspect))
		policy2_choices.update({"bestfit": _("Stretch linear")})

	# print "AVSWITCH - policy2_choices: ", policy2_choices
	config.av.policy_169 = ConfigSelection(choices=policy2_choices, default = "letterbox")

	policy_choices_proc="/proc/stb/video/policy_choices"
	try:
		policy_choices_raw=open(policy_choices_proc, "r").read()
	except:
		policy_choices_raw="panscan"

	policy_choices = {}

	if "pillarbox" in policy_choices_raw and not "panscan" in policy_choices_raw:
		# Very few boxes support "pillarbox" as an alias for "panscan" (Which in fact does pillarbox)
		# So only add "pillarbox" if "panscan" is not listed in choices

		# TRANSLATORS: (aspect ratio policy: black bars on left/right) in doubt, keep english term.
		policy_choices.update({"pillarbox": _("Pillarbox")})

	if "panscan" in policy_choices_raw:
		# DRIVER BUG:	"panscan" in /proc actually does "pillarbox" (That's probably why an alias to it named "pillarbox" existed)!
		#		Interpret "panscan" setting with a "Pillarbox" text in order to show the correct value in GUI

		# TRANSLATORS: (aspect ratio policy: black bars on left/right) in doubt, keep english term.
		policy_choices.update({"panscan": _("Pillarbox")})

	if "letterbox" in policy_choices_raw:
		# DRIVER BUG:	"letterbox" in /proc actually does pan&scan
		#		"letterbox" and 4:3 content on 16:9 TVs is mutually exclusive, as "letterbox" is the method to show wide content on narrow TVs
		#		Probably the bug arose as the driver actually does the same here as it would for wide content on narrow TVs (It stretches the picture to fit width)

		# TRANSLATORS: (aspect ratio policy: Fit width, cut/crop top and bottom (Maintain aspect ratio))
		policy_choices.update({"letterbox": _("Pan&scan")})

	if "nonliner" in policy_choices_raw and not "nonlinear" in policy_choices_raw:
		# TRANSLATORS: (aspect ratio policy: display as fullscreen, with stretching the left/right (Center 50% of picture maintain aspect, left/right 25% lose aspect heaver than on linear stretch))
		policy_choices.update({"nonliner": _("Stretch nonlinear")})
	if "nonlinear" in policy_choices_raw:
		# TRANSLATORS: (aspect ratio policy: display as fullscreen, with stretching the left/right (Center 50% of picture maintain aspect, left/right 25% lose aspect heaver than on linear stretch))
		policy_choices.update({"nonlinear": _("Stretch nonlinear")})

	# "auto", "bestfit" and "scale" are aliasses for the same: Stretch linear
	if "scale" in policy_choices_raw and not "auto" in policy_choices_raw and not "bestfit" in policy_choices_raw:
		# TRANSLATORS: (aspect ratio policy: display as fullscreen, with stretching all parts of the picture with the same factor (All parts lose aspect))
		policy_choices.update({"scale": _("Stretch linear")})
	if "auto" in policy_choices_raw and not "bestfit" in policy_choices_raw:
		# TRANSLATORS: (aspect ratio policy: display as fullscreen, with stretching all parts of the picture with the same factor (All parts lose aspect))
		policy_choices.update({"auto": _("Stretch linear")})
	if "bestfit" in policy_choices_raw:
		# TRANSLATORS: (aspect ratio policy: display as fullscreen, with stretching all parts of the picture with the same factor (All parts lose aspect))
		policy_choices.update({"bestfit": _("Stretch linear")})

	# print "AVSWITCH - policy_choices: ", policy_choices
	config.av.policy_43 = ConfigSelection(choices=policy_choices, default = "letterbox")
	config.av.tvsystem = ConfigSelection(choices = {"pal": _("PAL"), "ntsc": _("NTSC"), "multinorm": _("multinorm")}, default="pal")
	config.av.wss = ConfigEnableDisable(default = True)
	config.av.generalAC3delay = ConfigSelectionNumber(-1000, 1000, 5, default = 0)
	config.av.generalPCMdelay = ConfigSelectionNumber(-1000, 1000, 5, default = 0)
	config.av.vcrswitch = ConfigEnableDisable(default = False)

	iAVSwitch = AVSwitch()

	def setColorFormat(configElement):
		map = {"cvbs": 0, "rgb": 1, "svideo": 2, "yuv": 3}
		iAVSwitch.setColorFormat(map[configElement.value])

	def setAspectRatio(configElement):
		map = {"4_3_letterbox": 0, "4_3_panscan": 1, "16_9": 2, "16_9_always": 3, "16_10_letterbox": 4, "16_10_panscan": 5, "16_9_letterbox" : 6}
		iAVSwitch.setAspectRatio(map[configElement.value])

	def setSystem(configElement):
		map = {"pal": 0, "ntsc": 1, "multinorm" : 2}
		iAVSwitch.setSystem(map[configElement.value])

	def setWSS(configElement):
		iAVSwitch.setAspectWSS()

	# this will call the "setup-val" initial
	config.av.colorformat.addNotifier(setColorFormat)
	config.av.aspectratio.addNotifier(setAspectRatio)
	config.av.tvsystem.addNotifier(setSystem)
	config.av.wss.addNotifier(setWSS)

	iAVSwitch.setInput("ENCODER") # init on startup
	if getBoxType() in ('gbquad4k', 'gbue4k', 'gbquad', 'gbquadplus', 'gb800seplus', 'gb800ueplus', 'gbipbox', 'gbultra', 'gbultraue', 'gbultraueh', 'gbultrase', 'spycat', 'gbx1', 'gbx2', 'gbx3', 'gbx3h'):
		detected = False
	else:
		detected = eAVSwitch.getInstance().haveScartSwitch()

	SystemInfo["ScartSwitch"] = detected

	if SystemInfo["HasMultichannelPCM"]:
		def setPCMMultichannel(configElement):
			open(SystemInfo["HasMultichannelPCM"], "w").write(configElement.value and "enable" or "disable")
		config.av.pcm_multichannel = ConfigYesNo(default = False)
		config.av.pcm_multichannel.addNotifier(setPCMMultichannel)

	try:
		SystemInfo["CanDownmixAC3"] = "downmix" in open("/proc/stb/audio/ac3_choices", "r").read()
	except:
		SystemInfo["CanDownmixAC3"] = False

	if SystemInfo["CanDownmixAC3"]:
		def setAC3Downmix(configElement):
			open("/proc/stb/audio/ac3", "w").write(configElement.value and "downmix" or "passthrough")
		config.av.downmix_ac3 = ConfigYesNo(default = True)
		config.av.downmix_ac3.addNotifier(setAC3Downmix)

	try:
		SystemInfo["CanDownmixDTS"] = "downmix" in open("/proc/stb/audio/dts_choices", "r").read()
	except:
		SystemInfo["CanDownmixDTS"] = False

	if SystemInfo["CanDownmixDTS"]:
		def setDTSDownmix(configElement):
			open("/proc/stb/audio/dts", "w").write(configElement.value and "downmix" or "passthrough")
		config.av.downmix_dts = ConfigYesNo(default = True)
		config.av.downmix_dts.addNotifier(setDTSDownmix)

	try:
		SystemInfo["CanDownmixAAC"] = "downmix" in open("/proc/stb/audio/aac_choices", "r").read()
	except:
		SystemInfo["CanDownmixAAC"] = False

	if SystemInfo["CanDownmixAAC"]:
		def setAACDownmix(configElement):
			open("/proc/stb/audio/aac", "w").write(configElement.value and "downmix" or "passthrough")
		config.av.downmix_aac = ConfigYesNo(default = True)
		config.av.downmix_aac.addNotifier(setAACDownmix)

	if os.path.exists("/proc/stb/audio/aac_transcode_choices"):
		f = open("/proc/stb/audio/aac_transcode_choices", "r")
		can_aactranscode = f.read().strip().split(" ")
		f.close()
	else:
		can_aactranscode = False

	SystemInfo["CanAACTranscode"] = can_aactranscode

	if can_aactranscode:
		def setAACTranscode(configElement):
			f = open("/proc/stb/audio/aac_transcode", "w")
			f.write(configElement.value)
			f.close()
		choice_list = [("off", _("off")), ("ac3", _("AC3")), ("dts", _("DTS"))]
		config.av.transcodeaac = ConfigSelection(choices = choice_list, default = "off")
		config.av.transcodeaac.addNotifier(setAACTranscode)
	else:
		config.av.transcodeaac = ConfigNothing()

	try:
		SystemInfo["CanChangeOsdAlpha"] = open("/proc/stb/video/alpha", "r") and True or False
	except:
		SystemInfo["CanChangeOsdAlpha"] = False

	if SystemInfo["CanChangeOsdAlpha"]:
		def setAlpha(config):
			open("/proc/stb/video/alpha", "w").write(str(config.value))
		config.av.osd_alpha = ConfigSlider(default=255, increment = 5, limits=(20,255))
		config.av.osd_alpha.addNotifier(setAlpha)

	if os.path.exists("/proc/stb/vmpeg/0/pep_scaler_sharpness"):
		def setScaler_sharpness(config):
			myval = int(config.value)
			try:
				print "--> setting scaler_sharpness to: %0.8X" % myval
				open("/proc/stb/vmpeg/0/pep_scaler_sharpness", "w").write("%0.8X" % myval)
				open("/proc/stb/vmpeg/0/pep_apply", "w").write("1")
			except IOError:
				print "couldn't write pep_scaler_sharpness"

		if getBoxType() in ('gbquad4k', 'gbquad', 'gbquadplus'):
			config.av.scaler_sharpness = ConfigSlider(default=5, limits=(0,26))
		else:
			config.av.scaler_sharpness = ConfigSlider(default=13, limits=(0,26))
		config.av.scaler_sharpness.addNotifier(setScaler_sharpness)
	else:
		config.av.scaler_sharpness = NoSave(ConfigNothing())

	config.av.edid_override = ConfigYesNo(default = True)

	if SystemInfo["HasMultichannelPCM"]:
		def setMultichannelPCM(configElement):
			open(SystemInfo["HasMultichannelPCM"], "w").write(configElement.value and "enable" or "disable")
		config.av.multichannel_pcm = ConfigYesNo(default = False)
		config.av.multichannel_pcm.addNotifier(setMultichannelPCM)

	if SystemInfo["HasAutoVolume"]:
		def setAutoVolume(configElement):
			open(SystemInfo["HasAutoVolume"], "w").write(configElement.value)
		config.av.autovolume = ConfigSelection(default = "none", choices = [("none", _("off")), ("hdmi", _("HDMI")), ("spdif", _("SPDIF")), ("dac", _("DAC"))])
		config.av.autovolume.addNotifier(setAutoVolume)

	if SystemInfo["HasAutoVolumeLevel"]:
		def setAutoVolumeLevel(configElement):
			open(SystemInfo["HasAutoVolumeLevel"], "w").write(configElement.value and "enabled" or "disabled")
		config.av.autovolumelevel = ConfigYesNo(default = False)
		config.av.autovolumelevel.addNotifier(setAutoVolumeLevel)

	if SystemInfo["Has3DSurround"]:
		def set3DSurround(configElement):
			open(SystemInfo["Has3DSurround"], "w").write(configElement.value)
		config.av.surround_3d = ConfigSelection(default = "none", choices = [("none", _("off")), ("hdmi", _("HDMI")), ("spdif", _("SPDIF")), ("dac", _("DAC"))])
		config.av.surround_3d.addNotifier(set3DSurround)

	if SystemInfo["Has3DSpeaker"]:
		def set3DSpeaker(configElement):
			open(SystemInfo["Has3DSpeaker"], "w").write(configElement.value)
		config.av.speaker_3d = ConfigSelection(default = "center", choices = [("center", _("center")), ("wide", _("wide")), ("extrawide", _("extra wide"))])
		config.av.speaker_3d.addNotifier(set3DSpeaker)

	if SystemInfo["Has3DSurroundSpeaker"]:
		def set3DSurroundSpeaker(configElement):
			open(SystemInfo["Has3DSurroundSpeaker"], "w").write(configElement.value)
		config.av.surround_3d_speaker = ConfigSelection(default = "disabled", choices = [("disabled", _("off")), ("center", _("center")), ("wide", _("wide")), ("extrawide", _("extra wide"))])
		config.av.surround_3d_speaker.addNotifier(set3DSurroundSpeaker)

	if SystemInfo["Has3DSurroundSoftLimiter"]:
		def set3DSurroundSoftLimiter(configElement):
			open(SystemInfo["Has3DSurroundSoftLimiter"], "w").write(configElement.value and "enabled" or "disabled")
		config.av.surround_softlimiter_3d = ConfigYesNo(default = False)
		config.av.surround_softlimiter_3d.addNotifier(set3DSurroundSoftLimiter)
