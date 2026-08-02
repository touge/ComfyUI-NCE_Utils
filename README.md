自用脚本，不提供技术支持。


20260802更新：

1. 新增音频信息节点 `NCEGetAudioInfo`（获取音频信息），支持解析音频的时长（秒）、采样率（Hz）、通道数及总采样点数。
2. 重构音频节点目录，新建 `nodes/audios/` 目录，将音频信息节点与播放声音节点（`play_sound.py`）统一归集管理。


20250115更新：

1.新增本地化json语言文件。
如果安装过AIGODLIKE-COMFYUI-TRANSLATION插件，将translation/zh-CN/Nodes/ComfyUI-NCE_Utils.json，
拷贝到AIGODLIKE-COMFYUI-TRANSLATION/zh-CN/Nodes下，重启ComfyUI即可。

2.新增节点视频风格生成器
