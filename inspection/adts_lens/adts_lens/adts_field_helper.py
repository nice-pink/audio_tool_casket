class AdtsFieldHelper:

    @staticmethod
    def get_profile_name(index: int) -> str:
        if index < len(AdtsFieldHelper.NAMES):
            return AdtsFieldHelper.NAMES[index]
        else:
            return "???"

    @staticmethod
    def get_sample_rate(index: int) -> int:
        if index < len(AdtsFieldHelper.SAMPLING_FREQUENCIES):
            return AdtsFieldHelper.SAMPLING_FREQUENCIES[index]
        else:
            return -1

    @staticmethod
    def get_channel_config(index: int) -> str:
        if index < len(AdtsFieldHelper.CHANNEL_CONFIGURATIONS):
            return AdtsFieldHelper.CHANNEL_CONFIGURATIONS[index]
        else:
            return "???"

    NAMES = ["AAC Main",
            "AAC LC (Low Complexity)",
            "AAC SSR (Scalable Sample Rate)",
            "AAC LTP (Long Term Prediction)",
            "SBR (Spectral Band Replication)",
            "AAC Scalable",
            "TwinVQ",
            "CELP (Code Excited Linear Prediction)",
            "HXVC (Harmonic Vector eXcitation Coding)",
            "Reserved",
            "Reserved",
            "TTSI (Text-To-Speech Interface)",
            "Main Synthesis",
            "Wavetable Synthesis",
            "General MIDI",
            "Algorithmic Synthesis and Audio Effects",
            "ER (Error Resilient) AAC LC",
            "Reserved",
            "ER AAC LTP",
            "ER AAC Scalable",
            "ER TwinVQ",
            "ER BSAC (Bit-Sliced Arithmetic Coding)",
            "ER AAC LD (Low Delay)",
            "ER CELP",
            "ER HVXC",
            "ER HILN (Harmonic and Individual Lines plus Noise)",
            "ER Parametric",
            "SSC (SinuSoidal Coding)",
            "PS (Parametric Stereo)",
            "MPEG Surround",
            "(Escape value)",
            "Layer-1",
            "Layer-2",
            "Layer-3",
            "DST (Direct Stream Transfer)",
            "ALS (Audio Lossless)",
            "SLS (Scalable LosslesS)",
            "SLS non-core",
            "ER AAC ELD (Enhanced Low Delay)",
            "SMR (Symbolic Music Representation) Simple",
            "SMR Main",
            "USAC (Unified Speech and Audio Coding) (no SBR)",
            "SAOC (Spatial Audio Object Coding)",
            "LD MPEG Surround",
            "USAC"]

    SAMPLING_FREQUENCIES = [96000,
                            88200,
                            64000,
                            48000,
                            44100,
                            32000,
                            24000,
                            22050,
                            16000,
                            12000,
                            11025,
                            8000,
                            7350,
                            0,
                            0,
                            -1]

    CHANNEL_CONFIGURATIONS = ["ato",
                              "fc",
                              "fl-fr",
                              "fl-fc-fr",
                              "fl-fc-fr-bc",
                              "fl-fc-fr-bl-br",
                              "fl-fc-fr-bl-br-lfe",
                              "fl-fc-fr-sl-sr-bl-br-lfe",
                              "r",
                              "r",
                              "r",
                              "r",
                              "r",
                              "r",
                              "r",
                              "r"]