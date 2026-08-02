"""
音频信息节点
获取音频的时长、采样率、通道数和采样点数等信息
"""

CATEGORY = "🐍 NCE/音频"


class NCEGetAudioInfo:
    """获取音频信息"""

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO",),
            }
        }

    RETURN_TYPES = ("AUDIO", "FLOAT", "INT", "INT", "INT",)
    RETURN_NAMES = ("audio", "duration", "sample_rate", "channels", "samples",)
    FUNCTION = "get_info"
    CATEGORY = CATEGORY
    DESCRIPTION = """
获取音频的时长（秒）、采样率（Hz）、通道数和采样点数，
并将音频原样传递。
"""

    def get_info(self, audio):
        waveform = audio["waveform"]
        sample_rate = audio["sample_rate"]

        # waveform 形状通常为 [batch, channels, samples] 或 [channels, samples]
        shape = waveform.shape
        samples = shape[-1]
        channels = shape[-2] if len(shape) >= 2 else 1

        duration = float(samples) / float(sample_rate) if sample_rate > 0 else 0.0
        duration = round(duration, 4)

        info_text = f"Duration: {duration}s | Sample Rate: {sample_rate}Hz | Channels: {channels} | Samples: {samples}"

        return {
            "ui": {
                "text": [info_text]
            },
            "result": (audio, duration, sample_rate, channels, samples)
        }
